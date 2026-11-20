// PIM/m core: the memory, one block RAM of 40-bit cells behind
// request/response, shared by three clients (instruction fetch, the
// hash box, the data box).  Client 0 has priority.
package PimmMem;

import BRAM::*;
import FIFO::*;
import FIFOF::*;
import Vector::*;
import PimmTypes::*;

interface MemPort;
  method Action read(Addr a);
  method Action write(Addr a, Cell d);
  method ActionValue#(Cell) data;        // the answer to a read, in order
endinterface

typedef 3 MemClients;

interface PimmMem;
  interface Vector#(MemClients, MemPort) port;
endinterface

typedef struct {
  Bool wr;
  Addr addr;
  Cell data;
} MemReq deriving (Bits);

module mkPimmMem#(String file)(PimmMem);
  BRAM_Configure cfg = defaultValue;
  cfg.loadFormat = tagged Hex file;
  BRAM1Port#(Addr, Cell) ram <- mkBRAM1Server(cfg);

  // dequeue side unguarded: `issue` tests notEmpty itself
  Vector#(MemClients, FIFOF#(MemReq)) reqs <- replicateM(mkGFIFOF(False, True));
  Vector#(MemClients, FIFO#(Cell)) resps <- replicateM(mkFIFO);
  FIFO#(Bit#(2)) who <- mkSizedFIFO(4);

  rule issue (reqs[0].notEmpty || reqs[1].notEmpty || reqs[2].notEmpty);
    Bit#(2) i = reqs[0].notEmpty ? 0 : (reqs[1].notEmpty ? 1 : 2);
    let r = reqs[i].first;
    reqs[i].deq;
    ram.portA.request.put(BRAMRequest { write: r.wr, responseOnWrite: False,
                                        address: r.addr, datain: r.data });
    if (!r.wr) who.enq(i);
  endrule

  rule route;
    let d <- ram.portA.response.get;
    resps[who.first].enq(d);
    who.deq;
  endrule

  function MemPort mkPort(Integer i);
    return (interface MemPort;
      method Action read(Addr a);
        reqs[i].enq(MemReq { wr: False, addr: a, data: ? });
      endmethod
      method Action write(Addr a, Cell d);
        reqs[i].enq(MemReq { wr: True, addr: a, data: d });
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
