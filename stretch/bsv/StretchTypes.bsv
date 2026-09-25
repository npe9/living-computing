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
  Bit#(2)  spare;  // IBM bits 26-27 -- see below
  Bit#(18) count;  // IBM bits 28-45
  Bit#(18) refill; // IBM bits 46-63
} IndexWord deriving (Bits, Eq, FShow);

// IBM BITS 26-27 ARE NOT USED BY THE INDEX MACHINERY AND ARE STILL
// CARRIED, which is not a tidiness point -- `spare` was added because a
// diagnostic failed without it.  packIndexWord used to write 2'b00
// there, so every LX-then-SX round trip through an index register
// quietly rewrote those two bits.
//
// I-Box 3's routine 1222 (jb_ax3a p.144) puts a FLOATING POINT LOAD
// into an index register with LX, stores it into a work area with SX,
// and then does SVA into it -- and its comment names exactly what it
// depends on: "A FP INSTRUCT BITS 26 AND 27 OF WHICH ARE 10".  Those
// two bits are part of the operation code that makes the half-word
// decode as floating point.  Zeroed, the template decoded as a
// branch-on-indicator instead, SVA used a 19-bit address field instead
// of 18, and the deck's "STORES BIT 18" check fired.
//
// An index register lives in index core storage, which is ordinary
// 64-bit words; LX loads the whole word and SX stores the whole word.
// The deck relies on that, so the round trip has to be lossless.

function IndexWord unpackIndexWord(Word64 w);
  return IndexWord {
    addr:   w[63:40], // bits 0-23
    sign:   w[39:39], // bit 24
    flag:   w[38:38], // bit 25
    spare:  w[37:36], // bits 26-27, unused by the index machinery but
                      // preserved: see the note on IndexWord above
    count:  w[35:18], // bits 28-45
    refill: w[17:0]   // bits 46-63
  };
endfunction

function Word64 packIndexWord(IndexWord x);
  return { x.addr, x.sign, x.flag, x.spare, x.count, x.refill };
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
// 14 is skipped here.  It is not a gap in the transcription: jb_ax5b
// routine 1260's four 48-entry error tables (PDF pp.45-59) print all
// 48 indicator names in order, and THE DECK NAMES 14 "RESRVD".  Read
// straight through, those tables give MK IK IJ EK TS CPUS EKJ UNRJ CBJ
// EPGK UK EE EOP CS RESRVD OP AD USA EXE DS DF IF LC PF ZD IR LS PSH
// XPFP XPO XPH XPL XPU ZM RU TF UF VF XF BTR DTR PG0..PG6 -- which is
// this table exactly, and is a free 48-way cross-check of it.
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
// Floating-point operation codes, IBM bits 5-11 of the instruction.
// These are the same twenty-nine codes the assembler carries in
// strap/opcodes.py FP_CODES, and the identifier keeps the machine's own
// mnemonic so a listing row and a case arm read alike ("*+" is
// fpop_STAR_PLUS, "R/" is fpop_R_SLASH).
//
// They existed as bare 7-bit literals in three places that each wrote
// the whole set out by hand -- isValidFpCode in StretchDecode, the
// `known` disjunction in StretchExecute, and the dispatch arms
// themselves.  The three agreed, but three hand-maintained copies of a
// twenty-nine element set is a drift generator, and the mnemonic was
// carried only in a trailing comment.
// ---------------------------------------------------------------------
Bit#(7) fpop_PLUS        = 7'b0000010;   // +
Bit#(7) fpop_L           = 7'b0000110;   // L
Bit#(7) fpop_M_PLUS      = 7'b0001010;   // M+
Bit#(7) fpop_ST          = 7'b0001110;   // ST
Bit#(7) fpop_K           = 7'b0010010;   // K
Bit#(7) fpop_KR          = 7'b0010110;   // KR
Bit#(7) fpop_STAR        = 7'b0011010;   // *
Bit#(7) fpop_SLASH       = 7'b0011110;   // /
Bit#(7) fpop_PLUS_MG     = 7'b0100010;   // +MG
Bit#(7) fpop_LWF         = 7'b0100110;   // LWF
Bit#(7) fpop_M_PLUS_MG   = 7'b0101010;   // M+MG
Bit#(7) fpop_SRD         = 7'b0101110;   // SRD
Bit#(7) fpop_KMG         = 7'b0110010;   // KMG
Bit#(7) fpop_KMGR        = 7'b0110110;   // KMGR
Bit#(7) fpop_STAR_PLUS   = 7'b0111010;   // *+
Bit#(7) fpop_R_SLASH     = 7'b0111110;   // R/
Bit#(7) fpop_D_PLUS      = 7'b1000010;   // D+
Bit#(7) fpop_DL          = 7'b1000110;   // DL
Bit#(7) fpop_LFT         = 7'b1001010;   // LFT
Bit#(7) fpop_SLO         = 7'b1001110;   // SLO
Bit#(7) fpop_F_PLUS      = 7'b1010010;   // F+
Bit#(7) fpop_E_PLUS      = 7'b1010110;   // E+
Bit#(7) fpop_D_STAR      = 7'b1011010;   // D*
Bit#(7) fpop_D_SLASH     = 7'b1011110;   // D/
Bit#(7) fpop_D_PLUS_MG   = 7'b1100010;   // D+MG
Bit#(7) fpop_DLWF        = 7'b1100110;   // DLWF
Bit#(7) fpop_SRT         = 7'b1101110;   // SRT
Bit#(7) fpop_SHF         = 7'b1110010;   // SHF
Bit#(7) fpop_E_PLUS_I    = 7'b1110110;   // E+I

// ---------------------------------------------------------------------
// Direct index-arithmetic operation codes, IBM bits 23-27, and the
// three CONNECTIVE suffixes, IBM bits 55-59.  Both fields are five
// bits wide and THREE OF THE PATTERNS COLLIDE:
//
//     00111   LR   (direct index)   /   C    (connective)
//     01111   V+CR (direct index)   /   CM   (connective)
//     10111   SR   (direct index)   /   CT   (connective)
//
// As bare literals, grepping for one of a pair finds the other -- and
// 5'b01111 in particular appeared eleven times across three files,
// meaning CM in most of them and V+CR in the rest.  Naming them is the
// only way to tell those apart at a glance.
// ---------------------------------------------------------------------
Bit#(5) dixop_LX         = 5'b00001;   // LX
Bit#(5) dixop_LV         = 5'b00011;   // LV
Bit#(5) dixop_LC         = 5'b00101;   // LC
Bit#(5) dixop_LR         = 5'b00111;   // LR
Bit#(5) dixop_KV         = 5'b01001;   // KV
Bit#(5) dixop_V_PLUS     = 5'b01011;   // V+
Bit#(5) dixop_V_PLUS_C   = 5'b01101;   // V+C
Bit#(5) dixop_V_PLUS_CR  = 5'b01111;   // V+CR
Bit#(5) dixop_SX         = 5'b10001;   // SX
Bit#(5) dixop_SV         = 5'b10011;   // SV
Bit#(5) dixop_SC         = 5'b10101;   // SC
Bit#(5) dixop_SR         = 5'b10111;   // SR
Bit#(5) dixop_KC         = 5'b11001;   // KC
Bit#(5) dixop_LVE        = 5'b11011;   // LVE
Bit#(5) dixop_SVA        = 5'b11101;   // SVA
Bit#(5) dixop_RNX        = 5'b11111;   // RNX

Bit#(5) conn_C  = 5'b00111;   // C  -- result replaces the accumulator field
Bit#(5) conn_CM = 5'b01111;   // CM -- result replaces the storage field
Bit#(5) conn_CT = 5'b10111;   // CT -- result discarded, indicators only

// Format markers.  Both are 5'b10000 but in different fields, which is
// why they are named apart rather than shared.
Bit#(5) litIoOp     = 5'b10000;   // IBM 55-59: the I/O format marker
Bit#(5) litImmIndex = 5'b10000;   // IBM 23-27: the immediate-index marker

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

// The VflInt payload, named rather than anonymous so the arm that
// handles it can be lifted out of execute() into a function that
// takes it whole.  Connective and the rest stay anonymous until
// they need the same.
typedef struct { VflAddr a; VflMod m; Bit#(6) code; } VflInstr
  deriving (Bits, Eq, FShow);

// The Connective payload, named for the same reason VflInstr is: its
// arm is lifted out of execute() and has to be passed whole.  The two
// share VflAddr, which is what let progressiveIndex serve both.
typedef struct { VflAddr a; Bit#(4) conn; Bit#(5) suffix; } ConnInstr
  deriving (Bits, Eq, FShow);

// The DirIndex payload, named so its arm can leave execute() too.
typedef struct { HWordAddr addr; Bit#(4) j; Bit#(5) code; Bit#(4) idx; } DixInstr
  deriving (Bits, Eq, FShow);

// The ImmIndex payload.  Its arm's boundary turns out to be identical
// to DirIndex's, so both return the same IndexOutcome.
typedef struct { HWordAddr imm; Bit#(4) j; Bit#(4) code; } ImmInstr
  deriving (Bits, Eq, FShow);

// The IoOp payload.  Its arm is the only one that reaches the I/O
// interface, so it is the only one whose extracted function takes a
// StretchIO as well as a StretchStorage.
typedef struct { BitAddr addr1; Bit#(4) i1; WordAddr addr2; Bit#(4) op; Bit#(4) i2; } IoInstr
  deriving (Bits, Eq, FShow);

typedef union tagged {
  // Integer arithmetic / radix conversion, Figure 6 "INTEGER" row,
  // p.18; opcode field IBM bits 51-59 = abc(3)+code(6), pocket card
  // "INTEGER ARITHMETIC" table.
  VflInstr VflInt;

  // Connectives (16 boolean functions), same shape, opcode field
  // CONN(4, bits 51-54) + suffix(5, bits 55-59).
  ConnInstr Connective;

  // Floating point, Figure 6 "FLOATING POINT" row: half-word,
  // ADDRESS[0:17] (18b, a full-word address -- FP operands are always
  // full words, p.19-20) + abc+code[18:27] (10 bits, matches
  // pocket-card mnemonic table exactly) + I[28:31].
  struct { WordAddr addr; Bit#(1) unnorm; Bit#(1) absSign; Bit#(1) invSign;
           Bit#(7) code; Bit#(4) idx; } Fp;

  // Direct index arithmetic, Figure 6 "DIRECT INDEX" row: half-word,
  // ADDRESS[0:18](19b) + J[19:22] + OP[23:27](5b) + I[28:31].
  DixInstr DirIndex;

  // Immediate index arithmetic, Figure 6 "IMMEDIATE INDEX" row:
  // ADDRESS[0:18](19b, the immediate value) + J[19:22] + lit"10000"[23:27]
  // + OP[28:31](4b).
  ImmInstr ImmIndex;

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
  //
  // `swap` is IBM bit 57.  It used to be MISSING here, and the decoder
  // matched sub-ops 010 (Transmit) and 110 (Swap) in one condition
  // without recording which -- so a SWAP executed as a forward
  // one-word Transmit, silently, while bsv/README.md and
  // StretchExecute.bsv's own header both claimed it set indicator 15.
  // Unreachable from STRAP until strap_asm gained TRANSMIT_CODES on
  // 2026-09-22, and demonstrated that day: "SWAPI,1,SRC,DST" left SRC
  // alone and copied it into DST (0x9249249249249249), OP clear.
  // Reference Manual pp.30-31: modifier bits 55-57 are 57 =
  // bidirectional (swap), 56 = immediate count, 55 = backward.
  struct { BitAddr addr1; Bit#(4) i1; HWordAddr addr2; Bit#(4) j;
           Bit#(1) backward; Bit#(1) immCount; Bit#(1) swap;
           Bit#(4) i2; } Transmit;

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
  IoInstr IoOp;
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
  Maybe#(WordAddr) storeAddr;   // the word this E-box level stores to (ST/M+),
                                // so a younger load of that word waits for it
                                // (store-close-to-fetch, plan stage 3a note)
} LaLevel deriving (Bits, Eq, FShow);

endpackage
