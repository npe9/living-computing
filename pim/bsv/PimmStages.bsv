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
               XVar1, XVar2, XEnq, XStrInfo, XStrInfo2, XVec, XRead, XReuse1, XReuse2, XVEl, XBVec, XBVec2,
               XBIn, XBInW, XBGo, XBWait1, XBWait2, XBStr, XBOut2, XDiv, XVInfo, XMul, XVPut, XExt, XSCnst, XRAtom, XBVEl, XTagVal, XPack, XBMod } XState deriving (Bits, Eq);

module mkPimmExec#(PimmRegs regs, PimmDBox dbox, PimmHBox hbox, PimmGBox gbox,
                   PimmSBox sbox, PimmVBox vbox, PimmMBox mbox, MemPort smem)(PimmExec);
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
  Reg#(Bit#(8))      reuseTag <- mkRegU;
  Reg#(Cell)         vnew    <- mkRegU;
  Reg#(Bit#(8))      packK   <- mkRegU;     // the packed argument in hand

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
                || op == op_b_shift_left || op == op_b_shift_right;
  Bool builtinHere = arithHere || op == op_b_multiply || op == op_new_string
                  || op == op_b_string_element || op == op_set_string_element
                  || op == op_new_vector || op == op_set_vector_element
                  || op == op_b_vector_element || op == op_new_instruction
                  || op == op_new_module;
  // opcode 76 is numbered by its x field: 4 is the guard
  // tag_and_value(X, ^Tag, ^Value), registers y, z and the next cell's
  // top byte
  Bool isTagAndValue = op == 16'h2376 && x == 4;
  // a vector pointer, short (0..6 elements, the size in the tag) or long
  function Bool isVec(Cell c) = (c.tag & 8'hf0) == tag_VECT0o;
  function Bool isLongVec(Cell c) = (c.tag & 8'hfe) == 8'h1e;
  function Bit#(32) sizeOf(Cell c) = zeroExtend(vectorSize(c));
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

  // wait_vector_N, N = 2, 3, 5
  Bool isWaitVector = op == op_wait_vector_2 || op == op_wait_vector_3 || op == op_wait_vector_5;
  Bit#(8) waitN = ins.val[31:24] - op_wait_vector_0[7:0];
  Bool oneOperandGuard = op == op_switch_on_non_integer || op == op_hash_on_constant
                      || op == op_switch_on_constant
                      || op == op_wait || op == op_wait_integer || op == op_string
                      || op == op_integer || op == op_wait_constant
                      || op == op_switch_on_non_atom || op == op_wait_nil || op == op_wait_list
                      || isWaitVector || op == op_switch_on_non_list
                      || op == op_switch_on_non_vector || op == op_vector;
  Bool twoOperandGuard = op == op_not_less_than || op == op_less_than || op == op_equal
                      || op == op_subtract || op == op_and || op == op_vector_element
                      || op == op_shift_right || op == op_modulo || op == op_wait_value
                      || op == op_add;
  function Bool isAtomic(Cell c) = (c.tag & 8'hfe) == tag_INTo || (c.tag & 8'hfe) == tag_ATOMo;
  function Bool sameAtomic(Cell p, Cell q) = (p.tag & 8'hfe) == (q.tag & 8'hfe) && p.val == q.val;
  // an atom instruction is one cell: opcode byte = base | register, the
  // atom in the low 24 bits; get_atom's base is c0
  Bool isGetAtom = ins.tag == tag_KLB && ins.val[31:29] == 3'b110;
  // wait_atom's base is 80
  Bool isWaitAtom = ins.tag == tag_KLB && ins.val[31:29] == 3'b100;
  // put_atom's base is 40
  Bool isPutAtom = ins.tag == tag_KLB && ins.val[31:29] == 3'b010;
  Cell atomHere = mkCell(tag_ATOMo, zeroExtend(ins.val[23:0]));
  // put_vector_N, N = 2..4: N cells, no header
  Bool isPutVector = op == op_put_vector_1 || op == op_put_vector_2 || op == op_put_vector_3
                  || op == op_put_vector_4 || op == op_put_vector_5 || op == op_put_vector_6;
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
    else if (isWaitAtom) begin
      dbox.deref(regs.r(zeroExtend(ins.val[28:24])));
      st <= XDeref1;
    end
    else if (isTagAndValue) begin
      dbox.deref(regs.r(y));
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
    else if (op == op_mark_element) next;     // MRB marking: not modelled
    else if (op == op_put_nil) begin
      regs.wr(x, mkCell(tag_ATOMo, 0));     // nil is the atom 0
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
      // the integer is the low 24 bits; whether bit 23 is a sign is not
      // established (the image has no such operand): refused
      if (ins.val[23] == 1) stop(EndUnimp);
      else begin
        smem.write(sp, intC(zeroExtend(ins.val[23:0])));
        sp <= sp + 1;
        next;
      end
    end
    else if (op == op_write_nil) begin
      smem.write(sp, mkCell(tag_ATOMo, 0));
      sp <= sp + 1;
      next;
    end
    else if (op == op_write_value || op == op_write_marked_value) begin
      smem.write(sp, regs.r(x));
      sp <= sp + 1;
      next;
    end
    else if (op == op_read_variable || op == op_read_atom) begin
      smem.read(sp);
      st <= XRead;
    end
    else if (op == op_put_reused_structure) begin
      dbox.deref(regs.r(y));
      st <= XReuse1;
    end
    else if (op == op_write_variable || op == op_write_marked_variable) begin
      // marked: the variable is referenced more than once (MRB, not
      // modelled)
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
    else if (op == op_collect_value || op == op_collect_vector || op == op_collect_list) next;   // MRB reclamation: not modelled
    else if (op == op_put_structured_constant) begin
      // r[x] := the cell at the label, in the module's GC area
      smem.read(labelOf(pc, c16));
      st <= XSCnst;
    end
    // ---- goals
    else if (op == op_set_value || op == op_set_marked_value) begin
      regs.wa(x, regs.r(y));       // marked: MRB, not modelled
      next;
    end
    else if (op == op_set_integer) begin
      regs.wa(x, intCell(c16));
      next;
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
      finish(tagged Next labelOf(pc, c16));
    end
    else if (op == op_execute_external) begin
      // the same goal goes on in another module: the hash box finds
      // the predicate from the descriptor at the label
      hbox.external(labelOf(pc, c16));
      st <= XExt;
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
    else if (isWaitVector) begin
      if (isRef(a)) note(a);
      if ((a.tag & 8'hfe) == tag_VECT0o + (waitN << 1)) begin
        sp <= truncate(a.val);
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
    else if (op == op_wait_value) begin
      // the guard X = Y, for atomic values; structures are refused
      if (!isAtomic(a) || !isAtomic(b)) stop(EndUnimp);
      else if (sameAtomic(a, b)) next;
      else guardFail;
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
    else if (!isInt(a) || !isInt(b)) guardFail;
    else if (op == op_modulo) begin
      // a zero divisor fails the guard; the divide box takes 32 steps
      if (b.val == 0) guardFail;
      else begin
        mbox.divide(a.val, b.val);
        st <= XDiv;
      end
    end
    else if (op == op_shift_right) begin
      // logical; a count outside 0..31 fails the guard
      Bit#(5) count = truncate(b.val);
      if (b.val >= 32) guardFail;
      else begin
        regs.wr(z, intC(a.val >> count));
        next;
      end
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
             || (op == op_equal && ia == ib)) next;
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

  rule divided (st == XDiv);
    let d <- mbox.result;
    regs.wr(z, intC(d.remainder));
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
    regs.wr(x, op == op_put_list ? mkCell(tag_LISTo + 1, absAddr(a))
                                 : mkCell(tag_VECT0o + (vectorN << 1) + 1, absAddr(a)));
    next;
  endrule

  // the next element of the structure being read; an unbound element
  // is taken as a reference to it
  rule readElement (st == XRead);
    let d <- smem.data;
    Cell el = isUnboundCell(d) ? mkCell(tag_REFo, absAddr(sp)) : d;
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
    gbox.alloc(zeroExtend(z));
    st <= XReuse2;
  endrule

  rule reuse2 (st == XReuse2);
    let a <- gbox.allocResult;
    sp <= a;
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
    else if (op == op_new_module) begin
      // new_module(Vector, ^Module): the vector box makes the object
      if (!isVec(a)) stop(EndUnimp);
      else begin
        vbox.toModule(a);
        st <= XBMod;
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
        vbox.element(a, b.val);
        st <= XBVEl;
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

  rule vElement (st == XVEl);
    let r <- vbox.result;
    if (!r.ok) guardFail;
    else begin
      regs.wr(z, r.a);
      next;
    end
  endrule

  rule bModule (st == XBMod);
    let r <- vbox.result;
    if (!r.ok) stop(EndUnimp);
    else begin
      regs.wr(y, r.a);
      finish(tagged Next afterBuiltin);
    end
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
    // a reference there is not a structure pointer: refused
    if (isRef(c)) stop(EndUnimp);
    else begin
      regs.wr(x, c);
      next;
    end
  endrule

  rule external (st == XExt);
    let t <- hbox.resolved;
    if (t matches tagged Valid .a) begin
      alt <= tagged Invalid;
      nNoted <= 0;
      finish(tagged Next a);
    end
    else stop(EndUnimp);
  endrule

  rule vPut (st == XVPut);
    let r <- vbox.result;
    regs.wr(x, r.a);
    sp <= truncate(r.b.val);
    next;
  endrule

  rule vInfo (st == XVInfo);
    let r <- vbox.result;
    regs.wr(y, r.a);
    if (op == op_switch_on_non_vector) begin
      sp <= truncate(r.b.val);
      finish(tagged Next (pc + 2));
    end
    else next;
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
