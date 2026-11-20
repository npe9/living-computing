// PIM/m core: the memory, one block RAM of 40-bit cells behind
// request/response, shared by six clients (instruction fetch, the
// hash box, the data box, the goal box, the string box, the execute
// stage's structure writes).  Every write is traced here, when it is
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

typedef 6 MemClients;

interface PimmMem;
  interface Vector#(MemClients, MemPort) port;
endinterface

typedef struct {
  Bit#(3) who;
  Bool wr;
  Addr addr;
  Cell data;
} MemReq deriving (Bits);

module mkPimmMem#(String file)(PimmMem);
  BRAM_Configure cfg = defaultValue;
  cfg.loadFormat = tagged Hex file;
  BRAM1Port#(Addr, Cell) ram <- mkBRAM1Server(cfg);

  // One request queue for all clients: requests reach the RAM in the
  // order they were made, whoever made them, so a read never overtakes
  // an earlier write from another box.
  FIFO#(MemReq) reqs <- mkFIFO;
  Vector#(MemClients, FIFO#(Cell)) resps <- replicateM(mkFIFO);
  FIFO#(Bit#(3)) who <- mkSizedFIFO(4);

  rule issue;
    let r = reqs.first;
    reqs.deq;
    ram.portA.request.put(BRAMRequest { write: r.wr, responseOnWrite: False,
                                        address: r.addr, datain: r.data });
    if (!r.wr) who.enq(r.who);
  endrule

  rule route;
    let d <- ram.portA.response.get;
    resps[who.first].enq(d);
    who.deq;
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
