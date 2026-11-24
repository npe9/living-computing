// Xerox Alto II types and constants.
// Field layout follows Alto Hardware Manual §2.1 (bit 0 is MSB).

package AltoTypes;

typedef Bit#(16) Word;
typedef Bit#(10) UAddr;
typedef Bit#(5)  RSel;
typedef Bit#(4)  TaskId;

// Task numbers (priority = task id; 15 is highest).
typedef enum {
   TaskEmulator          = 0,
   TaskOrbit             = 1,
   TaskUnused2           = 2,
   TaskTridentOutput     = 3,
   TaskDiskSector        = 4,
   TaskUnused5           = 5,
   TaskUnused6           = 6,
   TaskEthernet          = 7,
   TaskMemoryRefresh     = 8,
   TaskDisplayWord       = 9,
   TaskCursor            = 10,
   TaskDisplayHorizontal = 11,
   TaskDisplayVertical   = 12,
   TaskParity            = 13,
   TaskDiskWord          = 14,
   TaskTridentInput      = 15
} TaskType deriving (Bits, Eq, FShow);

function TaskId taskId(TaskType t) = pack(t);

// Microinstruction fields.
typedef enum {
   AluBus            = 0,
   AluT              = 1,
   AluBusOrT         = 2,
   AluBusAndT        = 3,
   AluBusXorT        = 4,
   AluBusPlus1       = 5,
   AluBusMinus1      = 6,
   AluBusPlusT       = 7,
   AluBusMinusT      = 8,
   AluBusMinusTMinus1= 9,
   AluBusPlusTPlus1  = 10,
   AluBusPlusSkip    = 11,
   AluBusAndTWb      = 12,
   AluBusAndNotT     = 13,
   AluUndef1         = 14,
   AluUndef2         = 15
} AluFn deriving (Bits, Eq, FShow);

typedef enum {
   BsReadR        = 0,
   BsLoadR        = 1,
   BsNone         = 2,
   BsTask1        = 3,
   BsTask2        = 4,
   BsReadMD       = 5,
   BsReadMouse    = 6,
   BsReadDisp     = 7
} BusSource deriving (Bits, Eq, FShow);

typedef enum {
   F1None     = 0,
   F1LoadMAR  = 1,
   F1Task     = 2,
   F1Block    = 3,
   F1LLSH1    = 4,
   F1LRSH1    = 5,
   F1LLCY8    = 6,
   F1Constant = 7,
   // Task-specific values 8-15.
   F1Task8    = 8,
   F1Task9    = 9,
   F1Task10   = 10,
   F1Task11   = 11,
   F1Task12   = 12,
   F1Task13   = 13,
   F1Task14   = 14,
   F1Task15   = 15
} F1 deriving (Bits, Eq, FShow);

typedef enum {
   F2None     = 0,
   F2BusEq0   = 1,
   F2ShLt0    = 2,
   F2ShEq0    = 3,
   F2Bus      = 4,
   F2ALUCY    = 5,
   F2StoreMD  = 6,
   F2Constant = 7,
   F2Task8    = 8,
   F2Task9    = 9,
   F2Task10   = 10,
   F2Task11   = 11,
   F2Task12   = 12,
   F2Task13   = 13,
   F2Task14   = 14,
   F2Task15   = 15
} F2 deriving (Bits, Eq, FShow);

// Emulator F1/F2 (values 8-15).
Integer emuSWMODE   = 8;
Integer emuWRTRAM   = 9;
Integer emuRDRAM    = 10;
Integer emuLoadRMR  = 11;
Integer emuLoadESRB = 13;
Integer emuRSNF     = 14;
Integer emuSTARTF   = 15;

Integer emuBUSODD   = 8;
Integer emuMAGIC    = 9;
Integer emuLoadDNS  = 10;
Integer emuACDEST   = 11;
Integer emuLoadIR   = 12;
Integer emuIDISP    = 13;
Integer emuACSOURCE = 14;

// Disk F1/F2.
Integer dskSTROBE     = 9;
Integer dskLoadKSTAT  = 10;
Integer dskINCRECNO   = 11;
Integer dskCLRSTAT    = 12;
Integer dskLoadKCOMM  = 13;
Integer dskLoadKADR   = 14;
Integer dskLoadKDATA  = 15;

Integer dskINIT    = 8;
Integer dskRWC     = 9;
Integer dskRECNO   = 10;
Integer dskXFRDAT  = 11;
Integer dskSWRNRDY = 12;
Integer dskNFER    = 13;
Integer dskSTROBON = 14;

// Ethernet F1/F2 (HW manual §7.3; values are octal 13–16 / 10–16).
Integer ethEILFCT = 11;   // 13B look
Integer ethEPFCT  = 12;   // 14B post / reset
Integer ethEWFCT  = 13;   // 15B countdown wakeup
Integer ethEODFCT = 8;    // 10B output data
Integer ethEOSFCT = 9;    // 11B start output
Integer ethERBFCT = 10;   // 12B rest branch
Integer ethEEFCT  = 11;   // 13B end output
Integer ethEBFCT  = 12;   // 14B branch
Integer ethECBFCT = 13;   // 15B countdown branch
Integer ethEISFCT = 14;   // 16B start input

Integer etherFifoDepth  = 16;
Integer etherWordCycles = 32;    // 16 bits × 2 clocks/bit (§7.2)
Integer etherGapCycles  = 200;   // inter-frame silence before TX done

typedef enum { MemNone, MemLoadAddr, MemRead, MemStore } MemOp
   deriving (Bits, Eq, FShow);

typedef struct {
   RSel      rsel;
   AluFn     aluf;
   BusSource bs;
   F1        f1;
   F2        f2;
   Bool      loadT;
   Bool      loadL;
   UAddr     next;
} MicroInstr deriving (Bits, Eq, FShow);

function MicroInstr decodeU(Bit#(32) w);
   return MicroInstr {
      rsel:  w[31:27],
      aluf:  unpack(w[26:23]),
      bs:    unpack(w[22:20]),
      f1:    unpack(w[19:16]),
      f2:    unpack(w[15:12]),
      loadT: unpack(w[11]),
      loadL: unpack(w[10]),
      next:  w[9:0]
   };
endfunction

// ALU functions that also load T from the ALU output (HW manual).
function Bool loadTFromALU(AluFn f);
   Bit#(16) m = 16'h1C65;
   return unpack(m[pack(f)]);
endfunction

function Bool constantAccess(MicroInstr i);
   return i.f1 == F1Constant || i.f2 == F2Constant;
endfunction

function Bool bsUsesConstant(BusSource bs);
   // Constant ROM is also gated when BS>=4 (ContrAlto BS4), so MD/MOUSE/DISP
   // (and task-2) can AND a mask onto the bus.
   return pack(bs) >= 4;
endfunction

function Bit#(8) constantAddr(RSel rsel, BusSource bs);
   return {rsel, pack(bs)};
endfunction

function MemOp memOpOf(MicroInstr i);
   Bool constA = constantAccess(i);
   if (i.f1 == F1LoadMAR) return MemLoadAddr;
   else if (i.bs == BsReadMD && !constA) return MemRead;
   else if (i.f2 == F2StoreMD) return MemStore;
   else return MemNone;
endfunction

function Bool needsMemory(MicroInstr i) = memOpOf(i) != MemNone;

function Bool needsShifter(MicroInstr i);
   return i.f2 == F2ShLt0 || i.f2 == F2ShEq0 || pack(i.f2) == fromInteger(emuLoadDNS);
endfunction

// Memory map.
Word ramTop      = 16'hFDFF;   // 176777
Word utilIn      = 16'hFE18;   // 177030 mouse/keyset
Word kbdBase     = 16'hFE1C;   // 177034 keyboard
Word eiaLoc      = 16'hFFC1;   // 177701 interval timer / EIA
Word xmBankBase  = 16'hFFE0;   // 177740 XM bank registers

// Diablo 31 geometry. Record offsets are the hardware preamble +
// inter-record gaps (header delay 21 words, inter-record 4; sync at
// 44 / 58 / 78). 347 is the word-timeslice length of one sector.
Integer diabloCylinders   = 203;
Integer diabloHeads       = 2;
Integer diabloSectors     = 12;
Integer headerOffset      = 44;
Integer labelOffset       = 58;    // 44+14
Integer dataOffset        = 78;    // 58+20
Integer sectorWordCount   = 347;   // 269+44+34

// KSTAT fields from HW manual §6.0 (Alto bit 0 = MSB).
// S[0-3] sector, S[4-7] = 17B, S[8] seek fail, S[9] seek in progress,
// S[10] not ready, S[11] seclate, S[12] idle, S[13] checksum,
// S[14-15] completion (0 ok, 1 hw, 2 check, 3 illegal sector).
Word kstatS47      = 16'h0F00;
Word kstatSECLATE  = 16'h0010;
Word kstatNOTREADY = 16'h0020;
Word kstatSTROBE   = 16'h0040;
Word kstatSEEKFAIL = 16'h0080;

// Alto clock ≈ 170 ns (HW manual §2.0).
// Diablo 31: 40 ms/rev, 12 sectors → 3.33 ms/sector / 347 words ≈ 56 clocks.
Integer diskWordCycles    = 56;
// SECLATE is ~86 µs after the sector pulse if KSEC has not run.
Integer diskSeclateCycles = 505;
// Seek is the one sim concession: real Diablo 31 is ~15 ms/track
// (~88k clocks). Full-stroke seeks would dominate Bluesim runtime.
Integer diskSeekCycles    = 40;

Integer dispWordCycles    = 5;
Integer dispHBlankCycles  = 36;
Integer dispScanCycles    = 224;
Integer dispVBlankLines   = 34;
Integer dispScanlineWords = 38;
Integer dispVisibleLines  = 808;

Integer etherHostAddress  = 66;    // 102 octal, a conventional Alto host #

endpackage
