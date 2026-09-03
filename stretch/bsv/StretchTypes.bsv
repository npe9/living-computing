// StretchTypes.bsv
//
// Basic types for an IBM 7030 "Stretch" implementation.
//
// SOURCE: IBM 7030 Data Processing System Reference Manual, Form 22-6530-2
// (bitsavers.org/pdf/ibm/7030/22-6530-2_7030RefMan.pdf), especially
// Figure 6 "Instruction Formats" (p.18) and the "Operand Designation"
// chapter (pp.19-26); cross-checked against the IBM 7030 Reference Card,
// Form X22-6533-1 (bitsavers.org/pdf/ibm/7030/X22-6533_7030_PocketCard.pdf).
//
// BIT NUMBERING CONVENTION
// -------------------------
// IBM numbers bits left to right, MSB = bit 0. BSV/Verilog vectors number
// bits right to left, LSB = index 0. For a Bit#(64) word `w`, IBM bit `i`
// is BSV index `63-i`. An IBM field spanning bits [a,b) (a <= i < b, i.e.
// manual notation "bits a-(b-1)") is therefore the BSV slice
// w[63-a : 64-b]. Each extraction function below cites the IBM bit range
// it implements so the two numbering schemes never have to be mixed by
// the reader.

package StretchTypes;

// ---------------------------------------------------------------------
// Fundamental storage types
// ---------------------------------------------------------------------

typedef Bit#(64) Word64;      // one storage word (IBM bits 0-63)
typedef Bit#(32) HalfWord32;  // one instruction half-word (IBM bits 0-31)

typedef Bit#(18) WordAddr;    // word address (262,144 words max)
typedef Bit#(19) HWordAddr;   // half-word address (word addr . half select)
typedef Bit#(24) BitAddr;     // bit address = 18-bit word addr + 6-bit offset

// Split a 24-bit bit address into its word and in-word-bit parts.
// SOURCE: p.19 "The 18 high-order bits address full words. The six
// low-order bits address the bit in the addressed word which corresponds
// to the left end of the field."
function WordAddr baWord(BitAddr ba) = ba[23:6];
function Bit#(6)  baBit(BitAddr ba)  = ba[5:0];

function BitAddr mkBitAddr(WordAddr w, Bit#(6) bit_) = {w, bit_};

// ---------------------------------------------------------------------
// Special Storage Assignment (IBM 7030 Reference Card, "SPECIAL STORAGE
// ASSIGNMENT" table). The register file *is* memory: these are ordinary
// word addresses that happen to be wired to CPU registers instead of
// core storage cells.
// ---------------------------------------------------------------------

WordAddr addrZero            = 0;   // permanently 0, writes ignored
WordAddr addrIntervalTimer   = 1;   // bits 0-18, permanently protected
WordAddr addrTimeClock       = 1;   // bits 28-63, read-only, same word as timer
WordAddr addrInterruptAddr   = 2;   // bits 0-17, permanently protected
WordAddr addrUpperBoundary   = 3;   // bits 0-17
WordAddr addrLowerBoundary   = 3;   // bits 32-49
WordAddr addrBoundaryCtlBit  = 3;   // bit 57
WordAddr addrMaintenanceBits = 4;
WordAddr addrChannelAddress  = 5;   // bits 12-18, read-only
WordAddr addrOtherCpuBits    = 6;   // bits 0-18
WordAddr addrLeftZerosCount  = 7;   // bits 17-23
WordAddr addrAllOnesCount    = 7;   // bits 44-50
WordAddr addrAccLeft         = 8;   // Left Half of Accumulator, 64 bits
WordAddr addrAccRight        = 9;   // Right Half of Accumulator, 64 bits
WordAddr addrAccSignByte     = 10;  // bits 0-7
WordAddr addrIndicators      = 11;  // bits 0-19 read-only
WordAddr addrMask            = 12;  // bits 0-19 always 1, 48-63 always 0
WordAddr addrRemainder       = 13;
WordAddr addrFactor          = 14;
WordAddr addrTransit         = 15;
WordAddr addrIndexBase       = 16;  // X0..X15 at 16..31

function WordAddr addrIndex(Bit#(4) j) = zeroExtend(j) + addrIndexBase;

// ---------------------------------------------------------------------
// Index / control word layout (Figure 6, "INDEX WORD FORMAT",
// confirmed against prose on p.19: "the value field is leftmost... 25
// bits... interpreted as an address of 24 bits and a sign bit... index
// flag bit is adjacent to the value sign bit... two bits ... not used").
//
//   VALUE(0-24: addr[0:23]+sign[24]) | FLAG(25) | unused(26-27) |
//   COUNT(28-45) | REFILL(46-63)
//
// Externally confirmed against IBM's own assembler output: the I-Box 4
// listing (docs/jb_ax4b_ibox-4.pdf pp.155/159) prints its XW index
// words, and strap/verify_ibox4_listing.py matches this packing to
// them bit for bit (count=4 -> bit 43 set; refill = a word address in
// 46-63, e.g. IBRA10's own 011610). See strap/README.md "Gotchas" 15.
// ---------------------------------------------------------------------

typedef struct {
  Bit#(24) addr;   // IBM bits 0-23
  Bit#(1)  sign;   // IBM bit 24
  Bit#(1)  flag;   // IBM bit 25 (index flag XF)
  Bit#(18) count;  // IBM bits 28-45
  Bit#(18) refill; // IBM bits 46-63
} IndexWord deriving (Bits, Eq, FShow);

function IndexWord unpackIndexWord(Word64 w);
  return IndexWord {
    addr:   w[63:40], // bits 0-23
    sign:   w[39:39], // bit 24
    flag:   w[38:38], // bit 25
    count:  w[35:18], // bits 28-45
    refill: w[17:0]   // bits 46-63
  };
endfunction

function Word64 packIndexWord(IndexWord x);
  return { x.addr, x.sign, x.flag, 2'b00, x.count, x.refill };
endfunction

// Signed 25-bit value field (24-bit magnitude + sign), per p.21:
// "The value field of the index is interpreted as a signed 24-bit
// field" combined with a sign bit (sign-and-magnitude, matching the
// rest of the architecture -- see StretchALU.bsv).
function Int#(25) indexValue(IndexWord x);
  Bit#(25) mag = {1'b0, x.addr};
  return unpack(x.sign == 1 ? (~mag + 1) : mag); // treat as 2's-complement
                                                  // container for arithmetic;
                                                  // see StretchALU for the
                                                  // sign-magnitude ALU used
                                                  // on VFL storage fields.
endfunction

// ---------------------------------------------------------------------
// Floating point word layout (Figure 5, "Floating Point Data Format",
// p.19): 12-bit exponent (flag+10+sign), 52-bit fraction (48+4-bit sign
// byte, of which 3 bits are the T/U/V data flags).
// ---------------------------------------------------------------------

typedef struct {
  Bit#(1)  expFlag; // IBM bit 0
  Bit#(10) exp;     // IBM bits 1-10
  Bit#(1)  expSign; // IBM bit 11
  Bit#(48) frac;    // IBM bits 12-59
  Bit#(4)  fracSignByte; // IBM bits 60-63 (bit 63 = sign; 60-62 = T,U,V)
} FpWord deriving (Bits, Eq, FShow);

function FpWord unpackFpWord(Word64 w);
  return FpWord {
    expFlag: w[63:63],
    exp:     w[62:53],
    expSign: w[52:52],
    frac:    w[51:4],
    fracSignByte: w[3:0]
  };
endfunction

function Word64 packFpWord(FpWord x);
  return { x.expFlag, x.exp, x.expSign, x.frac, x.fracSignByte };
endfunction

// ---------------------------------------------------------------------
// Control word layout (Reference Manual p.107 Figure 35, "Control Word
// and Index Word Formats"): the format an input-output instruction's
// right effective address points at in core storage, and what the
// simulated exchange (StretchIO.bsv) tracks per channel while a
// transfer is in progress. "Follows that of an index word" per p.106,
// but is NOT the same layout -- the data word address is a plain
// 18-bit word address (no sign bit, unlike an index word's 24-bit+sign
// value field), and bits 18-27 are status/flag bits an index word
// doesn't have. See StretchIO.bsv's file header for which of the
// status bits this implementation actually drives.
// ---------------------------------------------------------------------

typedef struct {
  WordAddr dataAddr;  // IBM bits 0-17
  Bit#(1) unitReady;  // IBM bit 18
  Bit#(1) epgk;       // IBM bit 19, Exchange Program Check
  Bit#(1) uk;         // IBM bit 20, Unit Check
  Bit#(1) ee;         // IBM bit 21, End Exception
  Bit#(1) eop;        // IBM bit 22, End of Operation
  Bit#(1) cs;         // IBM bit 23, Channel Signal
  Bit#(1) seop;       // IBM bit 24, Suppress End of Operation
  Bit#(1) chain;      // IBM bit 25
  Bit#(1) multiple;   // IBM bit 26
  Bit#(1) skip;       // IBM bit 27
  Bit#(18) count;     // IBM bits 28-45
  Bit#(18) refill;    // IBM bits 46-63
} ControlWord deriving (Bits, Eq, FShow);

function ControlWord unpackControlWord(Word64 w);
  return ControlWord {
    dataAddr:  w[63:46],
    unitReady: w[45:45],
    epgk:      w[44:44],
    uk:        w[43:43],
    ee:        w[42:42],
    eop:       w[41:41],
    cs:        w[40:40],
    seop:      w[39:39],
    chain:     w[38:38],
    multiple:  w[37:37],
    skip:      w[36:36],
    count:     w[35:18],
    refill:    w[17:0]
  };
endfunction

function Word64 packControlWord(ControlWord c);
  return { c.dataAddr, c.unitReady, c.epgk, c.uk, c.ee, c.eop, c.cs, c.seop,
           c.chain, c.multiple, c.skip, c.count, c.refill };
endfunction

// A started-but-not-yet-drained input-output word transfer, threaded
// from StretchExecute's IoOp case out to StretchCore.step()'s FSM
// exactly the way progressive indexing's index-register write is
// threaded out via the Maybe#(Tuple2#(...)) already returned by
// execute() -- see StretchCore.bsv for why this has to be a multi-cycle
// FSM rather than a loop of st.writeWord calls inside execute() itself
// (bsv/README.md "Toolchain": one write per register per rule).
typedef struct {
  WordAddr ch;        // channel address (StretchIO.chanReader/chanPrinter)
  Bool isWrite;        // False = RD (device -> memory), True = W (memory -> device)
  WordAddr memAddr;    // next core-storage word address to move
  Bit#(6)  devIdx;      // next device-image word index to move, ONE BIT
                          // WIDER than StretchIO.DeviceIndex (TLog#(32)=5)
                          // deliberately: DeviceWords==32 exactly fills a
                          // 5-bit index, leaving no representable value
                          // for "one past the end" to detect device
                          // exhaustion against -- see StretchCore.bsv's
                          // ioPending FSM, which truncates this back to
                          // DeviceIndex only after confirming it's < 32
  Bit#(19) remaining;   // words still to transfer, counting this one
                          // (Bit#(19) to represent the p.107 "count field
                          // zero means 2^18" case without overflow)
  Bool suppressEop;     // SEOP: don't set the EOP status bit on completion
  Bool skip;             // control word's SKIP flag (p.107): on a READ,
                          // still advance the device cursor and memAddr
                          // each cycle but do NOT write core storage --
                          // meaningless on WRITE (manual: ignored), so
                          // execute() only ever sets this True for RD
} IoXfer deriving (Bits, Eq, FShow);

// ---------------------------------------------------------------------
// Indicators (IBM 7030 Reference Card, "INDICATOR LIST", 64 named
// bits). Only a subset is meaningfully driven by this implementation's
// execute stage; the rest are modeled as plain storage so BI (Branch on
// Indicator) and address 11 behave correctly even where the producing
// unit (I/O, floating point, interrupts) is out of scope. See
// bsv/README.md "Scope" section.
// ---------------------------------------------------------------------

Bit#(6) ind_MK   = 0;  Bit#(6) ind_IK   = 1;  Bit#(6) ind_IJ   = 2;
Bit#(6) ind_EK   = 3;  Bit#(6) ind_TS   = 4;  Bit#(6) ind_CPUS = 5;
Bit#(6) ind_EKJ  = 6;  Bit#(6) ind_UNRJ = 7;  Bit#(6) ind_CBJ  = 8;
Bit#(6) ind_EPGK = 9;  Bit#(6) ind_UK   = 10; Bit#(6) ind_EE   = 11;
Bit#(6) ind_EOP  = 12; Bit#(6) ind_CS   = 13;
Bit#(6) ind_OP   = 15; // Operation Code Invalid
Bit#(6) ind_AD   = 16; // Address Invalid
Bit#(6) ind_USA  = 17; Bit#(6) ind_EXE  = 18; Bit#(6) ind_DS   = 19;
Bit#(6) ind_DF   = 20; Bit#(6) ind_IF   = 21; Bit#(6) ind_LC   = 22;
Bit#(6) ind_PF   = 23; Bit#(6) ind_ZD   = 24; Bit#(6) ind_IR   = 25;
Bit#(6) ind_LS   = 26; Bit#(6) ind_PSH  = 27; Bit#(6) ind_XPFP = 28;
Bit#(6) ind_XPO  = 29; Bit#(6) ind_XPH  = 30; Bit#(6) ind_XPL  = 31;
Bit#(6) ind_XPU  = 32; Bit#(6) ind_ZM   = 33; Bit#(6) ind_RU   = 34;
Bit#(6) ind_TF   = 35; Bit#(6) ind_UF   = 36; Bit#(6) ind_VF   = 37;
Bit#(6) ind_XF   = 38; Bit#(6) ind_BTR  = 39; Bit#(6) ind_DTR  = 40;
// 41-47 PG0-PG6
Bit#(6) ind_XCZ  = 48; Bit#(6) ind_XVLZ = 49; Bit#(6) ind_XVZ  = 50;
Bit#(6) ind_XVGZ = 51; Bit#(6) ind_XL   = 52; Bit#(6) ind_XE   = 53;
Bit#(6) ind_XH   = 54; Bit#(6) ind_MOP  = 55; Bit#(6) ind_RLZ  = 56;
Bit#(6) ind_RZ   = 57; Bit#(6) ind_RGZ  = 58; Bit#(6) ind_RN   = 59;
Bit#(6) ind_AL   = 60; Bit#(6) ind_AE   = 61; Bit#(6) ind_AH   = 62;
Bit#(6) ind_NM   = 63;

// ---------------------------------------------------------------------
// Decoded-instruction representation.
//
// Per the advisor guidance captured in bsv/README.md ("decode
// completely, execute partially"): every format in Figure 6 gets a
// constructor here, including ones StretchExecute.bsv does not
// implement. A format that decodes to `Unimplemented` still reports
// its class faithfully; only truly malformed encodings are `Invalid`.
// ---------------------------------------------------------------------

// Variable-field-length operand descriptor shared by VFL and Connective
// formats (Figure 6 "INTEGER" / "CONNECTIVE" rows).
typedef struct {
  BitAddr addr;     // IBM bits 0-23
  Bit#(4) i1;       // IBM bits 28-31 (first index / progressive index reg)
  Bit#(3) p;        // IBM bits 32-34 (progressive indexing mode, p.21)
  Bit#(6) length;   // IBM bits 35-40 (0 means 64)
  Bit#(3) bs;       // IBM bits 41-43 (byte size, 0 means 8)
  Bit#(7) offset;   // IBM bits 44-50 (accumulator offset)
  Bit#(4) i2;       // IBM bits 60-63 (second index field)
} VflAddr deriving (Bits, Eq, FShow);

typedef struct {
  Bit#(1) unsign;   // a: 0=signed, 1=unsigned
  Bit#(1) invert;   // b: 0=same sign, 1=invert
  Bit#(1) decimal;  // c: 0=binary, 1=decimal (NOT IMPLEMENTED, see README)
} VflMod deriving (Bits, Eq, FShow);

typedef union tagged {
  // Integer arithmetic / radix conversion, Figure 6 "INTEGER" row,
  // p.18; opcode field IBM bits 51-59 = abc(3)+code(6), pocket card
  // "INTEGER ARITHMETIC" table.
  struct { VflAddr a; VflMod m; Bit#(6) code; } VflInt;

  // Connectives (16 boolean functions), same shape, opcode field
  // CONN(4, bits 51-54) + suffix(5, bits 55-59).
  struct { VflAddr a; Bit#(4) conn; Bit#(5) suffix; } Connective;

  // Floating point, Figure 6 "FLOATING POINT" row: half-word,
  // ADDRESS[0:17] (18b, a full-word address -- FP operands are always
  // full words, p.19-20) + abc+code[18:27] (10 bits, matches
  // pocket-card mnemonic table exactly) + I[28:31].
  struct { WordAddr addr; Bit#(1) unnorm; Bit#(1) absSign; Bit#(1) invSign;
           Bit#(7) code; Bit#(4) idx; } Fp;

  // Direct index arithmetic, Figure 6 "DIRECT INDEX" row: half-word,
  // ADDRESS[0:18](19b) + J[19:22] + OP[23:27](5b) + I[28:31].
  struct { HWordAddr addr; Bit#(4) j; Bit#(5) code; Bit#(4) idx; } DirIndex;

  // Immediate index arithmetic, Figure 6 "IMMEDIATE INDEX" row:
  // ADDRESS[0:18](19b, the immediate value) + J[19:22] + lit"10000"[23:27]
  // + OP[28:31](4b).
  struct { HWordAddr imm; Bit#(4) j; Bit#(4) code; } ImmIndex;

  // Count and branch, Figure 6 "COUNT AND BRANCH" row: half-word,
  // ADDRESS[0:18](19b) + J[19:22] + V(ab)[23:24] + lit"1001"[25:28] +
  // refill[29] + zeroTest[30] + I[31].
  struct { HWordAddr addr; Bit#(4) j; Bit#(2) v; Bit#(1) refill;
           Bit#(1) branchIfZero; Bit#(1) idx; } CountBranch;

  // Branch on indicator, Figure 6 "BRANCH ON INDICATOR" row: half-word,
  // ADDRESS[0:18](19b) + IND[19:24](6b) + lit"1000"[25:28] +
  // ab[29:30] + I[31].
  struct { HWordAddr addr; Bit#(6) indNum; Bit#(1) clear; Bit#(1) branchOn;
           Bit#(1) idx; } BranchInd;

  // Unconditional branching / miscellaneous, Figure 6 "MISCELLANEOUS"
  // + "DIRECT INDEX ARITHMETIC" adjacent rows: half-word,
  // ADDRESS[0:18](19b) + OP[19:21](3b) + lit(6b) + I[28:31](4b).
  // `misc` distinguishes the two literal-suffix families
  // (000000 = unconditional branch table, 100000 = misc-ops table).
  struct { HWordAddr addr; Bit#(3) code; Bool misc; Bit#(4) idx; } BranchOrMisc;

  // Transmit, Figure 6 "TRANSMIT" row: full word.
  struct { BitAddr addr1; Bit#(4) i1; HWordAddr addr2; Bit#(4) j;
           Bit#(1) backward; Bit#(1) immCount; Bit#(4) i2; } Transmit;

  // Input-Output, Reference Manual "IBM 7619 Exchange" pp.104-127,
  // pocket card "INPUT-OUTPUT OPERATIONS" row: full word,
  // ADDRESS(24,0-23,channel addr in low 7 bits after indexing) +
  // 1000(24-27) + I(28-31) + ADDRESS(18,32-49, second effective addr)
  // + OP(4,51-54) + 10000(55-59) + I(60-63). `op`'s bit 2 (weight 4) is
  // the SEOP flag; the base operation is bits 3,1,0: 000=RD, 001=W,
  // 010=CTL, 011=LOC, 100=CCW, 101=REL (derived from the pocket card's
  // 9-bit codes, e.g. RD=000010000, RDSEOP=010010000, REL=100110000,
  // RELSEOP=110110000 -- cross-checked against an independent reading
  // of the same table). See StretchExecute.bsv's IoOp case for which
  // of these six this implementation executes.
  //
  // Formats this decoder recognizes structurally but does not execute:
  // SIC (Store Instruction Counter If), Bit Branching. Kept distinct
  // (rather than merged into `Unimplemented`) so future work can add
  // execution without re-deriving the format.
  struct { BitAddr addr1; Bit#(4) i1; WordAddr addr2; Bit#(4) op; Bit#(4) i2; } IoOp;
  struct { BitAddr addr; Bit#(4) idx; HalfWord32 inner; } Sic;
  struct { BitAddr addr1; Bit#(4) i1; HWordAddr addr2; Bit#(3) modAbc;
           Bit#(1) idx; } BitBranch;

  // Structurally valid but not (yet) executed by StretchExecute.bsv.
  void Unimplemented;

  // Bit pattern does not correspond to any defined format/opcode.
  void Invalid;
} DecodedInstr deriving (Bits, Eq, FShow);

// Whether a decoded (or about-to-be-decoded) instruction occupies one
// or two half-words. Determined purely from the first half-word, see
// StretchDecode.isFullWordInstr for the citation.
typedef enum { Half, Full } InstrLen deriving (Bits, Eq, FShow);

// One of the instruction unit's two instruction buffers 1Y/2Y
// (StretchCore.bsv IC controls, docs/microarchitecture_plan.md
// stage 2a): the word address it holds or awaits, the word, whether
// a fetch is outstanding (and whether its result is to be discarded),
// and the I-checker countdown before the word may be used.
typedef struct {
  Bool     valid;
  Bool     pending;
  Bool     discard;
  WordAddr addr;
  Word64   data;
  Bit#(2)  chk;
} YReg deriving (Bits, Eq, FShow);

// One look-ahead level (docs/microarchitecture_plan.md stage 3a;
// Buchholz §15.3, Cocke & Kolsky §III.C): the prepared E-box-class
// instruction with its instruction-counter value, the operand
// address the instruction unit determined for it (Invalid for an
// immediate operand), the operand once fetched, whether the fetch
// has been issued, and the earlier level whose retirement this
// level's fetch must wait for (a store to the same word ahead of it).
typedef struct {
  Bool             valid;
  DecodedInstr     di;
  HWordAddr        pc;
  InstrLen         len;
  Maybe#(WordAddr) da;
  Maybe#(Word64)   data;
  Bool             fetchIssued;
  Maybe#(Bit#(2))  waitFor;
  Bool             branch;      // a guessed (not-taken) branch on an arithmetic indicator
  HWordAddr        target;      // its target, computed at preparation
} LaLevel deriving (Bits, Eq, FShow);

endpackage
