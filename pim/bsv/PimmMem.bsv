// PIM/m core: the memory, one block RAM of 40-bit cells behind
// request/response, shared by its clients (PimmCore.bsv's port order:
// instruction fetch, the hash box, the data box, the goal box, the
// string box, the execute stage's structure reads and writes, the
// vector box, the merger box, the shoen box, the SCSI box and, since
// 2026-11-25, the passive-unification box).  Every write is traced here, when it is
// requested: the machine does one thing at a time, so request order is
// the order of events, and the address and data printed are the ones
// queued for the RAM.
package PimmMem;

import BRAM::*;
import FIFO::*;
import Vector::*;
import PimmTypes::*;

interface MemPort;
  method Action read(Addr a);
  method Action write(Addr a, Cell d);
  method ActionValue#(Cell) data;        // the answer to a read, in order
endinterface

typedef 11 MemClients;

interface PimmMem;
  interface Vector#(MemClients, MemPort) port;
endinterface

typedef struct {
  Bit#(4) who;
  Bool wr;
  Addr addr;
  Cell data;
} MemReq deriving (Bits);

// Two RAMs behind the one queue: the cells below the heap (the IPL
// image and the stubs), loaded from the file, and the heap, which is
// not loaded: a heap cell is written before it is read.  So the file
// is 2^15 lines whatever the memory's size.  A checkpoint's heap
// (heapFile not "": the lockstep from a saved machine,
// ref/pimm/lockstep_shell.py) is loaded from its own file, addressed
// lines (@) from the heap's first cell: loading writes nothing, so
// nothing of it is traced.
typedef 15 LowBits;

module mkPimmMem#(String file, String heapFile)(PimmMem);
  BRAM_Configure cfg = defaultValue;
  cfg.loadFormat = tagged Hex file;
  BRAM1Port#(Bit#(LowBits), Cell) low <- mkBRAM1Server(cfg);
  BRAM_Configure hcfg = defaultValue;
  if (heapFile != "") hcfg.loadFormat = tagged Hex heapFile;
  BRAM1Port#(Addr, Cell) ram <- mkBRAM1Server(hcfg);
  FIFO#(Bool) fromLow <- mkSizedFIFO(4);

  // One request queue for all clients: requests reach the RAM in the
  // order they were made, whoever made them, so a read never overtakes
  // an earlier write from another box.
  FIFO#(MemReq) reqs <- mkFIFO;
  Vector#(MemClients, FIFO#(Cell)) resps <- replicateM(mkFIFO);
  FIFO#(Bit#(4)) who <- mkSizedFIFO(4);

  rule issue;
    let r = reqs.first;
    reqs.deq;
    Bool isLow = (r.addr >> valueOf(LowBits)) == 0;
    if (isLow)
      low.portA.request.put(BRAMRequest { write: r.wr, responseOnWrite: False,
                                          address: truncate(r.addr), datain: r.data });
    else
      ram.portA.request.put(BRAMRequest { write: r.wr, responseOnWrite: False,
                                          address: r.addr, datain: r.data });
    if (!r.wr) begin
      who.enq(r.who);
      fromLow.enq(isLow);
    end
  endrule

  rule routeLow (fromLow.first);
    let d <- low.portA.response.get;
    resps[who.first].enq(d);
    who.deq;
    fromLow.deq;
  endrule

  rule route (!fromLow.first);
    let d <- ram.portA.response.get;
    resps[who.first].enq(d);
    who.deq;
    fromLow.deq;
  endrule

  function MemPort mkPort(Integer i);
    return (interface MemPort;
      method Action read(Addr a);
        reqs.enq(MemReq { who: fromInteger(i), wr: False, addr: a, data: ? });
      endmethod
      method Action write(Addr a, Cell d);
        reqs.enq(MemReq { who: fromInteger(i), wr: True, addr: a, data: d });
        traceM(a, d);
      endmethod
      method ActionValue#(Cell) data;
        resps[i].deq;
        return resps[i].first;
      endmethod
    endinterface);
  endfunction

  interface port = genWith(mkPort);
endmodule

endpackage
