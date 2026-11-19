// PimSdramStoreTb.bsv -- Bluesim testbench for the SDRAM-backed LocalStore.
//
// A deterministic MemoryServer#(64,256) model (256 granules of 32 bytes,
// byte-enable writes, optional held read response) backs
// mkPimSdramStore.  The test checks:
//   * read miss -> fetch -> response -> hit, with all six words of the
//     granule readable and no second request issued on a hit;
//   * a write invalidates the granule and the next read refetches it;
//   * six 40-bit words pack into one 256-bit granule at the documented
//     offsets: granule a/6, data 40*(a%6), byteen 0x1F << 5*(a%6),
//     240 bits used (word 6 starts granule 1);
//   * a read response still in flight when a write drains is stale: it
//     must not fill the cache, and the next read refetches the new data;
//   * a load in the cycle a write drains must miss: the epoch bump that
//     invalidates the cache lands at the end of that cycle.
//
// Run from bsv/: ./run_sdram_tb.sh
//
// Discriminating power (observed 2026-11-19, not predicted).  The one
// injected bug lived in a /tmp copy of the sources: fillResponse's
// `if (readEpoch == epoch)` guard was removed and the fill stamped
// `cacheEpoch <= epoch`, i.e. every response was treated as current.
// Observed output (no "PimSdramTb: PASS" line; the raw simulator still
// exits 0 on $finish):
//   FAIL: stale read response filled the cache (t2): got 0xcafe000003, want 0x0000000000
//   FAIL: stale read response filled the cache (t3): got 0xcafe000003, want 0x0000000000
//   FAIL: stale read response filled the cache (t4): got 0xcafe000003, want 0x0000000000
//   FAIL: miss(15) after the stale response: got 0, want 1
//   FAIL: refetched word 3: got 0xcafe000003, want 0x123456789a
//   FAIL: timeout at cycle 3001, phase 4
//
// A second injection (2026-11-19) removed `|| writes.notEmpty` from
// `miss`, so a load in the drain cycle hit the stale granule.  Observed:
//   FAIL: miss(1) in the drain cycle: got 0, want 1
//   PimSdramTb: FAIL

package PimSdramStoreTb;

import RegFile::*;
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import StmtFSM::*;
import Memory::*;
import PimTypes::*;
import PimStages::*;
import PimSdramStore::*;

// ---------------------------------------------------------------
// Deterministic memory model.  Addresses are granule numbers; only the
// low 8 bits index the model, which is plenty for this test.
// ---------------------------------------------------------------

interface FakeMem;
  interface MemoryServer#(64, 256) server;
  method Action setData(Bit#(64) g, Bit#(256) d);
  method Bit#(256) peek(Bit#(64) g);
  method Action setHold(Bool h);      // capture (do not answer) the next read
  method Bool held();                 // a read response is being held
  method Action releaseHeld();            // answer the held read with held data
  method Bool reqAvail();
  method MemoryRequest#(64, 256) reqHead();
  method Action popReq();             // retire the observed request
  method Bit#(32) written();          // writes applied to the model
endinterface

module mkFakeMem(FakeMem);
  RegFile#(Bit#(8), Bit#(256)) mem <- mkRegFile(0, 255);
  FIFOF#(MemoryRequest#(64, 256))  inQ  <- mkFIFOF;
  FIFOF#(MemoryResponse#(256))     rsps <- mkFIFOF;

  // The observation log must never apply backpressure (mkFIFOF is a
  // two-element FIFO here, and this test does not dequeue while a burst
  // of writes is in flight), so it is an indexed RegFile.
  RegFile#(Bit#(6), MemoryRequest#(64, 256)) logMem <- mkRegFile(0, 63);
  Reg#(Bit#(6)) logHead <- mkReg(0);
  Reg#(Bit#(6)) logTail <- mkReg(0);

  Reg#(Bool)        holdMode  <- mkReg(False);
  Reg#(Bool)        heldValid <- mkReg(False);
  Reg#(Bool)        relReq    <- mkReg(False);
  Reg#(Bit#(256))   heldData  <- mkReg(0);
  Reg#(Bit#(32))    nWritten  <- mkReg(0);

  function Bit#(8) idx(Bit#(64) g) = truncate(g);

  function Bit#(256) byteMask(Integer i) =
    zeroExtend(8'hFF) << (8 * i);

  function Bit#(256) merge(Bit#(256) old, Bit#(256) d, Bit#(32) be);
    Bit#(256) r = old;
    for (Integer i = 0; i < 32; i = i + 1)
      if (be[i] == 1)
        r = (r & ~byteMask(i)) | (d & byteMask(i));
    return r;
  endfunction

  // The only response enqueue and the only memory write site, in two
  // mutually exclusive rules: a release and a queued request never race
  // on the response queue (the queue holds at most one entry here).
  rule releaseRsp (heldValid && relReq);
    rsps.enq(MemoryResponse {data: heldData});
    heldValid <= False;
    relReq    <= False;
  endrule

  rule serveQ (!(heldValid && relReq) && inQ.notEmpty);
    let req = inQ.first;
    inQ.deq;
    if (req.write) begin
      mem.upd(idx(req.address),
              merge(mem.sub(idx(req.address)), req.data,
                    truncate(req.byteen)));
      nWritten <= nWritten + 1;
    end
    else if (holdMode) begin
      heldData  <= mem.sub(idx(req.address));
      heldValid <= True;
    end
    else begin
      rsps.enq(MemoryResponse {data: mem.sub(idx(req.address))});
    end
  endrule

  interface MemoryServer server;
    interface Put request;
      method Action put(MemoryRequest#(64, 256) req);
        logMem.upd(logTail, req);
        logTail <= logTail + 1;
        inQ.enq(req);
      endmethod
    endinterface
    interface Get response = toGet(rsps);
  endinterface

  method Action setData(Bit#(64) g, Bit#(256) d) = mem.upd(idx(g), d);
  method Bit#(256) peek(Bit#(64) g) = mem.sub(idx(g));
  method Action setHold(Bool h) = action holdMode <= h; endaction;
  method Bool held() = heldValid;
  method Action releaseHeld();
    if (heldValid) begin relReq <= True; end
  endmethod
  method Bool reqAvail() = logHead != logTail;
  method MemoryRequest#(64, 256) reqHead() = logMem.sub(logHead);
  method Action popReq(); logHead <= logHead + 1; endmethod
  method Bit#(32) written() = nWritten;
endmodule

// ---------------------------------------------------------------
// Testbench
// ---------------------------------------------------------------

(* synthesize *)
module mkPimSdramTb(Empty);

  FakeMem fake <- mkFakeMem;
  LocalStore store <- mkPimSdramStore(fake.server);

  Reg#(Bit#(32)) cycles <- mkReg(0);
  Reg#(Bit#(4))  phase  <- mkReg(0);
  Reg#(Bool)     ok     <- mkReg(True);
  Reg#(Bit#(32)) wbase  <- mkReg(0);

  rule count;
    cycles <= cycles + 1;
  endrule

  // A stuck await must fail, not hang.
  rule watchdog (cycles > 3000);
    $display("FAIL: timeout at cycle %0d, phase %0d", cycles, phase);
    $finish;
  endrule

  // Six 40-bit words, one per offset in a granule.
  function Word tw(Bit#(3) i) = 40'hA500000000 + zeroExtend(i);
  function Word ow(Bit#(3) i) = 40'hCAFE000000 + zeroExtend(i);

  function Bit#(256) packedTw();
    Bit#(256) d = 0;
    for (Integer i = 0; i < 6; i = i + 1)
      d = d | (zeroExtend(tw(fromInteger(i))) << (40 * i));
    return d;
  endfunction

  function Bit#(256) packedOw();
    Bit#(256) d = 0;
    for (Integer i = 0; i < 6; i = i + 1)
      d = d | (zeroExtend(ow(fromInteger(i))) << (40 * i));
    return d;
  endfunction

  function Bit#(8) sh40(Bit#(3) i) = zeroExtend(i) * 8'd40;
  function Bit#(8) sh5(Bit#(3) i)  = zeroExtend(i) * 8'd5;

  function Bit#(256) place(Word w, Bit#(3) i) = zeroExtend(w) << sh40(i);
  function Bit#(32) byteEn(Bit#(3) i) = 32'h0000001F << sh5(i);

  function Action chk40(String label, Word got, Word want);
    return (got == want) ? noAction : (action
      $display("FAIL: %s: got 0x%010h, want 0x%010h", label, got, want);
      ok <= False;
    endaction);
  endfunction

  function Action chk256(String label, Bit#(256) got, Bit#(256) want);
    return (got == want) ? noAction : (action
      $display("FAIL: %s: got 0x%064h, want 0x%064h", label, got, want);
      ok <= False;
    endaction);
  endfunction

  function Action chkBool(String label, Bool got, Bool want);
    return (got == want) ? noAction : (action
      $display("FAIL: %s: got %0d, want %0d", label, got, want);
      ok <= False;
    endaction);
  endfunction

  // Check and retire one observed SDRAM request.  Reads carry data/byteen 0.
  function Action chkReq(String label, Bool wr, Bit#(64) addr,
                         Bit#(256) data, Bit#(32) be);
    action
      let r = fake.reqHead();
      Bool okW = r.write == wr;
      Bool okA = r.address == addr;
      Bool okD = r.data == data;
      Bool okE = r.byteen == be;
      if (!okW)
        $display("FAIL: %s: write = %0d, want %0d", label, r.write, wr);
      if (!okA)
        $display("FAIL: %s: granule = %0d, want %0d", label, r.address, addr);
      if (!okD)
        $display("FAIL: %s: data = 0x%064h, want 0x%064h",
                 label, r.data, data);
      if (!okE)
        $display("FAIL: %s: byteen = 0x%08h, want 0x%08h",
                 label, r.byteen, be);
      if (!(okW && okA && okD && okE)) ok <= False;
      fake.popReq();
    endaction
  endfunction

  Stmt test = seq
    action fake.setData(0, packedTw()); endaction
    action fake.setData(2, packedOw()); endaction

    // ---- Phase 1: miss -> fetch -> response -> hit. ----
    action phase <= 1; endaction
    chk40("read(0) before fetch", store.read(0), 0);
    chkBool("miss(0) before fetch", store.miss(0), True);
    action store.fetch(0); endaction
    await(!store.miss(0));
    chkBool("miss(0) after refill", store.miss(0), False);
    chk40("read(0) after refill", store.read(0), tw(0));
    chk40("read(1) after refill", store.read(1), tw(1));
    chk40("read(2) after refill", store.read(2), tw(2));
    chk40("read(3) after refill", store.read(3), tw(3));
    chk40("read(4) after refill", store.read(4), tw(4));
    chk40("read(5) after refill", store.read(5), tw(5));
    await(fake.reqAvail());
    chkReq("fill granule 0", False, 0, 0, 0);
    chkBool("miss(0) after fill is a hit", store.miss(0), False);
    // A fetch on a hit must not issue a request.
    action store.fetch(0); endaction
    action noAction; endaction
    action noAction; endaction
    chkBool("fetch on a hit issued a request", fake.reqAvail(), False);

    // ---- Phase 2: a write invalidates the granule. ----
    action phase <= 2; endaction
    action store.write(1, tw(1) + 40'h100); endaction
    // The drain cycle: writes.notEmpty is still true, so the load must
    // not hit the stale granule.
    chkBool("miss(1) in the drain cycle", store.miss(1), True);
    await(fake.reqAvail());
    chkReq("write word 1", True, 0, place(tw(1) + 40'h100, 1), byteEn(1));
    chkBool("miss(1) after a write", store.miss(1), True);
    action store.fetch(1); endaction
    await(!store.miss(1));
    chk40("read(1) after write refetch", store.read(1), tw(1) + 40'h100);
    chk40("read(0) still in the refetched granule", store.read(0), tw(0));
    await(fake.reqAvail());
    chkReq("refetch granule 0", False, 0, 0, 0);

    // ---- Phase 3: six words pack into one granule at 40-bit offsets. ----
    action phase <= 3; endaction
    action store.write(0, tw(0)); endaction
    action store.write(1, tw(1)); endaction
    action store.write(2, tw(2)); endaction
    action store.write(3, tw(3)); endaction
    action store.write(4, tw(4)); endaction
    action store.write(5, tw(5)); endaction
    await(fake.reqAvail()); chkReq("pack word 0", True, 0, place(tw(0),0), byteEn(0));
    await(fake.reqAvail()); chkReq("pack word 1", True, 0, place(tw(1),1), byteEn(1));
    await(fake.reqAvail()); chkReq("pack word 2", True, 0, place(tw(2),2), byteEn(2));
    await(fake.reqAvail()); chkReq("pack word 3", True, 0, place(tw(3),3), byteEn(3));
    await(fake.reqAvail()); chkReq("pack word 4", True, 0, place(tw(4),4), byteEn(4));
    await(fake.reqAvail()); chkReq("pack word 5", True, 0, place(tw(5),5), byteEn(5));
    chk256("packed granule 0", fake.peek(0), packedTw());
    action store.fetch(3); endaction
    await(!store.miss(3));
    chk40("pack read word 0", store.read(0), tw(0));
    chk40("pack read word 1", store.read(1), tw(1));
    chk40("pack read word 2", store.read(2), tw(2));
    chk40("pack read word 3", store.read(3), tw(3));
    chk40("pack read word 4", store.read(4), tw(4));
    chk40("pack read word 5", store.read(5), tw(5));
    await(fake.reqAvail());
    chkReq("pack refetch granule 0", False, 0, 0, 0);
    // Word 6 is the first word of the next granule, at offset 0.
    action store.write(6, tw(0) + 40'h200); endaction
    await(fake.reqAvail());
    chkReq("word 6 starts granule 1", True, 1,
           place(tw(0) + 40'h200, 0), byteEn(0));

    // ---- Phase 4: an in-flight read response after a write is stale. ----
    action phase <= 4; endaction
    // The cache holds granule 0; granule 2 is a miss.
    action fake.setHold(True); endaction
    action store.fetch(15); endaction
    await(fake.held());
    await(fake.reqAvail());
    chkReq("held read granule 2", False, 2, 0, 0);
    // The write drains while the read response is still held (the epoch
    // bump must make that response stale).
    action wbase <= fake.written(); endaction
    action store.write(15, 40'h123456789A); endaction
    await(fake.reqAvail());
    chkReq("write word 3 of granule 2", True, 2,
           place(40'h123456789A, 3), byteEn(3));
    await(fake.written() == wbase + 1);
    action fake.releaseHeld(); endaction
    action fake.setHold(False); endaction
    // Sample the cache while the stale response is consumed; with the
    // epoch broken the fill shows up on one of these cycles.
    chk40("stale read response filled the cache (t1)", store.read(15), 0);
    chk40("stale read response filled the cache (t2)", store.read(15), 0);
    chk40("stale read response filled the cache (t3)", store.read(15), 0);
    chk40("stale read response filled the cache (t4)", store.read(15), 0);
    chkBool("miss(15) after the stale response", store.miss(15), True);
    // The stale response may still have been pending when this runs, so
    // retry the fetch: a fetch while `pending` is dropped by design.
    action store.fetch(15); endaction
    action store.fetch(15); endaction
    action store.fetch(15); endaction
    action store.fetch(15); endaction
    await(!store.miss(15));
    chk40("refetched word 3", store.read(15), 40'h123456789A);
    chk40("refetched word 0", store.read(12), ow(0));
    chk40("refetched word 5", store.read(17), ow(5));
    await(fake.reqAvail());
    chkReq("refetch granule 2", False, 2, 0, 0);
    chkBool("no extra request left over", fake.reqAvail(), False);

    // ---- Report. ----
    action
      if (ok) $display("PimSdramTb: PASS");
      else    $display("PimSdramTb: FAIL");
    endaction
    $finish;
  endseq;

  mkAutoFSM(test);
endmodule

endpackage
