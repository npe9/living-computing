// PimSdramStore.bsv -- LocalStore backed by the ULX3S SDRAM controller.
//
// The PIM's LocalStore is a 40-bit-word memory.  The SDRAM controller is
// a 256-bit-granule MemoryServer.  This adapter packs six 40-bit words
// into one granule (240 bits used), caches one granule, and exposes
// `miss`/`fetch` so the pipeline can hold a fetch or load until the
// granule is resident.
//
// Read and write requests are buffered in separate FIFOs so the pipeline
// rule never enqueues to the SDRAM request port twice.  Two drain rules
// forward one request per cycle, writes first and reads only when no read
// is outstanding.  A write invalidates the cache and bumps the epoch, so
// a read response that was already in flight is discarded.

package PimSdramStore;

import Memory::*;
import ClientServer::*;
import GetPut::*;
import FIFOF::*;
import PimTypes::*;
import PimStages::*;

module mkPimSdramStore#(MemoryServer#(64, 256) server)
                       (LocalStore);

  Reg#(Bit#(256)) cacheData  <- mkReg(0);
  Reg#(Bit#(64))  cacheTag   <- mkReg(0);
  Reg#(Bool)      cacheValid <- mkReg(False);
  Reg#(Bool)      pending    <- mkReg(False);
  Reg#(Bit#(64))  pendingTag <- mkReg(0);
  Reg#(Bit#(8))   epoch      <- mkReg(0);
  Reg#(Bit#(8))   readEpoch  <- mkReg(0);

  FIFOF#(MemoryRequest#(64, 256)) writes <- mkFIFOF;
  FIFOF#(MemoryRequest#(64, 256)) reads  <- mkFIFOF;

  function Bit#(64) granuleOf(Addr a) = zeroExtend(a >> 2);
  function Bit#(3)  wordOf(Addr a)    = truncate(a & 3);

  function Bit#(8) shift40(Bit#(3) w) = zeroExtend(w) * 40;
  function Bit#(5) shift5(Bit#(3) w) = zeroExtend(w) * 5;
  function Bit#(32) mask5(Bit#(3) w) = 32'h0000001F << shift5(w);

  function Bit#(256) wordField(Bit#(256) d, Bit#(3) w) =
    d >> shift40(w);

  function Bit#(256) placeWord(Word w, Bit#(3) idx) =
    zeroExtend(w) << shift40(idx);

  function Bit#(256) maskWord(Bit#(3) idx) =
    zeroExtend(40'hFFFFFFFFFF) << shift40(idx);

  // Writes first: a store must not be overtaken by a younger load.  A
  // read is sent only when no read is outstanding and no write is queued.
  rule drainWrite (!pending && writes.notEmpty);
    server.request.put(writes.first);
    writes.deq;
    cacheValid <= False;
    epoch      <= epoch + 1;
  endrule

  rule drainRead (!pending && !writes.notEmpty && reads.notEmpty);
    let r = reads.first;
    reads.deq;
    server.request.put(r);
    pending    <= True;
    pendingTag <= r.address;
    readEpoch  <= epoch;
  endrule

  rule fillResponse (pending);
    let r <- server.response.get();
    pending <= False;
    if (readEpoch == epoch) begin
      cacheData  <= r.data;
      cacheTag   <= pendingTag;
      cacheValid <= True;
    end
  endrule

  method Word read(Addr a) =
    cacheValid && cacheTag == granuleOf(a)
      ? truncate(wordField(cacheData, wordOf(a)))
      : 0;

  method Bool miss(Addr a) =
    !(cacheValid && cacheTag == granuleOf(a)) || pending || !reads.notEmpty;

  method Action fetch(Addr a);
    if (!pending && !reads.notEmpty && !(cacheValid && cacheTag == granuleOf(a))) begin
      reads.enq(MemoryRequest {
        write:   False,
        address: granuleOf(a),
        data:    0,
        byteen:  0
      });
    end
  endmethod

  method Action write(Addr a, Word w);
    writes.enq(MemoryRequest {
      write:   True,
      address: granuleOf(a),
      data:    placeWord(w, wordOf(a)),
      byteen:  mask5(wordOf(a))
    });
  endmethod

endmodule

endpackage
