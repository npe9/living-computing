// PIM/m core: the garbage-collection box, R7G (2026-11-25).
//
// INFERENCE / OURS, the whole of it: ref/pimm/pimm_gc.py put in
// Bluespec, step for step, so that both models copy the same cells to
// the same places and print the same `K gc` line (its header has the
// sources: collect_garbage's microcode 02d5-02d7 only asks, by INFERENCE
// the collection is made later, as VPIM's is, f_gc_in_cluster.psl.c;
// the collector is a copying one by ANALOGY with VPIM's, TM-1044 ch.
// 11).
//
//   request        collect_garbage (the exec stage): a collection is
//                  asked for; the guard succeeds
//   collect        at the next goal switch (PimmCore pick_or_fire, before
//                  the alarm): the from-space is [lo, hp), the to-space
//                  starts at the heap's first cell when hp - lo fits below
//                  lo, else at hp.  The roots, in pimm_gc.py's order: the
//                  ready queue, the merger's list, the goals made ready
//                  since the last pickup (each list in order, the goal box's
//                  registers), the last of those, the armed alarm's
//                  variable (the timer box), each waiting SCSI command's
//                  buffer, CDB and three variables (the SCSI box, oldest
//                  first), the current shoen.  Then the to-space is scanned
//                  from its start to its end (records behind a header
//                  {GCHDR 3Ch, kind << 24 | length}), each copied goal's
//                  link is moved or cleared, and an FNV-1 checksum of the
//                  new heap is printed with the bounds: the K line.
//   collected      the collection is over: the goal box has the new hp and
//                  queues, the next goal is taken
//
// A forwarding mark is {GCFWD 3Dh, the new address}, written in the
// from-space.  The collector's writes are not traced (MemPort.quiet).
// Anything pimm_gc.py refuses is fatal here.
//
// Its own memory port; one FSM per routine of pimm_gc.py (block, data,
// word, module, code, goal, goals, shoen) and the main one, each called
// by start and await(done) with its arguments in registers (no routine
// is re-entered: the calls nest, word > shoen > goals > goal > block at
// the deepest, and none calls itself).
package PimmGcBox;

import StmtFSM::*;
import PimmGen::*;
import PimmTypes::*;
import PimmMem::*;
import PimmGBox::*;
import PimmTBox::*;
import PimmScsiBox::*;

interface PimmGcBox;
  method Action request;
  method Bool requested;
  method Action collect;
  method Action collected;
endinterface

Bit#(8) tag_GCHDR = 8'h3c;
Bit#(8) tag_GCFWD = 8'h3d;

typedef enum { WStatic, WTo, WFrom, WBad } Where deriving (Bits, Eq);

module mkPimmGcBox#(MemPort mem, PimmGBox gbox, PimmTBox tbox, PimmScsiBox scsi)(PimmGcBox);
  Addr base = fromInteger(heapStart);
  Bit#(28) memCells = 1 << valueOf(AddrBits);

  Reg#(Bool) asked   <- mkReg(False);
  Reg#(Bool) running <- mkReg(False);
  Reg#(Bool) over    <- mkReg(False);
  Reg#(Addr) lo  <- mkReg(fromInteger(heapStart));   // the heap is [lo, hp)
  Reg#(Addr) hp  <- mkRegU;
  Reg#(Addr) to  <- mkRegU;                          // the to-space so far: [to, top)
  Reg#(Addr) top <- mkRegU;

  function Where whereOf(Addr a) =
    a < base ? WStatic : (a >= to && a < top) ? WTo : (a >= lo && a < hp) ? WFrom : WBad;
  function Cell fwdTo(Addr a) = mkCell(tag_GCFWD, absAddr(a));
  function Cell intA(Addr a) = mkCell(tag_INTo, absAddr(a));
  function Action bad(Addr a) = fatal("gc: a pointer outside the heap");

  // the to-space's next n cells; full is fatal (pimm_gc.py alloc)
  function Action allocTo(Reg#(Addr) r, Addr n);
    action
      Bit#(28) nt = zeroExtend(top) + zeroExtend(n);
      if (nt >= memCells || (to < lo && nt > zeroExtend(lo))) fatal("gc: the to-space is full");
      r <= top;
      top <= truncate(nt);
    endaction
  endfunction

  // ---- block: n cells copied whole, after a header if asked --------
  Reg#(Addr) bA <- mkRegU;  Reg#(Addr) bN <- mkRegU;
  Reg#(Bool) bHas <- mkRegU; Reg#(Cell) bHdr <- mkRegU;
  Reg#(Addr) bR <- mkRegU;   Reg#(Addr) bNew <- mkRegU; Reg#(Addr) bH <- mkRegU;
  Reg#(Addr) bI <- mkRegU;   Reg#(Cell) bc <- mkRegU;
  Stmt blockS = seq
    if (whereOf(bA) == WBad) bad(bA);
    else if (whereOf(bA) != WFrom) bR <= bA;
    else seq
      mem.read(bA);
      action let c <- mem.data; bc <= c; endaction
      if (bc.tag == tag_GCFWD) seq
        bR <= cellAddr(bc);
        mem.read(bA + bN - 1);
        action
          let c <- mem.data;
          if (c.tag != tag_GCFWD || cellAddr(c) != bR + bN - 1) fatal("gc: a block partly copied");
        endaction
      endseq
      else seq
        if (bHas) seq
          allocTo(bH, 1);
          mem.quiet(bH, bHdr);
        endseq
        allocTo(bNew, bN);
        bI <= 0;
        while (bI < bN) seq
          mem.read(bA + bI);
          action
            let c <- mem.data;
            if (c.tag == tag_GCFWD) fatal("gc: a block partly copied");
            mem.quiet(bNew + bI, c);
          endaction
          action mem.quiet(bA + bI, fwdTo(bNew + bI)); bI <= bI + 1; endaction
        endseq
        bR <= bNew;
      endseq
    endseq
  endseq;
  FSM blockF <- mkFSM(blockS);
  function Stmt block(Addr a, Addr n, Bool has, Cell hdr) = seq
    action bA <= a; bN <= n; bHas <= has; bHdr <= hdr; endaction
    blockF.start;
    await(blockF.done);
  endseq;

  // ---- data: a structure of data cells, the first `head` a descriptor -
  Reg#(Addr) dA <- mkRegU;  Reg#(Addr) dN <- mkRegU; Reg#(Addr) dHead <- mkRegU;
  Reg#(Addr) dR <- mkRegU;  Reg#(Addr) dNew <- mkRegU; Reg#(Addr) dI <- mkRegU;
  Reg#(Addr) dF0 <- mkRegU; Reg#(Addr) dFw <- mkRegU;
  Reg#(Bool) allF <- mkRegU; Reg#(Bool) contig <- mkRegU; Reg#(Bool) headF <- mkRegU;
  Reg#(Bool) dIsF <- mkRegU; Reg#(Cell) dc <- mkRegU;
  Stmt dataS = seq
    if (whereOf(dA) == WBad) bad(dA);
    else if (whereOf(dA) != WFrom) dR <= dA;
    else seq
      action allF <= True; contig <= True; headF <= False; dI <= 0; endaction
      while (dI < dN) seq
        mem.read(dA + dI);
        action
          let c <- mem.data;
          if (c.tag == tag_GCFWD) begin
            if (dI < dHead) headF <= True;
            if (dI == 0) dF0 <= cellAddr(c);
            else if (cellAddr(c) != dF0 + dI) contig <= False;
          end
          else allF <= False;
          dI <= dI + 1;
        endaction
      endseq
      if (allF && contig) dR <= dF0;
      else if (headF) fatal("gc: a descriptor partly copied");
      else seq
        allocTo(dNew, dN);
        dI <= 0;
        while (dI < dN) seq
          mem.read(dA + dI);
          action let c <- mem.data; dc <= c; dIsF <= c.tag == tag_GCFWD; dFw <= cellAddr(c); endaction
          if (dIsF) seq
            mem.read(dFw);
            action
              let c <- mem.data;
              dc <= c;
              // an unbound variable moves in, its copy a reference to it
              if ((c.tag & 8'hfe) == tag_UNDF || (c.tag | 1) == tag_HOOKx)
                mem.quiet(dFw, mkCell(tag_REFo, absAddr(dNew + dI)));
            endaction
          endseq
          mem.quiet(dNew + dI, dc);
          action mem.quiet(dA + dI, fwdTo(dNew + dI)); dI <= dI + 1; endaction
        endseq
        dR <= dNew;
      endseq
    endseq
  endseq;
  FSM dataF <- mkFSM(dataS);
  function Stmt data(Addr a, Addr n, Addr head) = seq
    action dA <= a; dN <= n; dHead <= head; endaction
    dataF.start;
    await(dataF.done);
  endseq;

  // now(a): what a from-space cell holds, from its copy if it has one
  function Stmt now(Reg#(Cell) r, Reg#(Bool) wasF, Addr a) = seq
    mem.read(a);
    action let c <- mem.data; r <= c; wasF <= c.tag == tag_GCFWD; endaction
    if (wasF) seq
      mem.read(cellAddr(r));
      action let c <- mem.data; r <= c; endaction
    endseq
  endseq;

  // ---- module: its descriptor, then the cells, copied whole ---------
  Reg#(Addr) mA <- mkRegU; Reg#(Addr) mR <- mkRegU;
  Reg#(Cell) mc <- mkRegU; Reg#(Bool) mf <- mkRegU;
  Stmt moduleS = seq
    now(mc, mf, mA);
    if (mc.tag != tag_CDESC || mc.val[26:24] != 6) fatal("gc: no module there");
    else seq
      block(mA, zeroExtend(mc.val[23:0]) + 1, False, ?);
      mR <= bR;
    endseq
  endseq;
  FSM moduleF <- mkFSM(moduleS);
  function Stmt modul(Addr a) = seq mA <= a; moduleF.start; await(moduleF.done); endseq;

  // ---- code: a predicate's first instruction, moved with its module ---
  Reg#(Addr) cC <- mkRegU; Reg#(Addr) cR <- mkRegU; Reg#(Addr) cMod <- mkRegU;
  Reg#(Cell) cc <- mkRegU; Reg#(Bool) cf <- mkRegU;
  Stmt codeS = seq
    if (whereOf(cC) == WBad) bad(cC);
    else if (whereOf(cC) != WFrom) cR <= cC;
    else seq
      now(cc, cf, cC - 2);
      if (cc.tag != tag_PREDH) fatal("gc: code with no predicate head");
      else seq
        cMod <= cC - 2 - zeroExtend(cc.val[23:0]);
        modul(cMod);
        cR <= mR + (cC - cMod);
      endseq
    endseq
  endseq;
  FSM codeF <- mkFSM(codeS);
  function Stmt code(Addr c) = seq cC <= c; codeF.start; await(codeF.done); endseq;

  // ---- goal: a goal record, behind its header --------------------------
  Reg#(Addr) gG <- mkRegU; Reg#(Addr) gR <- mkRegU;
  Reg#(Cell) gc <- mkRegU; Reg#(Bool) gf <- mkRegU;
  Stmt goalS = seq
    if (whereOf(gG) == WBad) bad(gG);
    else if (whereOf(gG) != WFrom) gR <= gG;
    else seq
      now(gc, gf, gG + fromInteger(lay_G_ARGN));
      block(gG, fromInteger(lay_G_ARGS) + truncate(gc.val), True,
            mkCell(tag_GCHDR, 1 << 24 | (fromInteger(lay_G_ARGS) + gc.val)));
      gR <= bR;
    endseq
  endseq;
  FSM goalF <- mkFSM(goalS);
  function Stmt goal(Addr g) = seq gG <= g; goalF.start; await(goalF.done); endseq;

  // ---- goals: a list linked through G_LINK, in order -------------------
  Reg#(Addr) lG <- mkRegU; Reg#(Addr) lR <- mkRegU; Reg#(Bool) lFirst <- mkRegU;
  Stmt goalsS = seq
    action lR <= 0; lFirst <= True; endaction
    while (lG != 0) seq
      goal(lG);
      action if (lFirst) lR <= gR; lFirst <= False; endaction
      mem.read(gR + fromInteger(lay_G_LINK));
      action let c <- mem.data; lG <= c.val == 0 ? 0 : cellAddr(c); endaction
    endseq
  endseq;
  FSM goalsF <- mkFSM(goalsS);
  function Stmt goals(Addr g) = seq lG <= g; goalsF.start; await(goalsF.done); endseq;

  // ---- shoen: a shoen record, and with it its parked goals --------------
  Reg#(Addr) sS <- mkRegU; Reg#(Addr) sR <- mkRegU; Reg#(Bool) sWas <- mkRegU;
  Stmt shoenS = seq
    if (whereOf(sS) == WBad) bad(sS);
    else if (whereOf(sS) != WFrom) sR <= sS;
    else seq
      mem.read(sS);
      action let c <- mem.data; sWas <= c.tag == tag_GCFWD; endaction
      block(sS, fromInteger(lay_SH_SIZE), True,
            mkCell(tag_GCHDR, 3 << 24 | fromInteger(lay_SH_SIZE)));
      sR <= bR;
      if (!sWas) seq
        mem.read(sR + fromInteger(lay_SH_GOAL));
        action let c <- mem.data; sWas <= c.val == 0; lG <= cellAddr(c); endaction
        if (!sWas) seq goalsF.start; await(goalsF.done); endseq
      endseq
    endseq
  endseq;
  FSM shoenF <- mkFSM(shoenS);
  function Stmt shoen(Addr s) = seq sS <= s; shoenF.start; await(shoenF.done); endseq;

  // ---- word: the word with its address moved, by its tag ---------------
  Reg#(Cell) wW <- mkRegU; Reg#(Cell) wR <- mkRegU;
  Reg#(Cell) wc <- mkRegU; Reg#(Bool) wf <- mkRegU;
  Bit#(8) wt = wW.tag;
  Bit#(8) wk = wt < 8'h20 ? wt & 8'hfe : wt;
  Addr wa = cellAddr(wW);
  Bool wImm = wk == tag_INTo || wk == tag_ATOMo || wk == tag_UNDF || wk == tag_VECT0o
              || wt == tag_GMI || wt == tag_KLB || wt == tag_PREDH || wt == tag_FLTo;
  Stmt wordS = seq
    if (wImm) wR <= wW;
    else if (wk == tag_REFo) seq data(wa, 1, 0); wR <= mkCell(wt, absAddr(dR)); endseq
    else if (wk == tag_LISTo) seq data(wa, 2, 0); wR <= mkCell(wt, absAddr(dR)); endseq
    else if (wk >= tag_VECT1o && wk <= tag_VECT6o) seq
      data(wa, zeroExtend((wk - tag_VECT0o) >> 1), 0);
      wR <= mkCell(wt, absAddr(dR));
    endseq
    else if (wk == tag_VECTo) seq                    // a long vector
      if (whereOf(wa) == WBad) bad(wa);
      else if (whereOf(wa) != WFrom) wR <= wW;
      else seq
        now(wc, wf, wa);
        if (!(wc.tag == tag_VDESC && (wf || wc.val == absAddr(wa + 3))))
          fatal("gc: no long vector there");
        else seq
          now(wc, wf, wa + 1);
          data(wa, 3 + truncate(wc.val), 3);
          wR <= mkCell(wt, absAddr(dR));
        endseq
      endseq
    endseq
    else if (wk == tag_STRGo) seq
      now(wc, wf, wa);
      if (wc.tag != tag_CDESC || !(wc.val[26:24] == 0 || (wc.val[26:24] >= 3 && wc.val[26:24] <= 5)))
        fatal("gc: no string there");
      else seq
        block(wa, zeroExtend(wc.val[23:0]) + 1, False, ?);
        wR <= mkCell(wt, absAddr(bR));
      endseq
    endseq
    else if (wk == tag_HOOKo) seq
      block(wa, 2, True, mkCell(tag_GCHDR, 2 << 24 | 2));
      wR <= mkCell(wt, absAddr(bR));
    endseq
    else if (wt == tag_MOD) seq modul(wa); wR <= mkCell(wt, absAddr(mR)); endseq
    else if (wt == tag_COD) seq code(wa); wR <= mkCell(wt, absAddr(cR)); endseq
    else if (wt == tag_SHREC) seq shoen(wa); wR <= mkCell(wt, absAddr(sR)); endseq
    else fatal("gc: a word with a tag the collector does not know");
  endseq;
  FSM wordF <- mkFSM(wordS);
  function Stmt word(Cell w) = seq wW <= w; wordF.start; await(wordF.done); endseq;

  // ---- the collection ----------------------------------------------------
  Reg#(Addr) p <- mkRegU;  Reg#(Cell) pc <- mkRegU; Reg#(Cell) x <- mkRegU;
  Reg#(Addr) r <- mkRegU;  Reg#(Addr) n <- mkRegU;  Reg#(Addr) i <- mkRegU;
  Reg#(Addr) gCode <- mkRegU;
  Reg#(Addr) nRq <- mkRegU; Reg#(Addr) nMq <- mkRegU; Reg#(Addr) nMwH <- mkRegU;
  Reg#(Addr) nMwT <- mkRegU; Reg#(Addr) nCur <- mkRegU;
  Reg#(Bit#(3)) k <- mkRegU;
  Reg#(ScsiCmdState) cmd <- mkRegU;
  Reg#(Bit#(32)) h <- mkRegU;
  Bit#(32) fnvPrime = 16777619;
  Bit#(8) kind = pc.val[31:24];
  Addr toProcEnd = toProcStub + 2 * 12;

  Stmt fixGoal = seq
    mem.read(r + fromInteger(lay_G_STATUS));
    action let c <- mem.data; x <= c; endaction
    if (x.val >> 2 != 0) seq
      shoen(truncate(x.val >> 2));
      mem.quiet(r + fromInteger(lay_G_STATUS), mkCell(tag_INTo, zeroExtend(sR) << 2 | (x.val & 3)));
    endseq
    mem.read(r + fromInteger(lay_G_CODE));
    action let c <- mem.data; gCode <= cellAddr(c); endaction
    code(gCode);
    mem.quiet(r + fromInteger(lay_G_CODE), intA(cR));
    i <= fromInteger(lay_G_ARGS);
    while (i < n) seq
      mem.read(r + i);
      action let c <- mem.data; x <= c; endaction
      word(x);
      action mem.quiet(r + i, wR); i <= i + 1; endaction
    endseq
    if (gCode == mergeInStub) seq             // arg 1: {INT, its merger record}
      mem.read(r + fromInteger(lay_G_ARGS) + 1);
      action let c <- mem.data; x <= c; endaction
      data(cellAddr(x), 3, 0);
      mem.quiet(r + fromInteger(lay_G_ARGS) + 1, intA(dR));
    endseq
    else if (gCode >= toProcStub && gCode < toProcEnd && (gCode - toProcStub)[0] == 0) seq
      i <= r + fromInteger(lay_G_ARGS) + ((gCode - toProcStub) >> 1) + 1;   // arg N + 1: the code
      mem.read(i);
      action let c <- mem.data; x <= c; endaction
      code(cellAddr(x));
      mem.quiet(i, intA(cR));
    endseq
  endseq;

  Stmt fixSusp = seq
    mem.read(r + fromInteger(lay_S_NEXT));
    action let c <- mem.data; x <= c; endaction
    if (x.val != 0) seq
      block(cellAddr(x), 2, True, mkCell(tag_GCHDR, 2 << 24 | 2));
      mem.quiet(r + fromInteger(lay_S_NEXT), intA(bR));
    endseq
    mem.read(r + fromInteger(lay_S_GOAL));
    action let c <- mem.data; x <= c; endaction
    goal(cellAddr(x));
    mem.quiet(r + fromInteger(lay_S_GOAL), intA(gR));
  endseq;

  Stmt fixShoen = seq
    mem.read(r + fromInteger(lay_SH_PARENT));
    action let c <- mem.data; x <= c; endaction
    if (x.val != 0) seq
      shoen(cellAddr(x));
      mem.quiet(r + fromInteger(lay_SH_PARENT), intA(sR));
    endseq
    mem.read(r + fromInteger(lay_SH_REPORT));
    action let c <- mem.data; x <= c; endaction
    word(x);
    mem.quiet(r + fromInteger(lay_SH_REPORT), wR);
    mem.read(r + fromInteger(lay_SH_GOAL));
    action let c <- mem.data; x <= c; endaction
    if (x.val != 0) seq
      goal(cellAddr(x));
      mem.quiet(r + fromInteger(lay_SH_GOAL), intA(gR));
    endseq
  endseq;

  Stmt mainS = seq
    // the to-space (pimm_gc.py Collector.__init__)
    action
      hp <= gbox.hpOf;
      to <= (gbox.hpOf - lo <= lo - base) ? base : gbox.hpOf;
      top <= (gbox.hpOf - lo <= lo - base) ? base : gbox.hpOf;
    endaction
    // the roots
    goals(gbox.rqOf);
    nRq <= lR;
    goals(gbox.mqOf);
    nMq <= lR;
    goals(gbox.mwHOf);
    nMwH <= lR;
    nMwT <= 0;
    if (gbox.mwTOf != 0) seq goal(gbox.mwTOf); nMwT <= gR; endseq
    if (tbox.armed) seq word(tbox.wakeup); tbox.setWakeup(wR); endseq
    k <= 0;
    while (k < scsi.nWaitingOf) seq
      action let c <- scsi.gcTake; cmd <= c; endaction
      word(cmd.bufw);
      cmd.bufw <= wR;
      word(cmd.cdb);
      cmd.cdb <= wR;
      word(cmd.v0);
      cmd.v0 <= wR;
      word(cmd.v1);
      cmd.v1 <= wR;
      word(cmd.v2);
      cmd.v2 <= wR;
      action scsi.gcPut(cmd); k <= k + 1; endaction
    endseq
    nCur <= 0;
    if (gbox.shoen != 0) seq shoen(gbox.shoen); nCur <= sR; endseq
    // the scan
    p <= to;
    while (p < top) seq
      mem.read(p);
      action let c <- mem.data; pc <= c; endaction
      if (pc.tag == tag_GCHDR) seq
        action r <= p + 1; n <= zeroExtend(pc.val[23:0]); endaction
        if (kind == 1) fixGoal;
        else if (kind == 2) fixSusp;
        else if (kind == 3) fixShoen;
        else fatal("gc: a header of no kind");
        p <= p + 1 + n;
      endseq
      else if (pc.tag == tag_CDESC)
        p <= pc.val[26:24] == 6 ? p + 1 : p + 1 + zeroExtend(pc.val[23:0]);
      else if (pc.tag == tag_VDESC) action
        mem.quiet(p, mkCell(tag_VDESC, absAddr(p + 3)));
        p <= p + 3;
      endaction
      else seq
        word(pc);
        action mem.quiet(p, wR); p <= p + 1; endaction
      endseq
    endseq
    // the links (pimm_gc.py links)
    p <= to;
    while (p < top) seq
      mem.read(p);
      action let c <- mem.data; pc <= c; endaction
      if (pc.tag == tag_GCHDR) seq
        if (kind == 1) seq
          mem.read(p + 1 + fromInteger(lay_G_LINK));
          action let c <- mem.data; x <= c; endaction
          if (x.val != 0) seq
            if (!(cellAddr(x) >= lo && cellAddr(x) < hp)) fatal("gc: a goal linked outside the heap");
            mem.read(cellAddr(x));
            action
              let c <- mem.data;
              mem.quiet(p + 1 + fromInteger(lay_G_LINK), mkCell(tag_INTo, c.tag == tag_GCFWD ? c.val : 0));
            endaction
          endseq
        endseq
        p <= p + 1 + zeroExtend(pc.val[23:0]);
      endseq
      else if (pc.tag == tag_CDESC && pc.val[26:24] != 6) p <= p + 1 + zeroExtend(pc.val[23:0]);
      else p <= p + 1;
    endseq
    // the checksum and the K line
    action p <= to; h <= 32'h811c9dc5; endaction
    while (p < top) seq
      mem.read(p);
      action
        let c <- mem.data;
        Bit#(32) h1 = (h ^ zeroExtend(c.tag)) * fnvPrime;
        h <= (h1 ^ c.val) * fnvPrime;
        p <= p + 1;
      endaction
    endseq
    $display("K gc %0d %0d %0d %0d %08x", lo, hp, to, top, h);
    action
      gbox.gcSet(nRq, nMq, nMwH, nMwT, top, nCur);
      lo <= to;
      over <= True;
    endaction
  endseq;
  FSM mainF <- mkFSM(mainS);

  method Action request;
    asked <= True;
  endmethod
  method Bool requested = asked;
  method Action collect if (!running && mainF.done);
    asked <= False;
    running <= True;
    over <= False;
    mainF.start;
  endmethod
  method Action collected if (running && over);
    running <= False;
  endmethod
endmodule

endpackage
