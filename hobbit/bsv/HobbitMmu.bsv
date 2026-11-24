// HobbitMmu.bsv -- the ATT92010 memory management unit as a
// request/response box.
//
// Every field and rule below is transcribed from Chapter 2 of the
// AT&T 92010 Hobbit Microprocessor Programmer's Reference Manual
// (January 1993), cited by printed page.  The structure (a stateful box
// behind a request/response interface, not datapath spread through the
// pipeline) follows Flute (Bluespec, Inc., Apache-2.0) -- see
// docs/bluespec_architecture.md.
//
// Printed facts modelled here:
//
//   * 1,024 segments of 4 MB, 4 MB aligned (p. 2-1).
//   * Paged segment: VA 31:22 segment, 21:12 page, 11:0 offset
//     (Figure 2-1, p. 2-2); each page 1,024 words = 4 KB (p. 2-1).
//   * Nonpaged segment: VA 31:22 segment, 21:0 segment offset
//     (Figure 2-2, p. 2-2).
//   * Two fully associative 32-entry TLBs, one text and one data, and
//     two nonpaged segment registers (NPSRs), one text and one data
//     (p. 2-1; Figure 1-1 prints "2 X 32 PAGE TLB" and "2x1 SEG NPSR").
//   * Segment table: 1,024 4-byte entries in one 4 KB page frame, base
//     in STB; entry address = STB[31:12] ++ VA[31:22] (p. 2-4).
//   * Paged segment-table entry: 31:12 page table base, 11 cache,
//     10:4 reserved, 3 segment = 0, 2:1 reserved, 0 valid
//     (Table 2-1, p. 2-5).
//   * Nonpaged segment-table entry: 31:22 segment base, 21:12 bound
//     (0x0 = 4,096 bytes through 0x3FF = 4 MB in 4,096-byte steps),
//     11 cache (0 asserts NCACHE), 10:4 reserved, 3 segment = 1,
//     2 user, 1 writable, 0 valid (Table 2-2, pp. 2-5/2-6).
//   * Page-table entry: 31:12 page frame base, 11 cache (0 asserts
//     NCACHE), 10:5 reserved, 4 modified, 3 referenced, 2 user,
//     1 writable, 0 valid (Table 2-3, p. 2-7); entry address =
//     segment entry[31:12] ++ VA[21:12] (p. 2-6).
//   * A table may mix paged and nonpaged entries; bit 3 selects
//     (p. 2-6).
//   * R is set on first reference and M on a write; the memory copy is
//     written back with NCACHE asserted (pp. 2-7/2-8).
//   * TLBs and NPSRs flush on reset and on any write to STB (p. 2-8).
//     FLUSHPTE invalidates the TLB/NPSR entry for its effective address
//     and is not privileged (p. 2-8).
//   * Translation faults: no mapping, user access to a kernel-only
//     entry, or a write to a read-only entry (p. 2-3).  The fault class
//     is fetch, read or write, matching Table 1-26 IDs 0x7/0x8/0x9.
//
// Choices the manual does not make, named as choices:
//
//   * TLB replacement is round-robin.  The manual says "fully
//     associative" (p. 2-1) and prints no replacement policy.
//   * The table memory is an external port (MmuTables).  The model's
//     single-port HobbitMem cannot serve both the MMU walk and the
//     program's accesses in the same clock; the real bus arbitrates.
//     Hardware integration supplies a table port; the standalone MMU
//     testbench supplies mkMmuTableMem.  A walk is therefore
//     combinational here, and Table 2-4's walk penalties (p. 2-9) are
//     not charged: they are not instruction occupancy (docs/timing_tables.md),
//     and the bus model (plan.md step 7) owns A.
//   * R/M writeback is performed for at most one note per clock, text
//     first, because the table port has one write port.
//
// The box exposes two note channels (text and data) because the
// machine can translate a text reference and a data reference in the
// same clock; each channel is a DWire, and the one step rule consumes
// both, so no two rules ever write the TLB state.

package HobbitMmu;

import Vector::*;
import RegFile::*;
import HobbitTypes::*;

// ---------------------------------------------------------------------
// The physical memory side of the table walk.  `read` is combinational
// (a table lookup is a plain array read); `write` is the R/M writeback.
// ---------------------------------------------------------------------
interface MmuTables;
  method Word read(Word addr);
  method Action write(Word addr, Word val);
endinterface

typedef struct { Word tag; Word val; } MmuTblEntry deriving (Bits);

function Bool entryHas(Maybe#(MmuTblEntry) m, Word a);
  case (m) matches
    tagged Valid .e: return e.tag == a;
    default: return False;
  endcase
endfunction

// A 32-entry associative stand-in for the physical memory that holds the
// segment and page tables.  The model's bus (plan.md step 7) is what
// would serve a real walk; a combinational RegFile read would need one
// port per call site and the walk is called from many contexts, so the
// testbench store matches by address instead.  Every table address the
// testbenches use must be written before it is read; an unwritten
// address reads zero, which is an invalid entry (bit 0 = 0), exactly as
// unwritten physical memory behaves here.
module mkMmuTableMem(MmuTables);
  Reg#(Vector#(32, Maybe#(MmuTblEntry))) entries <-
    mkReg(replicate(tagged Invalid));

  method Word read(Word a);
    Word r = 0;
    for (Integer i = 0; i < 32; i = i + 1)
      if (entries[i] matches tagged Valid .e)
        if (e.tag == a)
          r = e.val;
    return r;
  endmethod

  method Action write(Word a, Word v);
    Vector#(32, Maybe#(MmuTblEntry)) ne = entries;
    Bool done = False;
    for (Integer i = 0; i < 32; i = i + 1)
      if (!done && entryHas(entries[i], a)) begin
        ne[i] = tagged Valid (MmuTblEntry { tag: a, val: v });
        done = True;
      end
    for (Integer i = 0; i < 32; i = i + 1)
      if (!done && !isValid(entries[i])) begin
        ne[i] = tagged Valid (MmuTblEntry { tag: a, val: v });
        done = True;
      end
    entries <= ne;
  endmethod
endmodule

// A port for a machine that never enables translation (PSW.V = 0).
module mkMmuTablesNull(MmuTables);
  method Word read(Word a) = 32'd0;
  method Action write(Word a, Word v);
  endmethod
endmodule

// ---------------------------------------------------------------------
// Types.
// ---------------------------------------------------------------------
typedef enum {
  MMU_OK,
  MMU_FETCH_FAULT,     // Table 1-26 ID 0x7
  MMU_READ_FAULT,      // Table 1-26 ID 0x8
  MMU_WRITE_FAULT      // Table 1-26 ID 0x9
} MmuFault deriving (Eq, Bits);

typedef struct {
  Word va;
  Bool isText;
  Bool isWrite;
  Bool user;      // PSW.EL = 1 (p. 1-15)
  Bool enabled;   // PSW.V = 1 (p. 2-1)
} MmuReq deriving (Bits);

typedef struct {
  Bool     valid;   // a mapping was produced
  Bool     hit;     // TLB or NPSR hit (p. 2-9); False = table walk
  Bool     paged;   // paged vs nonpaged segment (p. 2-5/2-6)
  Word     pa;
  MmuFault fault;
} MmuResp deriving (Bits);

// One TLB entry.  The tag is the 20-bit concatenation of the segment
// number and the page number; the payload is the page frame base plus
// the PTE's protection and cache bits (Table 2-3, p. 2-7).
typedef struct {
  Bool     valid;
  Bit#(10) seg;
  Bit#(10) vpn;
  Bit#(20) ppn;
  Bool     writable;
  Bool     user;
  Bool     cache;
} MmuTlbEntry deriving (Bits);

// One nonpaged segment register: the nonpaged segment-table entry
// fields of Table 2-2 (pp. 2-5/2-6).
typedef struct {
  Bool     valid;
  Bit#(10) seg;
  Bit#(10) base;
  Bit#(10) bound;
  Bool     user;
  Bool     writable;
  Bool     cache;
} MmuNpsr deriving (Bits);

function MmuTlbEntry invalidTlb();
  return MmuTlbEntry { valid: False, seg: 0, vpn: 0, ppn: 0,
                       writable: False, user: False, cache: False };
endfunction

function MmuNpsr invalidNpsr();
  return MmuNpsr { valid: False, seg: 0, base: 0, bound: 0,
                   user: False, writable: False, cache: False };
endfunction

function MmuResp mkResp(Bool valid, Bool hit, Bool paged, Word pa,
                        MmuFault f);
  return MmuResp { valid: valid, hit: hit, paged: paged, pa: pa, fault: f };
endfunction

function MmuFault reqFault(MmuReq r);
  return r.isText ? MMU_FETCH_FAULT
                  : (r.isWrite ? MMU_WRITE_FAULT : MMU_READ_FAULT);
endfunction

// A walk result carries everything the TLB/NPSR refill needs.
typedef struct {
  Bool     valid;
  Bool     paged;
  Word     pa;
  MmuFault fault;
  Bool     writable;
  Bool     user;
  Bool     cache;
  Bit#(20) ppn;
  Word     pte;      // raw page-table entry (paged only)
  Word     ste;      // raw segment-table entry
} MmuWalk deriving (Bits);

function Maybe#(MmuTlbEntry) findTlb(Vector#(32, MmuTlbEntry) v,
                                    Bit#(10) seg, Bit#(10) vpn);
  Maybe#(MmuTlbEntry) r = tagged Invalid;
  for (Integer i = 0; i < 32; i = i + 1)
    if (v[i].valid && (v[i].seg == seg) && (v[i].vpn == vpn))
      r = tagged Valid v[i];
  return r;
endfunction

function MmuFault permFault(Bool entryUser, Bool writable, MmuReq r);
  if (r.user && !entryUser)
    return reqFault(r);                 // kernel-only entry, p. 2-3
  else if (r.isWrite && !writable)
    return MMU_WRITE_FAULT;             // read-only page, p. 2-3
  else
    return MMU_OK;
endfunction

// Nonpaged bound: 0x0 = 4,096 bytes through 0x3FF = 4 MB (Table 2-2).
function Word boundBytes(Bit#(10) bound) =
  (zeroExtend(bound) + 1) << 12;

// ---------------------------------------------------------------------
// The MMU.
// ---------------------------------------------------------------------
interface HobbitMmu;
  // Pure translation of one reference.  Combinational: callers may call
  // it more than once per clock.  `enabled = False` returns the physical
  // address unchanged (PSW.V = 0, p. 1-14).
  method MmuResp translate(MmuReq r);

  // Record a translation so a miss refills the TLB/NPSR and R/M are
  // written back.  Two channels because text and data can translate in
  // the same clock.
  method Action noteText(MmuReq r);
  method Action noteText2(MmuReq r);
  method Action noteData(MmuReq r);
  method Action noteData2(MmuReq r);

  // STB write flushes all TLB/NPSR entries (p. 2-8); reset does too.
  method Action setStb(Word stb);
  method Action reset;
  // FLUSHPTE's effective address invalidates matching entries (p. 2-8).
  method Action flushPte(Word va);
  method Action flushAll;

  // Probes for the testbenches.
  method MmuTlbEntry tlbEntry(Bool text, Bit#(5) i);
  method Bool tlbValid(Bool text, Bit#(5) i);
  method MmuNpsr npsrEntry(Bool text);
  method Word stb();
  method Bit#(32) hits();
  method Bit#(32) misses();
  method Bit#(32) walks();
  method Bit#(32) faults();
  method Bit#(32) pteWrites();
endinterface

module mkHobbitMmu#(MmuTables tbl)(HobbitMmu);
  // A fully associative TLB must compare every entry every clock.  A
  // RegFile has one read port per call; 32 parallel reads would be 32
  // separate 32:1 muxes.  The 32-entry register vector is the array
  // shape a fully associative TLB needs, and the one step rule below is
  // its only writer (one assignment per vector).
  Reg#(Vector#(32, MmuTlbEntry)) tlbText <- mkReg(replicate(invalidTlb));
  Reg#(Vector#(32, MmuTlbEntry)) tlbData <- mkReg(replicate(invalidTlb));
  Reg#(MmuNpsr) npsrText <- mkReg(invalidNpsr);
  Reg#(MmuNpsr) npsrData <- mkReg(invalidNpsr);
  Reg#(Word) stbR <- mkReg(0);
  Reg#(Bit#(5)) nextText <- mkReg(0);
  Reg#(Bit#(5)) nextData <- mkReg(0);
  Reg#(Bit#(32)) hitsR <- mkReg(0);
  Reg#(Bit#(32)) missesR <- mkReg(0);
  Reg#(Bit#(32)) walksR <- mkReg(0);
  Reg#(Bit#(32)) faultsR <- mkReg(0);
  Reg#(Bit#(32)) pteWritesR <- mkReg(0);

  Wire#(Maybe#(MmuReq)) noteTextW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(MmuReq)) noteText2W <- mkDWire(tagged Invalid);
  Wire#(Maybe#(MmuReq)) noteDataW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(MmuReq)) noteData2W <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Word))   flushPteW <- mkDWire(tagged Invalid);
  Wire#(Bool)           flushAllW <- mkDWire(False);
  Wire#(Bool)           resetW <- mkDWire(False);
  Wire#(Maybe#(Word))   stbW <- mkDWire(tagged Invalid);

  // Segment table entry address: STB[31:12] ++ VA[31:22] (p. 2-4).
  function Word steAddr(Word va) = { stbR[31:12], va[31:22], 2'b00 };
  // Page table entry address: segment entry[31:12] ++ VA[21:12] (p. 2-6).
  function Word pteAddr(Word ste, Word va) =
    { ste[31:12], va[21:12], 2'b00 };

  function MmuWalk walk(MmuReq r);
    Word vs = steAddr(r.va);
    Word ste0 = tbl.read(vs);
    if (ste0[0] != 1'b1)
      return MmuWalk { valid: False, paged: False, pa: 0,
                       fault: reqFault(r), writable: False, user: False,
                       cache: False, ppn: 0, pte: 0, ste: ste0 };
    else if (ste0[3] == 1'b0) begin
      // Paged segment (Table 2-1, p. 2-5).
      Word pte = tbl.read(pteAddr(ste0, r.va));
      if (pte[0] != 1'b1)
        return MmuWalk { valid: False, paged: True, pa: 0,
                         fault: reqFault(r), writable: False, user: False,
                         cache: False, ppn: 0, pte: pte, ste: ste0 };
      else begin
        let f = permFault(pte[2] == 1'b1, pte[1] == 1'b1, r);
        return MmuWalk { valid: (f == MMU_OK), paged: True,
                         pa: { pte[31:12], r.va[11:0] },
                         fault: f,
                         writable: pte[1] == 1'b1,
                         user: pte[2] == 1'b1,
                         cache: pte[11] == 1'b1,
                         ppn: pte[31:12], pte: pte, ste: ste0 };
      end
    end else begin
      // Nonpaged segment (Table 2-2, pp. 2-5/2-6).
      Word off = zeroExtend(r.va[21:0]);
      if (off >= boundBytes(ste0[21:12]))
        return MmuWalk { valid: False, paged: False, pa: 0,
                         fault: reqFault(r), writable: False, user: False,
                         cache: False, ppn: 0, pte: 0, ste: ste0 };
      else begin
        let f = permFault(ste0[2] == 1'b1, ste0[1] == 1'b1, r);
        return MmuWalk { valid: (f == MMU_OK), paged: False,
                         pa: { ste0[31:22], r.va[21:0] },
                         fault: f,
                         writable: ste0[1] == 1'b1,
                         user: ste0[2] == 1'b1,
                         cache: ste0[11] == 1'b1,
                         ppn: 0, pte: 0, ste: ste0 };
      end
    end
  endfunction

  function Word pteAfterRef(Word pte, Bool isWrite) =
    pte | 32'h8 | (isWrite ? 32'h10 : 32'd0);

  function Vector#(32, MmuTlbEntry) refillTlb(Vector#(32, MmuTlbEntry) v,
                                              Bit#(5) idx, MmuTlbEntry e) =
    update(v, idx, e);

  function MmuResp translateFn(MmuReq r);
    if (!r.enabled)
      return mkResp(True, True, False, r.va, MMU_OK);
    else begin
      // Text TLB or data TLB (p. 2-1).
      let hitE = r.isText
                   ? findTlb(tlbText, r.va[31:22], r.va[21:12])
                   : findTlb(tlbData, r.va[31:22], r.va[21:12]);
      if (isValid(hitE)) begin
        let e = validValue(hitE);
        let f = permFault(e.user, e.writable, r);
        return mkResp(f == MMU_OK, True, True,
                      { e.ppn, r.va[11:0] }, f);
      end else begin
        let n = r.isText ? npsrText : npsrData;
        if (n.valid && (n.seg == r.va[31:22])) begin
          if (zeroExtend(r.va[21:0]) >= boundBytes(n.bound))
            return mkResp(False, True, False, 0, reqFault(r));
          else begin
            let f = permFault(n.user, n.writable, r);
            return mkResp(f == MMU_OK, True, False,
                          { n.base, r.va[21:0] }, f);
          end
        end else begin
          let w = walk(r);
          return mkResp(w.valid, False, w.paged, w.pa,
                        w.valid ? MMU_OK : w.fault);
        end
      end
    end
  endfunction

  rule step;
    Vector#(32, MmuTlbEntry) nt = tlbText;
    Vector#(32, MmuTlbEntry) nd = tlbData;
    MmuNpsr nnT = npsrText;
    MmuNpsr nnD = npsrData;
    Bit#(5) nNextT = nextText;
    Bit#(5) nNextD = nextData;
    Bit#(32) nHits = hitsR;
    Bit#(32) nMss = missesR;
    Bit#(32) nWalks = walksR;
    Bit#(32) nFaults = faultsR;
    Bit#(32) nPteW = pteWritesR;
    Word nStb = stbR;
    Maybe#(Tuple2#(Word, Word)) wb = tagged Invalid;

    if (resetW) begin
      nt = replicate(invalidTlb);
      nd = replicate(invalidTlb);
      nnT = invalidNpsr;
      nnD = invalidNpsr;
      nStb = 0;
    end else if (flushAllW) begin
      nt = replicate(invalidTlb);
      nd = replicate(invalidTlb);
      nnT = invalidNpsr;
      nnD = invalidNpsr;
    end else begin
      // A write to STB flushes the TLBs and NPSRs (p. 2-8).
      if (isValid(stbW)) begin
        nStb = validValue(stbW);
        nt = replicate(invalidTlb);
        nd = replicate(invalidTlb);
        nnT = invalidNpsr;
        nnD = invalidNpsr;
      end

      // FLUSHPTE invalidates the TLB/NPSR entry for its effective
      // address, in both the text and the data structures (p. 2-8).
      if (isValid(flushPteW)) begin
        let va = validValue(flushPteW);
        for (Integer i = 0; i < 32; i = i + 1) begin
          if (nt[i].valid && (nt[i].seg == va[31:22]) &&
              (nt[i].vpn == va[21:12]))
            nt[i] = invalidTlb;
          if (nd[i].valid && (nd[i].seg == va[31:22]) &&
              (nd[i].vpn == va[21:12]))
            nd[i] = invalidTlb;
        end
        if (nnT.valid && (nnT.seg == va[31:22])) nnT = invalidNpsr;
        if (nnD.valid && (nnD.seg == va[31:22])) nnD = invalidNpsr;
      end

      // ---- text note ------------------------------------------------
      if (isValid(noteTextW)) begin
        let r = validValue(noteTextW);
        let resp = translateFn(r);
        if (resp.fault != MMU_OK)
          nFaults = nFaults + 1;
        else if (resp.hit)
          nHits = nHits + 1;
        else begin
          nMss = nMss + 1;
          nWalks = nWalks + 1;
          let w = walk(r);
          if (w.valid) begin
            if (w.paged) begin
              nt = refillTlb(nt, nNextT,
                             MmuTlbEntry { valid: True, seg: r.va[31:22],
                                           vpn: r.va[21:12], ppn: w.ppn,
                                           writable: w.writable,
                                           user: w.user, cache: w.cache });
              nNextT = nNextT + 1;
              let np = pteAfterRef(w.pte, r.isWrite);
              if ((np != w.pte) && !isValid(wb)) begin
                wb = tagged Valid (tuple2(pteAddr(w.ste, r.va), np));
                nPteW = nPteW + 1;
              end
            end else begin
              nnT = MmuNpsr { valid: True, seg: r.va[31:22],
                              base: w.ste[31:22], bound: w.ste[21:12],
                              user: w.ste[2] == 1'b1,
                              writable: w.ste[1] == 1'b1,
                              cache: w.ste[11] == 1'b1 };
            end
          end else
            nFaults = nFaults + 1;
        end
      end

      // ---- text note ------------------------------------------------
      if (isValid(noteText2W)) begin
        let r = validValue(noteText2W);
        let resp = translateFn(r);
        if (resp.fault != MMU_OK)
          nFaults = nFaults + 1;
        else if (resp.hit)
          nHits = nHits + 1;
        else begin
          nMss = nMss + 1;
          nWalks = nWalks + 1;
          let w = walk(r);
          if (w.valid) begin
            if (w.paged) begin
              nt = refillTlb(nt, nNextT,
                             MmuTlbEntry { valid: True, seg: r.va[31:22],
                                           vpn: r.va[21:12], ppn: w.ppn,
                                           writable: w.writable,
                                           user: w.user, cache: w.cache });
              nNextT = nNextT + 1;
              let np = pteAfterRef(w.pte, r.isWrite);
              if ((np != w.pte) && !isValid(wb)) begin
                wb = tagged Valid (tuple2(pteAddr(w.ste, r.va), np));
                nPteW = nPteW + 1;
              end
            end else begin
              nnT = MmuNpsr { valid: True, seg: r.va[31:22],
                              base: w.ste[31:22], bound: w.ste[21:12],
                              user: w.ste[2] == 1'b1,
                              writable: w.ste[1] == 1'b1,
                              cache: w.ste[11] == 1'b1 };
            end
          end else
            nFaults = nFaults + 1;
        end
      end

      // ---- data note ------------------------------------------------
      if (isValid(noteDataW)) begin
        let r = validValue(noteDataW);
        let resp = translateFn(r);
        if (resp.fault != MMU_OK)
          nFaults = nFaults + 1;
        else if (resp.hit)
          nHits = nHits + 1;
        else begin
          nMss = nMss + 1;
          nWalks = nWalks + 1;
          let w = walk(r);
          if (w.valid) begin
            if (w.paged) begin
              nd = refillTlb(nd, nNextD,
                             MmuTlbEntry { valid: True, seg: r.va[31:22],
                                           vpn: r.va[21:12], ppn: w.ppn,
                                           writable: w.writable,
                                           user: w.user, cache: w.cache });
              nNextD = nNextD + 1;
              let np = pteAfterRef(w.pte, r.isWrite);
              if ((np != w.pte) && !isValid(wb)) begin
                wb = tagged Valid (tuple2(pteAddr(w.ste, r.va), np));
                nPteW = nPteW + 1;
              end
            end else begin
              nnD = MmuNpsr { valid: True, seg: r.va[31:22],
                              base: w.ste[31:22], bound: w.ste[21:12],
                              user: w.ste[2] == 1'b1,
                              writable: w.ste[1] == 1'b1,
                              cache: w.ste[11] == 1'b1 };
            end
          end else
            nFaults = nFaults + 1;
        end
      end
      // ---- data note ------------------------------------------------
      if (isValid(noteData2W)) begin
        let r = validValue(noteData2W);
        let resp = translateFn(r);
        if (resp.fault != MMU_OK)
          nFaults = nFaults + 1;
        else if (resp.hit)
          nHits = nHits + 1;
        else begin
          nMss = nMss + 1;
          nWalks = nWalks + 1;
          let w = walk(r);
          if (w.valid) begin
            if (w.paged) begin
              nd = refillTlb(nd, nNextD,
                             MmuTlbEntry { valid: True, seg: r.va[31:22],
                                           vpn: r.va[21:12], ppn: w.ppn,
                                           writable: w.writable,
                                           user: w.user, cache: w.cache });
              nNextD = nNextD + 1;
              let np = pteAfterRef(w.pte, r.isWrite);
              if ((np != w.pte) && !isValid(wb)) begin
                wb = tagged Valid (tuple2(pteAddr(w.ste, r.va), np));
                nPteW = nPteW + 1;
              end
            end else begin
              nnD = MmuNpsr { valid: True, seg: r.va[31:22],
                              base: w.ste[31:22], bound: w.ste[21:12],
                              user: w.ste[2] == 1'b1,
                              writable: w.ste[1] == 1'b1,
                              cache: w.ste[11] == 1'b1 };
            end
          end else
            nFaults = nFaults + 1;
        end
      end
    end


    tlbText  <= nt;
    tlbData  <= nd;
    npsrText <= nnT;
    npsrData <= nnD;
    stbR     <= nStb;
    nextText <= nNextT;
    nextData <= nNextD;
    hitsR    <= nHits;
    missesR  <= nMss;
    walksR   <= nWalks;
    faultsR  <= nFaults;
    pteWritesR <= nPteW;
    if (isValid(wb)) begin
      match { .a, .v } = validValue(wb);
      tbl.write(a, v);
    end
  endrule

  method MmuResp translate(MmuReq r) = translateFn(r);

  method Action noteText(MmuReq r);
    noteTextW <= tagged Valid r;
  endmethod

  method Action noteText2(MmuReq r);
    noteText2W <= tagged Valid r;
  endmethod

  method Action noteData(MmuReq r);
    noteDataW <= tagged Valid r;
  endmethod

  method Action noteData2(MmuReq r);
    noteData2W <= tagged Valid r;
  endmethod

  method Action setStb(Word stb);
    stbW <= tagged Valid stb;
  endmethod

  method Action reset();
    resetW <= True;
  endmethod

  method Action flushPte(Word va);
    flushPteW <= tagged Valid va;
  endmethod

  method Action flushAll();
    flushAllW <= True;
  endmethod

  method MmuTlbEntry tlbEntry(Bool text, Bit#(5) i) =
    text ? tlbText[i] : tlbData[i];
  method Bool tlbValid(Bool text, Bit#(5) i) =
    text ? tlbText[i].valid : tlbData[i].valid;
  method MmuNpsr npsrEntry(Bool text) = text ? npsrText : npsrData;
  method Word stb() = stbR;
  method Bit#(32) hits() = hitsR;
  method Bit#(32) misses() = missesR;
  method Bit#(32) walks() = walksR;
  method Bit#(32) faults() = faultsR;
  method Bit#(32) pteWrites() = pteWritesR;
endmodule

// ---------------------------------------------------------------------
// A translating memory face.  The core's stack cache and prefetch see a
// HobbitMem; every access is translated first when PSW.V = 1 (p. 2-1).
// A fault is latched so the event unit can raise the Table 1-26
// fetch/read/write fault; the access itself returns zero or is dropped,
// exactly as p. 2-3 says no memory access is made on a protection
// violation.
// ---------------------------------------------------------------------
typedef struct {
  Word addr;
  Bool isWrite;
} MmuMemFault deriving (Bits);

interface HobbitMmuMem;
  interface HobbitMem mem;
  method Bool fault();
  method Word faultAddr();
  method Bool faultWrite();
  method Action clearFault();
  // This clock's write is translated at kernel level whatever the PSW
  // (the privileged machine's KCALL frame, mkHobbitCoreSystem); a read
  // in the same clock is not affected.
  method Action kernelNow();
endinterface

module mkHobbitMmuMem#(HobbitMem phys, HobbitMmu mmu, Bool isText,
                       Reg#(Word) psw)(HobbitMmuMem);
  Reg#(Bool) lastOk <- mkReg(True);
  Reg#(Bool) faultR <- mkReg(False);
  Reg#(Word) faultAddrR <- mkReg(0);
  Reg#(Bool) faultWriteR <- mkReg(False);
  Wire#(Maybe#(MmuMemFault)) faultRW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(MmuMemFault)) faultWW <- mkDWire(tagged Invalid);
  Wire#(Bool) clearW <- mkDWire(False);
  Wire#(Bool) kernelW <- mkDWire(False);

  function MmuReq req(Word a, Bool wr) =
    MmuReq { va: a, isText: isText, isWrite: wr,
             user: (psw[10] == 1'b1) && !(wr && kernelW),
             enabled: (psw[16] == 1'b1) };

  rule latch;
    if (clearW) begin
      faultR <= False;
    end else if (isValid(faultRW)) begin
      match { .f } = validValue(faultRW);
      faultR      <= True;
      faultAddrR  <= f.addr;
      faultWriteR <= f.isWrite;
    end else if (isValid(faultWW)) begin
      match { .f } = validValue(faultWW);
      faultR      <= True;
      faultAddrR  <= f.addr;
      faultWriteR <= f.isWrite;
    end
  endrule

  interface HobbitMem mem;
    method Action readReq(Word a);
      let x = mmu.translate(req(a, False));
      if (isText) mmu.noteText(req(a, False));
      else        mmu.noteData(req(a, False));
      if (x.fault == MMU_OK) begin
        phys.readReq(x.pa);
        lastOk <= True;
      end else begin
        lastOk <= False;
        faultRW <= tagged Valid (MmuMemFault { addr: a, isWrite: False });
      end
    endmethod

    method Word readData() = lastOk ? phys.readData() : 32'd0;

    method Action write(Word a, Word v);
      let x = mmu.translate(req(a, True));
      if (isText) mmu.noteText2(req(a, True));
      else        mmu.noteData2(req(a, True));
      if (x.fault == MMU_OK)
        phys.write(x.pa, v);
      else
        faultWW <= tagged Valid (MmuMemFault { addr: a, isWrite: True });
    endmethod

    // Testbench probe only, like HobbitMem::peek: physical address.
    method Word peek(Word a) = phys.peek(a);
  endinterface

  method Bool fault() = faultR;
  method Word faultAddr() = faultAddrR;
  method Bool faultWrite() = faultWriteR;
  method Action clearFault();
    clearW <= True;
  endmethod
  method Action kernelNow();
    kernelW <= True;
  endmethod
endmodule


endpackage
