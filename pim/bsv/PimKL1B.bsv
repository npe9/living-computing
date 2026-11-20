// PimKL1B.bsv -- a minimal KL1-B execution path.
//
// The diagnostic ISA in PimPU is a model-defined stand-in.  This module
// is the separate KL1-B path the PIMOS binaries need: a 40-bit tagged
// word (8-bit tag + 32-bit value, TR-389 p. 9), an 8-bit register file,
// and a fetch/decode/execute step.  The encodings are the PIMOS
// assembler's (docs/kl1_encoding.md), labelled PIMOS-derived.
//
// Implemented so far: set_value, set_variable, set_constant,
// set_integer, set_nil, set_atom, set_list, put_value, put_variable,
// get_value, get_bound_value, write_value, write_variable,
// write_constant, put_constant, put_list, put_integer, write_integer,
// read_variable, read_constant, read_integer, read_nil, read_atom,
// get_constant, get_integer, get_nil, get_atom,
// add, subtract, multiply, divide, modulo, equal, not_equal,
// wait_value, wait_constant, wait_list, wait_integer, execute,
// enqueue_goal, suspend, proceed, halt, switch_on_non_integer,
// switch_on_non_atom, switch_on_non_list, try_me_else, fail.
// Anything else -- including the structure reads,
// get_structured_constant, the remaining switch_* forms and the
// choice-point control -- halts loudly rather than being skipped
// (AGENTS.md, "execute partially, document the rest").
//
// Semantics note.  put_/write_/get_/read_ follow the TR-246 p. 7 images.
// set_value/set_variable reuse the assembler's c8_r fields but are used
// as "general register <- integer/variable literal", not TR-246's
// goal-record argument slots (TR-246 p. 7), which this model does not
// have yet; the testbenches call this the model's set_value convention.
package PimKL1B;

import RegFile::*;

typedef Bit#(40) Word;
typedef Bit#(8)  RegNo;

interface PimKL1B;
  method Action load(Bit#(12) a, Word w);
  method Action loadHeap(Bit#(12) a, Word w);
  method Action setReg(RegNo r, Word w);
  method Action start(Word entry);
  method Action step();
  method Bool halted();
  method Word readReg(RegNo r);
  method Word readArg(Bit#(8) i);
  method Word pc();
endinterface

module mkPimKL1B(PimKL1B);

  RegFile#(RegNo, Word)  regs <- mkRegFileFull;
  RegFile#(Bit#(12), Word) mem <- mkRegFileFull;
  RegFile#(Bit#(12), Word) heap <- mkRegFileFull;

  Reg#(Word) pcR   <- mkReg(0);
  Reg#(Bool) run   <- mkReg(False);
  Reg#(Bool) haltR <- mkReg(False);
  Reg#(Bit#(12)) hp <- mkReg(0);
  Reg#(Bit#(8)) narg <- mkReg(0);
  RegFile#(Bit#(3), Word) goals <- mkRegFileFull;
  Reg#(Bit#(3)) rqfp <- mkReg(0);
  Reg#(Bit#(3)) rqt <- mkReg(0);
  // Goal-record argument save area (TR-246 p. 7): set_* writes here.
  RegFile#(Bit#(8), Word) args <- mkRegFileFull;
  Reg#(Bit#(8)) argPtr <- mkReg(0);

  // Choice-point stack: minimal backtracking for try_me_else / fail.
  // Each entry saves the else-label, argPtr, narg, and HP.  Full
  // register/heap state is NOT restored — documented stand-in.
  RegFile#(Bit#(4), Bit#(12)) cpLabel <- mkRegFileFull;
  RegFile#(Bit#(4), Bit#(8))  cpArgPtr <- mkRegFileFull;
  RegFile#(Bit#(4), Bit#(8))  cpNarg <- mkRegFileFull;
  RegFile#(Bit#(4), Bit#(12)) cpHP <- mkRegFileFull;
  Reg#(Bit#(4)) cpsp <- mkReg(0);

  // Tag values are the model's; the encoding is PIMOS-derived.
  Bit#(8) tagInt = 8'h02;
  Bit#(8) tagRef = 8'h03;
  Bit#(8) tagVar = 8'h01;
  Bit#(8) tagList = 8'h05;   // LIST: value points at consecutive car/cdr
  Bit#(8) tagNil = 8'h04;
  Bit#(8) tagAtom = 8'h06;

  function Word deref(Word w);
    return (w[39:32] == tagRef) ? heap.sub(w[11:0]) : w;
  endfunction

  function Action backtrackOrHalt();
    action
      if (cpsp == 0) haltR <= True;
      else begin
        argPtr <= cpArgPtr.sub(cpsp - 1);
        narg <= cpNarg.sub(cpsp - 1);
        hp <= cpHP.sub(cpsp - 1);
        cpsp <= cpsp - 1;
      end
    endaction
  endfunction

  function Bool isC40(Bit#(8) op);
    return (op == 8'h10 || op == 8'h20 || op == 8'h30
         || op == 8'ha0 || op == 8'hb0 || op == 8'hb8);
  endfunction

  method Action load(Bit#(12) a, Word w) = mem.upd(a, w);
  method Action loadHeap(Bit#(12) a, Word w) = heap.upd(a, w);
  method Action setReg(RegNo r, Word w) = regs.upd(r, w);

  method Action start(Word entry) if (!run);
    pcR <= entry;
    run <= True;
    haltR <= False;
  endmethod

  method Action step() if (run && !haltR);
    Word w = mem.sub(pcR[11:0]);
    Bit#(8)  tag = w[39:32];
    Bit#(32) val = w[31:0];
    Bit#(8)  op  = val[31:24];
    Bit#(8)  a   = val[23:16];
    Bit#(8)  b   = val[15:8];
    Bit#(8)  c   = val[7:0];
    if (tag == 8'h23 && isC40(op)) begin
      Word cw = mem.sub(pcR[11:0] + 1);
      Word d_get = deref(regs.sub(a));
      case (op)
        8'h10: args.upd(a, cw);                          // set_constant C, Gi
        8'h20: begin heap.upd(hp, cw); hp <= hp + 1; end  // write_constant C
        8'h30: regs.upd(a, cw);                          // put_constant C, Ai = C
        8'ha0: if (deref(regs.sub(a)) != cw) haltR <= True;  // wait_constant
        8'hb0: begin                                       // read_constant C
          if (args.sub(argPtr) != cw) backtrackOrHalt();
          else argPtr <= argPtr + 1;
        end
        8'hb8: begin                                       // get_constant C, Ai
          if (d_get == cw) begin
            // already equal
          end else if (d_get[39:32] == tagVar) begin
            if (regs.sub(a)[39:32] == tagRef) heap.upd(regs.sub(a)[11:0], cw);
            regs.upd(a, cw);
          end else backtrackOrHalt();
        end
        default: haltR <= True;   // unimplemented c40 opcode
      endcase
      Bool c40Backtrack = (op == 8'hb0 && args.sub(argPtr) != cw && cpsp > 0)
                       || (op == 8'hb8 && d_get != cw && d_get[39:32] != tagVar && cpsp > 0);
      if (c40Backtrack) pcR <= zeroExtend(cpLabel.sub(cpsp - 1));
      else pcR <= pcR + 2;
    end else begin
    if (tag == 8'h23) begin
      case (op)
        8'h00: args.upd(a, {tagAtom, 24'h0, c});  // set_atom c8, Gi
        8'h11: args.upd(a, {tagInt, 16'h0, val[15:0]});  // set_integer c16, Gi
        8'h12: args.upd(a, {tagNil, 24'h0, 0});   // set_nil Gi
        8'h18: args.upd(a, {tagList, 20'h0, hp});  // set_list Gi
        8'h14: regs.upd(b, {tagInt, 24'h0, a});   // set_value c8, r
        8'h13: regs.upd(b, {tagVar, 24'h0, a});   // set_variable c8, r
        8'h32: regs.upd(a, {tagNil, 24'h0, 0});  // put_nil Ai
        8'h31: regs.upd(a, {tagInt, 16'h0, val[15:0]});  // put_integer Ai, c16
        8'h34: regs.upd(b, regs.sub(a));          // put_value r, r
        8'h33: regs.upd(b, {tagVar, 24'h0, a});   // put_variable r, r
        8'hbc: regs.upd(b, regs.sub(a));          // get_value r, r
        8'h22: begin heap.upd(hp, {tagNil, 24'h0, 0}); hp <= hp + 1; end  // write_nil
        8'h21: begin heap.upd(hp, {tagInt, 8'h0, val[23:0]}); hp <= hp + 1; end  // write_integer c24
        8'h25: begin heap.upd(hp, regs.sub(a)); hp <= hp + 1; end  // write_value
        8'h24: begin heap.upd(hp, {tagVar, 24'h0, a}); hp <= hp + 1; end  // write_variable
        8'hbd: regs.upd(b, heap.sub(regs.sub(a)[11:0]));           // get_bound_value
        8'h2e: regs.upd(a, {tagList, 20'h0, hp});  // put_list Ai = list HP (TR-246 p.7)
        8'ha1: if (deref(regs.sub(a)) != {tagInt, 16'h0, {b, c}})   // wait_integer
                 haltR <= True;
        8'ha4: if (deref(regs.sub(a)) != deref(regs.sub(b)))        // wait_value
                 haltR <= True;
        8'ha6: if (deref(regs.sub(a))[39:32] != tagList)            // wait_list
                 haltR <= True;
        8'hb1: begin                               // read_integer c24
          if (args.sub(argPtr) != {tagInt, 8'h0, val[23:0]}) backtrackOrHalt();
          else argPtr <= argPtr + 1;
        end
        8'hb2: begin                               // read_nil
          if (args.sub(argPtr)[39:32] != tagNil) backtrackOrHalt();
          else argPtr <= argPtr + 1;
        end
        8'hb3: begin                               // read_atom A
          if (args.sub(argPtr)[39:32] != tagAtom) backtrackOrHalt();
          else argPtr <= argPtr + 1;
        end
        8'hf2: begin                               // equal Ai, Aj (guard)
          if (regs.sub(a)[39:32] != tagInt || regs.sub(b)[39:32] != tagInt
              || regs.sub(a)[31:0] != regs.sub(b)[31:0]) backtrackOrHalt();
        end
        8'hf3: begin                               // not_equal Ai, Aj
          if (regs.sub(a)[39:32] != tagInt || regs.sub(b)[39:32] != tagInt
              || regs.sub(a)[31:0] == regs.sub(b)[31:0]) backtrackOrHalt();
        end
        8'hf4: begin                               // add Ai, Aj, Ak
          if (regs.sub(a)[39:32] != tagInt || regs.sub(b)[39:32] != tagInt) haltR <= True;
          else regs.upd(c, {tagInt, regs.sub(a)[31:0] + regs.sub(b)[31:0]});
        end
        8'hf5: begin                               // subtract Ai, Aj, Ak
          if (regs.sub(a)[39:32] != tagInt || regs.sub(b)[39:32] != tagInt) haltR <= True;
          else regs.upd(c, {tagInt, regs.sub(a)[31:0] - regs.sub(b)[31:0]});
        end
        8'hf6: begin                               // multiply Ai, Aj, Ak
          if (regs.sub(a)[39:32] != tagInt || regs.sub(b)[39:32] != tagInt) haltR <= True;
          else regs.upd(c, {tagInt, regs.sub(a)[31:0] * regs.sub(b)[31:0]});
        end
        8'hf7: begin                               // divide Ai, Aj, Ak
          if (regs.sub(a)[39:32] != tagInt || regs.sub(b)[39:32] != tagInt
              || regs.sub(b)[31:0] == 0) haltR <= True;
          else regs.upd(c, {tagInt, regs.sub(a)[31:0] / regs.sub(b)[31:0]});
        end
        8'hf8: begin                               // modulo Ai, Aj, Ak
          if (regs.sub(a)[39:32] != tagInt || regs.sub(b)[39:32] != tagInt
              || regs.sub(b)[31:0] == 0) haltR <= True;
          else regs.upd(c, {tagInt, regs.sub(a)[31:0] % regs.sub(b)[31:0]});
        end
        8'hb9: begin                                 // get_integer c16, Ai
          Word d = deref(regs.sub(a));
          if (d == {tagInt, 16'h0, val[15:0]}) begin
            // already equal
          end else if (d[39:32] == tagVar) begin
            if (regs.sub(a)[39:32] == tagRef) heap.upd(regs.sub(a)[11:0], {tagInt, 16'h0, val[15:0]});
            regs.upd(a, {tagInt, 16'h0, val[15:0]});
          end else backtrackOrHalt();
        end
        8'hba: begin                                 // get_nil Ai
          Word d = deref(regs.sub(a));
          if (d[39:32] == tagNil) begin
            // already nil
          end else if (d[39:32] == tagVar) begin
            if (regs.sub(a)[39:32] == tagRef) heap.upd(regs.sub(a)[11:0], {tagNil, 24'h0, 0});
            regs.upd(a, {tagNil, 24'h0, 0});
          end else backtrackOrHalt();
        end
        8'hc0: begin                                 // get_atom A, Ai
          Word d = deref(regs.sub(a));
          if (d[39:32] == tagAtom) begin
            // already atom
          end else if (d[39:32] == tagVar) begin
            if (regs.sub(a)[39:32] == tagRef) heap.upd(regs.sub(a)[11:0], {tagAtom, 24'h0, 0});
            regs.upd(a, {tagAtom, 24'h0, 0});
          end else backtrackOrHalt();
        end
        8'hb4: regs.upd(a, deref(regs.sub(a)));   // read_variable
        // read_variable_without_deref: the register already holds the raw
        // value; only read_variable (0xb4) follows the REF.  A no-op is the
        // correct model behavior, not a stand-in.
        8'ha7: noAction;
        8'h28: noAction;                          // switch_on_non_integer: PC block
        8'h29: noAction;                          // switch_on_non_atom: PC block
        8'h2a: noAction;                          // switch_on_non_list: PC block
        8'h67: narg <= narg;                       // jump: pc set in the PC block
        8'h61: narg <= a;                          // execute: jump to label (b:c)
        8'h63: begin                                // enqueue_goal N, label
          goals.upd(rqt, zeroExtend((b << 8) | c));
          rqt <= rqt + 1;
        end
        8'h69: begin                                // suspend N, label
          goals.upd(rqt, zeroExtend((b << 8) | c));
          rqt <= rqt + 1;
        end
        8'h60: if (rqfp == rqt) haltR <= True;      // proceed: empty queue halts
        8'h71: haltR <= True;                     // halt
        8'h68: begin                                // try_me_else L
          cpLabel.upd(cpsp, zeroExtend((b << 8) | c));
          cpArgPtr.upd(cpsp, argPtr);
          cpNarg.upd(cpsp, narg);
          cpHP.upd(cpsp, hp);
          cpsp <= cpsp + 1;
        end
        8'h73: begin                                // fail
          if (cpsp == 0) haltR <= True;
          else begin
            argPtr <= cpArgPtr.sub(cpsp - 1);
            narg <= cpNarg.sub(cpsp - 1);
            hp <= cpHP.sub(cpsp - 1);
            cpsp <= cpsp - 1;
          end
        end
        // collect_value: emitted as a garbage-collection marker when a
        // value's last use is detected (compiler mrb.kl1).  This model has
        // no collector, so the marker is a no-op by design, not a stand-in.
        8'h1d: noAction;
        // otherwise N, label: commit the current choice point (discard the
        // alternative), then execute the predicate with arity N at label.
        // c8_c16_exe: a = arity, b:c = label.  Halts if there is no CP.
        8'h6a: begin
          if (cpsp == 0) haltR <= True;
          else cpsp <= cpsp - 1;
          narg <= a;
        end
        // wait: passive unification, waits for a variable to be bound.
        // Without a suspension mechanism, halt loudly on an unbound UREF
        // rather than silently proceed; a bound argument advances.
        8'he0: if (deref(regs.sub(a))[39:32] == tagVar) haltR <= True;
        // put_atom: argument-preparation atom write to a register.  The
        // atom ID is inline in the c field (type atom, not r_c40).
        8'h40: regs.upd(a, {tagAtom, 24'h0, c});
        default: if (op >= 8'h41 && op <= 8'h5f) begin
          // put_atom_1 .. put_atom_31: quick forms, atom ID in opcode.
          regs.upd(a, {tagAtom, 24'h0, op - 8'h40});
        end else haltR <= True;                   // unimplemented: stop loud
      endcase
    end else begin
      haltR <= True;
    end
    if (tag == 8'h23 && op == 8'h61) begin
      pcR <= zeroExtend((b << 8) | c);
    end else if (tag == 8'h23 && op == 8'h67) begin
      pcR <= zeroExtend((b << 8) | c);
    end else if (tag == 8'h23 && op == 8'h6a) begin
      pcR <= zeroExtend((b << 8) | c);   // otherwise: jump to label
    end else if (tag == 8'h23 && op == 8'h60 && rqfp != rqt) begin
      pcR <= goals.sub(rqfp);
      rqfp <= rqfp + 1;
    end else if (tag == 8'h23 && op == 8'h69) begin
      // The just-appended label, not goals.sub(rqt): the register update
      // is not visible in this cycle, so reading goals.sub(rqt) would
      // return the stale cell.
      pcR <= (rqfp == rqt) ? zeroExtend((b << 8) | c) : goals.sub(rqfp);
      rqfp <= rqfp + 1;
    end else if (tag == 8'h23 && op == 8'h28 && deref(regs.sub(a))[39:32] != tagInt) begin
      pcR <= zeroExtend((b << 8) | c);   // switch_on_non_integer: not INT -> label
    end else if (tag == 8'h23 && op == 8'h29 && deref(regs.sub(a))[39:32] != tagAtom) begin
      pcR <= zeroExtend((b << 8) | c);   // switch_on_non_atom: not ATOM -> label
    end else if (tag == 8'h23 && op == 8'h2a && deref(regs.sub(a))[39:32] != tagList) begin
      pcR <= zeroExtend((b << 8) | c);   // switch_on_non_list: not LIST -> label
    end else if (tag == 8'h23 && op == 8'h73 && cpsp > 0) begin
      pcR <= zeroExtend(cpLabel.sub(cpsp - 1));      // fail: backtrack to else label
    end else if (tag == 8'h23 && op == 8'hb1 && args.sub(argPtr) != {tagInt, 8'h0, val[23:0]} && cpsp > 0) begin
      pcR <= zeroExtend(cpLabel.sub(cpsp - 1));      // read_integer mismatch -> backtrack
    end else if (tag == 8'h23 && op == 8'hb2 && args.sub(argPtr)[39:32] != tagNil && cpsp > 0) begin
      pcR <= zeroExtend(cpLabel.sub(cpsp - 1));      // read_nil mismatch -> backtrack
    end else if (tag == 8'h23 && op == 8'hb3 && args.sub(argPtr)[39:32] != tagAtom && cpsp > 0) begin
      pcR <= zeroExtend(cpLabel.sub(cpsp - 1));      // read_atom mismatch -> backtrack
    end else if (tag == 8'h23 && op == 8'hf2 && (regs.sub(a)[39:32] != tagInt || regs.sub(b)[39:32] != tagInt || regs.sub(a)[31:0] != regs.sub(b)[31:0]) && cpsp > 0) begin
      pcR <= zeroExtend(cpLabel.sub(cpsp - 1));      // equal mismatch -> backtrack
    end else if (tag == 8'h23 && op == 8'hf3 && (regs.sub(a)[39:32] != tagInt || regs.sub(b)[39:32] != tagInt || regs.sub(a)[31:0] == regs.sub(b)[31:0]) && cpsp > 0) begin
      pcR <= zeroExtend(cpLabel.sub(cpsp - 1));      // not_equal mismatch -> backtrack
    end else if (tag == 8'h23 && op == 8'hb9 && deref(regs.sub(a)) != {tagInt, 16'h0, val[15:0]} && deref(regs.sub(a))[39:32] != tagVar && cpsp > 0) begin
      pcR <= zeroExtend(cpLabel.sub(cpsp - 1));      // get_integer mismatch -> backtrack
    end else if (tag == 8'h23 && op == 8'hba && deref(regs.sub(a))[39:32] != tagNil && deref(regs.sub(a))[39:32] != tagVar && cpsp > 0) begin
      pcR <= zeroExtend(cpLabel.sub(cpsp - 1));      // get_nil mismatch -> backtrack
    end else if (tag == 8'h23 && op == 8'hc0 && deref(regs.sub(a))[39:32] != tagAtom && deref(regs.sub(a))[39:32] != tagVar && cpsp > 0) begin
      pcR <= zeroExtend(cpLabel.sub(cpsp - 1));      // get_atom mismatch -> backtrack
    end else begin
      pcR <= pcR + 1;
    end
    end
  endmethod

  method Bool halted() = haltR;
  method Word readReg(RegNo r) = regs.sub(r);
  method Word readArg(Bit#(8) i) = args.sub(i);
  method Word pc() = pcR;

endmodule

endpackage
