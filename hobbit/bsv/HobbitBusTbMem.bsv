// HobbitBusTbMem.bsv -- testbench-only bus memory.
//
// The core's memory (HobbitBus.bsv, mkHobbitBusMemStub) is a RegFile with
// one read port and one write port, which is the shape the FPGA maps to a
// block RAM.  A testbench that names a dozen constant addresses would ask
// that RegFile for a dozen read ports, which the library does not allow.
// This module therefore provides the same bus slave interface over a
// 256-word register array: same protocol, same byte-merge rule, no port
// budget.  It is never part of the core or the board build.

package HobbitBusTbMem;

import Vector::*;
import HobbitTypes::*;
import HobbitBus::*;

interface HobbitBusTbStub;
  interface HobbitBusSlave busSlave;
  method Word peek(Word addr);
  method Action setRetry(Bool v);
  method Action setBerr(Bool v);
  method Action setWait(Bool v);
endinterface

module mkHobbitBusTbStub#(Reg#(Bool) holdR, Reg#(Bool) bgrantR)
                         (HobbitBusTbStub);
  Reg#(Vector#(256, Word)) m <- mkReg(replicate(0));
  Reg#(Vector#(256, Bool)) written <- mkReg(replicate(False));
  Reg#(Bool) retryR <- mkReg(False);
  Reg#(Bool) berrR <- mkReg(False);
  Reg#(Bool) waitR <- mkReg(False);

  function Bit#(8) idx(Word a) = truncate(a >> 2);

  function Word readWord(Word a);
    let i = idx(a);
    return written[i] ? m[i] : 32'd0;
  endfunction

  function Word mergeBytes(Word old, Word d, Bit#(4) be);
    Word r = old;
    for (Integer i = 0; i < 4; i = i + 1) begin
      if (be[i] == 1'b1) begin
        Bit#(8) b = truncate(d >> (8 * i));
        Word mask = 32'h000000FF << (8 * i);
        r = (r & ~mask) | (zeroExtend(b) << (8 * i));
      end
    end
    return r;
  endfunction

  function BusResp respondF(BusPins p);
    Bool done = p.start && !waitR;
    return BusResp { dack:  done && !retryR && !berrR,
                     berr:  done && berrR,
                     retry: done && retryR,
                     hold:  holdR,
                     bgrant: bgrantR,
                     hd:    (p.start && p.read) ? readWord(p.ha) : 32'd0 };
  endfunction

  method Word peek(Word a) = readWord(a);
  method Action setRetry(Bool v);
    retryR <= v;
  endmethod
  method Action setBerr(Bool v);
    berrR <= v;
  endmethod
  method Action setWait(Bool v);
    waitR <= v;
  endmethod

  interface HobbitBusSlave busSlave;
    method BusResp respond(BusPins p) = respondF(p);
    method Action commit(BusPins p);
      if (p.start && !p.read && !retryR && !berrR && !waitR) begin
        let i = idx(p.ha);
        m[i] <= mergeBytes(readWord(p.ha), p.hd, p.be);
        written[i] <= True;
      end
    endmethod
    method Bool hold() = holdR;
    method Bool bgrant() = bgrantR;
  endinterface
endmodule

interface HobbitBusTbMem;
  interface HobbitBusMaster master;
  method Word peek(Word addr);
  method BusPins pins();
  method BusPins writePins();
  method BusPins blockPins();
  method BusResp response();
  method BusResp writeResponse();
  method BusResp blockResponse();
  method Action setHold(Bool v);
  method Action setBgrant(Bool v);
  method Action setRetry(Bool v);
  method Action setBerr(Bool v);
  method Action setWait(Bool v);
  method Bool retried();
  method Bool busError();
  method Bool overrun();
  method Bool granted();
  method Bool breq();
  method Bool bgack();
endinterface

module mkHobbitBusTbMem(HobbitBusTbMem);
  Reg#(Bool) holdR <- mkReg(False);
  Reg#(Bool) bgrantR <- mkReg(True);

  HobbitBusTbStub stub <- mkHobbitBusTbStub(holdR, bgrantR);
  HobbitBusMaster mst <- mkHobbitBusMaster(stub.busSlave);

  method Word peek(Word addr) = stub.peek(addr);
  method BusPins pins() = mst.pins();
  method BusPins writePins() = mst.writePins();
  method BusPins blockPins() = mst.blockPins();
  method BusResp response() = mst.response();
  method BusResp writeResponse() = mst.writeResponse();
  method BusResp blockResponse() = mst.blockResponse();
  method Action setHold(Bool v);
    holdR <= v;
  endmethod
  method Action setBgrant(Bool v);
    bgrantR <= v;
  endmethod
  method Action setRetry(Bool v);
    stub.setRetry(v);
  endmethod
  method Action setBerr(Bool v);
    stub.setBerr(v);
  endmethod
  method Action setWait(Bool v);
    stub.setWait(v);
  endmethod
  method Bool retried() = mst.retried();
  method Bool busError() = mst.busError();
  method Bool overrun() = mst.overrun();
  method Bool granted() = mst.granted();
  method Bool breq() = mst.breq();
  method Bool bgack() = mst.bgack();

  interface HobbitBusMaster master = mst;
endmodule

endpackage
