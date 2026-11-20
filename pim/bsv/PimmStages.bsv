// PIM/m core: the two stages.
//
//   mkPimmFetch  reads the cell at a code address and the one after it
//   mkPimmExec   decodes it and carries it out: the clause-selection
//                state (the alternative clause, and the variables
//                guards met unbound), using the data, hash, goal and
//                string boxes for everything multi-cycle
//
// The machine is sequential here: the next fetch waits for the
// instruction before it.  No timing is claimed.
package PimmStages;

import FIFO::*;
import RegFile::*;
import Vector::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmRegs::*;
import PimmDBox::*;
import PimmHBox::*;
import PimmGBox::*;
import PimmSBox::*;

interface PimmFetch;
  method Action enq(Addr pc);
  method ActionValue#(Fetched) out;
endinterface

module mkPimmFetch#(MemPort mem)(PimmFetch);
  FIFO#(Addr) pcs <- mkFIFO;

  Reg#(Bit#(2)) phase <- mkReg(0);   // 0 idle, 1 second read to issue, 2 first cell awaited, 3 second
  Reg#(Cell)    first <- mkRegU;
  FIFO#(Fetched) outQ <- mkFIFO;

  rule second (phase == 1);
    mem.read(pcs.first + 1);
    phase <= 2;
  endrule

  rule got1 (phase == 2);
    let c <- mem.data;
    first <= c;
    phase <= 3;
  endrule

  rule got2 (phase == 3);
    let c <- mem.data;
    outQ.enq(Fetched { pc: pcs.first, word: first, next: c });
    pcs.deq;
    phase <= 0;
  endrule

  method Action enq(Addr pc) if (phase == 0);
    mem.read(pc);
    pcs.enq(pc);
    phase <= 1;
  endmethod

  method ActionValue#(Fetched) out;
    outQ.deq;
    return outQ.first;
  endmethod
endmodule

interface PimmExec;
  method Action newGoal;                       // clear the clause-selection state
  method Action enq(Fetched f);
  method ActionValue#(Step) out;
endinterface

typedef enum { XDecode, XDeref1, XDeref2, XNote2, XUnify, XWake, XHash,
               XSusp1, XSusp2, XSusp3,
               XVar1, XVar2, XEnq, XStrInfo, XStrInfo2, XVec,
               XBIn, XBInW, XBGo, XBWait1, XBWait2, XBStr, XBOut2 } XState deriving (Bits, Eq);

module mkPimmExec#(PimmRegs regs, PimmDBox dbox, PimmHBox hbox, PimmGBox gbox,
                   PimmSBox sbox, MemPort smem)(PimmExec);
  Reg#(Maybe#(Addr)) alt     <- mkReg(tagged Invalid);  // next clause on guard failure
  // the variables guards wanted bound, in the order met (a variable
  // met twice is there twice)
  RegFile#(Bit#(4), Addr) noted <- mkRegFileFull;
  Reg#(Bit#(5))      nNoted  <- mkReg(0);
  FIFO#(Fetched)     inQ     <- mkFIFO;
  FIFO#(Step)        outQ    <- mkFIFO;
  Reg#(XState)       st      <- mkReg(XDecode);
  Reg#(Cell)         opA     <- mkRegU;
  Reg#(Addr)         sGoal   <- mkRegU;     // suspending: the record
  Reg#(Bit#(5))      sI      <- mkRegU;     // suspending: the variable being hooked
  // a body built-in: its inputs, dereferenced, by operand position
  Vector#(4, Reg#(Cell)) vals <- replicateM(mkRegU);
  Reg#(Bit#(3))      bK      <- mkRegU;
  // the structure pointer: where the next write_* stores
  Reg#(Addr)         sp      <- mkRegU;

  // the instruction in hand
  let pc   = inQ.first.pc;
  let ins  = inQ.first.word;
  let ins2 = inQ.first.next;
  Bit#(16) op  = { ins.tag, ins.val[31:24] };
  Bit#(8)  x   = ins.val[23:16];
  Bit#(8)  y   = ins.val[15:8];
  Bit#(8)  z   = ins.val[7:0];
  Bit#(16) c16 = ins.val[15:0];

  // as a body built-in: register operands, three in the first cell and
  // the rest from the top byte of the second (klb_opr.kl1 p(r4..r7))
  Vector#(7, Bit#(8)) operand = newVector;
  operand[0] = x;
  operand[1] = y;
  operand[2] = z;
  operand[3] = ins2.val[31:24];
  operand[4] = ins2.val[23:16];
  operand[5] = ins2.val[15:8];
  operand[6] = ins2.val[7:0];
  Stub stub = fromMaybe(?, stubOf(op));
  Bool arithHere = op == op_b_add || op == op_b_subtract || op == op_b_and || op == op_b_or
                || op == op_b_shift_left;
  Bool builtinHere = arithHere || op == op_new_string
                  || op == op_b_string_element || op == op_set_string_element;
  Addr afterBuiltin = pc + (stub.n > 3 ? 2 : 1);

  function Action finish(Step s);
    action
      inQ.deq;
      outQ.enq(s);
      st <= XDecode;
    endaction
  endfunction

  function Action next() = finish(tagged Next (pc + 1));

  function Action stop(End e);
    action
      case (e)
        EndDone:  $display("E done");
        EndFail:  $display("E fail");
        EndSusp:  $display("E susp");
        EndUnimp: $display("E unimp");
        EndError: $display("E error");
      endcase
      finish(tagged Stop e);
    endaction
  endfunction

  function Action guardFail();
    action
      if (alt matches tagged Valid .a) finish(tagged Next a);
      else stop(EndError);
    endaction
  endfunction

  function Action note(Cell a);
    action
      if (nNoted == 16) fatal("more than 16 variables noted by guards");
      noted.upd(truncate(nNoted), cellAddr(a));
      nNoted <= nNoted + 1;
    endaction
  endfunction

  // The goal goes back to memory as a suspended record, entry = the
  // label, arguments r[0..x), then is hooked on each noted variable.
  function Action suspendGoal();
    action
      gbox.record(fromInteger(lay_SUSPENDED), labelOf(pc, c16), x, False, True);
      st <= XSusp1;
    endaction
  endfunction

  Bool oneOperandGuard = op == op_switch_on_non_integer || op == op_hash_on_constant
                      || op == op_wait || op == op_wait_integer || op == op_string;
  Bool twoOperandGuard = op == op_not_less_than || op == op_less_than || op == op_equal
                      || op == op_subtract || op == op_and;
  // an atom instruction is one cell: opcode byte = base | register, the
  // atom in the low 24 bits; get_atom's base is c0
  Bool isGetAtom = ins.tag == tag_KLB && ins.val[31:29] == 3'b110;
  Cell atomHere = mkCell(tag_ATOMo, zeroExtend(ins.val[23:0]));
  // put_vector_N, N = 2..4: N cells, no header
  Bool isPutVector = op == op_put_vector_2 || op == op_put_vector_3 || op == op_put_vector_4;
  Bit#(8) vectorN = ins.val[31:24] - op_put_vector_0[7:0];

  rule decode (st == XDecode);
    traceI(pc, ins);
    if (ins.tag != tag_GMI && ins.tag != tag_KLB) stop(EndError);
    // ---- clause selection
    else if (op == op_try_me_else) begin
      alt <= tagged Valid labelOf(pc, c16);
      next;
    end
    else if (op == op_otherwise) begin
      // clauses below apply only if none above can
      if (nNoted != 0) suspendGoal;
      else begin
        alt <= tagged Invalid;
        next;
      end
    end
    else if (op == op_suspend) begin
      if (nNoted != 0) suspendGoal;
      else stop(EndFail);
    end
    else if (oneOperandGuard || twoOperandGuard) begin
      dbox.deref(regs.r(x));
      st <= XDeref1;
    end
    // ---- moves and unification
    else if (op == op_put_integer) begin
      regs.wr(x, intCell(c16));
      next;
    end
    else if (op == op_put_value || op == op_put_marked_value) begin
      regs.wr(x, regs.r(y));        // the MRB marking is not modelled
      next;
    end
    else if (op == op_put_variable || op == op_set_variable) begin
      gbox.newVar;
      st <= XVar1;
    end
    else if (op == op_get_integer) begin
      dbox.unify(regs.r(x), intCell(c16));
      st <= XUnify;
    end
    else if (isGetAtom) begin
      dbox.unify(regs.r(zeroExtend(ins.val[28:24])), atomHere);
      st <= XUnify;
    end
    else if (isPutVector) begin
      gbox.alloc(zeroExtend(vectorN));
      st <= XVec;
    end
    else if (op == op_write_atom) begin
      smem.write(sp, atomHere);
      sp <= sp + 1;
      next;
    end
    else if (op == op_write_value) begin
      smem.write(sp, regs.r(x));
      sp <= sp + 1;
      next;
    end
    else if (op == op_write_variable) begin
      // the element itself is the new variable; r[x] refers to it
      smem.write(sp, mkCell(tag_UNDF, 0));
      regs.wr(x, mkCell(tag_REFo, absAddr(sp)));
      sp <= sp + 1;
      next;
    end
    else if (op == op_get_value || op == op_get_bound_value) begin
      dbox.unify(regs.r(x), regs.r(y));
      st <= XUnify;
    end
    else if (op == op_collect_value) next;   // MRB reclamation: not modelled
    // ---- goals
    else if (op == op_set_value) begin
      regs.wa(x, regs.r(y));
      next;
    end
    else if (op == op_enqueue_goal) begin
      gbox.record(fromInteger(lay_READY), labelOf(pc, c16), x, True, True);
      st <= XEnq;
    end
    else if (op == op_execute) begin
      // the same goal goes on as a reduction of the predicate at the label
      alt <= tagged Invalid;
      nNoted <= 0;
      finish(tagged Next labelOf(pc, c16));
    end
    else if (op == op_proceed) stop(EndDone);
    // ---- body built-ins
    else if (builtinHere) begin
      bK <= 0;
      st <= XBIn;
    end
    else stop(EndUnimp);
  endrule

  // ---- guards ----------------------------------------------------------
  rule deref1 (st == XDeref1);
    let a <- dbox.derefResult;
    if (op == op_switch_on_non_integer) begin
      if (isRef(a)) note(a);
      finish(tagged Next (isInt(a) ? pc + 1 : labelOf(pc, c16)));
    end
    else if (op == op_hash_on_constant) begin
      if (isRef(a)) note(a);
      hbox.lookup(pc, a, c16, !isRef(a));
      st <= XHash;
    end
    else if (op == op_wait) begin
      if (isRef(a)) begin
        note(a);
        guardFail;
      end
      else next;
    end
    else if (op == op_wait_integer) begin
      if (isRef(a)) note(a);
      if (isInt(a) && a.val == signExtend(c16)) next;
      else guardFail;
    end
    else if (op == op_string) begin
      // string(S, ^Length, ^Bits)
      if (isRef(a)) note(a);
      if (isStrg(a)) begin
        sbox.info(a);
        st <= XStrInfo;
      end
      else guardFail;
    end
    else begin
      opA <= a;
      dbox.deref(regs.r(y));
      st <= XDeref2;
    end
  endrule

  rule strInfo (st == XStrInfo);
    let r <- sbox.result;
    regs.wr(y, r.a);
    opA <= r.b;
    st <= XStrInfo2;
  endrule

  rule strInfo2 (st == XStrInfo2);
    regs.wr(z, opA);
    next;
  endrule

  // two integer operands: an unbound one is noted and the guard fails
  rule deref2 (st == XDeref2);
    let b <- dbox.derefResult;
    let a = opA;
    Int#(32) ia = unpack(a.val);
    Int#(32) ib = unpack(b.val);
    if (isRef(a) && isRef(b)) begin
      note(a);
      opA <= b;
      st <= XNote2;
    end
    else if (isRef(a) || isRef(b)) begin
      note(isRef(a) ? a : b);
      guardFail;
    end
    else if (!isInt(a) || !isInt(b)) guardFail;
    else if (op == op_subtract || op == op_and) begin
      // guard arithmetic: r[z] := r[x] op r[y]
      regs.wr(z, intC(op == op_subtract ? pack(ia - ib) : (a.val & b.val)));
      next;
    end
    else if ((op == op_not_less_than && ia >= ib) || (op == op_less_than && ia < ib)
             || (op == op_equal && ia == ib)) next;
    else guardFail;
  endrule

  rule note2 (st == XNote2);
    note(opA);
    guardFail;
  endrule

  rule hashed (st == XHash);
    let t <- hbox.target;
    finish(tagged Next t);
  endrule

  // ---- unification -------------------------------------------------------
  rule unified (st == XUnify);
    let r <- dbox.unifyResult;
    case (r) matches
      tagged UOk:      next;
      tagged UWake .s: begin
        gbox.wake(s);
        st <= XWake;
      end
      tagged UFail:    stop(EndFail);
      tagged UUnimp:   stop(EndUnimp);
    endcase
  endrule

  rule woke (st == XWake);
    gbox.done;
    next;
  endrule

  // ---- variables and goals -------------------------------------------------
  rule var1 (st == XVar1);
    let v <- gbox.newVarResult;
    opA <= v;
    if (op == op_put_variable) regs.wr(x, v);
    else regs.wa(x, v);
    st <= XVar2;
  endrule

  rule var2 (st == XVar2);
    regs.wr(y, opA);
    next;
  endrule

  rule vectorMade (st == XVec);
    let a <- gbox.allocResult;
    sp <= a;
    regs.wr(x, mkCell(tag_VECT0o + (vectorN << 1) + 1, absAddr(a)));
    next;
  endrule

  rule enqueued (st == XEnq);
    let g <- gbox.recordResult;
    next;
  endrule

  rule susp1 (st == XSusp1);
    let g <- gbox.recordResult;
    sGoal <= g;
    sI <= 0;
    st <= XSusp2;
  endrule

  rule susp2 (st == XSusp2);
    gbox.hook(sGoal, noted.sub(truncate(sI)));
    st <= XSusp3;
  endrule

  rule susp3 (st == XSusp3);
    gbox.done;
    if (sI + 1 == nNoted) stop(EndSusp);
    else begin
      sI <= sI + 1;
      st <= XSusp2;
    end
  endrule

  // ---- body built-ins ------------------------------------------------------
  // Dereference each input operand in order; if one is unbound the
  // built-in becomes a suspended goal of its stub, hooked on the first
  // such input; otherwise it is carried out.
  rule bIn (st == XBIn);
    if (bK == stub.n) st <= XBGo;
    else if (stub.outs[bK] == 1) bK <= bK + 1;
    else begin
      dbox.deref(regs.r(operand[bK]));
      st <= XBInW;
    end
  endrule

  rule bInW (st == XBInW);
    let v <- dbox.derefResult;
    vals[bK] <= v;
    bK <= bK + 1;
    st <= XBIn;
  endrule

  function Bool waitsOn(Integer i) =
    fromInteger(i) < stub.n && stub.outs[i] == 0 && isRef(vals[i]);

  rule bGo (st == XBGo);
    let a = vals[0];
    let b = vals[1];
    let c = vals[2];
    Int#(32) ia = unpack(a.val);
    Int#(32) ib = unpack(b.val);
    if (waitsOn(0) || waitsOn(1) || waitsOn(2) || waitsOn(3)) begin
      gbox.waitRecord(stub.addr, stub.n, operand, stub.outs);
      st <= XBWait1;
    end
    else if (arithHere) begin
      // r[z] := r[x] op r[y].  A non-integer, or a shift count outside
      // 0..31, is the built-in's exception: not modelled.
      if (!isInt(a) || !isInt(b) || (op == op_b_shift_left && b.val >= 32)) stop(EndUnimp);
      else begin
        Bit#(5) count = truncate(b.val);
        Bit#(32) r = (op == op_b_add) ? pack(ia + ib)
                   : (op == op_b_subtract) ? pack(ia - ib)
                   : (op == op_b_and) ? (a.val & b.val)
                   : (op == op_b_or) ? (a.val | b.val)
                   : (a.val << count);
        regs.wr(z, intC(r));
        finish(tagged Next afterBuiltin);
      end
    end
    else if (op == op_new_string) begin
      // new_string(Length, Bits, ^S)
      if (!isInt(a) || !isInt(b)) stop(EndUnimp);
      else begin
        sbox.newStr(a.val, b.val);
        st <= XBStr;
      end
    end
    else if (op == op_b_string_element) begin
      // string_element(S, I, ^E, ^S1)
      if (!isStrg(a) || !isInt(b)) stop(EndUnimp);
      else begin
        sbox.element(a, b.val);
        st <= XBStr;
      end
    end
    else begin
      // set_string_element(S, I, E, ^S1)
      if (!isStrg(a) || !isInt(b) || !isInt(c)) stop(EndUnimp);
      else begin
        sbox.setElement(a, b.val, c.val);
        st <= XBStr;
      end
    end
  endrule

  rule bWait1 (st == XBWait1);
    let g <- gbox.recordResult;
    Cell v = waitsOn(0) ? vals[0] : (waitsOn(1) ? vals[1] : (waitsOn(2) ? vals[2] : vals[3]));
    gbox.hook(g, cellAddr(v));
    st <= XBWait2;
  endrule

  rule bWait2 (st == XBWait2);
    gbox.done;
    finish(tagged Next afterBuiltin);
  endrule

  rule bStr (st == XBStr);
    let r <- sbox.result;
    if (op == op_new_string) begin
      regs.wr(z, r.a);
      finish(tagged Next afterBuiltin);
    end
    else if (op == op_b_string_element) begin
      regs.wr(z, r.a);
      st <= XBOut2;
    end
    else begin
      regs.wr(operand[3], r.a);
      finish(tagged Next afterBuiltin);
    end
  endrule

  rule bOut2 (st == XBOut2);
    regs.wr(operand[3], vals[0]);
    finish(tagged Next afterBuiltin);
  endrule

  method Action newGoal;
    alt <= tagged Invalid;
    nNoted <= 0;
  endmethod

  method Action enq(Fetched f) = inQ.enq(f);
  method ActionValue#(Step) out;
    outQ.deq;
    return outQ.first;
  endmethod
endmodule

endpackage
