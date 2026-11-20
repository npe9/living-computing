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
               NewStr, SetEl, Ptr, Slot } Kind deriving (Bits, Eq);

module mkPimmDriverTb(Empty);
  PimmCore core <- mkPimmCore("generated/pimm_ipl.hex");
  RegFile#(Bit#(20), Bit#(64)) script <- mkRegFileFullLoad("generated/pimm_script.hex");
  RegFile#(Bit#(4), Cell) slot <- mkRegFileFull;

  Reg#(Bit#(20)) ip      <- mkReg(0);
  Reg#(Bool)     awaited <- mkReg(False);   // the operation's answer is awaited

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
      Arg:    core.setArg(a, slot.sub(sb));
      ArgC:   core.setArg(a, cell_);
      Spawn:  core.spawn(truncate(cell_.val), a);
      Run:    begin core.run; answer = True; end
      Out:    begin core.derefReq(slot.sub(sa)); answer = True; end
      Unify:  begin core.unifyReq(slot.sub(sa), slot.sub(sb)); answer = True; end
      UnifyC: begin core.unifyReq(slot.sub(sa), cell_); answer = True; end
      NewStr: begin core.newString(cell_.val >> 8, zeroExtend(cell_.val[7:0])); answer = True; end
      SetEl:  begin core.setElement(slot.sub(sa), cell_.val >> 16, zeroExtend(cell_.val[15:0])); answer = True; end
      Ptr:    slot.upd(sa, mkCell(cell_.tag, slot.sub(sb).val));
      Slot:   slot.upd(sa, cell_);
      default: fatal("driver: operation not implemented");
    endcase
    if (answer) awaited <= True;
    else ip <= ip + 1;
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

  rule gotString (awaited && (kind == NewStr || kind == SetEl));
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
