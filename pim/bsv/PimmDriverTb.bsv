// Lockstep driver bench.  It executes a script of operations on the
// core from outside (make a variable, load an argument, spawn a goal,
// run, bind, print) and the core prints its trace.  The script is
// generated/pimm_script.hex, written by a lockstep test through
// ref/pimm/driver.py, which documents the operations and plays the
// same script on the reference model for comparison.
package PimmDriverTb;

import RegFile::*;
import PimmGen::*;
import PimmTypes::*;
import PimmCore::*;

typedef enum { End, NewVar, Arg, ArgC, Spawn, Run, Out, Unify, UnifyC,
               NewStr, SetEl, Ptr, Slot, SetW } Kind deriving (Bits, Eq);

module mkPimmDriverTb(Empty);
  PimmCore core <- mkPimmCore("generated/pimm_ipl.hex");
  RegFile#(Bit#(20), Bit#(64)) script <- mkRegFileFullLoad("generated/pimm_script.hex");
  RegFile#(Bit#(4), Cell) slot <- mkRegFileFull;

  Reg#(Bit#(20)) ip      <- mkReg(0);
  Reg#(Bool)     awaited <- mkReg(False);   // the operation's answer is awaited
  // cycles one operation has been awaited.  A core that never answers
  // (a fault injection once left it running for two hours) ends the
  // simulation with a line no reference trace has.
  Reg#(Bit#(31)) waited  <- mkReg(0);

  let w = script.sub(ip);
  Bit#(8) kind8 = w[63:56];
  Kind kind = unpack(truncate(kind8));
  Bit#(8) a = w[55:48];
  Bit#(8) b = w[47:40];
  Cell cell_ = mkCell(w[39:32], w[31:0]);
  Bit#(4) sa = truncate(a);
  Bit#(4) sb = truncate(b);

  rule request (!awaited);
    Bool answer = False;
    case (kind)
      End:    $finish(0);
      NewVar: begin core.newVar; answer = True; end
      // a slot keeps what it gives: MRB on
      Arg:    core.setArg(a, marked(slot.sub(sb)));
      ArgC:   core.setArg(a, cell_);
      Spawn:  core.spawn(truncate(cell_.val), a);
      Run:    begin core.run; answer = True; end
      Out:    begin core.derefReq(marked(slot.sub(sa))); answer = True; end
      Unify:  begin core.unifyReq(marked(slot.sub(sa)), marked(slot.sub(sb))); answer = True; end
      UnifyC: begin core.unifyReq(marked(slot.sub(sa)), cell_); answer = True; end
      NewStr: begin core.newString(cell_.val >> 8, zeroExtend(cell_.val[7:0])); answer = True; end
      SetEl:  begin core.setElement(slot.sub(sa), cell_.val >> 16, zeroExtend(cell_.val[15:0])); answer = True; end
      // a word of the bench's own new string, in place
      SetW:   begin core.pokeWord(slot.sub(sa), zeroExtend({b, cell_.tag}), cell_.val); answer = True; end
      Ptr:    slot.upd(sa, mkCell(cell_.tag, slot.sub(sb).val));
      Slot:   slot.upd(sa, cell_);
      default: fatal("driver: operation not implemented");
    endcase
    if (answer) awaited <= True;
    else ip <= ip + 1;
    waited <= 0;
  endrule

  rule stalled (awaited);
    if (waited[30] == 1) begin
      $display("X the core has not answered operation %0d in 2^30 cycles", ip);
      $finish(1);
    end
    waited <= waited + 1;
  endrule

  rule gotVar (awaited && kind == NewVar);
    let v <- core.newVarResult;
    slot.upd(sa, v);
    awaited <= False;
    ip <= ip + 1;
  endrule

  rule ran (awaited && kind == Run);
    let e <- core.finished;
    awaited <= False;
    ip <= ip + 1;
  endrule

  rule printed (awaited && kind == Out);
    let v <- core.derefResp;
    $display("O %02x%08x", v.tag, v.val);
    awaited <= False;
    ip <= ip + 1;
  endrule

  rule gotString (awaited && (kind == NewStr || kind == SetEl || kind == SetW));
    let v <- core.stringResult;
    slot.upd(sa, v);
    awaited <= False;
    ip <= ip + 1;
  endrule

  rule unified (awaited && (kind == Unify || kind == UnifyC));
    let ok <- core.unifyDone;
    awaited <= False;
    ip <= ip + 1;
  endrule
endmodule

endpackage
