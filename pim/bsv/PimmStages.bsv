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
import PimmVBox::*;
import PimmMBox::*;
import PimmNBox::*;
import PimmShBox::*;
import PimmScsiBox::*;

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
  method Bit#(32) reductions;                  // the goal's so far: executes, proceed
  method Action enq(Fetched f);
  method ActionValue#(Step) out;
endinterface

typedef enum { XDecode, XDeref1, XDeref2, XNote2, XUnify, XWake, XHash,
               XSusp1, XSusp2, XSusp3,
               XVar1, XVar2, XEnq, XStrInfo, XStrInfo2, XVec, XRead, XReuse1, XReuse2, XVEl, XBVec, XBVec2,
               XBIn, XBInW, XBGo, XBWait1, XBWait2, XBStr, XBn1, XBn2, XBn3, XBn4, XBn5, XBn6, XBn7, XBn8,
               XBs1, XBs2, XBs3, XBs4, XBs5, XBs6, XBs7, XBs8, XBs9, XBs10, XBs11, XBsOut, XBOut2, XBVOut, XDiv, XVInfo, XMul, XVPut, XExt, XSCnst, XRAtom, XBVEl, XTagVal, XPack, XBMod, XBHash, XBHash2, XSEq, XShow, XP2C, XP2Ca, XP2Cw1, XP2Cw2, XP2Cw3, XCode1, XCode2, XCode3, XCode4, XC2P1, XC2P2, XC2P3, XC2P4, XC2P5, XAp1, XAp2, XSWh1, XSWh2,
               XMg0, XMg1, XMg2, XMg3, XMi0, XMi1, XMi2, XMi2w, XMi3, XMiU, XMi4, XUStep, XUL1, XUL2,
               XShIn, XShInW, XShGo, XShC1, XShC2, XShC3, XShS,
               XSEl, XSo1, XSo2, XSo3, XSo4, XMark, XMkEl,
               XProc, XBDiv, XBSInfo, XBSInfo2, XGMul, XPv1, XPv2, XPv3, XPv4,
               XTq1, XTq2, XTq3, XTq4, XSTim, XTp0, XTp1, XTp2, XTpE,
               XSoW,
               XNode, XSan, XMv1, XMv2, XMv3, XMv4,
               XShF, XCPr1, XCPr2,
               XReuse3,
               XScI1, XScI2, XScC, XScW, XScO1, XScO2, XScO3, XScO4 } XState deriving (Bits, Eq);

module mkPimmExec#(PimmRegs regs, PimmDBox dbox, PimmHBox hbox, PimmGBox gbox,
                   PimmSBox sbox, PimmVBox vbox, PimmMBox mbox, PimmNBox nbox,
                   MemPort smem,
                   PimmShBox shbox, PimmScsiBox scsi)(PimmExec);
  Reg#(Maybe#(Addr)) alt     <- mkReg(tagged Invalid);  // next clause on guard failure
  // the variables guards wanted bound, in the order met (a variable
  // met twice is there twice)
  RegFile#(Bit#(4), Addr) noted <- mkRegFileFull;
  Reg#(Bit#(5))      nNoted  <- mkReg(0);
  FIFO#(Fetched)     inQ     <- mkFIFO;
  FIFO#(Step)        outQ    <- mkFIFO;
  Reg#(XState)       st      <- mkReg(XDecode);
  Reg#(Cell)         opA     <- mkRegU;
  Reg#(Cell)         opB     <- mkRegU;
  // wait_value on two vectors: the vectors, the element of X, the index
  Reg#(Cell)         pvA     <- mkRegU;
  Reg#(Cell)         pvB     <- mkRegU;
  Reg#(Cell)         pvX     <- mkRegU;
  Reg#(Bit#(32))     pvI     <- mkRegU;
  Reg#(Addr)         sGoal   <- mkRegU;     // suspending: the record
  Reg#(Bit#(5))      sI      <- mkRegU;     // suspending: the variable being hooked
  // a body built-in: its inputs, dereferenced, by operand position
  Vector#(4, Reg#(Cell)) vals <- replicateM(mkRegU);
  Reg#(Bit#(3))      bK      <- mkRegU;
  // the structure pointer: where the next write_* stores
  Reg#(Addr)         sp      <- mkRegU;
  // sp was set by wait_vector_N from a vector reached with every MRB
  // off: read_variable takes its elements as they are
  Reg#(Bool)         spSingle <- mkReg(False);
  Reg#(Bit#(25))     nextAtom <- mkReg(25'h0010000);   // new_atom's counter: ours
  Reg#(Bit#(8))      reuseTag <- mkRegU;
  Reg#(Cell)         vnew    <- mkRegU;
  Reg#(Bit#(8))      packK   <- mkRegU;     // the packed argument in hand
  // the clock (pimm.py INSTRUCTIONS_PER_TICK): the system timer in 1/16
  // msec, one tick per 423 instructions decoded (OURS rate from 615
  // KLIPS on append), counted before the instruction; clk holds the
  // value for the instruction in hand
  Reg#(Bit#(9))      tickSub <- mkReg(0);
  Reg#(Bit#(48))     ticks   <- mkReg(0);
  Reg#(Bit#(48))     clk     <- mkReg(0);
  // multiply_bignum_by_word: the word in hand, the length, Y, the carry,
  // the pass (False: the carry only; True: the words written), whether
  // the product is one word longer, the new string
  Reg#(Bit#(32))     bnI     <- mkRegU;
  Reg#(Bit#(32))     bnN     <- mkRegU;
  Reg#(Bit#(32))     bnY     <- mkRegU;
  Reg#(Bit#(32))     bnCarry <- mkRegU;
  Reg#(Bool)         bnPass2 <- mkRegU;
  Reg#(Bool)         bnExtra <- mkRegU;
  Reg#(Cell)         bnDst   <- mkRegU;
  // subtract_bignum (with bnN = X's length, bnI, bnCarry the borrow,
  // bnPass2, bnDst): Y, its length, whether Y is the larger, the most
  // significant word not 0 (pass 1), the word in hand, the outputs
  Reg#(Cell)         bsY     <- mkRegU;
  Reg#(Bit#(32))     bsM     <- mkRegU;
  Reg#(Bool)         bsSwap  <- mkRegU;
  Reg#(Bit#(32))     bsLast  <- mkRegU;
  Reg#(Bit#(32))     bsW     <- mkRegU;
  Reg#(Cell)         bsZ     <- mkRegU;
  Vector#(5, Reg#(Cell)) sv  <- replicateM(mkRegU);   // string_operation's vector
  Reg#(ScsiResult)   scR     <- mkRegU;     // scsi_command's outputs, being written
  // the reductions of the goal in hand: one per execute and one for its
  // proceed (the shoen's statistics, PimmShBox.bsv)
  Reg#(Bit#(32))     nRed    <- mkReg(0);

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
                || op == op_b_exclusive_or
                || op == op_b_shift_left || op == op_b_shift_right;
  Bool builtinHere = arithHere || op == op_b_multiply || op == op_new_string
                  || op == op_b_string_element || op == op_set_string_element
                  || op == op_new_vector || op == op_set_vector_element
                  || op == op_b_vector_element || op == op_new_instruction
                  || op == op_new_module || op == op_calculate_priority_from_minimum
                  || op == op_change_element_size || op == op_string_operation
                  || op == op_hash || op == op_predicate_to_code || op == op_apply
                  || op == op_b_divide || op == op_b_modulo || op == op_b_string
                  || op == op_calculate_priority_from_current || op == op_supply_atom_number
                  || op == op_scsi_command || op == op_set_timer || op == op_multiply_bignum_word
                  || op == op_subtract_bignum || op == op_b_vector
                  || op == op_code_to_predicate;
  // opcode 76 is numbered by its x field: 4 is the guard
  // tag_and_value(X, ^Tag, ^Value), registers y, z and the next cell's
  // top byte
  Bool isTagAndValue = op == 16'h2376 && x == 4;
  // opcode FC likewise: 3 is the guard floating_point_not_less_than(F1,
  // F2), registers y and z
  Bool isFloatGE = op == 16'h23fc && x == 3;
  // a vector pointer, short (0..6 elements, the size in the tag) or long
  function Bool isVec(Cell c) = (c.tag & 8'hf0) == tag_VECT0o;
  function Bool isLongVec(Cell c) = (c.tag & 8'hfe) == 8'h1e;
  function Bool isList(Cell c) = (c.tag & 8'hfe) == tag_LISTo;
  function Bit#(32) sizeOf(Cell c) = zeroExtend(vectorSize(c));
  Addr afterBuiltin = pc + (stub.n > 3 ? 2 : 1);

  function Action finish(Step s);
    action
      inQ.deq;
      outQ.enq(s);
      st <= XDecode;
    endaction
  endfunction

  // get_constant's constant is the next cell: its unification goes on two on
  function Action next() = finish(tagged Next (pc + (op == op_get_constant ? 2 : 1)));

  function Action stop(End e0);
    action
      // a goal failing inside a shoen is the shoen's exception path:
      // not modelled, so refused
      End e = (e0 == EndFail && gbox.shoen != 0) ? EndUnimp : e0;
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

  // the shoen built-ins of stages 1 and 2 (PimmShBox.bsv); the inputs
  // that are waited for: MinPrio, MaxPrio, ExcepMask, or the handle
  Bool shoenHere = op == op_create_shoen || op == op_start_shoen
                || op == op_shoen_statistics || op == op_remove_shoen
                || op == op_stop_shoen || op == op_abort_shoen || op == op_raise;
  Bit#(3) shoenIns = op == op_create_shoen ? 3 : 1;

  // wait_vector_N, N = 0..6
  Bool isWaitVector = op == op_wait_vector_0 || op == op_wait_vector_2 || op == op_wait_vector_3 || op == op_wait_vector_5
                   || op == op_wait_vector_1 || op == op_wait_vector_4 || op == op_wait_vector_6;
  Bit#(8) waitN = ins.val[31:24] - op_wait_vector_0[7:0];
  Bool oneOperandGuard = op == op_switch_on_non_integer || op == op_hash_on_constant
                      || op == op_switch_on_constant
                      || op == op_wait || op == op_wait_integer || op == op_string
                      || op == op_integer || op == op_wait_constant || op == op_floating_point
                      || op == op_atom || op == op_code
                      || op == op_switch_on_non_atom || op == op_wait_nil || op == op_wait_list
                      || isWaitVector || op == op_switch_on_non_list
                      || op == op_switch_on_non_vector || op == op_vector || op == op_wait_vector;
  Bool twoOperandGuard = op == op_not_less_than || op == op_less_than || op == op_equal
                      || op == op_subtract || op == op_and || op == op_vector_element
                      || op == op_shift_right || op == op_modulo || op == op_wait_value
                      || op == op_add || op == op_exclusive_or || op == op_string_element
                      || op == op_mark_element || op == op_divide || op == op_shift_left
                      || op == op_not_equal || op == op_multiply || op == op_diff;
  function Bool isAtomic(Cell c) = (c.tag & 8'hfe) == tag_INTo || (c.tag & 8'hfe) == tag_ATOMo;
  function Bool sameAtomic(Cell p, Cell q) = (p.tag & 8'hfe) == (q.tag & 8'hfe) && p.val == q.val;
  // an atom instruction is one cell: opcode byte = base | register, the
  // atom in the low 24 bits; get_atom's base is c0
  Bool isGetAtom = ins.tag == tag_KLB && ins.val[31:29] == 3'b110;
  // wait_atom's base is 80
  Bool isWaitAtom = ins.tag == tag_KLB && ins.val[31:29] == 3'b100;
  // put_atom's base is 40
  Bool isPutAtom = ins.tag == tag_KLB && ins.val[31:29] == 3'b010;
  // set_atom's base is 00: the goal argument in the opcode byte
  Bool isSetAtom = ins.tag == tag_KLB && ins.val[31:28] == 4'b0000;
  Cell atomHere = mkCell(tag_ATOMo, zeroExtend(ins.val[23:0]));
  // put_vector_N, N = 2..4: N cells, no header
  Bool isPutVector = op == op_put_vector_1 || op == op_put_vector_2 || op == op_put_vector_3
                  || op == op_put_vector_4 || op == op_put_vector_5 || op == op_put_vector_6;
  Bit#(8) vectorN = ins.val[31:24] - op_put_vector_0[7:0];

  rule decode (st == XDecode);
    traceI(pc, ins);
    clk <= ticks;
    if (tickSub == 422) begin
      tickSub <= 0;
      ticks <= ticks + 1;
    end
    else tickSub <= tickSub + 1;
    if (ins.tag != tag_GMI && ins.tag != tag_KLB) stop(EndError);
    // ---- clause selection
    else if (op == op_try_me_else) begin
      alt <= tagged Valid labelOf(pc, c16);
      next;
    end
    else if (op == op_jump) begin
      // an unconditional branch (VPIM klb_jump, PDSS KL1B_JUMP)
      finish(tagged Next labelOf(pc, c16));
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
      // no clause applies inside a shoen: the exception
      // reduction_failure, 9, tag 1 << 25, Info {Pe, Code, ArgV}, Code
      // the label as a code, ArgV r[0..x) (PimmShBox.bsv; ref/pimm/
      // pimm.py i_suspend).  An arity of 0 or above 6 is refused
      else if (gbox.shoen != 0) begin
        if (x == 0 || x > 6) stop(EndUnimp);
        else begin
          shbox.exception(fromInteger(lay_EXC_REDUCTION_FAILURE), 32'h02000000,
                          mkCell(tag_COD, absAddr(labelOf(pc, c16))), ?, x);
          st <= XShF;
        end
      end
      else stop(EndFail);
    end
    // read_eagerly, what the compiler writes for `alternatively.`: an
    // eager read of external references (TM-1044).  One processor has
    // none: nothing is done, the variables noted so far stay noted
    else if (op == op_read_eagerly) next;
    else if (isWaitAtom) begin
      dbox.deref(regs.r(zeroExtend(ins.val[28:24])));
      st <= XDeref1;
    end
    else if (isTagAndValue || isFloatGE) begin
      dbox.deref(regs.r(y));
      st <= XDeref1;
    end
    else if (op == op_display_console) begin
      dbox.deref(regs.r(x));
      st <= XDeref1;
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
    else if (op == op_put_constant) begin
      regs.wr(x, ins2);            // the whole next cell
      finish(tagged Next (pc + 2));
    end
    else if (op == op_put_nil) begin
      regs.wr(x, mkCell(tag_ATOMo, 0));     // nil is the atom 0
      next;
    end
    else if (op == op_put_value) begin
      regs.wr(x, regs.r(y));
      next;
    end
    else if (op == op_save || op == op_restore) begin
      // the compiler's register spill to the work slots (PimmRegs.bsv);
      // a slot of 256 or more is refused
      if (c16 >= 256) stop(EndUnimp);
      else begin
        if (op == op_save) regs.wv(truncate(c16), regs.r(x));
        else regs.wr(x, regs.v(truncate(c16)));
        next;
      end
    end
    else if (op == op_put_marked_value || op == op_set_marked_value || op == op_write_marked_value) begin
      // "the MRB of the destination is always set.  They are for
      // reference duplication" (TR-248): the source is marked first
      // (PDSS), then copied
      let src = op == op_write_marked_value ? x : y;
      regs.wr(src, marked(regs.r(src)));
      opA <= marked(regs.r(src));
      st <= XMark;
    end
    else if (op == op_put_variable || op == op_set_variable || op == op_put_marked_variable
             || op == op_set_marked_variable) begin
      gbox.newVar;
      st <= XVar1;
    end
    else if (op == op_get_integer) begin
      dbox.unify(regs.r(x), intCell(c16));
      st <= XUnify;
    end
    else if (op == op_get_constant) begin
      // get_constant(X, C): r[x] unified with the whole next cell
      dbox.unify(regs.r(x), ins2);
      st <= XUnify;
    end
    else if (isGetAtom) begin
      dbox.unify(regs.r(zeroExtend(ins.val[28:24])), atomHere);
      st <= XUnify;
    end
    else if (isPutAtom) begin
      regs.wr(zeroExtend(ins.val[28:24]), atomHere);
      next;
    end
    else if (op == op_get_nil) begin
      dbox.unify(regs.r(x), mkCell(tag_ATOMo, 0));
      st <= XUnify;
    end
    else if (op == op_put_list) begin
      gbox.alloc(2);       // car, then cdr
      st <= XVec;
    end
    else if (op == op_scsi_where) begin
      // scsi_where(^Info): [{0, 0, 0, 6}], one SCSI port on cluster 0,
      // processor 0, port 0, own unit 6 (the stand-in's single-FEP
      // value, PIMOS bios/boot/scsi_conf.kl1): a vector of four, then
      // the list cell, in one allocation of six cells
      gbox.alloc(6);
      st <= XSWh1;
    end
    else if (op == op_scsi_init) begin
      // scsi_init(^Obj, ^TargetInterruptVector, ^Info): Obj = 1, then
      // the SCSI box (PimmScsiBox.bsv): the device's buffer size, the
      // two vectors.  The values are OURS (bios/scsi/scsi_blt.kl1)
      regs.wr(x, intC(1));
      scsi.init;
      st <= XScI1;
    end
    else if (op == op_current_processor) begin
      // current_processor(^Current, ^X, ^Y): no input, never waits.  One
      // processor here: 0, 1, 1 (PDSS's values), written in that order
      regs.wr(x, intC(0));
      st <= XCPr1;
    end
    else if (op == op_system_timer) begin
      // system_timer(^X1, ^X2), a guard with no input: the clock's
      // upper 16 bits, then (sysTimerLow) its lower 32
      regs.wr(x, intC(zeroExtend(ticks[47:32])));
      st <= XSTim;
    end
    else if (op == op_current_node) begin
      // current_node(^NodeNumber, ^TotalNode): no input, never waits.
      // One node here (ours): 0, then 1 (nodeTotal)
      regs.wr(x, intC(0));
      st <= XNode;
    end
    else if (op == op_new_atom) begin
      // new_atom(^Atom): the next of a counter; which numbers is ours
      if (nextAtom[24] == 1) stop(EndUnimp);
      else begin
        regs.wr(x, mkCell(tag_ATOMo, zeroExtend(nextAtom)));
        nextAtom <= nextAtom + 1;
        next;
      end
    end
    else if (op == op_put_vector_0) begin
      regs.wr(x, mkCell(tag_VECT0o, 0));     // the empty vector: no cells
      next;
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
    else if (op == op_put_vector) begin
      // the general form: the size is the low 16 bits.  The image
      // uses it for 7, 8 and 10 elements only; below 7 it is refused
      if (c16 < 7) stop(EndUnimp);
      else begin
        vbox.build(zeroExtend(c16));
        st <= XVPut;
      end
    end
    else if (op == op_write_integer) begin
      // the integer is the low 24 bits, signed (the assembler's c24
      // form: klb_opr.kl1 p(c24, ..), p(c40, ..))
      smem.write(sp, intC(signExtend(ins.val[23:0])));
      sp <= sp + 1;
      next;
    end
    else if (op == op_write_nil) begin
      smem.write(sp, mkCell(tag_ATOMo, 0));
      sp <= sp + 1;
      next;
    end
    else if (op == op_write_value) begin
      smem.write(sp, regs.r(x));
      sp <= sp + 1;
      next;
    end
    // read_variable_without_deref: as read_variable here (neither
    // dereferences; library/compiler/regass.kl1 writes it for
    // read_variable when the structure is collected)
    else if (op == op_read_variable || op == op_read_atom || op == op_read_variable_without_deref) begin
      smem.read(sp);
      st <= XRead;
    end
    else if (op == op_put_reused_structure) begin
      dbox.deref(regs.r(y));
      st <= XReuse1;
    end
    else if (op == op_write_variable || op == op_write_marked_variable) begin
      // the element itself is the new variable; r[x] refers to it.
      // marked: the variable is referenced more than once, MRB on
      smem.write(sp, mkCell(tag_UNDF, 0));
      regs.wr(x, mkCell(op == op_write_marked_variable ? tag_REFx : tag_REFo, absAddr(sp)));
      sp <= sp + 1;
      next;
    end
    else if (op == op_get_value || op == op_get_bound_value) begin
      dbox.unify(regs.r(x), regs.r(y));
      st <= XUnify;
    end
    else if (op == op_collect_value || op == op_collect_vector || op == op_collect_list) next;   // MRB reclamation: not modelled
    else if (op == op_put_structured_constant) begin
      // r[x] := the cell at the label, in the module's GC area
      smem.read(labelOf(pc, c16));
      st <= XSCnst;
    end
    // ---- goals
    else if (op == op_set_value) begin
      regs.wa(x, regs.r(y));
      next;
    end
    else if (op == op_set_integer) begin
      regs.wa(x, intCell(c16));
      next;
    end
    else if (op == op_set_nil) begin
      regs.wa(x, mkCell(tag_ATOMo, 0));
      next;
    end
    else if (isSetAtom) begin
      regs.wa(zeroExtend(ins.val[27:24]), atomHere);
      next;
    end
    else if (op == op_enqueue_goal_with_priority) begin
      // two cells: the priority's register, the label; the arity in the
      // next cell's top byte (klb_opr.kl1 p(r_c16_c8_exe)).  The
      // priority must be an integer and is then dropped: one ready
      // queue here, where the machine has a goal stack per priority
      if (!isInt(regs.r(x)) || ins2.val[31:24] > 11) stop(EndUnimp);
      else begin
        gbox.record(fromInteger(lay_READY), labelOf(pc, c16), ins2.val[31:24], True, True);
        st <= XEnq;
      end
    end
    else if (op == op_enqueue_goal_to_processor) begin
      // Goal@processor(N), the operands of enqueue_goal_with_priority:
      // the processor's register, the label; the arity in the next
      // cell's top byte.  One processor here, number 0 (ours)
      dbox.deref(regs.r(x));
      st <= XProc;
    end
    else if (op == op_enqueue_goal) begin
      // A goal has 11 argument slots; the compiler packs the arguments
      // from the 11th on into a vector (library/compiler/pack.kl1,
      // max_goal_slots).  It is spread into the argument registers
      // here, as the goal is made (where the firmware does it is not
      // known), and the record holds every argument.
      if (x > 11) begin
        // a short vector of exactly the arguments left over
        if (x > 16 || (regs.a(11).tag & 8'hfe) != tag_VECT0o + ((truncate(x) - 10) << 1))
          stop(EndUnimp);
        else begin
          opA <= regs.a(11);
          packK <= 0;
          vbox.element(regs.a(11), 0);
          st <= XPack;
        end
      end
      else begin
        gbox.record(fromInteger(lay_READY), labelOf(pc, c16), x, True, True);
        st <= XEnq;
      end
    end
    else if (op == op_execute) begin
      // the same goal goes on as a reduction of the predicate at the label
      alt <= tagged Invalid;
      nNoted <= 0;
      nRed <= nRed + 1;
      finish(tagged Next labelOf(pc, c16));
    end
    else if (op == op_execute_external) begin
      // the same goal goes on in another module: the hash box finds
      // the predicate from the descriptor at the label
      hbox.external(labelOf(pc, c16));
      st <= XExt;
    end
    else if (op == op_enqueue_goal_external) begin
      // enqueue_goal with the predicate found as execute_external
      // finds it (the same operand type, klb_opr.kl1 p(c8_c16_ext))
      if (x > 11) stop(EndUnimp);
      else begin
        hbox.external(labelOf(pc, c16));
        st <= XExt;
      end
    end
    else if (op == op_merge) begin
      // merge(Out, ^In) as compiled (compiler/blt.kl1): the merger box
      // makes the record and the input variable, and a goal of the
      // stub merge_in waits on that variable (PimmNBox.bsv: ours)
      dbox.deref(regs.r(x));
      st <= XMg0;
    end
    else if (op == op_merge_in) begin
      // the merger's step: not a PIM/m instruction, only at its stub
      if (pc != mergeInStub) stop(EndUnimp);
      else begin
        dbox.deref(regs.r(x));
        st <= XMi0;
      end
    end
    else if (op == op_to_processor) begin
      // the waiting goal of Goal@processor(P): not a PIM/m instruction,
      // only at its stub (asm/pimm_stubs.py TO_PROCESSOR)
      if (z > 11 || pc != toProcStub + 2 * zeroExtend(z)) stop(EndUnimp);
      else begin
        dbox.deref(regs.r(x));
        st <= XTp0;
      end
    end
    else if (op == op_unify_step) begin
      // the step of a unification of two structures: not a PIM/m
      // instruction, only at its stub (asm/pimm_stubs.py)
      let sa = regs.r(x);
      Bit#(32) size = ((sa.tag & 8'hfe) == tag_LISTo) ? 2 : zeroExtend(((sa.tag & 8'hfe) - tag_VECT0o) >> 1);
      let ix = regs.r(z).val;
      if (pc != unifyStepStub) stop(EndUnimp);
      else if (isLongVec(sa)) begin
        // vectors of seven or more: sizes and elements from the
        // descriptors (rules uLong1, uLong2)
        vbox.info(sa);
        st <= XUL1;
      end
      else if (ix == size) next;
      else begin
        regs.wr(z, intC(ix + 1));
        dbox.step(sa, regs.r(y), truncate(ix));
        st <= XUStep;
      end
    end
    // ---- the shoen: create_shoen, start_shoen (rules below)
    else if (shoenHere) begin
      bK <= 0;
      vals[3] <= intC(0);          // create_shoen does not wait for Code
      st <= XShIn;
    end
    else if (op == op_proceed) begin
      nRed <= nRed + 1;
      stop(EndDone);
    end
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
    if (isTagAndValue) begin
      // the tag as it stands (whether an MRB bit is returned is not
      // established), then the value
      if (isRef(a)) begin
        note(a);
        guardFail;
      end
      else begin
        regs.wr(z, intC(zeroExtend(a.tag)));
        opA <= a;
        st <= XTagVal;
      end
    end
    else if (op == op_display_console) begin
      // display_console(X): the value as it is now, to the console
      // trace; a string's cells by the string box.  Never waits.
      traceC(a);
      if (isStrg(a)) begin
        sbox.show(a);
        st <= XShow;
      end
      else next;
    end
    else if (op == op_code) begin
      // guard code(X, ^Arity, ^Module, ^Position): the whole tag is
      // compared (COD and MOD differ in the low bit, which is no MRB
      // from 20h on); the predicate head is two cells before the code
      if (isRef(a)) note(a);
      if (a.tag != tag_COD) guardFail;
      else begin
        opA <= a;
        smem.read(cellAddr(a) - 2);
        st <= XCode1;
      end
    end
    else if (isWaitAtom) begin
      if (isRef(a)) note(a);
      if ((a.tag & 8'hfe) == tag_ATOMo && a.val == atomHere.val) next;
      else guardFail;
    end
    else if (op == op_switch_on_non_atom) begin
      if (isRef(a)) note(a);
      finish(tagged Next ((a.tag & 8'hfe) == tag_ATOMo ? pc + 1 : labelOf(pc, c16)));
    end
    else if (op == op_wait_nil) begin
      if (isRef(a)) note(a);
      if ((a.tag & 8'hfe) == tag_ATOMo && a.val == 0) next;
      else guardFail;
    end
    else if (op == op_wait_list) begin
      if (isRef(a)) note(a);
      if ((a.tag & 8'hfe) == tag_LISTo) begin
        sp <= truncate(a.val);
        spSingle <= False;
        next;
      end
      else guardFail;
    end
    else if (op == op_switch_on_non_integer) begin
      if (isRef(a)) note(a);
      finish(tagged Next (isInt(a) ? pc + 1 : labelOf(pc, c16)));
    end
    else if (op == op_hash_on_constant) begin
      if (isRef(a)) note(a);
      hbox.lookup(pc, a, c16, !isRef(a));
      st <= XHash;
    end
    else if (op == op_switch_on_constant) begin
      if (isRef(a)) note(a);
      hbox.scan(pc, a, c16, !isRef(a));
      st <= XHash;
    end
    else if (op == op_wait) begin
      if (isRef(a)) begin
        note(a);
        guardFail;
      end
      else next;
    end
    else if (op == op_switch_on_non_list) begin
      if (isRef(a)) note(a);
      if ((a.tag & 8'hfe) == tag_LISTo) begin
        sp <= truncate(a.val);
        spSingle <= False;
        next;
      end
      else finish(tagged Next labelOf(pc, c16));
    end
    else if (op == op_switch_on_non_vector) begin
      // two cells, the label in the second; only the branch is modelled
      if (isRef(a)) note(a);
      if (isLongVec(a)) begin
        vbox.info(a);                 // the size is in the descriptor
        st <= XVInfo;
      end
      else if (isVec(a)) begin
        // r[y] := the number of elements ("Ari" in the compiler's
        // index.kl1); the structure pointer at the first
        regs.wr(y, intC(sizeOf(a)));
        sp <= truncate(a.val);
        spSingle <= False;
        finish(tagged Next (pc + 2));
      end
      else finish(tagged Next labelOf(pc, ins2.val[15:0]));
    end
    else if (op == op_vector) begin
      // guard vector(X, ^Size)
      if (isRef(a)) begin
        note(a);
        guardFail;
      end
      else if (isLongVec(a)) begin
        vbox.info(a);
        st <= XVInfo;
      end
      else if (isVec(a)) begin
        regs.wr(y, intC(sizeOf(a)));
        next;
      end
      else guardFail;
    end
    else if (op == op_wait_vector) begin
      // the general form, a vector of 7 or more, the length the low 16
      // bits (assembler klb_opr.kl1 p(r_vector, ..) Length>6); the
      // length is in the descriptor
      if (isRef(a)) note(a);
      if (c16 < 7) stop(EndUnimp);
      else if (isLongVec(a)) begin
        opA <= a;
        vbox.info(a);
        st <= XVInfo;
      end
      else guardFail;
    end
    else if (isWaitVector) begin
      if (isRef(a)) note(a);
      if ((a.tag & 8'hfe) == tag_VECT0o + (waitN << 1)) begin
        sp <= truncate(a.val);
        spSingle <= a.tag[0] == 0;
        next;
      end
      else guardFail;
    end
    else if (op == op_wait_integer) begin
      if (isRef(a)) note(a);
      if (isInt(a) && a.val == signExtend(c16)) next;
      else guardFail;
    end
    else if (op == op_wait_constant) begin
      // two cells: the constant is the whole next cell.  Atomic values
      // only; a structure is refused
      if (isRef(a)) begin
        note(a);
        guardFail;
      end
      else if (!isAtomic(a) || !isAtomic(ins2)) stop(EndUnimp);
      else if (sameAtomic(a, ins2)) finish(tagged Next (pc + 2));
      else guardFail;
    end
    else if (op == op_integer) begin
      if (isRef(a)) note(a);
      if (isInt(a)) next;
      else guardFail;
    end
    else if (op == op_atom) begin
      if (isRef(a)) note(a);
      if ((a.tag & 8'hfe) == tag_ATOMo) next;
      else guardFail;
    end
    else if (op == op_floating_point) begin
      // the type test only: there is no floating point arithmetic
      if (isRef(a)) note(a);
      if ((a.tag & 8'hfe) == tag_FLTo) next;
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
      dbox.deref(regs.r(isFloatGE ? z : y));
      st <= XDeref2;
    end
  endrule

  rule tagValue (st == XTagVal);
    regs.wr(ins2.val[31:24], intC(opA.val));
    finish(tagged Next (pc + 2));
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
    if (op == op_wait_value && isRef(a) && isRef(b) && a.val == b.val)
      stop(EndUnimp);              // one variable twice: not modelled
    else if (isRef(a) && isRef(b)) begin
      note(a);
      opA <= b;
      st <= XNote2;
    end
    else if (isRef(a) || isRef(b)) begin
      note(isRef(a) ? a : b);
      guardFail;
    end
    else if (isFloatGE) begin
      // "If both are floating points and ... succeeds.  Otherwise it
      // fails": no floating point here, so two floats are refused
      if ((a.tag & 8'hfe) == tag_FLTo && (b.tag & 8'hfe) == tag_FLTo) stop(EndUnimp);
      else guardFail;
    end
    else if (op == op_wait_value && (isVec(a) || isVec(b) || isList(a) || isList(b))) begin
      // two vectors of 0..6 elements, element by element (PDSS's
      // passive unification as far as docs/pimm_semantics.md takes
      // it); a vector against anything else fails; a list or a long
      // vector is refused
      if (isList(a) || isList(b) || isLongVec(a) || isLongVec(b)) stop(EndUnimp);
      else if (!isVec(a) || !isVec(b) || sizeOf(a) != sizeOf(b)) guardFail;
      else if (sizeOf(a) == 0) next;
      else begin
        pvA <= a;
        pvB <= b;
        pvI <= 0;
        vbox.element(a, 0);
        st <= XPv1;
      end
    end
    else if (op == op_wait_value && isStrg(a) && isStrg(b)) begin
      // two strings: the same when every word is
      sbox.equal(a, b);
      st <= XSEq;
    end
    else if (op == op_wait_value && (isStrg(a) || isStrg(b))
             && (isStrg(a) || isAtomic(a)) && (isStrg(b) || isAtomic(b)))
      guardFail;                   // a string and an atomic value
    else if (op == op_wait_value) begin
      // the guard X = Y, for atomic values and strings; lists and
      // vectors are refused
      if (!isAtomic(a) || !isAtomic(b)) stop(EndUnimp);
      else if (sameAtomic(a, b)) next;
      else guardFail;
    end
    else if (op == op_diff) begin
      // diff(X, Y), X \= Y: fails if they are equal (manual); one
      // atomic and the other not: never equal (KLIC gblt_diff, PDSS
      // g_diff); two that are not atomic are refused
      if (!isAtomic(a) && !isAtomic(b)) stop(EndUnimp);
      else if (isAtomic(a) && isAtomic(b) && sameAtomic(a, b)) guardFail;
      else next;
    end
    else if (op == op_vector_element) begin
      // guard vector_element(Vector, Position, ^Element)
      // the vector box checks a long vector's size
      if (!isVec(a) || !isInt(b) || (!isLongVec(a) && b.val >= sizeOf(a))) guardFail;
      else begin
        vbox.element(a, b.val);
        st <= XVEl;
      end
    end
    else if (op == op_mark_element) begin
      // mark_element(Vector, Position): the element's MRB on, in the
      // vector
      if (!isVec(a) || !isInt(b)) stop(EndUnimp);
      else begin
        vbox.markElement(a, b.val);
        st <= XMkEl;
      end
    end
    else if (op == op_string_element) begin
      // guard string_element(String, Position, ^Element): the string
      // box says whether the position is inside
      if (!isStrg(a) || !isInt(b)) guardFail;
      else begin
        sbox.tryElement(a, b.val);
        st <= XSEl;
      end
    end
    else if (!isInt(a) || !isInt(b)) guardFail;
    else if (op == op_exclusive_or) begin
      regs.wr(z, intC(a.val ^ b.val));
      next;
    end
    else if (op == op_modulo || op == op_divide) begin
      // a zero divisor fails the guard, and for divide the one
      // overflow, the least integer by -1; the divide box takes 32 steps
      if (b.val == 0 || (op == op_divide && a.val == 32'h80000000 && b.val == 32'hffffffff)) guardFail;
      else begin
        mbox.divide(a.val, b.val);
        st <= XDiv;
      end
    end
    else if (op == op_shift_right || op == op_shift_left) begin
      // logical; a count outside 0..31 fails the guard
      Bit#(5) count = truncate(b.val);
      if (b.val >= 32) guardFail;
      else begin
        regs.wr(z, intC(op == op_shift_left ? a.val << count : a.val >> count));
        next;
      end
    end
    else if (op == op_multiply) begin
      // guard multiply in the multiply box; an overflow fails the
      // guard (manual, multiply: "Fail, Exception")
      mbox.multiply(a.val, b.val);
      st <= XGMul;
    end
    else if (op == op_add) begin
      // an overflow fails the guard (manual)
      Int#(33) sum = signExtend(ia) + signExtend(ib);
      Bit#(33) sb = pack(sum);
      if (sb[32] != sb[31]) guardFail;
      else begin
        regs.wr(z, intC(sb[31:0]));
        next;
      end
    end
    else if (op == op_subtract || op == op_and) begin
      // guard arithmetic: r[z] := r[x] op r[y]
      regs.wr(z, intC(op == op_subtract ? pack(ia - ib) : (a.val & b.val)));
      next;
    end
    else if ((op == op_not_less_than && ia >= ib) || (op == op_less_than && ia < ib)
             || (op == op_equal && ia == ib)
             || (op == op_not_equal && ia != ib)) next;
    else guardFail;
  endrule

  rule multiplied (st == XMul);
    let p <- mbox.product;
    if (p.overflow) stop(EndUnimp);
    else begin
      regs.wr(z, intC(p.value));
      finish(tagged Next afterBuiltin);
    end
  endrule

  // guard multiply: the product, or the guard fails on an overflow
  rule gMultiplied (st == XGMul);
    let p <- mbox.product;
    if (p.overflow) guardFail;
    else begin
      regs.wr(z, intC(p.value));
      next;
    end
  endrule

  // wait_value on two vectors: element i of X, then of Y, each
  // dereferenced; an unbound one is noted (X's first), an element of X
  // that is not atomic is refused
  rule pv1 (st == XPv1);
    let r <- vbox.result;
    dbox.deref(r.a);
    st <= XPv2;
  endrule

  rule pv2 (st == XPv2);
    let x <- dbox.derefResult;
    pvX <= x;
    vbox.element(pvB, pvI);
    st <= XPv3;
  endrule

  rule pv3 (st == XPv3);
    let r <- vbox.result;
    dbox.deref(r.a);
    st <= XPv4;
  endrule

  rule pv4 (st == XPv4);
    let y <- dbox.derefResult;
    let x = pvX;
    if (isRef(x)) begin
      note(x);
      guardFail;
    end
    else if (!isAtomic(x)) stop(EndUnimp);
    else if (isRef(y)) begin
      note(y);
      guardFail;
    end
    else if (!sameAtomic(x, y)) guardFail;
    else if (pvI + 1 == sizeOf(pvA)) next;
    else begin
      pvI <= pvI + 1;
      vbox.element(pvA, pvI + 1);
      st <= XPv1;
    end
  endrule

  rule divided (st == XDiv);
    let d <- mbox.result;
    regs.wr(z, intC(op == op_divide ? d.quotient : d.remainder));
    next;
  endrule

  rule bDivided (st == XBDiv);
    let d <- mbox.result;
    regs.wr(z, intC(op == op_b_divide ? d.quotient : d.remainder));
    finish(tagged Next afterBuiltin);
  endrule

  // b_string: the size, the element width, then the string itself
  rule bStrInfo (st == XBSInfo);
    let r <- sbox.result;
    regs.wr(y, r.a);
    opA <= r.b;
    st <= XBSInfo2;
  endrule

  rule bStrInfo2 (st == XBSInfo2);
    regs.wr(z, opA);
    st <= XBOut2;
  endrule

  // supply_atom_number: Done, the fresh variable
  rule supplied (st == XSan);
    let v <- gbox.newVarResult;
    regs.wr(z, v);
    finish(tagged Next afterBuiltin);
  endrule

  // current_node: the second output, the total number of nodes
  rule sysTimerLow (st == XSTim);
    regs.wr(y, intC(clk[31:0]));
    next;
  endrule

  rule nodeTotal (st == XNode);
    regs.wr(y, intC(1));
    next;
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
      tagged UGoal .q: begin
        gbox.unifyGoal(q.a, q.b);
        st <= XWake;
      end
    endcase
  endrule

  // an element of two structures unified: the instruction is taken again
  rule uLong1 (st == XUL1);
    let r <- vbox.result;
    opA <= mkCell(regs.r(x).tag, r.b.val);    // a's first element
    opB <= r.a;                               // a's size
    vbox.info(regs.r(y));
    st <= XUL2;
  endrule

  rule uLong2 (st == XUL2);
    let r <- vbox.result;
    let ix = regs.r(z).val;
    if (r.a.val != opB.val) stop(EndFail);
    else if (ix == opB.val) next;
    else begin
      regs.wr(z, intC(ix + 1));
      dbox.step(mkCell(opA.tag, opA.val + ix), mkCell(regs.r(y).tag, r.b.val + ix), 0);
      st <= XUStep;
    end
  endrule

  rule unifyStepped (st == XUStep || st == XMiU);
    let r <- dbox.unifyResult;
    case (r) matches
      tagged UOk:      finish(tagged Next pc);
      tagged UWake .s: begin
        gbox.wake(s);
        st <= XMi2w;
      end
      tagged UFail:    stop(EndFail);
      tagged UUnimp:   stop(EndUnimp);
      tagged UGoal .q: begin
        gbox.unifyGoal(q.a, q.b);
        st <= XMi2w;
      end
    endcase
  endrule

  rule woke (st == XWake);
    gbox.done;
    next;
  endrule

  // ---- variables and goals -------------------------------------------------
  rule var1 (st == XVar1);
    let v0 <- gbox.newVarResult;
    // put_/set_marked_variable: both references with the MRB on (PDSS)
    let v = (op == op_put_marked_variable || op == op_set_marked_variable) ? marked(v0) : v0;
    opA <= v;
    if (op == op_put_variable || op == op_put_marked_variable) regs.wr(x, v);
    else regs.wa(x, v);
    st <= XVar2;
  endrule

  rule var2 (st == XVar2);
    regs.wr(y, opA);
    next;
  endrule

  // the second half of a marked instruction: the copy
  rule markCopy (st == XMark);
    if (op == op_put_marked_value) regs.wr(x, opA);
    else if (op == op_set_marked_value) regs.wa(x, opA);
    else begin
      smem.write(sp, opA);
      sp <= sp + 1;
    end
    next;
  endrule

  rule markedElement (st == XMkEl);
    let r <- vbox.result;
    if (!r.ok) stop(EndUnimp);
    else next;
  endrule

  rule vectorMade (st == XVec);
    let a <- gbox.allocResult;
    sp <= a;
    spSingle <= False;
    regs.wr(x, op == op_put_list ? mkCell(tag_LISTo + 1, absAddr(a))
                                 : mkCell(tag_VECT0o + (vectorN << 1) + 1, absAddr(a)));
    next;
  endrule

  // the next element of the structure being read; an unbound element
  // is taken as a reference to it
  rule readElement (st == XRead);
    let d <- smem.data;
    // the cell goes on holding it, so its MRB is on, unless the vector
    // was reached with every MRB off (PDSS read_element)
    Cell el = isUnboundCell(d) ? mkCell(spSingle ? tag_REFo : tag_REFx, absAddr(sp))
                               : (spSingle ? d : marked(d));
    if (op == op_read_atom) begin
      dbox.deref(el);
      st <= XRAtom;
    end
    else begin
      regs.wr(x, el);
      sp <= sp + 1;
      next;
    end
  endrule

  // read_atom: the element must be the atom; an unbound one is noted
  rule readAtom (st == XRAtom);
    let a <- dbox.derefResult;
    if (isRef(a)) note(a);
    if ((a.tag & 8'hfe) == tag_ATOMo && a.val == atomHere.val) begin
      sp <= sp + 1;
      next;
    end
    else guardFail;
  endrule

  // put_reused_structure: nothing is ever reused (no reference counts);
  // new cells under the tag of the structure in r[y]
  rule reuse1 (st == XReuse1);
    let a <- dbox.derefResult;
    reuseTag <= a.tag;
    if (isLongVec(a)) begin
      // a vector of seven or more has its descriptor: the new one gets
      // its own (the vector box, as put_vector).  Fewer than seven
      // cells under a long vector's tag would be no vector: refused
      if (z < 7) stop(EndUnimp);
      else begin
        vbox.build(zeroExtend(z));
        st <= XReuse3;
      end
    end
    else begin
      gbox.alloc(zeroExtend(z));
      st <= XReuse2;
    end
  endrule

  rule reuse3 (st == XReuse3);
    let r <- vbox.result;
    regs.wr(x, mkCell(reuseTag, r.a.val));
    sp <= truncate(r.b.val);
    spSingle <= False;
    next;
  endrule

  rule reuse2 (st == XReuse2);
    let a <- gbox.allocResult;
    sp <= a;
    spSingle <= False;
    regs.wr(x, mkCell(reuseTag, absAddr(a)));
    next;
  endrule

  rule spread (st == XPack);
    let r <- vbox.result;
    if (!r.ok) stop(EndUnimp);          // the vector is too short
    else begin
      regs.wa(11 + packK, r.a);
      if (packK + 11 == x) begin
        gbox.record(fromInteger(lay_READY), labelOf(pc, c16), x, True, True);
        st <= XEnq;
      end
      else begin
        packK <= packK + 1;
        vbox.element(opA, zeroExtend(packK) + 1);
      end
    end
  endrule

  // enqueue_goal_to_processor: for processor 0 the goal is made as
  // enqueue_goal makes it; any other processor is refused
  rule toProcessor (st == XProc);
    let a <- dbox.derefResult;
    if (isRef(a) && ins2.val[31:24] <= 11) begin
      // P unbound: the goal waits for it (carried over from VPIM,
      // agreeing with KLIC; asm/pimm_stubs.py TO_PROCESSOR): P and
      // the code address after the arguments
      opA <= a;
      st <= XTq1;
    end
    else if (!isInt(a) || a.val != 0 || ins2.val[31:24] > 11) stop(EndUnimp);
    else begin
      gbox.record(fromInteger(lay_READY), labelOf(pc, c16), ins2.val[31:24], True, True);
      st <= XEnq;
    end
  endrule

  rule tq1 (st == XTq1);
    regs.wa(ins2.val[31:24] + 1, opA);
    st <= XTq2;
  endrule

  rule tq2 (st == XTq2);
    regs.wa(ins2.val[31:24] + 2, intC(absAddr(labelOf(pc, c16))));
    st <= XTq3;
  endrule

  rule tq3 (st == XTq3);
    Bit#(8) n = ins2.val[31:24];
    gbox.record(fromInteger(lay_SUSPENDED), toProcStub + 2 * zeroExtend(n), n + 2, True, True);
    st <= XTq4;
  endrule

  rule tq4 (st == XTq4);
    let g <- gbox.recordResult;
    gbox.hook(g, cellAddr(opA));
    st <= XTp2;
  endrule

  // the stub to_processor x, y, z: r0.. the z arguments, r[x] = P,
  // r[y] = the code.  P still unbound, wait again; P = 0, the goal
  // made ready
  rule tp0 (st == XTp0);
    let a <- dbox.derefResult;
    opA <= a;
    if (isRef(a)) begin
      gbox.record(fromInteger(lay_SUSPENDED), pc, z + 2, False, True);
      st <= XTp1;
    end
    else if (!isInt(a) || a.val != 0) stop(EndUnimp);
    else begin
      gbox.record(fromInteger(lay_READY), cellAddr(regs.r(y)), z, False, True);
      st <= XTpE;
    end
  endrule

  rule tp1 (st == XTp1);
    let g <- gbox.recordResult;
    gbox.hook(g, cellAddr(opA));
    st <= XTp2;
  endrule

  // a hook finished: the enqueue goes on past its two cells, the stub
  // to its proceed
  rule tp2 (st == XTp2);
    gbox.done;
    if (op == op_to_processor) next;
    else finish(tagged Next (pc + 2));
  endrule

  rule tpE (st == XTpE);
    let g <- gbox.recordResult;
    next;
  endrule

  rule enqueued (st == XEnq);
    let g <- gbox.recordResult;
    Bool twoCells = op == op_enqueue_goal_with_priority || op == op_enqueue_goal_to_processor;
    finish(tagged Next (twoCells ? pc + 2 : pc + 1));
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

  // set_vector_element does not wait for the new element (operand 2)
  function Bool waitsOn(Integer i) =
    fromInteger(i) < stub.n && stub.outs[i] == 0 && isRef(vals[i])
    && !(op == op_set_vector_element && i == 2);

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
      if (!isInt(a) || !isInt(b) || ((op == op_b_shift_left || op == op_b_shift_right) && b.val >= 32))
        stop(EndUnimp);
      else begin
        Bit#(5) count = truncate(b.val);
        Bit#(32) r = (op == op_b_add) ? pack(ia + ib)
                   : (op == op_b_subtract) ? pack(ia - ib)
                   : (op == op_b_and) ? (a.val & b.val)
                   : (op == op_b_or) ? (a.val | b.val)
                   : (op == op_b_exclusive_or) ? (a.val ^ b.val)
                   : (op == op_b_shift_right) ? (a.val >> count)
                   : (a.val << count);
        regs.wr(z, intC(r));
        finish(tagged Next afterBuiltin);
      end
    end
    else if (op == op_b_multiply) begin
      // r[z] := r[x] * r[y] in the multiply box; a non-integer or an
      // overflow is the built-in's exception: not modelled
      if (!isInt(a) || !isInt(b)) stop(EndUnimp);
      else begin
        mbox.multiply(a.val, b.val);
        st <= XMul;
      end
    end
    else if (op == op_b_divide || op == op_b_modulo) begin
      // r[z] := r[x] / r[y], or the remainder, as the guards (the
      // divide box).  A non-integer, a zero divisor and, for divide,
      // the least integer by -1 are the built-in's exception: not
      // modelled
      if (!isInt(a) || !isInt(b) || b.val == 0
          || (op == op_b_divide && a.val == 32'h80000000 && b.val == 32'hffffffff)) stop(EndUnimp);
      else begin
        mbox.divide(a.val, b.val);
        st <= XBDiv;
      end
    end
    else if (op == op_b_string) begin
      // string(X, ^Size, ^ElementSize, ^NewString): anything but a
      // string is the built-in's exception: not modelled
      if (!isStrg(a)) stop(EndUnimp);
      else begin
        sbox.info(a);
        st <= XBSInfo;
      end
    end
    else if (op == op_change_element_size) begin
      // change_element_size(String, Bits, ^NewString)
      if (!isStrg(a) || !isInt(b)) stop(EndUnimp);
      else begin
        sbox.changeSize(a, b.val);
        st <= XBStr;
      end
    end
    else if (op == op_string_operation) begin
      // the binary form only: a vector of five (compiler/blt.kl1); the
      // operation is checked when the elements are all there
      if (isLongVec(b) || !isVec(b) || sizeOf(b) != 5) stop(EndUnimp);
      else begin
        packK <= 0;
        vbox.element(b, 0);
        st <= XSo1;
      end
    end
    else if (op == op_subtract_bignum) begin
      // subtract_bignum(BigX, BigY, ^Borrow, ^BigZ): rules bs1..bsOut.
      // Either not a string: the built-in's exception, refused
      if (!isStrg(a) || !isStrg(b)) stop(EndUnimp);
      else begin
        opA <= a;
        bsY <= b;
        sbox.info(a);
        st <= XBs1;
      end
    end
    else if (op == op_multiply_bignum_word) begin
      // multiply_bignum_by_word(BigX, Y, ^BigZ): rules bn1..bn8.  Not a
      // string, or Y not an integer: the built-in's exception, refused
      if (!isStrg(a) || !isInt(b)) stop(EndUnimp);
      else begin
        opA <= a;
        bnY <= b.val;
        sbox.info(a);
        st <= XBn1;
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
    else if (op == op_hash) begin
      // hash(X, ^Value, ^NewX), PDSS's function: an atom's or
      // integer's value, -1 for a list, a short vector's size, a
      // string's by the string box; anything else is refused
      if (isStrg(a)) begin
        sbox.hashStr(a);
        st <= XBHash;
      end
      else if (isAtomic(a) || (a.tag & 8'hfe) == tag_LISTo || (isVec(a) && !isLongVec(a))) begin
        regs.wr(y, intC(isAtomic(a) ? a.val : (isVec(a) ? sizeOf(a) : 32'hffffffff)));
        st <= XBHash2;
      end
      else stop(EndUnimp);
    end
    else if (op == op_apply) begin
      // apply(Code, Args): a ready goal of the code, its arguments the
      // vector's elements (through the argument registers).  Anything
      // but a code and a vector of up to six is the built-in's
      // exception or not modelled; the count is checked against the
      // predicate head, two cells before the code
      if (a.tag != tag_COD || !isVec(b) || (b.tag & 8'hfe) > tag_VECT0o + 12) stop(EndUnimp);
      else begin
        smem.read(cellAddr(a) - 2);
        st <= XAp1;
      end
    end
    else if (op == op_predicate_to_code) begin
      // predicate_to_code(Module, Name, Arity, ^Code): the hash box
      // finds the predicate in the module's entry table; the key is
      // arity << 24 | (atom + arity), an ATOM cell.  Anything but a
      // module, an atom and an arity of 0..255 is the built-in's
      // exception: not modelled
      if (a.tag != tag_MOD || (b.tag & 8'hfe) != tag_ATOMo || !isInt(c) || c.val > 255) stop(EndUnimp);
      else begin
        Bit#(24) nameN = truncate(b.val + c.val);
        hbox.entry(a, mkCell(tag_ATOMo, {c.val[7:0], nameN}));
        st <= XP2C;
      end
    end
    else if (op == op_new_module) begin
      // new_module(Vector, ^Module): the vector box makes the object
      if (!isVec(a)) stop(EndUnimp);
      else begin
        vbox.toModule(a);
        st <= XBMod;
      end
    end
    else if (op == op_calculate_priority_from_minimum) begin
      // calculate_priority_from_minimum(X, ^Y), X in 0..4096 (manual).
      // No shoen here: its priority range is taken as 0..4096, so
      // Y = X.  That range is ours.
      if (!isInt(a) || a.val > 4096) stop(EndUnimp);
      else begin
        regs.wr(y, intC(a.val));
        finish(tagged Next afterBuiltin);
      end
    end
    else if (op == op_calculate_priority_from_current) begin
      // calculate_priority_from_current(X, ^Y), X in -4096..4096
      // (manual).  PDSS's formula (blt_b_rltv) with the range 0..4096
      // and the current priority 4096 (both ours): Y = 4096 + X for
      // X < 0, 4096 for X >= 0.  The range test is signed
      if (!isInt(a) || ia < -4096 || ia > 4096) stop(EndUnimp);
      else begin
        regs.wr(y, intC(ia < 0 ? 4096 + a.val : 4096));
        finish(tagged Next afterBuiltin);
      end
    end
    else if (op == op_supply_atom_number) begin
      // supply_atom_number(X, Y, ^Done): what it does is not sourced.
      // Ours, the narrowest its callers need: two integers, dropped;
      // Done a fresh variable that nothing here binds
      if (!isInt(a) || !isInt(b)) stop(EndUnimp);
      else begin
        gbox.newVar;
        st <= XSan;
      end
    end
    else if (op == op_set_timer) begin
      // set_timer(Time, ^Wakeup): a time reached, (now - Time) mod 2^32
      // < 2^31, gives Wakeup = now (the clock's lower 32 bits); a time
      // still to come is refused
      Bit#(32) d = clk[31:0] - a.val;
      if (!isInt(a) || d[31] == 1) stop(EndUnimp);
      else begin
        regs.wr(y, intC(clk[31:0]));
        finish(tagged Next afterBuiltin);
      end
    end
    else if (op == op_new_instruction) begin
      // new_instruction(Tag, Value, ^Cell): atomic tags and tags from
      // 20h only; a reference or pointer tag is refused
      if (!isInt(a) || !isInt(b) || a.val > 255 || (a.val > 3 && a.val < 32)) stop(EndUnimp);
      else begin
        regs.wr(z, mkCell(truncate(a.val), b.val));
        finish(tagged Next afterBuiltin);
      end
    end
    else if (op == op_b_vector_element) begin
      // vector_element(V, I, ^E, ^V1); the vector box checks the index
      if (!isVec(a) || !isInt(b)) stop(EndUnimp);
      else begin
        vbox.markElement(a, b.val);     // V1 still holds the element
        st <= XBVEl;
      end
    end
    else if (op == op_code_to_predicate) begin
      // code_to_predicate(Code, ^Module, ^Name, ^Arity, ^Info): the
      // predicate head two cells before the code, as the guard code's;
      // anything but a code is the exception: not modelled
      if (a.tag != tag_COD) stop(EndUnimp);
      else begin
        opA <= a;
        smem.read(cellAddr(a) - 2);
        st <= XC2P1;
      end
    end
    else if (op == op_b_vector) begin
      // body vector(X, ^Size, ^NewVector): r[y] := the size, then r[z]
      // := X.  Anything but a vector is the exception: not modelled
      if (!isVec(a)) stop(EndUnimp);
      else if (isLongVec(a)) begin
        vbox.info(a);
        st <= XVInfo;
      end
      else begin
        regs.wr(y, intC(sizeOf(a)));
        st <= XBVOut;
      end
    end
    else if (op == op_new_vector) begin
      // new_vector(Size, ^V)
      if (!isInt(a) || a.val[31] == 1) stop(EndUnimp);
      else begin
        vbox.newVec(a.val);
        st <= XBVec;
      end
    end
    else if (op == op_set_vector_element) begin
      // set_vector_element(V, I, New, ^Old, ^V1)
      if (!isVec(a) || !isInt(b) || (!isLongVec(a) && b.val >= sizeOf(a))) stop(EndUnimp);
      else begin
        vbox.setElement(a, b.val, c);
        st <= XBVec;
      end
    end
    else if (op == op_scsi_command) begin
      // scsi_command(Obj, Vector, ^Data, ^TransferredLength, ^Id,
      // ^Result, ^NewObj): the SCSI box, for a vector of seven (a long
      // vector; anything else is refused)
      if (!isLongVec(b)) stop(EndUnimp);
      else begin
        scsi.command(a, b);
        st <= XScC;
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

  // multiply_bignum_by_word (pimm.py i_multiply_bignum_word, after
  // VPIM): the empty X is the answer; a leading zero word is the
  // exception; Y = 0 gives the empty string.  Two passes from the least
  // significant word: the first finds the last carry (so the length),
  // the second writes the product into a new string of zeros, the
  // carry last at word 0
  rule bn1 (st == XBn1);
    let r <- sbox.result;
    if (r.b.val != 32) stop(EndUnimp);
    else if (r.a.val == 0) begin
      regs.wr(z, opA);
      finish(tagged Next afterBuiltin);
    end
    else begin
      bnN <= r.a.val;
      sbox.element(opA, 0);
      st <= XBn2;
    end
  endrule

  rule bn2 (st == XBn2);
    let r <- sbox.result;
    if (r.a.val == 0) stop(EndUnimp);
    else if (bnY == 0) begin
      sbox.newStr(0, 32);
      st <= XBn7;
    end
    else begin
      bnPass2 <= False;
      bnCarry <= 0;
      bnI <= bnN - 1;
      sbox.element(opA, bnN - 1);
      st <= XBn3;
    end
  endrule

  rule bn3 (st == XBn3);
    let r <- sbox.result;
    mbox.multiplyAdd(r.a.val, bnY, bnCarry);
    st <= XBn4;
  endrule

  rule bn4 (st == XBn4);
    let p <- mbox.wide;
    bnCarry <= p[63:32];
    if (bnPass2) begin
      sbox.poke(bnDst, bnI + (bnExtra ? 1 : 0), p[31:0]);
      st <= XBn5;
    end
    else if (bnI == 0) begin
      Bool extra = p[63:32] != 0;
      bnExtra <= extra;
      sbox.newStr(bnN + (extra ? 1 : 0), 32);
      st <= XBn6;
    end
    else begin
      bnI <= bnI - 1;
      sbox.element(opA, bnI - 1);
      st <= XBn3;
    end
  endrule

  rule bn5 (st == XBn5);
    let r <- sbox.result;
    if (bnI != 0) begin
      bnI <= bnI - 1;
      sbox.element(opA, bnI - 1);
      st <= XBn3;
    end
    else if (bnExtra) begin
      sbox.poke(bnDst, 0, bnCarry);
      st <= XBn8;
    end
    else begin
      regs.wr(z, bnDst);
      finish(tagged Next afterBuiltin);
    end
  endrule

  rule bn6 (st == XBn6);
    let r <- sbox.result;
    bnDst <= r.a;
    bnPass2 <= True;
    bnCarry <= 0;
    bnI <= bnN - 1;
    sbox.element(opA, bnN - 1);
    st <= XBn3;
  endrule

  rule bn7 (st == XBn7);
    let r <- sbox.result;
    regs.wr(z, r.a);
    finish(tagged Next afterBuiltin);
  endrule

  rule bn8 (st == XBn8);
    let r <- sbox.result;
    regs.wr(z, bnDst);
    finish(tagged Next afterBuiltin);
  endrule

  // subtract_bignum (pimm.py i_subtract_bignum, after VPIM): both
  // 32-bit strings with no leading zero word (else the exception); Y
  // empty: X and 0; X empty: Y and 1; then the larger is found (the
  // lengths, else the words from the most significant), equal gives the
  // empty string and 0; else two passes from the least significant
  // word, the first finding the most significant word not 0 (so the
  // length), the second writing the kept words into a new string
  Cell bsL = bsSwap ? bsY : opA;
  Cell bsS = bsSwap ? opA : bsY;
  Bit#(32) bsNL = bsSwap ? bsM : bnN;
  Bit#(32) bsOff = bsSwap ? bsM - bnN : bnN - bsM;

  function Action bsOut(Bit#(32) borrow, Cell zc);
    action
      regs.wr(z, intC(borrow));
      bsZ <= zc;
      st <= XBsOut;
    endaction
  endfunction

  function Action bsStart(Bool swap);
    action
      Bit#(32) nl = swap ? bsM : bnN;
      bsSwap <= swap;
      bnPass2 <= False;
      bnCarry <= 0;
      bsLast <= nl;
      bnI <= nl - 1;
      sbox.element(swap ? bsY : opA, nl - 1);
      st <= XBs7;
    endaction
  endfunction

  function Action bsStep(Bit#(32) lw, Bit#(32) sw);
    action
      Bit#(33) d = zeroExtend(lw) - zeroExtend(sw) - zeroExtend(bnCarry[0]);
      Bit#(32) w = d[31:0];
      bnCarry <= zeroExtend(d[32]);
      if (!bnPass2) begin
        Bit#(32) last = w != 0 ? bnI : bsLast;
        bsLast <= last;
        if (bnI == 0) begin
          sbox.newStr(bsNL - last, 32);
          st <= XBs9;
        end
        else begin
          bnI <= bnI - 1;
          sbox.element(bsL, bnI - 1);
          st <= XBs7;
        end
      end
      else begin
        sbox.poke(bnDst, bnI - bsLast, w);
        st <= XBs10;
      end
    endaction
  endfunction

  rule bs1 (st == XBs1);
    let r <- sbox.result;
    if (r.b.val != 32) stop(EndUnimp);
    else begin
      bnN <= r.a.val;
      sbox.info(bsY);
      st <= XBs2;
    end
  endrule

  rule bs2 (st == XBs2);
    let r <- sbox.result;
    if (r.b.val != 32) stop(EndUnimp);
    else begin
      bsM <= r.a.val;
      if (bnN != 0) begin
        sbox.element(opA, 0);
        st <= XBs3;
      end
      else if (r.a.val != 0) begin
        sbox.element(bsY, 0);
        st <= XBs4;
      end
      else bsOut(0, opA);
    end
  endrule

  rule bs3 (st == XBs3);
    let r <- sbox.result;
    if (r.a.val == 0) stop(EndUnimp);
    else if (bsM != 0) begin
      sbox.element(bsY, 0);
      st <= XBs4;
    end
    else bsOut(0, opA);
  endrule

  rule bs4 (st == XBs4);
    let r <- sbox.result;
    if (r.a.val == 0) stop(EndUnimp);
    else if (bnN == 0) bsOut(1, bsY);
    else if (bnN != bsM) bsStart(bsM > bnN);
    else begin
      bnI <= 0;
      sbox.element(opA, 0);
      st <= XBs5;
    end
  endrule

  rule bs5 (st == XBs5);
    let r <- sbox.result;
    bsW <= r.a.val;
    sbox.element(bsY, bnI);
    st <= XBs6;
  endrule

  rule bs6 (st == XBs6);
    let r <- sbox.result;
    if (bsW != r.a.val) bsStart(r.a.val > bsW);
    else if (bnI + 1 == bnN) begin
      sbox.newStr(0, 32);
      st <= XBs11;
    end
    else begin
      bnI <= bnI + 1;
      sbox.element(opA, bnI + 1);
      st <= XBs5;
    end
  endrule

  rule bs7 (st == XBs7);
    let r <- sbox.result;
    bsW <= r.a.val;
    if (bnI >= bsOff) begin
      sbox.element(bsS, bnI - bsOff);
      st <= XBs8;
    end
    else bsStep(r.a.val, 0);
  endrule

  rule bs8 (st == XBs8);
    let r <- sbox.result;
    bsStep(bsW, r.a.val);
  endrule

  rule bs9 (st == XBs9);
    let r <- sbox.result;
    bnDst <= r.a;
    bnPass2 <= True;
    bnCarry <= 0;
    bnI <= bsNL - 1;
    sbox.element(bsL, bsNL - 1);
    st <= XBs7;
  endrule

  rule bs10 (st == XBs10);
    let r <- sbox.result;
    if (bnI == bsLast) bsOut(bsSwap ? 1 : 0, bnDst);
    else begin
      bnI <= bnI - 1;
      sbox.element(bsL, bnI - 1);
      st <= XBs7;
    end
  endrule

  rule bs11 (st == XBs11);
    let r <- sbox.result;
    bsOut(0, r.a);
  endrule

  rule bsWrite (st == XBsOut);
    regs.wr(operand[3], bsZ);
    finish(tagged Next afterBuiltin);
  endrule

  rule bStr (st == XBStr);
    let r <- sbox.result;
    if (op == op_new_string || op == op_change_element_size) begin
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

  rule shown (st == XShow);
    let r <- sbox.result;
    next;
  endrule

  rule sEqual (st == XSEq);
    let r <- sbox.result;
    if (r.ok) next;
    else guardFail;
  endrule

  // hash(X, ^Value, ^NewX): Value, then NewX = X
  rule bHash (st == XBHash);
    let r <- sbox.result;
    regs.wr(y, r.a);
    st <= XBHash2;
  endrule

  rule bHash2 (st == XBHash2);
    regs.wr(z, vals[0]);
    finish(tagged Next afterBuiltin);
  endrule

  rule sElement (st == XSEl);
    let r <- sbox.result;
    if (!r.ok) guardFail;
    else begin
      regs.wr(z, r.a);
      next;
    end
  endrule

  // string_operation(Op, {Pos1, Str1, Len, Pos2, Str2}, ^NewS1, ^NewS2):
  // the five elements, dereferenced, then the string box
  rule strOp1 (st == XSo1);
    let r <- vbox.result;
    dbox.deref(r.a);
    st <= XSo2;
  endrule

  rule strOp2 (st == XSo2);
    let v <- dbox.derefResult;
    sv[packK] <= v;
    if (packK == 4) st <= XSo3;
    else begin
      packK <= packK + 1;
      vbox.element(vals[1], zeroExtend(packK) + 1);
      st <= XSo1;
    end
  endrule

  // An element that is not yet a value is waited for (the manual: the
  // built-in waits): the goal of the stub, as for an unbound operand,
  // hooked on the first such element in order.  A wrong type or
  // operation (the built-in's exception) is not modelled
  function Bool svWaits(Integer i) = isRef(sv[i]);

  rule strOp3 (st == XSo3);
    if (svWaits(0) || svWaits(1) || svWaits(2) || svWaits(3) || svWaits(4)) begin
      gbox.waitRecord(stub.addr, stub.n, operand, stub.outs);
      st <= XSoW;
    end
    else if (!isInt(vals[0]) || vals[0].val > 15
             || !isInt(sv[0]) || !isStrg(sv[1]) || !isInt(sv[2]) || !isInt(sv[3]) || !isStrg(sv[4]))
      stop(EndUnimp);
    else begin
      sbox.stringOp(truncate(vals[0].val), sv[1], sv[0].val, sv[2].val, sv[3].val, sv[4]);
      st <= XSo4;
    end
  endrule

  rule strOpWait (st == XSoW);
    let g <- gbox.recordResult;
    Cell v = svWaits(0) ? sv[0] : (svWaits(1) ? sv[1] : (svWaits(2) ? sv[2]
           : (svWaits(3) ? sv[3] : sv[4])));
    gbox.hook(g, cellAddr(v));
    st <= XBWait2;
  endrule

  rule strOp4 (st == XSo4);
    let r <- sbox.result;
    regs.wr(z, r.a);
    vals[0] <= r.b;
    st <= XBOut2;
  endrule

  rule vElement (st == XVEl);
    let r <- vbox.result;
    if (!r.ok) guardFail;
    else begin
      regs.wr(z, r.a);
      next;
    end
  endrule

  // predicate_to_code: the code object, or the vector {Module, Name,
  // Arity} when the module has no such predicate (PIMOS manual)
  rule p2c (st == XP2C);
    let t <- hbox.resolved;
    if (t matches tagged Valid .at) begin
      regs.wr(operand[3], mkCell(tag_COD, absAddr(at)));
      finish(tagged Next afterBuiltin);
    end
    else begin
      gbox.alloc(3);
      st <= XP2Ca;
    end
  endrule

  rule p2cAlloc (st == XP2Ca);
    let at <- gbox.allocResult;
    opA <= mkCell(tag_VECT0o + 7, absAddr(at));
    smem.write(at, vals[0]);
    st <= XP2Cw1;
  endrule

  rule p2cW1 (st == XP2Cw1);
    smem.write(cellAddr(opA) + 1, vals[1]);
    st <= XP2Cw2;
  endrule

  rule p2cW2 (st == XP2Cw2);
    smem.write(cellAddr(opA) + 2, vals[2]);
    st <= XP2Cw3;
  endrule

  rule p2cW3 (st == XP2Cw3);
    regs.wr(operand[3], opA);
    finish(tagged Next afterBuiltin);
  endrule

  // apply: the head's arity must be the vector's size; then each
  // element is taken (its MRB on if the vector's is) into an argument
  // register, and the goal is made as enqueue_goal makes one
  Bit#(8) applyN = zeroExtend(((vals[1].tag & 8'hfe) - tag_VECT0o) >> 1);

  rule apply1 (st == XAp1);
    let h <- smem.data;
    if (h.tag != tag_PREDH || h.val[31:24] != applyN) stop(EndUnimp);
    else if (applyN == 0) begin
      // the empty vector: a goal of no argument
      gbox.record(fromInteger(lay_READY), cellAddr(vals[0]), 0, True, True);
      st <= XEnq;
    end
    else begin
      packK <= 0;
      smem.read(cellAddr(vals[1]));
      st <= XAp2;
    end
  endrule

  rule apply2 (st == XAp2);
    let c <- smem.data;
    Bool on = vals[1].tag[0] == 1;
    Addr at = cellAddr(vals[1]) + zeroExtend(packK);
    regs.wa(packK + 1, isUnboundCell(c) ? mkCell(on ? tag_REFx : tag_REFo, absAddr(at))
                                        : (on ? marked(c) : c));
    if (packK + 1 == applyN) begin
      gbox.record(fromInteger(lay_READY), cellAddr(vals[0]), applyN, True, True);
      st <= XEnq;
    end
    else begin
      packK <= packK + 1;
      smem.read(at + 1);
    end
  endrule

  // scsi_where: the vector's four cells, the list cell's two
  rule scsiWhere1 (st == XSWh1);
    let at <- gbox.allocResult;
    opA <= mkCell(tag_LISTo + 1, absAddr(at + 4));
    smem.write(at, intCell(0));
    packK <= 1;
    st <= XSWh2;
  endrule

  rule scsiWhere2 (st == XSWh2);
    Addr list = cellAddr(opA);
    Addr vec = list - 4;
    case (packK)
      1, 2: smem.write(vec + zeroExtend(packK), intCell(0));
      3:    smem.write(vec + 3, intCell(6));
      4:    smem.write(list, mkCell(tag_VECT0o + 9, absAddr(vec)));
      5:    smem.write(list + 1, mkCell(tag_ATOMo, 0));
    endcase
    if (packK == 6) begin
      regs.wr(x, opA);
      next;
    end
    else packK <= packK + 1;
  endrule

  // the guard code: the head, then the module's descriptor cell
  rule code1 (st == XCode1);
    let h <- smem.data;
    if (h.tag != tag_PREDH) stop(EndUnimp);
    else begin
      opB <= h;
      Bit#(32) back = zeroExtend(h.val[23:0]);   // through 32 bits: any address width
      smem.read(cellAddr(opA) - 2 - truncate(back));
      st <= XCode2;
    end
  endrule

  rule code2 (st == XCode2);
    let d <- smem.data;
    if (d.tag != tag_CDESC) stop(EndUnimp);
    else begin
      regs.wr(y, intC(zeroExtend(opB.val[31:24])));
      st <= XCode3;
    end
  endrule

  rule code3 (st == XCode3);
    Bit#(32) m = opA.val - 2 - zeroExtend(opB.val[23:0]);
    regs.wr(z, mkCell(tag_MOD, m));
    st <= XCode4;
  endrule

  rule code4 (st == XCode4);
    regs.wr(operand[3], intC(2 + zeroExtend(opB.val[23:0])));
    finish(tagged Next (pc + 2));
  endrule

  // code_to_predicate: the head, the module's descriptor cell, then
  // the name (Code - 4) and Info (Code - 3) (assemble.kl1 make_pred_head)
  rule c2p1 (st == XC2P1);
    let h <- smem.data;
    if (h.tag != tag_PREDH) stop(EndUnimp);
    else begin
      opB <= h;
      Bit#(32) back = zeroExtend(h.val[23:0]);
      smem.read(cellAddr(opA) - 2 - truncate(back));
      st <= XC2P2;
    end
  endrule

  rule c2p2 (st == XC2P2);
    let d <- smem.data;
    if (d.tag != tag_CDESC) stop(EndUnimp);
    else begin
      regs.wr(y, mkCell(tag_MOD, opA.val - 2 - zeroExtend(opB.val[23:0])));
      smem.read(cellAddr(opA) - 4);
      st <= XC2P3;
    end
  endrule

  rule c2p3 (st == XC2P3);
    let n <- smem.data;
    if ((n.tag & 8'hfe) != tag_ATOMo) stop(EndUnimp);
    else begin
      regs.wr(z, mkCell(tag_ATOMo, n.val));
      smem.read(cellAddr(opA) - 3);
      st <= XC2P4;
    end
  endrule

  rule c2p4 (st == XC2P4);
    let i <- smem.data;
    regs.wr(operand[3], intC(zeroExtend(opB.val[31:24])));
    opA <= i;
    st <= XC2P5;
  endrule

  rule c2p5 (st == XC2P5);
    regs.wr(operand[4], opA);
    finish(tagged Next afterBuiltin);
  endrule

  rule bModule (st == XBMod);
    let r <- vbox.result;
    if (!r.ok) stop(EndUnimp);
    else begin
      regs.wr(y, r.a);
      finish(tagged Next afterBuiltin);
    end
  endrule

  // ---- the merger ------------------------------------------------------
  rule merge0 (st == XMg0);
    let a <- dbox.derefResult;
    if (!isRef(a)) stop(EndUnimp);        // the output must be a variable
    else begin
      nbox.create(a);
      st <= XMg1;
    end
  endrule

  rule merge1 (st == XMg1);
    let r <- nbox.result;
    regs.wr(y, r.a);
    opA <= r.a;
    vnew <= r.b;
    st <= XMg2;
  endrule

  rule merge2 (st == XMg2);
    Vector#(7, Bit#(8)) ops = replicate(0);
    ops[0] = y;
    ops[1] = 254;
    regs.wr(254, vnew);
    gbox.waitRecord(mergeInStub, 2, ops, 0);
    st <= XMg3;
  endrule

  rule merge3 (st == XMg3);
    let g <- gbox.recordResult;
    gbox.hook(g, cellAddr(opA));
    st <= XMi2;
  endrule

  rule mergeIn0 (st == XMi0);
    let a <- dbox.derefResult;
    opA <= a;
    if (isRef(a)) begin
      // nothing yet: wait on the stream again
      Vector#(7, Bit#(8)) ops = replicate(0);
      ops[0] = x;
      ops[1] = y;
      gbox.waitRecord(mergeInStub, 2, ops, 0);
      st <= XMi1;
    end
    else if ((a.tag & 8'hfe) == tag_LISTo) begin
      nbox.cons(a, regs.r(y));
      st <= XMi3;
    end
    else if ((a.tag & 8'hfe) == tag_ATOMo && a.val == 0) begin
      nbox.close(regs.r(y));
      st <= XMi4;
    end
    else if (isVec(a) && !isLongVec(a)) begin
      // a vector: as many inputs as it has elements (TR-466 3.3)
      nbox.spread(regs.r(y), sizeOf(a));
      st <= XMv1;
    end
    else stop(EndUnimp);                  // a vector of 7 or more, or not a stream
  endrule

  rule mergeIn1 (st == XMi1);
    let g <- gbox.recordResult;
    gbox.hook(g, cellAddr(opA));
    st <= XMi2;
  endrule

  rule mergeIn2 (st == XMi2);
    gbox.done;
    next;
  endrule

  // an element: on with the cdr, the output gets the new list cell
  rule mergeIn3 (st == XMi3);
    let r <- nbox.result;
    regs.wr(x, r.c);
    dbox.unify(r.b, r.a);
    st <= XMiU;
  endrule

  rule mergeInW (st == XMi2w);
    gbox.done;
    finish(tagged Next pc);
  endrule

  // an input bound to a vector: it ends and each element gets a ready
  // goal of merge_in, made through the argument registers (a1 the
  // element, taken with its MRB on, a2 the record), the last element's
  // newest.  The empty vector only ends the input
  rule mergeVec1 (st == XMv1);
    let r <- nbox.result;
    if (r.ok) begin
      dbox.unify(r.a, mkCell(tag_ATOMo, 0));
      st <= XUnify;
    end
    else if (vectorSize(opA) == 0) next;
    else begin
      packK <= 0;
      smem.read(cellAddr(opA));
      st <= XMv2;
    end
  endrule

  rule mergeVec2 (st == XMv2);
    let c <- smem.data;
    Addr at = cellAddr(opA) + zeroExtend(packK);
    regs.wa(1, isUnboundCell(c) ? mkCell(tag_REFx, absAddr(at)) : marked(c));
    st <= XMv3;
  endrule

  rule mergeVec3 (st == XMv3);
    regs.wa(2, regs.r(y));
    gbox.record(fromInteger(lay_READY), mergeInStub, 2, True, True);
    st <= XMv4;
  endrule

  rule mergeVec4 (st == XMv4);
    let g <- gbox.recordResult;
    if (zeroExtend(packK) + 1 == sizeOf(opA)) next;
    else begin
      packK <= packK + 1;
      smem.read(cellAddr(opA) + zeroExtend(packK) + 1);
      st <= XMv2;
    end
  endrule

  // an input ends: the last one closes the output
  rule mergeIn4 (st == XMi4);
    let r <- nbox.result;
    if (r.ok) begin
      dbox.unify(r.a, mkCell(tag_ATOMo, 0));
      st <= XUnify;
    end
    else next;
  endrule

  // ---- the shoen ---------------------------------------------------------
  // create_shoen(MinPrio, MaxPrio, ExcepMask, Code, Argv, ^Report,
  // ^Shoen), 22:E0, seven registers (klb_opr.kl1 p(r7)), and
  // start_shoen(Shoen, ^NewShoen), 22:E1: encodings and directions are
  // PIM/m-sourced (PIMOS library/assembler/inst_tab.kl1:332-362,
  // library/compiler/blt.kl1:537-601), what they do is not
  // (PimmShBox.bsv).  The inputs waited for are dereferenced in order;
  // an unbound one makes the built-in a goal of its stub, as any body
  // built-in.
  rule shIn (st == XShIn);
    dbox.deref(regs.r(operand[bK]));
    st <= XShInW;
  endrule

  rule shInW (st == XShInW);
    let v <- dbox.derefResult;
    vals[bK] <= v;
    if (bK + 1 == shoenIns) st <= XShGo;
    else begin
      bK <= bK + 1;
      st <= XShIn;
    end
  endrule

  rule shGo (st == XShGo);
    // raise waits for its Tag only (stage 3): Info and Data are not read
    if (waitsOn(0) || (op != op_raise && (waitsOn(1) || waitsOn(2)))) begin
      gbox.waitRecord(stub.addr, stub.n, operand, stub.outs);
      st <= XBWait1;
    end
    else if (op == op_start_shoen) begin
      // anything but a handle is refused
      if (vals[0].tag != tag_SHREC) stop(EndUnimp);
      else begin
        shbox.start(vals[0]);
        st <= XShS;
      end
    end
    // shoen_statistics(Shoen, ^NewShoen), 22:E6, and remove_shoen(Shoen),
    // 22:E4 (stage 2): anything but a handle is refused
    else if (op == op_shoen_statistics || op == op_remove_shoen) begin
      if (vals[0].tag != tag_SHREC) stop(EndUnimp);
      else begin
        if (op == op_shoen_statistics) shbox.statistics(vals[0]);
        else shbox.remove(vals[0]);
        st <= XShS;
      end
    end
    // stage 3: stop_shoen(Shoen, ^NewShoen), 22:E2, abort_shoen(Shoen,
    // ^NewShoen), 22:E3: anything but a handle is refused
    else if (op == op_stop_shoen || op == op_abort_shoen) begin
      if (vals[0].tag != tag_SHREC) stop(EndUnimp);
      else begin
        if (op == op_stop_shoen) shbox.stop(vals[0]);
        else shbox.abort(vals[0]);
        st <= XShS;
      end
    end
    // raise(Tag, Info, Data), 22:F2: a `raised` exception, 16, the tag
    // Tag; Info and Data as the registers hold them.  A Tag that is no
    // integer is refused
    else if (op == op_raise) begin
      if (!isInt(vals[0])) stop(EndUnimp);
      else begin
        shbox.exception(fromInteger(lay_EXC_RAISED), vals[0].val,
                        regs.r(operand[1]), regs.r(operand[2]), 0);
        st <= XShS;
      end
    end
    // MinPrio, MaxPrio and ExcepMask must be integers (shoen:execute1/7
    // passes vectors: refused) and are then dropped: no priorities and
    // no exceptions here
    else if (!isInt(vals[0]) || !isInt(vals[1]) || !isInt(vals[2])) stop(EndUnimp);
    else begin
      // Code and Argv as they are (apply waits for them itself), to
      // the argument registers of the first goal.  They are read
      // before an output is written: in the image the outputs ARE
      // these registers (shoen:execute/4, cell 15553: 22:e0040506,
      // 00:00010001)
      regs.wa(1, regs.r(operand[3]));
      st <= XShC1;
    end
  endrule

  rule shCreate1 (st == XShC1);
    regs.wa(2, regs.r(operand[4]));
    shbox.create(vals[2]);
    st <= XShC2;
  endrule

  rule shCreate2 (st == XShC2);
    let r <- shbox.result;
    regs.wr(operand[5], r.a);        // Report: a fresh variable
    opA <= r.b;
    st <= XShC3;
  endrule

  rule shCreate3 (st == XShC3);
    regs.wr(operand[6], opA);        // Shoen: the handle
    finish(tagged Next (pc + 2));
  endrule

  // a shoen that is not dormant is refused (a shoen removed already, by
  // remove_shoen); NewShoen is the same handle, remove_shoen has none
  rule shStarted (st == XShS);
    let r <- shbox.result;
    if (!r.ok) stop(EndUnimp);
    else if (op == op_remove_shoen || op == op_raise) next;
    else begin
      regs.wr(y, vals[0]);
      next;
    end
  endrule

  // a reduction failure reported (stage 3): the goal ends, one
  // reduction, as at a proceed; refused if no shoen took it
  rule shFailed (st == XShF);
    let r <- shbox.result;
    if (!r.ok) stop(EndUnimp);
    else begin
      nRed <= nRed + 1;
      $display("E fail");
      finish(tagged Stop EndDone);
    end
  endrule

  // current_processor: the second and third outputs
  rule cProc1 (st == XCPr1);
    regs.wr(y, intC(1));
    st <= XCPr2;
  endrule

  rule cProc2 (st == XCPr2);
    regs.wr(z, intC(1));
    next;
  endrule

  rule bVectorElement (st == XBVEl);
    let r <- vbox.result;
    if (!r.ok) stop(EndUnimp);
    else begin
      regs.wr(z, r.a);
      st <= XBOut2;
    end
  endrule

  rule structuredConstant (st == XSCnst);
    let c <- smem.data;
    // the cell as it stands: a structure pointer, or for module#M a
    // reference (to the image's module table, or to the variable the
    // IPL's linker binds), which whatever uses it dereferences
    regs.wr(x, c);
    next;
  endrule

  rule external (st == XExt);
    let t <- hbox.resolved;
    if (t matches tagged Valid .a) begin
      if (op == op_enqueue_goal_external) begin
        gbox.record(fromInteger(lay_READY), a, x, True, True);
        st <= XEnq;
      end
      else begin
        alt <= tagged Invalid;
        nNoted <= 0;
        nRed <= nRed + 1;
        finish(tagged Next a);
      end
    end
    else stop(EndUnimp);
  endrule

  rule vPut (st == XVPut);
    let r <- vbox.result;
    regs.wr(x, r.a);
    sp <= truncate(r.b.val);
    spSingle <= False;
    next;
  endrule

  rule vInfo (st == XVInfo);
    let r <- vbox.result;
    if (op == op_wait_vector) begin
      if (r.a.val == zeroExtend(c16)) begin
        sp <= truncate(r.b.val);
        spSingle <= opA.tag[0] == 0;
        next;
      end
      else guardFail;
    end
    else if (op == op_switch_on_non_vector) begin
      regs.wr(y, r.a);
      sp <= truncate(r.b.val);
      spSingle <= False;
      finish(tagged Next (pc + 2));
    end
    else if (op == op_b_vector) begin
      regs.wr(y, r.a);
      st <= XBVOut;
    end
    else begin
      regs.wr(y, r.a);
      next;
    end
  endrule

  // body vector/3: NewVector, after the size
  rule bVOut (st == XBVOut);
    regs.wr(z, vals[0]);
    finish(tagged Next afterBuiltin);
  endrule

  rule bVec (st == XBVec);
    let r <- vbox.result;
    if (!r.ok) stop(EndUnimp);
    else if (op == op_new_vector) begin
      regs.wr(y, r.a);
      finish(tagged Next afterBuiltin);
    end
    else begin
      regs.wr(operand[3], r.b);
      vnew <= r.a;
      st <= XBVec2;
    end
  endrule

  rule bVec2 (st == XBVec2);
    regs.wr(operand[4], vnew);
    finish(tagged Next afterBuiltin);
  endrule

  // ---- the SCSI built-ins (PimmScsiBox.bsv) ---------------------------------
  rule scsiInit1 (st == XScI1);
    let r <- scsi.result;
    if (r matches tagged Vector .v) regs.wr(y, v);
    scsi.initInfo;
    st <= XScI2;
  endrule

  rule scsiInit2 (st == XScI2);
    let r <- scsi.result;
    if (r matches tagged Vector .v) regs.wr(z, v);
    next;
  endrule

  // an element of the vector unbound: the stub's goal waits on it, as
  // string_operation's; refused: not modelled; done: the five outputs
  rule scsiCommand (st == XScC);
    let r <- scsi.result;
    case (r) matches
      tagged Wait .at: begin
        gbox.waitRecord(stub.addr, stub.n, operand, stub.outs);
        opA <= mkCell(tag_REFo, absAddr(at));
        st <= XScW;
      end
      tagged Done .d: begin
        regs.wr(operand[2], d.data);
        scR <= r;
        st <= XScO1;
      end
      default: stop(EndUnimp);
    endcase
  endrule

  rule scsiWait (st == XScW);
    let g <- gbox.recordResult;
    gbox.hook(g, cellAddr(opA));
    st <= XBWait2;
  endrule

  rule scsiOut (st == XScO1 || st == XScO2 || st == XScO3 || st == XScO4);
    if (scR matches tagged Done .d) begin
      case (st)
        XScO1: begin regs.wr(operand[3], d.tl);     st <= XScO2; end
        XScO2: begin regs.wr(operand[4], d.id);     st <= XScO3; end
        XScO3: begin regs.wr(operand[5], d.result); st <= XScO4; end
        default: begin
          regs.wr(operand[6], vals[0]);              // NewObj: Obj
          finish(tagged Next afterBuiltin);
        end
      endcase
    end
  endrule

  rule bOut2 (st == XBOut2);
    regs.wr(operand[3], vals[0]);
    finish(tagged Next afterBuiltin);
  endrule

  method Action newGoal;
    alt <= tagged Invalid;
    nNoted <= 0;
    nRed <= 0;
  endmethod

  method Bit#(32) reductions = nRed;

  method Action enq(Fetched f) = inQ.enq(f);
  method ActionValue#(Step) out;
    outQ.deq;
    return outQ.first;
  endmethod
endmodule

endpackage
