// HobbitEvents.bsv -- ATT92010 event processing as a box.
//
// Every sequence and priority below is from section 1.11 of the
// AT&T 92010 Hobbit Microprocessor Programmer's Reference Manual
// (January 1993), cited by printed page.  The structure follows Flute
// (Bluespec, Inc., Apache-2.0) -- see docs/bluespec_architecture.md:
// the multi-cycle event sequence is a stateful box with a
// raise/busy/done interface, not logic spread through the pipeline.
//
// Printed facts modelled here:
//
//   * Priority, highest first (p. 1-40): reset, interrupts, trace,
//     instruction fetch faults, illegal instructions, unimplemented
//     instructions/trapped niladic, unimplemented registers, alignment
//     faults, data read and write and read bus-error faults, privilege
//     violation, divide by zero.
//   * Interrupt levels (Table 1-25, p. 1-36): IL[2:0] = 000 NMI, 001
//     level 1 ... 110 level 6, 111 no interrupt.  A request is
//     serviced when its level is less than PSW.IPL, or equal to 0
//     (p. 1-36).
//   * Interrupt sequence (p. 1-37): disable interrupts; if CSP = ISP
//     then ISP = SHAD else SP = SHAD; *(ISP-8) = PC; *(ISP-4) = PSW;
//     ISP -= 16; SHAD = ISP; PC = *(VB+16+4*level); PSW &= 0xFFFF0000;
//     enable NMI.
//   * Exception sequence (p. 1-38): *(ISP-12) = exception ID;
//     *(ISP-8) = PC; *(ISP-4) = PSW; ISP -= 16; SHAD = ISP;
//     PC = *(VB+4); PSW &= 0xFFFF0000.  For IDs 0x8/0x9 the operand
//     aligned virtual address is saved in FAULT (p. 1-39).
//   * Unimplemented instruction (p. 1-39): *(CSP) = PC of unimplemented
//     opcode; PC = *(VB+12).  Trapped niladic (subcode 0x200..0x3FF,
//     p. 1-40): same save, PC = *(VB+8).
//   * Reset (p. 1-35): disable interrupts; flush PFB and IC; SHAD = 0
//     (external reset) or PSW (internal); PSW = 0; CONFIG = 0; PC = 0;
//     enable NMI.
//   * Exception identifiers (Table 1-26, p. 1-38): 0x1 divide by zero,
//     0x2 trace, 0x3 illegal, 0x4 alignment, 0x5 privilege, 0x6
//     unimplemented register, 0x7 fetch fault, 0x8 data read fault,
//     0x9 data write fault, 0xA I/O bus fault, 0xB table walk bus fault.
//   * Vector table (Table 1-14, p. 1-20): VB+0 KCALL, +4 exception,
//     +8 niladic, +12 unimplemented, +16 NMI, +20..+40 levels 1..6.
//   * A fault reading/writing the interrupt stack or the vector table
//     during event processing resets the processor (p. 1-35).
//
// The frame paths are virtual when PSW.V = 1 (p. 1-20 says vector-table
// address translation is performed when the MMU is enabled); the box
// therefore translates every frame address and the vector address
// through the MMU.  A translation fault on any of them takes the reset
// path of p. 1-35.
//
// The interrupt stack and vector table live in a small model memory
// (HobbitEventMem, 256 words / 1 KB) rather than in the program's
// single-port HobbitMem: the model's memory has one write port, and the
// event sequence must write up to three frame words while the stack
// cache may be writing.  The real chip has one bus and arbitrates; that
// arbitration is plan.md step 7 and is not invented here.
//
// The sequence is multi-cycle: one frame word per clock (the event
// memory's one write port), then the vector read.  The manual prints
// the sequence, not its cycle count; no Table 4 timing covers it.

package HobbitEvents;

import Vector::*;
import RegFile::*;
import HobbitTypes::*;
import HobbitMmu::*;

// ---------------------------------------------------------------------
// The interrupt-stack / vector-table model memory (1 KB).
// ---------------------------------------------------------------------
interface HobbitEventMem;
  method Word read(Word addr);          // combinational
  method Action write(Word addr, Word val);
endinterface

module mkHobbitEventMem(HobbitEventMem);
  // 256 words: the vector table at 0x000..0x034 and a stack at
  // 0x0F0..0x100 both fit.  Index is addr[9:2].
  RegFile#(Bit#(8), Word) rf <- mkRegFileFull;
  Reg#(Bit#(256)) written <- mkReg(0);

  function Bit#(8) idx(Word a) = truncate(a >> 2);

  method Word read(Word a) =
    (written[idx(a)] == 1'b1) ? rf.sub(idx(a)) : 32'd0;

  method Action write(Word a, Word v);
    rf.upd(idx(a), v);
    written <= written | (256'd1 << idx(a));
  endmethod
endmodule

// ---------------------------------------------------------------------
// Types.
// ---------------------------------------------------------------------
typedef enum {
  EV_NONE,          // priority 0
  EV_RESET,         // 1  p. 1-40
  EV_INTERRUPT,     // 2
  EV_TRACE,         // 3
  EV_FETCH_FAULT,   // 4
  EV_ILLEGAL,       // 5
  EV_UNIMP,         // 6  unimplemented instruction / trapped niladic
  EV_UNIMP_REG,     // 7
  EV_ALIGN,         // 8
  EV_READ_FAULT,    // 9  data read and write and read bus-error faults
  EV_WRITE_FAULT,   // 9
  EV_BUS_ERROR,     // 9
  EV_WALK_FAULT,    // 9  MMU table walk bus fault (Table 1-26 0xB)
  EV_PRIVILEGE,     // 10
  EV_DIVZERO        // 11
} EventClass deriving (Eq, Bits);

typedef struct {
  Bool     reset;
  Bool     internalReset;   // SHAD = PSW instead of 0 (p. 1-35)
  Bool     interrupt;
  Bit#(3)  il;              // IL[2:0], Table 1-25 p. 1-36
  Bool     trace;
  Bool     fetchFault;
  Bool     illegal;
  Bool     unimp;
  Bool     niladic;         // subcode 0x200..0x3FF -> VB+8 (p. 1-40)
  Bool     unimpReg;
  Bool     align;
  Bool     readFault;
  Bool     writeFault;
  Bool     busError;
  Bool     walkFault;
  Bool     privilege;
  Bool     divZero;
  Word     pc;              // faulting/interrupted PC
  Word     va;              // operand-aligned faulting address (FAULT)
  Word     psw;
  Word     sp;              // current SP (stack cache)
  Word     vb;              // vector table base
} EventCauses deriving (Bits);

function EventCauses noEventCauses();
  return EventCauses { reset: False, internalReset: False,
                       interrupt: False, il: 7, trace: False,
                       fetchFault: False, illegal: False, unimp: False,
                       niladic: False, unimpReg: False, align: False,
                       readFault: False, writeFault: False,
                       busError: False, walkFault: False,
                       privilege: False, divZero: False,
                       pc: 0, va: 0, psw: 0, sp: 0, vb: 0 };
endfunction

typedef struct {
  Bool       taken;
  EventClass cls;
  Bit#(4)    id;
  Word       vector;
  Word       savedPc;
  Word       savedPsw;
  Word       newPsw;
  Word       newIsp;
  Word       newShad;
  Word       newSp;
  Word       faultReg;
  Word       cspStoreAddr;
  Word       cspStoreData;
} EventResult deriving (Bits);

// Interrupt acceptance, p. 1-36: level < IPL, or level 0 (NMI); IL=7
// means no interrupt (Table 1-25).
function Bool interruptAccepted(Bit#(3) il, Word psw);
  let ipl = psw[14:12];
  return (il != 3'b111) && ((il == 3'b000) || (il < ipl));
endfunction

function EventClass chooseClass(EventCauses c);
  if (c.reset)
    return EV_RESET;
  else if (c.interrupt && interruptAccepted(c.il, c.psw))
    return EV_INTERRUPT;
  else if (c.trace)
    return EV_TRACE;
  else if (c.fetchFault)
    return EV_FETCH_FAULT;
  else if (c.illegal)
    return EV_ILLEGAL;
  else if (c.unimp)
    return EV_UNIMP;
  else if (c.unimpReg)
    return EV_UNIMP_REG;
  else if (c.align)
    return EV_ALIGN;
  else if (c.readFault)
    return EV_READ_FAULT;
  else if (c.writeFault)
    return EV_WRITE_FAULT;
  else if (c.busError)
    return EV_BUS_ERROR;
  else if (c.walkFault)
    return EV_WALK_FAULT;
  else if (c.privilege)
    return EV_PRIVILEGE;
  else if (c.divZero)
    return EV_DIVZERO;
  else
    return EV_NONE;
endfunction

// Table 1-26, p. 1-38.
function Bit#(4) classId(EventClass c);
  case (c)
    EV_DIVZERO:     return 4'h1;
    EV_TRACE:       return 4'h2;
    EV_ILLEGAL:     return 4'h3;
    EV_ALIGN:       return 4'h4;
    EV_PRIVILEGE:   return 4'h5;
    EV_UNIMP_REG:   return 4'h6;
    EV_FETCH_FAULT: return 4'h7;
    EV_READ_FAULT:  return 4'h8;
    EV_WRITE_FAULT: return 4'h9;
    EV_BUS_ERROR:   return 4'hA;
    EV_WALK_FAULT:  return 4'hB;
    default:        return 4'h0;
  endcase
endfunction

function Bool isFrameException(EventClass c);
  return c == EV_TRACE || c == EV_ILLEGAL || c == EV_ALIGN ||
         c == EV_PRIVILEGE || c == EV_UNIMP_REG ||
         c == EV_FETCH_FAULT || c == EV_READ_FAULT ||
         c == EV_WRITE_FAULT || c == EV_BUS_ERROR ||
         c == EV_WALK_FAULT || c == EV_DIVZERO;
endfunction

// ---------------------------------------------------------------------
// The event box.
// ---------------------------------------------------------------------
typedef enum { EVS_IDLE, EVS_WRITE, EVS_VECTOR, EVS_DONE } EvState
  deriving (Eq, Bits);

interface HobbitEvents;
  method Action raise(EventCauses c);
  method Bool busy();
  method Bool done();
  method EventResult result();
  method Word isp();
  method Word shad();
  method Word faultReg();
  method Action setIsp(Word isp);
  method Action setShad(Word shad);
  // The FAULT control register (Table 1-24 reg 9, p. 1-26): a CPU write
  // from the core.  The unit sets it itself on a read or write fault.
  method Action setFault(Word v);
  method Action ack();
  // Testbench access to the model event memory (load vectors, read the
  // saved frame).  The machine's only writer is the sequence rule.
  method Word memRead(Word addr);
  method Action memWrite(Word addr, Word val);
  // Every physical word this clock's step could read combinationally:
  // the walks of the frame and vector translations it evaluates
  // (HobbitMmu walkProbe) and the vector word itself.  Over-approximate
  // (the frame candidates of a raise are listed whatever the class), and
  // read by nothing in the machine: the ULX3S top prefetches them
  // (fpga/README.md, "The core's combinational reads").
  method Vector#(13, Maybe#(Word)) combProbes();
endinterface

// `cspInCore`: the unit is inside the core, which applies the
// unimplemented sequence's `*(CSP) = PC` to the real stack itself when
// the CSP is the SP (through the stack cache: EU_S3's commit).  The unit
// then does not also write that word to its own 256-word memory, whose
// index is addr[9:2]: a stack address aliases the vector table there, and
// an SP that is 0x000 or 0x00C modulo 1 Kbyte would overwrite the very
// vector the sequence reads next.  The standalone testbenches keep the
// write (their memory *is* the stack).
module mkHobbitEvents#(HobbitEventMem mem, HobbitMmu mmu)(HobbitEvents);
  HobbitEvents e <- mkHobbitEventsP(mem, mmu, False, False);
  return e;
endmodule

module mkHobbitEventsCore#(HobbitEventMem mem, HobbitMmu mmu)(HobbitEvents);
  HobbitEvents e <- mkHobbitEventsP(mem, mmu, True, False);
  return e;
endmodule

// The privileged machine's event unit (mkHobbitCoreSystem): the frame and
// the vector are the kernel's, so they are translated at kernel level
// whatever the level of the PSW the event interrupts -- the reference
// model's rule (hobbit_sem.System: "KCALL's frame and every vector read
// are made at kernel level whatever the PSW's level"); p. 1-37/1-38
// put both on the interrupt stack and the vector table, which a
// user-level translation of a kernel page would refuse.
module mkHobbitEventsSys#(HobbitEventMem mem, HobbitMmu mmu)(HobbitEvents);
  HobbitEvents e <- mkHobbitEventsP(mem, mmu, True, True);
  return e;
endmodule

module mkHobbitEventsP#(HobbitEventMem mem, HobbitMmu mmu,
                        Bool cspInCore, Bool atKernel)(HobbitEvents);
  Reg#(EvState) state <- mkReg(EVS_IDLE);
  Reg#(EventCauses) cR <- mkRegU;
  Reg#(EventClass) clsR <- mkReg(EV_NONE);
  Reg#(Bit#(4)) idR <- mkReg(0);
  Reg#(Word) baseR <- mkReg(0);
  Reg#(Word) newIspR <- mkReg(0);
  Reg#(Word) newShadR <- mkReg(0);
  Reg#(Word) newSpR <- mkReg(0);
  Reg#(Word) newPswR <- mkReg(0);
  Reg#(Word) vecAddrR <- mkReg(0);
  Reg#(Word) vecR <- mkReg(0);
  Reg#(Word) savedPcR <- mkReg(0);
  Reg#(Word) savedPswR <- mkReg(0);
  Reg#(Word) faultR <- mkReg(0);
  Reg#(Word) cspAddrR <- mkReg(0);
  Reg#(Word) cspDataR <- mkReg(0);
  Reg#(Bool) haveCspR <- mkReg(False);
  Reg#(Vector#(3, Word)) wrAddr <- mkReg(replicate(0));
  Reg#(Vector#(3, Word)) wrData <- mkReg(replicate(0));
  Reg#(Bit#(2)) nWrR <- mkReg(0);
  Reg#(Bit#(2)) wrIdxR <- mkReg(0);
  Reg#(Bool) doneR <- mkReg(False);
  Reg#(Bool) takenR <- mkReg(False);

  Reg#(Word) ispR <- mkReg(0);
  Reg#(Word) shadR <- mkReg(0);

  Wire#(Maybe#(EventCauses)) raiseW <- mkDWire(tagged Invalid);
  Wire#(Bool) ackW <- mkDWire(False);
  Wire#(Maybe#(Word)) setIspW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Word)) setShadW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Word)) setFaultW <- mkDWire(tagged Invalid);

  // Translate an event address; PSW.V selects (p. 1-20, p. 2-1).
  function MmuResp xlate(Word va, Bool wr, Word psw);
    return mmu.translate(MmuReq { va: va,
                                  isText: False,
                                  isWrite: wr,
                                  user: !atKernel && (psw[10] == 1'b1),
                                  enabled: (psw[16] == 1'b1) });
  endfunction

  function Bool xlateOk(Word va, Bool wr, Word psw);
    return xlate(va, wr, psw).fault == MMU_OK;
  endfunction

  function Word paOf(Word va, Bool wr, Word psw);
    return xlate(va, wr, psw).pa;
  endfunction

  // The step's translations: at most two a clock, by state and class.
  // In EVS_IDLE a raise needs base - 4 and base - 12 for its frame (base
  // - 8 is on one of their pages: a translation is a function of
  // va[31:12] alone, HobbitMmu translateFn), or the CSP alone for the
  // unimplemented sequence; EVS_WRITE needs its frame word, EVS_VECTOR
  // the vector.  So one translation (`evX1`) is muxed by state and class,
  // and one more (`evX2`) is base - 12's.  combProbes asks for the walks
  // of the same two requests, so the probes share this logic
  // (docs/fpga_area.md).
  Word ispNow = isValid(setIspW) ? validValue(setIspW) : ispR;
  Word shadNow = isValid(setShadW) ? validValue(setShadW) : shadR;
  EventCauses cRaise = validValue(raiseW);
  Word evBase = (cRaise.psw[9] == 1'b0) ? shadNow : ispNow;
  Word evCsp = (cRaise.psw[9] == 1'b1) ? cRaise.sp : ispNow;
  Bool evUnimp = (chooseClass(cRaise) == EV_UNIMP);
  Word evX1Va = (state == EVS_IDLE) ? (evUnimp ? evCsp : evBase - 4)
              : ((state == EVS_WRITE) ? wrAddr[wrIdxR] : vecAddrR);
  Bool evX1Wr = (state != EVS_VECTOR);
  Word evX1Psw = (state == EVS_IDLE) ? cRaise.psw : cR.psw;
  MmuResp evX1 = xlate(evX1Va, evX1Wr, evX1Psw);
  MmuResp evX2 = xlate(evBase - 12, True, cRaise.psw);

  rule step;
    // ISP/SHAD may be loaded by a testbench or the core before an event.
    Word isp = isValid(setIspW) ? validValue(setIspW) : ispR;
    Word shad = isValid(setShadW) ? validValue(setShadW) : shadR;

    Word nIsp = isp;
    Word nShad = shad;
    Word nNewIsp = newIspR;
    Word nNewShad = newShadR;
    Word nNewSp = newSpR;
    Word nNewPsw = newPswR;
    Word nBase = baseR;
    Word nVecAddr = vecAddrR;
    Word nVec = vecR;
    Word nSavedPc = savedPcR;
    Word nSavedPsw = savedPswR;
    Word fault0 = fromMaybe(faultR, setFaultW);
    Word nFault = fault0;
    Word nCspAddr = cspAddrR;
    Word nCspData = cspDataR;
    Bool nHaveCsp = haveCspR;
    Vector#(3, Word) nWrAddr = wrAddr;
    Vector#(3, Word) nWrData = wrData;
    Bit#(2) nNWr = nWrR;
    Bit#(2) nWrIdx = wrIdxR;
    EventClass nCls = clsR;
    Bit#(4) nId = idR;
    Bool nDone = doneR;
    Bool nTaken = takenR;
    EvState nState = state;
    EventCauses nC = cR;

    case (state)
      EVS_IDLE: begin
        if (isValid(raiseW)) begin
          let c = validValue(raiseW);
          let cls0 = chooseClass(c);
          nC = c;
          if (cls0 == EV_NONE) begin
            nState = EVS_DONE;
            nTaken = False;
            nDone  = True;
          end else begin
            // The interrupt/exception sequence first selects the
            // interrupt stack: if CSP = ISP then ISP = SHAD else
            // SP = SHAD (p. 1-37/1-38).
            Word base = (c.psw[9] == 1'b0) ? shad : isp;
            Word spNew = (c.psw[9] == 1'b0) ? c.sp : shad;
            // The frame words' translations (evX1, evX2 above): base - 8
            // is on base - 4's page unless base[11:0] < 8, and then on
            // base - 12's.  evX1 is base - 4's except for the
            // unimplemented sequence, which translates only the CSP.
            Bool okM12 = (evX2.fault == MMU_OK);
            Bool okM4  = (evX1.fault == MMU_OK);
            Bool okM8  = (base[11:0] >= 12'd8) ? okM4 : okM12;
            Word vAddr = 0;
            Word nPsw = c.psw;
            Word id = 0;
            Word nFl = fault0;
            Vector#(3, Word) as = replicate(0);
            Vector#(3, Word) ds = replicate(0);
            Bit#(2) nw = 0;
            Bool csp = False;
            Word cspA = 0;
            Word cspD = 0;
            Bool ok = True;

            if (cls0 == EV_RESET) begin
              nPsw  = 0;
              nShad = c.internalReset ? c.psw : 0;
              nIsp  = isp;
              vAddr = 0;
              nw    = 0;
            end else if (cls0 == EV_INTERRUPT) begin
              as[0] = base - 8;  ds[0] = c.pc;
              as[1] = base - 4;  ds[1] = c.psw;
              nw    = 2;
              nIsp  = base - 16;
              nShad = nIsp;
              vAddr = c.vb + 16 + (zeroExtend(c.il) << 2);
              nPsw  = c.psw & 32'hFFFF0000;
              ok    = okM8 && okM4;              // as[0], as[1]
            end else if (isFrameException(cls0)) begin
              id    = zeroExtend(classId(cls0));
              as[0] = base - 12; ds[0] = id;
              as[1] = base - 8;  ds[1] = c.pc;
              as[2] = base - 4;  ds[2] = c.psw;
              nw    = 3;
              nIsp  = base - 16;
              nShad = nIsp;
              vAddr = c.vb + 4;
              nPsw  = c.psw & 32'hFFFF0000;
              // "the word-aligned virtual address" (p. 1-39).
              if (id == 32'h8 || id == 32'h9)
                nFl = c.va & 32'hFFFFFFFC;
              ok    = okM12 && okM8 && okM4;     // as[0], as[1], as[2]
            end else if (cls0 == EV_UNIMP) begin
              // *(CSP) = PC; PC = *(VB+12) or *(VB+8) (pp. 1-39/1-40).
              Word cspAddr = (c.psw[9] == 1'b1) ? c.sp : isp;
              csp   = True;
              cspA  = cspAddr;
              cspD  = c.pc;
              as[0] = cspAddr;
              ds[0] = c.pc;
              vAddr = c.vb + (c.niladic ? 8 : 12);
              nw    = (cspInCore && (c.psw[9] == 1'b1)) ? 0 : 1;
              nIsp  = isp;
              nShad = shad;
              nPsw  = c.psw;
              ok    = (evX1.fault == MMU_OK);  // evX1 is cspA's here
            end

            // A translation fault during event processing resets the
            // processor (p. 1-35).
            if (!ok) begin
              nCls   = EV_RESET;
              nId    = 0;
              nPsw   = 0;
              nShad  = 0;
              nIsp   = isp;
              vAddr  = 0;
              nw     = 0;
              csp    = False;
            end else
              nCls = cls0;

            nId       = id[3:0];
            nBase     = base;
            nNewIsp   = nIsp;
            nNewShad  = nShad;
            nNewSp    = spNew;
            nNewPsw   = nPsw;
            nVecAddr  = vAddr;
            nSavedPc  = c.pc;
            nSavedPsw = c.psw;
            nFault    = nFl;
            nCspAddr  = cspA;
            nCspData  = cspD;
            nHaveCsp  = csp;
            nWrAddr   = as;
            nWrData   = ds;
            nNWr      = nw;
            nWrIdx    = 0;
            nTaken    = True;
            nVec      = 0;
            if ((cls0 == EV_RESET) || (!ok))
              nState = EVS_VECTOR;   // vector 0, read skipped below
            else
              nState = (nw == 0) ? EVS_VECTOR : EVS_WRITE;
          end
        end
      end

      EVS_WRITE: begin
        let c = nC;
        Word d = nWrData[nWrIdx];
        let x = evX1;                    // nWrAddr[nWrIdx], a write
        if (x.fault == MMU_OK)
          mem.write(x.pa, d);
        else begin
          // Should have been caught in capture; reset anyway.
          nNewPsw  = 0;
          nNewShad = 0;
          nState = EVS_VECTOR;
        end
        if (nWrIdx + 1 == nNWr)
          nState = EVS_VECTOR;
        else
          nWrIdx = nWrIdx + 1;
      end

      EVS_VECTOR: begin
        let c = nC;
        if ((nCls == EV_RESET) && (nVecAddr == 0)) begin
          nVec = 0;
        end else begin
          let x = evX1;                  // nVecAddr, a read
          if (x.fault == MMU_OK)
            nVec = mem.read(x.pa);
          else begin
            // A faulted vector read resets (p. 1-35).
            nCls     = EV_RESET;
            nId      = 0;
            nNewPsw  = 0;
            nNewShad = 0;
            nVec     = 0;
          end
        end
        nDone = True;
        nState = EVS_DONE;
      end

      EVS_DONE: begin
        if (ackW) begin
          nState = EVS_IDLE;
          nDone  = False;
          nTaken = False;
        end
      end
    endcase

    ispR       <= nIsp;
    shadR      <= nShad;
    newIspR    <= nNewIsp;
    newShadR   <= nNewShad;
    newSpR     <= nNewSp;
    newPswR    <= nNewPsw;
    baseR      <= nBase;
    vecAddrR   <= nVecAddr;
    vecR       <= nVec;
    savedPcR   <= nSavedPc;
    savedPswR  <= nSavedPsw;
    faultR     <= nFault;
    cspAddrR   <= nCspAddr;
    cspDataR   <= nCspData;
    haveCspR   <= nHaveCsp;
    wrAddr     <= nWrAddr;
    wrData     <= nWrData;
    nWrR       <= nNWr;
    wrIdxR     <= nWrIdx;
    clsR       <= nCls;
    idR        <= nId;
    doneR      <= nDone;
    takenR     <= nTaken;
    state      <= nState;
    cR         <= nC;
  endrule

  method Action raise(EventCauses c);
    raiseW <= tagged Valid c;
  endmethod

  method Bool busy() = (state != EVS_IDLE);
  method Bool done() = doneR;

  method EventResult result();
    return EventResult {
      taken: takenR, cls: clsR, id: idR, vector: vecR,
      savedPc: savedPcR, savedPsw: savedPswR, newPsw: newPswR,
      newIsp: newIspR, newShad: newShadR, newSp: newSpR,
      faultReg: faultR,
      cspStoreAddr: cspAddrR, cspStoreData: cspDataR
    };
  endmethod

  method Word isp() = ispR;
  method Word shad() = shadR;
  method Word faultReg() = faultR;

  method Action setIsp(Word v);
    setIspW <= tagged Valid v;
  endmethod

  method Action setShad(Word v);
    setShadW <= tagged Valid v;
  endmethod

  method Action setFault(Word v);
    setFaultW <= tagged Valid v;
  endmethod

  method Action ack();
    ackW <= True;
  endmethod

  method Vector#(13, Maybe#(Word)) combProbes();
    Vector#(13, Maybe#(Word)) v = replicate(tagged Invalid);
    function Vector#(2, Maybe#(Word)) wp(Word va, Bool wr, Word psw) =
      mmu.walkProbe(MmuReq { va: va, isText: False, isWrite: wr,
                             user: !atKernel && (psw[10] == 1'b1),
                             enabled: (psw[16] == 1'b1) });
    // The walks of evX1's and evX2's requests (the step's translations
    // above): base - 4 or the CSP and base - 12 in EVS_IDLE (base - 8's
    // walk is one of the frame's two, a walk's words being a function of
    // the page), the frame word in EVS_WRITE, the vector in EVS_VECTOR.
    let a = wp(evX1Va, evX1Wr, evX1Psw);
    let d = wp(evBase - 12, True, cRaise.psw);
    case (state)
      EVS_IDLE:
        if (isValid(raiseW)) begin
          v[0] = a[0]; v[1] = a[1]; v[4] = d[0]; v[5] = d[1];
        end
      EVS_WRITE: begin
        v[8] = a[0]; v[9] = a[1];
      end
      EVS_VECTOR: begin
        v[10] = a[0]; v[11] = a[1];
        if (evX1.fault == MMU_OK) v[12] = tagged Valid evX1.pa;
      end
    endcase
    return v;
  endmethod

  method Word memRead(Word addr) = mem.read(addr);
  method Action memWrite(Word addr, Word val);
    mem.write(addr, val);
  endmethod
endmodule

endpackage
