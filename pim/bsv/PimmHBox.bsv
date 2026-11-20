// PIM/m core: the hash box.  Walks the table that follows a
// hash_on_constant instruction (docs/pimm_semantics.md):
//
//   pc      hash_on_constant r, mask
//   pc+1    the miss label, relative to itself: pc + 1 + 2 + value
//   pc+2..  mask+1 slots, indexed by key AND mask:
//             not an integer cell      empty
//             {INT, count<<16 | off}   `count` pairs at slot + off
//   pair    {key, {INT, off}}, target = the off cell + 1 + off
//
// A key that is not bound takes the miss label.
//
// It also walks the pairs that follow a switch_on_constant
// (library/assembler/klb_opr.kl1, r_c16_c16_16s_sw):
//
//   pc      switch_on_constant r, count
//   pair    {key, {INT, else << 16 | off}}, `count` of them; both
//           fields are relative to the second cell + 2
//
// compared in order.  No match takes the last pair's else label; a key
// that is not bound takes the first pair's.
package PimmHBox;

import FIFO::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;

interface PimmHBox;
  method Action lookup(Addr pc, Cell key, Bit#(16) mask, Bool bound);
  method Action scan(Addr pc, Cell key, Bit#(16) count, Bool bound);
  method ActionValue#(Addr) target;
endinterface

typedef enum { HIdle, HMiss, HSlot, HKey, HOff, HSKey, HSLab } HState deriving (Bits, Eq);

module mkPimmHBox#(MemPort mem)(PimmHBox);
  Reg#(HState)   st    <- mkReg(HIdle);
  Reg#(Addr)     base  <- mkRegU;     // the instruction
  Reg#(Cell)     want  <- mkRegU;     // the key as a table entry holds it
  Reg#(Bit#(16)) msk   <- mkRegU;
  Reg#(Bool)     live  <- mkRegU;
  Reg#(Addr)     miss  <- mkRegU;
  Reg#(Addr)     ent   <- mkRegU;     // slot, then the pair being compared
  Reg#(Bit#(16)) left  <- mkRegU;     // pairs still to compare
  FIFO#(Addr)    resQ  <- mkFIFO;

  rule gotMiss (st == HMiss);
    let c <- mem.data;
    Addr m = labelOf(base + 1, c.val[15:0]);
    miss <= m;
    if (!live) begin
      resQ.enq(m);
      st <= HIdle;
    end
    else begin
      Addr slot = base + 2 + zeroExtend(want.val[15:0] & msk);
      ent <= slot;
      mem.read(slot);
      st <= HSlot;
    end
  endrule

  rule gotSlot (st == HSlot);
    let c <- mem.data;
    Bit#(16) count = c.val[31:16];
    if (c.tag != tag_INTo || count == 0) begin
      resQ.enq(miss);
      st <= HIdle;
    end
    else begin
      Addr e = ent + zeroExtend(c.val[15:0]);
      ent <= e;
      left <= count;
      mem.read(e);
      st <= HKey;
    end
  endrule

  rule gotKey (st == HKey);
    let c <- mem.data;
    if (c == want) begin
      mem.read(ent + 1);
      st <= HOff;
    end
    else if (left == 1) begin
      resQ.enq(miss);
      st <= HIdle;
    end
    else begin
      left <= left - 1;
      ent <= ent + 2;
      mem.read(ent + 2);
    end
  endrule

  rule gotOff (st == HOff);
    let c <- mem.data;
    resQ.enq(ent + 1 + 1 + signExtend(c.val[15:0]));
    st <= HIdle;
  endrule

  // ---- switch_on_constant ----------------------------------------------
  Reg#(Bool) hit <- mkRegU;

  rule gotSKey (st == HSKey);
    let c <- mem.data;
    hit <= live && c == want;
    mem.read(ent + 1);
    st <= HSLab;
  endrule

  rule gotSLab (st == HSLab);
    let c <- mem.data;
    Addr here = ent + 1;
    if (hit) begin
      resQ.enq(labelOf(here, c.val[15:0]));
      st <= HIdle;
    end
    else if (!live || left == 1) begin
      resQ.enq(labelOf(here, c.val[31:16]));
      st <= HIdle;
    end
    else begin
      left <= left - 1;
      ent <= ent + 2;
      mem.read(ent + 2);
      st <= HSKey;
    end
  endrule

  method Action scan(Addr pc, Cell key, Bit#(16) count, Bool bound) if (st == HIdle);
    want <= mkCell(key.tag & 8'hfe, key.val);
    live <= bound;
    left <= count;
    ent <= pc + 1;
    mem.read(pc + 1);
    st <= HSKey;
  endmethod

  method Action lookup(Addr pc, Cell key, Bit#(16) mask, Bool bound) if (st == HIdle);
    base <= pc;
    want <= mkCell(key.tag & 8'hfe, key.val);
    msk <= mask;
    live <= bound;
    mem.read(pc + 1);
    st <= HMiss;
  endmethod

  method ActionValue#(Addr) target;
    resQ.deq;
    return resQ.first;
  endmethod
endmodule

endpackage
