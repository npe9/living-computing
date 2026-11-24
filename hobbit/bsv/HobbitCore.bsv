// HobbitCore.bsv -- orchestration of the ATT92010 Hobbit model.
//
// Structure (the pipeline of printed pp. 1-32/1-33 and section 4.3 of
// the January 1993 Programmer's Reference Manual):
//
//   HobbitPrefetch     the 3 KB three-way prefetch buffer cache (box).
//   HobbitPdu          prefetch/decode unit, PDU_S1/S2/S3 (three stage
//                      modules, Figure 1-1 "3-STAGE PIPELINE").
//   HobbitDecodeStore  32-entry direct-mapped decoded instruction cache
//                      of 32 x 192 bits (p. 1-2, p. 1-1).
//   HobbitStackCache   64 x 32 x 2-bit stack cache: one read and one
//                      write port per clock (box).
//   HobbitEuS1/S2/S3   execution unit, EU_S1/S2/S3 (Figure 1-1
//                      "EXECUTION UNIT 3-STAGE PIPELINE").
//
// The stage modules follow Flute's CPU_StageN_IFC convention
// (enq/deq/out/set_full plus Server#(Token,Token)); the wiring below is
// the orchestrator, as Flute's CPU.bsv is.  See
// docs/bluespec_architecture.md.
//
// Cycle accounting.  Each stage supplies one issue slot.  `extraCycles`
// in HobbitTypes adds only what Tables 4-32..4-36 print beyond that
// slot: RETURN and POPN +1, ENTER +Q.E, the unimplemented-opcode
// sequence +6+A.  A conditional jump's misprediction is structural: the
// stage that can first see PSW.F decides how many younger slots the
// jump pays for (EU_S3 for a compare-adjacent jump: 2, EU_S2 for the
// two-instruction distance: 1, EU_S1 for three or more: 0), which is
// Table 4-35's 3/2/1.  A folded branch is one record with cyc = 0
// (p. 4-3 note, Table 4-35).  Fetch misses (the PDU/IC fill) and
// operand-forwarding stalls never enter `cyc`: they are not the
// instruction's occupancy, and the p. 4-1 assumptions charge no
// Table 4-37 fetch delay.
//
// The HRI record is the trace port (Flute's g_pc_trace analogue), not
// datapath: EU_S3 pushes records into a trace FIFO and mkHobbitCore
// drains and prints them one at a time.

package HobbitCore;

import Vector::*;
import FIFOF::*;
import GetPut::*;
import ClientServer::*;
import HobbitTypes::*;
import HobbitDecode::*;
import HobbitStackCache::*;
import HobbitMmu::*;
import HobbitEvents::*;

interface HobbitCore;
  // Warm the prefetch buffer from the synchronous memory (one 64-bit
  // line per three clocks) after the image is loaded; the run starts
  // when ready().
  method Action prefetchImage();
  // Fill the prefetch window from an address other than 0 (a Plan 9
  // image's code starts at 0x1020).
  method Action prefetchImageAt(Word addr);
  method Bool prefetchReady();

  method Action start(Word sp, Word msp);
  // Start with an explicit PSW (the MMU path sets V = 1, p. 1-14).
  method Action startPsw(Word sp, Word msp, Word psw);
  // Start at an explicit PC (a Plan 9 image's entry is not 0).
  method Action startAt(Word pc, Word sp, Word msp, Word psw);

  method Bool halted();
  method Bool atLimit();
  method Bool faulted();
  method Word faultPc();
  method Word pc();

  method Word sp();
  method Word msp();
  method Word cacheWord(Word addr);
  method Bool cached(Word addr);

  method Bit#(32) folded();
  method Bit#(32) refills();
  method Bit#(32) instrs();
  method Word minSp();
  method Word maxSp();

  method Bool hriValid();
  method Hri hri();
  // True when no retirement record is being presented and none is
  // waiting; the harnesses use it to stop after the last record.
  method Bool quiescent();

  // ---- MMU / event testbench surface --------------------------------
  method Word psw();
  method Action setPsw(Word psw);
  // CONFIG bit 16 (kernel little-endian data, p. 1-10).
  method Action setConfigKl(Bool kl);
  method Word vb();
  method Action setVb(Word vb);
  method Bit#(3) il();
  method Action setIl(Bit#(3) il);
  // A recorded interrupt (bsv/P9KernTb.bsv): taken at the instruction
  // boundary after record `n` at level `level`.
  //
  // Through two queues, so the testbench schedules against nothing in the
  // core: `armInterrupt` enqueues (n, level); `takenInterrupt` hands back
  // the PC each taken one saved, in order.
  method Action armInterrupt(Bit#(32) n, Bit#(3) level);
  method ActionValue#(Word) takenInterrupt();
  method Word isp();
  method Word shad();
  method Action setIsp(Word isp);
  method Action setShad(Word shad);
  method Action flushPte(Word va);
  method Action flushTlb();
  method Action setStb(Word stb);
  method Bit#(32) mmuHits();
  method Bit#(32) mmuMisses();
  method Bit#(32) mmuWalks();
  method Bit#(32) mmuFaults();
  method Bool eventTaken();
  method Word eventPc();
  method Bit#(4) eventId();
  method Word savedPc();
  method Word savedPsw();
  method Bool eventActive();
  method Word eventMemRead(Word a);
  method Action eventMemWrite(Word a, Word v);

  // Verification probe for the harnesses (like HobbitMem::peek); the
  // machine never reads it.
  method Bit#(64) dbgState();
  // Harness probe: EU_S3's boundary state and the orchestrator's.
  method Bit#(32) dbgBoundary();
  // Every physical word the machine may read combinationally this clock
  // through `tbl` and the event memory: the MMU's walks for the faces'
  // references, the event unit's (HobbitEvents combProbes) and VB, which
  // KCALL reads in EU_S2 (vbProbe).  The machine never reads this; the ULX3S top
  // has those words in its combinational window before it lets the
  // clock edge happen (fpga/README.md, "The core's combinational reads").
  method Vector#(21, Maybe#(Word)) combProbes();
  // VB, which KCALL reads in EU_S2 (`events.memRead(vb)`): the 22nd
  // probe, separate because it is read before EU_S3's commit writes VB
  // and the other probes after the commit's wires.
  method Word vbProbe();
  // This clock's data-memory write's byte enables and whether its read is
  // a merge word (HobbitStackCache memWrBe/memRdMerge): for a bus with
  // byte lanes (HobbitSocCpu).  Memories that store whole words ignore
  // them, the write's word being merge-complete.
  method Bit#(4) memWrBe();
  method Bool memRdMerge();
  // The operand read's speculation and the memory's refusal of it
  // (HobbitStackCache memRdSpec/rdNack).
  method Bool memRdSpec();
  method Action setRdNack(Bool n);
endinterface

// One architectural write.  `addr` is the word address and `mask` the byte
// marks the HRI record carries; `data` is the value placed in its byte
// lanes (other lanes zero, sem/README.md's convention, p. 1-4), and `wdata`
// is the merge-complete word the stack cache stores and the bypass network
// forwards, so a byte write never clobbers the neighbouring bytes.
typedef struct {
  Bool    we;
  Word    addr;
  Word    data;
  Bit#(8) mask;
  Word    wdata;
} WrInfo deriving (Bits);

function WrInfo noWr() =
  WrInfo { we: False, addr: 0, data: 0, mask: 0, wdata: 0 };

// One PSW update: the bits in `mask` are replaced by `value`.  PSW bit 4
// is F, bit 5 C and bit 6 V (Table 1-8, pp. 1-14..1-16).
typedef struct {
  Bool     we;
  Bit#(32) mask;
  Bit#(32) value;
} PswUpdate deriving (Bits);

function PswUpdate noPswUpd() = PswUpdate { we: False, mask: 0, value: 0 };
function PswUpdate pswF(Bool f) =
  PswUpdate { we: True, mask: 32'h10, value: f ? 32'h10 : 32'd0 };
function PswUpdate pswCV(Bool c, Bool v) =
  PswUpdate { we: True, mask: 32'h60,
              value: (c ? 32'h20 : 32'd0) | (v ? 32'h40 : 32'd0) };
function PswUpdate pswCVKeepC(Bool v) =      // C unchanged, V replaced
  PswUpdate { we: True, mask: 32'h40, value: v ? 32'h40 : 32'd0 };
function PswUpdate pswCKeepV(Bool c) =       // V unchanged, C replaced
  PswUpdate { we: True, mask: 32'h20, value: c ? 32'h20 : 32'd0 };

function Bool isCondJumpOp(HobbitOp op) =
  op == OP_JMPTY || op == OP_JMPTN || op == OP_JMPFY || op == OP_JMPFN;

function Bool isCompareOp(HobbitOp op) =
  op == OP_CMPEQ || op == OP_CMPGT || op == OP_CMPHI;

// A `[3]` form writes the accumulator at CSP+4 (p. 1-7, Figure 1-4).
function Bool isAccOp(HobbitOp op);
  case (op)
    OP_ADD3, OP_SUB3, OP_AND3, OP_OR3, OP_XOR3, OP_SHL3, OP_SHR3,
    OP_USHR3, OP_MUL3, OP_DIV3, OP_REM3, OP_LDRAA: return True;
    default: return False;
  endcase
endfunction

// A conditional store: TADD/TSUB store only when the result is untagged
// and did not overflow (pp. 3-44, 3-47).
function Bool isCondStoreOp(HobbitOp op) =
  op == OP_TADD || op == OP_TSUB;

function Bool isSpOp(HobbitOp op) =
  op == OP_ENTER || op == OP_CATCH || op == OP_POPN || op == OP_RETURN;

// The interlocked read-modify-writes (pp. 3-6, 3-8, 3-37).
function Bool isInterlockedOp(HobbitOp op) =
  op == OP_ORI || op == OP_ANDI || op == OP_ADDI;

// The privileged machine's own instructions (mkHobbitCoreSystem).
function Bool isSysOp(HobbitOp op) =
  op == OP_CRET || op == OP_KRET || op == OP_FLUSH || op == OP_FLUSHPTE;

// A three-parcel monadic (Table 1-19, p. 1-24): its operand is one 32-bit
// field, so CONFIG.PX does not apply to it.
function Bool isMonadicOp(HobbitOp op);
  case (op)
    OP_CALL, OP_JMP, OP_JMPTY, OP_JMPTN, OP_JMPFY, OP_JMPFN, OP_RETURN,
    OP_CATCH, OP_ENTER, OP_POPN, OP_KCALL, OP_LDRAA, OP_FLUSHPTE:
      return True;
    default: return False;
  endcase
endfunction

// A dyadic instruction with 16-bit operand fields: three parcels, or
// four with the CPU escape (p. 1-23).
function Bool pxForm(DecodedInstr d) =
  ((d.cpu ? d.plen - 1 : d.plen) == 8'd3) && !isMonadicOp(d.op);

function Bool signedGtW(Word a, Word b);
  Int#(32) x = unpack(a);
  Int#(32) y = unpack(b);
  return x > y;
endfunction

// p. 3-41: SHL3 shifts the destination left, zeros filling, by the low
// five bits of the source.  p. 3-42: SHR3 shifts right and copies the
// sign bit into the vacated bits, so the right shift is arithmetic on the
// two's-complement word.
function Word shlWord(Word v, Word n) = v << n[4:0];
function Word sarWord(Word v, Word n);
  Int#(32) s = unpack(v);
  return pack(s >> n[4:0]);
endfunction
function Word ushrWord(Word v, Word n) = v >> n[4:0];

// Arithmetic results and flags.  pp. 1-29..1-30 (C on unsigned carry or
// borrow, V on signed overflow), p. 3-5 (ADD/ADD3), p. 3-43 (SUB/SUB3).
typedef struct { Word r; Bool c; Bool v; } Arith deriving (Bits);

function Arith addArith(Word a, Word b);
  Bit#(33) raw = zeroExtend(a) + zeroExtend(b);
  Word r = truncate(raw);
  Bool c = raw[32] == 1'b1;
  Bool v = ((a ^ r) & (b ^ r) & 32'h80000000) != 0;
  return Arith { r: r, c: c, v: v };
endfunction

function Arith subArith(Word a, Word b);
  Word r = a - b;
  Bool c = a < b;                                  // borrow
  Bool v = ((a ^ b) & (a ^ r) & 32'h80000000) != 0;
  return Arith { r: r, c: c, v: v };
endfunction

// p. 3-34: C is set when the unsigned product overflows the destination's
// width, V when the signed product does; the stored product is the low
// 32 bits, truncated again by the store.
//
// One 32 x 32 product serves both flags (docs/fpga_area.md): the signed
// 64-bit product of the sign-extended operands is the unsigned one less
// b * 2^32 when a is negative and less a * 2^32 when b is negative,
// modulo 2^64.  mulArithRef is the former two-product form, which
// HobbitArithTb compares this one with.
function Arith mulArith(Word a, Word b, Word sizeBytes);
  Bit#(64) up = zeroExtend(a) * zeroExtend(b);
  Bit#(64) corr = ((a[31] == 1'b1) ? {b, 32'd0} : 64'd0) +
                  ((b[31] == 1'b1) ? {a, 32'd0} : 64'd0);
  Int#(64) sp = unpack(up - corr);
  Bit#(6) bits = truncate(sizeBytes << 3);
  Bit#(64) umax = (64'd1 << bits) - 1;
  Int#(64) smax = unpack((64'd1 << (bits - 1)) - 1);
  Int#(64) smin = -unpack(64'd1 << (bits - 1));
  return Arith { r: truncate(up),
                 c: up > umax,
                 v: (sp > smax) || (sp < smin) };
endfunction

function Arith mulArithRef(Word a, Word b, Word sizeBytes);
  Bit#(64) up = zeroExtend(a) * zeroExtend(b);
  Int#(64) sa = unpack(signExtend(a));
  Int#(64) sb = unpack(signExtend(b));
  Int#(64) sp = sa * sb;
  Bit#(6) bits = truncate(sizeBytes << 3);
  Bit#(64) umax = (64'd1 << bits) - 1;
  Int#(64) smax = unpack((64'd1 << (bits - 1)) - 1);
  Int#(64) smin = -unpack(64'd1 << (bits - 1));
  return Arith { r: truncate(up),
                 c: up > umax,
                 v: (sp > smax) || (sp < smin) };
endfunction

// Two's-complement division truncating toward zero, remainder carrying the
// dividend's sign (p. 3-17, p. 3-39; the rounding rule is a named choice in
// sem/README.md).  `ovf` is the 0x80000000 / -1 case (p. 3-17).
//
// The datapath computes all four divide instructions on one 32-bit
// unsigned restoring divider (divUnit), on the operands' magnitudes for
// the signed forms (docs/fpga_area.md).  divSigned is the former 64-bit
// form, kept as the reference HobbitArithTb compares divUnit with.
function Tuple2#(Word, Word) udivmod32(Word n, Word d);
  Bit#(33) r = 0;
  Word q = n;
  for (Integer i = 0; i < 32; i = i + 1) begin
    r = { r[31:0], q[31] };
    q = q << 1;
    Bit#(34) t = { 1'b0, r } - { 2'b0, d };
    if (t[33] == 1'b0) begin
      r = truncate(t);
      q[0] = 1'b1;
    end
  end
  return tuple2(q, truncate(r));
endfunction

// Quotient and remainder of a / b: signed (truncating toward zero, the
// remainder carrying the dividend's sign) or unsigned.  b == 0 is the
// callers' case (the exception, and a result of 0).
function Tuple2#(Word, Word) divUnit(Bool sgn, Word a, Word b);
  Bool na = sgn && (a[31] == 1'b1);
  Bool nb = sgn && (b[31] == 1'b1);
  match { .uq, .ur } = udivmod32(na ? -a : a, nb ? -b : b);
  return tuple2((na != nb) ? -uq : uq, na ? -ur : ur);
endfunction

function Tuple3#(Word, Word, Bool) divSigned(Word a, Word b);
  Int#(64) x = unpack(signExtend(a));
  Int#(64) y = unpack(signExtend(b));
  Int#(64) ax = (x < 0) ? -x : x;
  Int#(64) ay = (y < 0) ? -y : y;
  Int#(64) q = ax / ay;
  if ((x < 0) != (y < 0)) q = -q;
  Int#(64) r = x - q * y;
  Bool ovf = (a == 32'h80000000) && (b == 32'hFFFFFFFF);
  return tuple3(truncate(pack(q)), truncate(pack(r)), ovf);
endfunction

// --- operand classes -------------------------------------------------

// True for every mode whose instruction field is a stack offset: 0x4-0x7
// and 0x8-0xB (direct and indirect byte/half), 0xD and 0xE (word).
function Bool modeIsSpRel(OpMode m) =
  ((m >= 4'h4) && (m <= 4'hB)) || (m == 4'hD) || (m == 4'hE);

function Bool signedGt(Word a, Word b);
  Int#(32) x = unpack(a);
  Int#(32) y = unpack(b);
  return x > y;
endfunction

// The source operand is read as a value (everything but the flow
// instructions, the stack class, and MOVA/LDRAA, which want an address).
// CALL or JMP whose target is a word in memory or in a stack slot (Table
// 1-23's 0xC and 0xD, p. 1-26).  The word is read as the source operand
// and the new PC is known in EU_S2, exactly as RETURN's is.
function Bool flowIndirect(DecodedInstr d) =
  ((d.op == OP_CALL) || (d.op == OP_JMP)) && (d.src.mode != 4'hF);

function Bool opReadsSrc(HobbitOp op);
  case (op)
    OP_CALL, OP_JMP, OP_JMPTY, OP_JMPTN, OP_JMPFY, OP_JMPFN,
    OP_RETURN, OP_ENTER, OP_CATCH, OP_POPN, OP_NOP,
    OP_MOVA, OP_LDRAA, OP_KCALL,
    OP_CRET, OP_KRET, OP_FLUSH, OP_FLUSHPTE: return False;
    default: return True;
  endcase
endfunction

// The destination-field operand is read as a value (the second operand of
// a compare, or the addend/minuend of a two-operand arithmetic form).
function Bool opReadsDst(HobbitOp op);
  case (op)
    OP_ADD, OP_ADD3, OP_SUB, OP_SUB3, OP_AND, OP_AND3, OP_OR, OP_OR3,
    OP_XOR, OP_XOR3, OP_CMPEQ, OP_CMPGT, OP_CMPHI, OP_SHL, OP_SHL3,
    OP_SHR, OP_SHR3, OP_USHR, OP_USHR3, OP_MUL, OP_MUL3, OP_DIV, OP_DIV3,
    OP_REM, OP_REM3, OP_UDIV, OP_UREM, OP_TADD, OP_TSUB,
    OP_ORI, OP_ANDI, OP_ADDI: return True;
    default: return False;
  endcase
endfunction

// The instruction leaves a value in the destination-field operand's
// location (its own operand, not the accumulator).
function Bool opWritesDst(HobbitOp op);
  case (op)
    OP_MOV, OP_ADD, OP_SUB, OP_AND, OP_OR, OP_XOR, OP_SHL, OP_SHR,
    OP_USHR, OP_MUL, OP_DIV, OP_REM, OP_UDIV, OP_UREM,
    OP_TADD, OP_TSUB, OP_MOVA, OP_DQM2, OP_DQM4,
    OP_ORI, OP_ANDI, OP_ADDI: return True;
    default: return False;
  endcase
endfunction

// The address of the source operand (MOVA/LDRAA), not its value.
function Bool opNeedsSrcEa(HobbitOp op) =
  (op == OP_MOVA) || (op == OP_LDRAA);

// The flag a folded branch must test.  A compare folded together with
// its branch produces the new PSW.F in the same instruction, so the
// branch sees the compare's result, not the previous flag (p. 3-13,
// p. 3-28, p. 4-7).
function Bool flagAfterOp(HobbitOp op, Word srcV, Word dstV, Bool oldFlag);
  case (op)
    OP_CMPEQ: return srcV == dstV;
    OP_CMPGT: return signedGtW(srcV, dstV);
    OP_CMPHI: return srcV > dstV;                // unsigned (p. 3-13)
    default:  return oldFlag;
  endcase
endfunction

// ---------------------------------------------------------------------
// EU_S1: fetch, operand read and the bypass network.
// ---------------------------------------------------------------------
// One resolved operand: value, effective address, containing word, and
// whether the read was captured (stack-cache hit) or faulted.
typedef struct {
  Word val;
  Word ea;
  Word word;
  Bool ok;
  Bool bad;
  Word wa;        // the word address this operand read
} OpRead deriving (Bits);

// One word read by EU_S1: `ok` False means the word is neither in flight,
// nor in the stack cache, nor yet fetched from memory.
typedef struct {
  Word w;
  Bool ok;
} WordRd deriving (Bits);

typedef struct {
  DecInstEntry e;
  Word   pc;
  Word   spBefore;
  Word   mspBefore;
  Word   srcVal;
  Word   srcEa;
  Word   dstVal;
  Word   dstEa;
  Word   dstWord;      // the word the destination operand lives in
  Word   retPc;
  Word   base;
  Word   nextPc;       // predicted next PC
  Bit#(4) sinceCmp;    // issue distance from the last compare
  Word   extra;        // table extras beyond the pipeline slot
  Bool   bad;          // operand resolution found an alignment fault
  // External-memory operands (see "Memory operands" in mkHobbitEuS1).
  Bool   memMiss;      // a needed word is still in memory: not ready
  Word   memMissAddr;  // the first such word's address
  Bool   memMissMerge; // ... wanted only to merge a byte or half store into
  Bool   ptMem;        // the pointed-to word lies outside the stack cache
  Word   ptWord;       // ... and this is it, in-flight writers applied
  Bool   pt2Mem;       // the same for the destination's pointed-to word
  Word   pt2Word;      // when both operands are indirect
  // DQM with a source in memory or the stack is issued as two or four
  // word moves (HobbitCore `curOut`): which word this is, and whether it
  // is the last.
  Bool   dqmMem;
  Bit#(2) dqmIdx;
  Bool   dqmLast;
  // The privileged machine (mkHobbitCoreSystem).  `csp` is the current
  // stack pointer the instruction's stack operands were formed from:
  // SP, or the ISP when PSW bit 9 is 0 (p. 1-12, Table 1-8 p. 1-15).
  // `ispMode` says which.  In the other cores csp = spBefore always.
  Word   csp;
  Bool   ispMode;
  // The slot waits for an empty pipeline before it is handed on: a CPU
  // instruction (it reads control registers and the PSW as committed),
  // CRET, KRET and the flushes.  Each of them also serializes after
  // itself (EU_S3 `serialize`), so it executes alone.
  Bool   drainFirst;
} EuS1Out deriving (Bits);

// One bypass source: the instruction in EU_S2 or EU_S3.
typedef struct {
  Bool valid;
  Bool we;
  Word addr;
  Word data;
  Bool changesSp;
  Word spAfter;
  Bool changesMsp;
  Word mspAfter;
} EuBypass deriving (Bits);

function EuBypass noBypass() =
  EuBypass { valid: False, we: False, addr: 0, data: 0,
             changesSp: False, spAfter: 0,
             changesMsp: False, mspAfter: 0 };

// ---------------------------------------------------------------------
// The control registers of section 1.5 (pp. 1-8..1-20), as one box.
//
// Mode 7 after the CPU escape names them (Table 1-24, p. 1-26):
//   1 MSP  2 ISP  3 SP  4 CONFIG  5 PSW  6 SHAD  7 VB  8 STB  9 FAULT
//   10 ID  11 TIMER1  12 TIMER2
// The box reads every one of them and writes the ones that have no other
// owner.  The PSW is the core's (one rule writes it, through EU_S3's PSW
// update); SP and MSP are the stack cache's (EU_S3's box command); the
// ISP and SHAD live in the event unit, which pushes the frames; STB is the
// MMU's.  EU_S3's commit rule is the only caller of `apply`, so every
// control-register write of the machine has one writer: the retiring
// instruction.
//
// Reserved bits read 0 (Tables 1-2, 1-5, 1-6, 1-9, 1-10, 1-11, 1-14):
// bits 3:0 of ISP, MSP, SP, SHAD and VB, bits 15:0 of CONFIG, bits 10:0
// of STB.  The timers are registers only: nothing counts them yet
// (s9term does not use them before /boot; docs/p9boot.md).
// ---------------------------------------------------------------------
typedef struct {
  Maybe#(Word) isp;
  Maybe#(Word) shad;
  Maybe#(Tuple2#(Bit#(4), Word)) creg;  // CONFIG, VB, STB, FAULT, ID, TIMERn
} CtlUpd deriving (Bits);

function CtlUpd noCtlUpd() =
  CtlUpd { isp: tagged Invalid, shad: tagged Invalid, creg: tagged Invalid };

interface HobbitCtl;
  method Word read(Bit#(4) r, Word psw);
  method Action apply(CtlUpd u);
  method Word isp();
  method Bool px();                     // CONFIG bit 17 (p. 1-23)
  method Word configReg();
endinterface

module mkHobbitCtl#(Reg#(Bool) kl, Reg#(Word) vb, HobbitEvents ev,
                    HobbitMmu mmu, HobbitStackCache sc)(HobbitCtl);
  Reg#(Word) configR <- mkReg(0);       // 0 on reset (p. 1-36)
  Reg#(Word) timer1R <- mkReg(0);
  Reg#(Word) timer2R <- mkReg(0);

  method Word read(Bit#(4) r, Word psw);
    case (r)
      4'd1:  return sc.msp & 32'hFFFFFFF0;
      4'd2:  return ev.isp & 32'hFFFFFFF0;
      4'd3:  return sc.sp & 32'hFFFFFFF0;
      4'd4:  return configR & 32'hFFFF0000;
      4'd5:  return psw;
      // SHAD follows the CSP (p. 1-16): the stack cache keeps it for SP,
      // the event unit for the ISP.
      4'd6:  return ((psw[9] == 1'b1) ? sc.shad : ev.shad) & 32'hFFFFFFF0;
      4'd7:  return vb & 32'hFFFFFFF0;
      4'd8:  return mmu.stb & 32'hFFFFF800;
      // FAULT lives in the event unit, which sets it on a read or write
      // fault (p. 1-39); until 2026-11-24 the core kept a second copy here
      // that only a CPU write changed, so the kernel read 0 after a fault.
      4'd9:  return ev.faultReg;
      // The JTAG ID (Table 1-4, p. 1-11): version 1 (mask two), part 0,
      // manufacturer 0x3B -- the reference model's choice
      // (hobbit_sem.System.ident), adopted.
      4'd10: return 32'h1000003B;
      4'd11: return timer1R;
      4'd12: return timer2R;
      default: return 0;
    endcase
  endmethod

  method Action apply(CtlUpd u);
    if (u.isp matches tagged Valid .v) ev.setIsp(v & 32'hFFFFFFF0);
    if (u.shad matches tagged Valid .v) ev.setShad(v & 32'hFFFFFFF0);
    if (u.creg matches tagged Valid {.r, .v}) begin
      case (r)
        4'd4: begin
          configR <= v & 32'hFFFF0000;
          kl <= (v[16] == 1'b1);
        end
        4'd7: vb <= v & 32'hFFFFFFF0;
        // A write to STB flushes the TLBs and NPSRs (p. 1-18, p. 2-8).
        4'd8: mmu.setStb(v & 32'hFFFFF800);
        4'd9: ev.setFault(v);
        4'd11: timer1R <= v;
        4'd12: timer2R <= v;
        default: noAction;              // ID: a write does nothing (p. 1-11)
      endcase
    end
  endmethod

  method Word isp() = ev.isp;
  method Bool px() = (configR[17] == 1'b1);
  method Word configReg() = configR;
endmodule

interface HobbitEuS1;
  interface Server#(Token, Token) server_reset;
  method Action start(Word pc);
  method Action stop();
  // The orchestrator evaluates the slot once (`out`) and hands the same
  // value here, so the operand reads are one set of stack-cache ports.
  method Action deq(EuS1Out o);
  method EuS1Out out;
  method Bool notEmpty;
  method Word pc();
  method Bit#(8) dbgS1;
  // Drop whatever the slot holds and redirect to `pc` (a squash).
  method Action redirect(Word pc);
endinterface

module mkHobbitEuS1#(HobbitDecodeStore ic, HobbitStackCache sc,
                     MemCycles mcyc,
                     EuBypass byS2, EuBypass byS3, Reg#(Word) psw,
                     Reg#(Bool) kl, Bool squash, Bool drained,
                     Bool s2Taken, Word pcLimit,
                     Reg#(Bool) eventActive,
                     Bool sysOn, HobbitCtl ctl)(HobbitEuS1);
  // structure follows Flute (Bluespec, Inc., Apache-2.0) — see
  // docs/bluespec_architecture.md: one module per EU stage with a
  // registered boundary and one rule for the work the stage does alone.

  Reg#(Bool) active <- mkReg(False);
  // The stage holds at most one slot: `fullR` says the decoded entry for
  // pcR is present and is being handed to EU_S2.  No stall register is
  // needed, because the slot flag *is* the back-pressure (Flute's
  // CPU_Stage1 `full`), and only this stage writes it.
  Reg#(Bool) fullR <- mkReg(False);
  Reg#(Word) pcR <- mkReg(0);
  Reg#(Word) block <- mkReg(0);        // issue interlock, in clocks
  Reg#(Bit#(4)) sinceCmp <- mkReg(0);

  FIFOF#(Token) f_reset_reqs <- mkFIFOF;
  FIFOF#(Token) f_reset_rsps <- mkFIFOF;

  function Word fwdSp();
    return byS2.changesSp ? byS2.spAfter
         : byS3.changesSp ? byS3.spAfter
         : sc.sp();
  endfunction

  function Word fwdMsp();
    return byS2.changesMsp ? byS2.mspAfter
         : byS3.changesMsp ? byS3.mspAfter
         : sc.msp();
  endfunction

  function Bool inCache(Word a, Word spb, Word mspb);
    return (a >= spb) && (a < mspb) && (a < sc.fillWatermark());
  endfunction

  // ---- Memory operands ------------------------------------------------
  // The stack cache holds only [SP, MSP), at most 256 bytes (p. 1-5,
  // p. 1-12).  An operand anywhere else -- an absolute address, a
  // pointer's target, the caller's frame that RETURN's displacement
  // reaches after a large ENTER -- is a word of external memory.  The
  // memory has one registered read port, owned by the stack-cache box, so
  // such a word is fetched before the slot is handed to EU_S2: one
  // request per clock, the word usable in the following clock straight
  // off the port (`sc.memLive`) and kept in one of three latches after
  // that.  Four, because an instruction names at most a source word, a
  // destination word and the word each of them points to.  The wait is the model's A = 1 cycle per word
  // (p. 4-2; a choice, HobbitTypes) and, like the forwarding stalls, is
  // not part of `cyc`: Table 4-38's operand delays are outside the p. 4-1
  // assumptions the HRI count is stated under.
  //
  // A latched word must not go stale while it waits: every architectural
  // write passes through EU_S3, so the latch rule copies EU_S3's write
  // into a latch that holds the same address, and the bypass network
  // covers the writers still in flight when the word is used.
  Reg#(Maybe#(Tuple2#(Word, Word))) lat0 <- mkReg(tagged Invalid);
  Reg#(Maybe#(Tuple2#(Word, Word))) lat1 <- mkReg(tagged Invalid);
  Reg#(Maybe#(Tuple2#(Word, Word))) lat2 <- mkReg(tagged Invalid);
  Reg#(Maybe#(Tuple2#(Word, Word))) lat3 <- mkReg(tagged Invalid);
  Reg#(Bit#(2)) latNext <- mkReg(0);
  Wire#(Bool) latClearW <- mkDWire(False);
  // `start` asks for the clear through a register pair instead of the
  // wire.  With events on, `start` is called from the orchestrator's
  // finishEvent, and a wire from there closed a rule cycle
  // (latchOperand reads EU_S3's bypass, so it precedes move2to3; move2to3
  // reads eventActive, so it precedes finishEvent; a wire from
  // finishEvent would have to precede latchOperand).  bsc broke the
  // cycle by making latchOperand and move2to3 conflict, so the latches
  // missed every clock in which EU_S2 handed to EU_S3: a fetched word
  // could be dropped and a clear could be lost.  A toggle read by the
  // latch rule orders the latch rule first, with no cycle; the clear then
  // lands one clock after `start`, and the slot is empty for that clock
  // (`start` clears fullR and `present` needs a clock to fill it).
  Reg#(Bool) latClrReq <- mkReg(False);
  Reg#(Bool) latClrSeen <- mkReg(False);
  // Set by the handoff of a DQM; see `present`.
  Reg#(Bool) holdR <- mkReg(False);
  // DQM whose source is a word mode (p. 3-18: "moves either two or four
  // contiguous words from the source to the destination").  The EU moves
  // one word per instruction slot, so such a DQM occupies the slot two
  // or four times: this is the word being moved.  Each pass is an
  // ordinary word MOV with both addresses advanced by 4*dqmIdx, so the
  // source's words come through the same paths as any operand (cache,
  // memory, bypass); only the first pass has a retirement record, and it
  // carries the whole instruction's Table 4-34 count; PC moves on, and a
  // folded branch is taken up, with the last.  A double- or quad-aligned
  // source and destination either coincide or do not overlap, so the
  // order of the words cannot matter.
  Reg#(Bit#(2)) dqmIdx <- mkReg(0);

  function Maybe#(Word) latHit(Maybe#(Tuple2#(Word, Word)) l, Word wa);
    if (l matches tagged Valid {.a, .d} &&& (a == wa))
      return tagged Valid d;
    else
      return tagged Invalid;
  endfunction

  function WordRd memWord(Word wa);
    if (sc.memLive() matches tagged Valid .a &&& (a == wa))
      return WordRd { w: sc.memData(), ok: True };
    else if (latHit(lat0, wa) matches tagged Valid .d)
      return WordRd { w: d, ok: True };
    else if (latHit(lat1, wa) matches tagged Valid .d)
      return WordRd { w: d, ok: True };
    else if (latHit(lat2, wa) matches tagged Valid .d)
      return WordRd { w: d, ok: True };
    else if (latHit(lat3, wa) matches tagged Valid .d)
      return WordRd { w: d, ok: True };
    else
      return WordRd { w: 0, ok: False };
  endfunction

  // A word read with the p. 1-1 "operand bypass mechanism": the youngest
  // in-flight writer wins, then the committed stack cache, then memory.
  // `wa` is a word address, so a byte store and a later byte load of the
  // same word meet.
  function WordRd readWord(Word wa, Word spb, Word mspb);
    if (byS2.we && (byS2.addr == wa))
      return WordRd { w: byS2.data, ok: True };
    else if (byS3.we && (byS3.addr == wa))
      return WordRd { w: byS3.data, ok: True };
    else if (inCache(wa, spb, mspb))
      return WordRd { w: sc.read(wa, spb, mspb), ok: True };
    else
      return memWord(wa);
  endfunction

  // The second read port ("64x32x2", Figure 1-1, p. 1-2): the destination
  // operand's word, read in the same cycle as the source's.
  function WordRd readWord2(Word wa, Word spb, Word mspb);
    if (byS2.we && (byS2.addr == wa))
      return WordRd { w: byS2.data, ok: True };
    else if (byS3.we && (byS3.addr == wa))
      return WordRd { w: byS3.data, ok: True };
    else if (inCache(wa, spb, mspb))
      return WordRd { w: sc.read2(wa, spb, mspb), ok: True };
    else
      return memWord(wa);
  endfunction

  // The word a pointer names, when it is not in the stack cache.  A word
  // inside the cache is left to EU_S2's own read (the two stages share
  // the two printed ports and never read in the same clock), so this
  // touches no cache port: in-flight writers, then memory.  The Bool says
  // "EU_S1 supplies the word".
  function Tuple2#(WordRd, Bool) readPt(Word wa, Word spb, Word mspb);
    if (byS2.we && (byS2.addr == wa))
      return tuple2(WordRd { w: byS2.data, ok: True }, True);
    else if (byS3.we && (byS3.addr == wa))
      return tuple2(WordRd { w: byS3.data, ok: True }, True);
    else if (inCache(wa, spb, mspb))
      return tuple2(WordRd { w: 0, ok: True }, False);
    else
      return tuple2(memWord(wa), True);
  endfunction

  // Resolve one Table 1-21 operand (p. 1-25) on the first stack-cache read
  // port: the effective address, the containing word and the
  // width-extended value.  `bad` reports a misaligned half-word or word
  // access (p. 1-4).  One call site, one port: the destination uses
  // operandB() and the second port.
  //
  // A stack-offset-indirect mode (0x8-0xB, 0xE) is resolved in two steps
  // (p. 1-27): "The word at this address is fetched and then used as an
  // address to obtain the data operand."  This function fetches the
  // pointer word from CSP+offset and returns the pointer's value as the
  // operand's effective address; EU_S2 fetches the word it names.  The
  // offset must be word-aligned and a misaligned one is an alignment
  // fault (p. 1-27), reported through `bad`; the pointed-to address is
  // checked against the operand's width in EU_S2 (p. 1-4).
  function OpRead operandA(Operand o, Word cb, Word spb, Word mspb, Bool ctlr);
    if (ctlr) begin
      // A control register after the CPU escape (Table 1-24, p. 1-26).
      return OpRead { val: ctl.read(o.val[3:0], psw), ea: 0, word: 0,
                      ok: True, bad: False, wa: 0 };
    end else if (modeIsImm(o.mode)) begin
      return OpRead { val: o.val, ea: 0, word: 0, ok: True, bad: False,
                      wa: 0 };
    end else if (modeIsIndirect(o.mode)) begin
      Word wa = (cb + o.val) & 32'hFFFFFFFC;
      let r = readWord(wa, spb, mspb);
      return OpRead { val: 0, ea: r.w, word: 0, ok: r.ok,
                      bad: ((o.val & 3) != 0), wa: wa };
    end else begin
      Word a  = modeIsSpRel(o.mode) ? (cb + o.val) : o.val;
      Word sz = modeSize(o.mode);
      Bool bad = ((sz == 4) && ((a & 3) != 0)) ||
                 ((sz == 2) && ((a & 1) != 0));
      let r = readWord(a & 32'hFFFFFFFC, spb, mspb);
      return OpRead { val: extendLoad(r.w, a, sz, modeSigned(o.mode),
                                      dataLittle(psw, kl)),
                      ea: a, word: r.w, ok: r.ok, bad: bad,
                      wa: a & 32'hFFFFFFFC };
    end
  endfunction

  function OpRead operandB(Operand o, Word cb, Word spb, Word mspb, Bool ctlr);
    if (ctlr) begin
      // A control register after the CPU escape (Table 1-24, p. 1-26).
      return OpRead { val: ctl.read(o.val[3:0], psw), ea: 0, word: 0,
                      ok: True, bad: False, wa: 0 };
    end else if (modeIsImm(o.mode)) begin
      return OpRead { val: o.val, ea: 0, word: 0, ok: True, bad: False,
                      wa: 0 };
    end else if (modeIsIndirect(o.mode)) begin
      Word wa = (cb + o.val) & 32'hFFFFFFFC;
      let r = readWord2(wa, spb, mspb);
      return OpRead { val: 0, ea: r.w, word: 0, ok: r.ok,
                      bad: ((o.val & 3) != 0), wa: wa };
    end else begin
      Word a  = modeIsSpRel(o.mode) ? (cb + o.val) : o.val;
      Word sz = modeSize(o.mode);
      Bool bad = ((sz == 4) && ((a & 3) != 0)) ||
                 ((sz == 2) && ((a & 1) != 0));
      let r = readWord2(a & 32'hFFFFFFFC, spb, mspb);
      return OpRead { val: extendLoad(r.w, a, sz, modeSigned(o.mode),
                                      dataLittle(psw, kl)),
                      ea: a, word: r.w, ok: r.ok, bad: bad,
                      wa: a & 32'hFFFFFFFC };
    end
  endfunction


  function EuS1Out mkOut(DecInstEntry e, Word pc, Word spb, Word mspb,
                         Word srcV, Word srcEa, Word dstV, Word dstEa,
                         Word dstW, Word retPc, Bool bad, Bit#(4) dcmp,
                         Bool memMiss, Word memMissAddr,
                         Bool ptMem, Word ptWord,
                         Bool pt2Mem, Word pt2Word);
    let d = e.d;
    Word base = pc + plenBytes(d.plen);
    // A conditional jump issued three or more instructions after its
    // compare resolves in EU_S1: the committed flag is already there,
    // so a misprediction costs no squashed slot (Table 4-35).
    Word npc = e.nextPc;
    if (isCondJumpOp(d.op) && (dcmp >= 2)) begin
      Bool taken = branchTaken(d.op, (psw[4] == 1'b1));
      npc = (taken == predictedTaken(d.op)) ? e.nextPc : e.altNextPc;
    end
    Bool takenGuess = isCondJumpOp(d.op) ? predictedTaken(d.op) : False;
    Word extra = extraCycles(e, spb, mspb, mcyc, takenGuess, dcmp);
    return EuS1Out { e: e, pc: pc, spBefore: spb, mspBefore: mspb,
                     srcVal: srcV, srcEa: srcEa,
                     dstVal: dstV, dstEa: dstEa, dstWord: dstW,
                     retPc: retPc,
                     base: base, nextPc: npc, sinceCmp: dcmp,
                     extra: extra, bad: bad,
                     memMiss: memMiss, memMissAddr: memMissAddr,
                     memMissMerge: False,
                     ptMem: ptMem, ptWord: ptWord,
                     pt2Mem: pt2Mem, pt2Word: pt2Word };
  endfunction

  function EuS1Out curOut();
    let m = ic.lookup(pcR);
    if (!isValid(m))
      return unpack(0);
    else begin
      DecInstEntry e = validValue(m);
      // The privileged instructions exist only in the privileged machine;
      // the other cores take them as before (a lone CPU escape is TR_CPU,
      // KRET/CRET/FLUSHI/FLUSHP/FLUSHPTE the unimplemented sequence).
      if (!sysOn && (e.d.tr == TR_NONE) && (e.d.cpu || isSysOp(e.d.op)))
        e.d.tr = e.d.cpu ? TR_CPU : TR_UNIMP;
      // CONFIG.PX (Table 1-2, p. 1-10; p. 1-23): a 16-bit absolute address
      // takes bits 31:29 from the PC.  Only the dyadic three-parcel forms
      // have 16-bit absolute fields (a monadic's operand is 32 bits).
      if (sysOn && ctl.px && (e.d.tr == TR_NONE) && pxForm(e.d)) begin
        if (modeIsAbs(e.d.src.mode))
          e.d.src.val = e.d.src.val | (e.d.pc & 32'hE0000000);
        if (modeIsAbs(e.d.dst.mode))
          e.d.dst.val = e.d.dst.val | (e.d.pc & 32'hE0000000);
      end
      let d = e.d;
      // CSP = ISP when PSW bit 9 is 0 (p. 1-12): stack operands are
      // formed from the ISP, which "is not associated with the stack
      // cache" -- such an operand is a memory word unless it happens to
      // lie in [SP, MSP), exactly as for any other address.
      Bool ispMode = sysOn && (psw[9] == 1'b0);
      Bool dqmM = isDqmOp(d.op) && (d.src.mode != 4'hF) &&
                  (d.tr == TR_NONE);
      Word dqmOff = dqmM ? (zeroExtend(dqmIdx) << 2) : 0;
      Bool dqmLast = !dqmM || (dqmIdx == ((d.op == OP_DQM4) ? 2'd3 : 2'd1));
      // Only the last word's pass may carry a folded branch.
      if (dqmM && !dqmLast) e.d.fold = False;
      Word spb = fwdSp();
      Word mspb = fwdMsp();
      Word cb = ispMode ? ctl.isp : spb;
      Word srcV = 0;
      Word srcEa = 0;
      Word dstV = 0;
      Word dstEa = 0;
      Word dstW = 0;
      Word retPc = 0;
      Bool bad = False;
      Bool miss = False;
      Word missAddr = 0;
      // The missing word is wanted only as the merge word of a byte or
      // half-word store the instruction does not read (mergeStore): its
      // bytes outside the store's lanes are all it contributes, and a
      // byte-enabled write needs none of them (HobbitStackCache memReq).
      Bool missMerge = False;
      Bool ptMem = False;
      Word ptWord = 0;
      Bool pt2Mem = False;
      Word pt2Word = 0;
      if (d.tr == TR_NONE) begin
        // The first read port carries the source operand.  KCALL's Table
        // 3-2 word32 operand (p. 3-4) is the same operand: mode 0xD means
        // "the stack-offset address itself", so it is presented as an
        // immediate, which needs no read.  RETURN's new PC is its word
        // stack offset read as a word, so it is the source value too
        // (p. 3-40).
        Operand so = d.src;
        if ((d.op == OP_KCALL) && (so.mode == 4'hD))
          so = Operand { mode: 4'hF, val: cb + so.val };
        if (dqmM && !modeIsIndirect(so.mode))
          so.val = so.val + dqmOff;
        // One operandA and one operandB call site per instruction: the
        // two read ports are the printed 64x32x2, and the branchy form
        // (a call per consumer) duplicated the ports bsc counts.  MOVA
        // and LDRAA want the source *address*, not its value (p. 3-31,
        // p. 3-33); every other consumer wants the value.
        // ENTER whose source is absolute or stack-offset-indirect takes
        // its target from memory or the stack cache (p. 3-20, cases 3 and
        // 4): "the target value ... is fetched from memory (or the stack
        // cache)".  The word is read here like any source operand and the
        // instruction then goes down the pipe as the immediate form
        // (case 2), which has the same semantics once the value is known:
        // flush the cache unconditionally, MSP = SP = target (p. 3-19).
        // CATCH's operand is the same word32 (p. 3-10), and the same holds:
        // once read, the target is the immediate form's.
        Bool word32Mem = ((d.op == OP_ENTER) || (d.op == OP_CATCH)) &&
                         ((so.mode == 4'hC) || (so.mode == 4'hE));
        if (opReadsSrc(d.op) || (d.op == OP_KCALL) ||
            (d.op == OP_RETURN) || flowIndirect(d) ||
            opNeedsSrcEa(d.op) || word32Mem) begin
          let r = operandA(so, cb, spb, mspb, d.cpu && (so.mode == 4'h7));
          srcEa = (dqmM && modeIsIndirect(so.mode)) ? r.ea + dqmOff : r.ea;
          bad = bad || r.bad;
          if (word32Mem)
            e.d.src = Operand { mode: 4'hF,
                                val: (so.mode == 4'hE) ? r.ea : r.val };
          if (!opNeedsSrcEa(d.op)) begin
            srcV = r.val;
            if ((d.op == OP_RETURN) || flowIndirect(d)) retPc = r.val;
          end
          // MOVA/LDRAA want only the address; a pointer word is always
          // needed, because it *is* the address.
          Bool need = !opNeedsSrcEa(d.op) || modeIsIndirect(so.mode);
          if (need && !r.ok) begin
            miss = True; missAddr = r.wa;
          end
        end
        if (opReadsDst(d.op) || opWritesDst(d.op)) begin
          Operand dop = d.dst;
          if (dqmM && !modeIsIndirect(dop.mode))
            dop.val = dop.val + dqmOff;
          let r = operandB(dop, cb, spb, mspb, d.cpu && (dop.mode == 4'h7));
          dstEa = (dqmM && modeIsIndirect(dop.mode)) ? r.ea + dqmOff : r.ea;
          dstW = r.word; bad = bad || r.bad;
          if (opReadsDst(d.op)) dstV = r.val;
          // A word-wide store needs no old word (mergeStore ignores it at
          // width 4), so a write-only word destination is not fetched.
          Bool need = opReadsDst(d.op) || modeIsIndirect(d.dst.mode) ||
                      (!modeIsImm(d.dst.mode) && (modeSize(d.dst.mode) < 4));
          if (need && !r.ok && !miss) begin
            miss = True; missAddr = r.wa;
            missMerge = !opReadsDst(d.op) && !modeIsIndirect(d.dst.mode);
          end
        end
        // The pointed-to word, exactly when EU_S2 will want one (the same
        // two predicates as its `step`), once the pointer itself is here.
        Bool srcInd = modeIsIndirect(d.src.mode) &&
                      (opReadsSrc(d.op) || (d.op == OP_KCALL) ||
                       (d.op == OP_RETURN));
        Bool dstInd = modeIsIndirect(d.dst.mode) &&
                      (opReadsDst(d.op) ||
                       (opWritesDst(d.op) && (modeSize(d.dst.mode) < 4)));
        if ((srcInd || dstInd) && !miss) begin
          Word pa = (srcInd ? srcEa : dstEa) & 32'hFFFFFFFC;
          match { .r, .fromS1 } = readPt(pa, spb, mspb);
          ptMem = fromS1; ptWord = r.w;
          if (!r.ok) begin
            miss = True; missAddr = pa;
            missMerge = !srcInd && !opReadsDst(d.op);
          end
        end
        // Both operands indirect: the destination's pointed-to word as
        // well (a compare of two bytes through two pointers is 1e's
        // strcmp and its format scanner).
        if (srcInd && dstInd && !miss) begin
          Word pa2 = dstEa & 32'hFFFFFFFC;
          match { .r2, .fromS1b } = readPt(pa2, spb, mspb);
          pt2Mem = fromS1b; pt2Word = r2.w;
          if (!r2.ok) begin
            miss = True; missAddr = pa2;
            missMerge = !opReadsDst(d.op);
          end
        end
        // CRET (p. 3-15) and KRET (p. 3-30) read the interrupt stack's
        // frame: SP at ISP+0 and MSP at ISP+4 (CRET only), PC at ISP+8,
        // PSW at ISP+12 -- whatever the CSP is.  The four words come
        // through the same paths as operands: the two read ports for the
        // first pair and the two pointed-to slots (EU_S2's
        // readPointed/readPointed2) for the second.
        if ((d.op == OP_CRET) || (d.op == OP_KRET)) begin
          Word ib = ctl.isp & 32'hFFFFFFF0;
          let r0 = readWord(ib, spb, mspb);
          let r1 = readWord2(ib + 4, spb, mspb);
          srcV = r0.w; dstV = r1.w;
          srcEa = ib + 8; dstEa = ib + 12;
          if ((d.op == OP_CRET) && !r0.ok) begin
            miss = True; missAddr = ib;
          end else if ((d.op == OP_CRET) && !r1.ok) begin
            miss = True; missAddr = ib + 4;
          end
          if (!miss) begin
            match { .r, .f } = readPt(ib + 8, spb, mspb);
            ptMem = f; ptWord = r.w;
            if (!r.ok) begin miss = True; missAddr = ib + 8; end
          end
          if (!miss) begin
            match { .r, .f } = readPt(ib + 12, spb, mspb);
            pt2Mem = f; pt2Word = r.w;
            if (!r.ok) begin miss = True; missAddr = ib + 12; end
          end
        end
      end
      EuS1Out o = mkOut(e, pcR, spb, mspb, srcV, srcEa, dstV, dstEa, dstW,
                        retPc, bad, sinceCmp, miss, missAddr, ptMem, ptWord,
                        pt2Mem, pt2Word);
      o.memMissMerge = miss && missMerge;
      o.dqmMem  = dqmM;
      o.dqmIdx  = dqmM ? dqmIdx : 0;
      o.dqmLast = dqmLast;
      o.csp     = cb;
      o.ispMode = ispMode;
      // The interlocked forms too, in every core: "clearing the pipeline
      // before an interlocked instruction enters the first pipeline stage.
      // No other instruction is allowed into the pipeline until the
      // executing interlocked instruction completes" (pp. 3-6, 3-8, 3-37
      // Notes); `holdR` is the second half.
      o.drainFirst = (d.tr == TR_NONE) &&
                     ((sysOn && (d.cpu || isSysOp(d.op))) ||
                      isInterlockedOp(d.op));
      // With CSP = ISP the stack class moves the ISP and nothing else:
      // no flush, so no ENTER flush cycles (Table 4-36's E is 0).
      if (ispMode && isSpOp(d.op))
        o.extra = ((d.op == OP_RETURN) || (d.op == OP_POPN)) ? 1 : 0;
      if (dqmM) begin
        // Table 4-34 (p. 4-4), by where the two blocks live.  Double
        // word: SC to SC 4, SC/M to M/SC 2 + D, M to M 2.D -- all 4 with
        // D = 2.  Quad word: SC to SC 8, SC/M to M/SC 4 + D = 6, M to M
        // the printed 8.S = 8 (S read as A, sem/hobbit_sem.py S_CYC).
        Bool srcSc = inCache(srcEa - dqmOff, spb, mspb);
        Bool dstSc = inCache(dstEa - dqmOff, spb, mspb);
        o.extra = (d.op == OP_DQM4) ? ((srcSc != dstSc) ? 5 : 7) : 3;
      end
      return o;
    end
  endfunction

  // The one rule this stage runs on its own: own the slot.  With the
  // slot empty it first waits out the issue interlock, then presents the
  // decoded entry for pcR -- starting the single fetch that will install
  // it when the decoded store has no entry yet.  The guard is one
  // predicate and the body writes only block/fullR (plus the store's
  // fetch request), so EU_S1's handoff (`deq`, `redirect`) and this rule
  // are always mutually exclusive: deq/redirect need a populated slot or
  // a squash, and neither is true here.
  // After a DQM nothing is presented until the pipeline behind it is
  // empty (`drained`): its words after the first leave from EU_S3's
  // commit and are not in the bypass network, so an instruction issued
  // behind it could read a word the DQM has not written yet.
  //
  // After a CATCH likewise, and `drained` includes the stack-cache box
  // being idle: the refill a CATCH starts takes a clock per word, and the
  // box keeps one refill's state.  A second CATCH restarted it and an
  // ENTER's flush replaced it, and in both cases the words the first
  // refill had not reached were then treated as loaded.  With every run
  // starting on a full cache a refill was rare and short; a 1e process
  // starts with the cache empty and empties it at every kernel entry, and
  // za hit this 29,664 instructions in.  The wait is not in `cyc`: Table
  // 4-36 prices CATCH at a flat 1 and the model keeps that.
  rule present (active && !squash && !fullR && !eventActive &&
                (pcR < pcLimit));
    if (holdR) begin
      if (drained) holdR <= False;
    end else if (block != 0)
      block <= block - 1;
    else if (isValid(ic.lookup(pcR)))
      fullR <= True;
    else begin
      ic.fill(pcR);
    end
  endrule

  // Ask memory for the first word the slot still lacks.  The box must
  // be idle: a flush or a parked write means memory does not yet hold
  // every committed word, and a refill owns the read port.
  // `!s2Taken`: no fetch while an instruction sits unexecuted in EU_S2's
  // input slot.  Its result is not in the bypass network yet, so an
  // address formed from a word it is about to write -- a pointer just
  // being computed -- would be the *old* value, and the fetch would go
  // to an address the program never uses (1e's `za`: a table scan read
  // memory at `4*i` before the `ADD` of the table's base had executed;
  // 2,399 such reads in 125,572 instructions).  The right word was
  // always fetched afterwards, so nothing was wrong with the values; but
  // it is a read the part would not make, and a device register would
  // see it.  The instruction cannot be handed to EU_S2 before that slot
  // empties anyway.
  rule fetchOperand (active && !squash && fullR && !eventActive &&
                     !s2Taken && curOut().memMiss && sc.memIdle());
    sc.memReq(curOut().memMissAddr, curOut().memMissMerge, !drained);
  endrule

  // The single writer of the latches.  The word on the memory port is
  // kept (round robin), EU_S3's write refreshes any latch holding its
  // address, and a handoff, a squash or a start empties all three.
  rule latchOperand;
    function Maybe#(Tuple2#(Word, Word)) snoop(Maybe#(Tuple2#(Word, Word)) l);
      if (l matches tagged Valid {.a, .d} &&& (byS3.we && (byS3.addr == a)))
        return tagged Valid tuple2(a, byS3.data);
      else
        return l;
    endfunction
    latClrSeen <= latClrReq;
    if (latClearW || (latClrReq != latClrSeen)) begin
      lat0 <= tagged Invalid;
      lat1 <= tagged Invalid;
      lat2 <= tagged Invalid;
      lat3 <= tagged Invalid;
      latNext <= 0;
    end else begin
      let n0 = snoop(lat0);
      let n1 = snoop(lat1);
      let n2 = snoop(lat2);
      let n3 = snoop(lat3);
      if (sc.memLive() matches tagged Valid .a) begin
        Word d = (byS3.we && (byS3.addr == a)) ? byS3.data : sc.memData();
        let v = tagged Valid tuple2(a, d);
        case (latNext)
          0: n0 = v;
          1: n1 = v;
          2: n2 = v;
          default: n3 = v;
        endcase
        latNext <= latNext + 1;
      end
      lat0 <= n0;
      lat1 <= n1;
      lat2 <= n2;
      lat3 <= n3;
    end
  endrule

  rule rl_reset;
    f_reset_reqs.deq;
    active   <= False;
    fullR    <= False;
    block    <= 0;
    sinceCmp <= 0;
    latClearW <= True;
    f_reset_rsps.enq(?);
  endrule

  method Action start(Word pc);
    pcR      <= pc;
    active   <= True;
    fullR    <= False;
    block    <= 0;
    sinceCmp <= 0;
    holdR    <= False;
    dqmIdx   <= 0;
    latClrReq <= !latClrReq;
  endmethod

  method Action stop();
    active <= False;
  endmethod

  // The slot is presentable once every memory word it needs is here.
  method Bool notEmpty() = fullR && !curOut().memMiss &&
                          (!curOut().drainFirst || drained);

  // Probe layout, bits 41..34 of dbgState: {active, full, blocked,
  // squash, lookupValid, 3'b0}.  `full` replaces the retired `stall`
  // register: the slot flag is the stage's only back-pressure state.
  method Bit#(8) dbgS1 = { pack(active), pack(fullR), pack(block != 0),
                           pack(squash), pack(isValid(ic.lookup(pcR))), 3'b0 };

  method EuS1Out out() = curOut();

  method Word pc() = pcR;

  // The state advance the orchestrator performs when EU_S2 takes the
  // slot.  It writes every register `present` can write, so the two must
  // never need to fire together -- and they cannot: `present` requires
  // an empty slot and this method is called on a full one.
  method Action deq(EuS1Out o);
    // A DQM from memory stays at its PC until its last word has gone.
    Bool stay = o.dqmMem && !o.dqmLast;
    fullR <= False;
    if (!stay) begin
      pcR      <= o.nextPc;
      block    <= o.extra;
      sinceCmp <= isCompareOp(o.e.d.op) ? 0
                : ((sinceCmp == 15) ? 15 : sinceCmp + 1);
      holdR    <= isDqmOp(o.e.d.op) || (o.e.d.op == OP_CATCH) ||
                  isInterlockedOp(o.e.d.op);
    end
    dqmIdx   <= stay ? dqmIdx + 1 : 0;
    latClearW <= True;
  endmethod

  // A squash does not go through `deq`: it must redirect even when the
  // slot is empty.  The orchestrator calls this from a rule guarded by
  // `squash`, which is exactly the complement of `present`'s guard.
  method Action redirect(Word target);
    fullR    <= False;
    pcR      <= target;
    block    <= 0;
    sinceCmp <= 0;
    holdR    <= False;
    dqmIdx   <= 0;
    latClearW <= True;
  endmethod

  interface Server server_reset;
    interface Put request  = toPut(f_reset_reqs);
    interface Get response = toGet(f_reset_rsps);
  endinterface
endmodule

// ---------------------------------------------------------------------
// EU_S2: execute.  The ALU, PSW.F, the stack pointers and the branch
// resolution live here.
// ---------------------------------------------------------------------
typedef struct {
  DecInstEntry e;
  Word   pc;
  Word   spBefore;
  Word   mspBefore;
  Word   spAfter;
  Word   mspAfter;
  Word   base;
  WrInfo wr;
  Word   nextPc;
  Bool   squash;       // misprediction resolved in this stage
  Word   redirectPc;
  Word   occ;
  Bit#(4) sinceCmp;
  Bool   flagValid;    // the instruction writes PSW.F itself
  Bool   flagValue;
  PswUpdate pswUpd;    // the instruction's C/V/F write (Table 1-8)
  Bool   foldMis;      // compare-host folded branch mispredicted
  Word   foldRedirect;
  ScCmd  cmd;
  Bool   fatal;        // alignment fault or divide by zero: no record
  Bool   divZero;      // the fatal case is the p. 3-17 zero divide
  Bool   kcall;        // KCALL: frame tail and ISP at commit
  Bit#(3) dqm;         // DQM: words in the block (0, 2 or 4)
  Bool   silent;       // a later word of a DQM from memory: no record
  Word   kframe;       // KCALL's frame base (ISP before)
  // The privileged machine (mkHobbitCoreSystem):
  Bool   serialize;    // squash every younger instruction at commit and
  Word   serPc;        // ... refetch from here (the instruction's next PC)
  CtlUpd ctlUpd;       // control-register writes, applied at commit
  Bool   cretCatch;    // CRET's CATCH portion: refill [SP, catchTo)
  Word   catchTo;      // ... under the restored PSW (p. 3-15)
  Bool   flushTlb;     // FLUSHPTE (p. 3-27): every TLB/NPSR entry
  Bool   flushIc;      // FLUSHI/FLUSHP (pp. 3-24, 3-25)
  // A second architectural write that is not the record's: the
  // interlocked forms' accumulator (pp. 3-6, 3-8, 3-37).
  Bool   xw;
  Word   xwAddr;
  Word   xwData;
} EuS2Out deriving (Bits);

interface HobbitEuS2;
  interface Server#(Token, Token) server_reset;
  method Action start();
  method Action enq(EuS1Out d);
  method Bool canAccept();
  method EuS2Out out;
  method Action deq;
  method Bool notEmpty;
  // Harness probe: the stage holds a record in either slot.
  method Bool occupied();
  method EuBypass bypass;
  method Bool squash;
  method Word redirectPc;
  method Action flush();
endinterface

module mkHobbitEuS2#(Reg#(Word) psw, Reg#(Bool) kl, Reg#(Word) vb,
                     HobbitStackCache sc, EuBypass byS3,
                     HobbitEvents events, Bool sysOn)(HobbitEuS2);
  // structure follows Flute (Bluespec, Inc., Apache-2.0) — see
  // docs/bluespec_architecture.md.
  //
  // The stage holds one input slot and one output slot as plain
  // full/data register pairs, not FIFOFs.  A FIFOF's `first` is a method
  // *guarded by notEmpty*, and Bluespec conjoins a guarded method's
  // condition into every rule that may call it -- including the rules of
  // a consumer that only wants `squash`/`bypass` when the slot happens to
  // be occupied.  That would make EU_S1's fetch depend on this stage's
  // occupancy (the boot deadlock).  A register whose validity is a
  // separate flag has no implicit condition, so the consumers' own guards
  // are the whole story.
  Reg#(Bool) inFull  <- mkReg(False);
  Reg#(EuS1Out) inD  <- mkRegU;
  Reg#(Bool) outFull <- mkReg(False);
  Reg#(EuS2Out) outD <- mkRegU;
  Wire#(Bool) flushW <- mkDWire(False);

  FIFOF#(Token) f_reset_reqs <- mkFIFOF;
  FIFOF#(Token) f_reset_rsps <- mkFIFOF;

  function Word opAddr2(Operand o, Word spb) =
    modeIsSpRel(o.mode) ? spb + o.val : o.val;

  // The width of the destination operand's access (p. 1-28); an immediate
  // destination has no width of its own.
  function Word dstBytes(Operand o) = modeIsImm(o.mode) ? 4 : modeSize(o.mode);

  // The pointed-to operand's address must meet the width's alignment
  // rule: a word is word-aligned, a half-word half-word-aligned, a byte
  // has no constraint (p. 1-4, p. 1-27).
  function Bool widthBad(Word a, Word sz);
    return ((sz == 4) && ((a & 3) != 0)) || ((sz == 2) && ((a & 1) != 0));
  endfunction

  // The word a stack-offset-indirect pointer names (p. 1-27).  EU_S3 is
  // the only older instruction still in flight, so its write bypasses the
  // array exactly as it does for EU_S1's operand read; otherwise the
  // committed stack cache supplies the word.  The two stages never read
  // in the same clock (`deliver` needs an empty input slot, `step` a full
  // one), so this second-stage read shares the box's two printed ports
  // (Figure 1-1, p. 1-2) without a third.
  //
  // A pointer usually names a word *outside* the stack cache (data, a
  // buffer, a frame above MSP).  EU_S1 fetched that word from memory
  // with the writers then in flight applied (`ptMem`/`ptWord`); the only
  // one of those still in flight now is in EU_S3, and it bypasses here.
  function Word readPointed(EuS1Out i, Word ea, Word spb, Word mspb);
    Word wa = ea & 32'hFFFFFFFC;
    if (byS3.valid && byS3.we && (byS3.addr == wa)) return byS3.data;
    else if (i.ptMem) return i.ptWord;
    else return sc.read(wa, spb, mspb);
  endfunction

  // The destination's pointed-to word when both operands are indirect:
  // the second printed port.
  function Word readPointed2(EuS1Out i, Word ea, Word spb, Word mspb);
    Word wa = ea & 32'hFFFFFFFC;
    if (byS3.valid && byS3.we && (byS3.addr == wa)) return byS3.data;
    else if (i.pt2Mem) return i.pt2Word;
    else return sc.read2(wa, spb, mspb);
  endfunction

  // Two's-complement division truncating toward zero, remainder carrying
  // the dividend's sign (pp. 3-17, 3-39).  A zero divisor is the
  // divide-by-zero exception and never reaches here (the caller sets
  // `fatal`); the guard keeps the division out of the datapath.
  function Word divQ(Word a, Word b);
    if (b == 0) begin
      return 0;
    end else begin
      match { .q, .r, .o } = divSigned(a, b);
      return q;
    end
  endfunction
  function Word divR(Word a, Word b);
    if (b == 0) begin
      return 0;
    end else begin
      match { .q, .r, .o } = divSigned(a, b);
      return r;
    end
  endfunction

  // The value an instruction leaves in its destination location.
  function Word aluWord(HobbitOp op, Word src, Word dst);
    case (op)
      OP_MOV, OP_DQM2, OP_DQM4:  return src;
      OP_ADD, OP_ADD3, OP_TADD: return dst + src;
      OP_SUB, OP_SUB3, OP_TSUB: return dst - src;
      OP_AND, OP_AND3: return dst & src;
      OP_OR,  OP_OR3:  return dst | src;
      OP_XOR, OP_XOR3: return dst ^ src;
      OP_SHL, OP_SHL3: return shlWord(dst, src);
      OP_SHR, OP_SHR3: return sarWord(dst, src);
      OP_USHR, OP_USHR3: return ushrWord(dst, src);
      OP_MUL, OP_MUL3: return dst * src;
      OP_DIV, OP_DIV3: return divQ(dst, src);
      OP_REM, OP_REM3: return divR(dst, src);
      OP_UDIV: return (src == 0) ? 0 : (dst / src);
      OP_UREM: return (src == 0) ? 0 : (dst % src);
      default: return 0;
    endcase
  endfunction

  function WrInfo accWr(Word spb, Word res) =
    WrInfo { we: True, addr: (spb + 4) & 32'hFFFFFFFC, data: res,
             mask: 8'h0F, wdata: res };

  // A store to the destination operand: the record's data is the value in
  // its byte lanes with the byte marks of the access, and the word the
  // stack cache keeps merges those lanes into the containing word.
  function WrInfo memWr(EuS1Out i, Word old, Word res);
    Word sz = dstBytes(i.e.d.dst);
    Word a  = i.dstEa;
    Bool le = dataLittle(psw, kl);
    return WrInfo { we: True, addr: a & 32'hFFFFFFFC,
                    data: laneData(res, a, sz, le),
                    mask: storeMask(a, sz, le),
                    wdata: mergeStore(old, res, a, sz, le) };
  endfunction

  function BoxOp boxOpOf(HobbitOp op);
    case (op)
      OP_ENTER:  return BX_ENTER;
      OP_CATCH:  return BX_CATCH;
      OP_POPN:   return BX_POPN;
      OP_RETURN: return BX_RETURN;
      default:   return BX_NONE;
    endcase
  endfunction

  function Word stackTarget(EuS1Out i);
    let d = i.e.d;
    case (d.op)
      OP_ENTER:  return enterTarget(d, i.spBefore);
      OP_CATCH:  return modeIsStack(d.src.mode) ? i.spBefore + d.src.val
                                                : d.src.val;
      OP_POPN:   return d.src.val;
      OP_RETURN: return d.src.val;
      default:   return 0;
    endcase
  endfunction

  // The one rule this stage runs on its own: take the input slot, do the
  // work, fill the output slot.  `enq` needs an empty input slot and this
  // rule needs a full one; this rule needs an empty output slot and `deq`
  // needs a full one -- so no two of them ever write the same register in
  // the same clock.
  rule step (flushW || (inFull && !outFull));
   if (flushW) begin
    inFull  <= False;
    outFull <= False;
   end else begin
    let i = inD;
    let e = i.e;
    let d = e.d;
    Bool trap = (d.tr != TR_NONE);

    // ---- indirect operands: the word the pointer names (p. 1-27) ------
    // EU_S1 read the pointer word and left its value in srcEa/dstEa; the
    // one word that pointer names is fetched here, one stage later, on
    // one printed read port.  The instruction's own before-SP is the
    // address base, so an older POPN/RETURN in flight cannot move this
    // operand.  `bad` is the offset's alignment fault from EU_S1
    // (p. 1-27) plus the pointed-to address's width rule (p. 1-4); either
    // one is the p. 1-26 exception 0x4 and stops the run without a
    // retirement record, as the sem's Refusal does.
    //
    // Each operand may need a pointed-to word.  This stage reads them
    // on the cache's two printed ports (64x32x2, Figure 1-1, p. 1-2):
    // the pointer words were EU_S1's reads, a clock earlier.
    Word src = i.srcVal;
    Word dst = i.dstVal;
    Word dstW = i.dstWord;
    Bool bad = i.bad;
    // CRET/KRET's PC and PSW words (EU_S1 left their addresses in
    // srcEa/dstEa and fetched them like pointed-to words).
    Bool sysFrame = (d.op == OP_CRET) || (d.op == OP_KRET);
    Word framePc = 0;
    Word framePsw = 0;
    if (!trap) begin
      Bool srcInd = modeIsIndirect(d.src.mode) &&
                    (opReadsSrc(d.op) || (d.op == OP_KCALL) ||
                     (d.op == OP_RETURN));
      // A word store needs no old word for a merge (mergeStore ignores
      // it at width 4); a byte or half store does, and so does any
      // destination the instruction reads as a value.
      Bool dstInd = modeIsIndirect(d.dst.mode) &&
                    (opReadsDst(d.op) ||
                     (opWritesDst(d.op) && (dstBytes(d.dst) < 4)));
      if (srcInd || dstInd || sysFrame) begin
        Word ea = (srcInd || sysFrame) ? i.srcEa : i.dstEa;
        let w = readPointed(i, ea, i.spBefore, i.mspBefore);
        let w2 = readPointed2(i, i.dstEa, i.spBefore, i.mspBefore);
        framePc = w;
        framePsw = w2;
        if (srcInd) begin
          src = extendLoad(w, i.srcEa, modeSize(d.src.mode),
                           modeSigned(d.src.mode), dataLittle(psw, kl));
          bad = bad || widthBad(i.srcEa, modeSize(d.src.mode));
        end
        if (dstInd) begin
          Word wd = srcInd ? w2 : w;
          dstW = wd;
          dst = extendLoad(wd, i.dstEa, dstBytes(d.dst),
                           modeSigned(d.dst.mode), dataLittle(psw, kl));
          bad = bad || widthBad(i.dstEa, dstBytes(d.dst));
        end
      end
    end

    Bool cmp = isCompareOp(d.op) && !trap;
    Bool flagNew = flagAfterOp(d.op, src, dst, (psw[4] == 1'b1));
    SpMsp after = (trap || i.ispMode)
                    ? SpMsp { sp: i.spBefore, msp: i.mspBefore }
                    : archAfterSpMsp(d, i.spBefore, i.mspBefore);

    // ---- the result and the PSW write (pp. 3-5..3-51) ----------------
    Word sz  = dstBytes(d.dst);
    Word res = 0;
    PswUpdate pu = noPswUpd();
    Bool store = True;
    Bool fatal = bad;
    Bool divZero = False;
    Bool hasTag = False;
    Bool ilToAcc = !modeIsImm(d.dst.mode) && (sz == 4) &&
                   (i.dstEa == i.csp + 4);
    // The one divider of the four divide instructions (divUnit).
    Bool divSgn = (d.op == OP_DIV) || (d.op == OP_DIV3) ||
                  (d.op == OP_REM) || (d.op == OP_REM3);
    match { .divQuo, .divRem } = divUnit(divSgn, dst, src);

    case (d.op)
      OP_MOV: res = src;
      // DQM with a constant: this is the first of its two or four words,
      // the one the record carries; the rest leave from EU_S3's commit.
      // The block must be double- or quad-aligned (p. 3-18 Notes).
      OP_DQM2, OP_DQM4: begin
        res = src;
        Word off = i.dqmMem ? (zeroExtend(i.dqmIdx) << 2) : 0;
        if (((i.dstEa - off) & (dqmBytes(d.op) - 1)) != 0) fatal = True;
        if (i.dqmMem && (((i.srcEa - off) & (dqmBytes(d.op) - 1)) != 0))
          fatal = True;
      end
      OP_ADD, OP_ADD3: begin
        let a = addArith(dst, src); res = a.r; pu = pswCV(a.c, a.v);
      end
      OP_SUB, OP_SUB3: begin
        let a = subArith(dst, src); res = a.r; pu = pswCV(a.c, a.v);
      end
      OP_AND, OP_AND3: res = dst & src;
      OP_OR,  OP_OR3:  res = dst | src;
      OP_XOR, OP_XOR3: res = dst ^ src;
      OP_CMPEQ: begin pu = pswF(src == dst); store = False; end
      OP_CMPGT: begin pu = pswF(signedGt(src, dst)); store = False; end
      OP_CMPHI: begin pu = pswF(src > dst); store = False; end
      OP_SHL, OP_SHL3:   res = shlWord(dst, src);
      OP_SHR, OP_SHR3:   res = sarWord(dst, src);
      OP_USHR, OP_USHR3: res = ushrWord(dst, src);
      OP_MUL, OP_MUL3: begin
        let a = mulArith(dst, src, (d.op == OP_MUL3) ? 4 : sz);
        res = a.r; pu = pswCV(a.c, a.v);
      end
      OP_DIV, OP_DIV3: begin
        if (src == 0) begin fatal = True; divZero = True; end
        res = (src == 0) ? 0 : divQuo;
        pu = pswCVKeepC((dst == 32'h80000000) && (src == 32'hFFFFFFFF));
      end
      OP_REM, OP_REM3: begin
        if (src == 0) begin fatal = True; divZero = True; end
        res = (src == 0) ? 0 : divRem;
        pu = pswCVKeepC(False);              // V always cleared, C unchanged
      end
      OP_UDIV: begin
        if (src == 0) begin fatal = True; divZero = True; end
        res = (src == 0) ? 0 : divQuo;
        pu = pswCKeepV(False);               // C cleared, V unchanged
      end
      OP_UREM: begin
        if (src == 0) begin fatal = True; divZero = True; end
        res = (src == 0) ? 0 : divRem;
        pu = pswCKeepV(False);
      end
      OP_TADD, OP_TSUB: begin
        hasTag = ((src | dst) & 3) != 0;
        let a = (d.op == OP_TADD) ? addArith(dst, src) : subArith(dst, src);
        res = a.r;
        if (hasTag) begin
          pu = pswF(True);                   // tagged: F=1, no store, C/V kept
          store = False;
        end else begin
          pu = pswF(a.v);
          store = !a.v;                      // store only when F = 0
        end
      end
      // The interlocked forms (pp. 3-6, 3-8, 3-37): the destination is
      // read and written as one operation, and its previous value goes
      // to the accumulator; C and V are not affected.  The record carries
      // the destination's write; the accumulator's leaves from EU_S3 the
      // next clock (`xw`), and EU_S1 issues nothing until it has.  "If
      // R4 is the destination, after the interlocked instruction
      // completes, R4 is the previous value of R4; hence, no operation"
      // (p. 3-6 note): the one write is then the old value.
      OP_ORI, OP_ANDI, OP_ADDI: begin
        Word r = (d.op == OP_ORI) ? (dst | src)
               : (d.op == OP_ANDI) ? (dst & src) : (dst + src);
        res = ilToAcc ? dst : r;
      end
      OP_MOVA:  res = i.srcEa;
      OP_LDRAA: res = i.srcEa;               // Acc = &dst (p. 3-31)
      OP_KCALL: begin
        res = src;
        // PSW = PSW & 0xFFFF0000 (p. 3-29): kernel level, ISP as CSP,
        // tracing and interrupts inhibited.
        pu = PswUpdate { we: True, mask: 32'h0000FFFF, value: 0 };
      end
      default: store = False;
    endcase

    // ---- the privileged machine (mkHobbitCoreSystem) ------------------
    // PSW.E (Table 1-8, p. 1-15; pp. 3-19..3-21): ENTER sets it when the
    // stack-offset form flushed nothing ("MSP - target <= SCSIZE") and
    // clears it otherwise; with CSP = ISP it is set.
    if ((d.op == OP_ENTER) && !trap) begin
      Bool eSet = True;
      if (!i.ispMode) begin
        Word t = enterTarget(d, i.spBefore);
        eSet = modeIsStack(d.src.mode) && !((i.mspBefore - t) > 256);
      end
      pu = PswUpdate { we: True, mask: 32'h800,
                       value: eSet ? 32'h800 : 32'h0 };
    end
    CtlUpd cu = noCtlUpd();
    Bool ser = False;
    Word serPc = i.nextPc;
    Bool cretCatch = False;
    Word catchTo = 0;
    Bool flushTlb = False;
    Bool flushIc = False;
    if (sysOn && !trap) begin
      // The CPU escape: every CPU instruction executes alone (EU_S1
      // waits for an empty pipeline; here it squashes what follows).  A
      // control-register destination is written at commit, last
      // (p. 3-14), and is not a memory write: the reference record has
      // no store for it.  "When the SP is the direct destination ... the
      // MSP is updated with the same value. This defines an empty stack
      // cache" (p. 1-13).  SHAD follows a written CSP (p. 1-16).
      if (d.cpu) ser = True;
      if (d.cpu && (d.dst.mode == 4'h7) && opWritesDst(d.op) && store) begin
        Bit#(4) r = d.dst.val[3:0];
        Word v16 = res & 32'hFFFFFFF0;
        case (r)
          4'd1: after.msp = v16;
          4'd2: begin
            cu.isp = tagged Valid v16;
            if (psw[9] == 1'b0) cu.shad = tagged Valid v16;
          end
          4'd3: begin
            after = SpMsp { sp: v16, msp: v16 };
            if (psw[9] == 1'b1) cu.shad = tagged Valid v16;
          end
          // Bits 3:0 "must be written with 0" and 31:17 are reserved
          // (Table 1-8, pp. 1-14, 1-16); the write replaces the PSW,
          // flags included.
          4'd5: pu = PswUpdate { we: True, mask: 32'hFFFFFFFF,
                                 value: res & 32'h0001FFF0 };
          4'd6: cu.shad = tagged Valid v16;
          default: cu.creg = tagged Valid tuple2(r, res);
        endcase
        store = False;
      end
      // CSP = ISP: "SHAD = ISP = target" for ENTER, ISP += src for POPN
      // and RETURN (PC = *(ISP+src)), CATCH a no-op (pp. 3-10, 3-19,
      // 3-38, 3-40).  The ISP moves at commit, so the instruction
      // serializes: the next one forms its stack operands from the new
      // ISP.
      if (i.ispMode && isSpOp(d.op)) begin
        Word nisp = i.csp;
        case (d.op)
          OP_ENTER:  nisp = (modeIsStack(d.src.mode) ? i.csp + d.src.val
                                                     : d.src.val)
                            & 32'hFFFFFFF0;
          OP_RETURN: begin
            nisp  = i.csp + (d.src.val & 32'hFFFFFFF0);
            serPc = i.retPc;
          end
          OP_POPN:   nisp = i.csp + (d.src.val & 32'hFFFFFFF0);
          default:   nisp = i.csp;
        endcase
        cu.isp  = tagged Valid nisp;
        cu.shad = tagged Valid nisp;
        ser = True;
      end
      // CRET (p. 3-15): SP = *(ISP+0); MSP = *(ISP+4) after an
      // unconditional CATCH to it; PC = *(ISP+8); PSW = *(ISP+12);
      // ISP += 16; SHAD = the new CSP.  The cache is emptied at SP and
      // refilled under the *restored* PSW (cretCatch, EU_S3), so the
      // record's MSP after is the target.  KRET (p. 3-30): PC, PSW and
      // ISP the same way; SP and MSP unchanged.
      if (sysFrame) begin
        Word ib = i.srcEa - 8;
        Word nisp = ib + 16;
        pu = PswUpdate { we: True, mask: 32'hFFFFFFFF, value: framePsw };
        cu.isp = tagged Valid nisp;
        ser = True;
        serPc = framePc & 32'hFFFFFFFE;
        if (d.op == OP_CRET) begin
          Word nsp  = i.srcVal & 32'hFFFFFFF0;
          Word nmsp = i.dstVal & 32'hFFFFFFF0;
          after = SpMsp { sp: nsp, msp: nmsp };
          cu.shad = tagged Valid ((framePsw[9] == 1'b1) ? nsp : nisp);
          cretCatch = (framePsw[9] == 1'b1) && (nmsp > nsp);
          catchTo = nmsp;
        end else
          cu.shad = tagged Valid ((framePsw[9] == 1'b1) ? i.spBefore : nisp);
      end
      if (d.op == OP_FLUSH) begin
        ser = True; flushIc = True;
      end
      if (d.op == OP_FLUSHPTE) begin
        ser = True; flushTlb = True;
      end
    end

    // ---- the one architectural write --------------------------------
    WrInfo wr = noWr();
    // The trap's write is the unimplemented-instruction sequence's
    // `*(CSP) = PC` (pp. 1-39, 1-40).  On the privileged machine the other
    // traps are exceptions (p. 1-38), which write only their frame on the
    // interrupt stack: their record has no write (hobbit_sem
    // `_system_exception`; the s9term boot's first user fetch fault,
    // record 2,886,867).  The other cores keep the old record.
    if (trap && (!sysOn || (d.tr == TR_UNIMP)))
      wr = WrInfo { we: True, addr: i.csp & 32'hFFFFFFFC, data: d.pc,
                    mask: 8'h0F, wdata: d.pc };
    else if (d.op == OP_KCALL)
      wr = WrInfo { we: True, addr: (events.isp() - 12) & 32'hFFFFFFFC,
                    data: src, mask: 8'h0F, wdata: src };
    else if (isAccOp(d.op))
      wr = accWr(i.csp, res);
    else if (d.op == OP_CALL)
      wr = WrInfo { we: True, addr: i.csp & 32'hFFFFFFFC, data: i.base,
                    mask: 8'h0F, wdata: i.base };
    else if (opWritesDst(d.op) && store) begin
      if (modeIsImm(d.dst.mode))
        fatal = True;                        // store to an immediate: illegal
      else
        wr = memWr(i, dstW, res);
    end

    // Branch resolution in this stage: RETURN's indirect target and a
    // conditional jump two instructions after its compare.
    Bool squashR = False;
    Word redirectR = 0;
    Word occ = 1 + i.extra;
    Bool foldMisR = False;
    Word foldRedirR = 0;

    if (!trap) begin
      if (d.op == OP_KCALL) begin
        // PC = *(VB+0) (p. 3-29); the frame and ISP are handled at commit.
        squashR   = True;
        redirectR = events.memRead(vb);
      end else if (((d.op == OP_RETURN) && !i.ispMode) || flowIndirect(d)) begin
        squashR   = True;
        redirectR = i.retPc;
      end else if (isCondJumpOp(d.op) && !d.fold) begin
        if (i.sinceCmp == 1) begin
          Bool taken = branchTaken(d.op, (psw[4] == 1'b1));
          if (taken != predictedTaken(d.op)) begin
            squashR   = True;
            redirectR = e.altNextPc;
            occ       = occ + 1;          // Table 4-35: 2
          end
        end
        // sinceCmp == 0 resolves in EU_S3; sinceCmp >= 2 in EU_S1.
      end else if (d.fold && isCompareOp(d.op)) begin
        // A folded branch into the compare itself: the flag is the
        // compare's result.  The branch's own record carries the
        // Table 4-35 cost; the host keeps its one slot.
        Bool taken = branchTaken(d.foldOp, flagNew);
        if (taken != predictedTaken(d.foldOp)) begin
          foldMisR   = True;
          foldRedirR = taken ? d.foldTarget : d.foldAfter;
        end
      end
    end

    ScCmd cmd = ScCmd { op: (trap || fatal || i.ispMode) ? BX_NONE
                                                         : boxOpOf(d.op),
                        we: wr.we, waddr: wr.addr, wdata: wr.wdata,
                        wbe: wr.mask[3:0],
                        spBefore: i.spBefore, mspBefore: i.mspBefore,
                        spAfter: after.sp,
                        mspAfter: cretCatch ? after.sp : after.msp,
                        target: stackTarget(i),
                        stackMode: modeIsStack(d.src.mode) };

    outD <= EuS2Out { e: e, pc: i.pc,
                      spBefore: i.spBefore, mspBefore: i.mspBefore,
                      spAfter: after.sp, mspAfter: after.msp,
                      base: i.base, wr: wr, nextPc: i.nextPc,
                      squash: squashR, redirectPc: redirectR,
                      occ: occ, sinceCmp: i.sinceCmp,
                      flagValid: cmp, flagValue: flagNew, pswUpd: pu,
                      foldMis: foldMisR, foldRedirect: foldRedirR,
                      cmd: cmd,
                      fatal: fatal && !trap,
                      divZero: divZero,
                      kcall: (d.op == OP_KCALL) && !trap && !fatal,
                      dqm: (isDqmOp(d.op) && !i.dqmMem && !trap && !fatal)
                             ? ((d.op == OP_DQM4) ? 3'd4 : 3'd2) : 3'd0,
                      silent: i.dqmMem && (i.dqmIdx != 0),
                      kframe: events.isp(),
                      serialize: ser && !fatal, serPc: serPc,
                      ctlUpd: cu, cretCatch: cretCatch && !fatal,
                      catchTo: catchTo,
                      flushTlb: flushTlb, flushIc: flushIc,
                      xw: isInterlockedOp(d.op) && !ilToAcc && !trap && !fatal,
                      xwAddr: (i.csp + 4) & 32'hFFFFFFFC, xwData: dst };
    outFull <= True;
    inFull  <= False;
   end
  endrule

  rule rl_reset;
    f_reset_reqs.deq;
    f_reset_rsps.enq(?);
  endrule

  method Action start();
    inFull  <= False;
    outFull <= False;
  endmethod

  method Action enq(EuS1Out d);
    inD    <= d;
    inFull <= True;
  endmethod
  method Bool canAccept() = !inFull;
  method EuS2Out out() = outD;
  method Action deq();
    outFull <= False;
  endmethod
  method Bool notEmpty() = outFull;
  method Bool occupied() = inFull || outFull;

  method EuBypass bypass();
    if (!outFull) return noBypass();
    else begin
      let o = outD;
      return EuBypass { valid: True, we: o.wr.we,
                        addr: o.wr.addr, data: o.wr.wdata,
                        changesSp: isSpOp(o.e.d.op),
                        spAfter: o.spAfter,
                        changesMsp: isSpOp(o.e.d.op),
                        mspAfter: o.mspAfter };
    end
  endmethod

  method Bool squash() = outFull && outD.squash;
  method Word redirectPc() = outFull ? outD.redirectPc : 0;
  method Action flush();
    flushW <= True;
  endmethod

  interface Server server_reset;
    interface Put request  = toPut(f_reset_reqs);
    interface Get response = toGet(f_reset_rsps);
  endinterface
endmodule

// ---------------------------------------------------------------------
// EU_S3: write back, retire and emit the trace record.
// ---------------------------------------------------------------------
interface HobbitEuS3;
  interface Server#(Token, Token) server_reset;
  method Action start();
  method Action enq(EuS2Out d);
  method Bool canAccept();
  method Bool notEmpty();
  method Hri out();
  method Action deq();
  method Bool occupied();
  method Bool pswF();
  method Maybe#(PswUpdate) pswWrite();
  // True while a KCALL frame word is still to be written; the orchestrator
  // holds the pipeline until it drains, so younger instructions cannot read
  // a half-written frame.
  method Bool framePending();
  method Bool flushIcNow();
  // CRET's CATCH portion (p. 3-15) is under way: its record waits for the
  // refill, and `cretPc` is the PC the CRET restored.  `cretFault` ends
  // it at a read fault (p. 3-11): the record goes out with MSP at the
  // blocks filled, `mspFilled`.
  method Bool cretCatchActive();
  method Word cretPc();
  method Action cretFault(Word mspFilled);
  // Harness probe for the interrupt boundary (P9KernTb's stall report).
  method Bit#(12) dbgStop();
  // An interrupt boundary (mkHobbitCoreSystem's recorded interrupts):
  // commit nothing once `n` records have retired (the head of the
  // orchestrator's interrupt queue, passed in as `stopAt`); `stopPc` is
  // then the PC of the instruction that has not executed.
  method Maybe#(Word) stopPc();
  method Bool trapPending();
  method TrapReason trapReason();
  method Word trapPc();
  method Parcel trapInsn0();
  method Bool trapNiladic();
  method Action clearTrap();
  method Action flush();
  method Word lastPc();
  method EuBypass bypass();
  method Bool squash();
  method Word redirectPc();
  method Bool faulted();
  method Word faultPc();
  method Bit#(32) instrs();
  method Bit#(32) folded();
endinterface

module mkHobbitEuS3#(HobbitStackCache sc, Reg#(Word) psw,
                     HobbitEvents events, Bool eventsOn,
                     HobbitCtl ctl, HobbitMmu mmu,
                     Maybe#(Bit#(32)) stopR,
                     HobbitMmuMem dface, Bool sysOn)(HobbitEuS3);
  // structure follows Flute (Bluespec, Inc., Apache-2.0) — see
  // docs/bluespec_architecture.md.  The HRI record is the trace port
  // (Flute's g_pc_trace analogue), not datapath.

  // Input slot as a full/data register pair for the same reason as EU_S2:
  // `bypass`, `squash` and `redirectPc` are read by EU_S1's rules, and a
  // FIFOF's guarded `first` would conjoin this stage's occupancy into
  // them.  `traceQ` keeps its FIFOF shape: every rule that touches its
  // `first` is genuinely guarded by its `notEmpty`.
  Reg#(Bool) inFull <- mkReg(False);
  Reg#(EuS2Out) inD <- mkRegU;
  FIFOF#(Hri) traceQ <- mkSizedFIFOF(64);
  Reg#(Bool) faultedR <- mkReg(False);
  Reg#(Word) faultPcR <- mkReg(0);
  Reg#(Bit#(32)) ninstr <- mkReg(0);
  Reg#(Bit#(32)) nfold <- mkReg(0);
  Reg#(Bool) haltR <- mkReg(False);
  Reg#(Word) lastPcR <- mkReg(0);
  Reg#(Bool) trapPendR <- mkReg(False);
  Reg#(TrapReason) trapReasonR <- mkReg(TR_NONE);
  Reg#(Word) trapPcR <- mkReg(0);
  Reg#(Parcel) trapInsn0R <- mkReg(0);
  Reg#(Bool) trapNiladicR <- mkReg(False);

  // The instruction's PSW write and an event's pipeline flush are one-cycle
  // wires so the core's PSW rule sees them in the commit cycle, and the
  // commit rule can be blocked in the flush cycle.
  Wire#(Maybe#(PswUpdate)) flagWW <- mkDWire(tagged Invalid);
  Wire#(Bool) flushW <- mkDWire(False);

  // A folded branch record follows its host in the trace.
  Reg#(Maybe#(Hri)) pendFold <- mkReg(tagged Invalid);

  // KCALL's frame tail (return PC at ISP-8, PSW at ISP-4; p. 3-29).  The
  // box has one command per cycle, so the two words leave in the two
  // following cycles; `framePending` holds the pipeline until they do.
  Reg#(Bool) fq0v <- mkReg(False);
  Reg#(Word) fq0a <- mkReg(0);
  Reg#(Word) fq0d <- mkReg(0);
  Reg#(Bool) fq1v <- mkReg(False);
  Reg#(Word) fq1a <- mkReg(0);
  Reg#(Word) fq1d <- mkReg(0);
  // A third entry: DQM's quad word has three words after the first.
  Reg#(Bool) fq2v <- mkReg(False);
  Reg#(Word) fq2a <- mkReg(0);
  Reg#(Word) fq2d <- mkReg(0);
  // CRET's CATCH portion (p. 3-15): the refill of [SP, MSP) starts one
  // clock after the CRET commits, when the restored PSW (virtual
  // addressing, its level) is the PSW the data face translates with;
  // `catchWait` then holds the pipeline until the refill has ended.
  Reg#(Maybe#(Tuple2#(Word, Word))) pendCatch <- mkReg(tagged Invalid);
  Reg#(Bool) catchWait <- mkReg(False);
  // CRET's record, held until its CATCH portion ends: the reference
  // retires CRET with MSP where the portion left it -- the target, or the
  // last block filled before a read fault (hobbit_sem `_cret_catch`).
  Reg#(Maybe#(Hri)) pendCretRec <- mkReg(tagged Invalid);
  Reg#(Word) cretPcR <- mkReg(0);
  Wire#(Maybe#(Word)) cretFaultW <- mkDWire(tagged Invalid);
  // The interrupt boundary: after record `stopR` no instruction commits
  // until the orchestrator has taken the interrupt.  A host and its folded
  // branch are two records the reference model executes as two steps, so
  // the boundary can fall between them; the host then commits alone and
  // squashes to the branch's PC (`splitHere`), and the branch is the
  // instruction the interrupt saves.  `stopR` is the parameter: the
  // record number at the head of the orchestrator's queue.
  // FLUSHI/FLUSHP: the orchestrator empties the decoded-instruction
  // store when it redirects for the serializing squash.

  FIFOF#(Token) f_reset_reqs <- mkFIFOF;
  FIFOF#(Token) f_reset_rsps <- mkFIFOF;

  // A conditional jump issued immediately after its compare resolves
  // here, because the compare's PSW.F write and this stage's read are
  // the same edge: two younger slots are squashed (Table 4-35's 3).
  //
  // The same machinery retires a folded branch: it is one record with
  // cyc 0 (p. 4-3 note), and a misprediction costs the branch record 3
  // (Table 4-35's only printed row for it), on the flag below.
  //
  // The flag a folded branch tests: the host's own result when the host
  // is a compare, and the committed PSW.F otherwise.  A host that is not
  // a compare issues at least one slot after its compare, so by the time
  // it reaches this stage the compare's commit has written pswFR (a fold
  // into the compare itself cannot use pswFR -- the host is the writer --
  // and EU_S2 resolves that case, reporting it as foldMis).
  function Bool foldFlagValue(EuS2Out o) =
    isCompareOp(o.e.d.op) ? o.flagValue : (psw[4] == 1'b1);

  function Bool foldTaken(EuS2Out o) =
    branchTaken(o.e.d.foldOp, foldFlagValue(o));

  function Bool foldMispredicted(EuS2Out o) =
    o.e.d.fold &&
    (o.foldMis || (foldTaken(o) != predictedTaken(o.e.d.foldOp)));

  Bit#(32) recNow = ninstr + nfold;
  Bool stopHere = case (stopR) matches
                    tagged Valid .n: return recNow == n;
                    default: return False;
                  endcase;
  function Bool splitHere(EuS2Out o);
    case (stopR) matches
      tagged Valid .n:
        return o.e.d.fold && !o.silent && (o.e.d.tr == TR_NONE) &&
               (recNow + 1 == n);
      default: return False;
    endcase
  endfunction

  function Bool squashOf(EuS2Out o);
    if (o.e.d.tr != TR_NONE) return False;
    else if (splitHere(o)) return True;
    else if (o.serialize) return True;
    else if (isCondJumpOp(o.e.d.op) && !o.e.d.fold &&
             (o.sinceCmp == 0)) begin
      Bool taken = branchTaken(o.e.d.op, (psw[4] == 1'b1));
      return taken != predictedTaken(o.e.d.op);
    end else
      return foldMispredicted(o);
  endfunction

  function Word redirectOf(EuS2Out o);
    if (splitHere(o))
      return o.e.d.foldPc;
    else if (o.serialize)
      return o.serPc;
    else if (isCondJumpOp(o.e.d.op) && !o.e.d.fold &&
        (o.sinceCmp == 0)) begin
      // A misprediction means the actual path is the alternate one.
      return o.e.altNextPc;
    end else if (o.e.d.fold)
      return foldTaken(o) ? o.e.d.foldTarget : o.e.d.foldAfter;
    else
      return 0;
  endfunction

  function Hri hostRecord(EuS2Out o, Word cyc);
    let d = o.e.d;
    return Hri { valid: True, pc: d.pc, insn0: d.insn0, insn1: d.insn1,
                 sp_before: o.spBefore, sp_after: o.spAfter,
                 msp_before: o.mspBefore, msp_after: o.mspAfter,
                 mem_we: o.wr.we, mem_addr: o.wr.addr,
                 mem_wdata: o.wr.data,
                 mem_wmask: o.wr.we ? o.wr.mask : 8'h00,
                 trap: (d.tr != TR_NONE), cyc: cyc };
  endfunction

  function Hri foldRecord(EuS2Out o, Word cyc);
    let d = o.e.d;
    return Hri { valid: True, pc: d.foldPc, insn0: d.foldInsn0, insn1: 0,
                 sp_before: o.spBefore, sp_after: o.spAfter,
                 msp_before: o.mspBefore, msp_after: o.mspAfter,
                 mem_we: False, mem_addr: 0, mem_wdata: 0,
                 mem_wmask: 0, trap: False, cyc: cyc };
  endfunction

  // An event flush with an instruction still held: only the interrupt
  // boundary does that (every other event starts with this slot empty, or
  // with its instruction just committed).  The held instruction has not
  // executed -- the interrupt saves its PC -- so it is dropped.
  rule dropHeld (flushW && (inFull || isValid(cretFaultW)));
    inFull <= False;
    if (cretFaultW matches tagged Valid .m) begin
      if (pendCretRec matches tagged Valid .h) begin
        let k = h;
        k.msp_after = m;
        traceQ.enq(k);
      end
      pendCretRec <= tagged Invalid;
      pendCatch <= tagged Invalid;
      catchWait <= False;
    end
  endrule

  rule commit (!haltR && traceQ.notFull && !flushW);
    if (pendCatch matches tagged Valid {.csp, .cto}) begin
      // CRET's refill: the cache was emptied at the new SP by the CRET's
      // own command; this CATCH fills it to the restored MSP.
      ScCmd k = noScCmd();
      k.op = BX_CATCH;
      k.spBefore  = csp;
      k.mspBefore = csp;
      k.spAfter   = csp;
      k.mspAfter  = cto;
      k.target    = cto;
      k.stackMode = False;
      sc.commit(k);
      pendCatch <= tagged Invalid;
      catchWait <= True;
    end else if (catchWait) begin
      if (!sc.busy) begin
        catchWait <= False;
        if (pendCretRec matches tagged Valid .h) traceQ.enq(h);
        pendCretRec <= tagged Invalid;
      end
    end else if (fq0v) begin
      // KCALL's frame tail (return PC at ISP-8, PSW at ISP-4; p. 3-29),
      // one word per clock through the box's single command port, ahead
      // of any retirement in this same rule.
      ScCmd k = noScCmd();
      k.op     = BX_WRITE;
      k.we     = True;
      k.waddr  = fq0a;
      k.wdata  = fq0d;
      k.spBefore  = sc.sp;
      k.mspBefore = sc.msp;
      k.spAfter   = sc.sp;
      k.mspAfter  = sc.msp;
      sc.commit(k);
      fq0v <= fq1v;
      fq0a <= fq1a;
      fq0d <= fq1d;
      fq1v <= fq2v;
      fq1a <= fq2a;
      fq1d <= fq2d;
      fq2v <= False;
    end else if (fq1v) begin
      ScCmd k = noScCmd();
      k.op     = BX_WRITE;
      k.we     = True;
      k.waddr  = fq1a;
      k.wdata  = fq1d;
      k.spBefore  = sc.sp;
      k.mspBefore = sc.msp;
      k.spAfter   = sc.sp;
      k.mspAfter  = sc.msp;
      sc.commit(k);
      fq1v <= False;
    end else if (pendFold matches tagged Valid .r) begin
      traceQ.enq(r);
      pendFold <= tagged Invalid;
    end else if (inFull && !(stopHere && !inD.silent)) begin
      let o = inD;
      let d = o.e.d;
      Bool split = splitHere(o);
      if (o.fatal) begin
        // A fault the printed architecture raises as an exception (a
        // misaligned operand, pp. 1-4/1-27, or a zero divide, p. 3-17)
        // has no retirement record in this model: like the sem's Refusal
        // it stops the run loudly, and no architectural write happens.
        inFull   <= False;
        haltR    <= True;
        faultedR <= True;
        faultPcR <= d.pc;
        if (o.divZero)
          $fwrite(stderr, "TRAP pc=0x%08x: divide by zero (p. 3-17)\n", d.pc);
        else
          $fwrite(stderr,
                  "TRAP pc=0x%08x: misaligned operand (p. 1-4, p. 1-27)\n",
                  d.pc);
      end else begin
      // A jump resolved in this stage pays the two squashed slots
      // (Table 4-35's 3) on its own record.  A folded branch's cost is
      // the branch record's, which foldRecord carries; the host keeps its
      // one slot (p. 4-3 note), so a fold never adds to occ.
      Bool lateMis = isCondJumpOp(d.op) && !d.fold && (o.sinceCmp == 0) &&
                     squashOf(o);
      Word occ = o.occ + (lateMis ? 2 : 0);
      if (o.cretCatch) begin
        pendCretRec <= tagged Valid hostRecord(o, occ);
        cretPcR <= o.serPc;
      end else if (!o.silent)
        traceQ.enq(hostRecord(o, occ));
      if (d.fold && !split)
        pendFold <= tagged Valid (foldRecord(o, foldMispredicted(o) ? 3 : 0));
      if (o.pswUpd.we) flagWW <= tagged Valid o.pswUpd;
      if (!o.silent) ninstr <= ninstr + 1;
      if (d.fold && !split) nfold <= nfold + 1;
      lastPcR <= d.pc;
      // KCALL's frame is the kernel's: the reference makes it at kernel
      // level whatever the PSW's level (hobbit_sem.System).  Its first
      // word goes to memory in this clock under the caller's PSW, so the
      // data face is told; the two below drain after the PSW has become
      // the kernel's.  Found at record 2,888,578 of the s9term boot,
      // /boot's first system call, a write fault on the interrupt stack.
      if (sysOn && o.kcall) dface.kernelNow;
      if (o.kcall) begin
        // The frame's remaining two words (p. 3-29) and ISP -= 16.  The
        // orchestrator holds the pipeline while they drain.
        fq0v <= True;
        fq0a <= (o.kframe - 8) & 32'hFFFFFFFC;
        fq0d <= o.nextPc;                       // return PC
        fq1v <= True;
        fq1a <= (o.kframe - 4) & 32'hFFFFFFFC;
        fq1d <= psw;                            // PSW before the call
      end else if (o.xw) begin
        fq0v <= True;
        fq0a <= o.xwAddr;
        fq0d <= o.xwData;
      end else if (o.dqm != 0) begin
        // DQM's remaining words (p. 3-18): the same constant at the next
        // one or three word addresses, through the same drain.  EU_S1
        // issues nothing after a DQM until this has emptied.
        fq0v <= True;
        fq0a <= o.wr.addr + 4;
        fq0d <= o.wr.wdata;
        fq1v <= (o.dqm == 3'd4);
        fq1a <= o.wr.addr + 8;
        fq1d <= o.wr.wdata;
        fq2v <= (o.dqm == 3'd4);
        fq2a <= o.wr.addr + 12;
        fq2d <= o.wr.wdata;
      end
      if (d.tr != TR_NONE && eventsOn) begin
        // A trap must not move SP/MSP; noScCmd() carries zero pointers,
        // so keep the before values.  The one trap with an architectural
        // write is the unimplemented-instruction sequence, `*(CSP) = PC`
        // (pp. 1-39, 1-40): when the CSP is the SP that word belongs to
        // the stack, so it goes through the box like any other store
        // (into the cache when SP is inside the window, to memory when it
        // is not).  It used to reach only the event unit's own memory, so
        // a handler that returned through the stack read a stale word;
        // 1e's floating-point handler returns exactly that way.
        let k = noScCmd();
        k.spBefore  = o.spBefore;
        k.mspBefore = o.mspBefore;
        k.spAfter   = o.spBefore;
        k.mspAfter  = o.mspBefore;
        if ((d.tr == TR_UNIMP) && (psw[9] == 1'b1)) begin
          k.op    = BX_WRITE;
          k.we    = True;
          k.waddr = o.wr.addr;
          k.wdata = o.wr.wdata;
        end
        sc.commit(k);
      end else
        sc.commit(o.cmd);
      // Control-register writes, one call for the instruction: KCALL's
      // ISP -= 16 and SHAD = ISP (p. 3-29), or what EU_S2 decided
      // (mkHobbitCoreSystem: the CPU escape, CRET, KRET, CSP = ISP).
      Word kisp = (o.kframe - 16) & 32'hFFFFFFF0;
      CtlUpd cu = o.kcall ? CtlUpd { isp: tagged Valid kisp,
                                     shad: tagged Valid kisp,
                                     creg: tagged Invalid }
                          : o.ctlUpd;
      if ((d.tr == TR_NONE) &&
          (isValid(cu.isp) || isValid(cu.shad) || isValid(cu.creg)))
        ctl.apply(cu);
      if (o.cretCatch)
        pendCatch <= tagged Valid tuple2(o.spAfter, o.catchTo);
      if (o.flushTlb) mmu.flushAll;
      inFull <= False;
      if (d.tr != TR_NONE) begin
        if (eventsOn) begin
          trapPendR    <= True;
          trapReasonR  <= d.tr;
          trapPcR      <= d.pc;
          trapInsn0R   <= d.insn0;
          trapNiladicR <= (d.insn0[15:10] == 6'b001011) &&
                          (d.insn0[9:0] >= 10'h200);
        end else begin
          faultedR <= True;
          faultPcR <= d.pc;
          haltR    <= True;
          $fwrite(stderr, "TRAP pc=0x%08x: %s\n", d.pc, trapText(d.tr));
        end
      end
      end
    end
  endrule

  // KCALL's frame tail used to drain from a rule of its own (`drainFrame`).
  // It is written from `commit` below instead: a second rule calling the
  // box's commit method is starved by this one, and that starvation froze
  // 1e's `cat` at its syscall stub for 20,000 clocks (frame word pending,
  // commit slot empty, no fault, nothing retiring).  One rule, one box
  // command per clock, frame words ahead of any retirement.

  rule rl_reset;
    f_reset_reqs.deq;
    faultedR <= False;
    faultPcR <= 0;
    ninstr   <= 0;
    nfold    <= 0;
    haltR    <= False;
    pendFold <= tagged Invalid;
    inFull   <= False;
    fq0v <= False;
    fq1v <= False;
    fq2v <= False;
    pendCatch <= tagged Invalid;
    catchWait <= False;
    trapPendR <= False;
    trapReasonR <= TR_NONE;
    trapPcR <= 0;
    trapInsn0R <= 0;
    trapNiladicR <= False;
    lastPcR <= 0;
    traceQ.clear;
    f_reset_rsps.enq(?);
  endrule

  method Action start();
    faultedR <= False;
    faultPcR <= 0;
    ninstr   <= 0;
    nfold    <= 0;
    haltR    <= False;
    pendFold <= tagged Invalid;
    inFull   <= False;
    trapPendR <= False;
    trapReasonR <= TR_NONE;
    trapPcR <= 0;
    trapInsn0R <= 0;
    trapNiladicR <= False;
    lastPcR <= 0;
    traceQ.clear;
  endmethod

  // The handoff into this stage.  `enq` needs an empty slot and the
  // commit rule needs a full one, so they never collide.
  method Action enq(EuS2Out d);
    inD    <= d;
    inFull <= True;
  endmethod
  method Bool canAccept() = !inFull;
  method Bool notEmpty() = traceQ.notEmpty;
  // Harness probe: any record this stage still holds, in either slot.
  method Bool occupied() = inFull || traceQ.notEmpty;
  method Hri out() = traceQ.first;
  method Action deq() = traceQ.deq;
  method Bool pswF() = (psw[4] == 1'b1);
  method Maybe#(PswUpdate) pswWrite() = flagWW;
  method Bool framePending() = fq0v || fq1v || fq2v ||
                              isValid(pendCatch) || catchWait;
  method Bool flushIcNow() = inFull && inD.serialize && inD.flushIc;
  method Bool cretCatchActive() = isValid(pendCretRec);
  method Word cretPc() = cretPcR;
  method Action cretFault(Word mspFilled);
    cretFaultW <= tagged Valid mspFilled;
  endmethod
  method Maybe#(Word) stopPc();
    if (stopHere && inFull && !inD.silent && !fq0v && !fq1v && !fq2v &&
        !isValid(pendFold) && !isValid(pendCatch) && !catchWait)
      return tagged Valid inD.e.d.pc;
    else
      return tagged Invalid;
  endmethod
  method Bool trapPending() = trapPendR;
  method TrapReason trapReason() = trapReasonR;
  method Word trapPc() = trapPcR;
  method Parcel trapInsn0() = trapInsn0R;
  method Bool trapNiladic() = trapNiladicR;
  method Action clearTrap();
    trapPendR <= False;
  endmethod
  method Action flush();
    flushW <= True;
  endmethod
  method Word lastPc() = lastPcR;

  method EuBypass bypass();
    if (!inFull) return noBypass();
    else begin
      let o = inD;
      return EuBypass { valid: True, we: o.wr.we,
                        addr: o.wr.addr, data: o.wr.wdata,
                        changesSp: isSpOp(o.e.d.op),
                        spAfter: o.spAfter,
                        changesMsp: isSpOp(o.e.d.op),
                        mspAfter: o.mspAfter };
    end
  endmethod

  method Bool squash() = inFull && squashOf(inD);
  method Word redirectPc() = inFull ? redirectOf(inD) : 0;
  method Bit#(12) dbgStop() =
    { pack(isValid(stopR)), pack(stopHere), pack(inFull), pack(inD.silent),
      pack(fq0v), pack(fq1v), pack(fq2v), pack(isValid(pendFold)),
      pack(isValid(pendCatch)), pack(catchWait),
      pack(inFull && squashOf(inD)), pack(inFull && inD.serialize) };
  method Bool faulted() = faultedR;
  method Word faultPc() = faultPcR;
  method Bit#(32) instrs() = ninstr;
  method Bit#(32) folded() = nfold;

  interface Server server_reset;
    interface Put request  = toPut(f_reset_reqs);
    interface Get response = toGet(f_reset_rsps);
  endinterface
endmodule

// ---------------------------------------------------------------------
// Core: wire the boxes and the three EU stages, and drain the trace.
//
// PSW bit 16 (V) selects translation (p. 1-14, p. 2-1).  The stack
// cache and the prefetch buffer see translating memory faces; a fault
// latches in the data face (or becomes a TR_FETCH_FAULT in the PDU) and
// raises the p. 1-38 event sequence instead of the model's loud trap.
// `eventsOn = False` (mkHobbitCore) keeps the earlier diagnostic
// behaviour for the fixed oracles; `eventsOn = True`
// (mkHobbitCoreMmu) is the integrated MMU/event path.
// ---------------------------------------------------------------------
module mkHobbitCoreImpl#(HobbitMem mem, Word pcLimit, MemCycles m,
                         MmuTables tbl, Bool eventsOn,
                         Bool sysOn, HobbitEventMem evmem)(HobbitCore);

  Reg#(Word) pswR <- mkReg(0);
  // CONFIG bit 16, kernel little-endian (Table 1-2, p. 1-10): the data
  // byte order at kernel level, as PSW bit 15 is at user level (p. 1-3).
  // CONFIG's other bits are not modelled; reset value 0 (p. 1-36).
  Reg#(Bool) configKlR <- mkReg(False);
  Reg#(Word) vbR <- mkReg(0);
  Reg#(Bit#(3)) ilR <- mkReg(7);
  Reg#(Bool) eventActiveR <- mkReg(False);
  Reg#(Bool) traceFired <- mkReg(False);
  // A data-face read fault, classified on the clock it becomes visible:
  // `dfOpR` when the read was EU_S1's operand fetch (the box's memLive
  // names it), not a commit-time refill.  See `dfOperand` below.
  Reg#(Bool) dfKnownR <- mkReg(False);
  Reg#(Bool) dfOpR <- mkReg(False);

  Reg#(Bool) eventTakenR <- mkReg(False);
  Reg#(Word) eventPcR <- mkReg(0);
  Reg#(Bit#(4)) eventIdR <- mkReg(0);
  Reg#(Word) savedPcR <- mkReg(0);
  Reg#(Word) savedPswR <- mkReg(0);

  Wire#(Maybe#(Word)) setPswW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Word)) startPswW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Word)) eventPswW <- mkDWire(tagged Invalid);

  Reg#(Hri) present <- mkReg(unpack(0));
  Reg#(Bool) presentValid <- mkReg(False);
  // The privileged machine's exception record (hobbit_sem
  // _system_exception): an operand read fault takes the exception at an
  // instruction that never commits, and the reference retires a trap=1
  // record for it -- the faulting instruction's PC and parcels, the stack
  // pointers before the event and after it, no write.  `evRecPend` holds
  // the first half from startEvent, `evRec` the whole record from
  // finishEvent until the presentation slot takes it; `evRecs` counts
  // them as retirements.
  Reg#(Maybe#(Hri)) evRecPend <- mkReg(tagged Invalid);
  Reg#(Maybe#(Hri)) evRec <- mkReg(tagged Invalid);
  Reg#(Bit#(32)) evRecs <- mkReg(0);
  // A read fault in CRET's CATCH portion: the MSP the event leaves.
  Reg#(Maybe#(Word)) cretMspR <- mkReg(tagged Invalid);

  HobbitMmu mmu <- mkHobbitMmu(tbl);
  HobbitMmuMem textFace <- mkHobbitMmuMem(mem, mmu, True, pswR);
  HobbitMmuMem dataFace <- mkHobbitMmuMem(mem, mmu, False, pswR);
  HobbitEvents events <- (sysOn ? mkHobbitEventsSys(evmem, mmu)
                                : mkHobbitEventsCore(evmem, mmu));

  // The box owns the memory's one read port and lends it to the
  // prefetch buffer (sc.textPort), so it is instantiated first.
  HobbitStackCache sc <- mkHobbitStackCacheT(dataFace.mem, mem, m);
  HobbitPrefetch pf <- mkHobbitPrefetch(mem, sc.textPort, mmu, pswR);
  HobbitPdu pdu <- mkHobbitPdu(pf);
  HobbitDecodeStore ic <- mkHobbitDecodeStore(pdu, pf);
  HobbitCtl ctl <- mkHobbitCtl(configKlR, vbR, events, mmu, sc);

  // Instantiate the stages downstream-first so the bypass and flag
  // expressions can be passed as Flute passes stage2.out.bypass.
  // The recorded interrupts (armInterrupt): the head's record number is
  // EU_S3's boundary.  The PCs the taken ones saved go back the same way.
  // Unguarded: `stopAt` reads the head every clock, and a guarded `first`
  // would lift "not empty" into every rule that reads EU_S3's boundary --
  // the commit rule among them -- so the core stopped dead once the queue
  // emptied (found when the first interrupt of the s9term boot was taken
  // and nothing after it retired).  The uses below test notEmpty.
  FIFOF#(Tuple2#(Bit#(32), Bit#(3))) intQ <- mkUGSizedFIFOF(2);
  FIFOF#(Word) tookQ <- mkSizedFIFOF(4);
  // EU_S3 counts what it commits; the recorded number also counts the
  // exception records (`evRecs`, below), which EU_S3 never sees.
  Maybe#(Bit#(32)) stopAt = intQ.notEmpty
                              ? tagged Valid (tpl_1(intQ.first) - evRecs)
                              : tagged Invalid;
  HobbitEuS3 s3 <- mkHobbitEuS3(sc, pswR, events, eventsOn, ctl, mmu,
                                stopAt, dataFace, sysOn);
  HobbitEuS2 s2 <- mkHobbitEuS2(pswR, configKlR, vbR, sc, s3.bypass, events,
                                sysOn);

  // EU_S3 resolves the youngest misprediction (a jump right after its
  // compare); otherwise EU_S2's.
  Bool squash = s2.squash || s3.squash;
  Word redirectPc = s3.squash ? s3.redirectPc : s2.redirectPc;

  Bool drained = !s2.occupied && !s3.occupied && !s3.framePending() &&
                 !sc.busy();
  HobbitEuS1 s1 <- mkHobbitEuS1(ic, sc, m, s2.bypass, s3.bypass, pswR,
                                configKlR, squash, drained,
                                !s2.canAccept, pcLimit, eventActiveR,
                                sysOn, ctl);

  // ---- PSW ownership ------------------------------------------------
  // One rule writes PSW.  A compare's F bit arrives on EU_S3's DWire in
  // the commit cycle, so a compare-adjacent jump sees it in the next
  // cycle (Table 4-35's structural 3).  A start or a testbench write
  // overrides; an event's PSW &= 0xFFFF0000 (p. 1-37/1-38) is applied by
  // the finish rule.
  rule pswUpdate;
    if (isValid(startPswW))
      pswR <= validValue(startPswW);
    else if (isValid(setPswW))
      pswR <= validValue(setPswW);
    else if (isValid(eventPswW))
      pswR <= validValue(eventPswW);
    else if (isValid(s3.pswWrite())) begin
      let u = validValue(s3.pswWrite());
      pswR <= (pswR & ~u.mask) | (u.value & u.mask);
    end
  endrule

  // ---- S1 -> S2, the squash redirect, and S2 -> S3 -------------------
  function Action startCoreAt(Word sp, Word msp, Word p, Word pc0) =
    action
      sc.reset(sp, msp);
      ic.reset;
      s2.start;
      s3.start;
      s1.start(pc0);
      events.setIsp(sp);
      events.setShad(sp);
      startPswW <= tagged Valid p;
      presentValid <= False;
      present <= unpack(0);
      eventActiveR <= False;
      eventTakenR <= False;
      traceFired <= False;
    endaction;

  function Action startCore(Word sp, Word msp, Word p) =
    startCoreAt(sp, msp, p, 0);

  function Bool pipelineIdle() =
    !s1.notEmpty && !s2.occupied && !s3.occupied;

  function Bool intWanted() =
    (ilR != 3'b111) && ((ilR == 3'b000) || (ilR < pswR[14:12])) &&
    pipelineIdle();

  function Bool traceWanted() =
    (pswR[7] == 1'b1) && !traceFired && pipelineIdle();

  // Precise data faults (p. 1-37: an exception is taken at the faulting
  // instruction, which has not completed).  EU_S1 fetches an operand
  // before the instructions ahead of it have committed, and on a
  // mispredicted path it fetches operands the program never reads; such a
  // read can fault (1e's netadd, record 2,658,001 of the s9term boot: the
  // not-taken guess of a folded branch read through a pointer the taken
  // path does not dereference).  So an operand fault is held: EU_S1's
  // instruction goes no further, the older ones complete, and the event
  // starts only once they have -- the faulting instruction is then the
  // oldest, and its PC is EU_S1's.  A squash in the meantime proves the
  // read was on a wrong path and drops the fault.  A fault on a refill
  // (a write, or the box's CATCH/RETURN refill at commit) belongs to the
  // instruction that just committed, as before.
  Bool dfOperand = dataFace.fault() &&
                   (dfKnownR ? dfOpR : isValid(sc.memLive()));
  Bool dfOldest = !s2.occupied && !s3.occupied && !s3.framePending() &&
                  !squash;
  Bool dfTake = dataFace.fault() && (!dfOperand || dfOldest);

  rule classifyDataFault;
    if (!dataFace.fault()) begin
      dfKnownR <= False;
    end else if (!dfKnownR) begin
      dfKnownR <= True;
      dfOpR <= isValid(sc.memLive());
    end
  endrule

  // The recorded interrupt: EU_S3 has stopped at the boundary and holds
  // the next instruction (docs/p9boot.md, "The boot on the core").
  Bool boundaryInt = eventsOn && intQ.notEmpty && tookQ.notFull &&
                     isValid(s3.stopPc);

  function Bool eventWanted() =
    eventsOn && !eventActiveR &&
    (s3.trapPending() || dfTake || intWanted() || traceWanted() ||
     boundaryInt);

  // `!s3.framePending()` holds the pipeline while a KCALL's frame tail
  // drains, so the vector handler cannot read a half-written frame.
  rule deliver (!eventWanted() && !squash && !s3.framePending() &&
                !dfOperand && s1.notEmpty && s2.canAccept);
    let o = s1.out;
    s2.enq(o);
    s1.deq(o);
  endrule

  // A misprediction resolved in EU_S3 squashes *two* younger slots
  // (Table 4-35's 3): EU_S1's and EU_S2's.  EU_S1 is redirected; EU_S2
  // may already hold the first wrong-path instruction -- delivered in the
  // clock the resolving instruction moved from EU_S2 to EU_S3, before
  // EU_S3 could raise `squash` -- and it must be dropped too.  Until
  // 2026-11-20 it was not: it retired.  That needs the wrong-path
  // instruction to be in the decoded store already (a loop's second
  // pass), which no golden did; 1e's `echo` did at its 48th retirement
  // (atexit's table scan), and golden 018 now does.  A misprediction
  // resolved in EU_S2 needs no flush: `deliver` is held from the clock
  // the resolving instruction enters EU_S2's output slot.
  rule redirect (eventWanted() == False && squash);
    s1.redirect(redirectPc);
    if (s3.squash) s2.flush;
    // FLUSHI/FLUSHP (pp. 3-24, 3-25): the decoded-instruction store is
    // emptied as the serializing squash refetches past the flush.
    if (s3.flushIcNow) ic.reset;
    if (dfOperand) dataFace.clearFault;
  endrule

  rule move2to3 (!eventWanted() && s2.notEmpty && s3.canAccept);
    s3.enq(s2.out);
    s2.deq;
  endrule

  rule stopAtLimit (!eventWanted() && (s1.pc >= pcLimit));
    s1.stop;
  endrule

  // ---- event start / finish -----------------------------------------
  // The causes are all presented; the events box applies the p. 1-40
  // priority.  An interrupt outranks an instruction fault, so its PC is
  // the next instruction; otherwise the faulting instruction's PC (or
  // the p. 1-39 store PC for a data fault) is saved.
  rule startEvent (eventWanted());
    let c = noEventCauses();
    c.psw = pswR;
    c.sp  = sc.sp;
    c.vb  = vbR;
    let tp = s3.trapPending();
    let df = dfTake;
    let iw = intWanted();
    let tw = traceWanted();
    let bw = boundaryInt && !s3.trapPending();
    // CRET's CATCH portion faulted (p. 3-11, exception 8): the exception
    // is taken at the PC the CRET restored, under the restored PSW, with
    // MSP at the blocks already filled (hobbit_sem `_cret_catch`).
    let cf = df && !dfOperand && s3.cretCatchActive;

    if (bw)
      c.pc = validValue(s3.stopPc);
    else if (iw)
      c.pc = s1.pc;
    else if (tp)
      c.pc = s3.trapPc();
    else if (df && dfOperand)
      c.pc = s1.pc;
    else if (cf)
      c.pc = s3.cretPc;
    else if (df)
      c.pc = s3.lastPc();
    else
      c.pc = s1.pc;

    if (tp) begin
      case (s3.trapReason())
        TR_CPU:         c.illegal  = True;
        TR_BAD_LENGTH:  c.illegal  = True;
        TR_BAD_MODE:    c.illegal  = True;
        TR_RETURN_MODE: c.illegal  = True;
        TR_UNIMP: begin
          c.unimp   = True;
          c.niladic = s3.trapNiladic();
        end
        TR_ALIGN:       c.align    = True;
        TR_FETCH_MISS:  c.fetchFault = True;
        TR_FETCH_FAULT: c.fetchFault = True;
        TR_UNIMP_REG:   c.unimpReg = True;     // exception 6 (p. 1-27)
        default:        c.illegal  = True;
      endcase
    end
    if (df) begin
      if (dataFace.faultWrite()) c.writeFault = True;
      else                       c.readFault  = True;
      c.va = dataFace.faultAddr();
    end
    if (iw) begin
      c.interrupt = True;
      c.il      = ilR;
    end
    if (bw) begin
      c.interrupt = True;
      c.il      = tpl_2(intQ.first);
      intQ.deq;
      tookQ.enq(validValue(s3.stopPc));
    end
    if (tw) c.trace = True;

    if (cf) begin
      Word filled = dataFace.faultAddr() & 32'hFFFFFFF0;
      s3.cretFault(filled);
      cretMspR <= tagged Valid filled;
      sc.reset(sc.sp, filled);
    end
    if (sysOn && df && dfOperand && !bw && !iw && !tp) begin
      let e = s1.out.e.d;
      evRecPend <= tagged Valid Hri {
        valid: True, pc: s1.pc, insn0: e.insn0, insn1: e.insn1,
        sp_before: sc.sp, sp_after: 0, msp_before: sc.msp, msp_after: 0,
        mem_we: False, mem_addr: 0, mem_wdata: 0, mem_wmask: 0,
        trap: True, cyc: 0 };
    end

    if (!sysOn || (pswR[9] == 1'b1)) events.setShad(sc.shad);
    events.raise(c);
    eventActiveR <= True;
    if (tw) traceFired <= True;
    s1.stop;
    s2.flush;
    s3.flush;
    ic.reset;
    s3.clearTrap;
    dataFace.clearFault;
  endrule

  rule finishEvent (eventActiveR && events.done());
    let r = events.result();
    eventPswW  <= tagged Valid r.newPsw;
    s1.start(r.vector);
    sc.reset(r.newSp, fromMaybe(sc.msp, cretMspR));
    cretMspR <= tagged Invalid;
    events.ack;
    eventActiveR <= False;
    eventTakenR <= r.taken;
    eventPcR    <= r.vector;
    eventIdR    <= r.id;
    savedPcR    <= r.savedPc;
    savedPswR   <= r.savedPsw;
    if (r.newPsw[7] == 1'b0) traceFired <= False;
    if (evRecPend matches tagged Valid .h) begin
      let k = h;
      k.sp_after = r.newSp;
      k.msp_after = sc.msp;
      evRec <= tagged Valid k;
      evRecPend <= tagged Invalid;
      evRecs <= evRecs + 1;
    end
  endrule

  // ---- retirement presentation --------------------------------------
  (* descending_urgency = "loadEventRecord, loadTrace" *)
  rule loadEventRecord (!presentValid && isValid(evRec));
    present <= validValue(evRec);
    presentValid <= True;
    evRec <= tagged Invalid;
  endrule

  rule loadTrace (!presentValid && s3.notEmpty && !isValid(evRec));
    present <= s3.out;
    presentValid <= True;
    s3.deq;
  endrule

  rule retire (presentValid);
    let r = present;
    // The fixed line prints the PC in four hex digits; a PC that does not
    // fit them is printed whole (1e's zc has its text above 64 Kbytes, and
    // until 2026-11-20 its records lost the PC's upper half here).
    if (r.pc[31:16] == 0)
      $display("HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%d addr=%08x data=%08x mask=%02x trap=%d cyc=%0d",
               r.pc[15:0], r.insn0, r.insn1,
               r.sp_before, r.sp_after, r.msp_before, r.msp_after,
               pack(r.mem_we), r.mem_addr, r.mem_wdata, r.mem_wmask,
               pack(r.trap), r.cyc);
    else
      $display("HRI pc=%08x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%d addr=%08x data=%08x mask=%02x trap=%d cyc=%0d",
               r.pc, r.insn0, r.insn1,
               r.sp_before, r.sp_after, r.msp_before, r.msp_after,
               pack(r.mem_we), r.mem_addr, r.mem_wdata, r.mem_wmask,
               pack(r.trap), r.cyc);
    presentValid <= False;
  endrule

  method Action prefetchImage();
    pf.startFill();
  endmethod

  method Action prefetchImageAt(Word addr);
    pf.startFillAt(addr);
  endmethod

  method Bool prefetchReady() = pf.ready();

  method Action startPsw(Word sp, Word msp, Word p);
    startCore(sp, msp, p);
  endmethod

  method Action start(Word sp, Word msp);
    startCore(sp, msp, 0);
  endmethod

  method Action startAt(Word pc, Word sp, Word msp, Word psw);
    startCoreAt(sp, msp, psw, pc);
  endmethod

  method Bool halted() = s3.faulted;
  method Bool atLimit() =
    (pcLimit != 32'hFFFFFFFF) && !eventActiveR && (s1.pc >= pcLimit) &&
    !s1.notEmpty && !s2.occupied && !s3.occupied;
  method Bool faulted() = s3.faulted;
  method Word faultPc() = s3.faultPc;
  method Word pc() = s1.pc;

  method Word sp() = sc.sp;
  method Word msp() = sc.msp;
  method Word cacheWord(Word addr) = sc.cacheWord(addr);
  method Bool cached(Word addr) = sc.cached(addr);

  method Bit#(32) folded() = s3.folded;
  method Bit#(32) refills() = sc.refills;
  method Bit#(32) instrs() = s3.instrs + evRecs;
  method Word minSp() = sc.minSpSeen;
  method Word maxSp() = sc.maxSpSeen;

  method Bool hriValid() = presentValid;
  method Hri hri() = present;
  method Bool quiescent() = !presentValid && !s3.notEmpty;

  // ---- MMU / event testbench surface (added; no existing method
  // changed).  The machine never calls these.
  method Word psw() = pswR;
  method Action setConfigKl(Bool kl);
    configKlR <= kl;
  endmethod
  method Action setPsw(Word p);
    setPswW <= tagged Valid p;
    traceFired <= False;
  endmethod
  method Word vb() = vbR;
  method Action setVb(Word v) = action vbR <= v; endaction;
  method Bit#(3) il() = ilR;
  method Action armInterrupt(Bit#(32) n, Bit#(3) level) if (intQ.notFull);
    intQ.enq(tuple2(n, level));
  endmethod
  method ActionValue#(Word) takenInterrupt();
    tookQ.deq;
    return tookQ.first;
  endmethod
  method Action setIl(Bit#(3) v) = action ilR <= v; endaction;
  method Word isp() = events.isp;
  method Word shad() = events.shad;
  method Action setIsp(Word v) = events.setIsp(v);
  method Action setShad(Word v) = events.setShad(v);
  method Action flushPte(Word va) = mmu.flushPte(va);
  method Action flushTlb() = mmu.flushAll;
  method Action setStb(Word v) = mmu.setStb(v);
  method Bit#(32) mmuHits() = mmu.hits;
  method Bit#(32) mmuMisses() = mmu.misses;
  method Bit#(32) mmuWalks() = mmu.walks;
  method Bit#(32) mmuFaults() = mmu.faults;
  method Bool eventTaken() = eventTakenR;
  method Word eventPc() = eventPcR;
  method Bit#(4) eventId() = eventIdR;
  method Word savedPc() = savedPcR;
  method Word savedPsw() = savedPswR;
  method Bool eventActive() = eventActiveR;
  method Word eventMemRead(Word a) = events.memRead(a);
  method Action eventMemWrite(Word a, Word v) = events.memWrite(a, v);
  method Vector#(21, Maybe#(Word)) combProbes() =
    append(mmu.walkProbes, events.combProbes);
  method Word vbProbe() = vbR;
  method Bit#(4) memWrBe() = sc.memWrBe;
  method Bool memRdMerge() = sc.memRdMerge;
  method Bool memRdSpec() = sc.memRdSpec;
  method Action setRdNack(Bool n);
    sc.rdNack(n);
  endmethod

  method Bit#(32) dbgBoundary() =
    { 4'b0, s3.dbgStop,
      pack(intQ.notEmpty), pack(tookQ.notFull), pack(eventActiveR),
      pack(s1.notEmpty), pack(s2.occupied), pack(s3.occupied),
      pack(isValid(s3.stopPc)), pack(squash), pack(eventWanted()),
      pack(dfOperand), pack(s3.framePending), pack(s2.canAccept),
      pack(boundaryInt), pack(s3.trapPending), pack(dataFace.fault()),
      pack(s3.canAccept) };
  method Bit#(64) dbgState() =
    { zeroExtend(s1.pc[15:0]), pack(s2.notEmpty), pack(s3.notEmpty),
      pack(ic.filling), pack(pdu.outValid), pack(pdu.accepting),
      pack(pf.ready), s1.dbgS1, 34'b0 };

endmodule

// The fixed oracles keep the earlier loud-trap behaviour and physical
// memory; the integrated MMU/event path is a separate constructor.
module mkHobbitCore#(HobbitMem mem, Word pcLimit, MemCycles m)(HobbitCore);
  MmuTables tbl <- mkMmuTablesNull();
  HobbitEventMem evmem <- mkHobbitEventMem;
  HobbitCore c <- mkHobbitCoreImpl(mem, pcLimit, m, tbl, False, False, evmem);
  return c;
endmodule

// Events on, addressing physical: the unimplemented-instruction
// sequence and the other event sequences are performed (pp. 1-39, 1-40)
// instead of halting, with no translation tables.  A 1st Edition Plan 9
// process needs this for floating point (bsv/P9HostTb.bsv).
module mkHobbitCoreEvents#(HobbitMem mem, Word pcLimit, MemCycles m)(HobbitCore);
  MmuTables tbl <- mkMmuTablesNull();
  HobbitEventMem evmem <- mkHobbitEventMem;
  HobbitCore c <- mkHobbitCoreImpl(mem, pcLimit, m, tbl, True, False, evmem);
  return c;
endmodule

module mkHobbitCoreMmu#(HobbitMem mem, Word pcLimit, MemCycles m,
                        MmuTables tbl)(HobbitCore);
  HobbitEventMem evmem <- mkHobbitEventMem;
  HobbitCore c <- mkHobbitCoreImpl(mem, pcLimit, m, tbl, True, False, evmem);
  return c;
endmodule

// The privileged machine: everything mkHobbitCoreMmu has, plus the CPU
// escape and the control registers (p. 3-14, Table 1-24), CSP = ISP
// (p. 1-12), CRET and KRET (pp. 3-15, 3-30), FLUSHI/FLUSHP/FLUSHPTE and
// CONFIG.PX/KL -- what a kernel executes.  bsv/P9KernTb.bsv boots the
// shipped 1e kernel on it (docs/p9boot.md, "The boot on the core").  The
// table walk reads `tbl`, which a kernel boot backs with the machine's
// own memory (the kernel builds its tables in RAM).
module mkHobbitCoreSystem#(HobbitMem mem, Word pcLimit, MemCycles m,
                           MmuTables tbl, HobbitEventMem evmem)(HobbitCore);
  HobbitCore c <- mkHobbitCoreImpl(mem, pcLimit, m, tbl, True, True, evmem);
  return c;
endmodule

endpackage
