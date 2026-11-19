// PimTypes.bsv -- word, tag, register, instruction and microinstruction
// encodings for the PIM/m processing-element model.
//
// Sources for the architectural shape (everything cited "p.NN" is the
// printed page of Nakashima et al., "Architecture and Implementation of
// PIM/m", in FGCS '92 Proceedings vol. 1, PDF pp. 458-468 in
// docs/FGCS92_Volume_1.pdf):
//
//   * 40-bit word, 8-bit tag                        p.426 (PU figure 5 note)
//   * MRB is one bit of the tag                     pp.429-430 (3.1)
//   * An/Xn register file, WR control registers     p.427 (2.3)
//   * PC and SP are hardware counters               p.427 (2.3)
//   * 32K x 64-bit writable control store           p.426 (2.2)
//   * five stages D, A, R, S, E                     p.428 (2.3, figure 5)
//   * MAR1/2, MDR1/2, XR/YR                         p.428 (2.3)
//   * tag-check jumps: two-way, three-way, multi-way p.428 (2.4)
//   * pipelined dereference, SRP and COL            pp.428-430 (2.4, 3.1)
//
// NOT DOCUMENTED in the acquired sources, and therefore model-defined
// here (marked MODEL below): the 8-bit tag's type-field layout, the
// register counts, the instruction word layout, the 64-bit
// microinstruction layout, the decode-table entry layout, and the
// jump-table offset encoding.  The 1992 paper gives the word width and
// the mechanism, not the bit assignments.  See docs/architecture.md
// "Evidence status" for the gap list.
//
// The model's local store is 64K words, not the documented 16M words
// (p.426), so that a Bluesim image is small; Addr is the scaled address
// type and every place that matters is parameterized by it.

package PimTypes;

import RegFile::*;

// ---------------------------------------------------------------------
// Words and tags
// ---------------------------------------------------------------------

typedef Bit#(40) Word;
typedef Bit#(32) Data;
typedef Bit#(8)  Tag;
typedef Bit#(7)  TagType;

// MODEL: tag[0] = MRB, tag[7:1] = type.  The documents fix only the
// width (8 bits) and the existence of MRB.
TagType tagInt    = 7'd0;
TagType tagAtom   = 7'd1;
TagType tagRef    = 7'd2;   // reference pointer, p.428
TagType tagVar    = 7'd3;   // unbound variable cell, p.429
TagType tagList   = 7'd4;   // list cell, p.429
TagType tagStruct = 7'd5;   // structure, p.430
TagType tagCode   = 7'd6;   // code module identifier, p.432
TagType tagFloat  = 7'd7;

function Tag mkTag(TagType t, Bool mrb) = { t, pack(mrb) };
function TagType tagType(Tag t) = t[7:1];
function Bool tagMRB(Tag t) = t[0] == 1;
function Word mkWord(TagType t, Bool mrb, Data d) = { mkTag(t, mrb), d };
function Word wordInt(Data d) = mkWord(tagInt, False, d);
function Data wordData(Word w) = w[31:0];
function Tag wordTag(Word w) = w[39:32];

// ---------------------------------------------------------------------
// Addresses, microprogram counter, register selectors
// ---------------------------------------------------------------------

typedef Bit#(16) Addr;       // MODEL: scaled from the documented 16M words
typedef Bit#(15) UPc;        // 32K-word WCS, p.426
typedef Bit#(8)  Opcode;
typedef Bit#(6)  RegSel;

// Register space used by microcode.  0-15 An, 16-31 Xn, 32-39 the WR
// control registers of p.427, 40 SP, 41 PC, 42-47 the E-stage
// temporaries of p.428.  48-53 are source-only pseudo-selectors.
RegSel rselA0   = 6'd0;
RegSel rselX0   = 6'd16;
RegSel rselAp   = 6'd32;
RegSel rselCgp  = 6'd33;
RegSel rselGsp  = 6'd34;
RegSel rselSst  = 6'd35;
RegSel rselHp   = 6'd36;
RegSel rselFvp  = 6'd37;
RegSel rselFlp  = 6'd38;
RegSel rselFgp  = 6'd39;
RegSel rselSp   = 6'd40;
RegSel rselPc   = 6'd41;
RegSel rselMar1 = 6'd42;
RegSel rselMar2 = 6'd43;
RegSel rselMdr1 = 6'd44;
RegSel rselMdr2 = 6'd45;
RegSel rselXr   = 6'd46;
RegSel rselYr   = 6'd47;

RegSel rselImm   = 6'd48;   // zero-extended 16-bit micro immediate
RegSel rselRs    = 6'd49;   // instruction rs operand
RegSel rselRt    = 6'd50;   // instruction rt operand
RegSel rselRd    = 6'd51;   // instruction rd operand
RegSel rselFetch = 6'd52;   // word fetched by the R stage
RegSel rselDeref = 6'd53;   // word resolved by the S stage
RegSel rselNone  = 6'd63;   // no destination

// Instruction register fields are 5 bits: 0-15 An, 16-31 Xn.
function RegSel regFieldToSel(Bit#(5) r) = zeroExtend(r);

// ---------------------------------------------------------------------
// Machine instruction (MODEL encoding, see header)
//   [39:32] opcode  [31:27] rd  [26:22] rs  [21:17] rt  [16:0] imm
// ---------------------------------------------------------------------

typedef struct {
  Opcode   op;
  Bit#(5)  rd;
  Bit#(5)  rs;
  Bit#(5)  rt;
  Bit#(17) imm;
} Instr deriving (Bits, Eq);

function Instr unpackInstr(Word w) = Instr {
  op:  w[39:32],
  rd:  w[31:27],
  rs:  w[26:22],
  rt:  w[21:17],
  imm: w[16:0]
};

function Word packInstr(Instr i) = { i.op, i.rd, i.rs, i.rt, i.imm };

// MODEL opcodes.  KL1-B's actual encoding is not in the acquired
// corpus (the paper names the instruction set and cites Kimura and
// Chikayama 1987, which is not in docs/); this table is the model's
// own, and docs/architecture.md records the gap.
Opcode opNop     = 8'h00;
Opcode opHalt    = 8'h01;
Opcode opPutImm = 8'h02;
Opcode opPutReg = 8'h03;
Opcode opGetArg = 8'h04;
Opcode opAdd     = 8'h05;
Opcode opSub     = 8'h06;
Opcode opMove    = 8'h07;
Opcode opLoad    = 8'h08;
Opcode opStore   = 8'h09;
Opcode opDeref   = 8'h0A;
Opcode opSetMrb = 8'h0B;
Opcode opClrMrb = 8'h0C;
Opcode opJmp     = 8'h0D;
Opcode opJmpTag = 8'h0E;

// ---------------------------------------------------------------------
// Decode-table entry (the D stage's RAM decoder, p.428).
// MODEL packing: [19:5] microprogram base, [4] valid, [3] needsEA,
// [2] isLoad, [1] isStore, [0] deref.
// ---------------------------------------------------------------------

typedef struct {
  UPc  uBase;
  Bool valid;
  Bool needsEA;
  Bool isLoad;
  Bool isStore;
  Bool deref;
} DecodeEntry deriving (Bits, Eq);

function DecodeEntry unpackDecode(Bit#(20) x) = DecodeEntry {
  uBase:   x[19:5],
  valid:   x[4] == 1,
  needsEA: x[3] == 1,
  isLoad:  x[2] == 1,
  isStore: x[1] == 1,
  deref:   x[0] == 1
};

function Bit#(20) packDecode(DecodeEntry d) =
  { d.uBase, pack(d.valid), pack(d.needsEA), pack(d.isLoad),
    pack(d.isStore), pack(d.deref) };

typedef struct {
  Instr       instr;
  DecodeEntry dec;
} DecodedInstr deriving (Bits, Eq);

// ---------------------------------------------------------------------
// Microinstruction (MODEL encoding, see header).
//   [63:49] next   [48:33] imm   [32:29] aluOp   [28:23] srcA
//   [22:17] srcB   [16:11] dst   [10:9]  memOp   [8:6]   cond
//   [5] deref [4] halt [3] mrbSet [2] mrbClr [1] last [0] branch
// ---------------------------------------------------------------------

typedef Bit#(4) AluOp;
AluOp aluAdd     = 4'd0;
AluOp aluSub     = 4'd1;
AluOp aluAnd     = 4'd2;
AluOp aluOr      = 4'd3;
AluOp aluXor     = 4'd4;
AluOp aluMov     = 4'd5;
AluOp aluShl     = 4'd6;
AluOp aluShr     = 4'd7;
AluOp aluEq      = 4'd8;
AluOp aluNe      = 4'd9;
AluOp aluTagSet = 4'd10;   // set MRB, p.429
AluOp aluTagClr = 4'd11;   // clear MRB, p.429
AluOp aluNeg     = 4'd12;

typedef Bit#(2) MemOp;
MemOp memNone  = 2'd0;
MemOp memRead  = 2'd1;
MemOp memWrite = 2'd2;

typedef Bit#(3) Cond;
Cond condAlways     = 3'd0;
Cond condNever      = 3'd1;
Cond condTagEq     = 3'd2;  // tag(srcA) == instruction imm[6:0]
Cond condTagNe     = 3'd3;
Cond condTagRef    = 3'd4;
Cond condTagNotRef = 3'd5;
Cond condMultiway   = 3'd6;  // uPC + jumpTable[tag(srcA)]
Cond condZero       = 3'd7;

function Bool isTagCond(Cond c) =
  c == condTagEq || c == condTagNe || c == condTagRef ||
  c == condTagNotRef || c == condMultiway;

typedef struct {
  UPc    next;
  Bit#(16) imm;
  AluOp  aluOp;
  RegSel srcA;
  RegSel srcB;
  RegSel dst;
  MemOp  memOp;
  Cond   cond;
  Bool   deref;
  Bool   halt;
  Bool   mrbSet;
  Bool   mrbClr;
  Bool   last;
  Bool   branch;   // taken condition writes PC from the instruction's rt
} MicroInstr deriving (Bits, Eq);

function MicroInstr unpackMicro(Bit#(64) x) = MicroInstr {
  next:   x[63:49],
  imm:    x[48:33],
  aluOp:  x[32:29],
  srcA:   x[28:23],
  srcB:   x[22:17],
  dst:    x[16:11],
  memOp:  x[10:9],
  cond:   x[8:6],
  deref:  x[5] == 1,
  halt:   x[4] == 1,
  mrbSet: x[3] == 1,
  mrbClr: x[2] == 1,
  last:   x[1] == 1,
  branch: x[0] == 1
};

function Bit#(64) packMicro(MicroInstr m) =
  { m.next, m.imm, m.aluOp, m.srcA, m.srcB, m.dst, m.memOp, m.cond,
    pack(m.deref), pack(m.halt), pack(m.mrbSet), pack(m.mrbClr),
    pack(m.last), pack(m.branch) };

// ---------------------------------------------------------------------
// Pipeline bundles
// ---------------------------------------------------------------------

typedef struct {
  Instr       instr;
  DecodeEntry dec;
  Bool        valid;
} D2A deriving (Bits, Eq);

typedef struct {
  Instr       instr;
  DecodeEntry dec;
  Addr        ea;
  Word        rsVal;
  Word        rtVal;
  Word        rdVal;
  Bool        valid;
} A2R deriving (Bits, Eq);

typedef struct {
  Instr       instr;
  DecodeEntry dec;
  Addr        ea;
  Word        rsVal;
  Word        rtVal;
  Word        rdVal;
  Word        fetched;
  Bool        valid;
} R2S deriving (Bits, Eq);

typedef struct {
  Instr       instr;
  DecodeEntry dec;
  Addr        ea;
  Word        rsVal;
  Word        rtVal;
  Word        rdVal;
  Word        fetched;
  Word        derefVal;
  Bool        srp;
  Bool        col;
  Bool        valid;
} S2E deriving (Bits, Eq);

endpackage
