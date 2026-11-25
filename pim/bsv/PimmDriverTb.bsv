// Lockstep driver bench.  It executes a script of operations on the
// core from outside (make a variable, load an argument, spawn a goal,
// run, bind, print) and the core prints its trace.  The script is
// generated/pimm_script.hex, written by a lockstep test through
// ref/pimm/driver.py, which documents the operations and plays the
// same script on the reference model for comparison.
//
// The SCSI device is a tape (ref/pimm/driver.py "The device tape"): the
// answers the reference model's device gave, in order, after the
// script's END.  Each command the core puts on its port is printed as a
// B line from what the core sent, then answered from the tape.
//
// mkPimmShellTb is the same bench on a checkpoint: the heap of a saved
// machine loaded into the core's memory (checkpoint/heap.hex), the
// script checkpoint/script.hex, which begins with the RESTORE
// operations that give the core the rest of the saved machine
// (ref/pimm/lockstep_shell.py, bsv/run_pimm_shell.sh).
package PimmDriverTb;

import RegFile::*;
import PimmGen::*;
import PimmTypes::*;
import PimmCore::*;
import PimmScsiBox::*;

typedef enum { End, NewVar, Arg, ArgC, Spawn, Run, Out, Unify, UnifyC,
               NewStr, SetEl, Ptr, Slot, SetW, Poll, Tape, Restore, Alarm } Kind deriving (Bits, Eq);

// the device: idle, printing a command's CDB, printing a SEND's bytes,
// giving an answer's bytes
typedef enum { DevIdle, DevCdb, DevData, DevAnswer } DevState deriving (Bits, Eq);

module mkPimmDriverTb(Empty);
  let d <- mkPimmDriver("generated/pimm_script.hex", "");
  return d;
endmodule

module mkPimmShellTb(Empty);
  let d <- mkPimmDriver("checkpoint/script.hex", "checkpoint/heap.hex");
  return d;
endmodule

module mkPimmDriver#(String scriptFile, String heap)(Empty);
  PimmCore core <- mkPimmCore("generated/pimm_ipl.hex", heap);
  RegFile#(Bit#(24), Bit#(64)) script <- mkRegFileFullLoad(scriptFile);
  RegFile#(Bit#(4), Cell) slot <- mkRegFileFull;

  Reg#(Bit#(24)) ip      <- mkReg(0);
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

  // the device tape: where the next entry is; none, no device
  Reg#(Bool)     hasTape <- mkReg(False);
  Reg#(Bit#(24)) tp      <- mkRegU;
  Reg#(DevState) dev     <- mkReg(DevIdle);
  Reg#(Bit#(32)) left    <- mkRegU;     // bytes still to print, or to give
  Reg#(ScsiCmd)  cmd     <- mkRegU;
  Reg#(Bool)     low     <- mkRegU;     // the answer: the tape word's low half next

  rule request (!awaited);
    Bool answer = False;
    case (kind)
      End:    $finish(0);
      NewVar: begin core.newVar; answer = True; end
      // a slot keeps what it gives: MRB on
      Arg:    core.setArg(a, marked(slot.sub(sb)));
      ArgC:   core.setArg(a, cell_);
      Spawn:  begin core.spawn(truncate(cell_.val), a); answer = True; end
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
      Poll:   begin core.scsiPoll; answer = True; end
      Tape:   begin hasTape <= True; tp <= truncate(cell_.val); end
      // a checkpoint's state, given to the core silently (PimmCore.restore)
      Restore: core.restore(a, cell_);
      // R8: idle, an alarm armed: the clock moved on to it (driver.py ALARM)
      Alarm:  core.skipToAlarm;
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

  rule spawnedGoal (awaited && kind == Spawn);
    let g <- core.spawned;
    awaited <= False;
    ip <= ip + 1;
  endrule

  rule polled (awaited && kind == Poll);
    let n <- core.scsiPolled;
    awaited <= False;
    ip <= ip + 1;
  endrule

  // ---- the device ----------------------------------------------------------
  // the top `n` bytes of a word, in hex
  function Action hexBytes(Bit#(32) w, Bit#(32) n);
    action
      case (n)
        1: $write("%02x", w[31:24]);
        2: $write("%04x", w[31:16]);
        3: $write("%06x", w[31:8]);
        default: $write("%08x", w);
      endcase
    endaction
  endfunction

  function Bit#(32) min4(Bit#(32) v) = v < 4 ? v : 4;
  Bit#(64) entry = script.sub(tp);
  Bit#(8)  entryKind = entry[63:56];

  function Action noTape(String why);
    action
      $display("X device tape: %s at word %0d", why, tp);
      $finish(1);
    endaction
  endfunction

  // the line ends; the tape's answer
  function Action answerCommand;
    action
      $display("");
      if (entryKind == 2) begin
        core.scsiResp(tagged Answer { ready: False, result: 0, n: 0 });
        tp <= tp + 1;
        dev <= DevIdle;
      end
      else if (entryKind == 3) begin
        Bit#(32) nb = zeroExtend(entry[55:32]);
        core.scsiResp(tagged Answer { ready: True, result: entry[31:0], n: nb });
        tp <= tp + 1;
        left <= nb;
        low <= False;
        dev <= nb == 0 ? DevIdle : DevAnswer;
      end
      else noTape("not a command's answer");
    endaction
  endfunction

  // after the CDB: direction and length, then a SEND's bytes
  function Action afterCdb(ScsiCmd c);
    action
      $write(" %0d %0d", c.dir, c.length);
      if (c.dir == 1 && c.length != 0) begin
        $write(" ");
        left <= pack(c.length);
        dev <= DevData;
      end
      else answerCommand;
    endaction
  endfunction

  rule devRequest (dev == DevIdle);
    let r <- core.scsiReq;
    case (r) matches
      tagged Init: begin
        $display("B init");
        if (!hasTape) noTape("none");
        else if (entryKind != 1) noTape("not scsi_init's answer");
        else begin
          core.scsiResp(tagged Size entry[31:0]);
          tp <= tp + 1;
        end
      end
      tagged Command .c: begin
        if (!hasTape) noTape("none");
        $write("B %0d %0d ", c.unit, c.lun);
        cmd <= c;
        if (c.cdbLen == 0) afterCdb(c);
        else begin
          left <= c.cdbLen;
          dev <= DevCdb;
        end
      end
      default: fatal("driver: a word from the core where a command was expected");
    endcase
  endrule

  rule devWord (dev == DevCdb || dev == DevData);
    let r <- core.scsiReq;
    if (r matches tagged Word .w) begin
      hexBytes(w, min4(left));
      if (left > 4) left <= left - 4;
      else if (dev == DevCdb) afterCdb(cmd);
      else answerCommand;
    end
    else fatal("driver: a command from the core where a word was expected");
  endrule

  rule devAnswer (dev == DevAnswer);
    Bit#(64) d = script.sub(tp);
    core.scsiResp(tagged Data (low ? d[31:0] : d[63:32]));
    left <= left - min4(left);
    low <= !low;
    // the last word's other half, if it is not used, is padding
    if (low || left <= 4) tp <= tp + 1;
    if (left <= 4) dev <= DevIdle;
  endrule
endmodule

endpackage
