// StretchDecode.bsv
//
// Instruction decode for the IBM 7030. See StretchTypes.bsv for the bit-
// numbering convention and DecodedInstr shape, and bsv/README.md for the
// overall scope statement.
//
// DECODE STRATEGY (read before modifying)
// ----------------------------------------
// Figure 6 (22-6530-2, p.18) gives each format's field layout, but it is
// a *programmer's* reference: it shows the bit pattern once you already
// know which named operation you have, not a specification of how the
// 1961 hardware disambiguates arbitrary bit patterns into formats. Two
// facts anchor half/full-word discrimination and full-word sub-format
// discrimination unambiguously (both cited at their point of use below):
// bits 24-27 of a full-word format's first half-word are always the
// literal pattern 1000 (confirmed both from Figure 6 and from the prose
// description of BRANCH ON BIT and STORE INSTRUCTION COUNTER IF), and a
// handful of formats carry their own fixed literal sub-fields.
//
// Beyond that, several half-word formats (DIRECT INDEX, IMMEDIATE
// INDEX, COUNT AND BRANCH, BRANCH ON INDICATOR, the unconditional
// branch / miscellaneous pair) place variable-value operand fields (an
// index register number, an indicator number) at overlapping bit
// positions, and only their *opcode* sub-fields are constrained to a
// known set of values. This decoder therefore resolves half-word
// format ambiguity the way an assembler's disassembler would: try each
// candidate format in turn, and commit to it only if the opcode
// sub-field it would extract is one of the values the pocket card
// (X22-6533-1) actually lists. This decodes every correctly-assembled
// instruction correctly. What it does *not* claim is bit-for-bit
// replication of the real decode circuit's behavior on operation codes
// that were never assigned -- those fall out as Invalid here, where the
// real machine might have repurposed the bits differently. This is a
// documented limitation, not a silent one.

package StretchDecode;

import StretchTypes::*;

// ---------------------------------------------------------------------
// Half/full word length.
// SOURCE: Figure 6, p.18 -- every full-word format (INTEGER, CONNECTIVE,
// INPUT-OUTPUT, TRANSMIT, SIC, BRANCH ON BIT) begins ADDRESS(24) then the
// literal 1000 at bits 24-27; no half-word format has this marker there
// (half-word formats place a 3-6 bit operand/opcode field spanning bits
// 19 up, never a fixed 1000 at 24-27 -- see e.g. BRANCH ON BIT prose,
// p.~100: "Bits 24-27 ... designate the operation" together with the
// preceding 24-bit address, which only makes sense as a length tag
// shared by the whole full-word family).
// ---------------------------------------------------------------------
function InstrLen instrLen(HalfWord32 hw0);
  return (hw0[7:4] == 4'b1000) ? Full : Half;
endfunction

// ---------------------------------------------------------------------
// Full-word formats
// ---------------------------------------------------------------------

function VflAddr vflAddrOf(Word64 w);
  return VflAddr {
    addr:   w[63:40],
    i1:     w[35:32],
    p:      w[31:29],
    length: w[28:23],
    bs:     w[22:20],
    offset: w[19:13],
    i2:     w[3:0]
  };
endfunction

function Bool isConnSuffix(Bit#(5) s) =
  (s == conn_C) || (s == conn_CM) || (s == conn_CT);

// Known VFL integer-arithmetic / radix-conversion base codes (pocket
// card "INTEGER ARITHMETIC" + "RADIX CONVERSION" tables, the 6 bits
// following the abc modifiers).
function Bool isVflIntCode(Bit#(6) c);
  return case (c)
    6'b000001, // +
    6'b100001, // +MG
    6'b000101, // L
    6'b100101, // LWF
    6'b001001, // M+
    6'b101001, // M+MG
    6'b101011, // M+1
    6'b001101, // ST
    6'b101101, // SRD
    6'b010001, // K
    6'b110001, // KF
    6'b010011, // KE
    6'b110011, // KFE
    6'b010101, // KR
    6'b110101, // KFR
    6'b111101, // LTRS
    6'b011001, // *
    6'b001011, // LFT
    6'b111001, // *+
    6'b011101, // /
    6'b000011, // LCV
    6'b100011, // LTRCV
    6'b011011, // CV
    6'b111011: True; // DCV
    default: False;
  endcase;
endfunction

function DecodedInstr decodeFullWord(Word64 w);
  Bit#(9) op9    = w[12:4];
  VflMod  m      = VflMod { unsign: op9[8], invert: op9[7], decimal: op9[6] };
  Bit#(6) code6  = op9[5:0];
  Bit#(4) conn4  = op9[8:5];
  Bit#(5) suffix = op9[4:0];
  VflAddr a      = vflAddrOf(w);

  // BIT BRANCHING: second half-word literal 111000000 at bits 51-59
  // (local bits 19-27 of the second half-word). SOURCE: Figure 6,
  // pocket card "BIT BRANCHING" row.
  if (w[12:4] == 9'b111000000) // note: overlaps op9's position on purpose
    return tagged BitBranch { addr1: a.addr, i1: a.i1,
                               addr2: w[31:13], modAbc: w[3:1], idx: w[0] };

  // INPUT-OUTPUT: literal 10000 at bits 55-59 (second half-word local
  // bits 23-27). SOURCE: pocket card "INPUT-OUTPUT OPERATIONS" row.
  // addr2 = IBM bits 32-49 (18 bits) = w[31:14]; op = IBM bits 51-54
  // (4 bits) = w[12:9]; i2 = IBM bits 60-63 = w[3:0]. See StretchTypes'
  // IoOp comment for the op-field bit layout.
  else if (w[8:4] == litIoOp)
    return tagged IoOp { addr1: a.addr, i1: a.i1, addr2: w[31:14],
                          op: w[12:9], i2: w[3:0] };

  // TRANSMIT: 3-bit sub-op at bits 57-59 (second half-word local bits
  // 25-27) is 010 (Transmit) or 110 (Swap); bits 55-56 are the a/b
  // (backward/immediate-count) modifiers. SOURCE: pocket card
  // "TRANSMIT OPERATIONS" row.
  else if (w[6:4] == 3'b010 || w[6:4] == 3'b110)
    return tagged Transmit { addr1: a.addr, i1: a.i1, addr2: w[31:13],
                              j: w[12:9], backward: w[8:8], immCount: w[7:7],
                              i2: w[3:0] };

  // SIC (STORE INSTRUCTION COUNTER IF): second half-word is itself a
  // valid half-word branch instruction (Unconditional Branch,
  // Count-and-Branch, or Branch-on-Indicator shape). SOURCE: p.~100
  // "Bits 32-63 specify the half-word branch instruction used."
  else if (isValidEmbeddedBranch(w[31:0]))
    return tagged Sic { addr: a.addr, idx: a.i1, inner: w[31:0] };

  // Otherwise: VFL integer/radix-conversion or connective.
  else if (isConnSuffix(suffix))
    return tagged Connective ConnInstr { a: a, conn: conn4, suffix: suffix };
  else if (isVflIntCode(code6))
    return tagged VflInt VflInstr { a: a, m: m, code: code6 };
  else
    return tagged Invalid;
endfunction

// Cheap validity probe used only to recognize a SIC-embedded branch;
// does not need to fully decode it. NOTE: forward-referenced from
// decodeFullWord above; isValidUncondBranchOp is defined further down
// with the other half-word opcode validators -- BSV allows this
// top-level forward reference within a package.
function Bool isValidEmbeddedBranch(HalfWord32 hw);
  if (isValidUncondBranchOp(hw[12:10]) && hw[9:4] == 6'b000000)
    return True;
  else if (hw[6:3] == 4'b1001) // count-and-branch literal
    return True;
  else if (hw[6:3] == 4'b1000) // branch-on-indicator literal
    return True;
  else
    return False;
endfunction

// ---------------------------------------------------------------------
// Half-word formats. Each `tryX` validates its opcode sub-field before
// committing; `decodeHalfWord` tries them in a fixed priority order
// (see file header) and returns the first validated match.
// ---------------------------------------------------------------------

function Bool isValidUncondBranchOp(Bit#(3) c);
  return case (c)
    3'b000, 3'b001, 3'b010, 3'b011, 3'b100, 3'b110: True; // BE,BD,B,BR,BEW,NOP
    default: False;
  endcase;
endfunction

function Bool isValidMiscOp(Bit#(3) c);
  return case (c)
    3'b000, 3'b001, 3'b010, 3'b011, 3'b100: True; // R,RCZ,EX,EXIC,Z
    default: False;
  endcase;
endfunction

function Bool isValidDirIndexOp(Bit#(5) c);
  return case (c)
    dixop_LX, // LX
    dixop_LV, // LV
    dixop_LC, // LC
    dixop_LR, // LR
    dixop_SX, // SX
    dixop_SV, // SV
    dixop_SC, // SC
    dixop_SR, // SR
    dixop_V_PLUS, // V+
    dixop_V_PLUS_C, // V+C
    dixop_V_PLUS_CR, // V+CR
    dixop_KV, // KV
    dixop_KC, // KC
    dixop_RNX, // RNX
    dixop_LVE, // LVE
    dixop_SVA: True; // SVA
    default: False;
  endcase;
endfunction

function Bool isValidImmIndexOp(Bit#(4) c);
  return True; // all 16 combinations of the 4-bit field are assigned,
               // pocket card "IMMEDIATE INDEX ARITHMETIC" table.
endfunction

function Bool isValidFpCode(Bit#(7) c);
  return case (c)
    fpop_PLUS,
    fpop_PLUS_MG,
    fpop_L,
    fpop_LWF,
    fpop_M_PLUS,
    fpop_M_PLUS_MG,
    fpop_ST,
    fpop_K,
    fpop_KMG,
    fpop_KR,
    fpop_KMGR,
    fpop_STAR,
    fpop_SLASH,
    fpop_R_SLASH,
    fpop_SRT,
    fpop_D_PLUS,
    fpop_D_PLUS_MG,
    fpop_DL,
    fpop_DLWF,
    fpop_SRD,
    fpop_SLO,
    fpop_D_STAR,
    fpop_LFT,
    fpop_STAR_PLUS,
    fpop_D_SLASH,
    fpop_F_PLUS,
    fpop_SHF,
    fpop_E_PLUS,
    fpop_E_PLUS_I: True; // E+I
    default: False;
  endcase;
endfunction

function Maybe#(DecodedInstr) tryDirIndex(HalfWord32 hw);
  Bit#(5) code = hw[8:4];
  return isValidDirIndexOp(code)
    ? tagged Valid (tagged DirIndex { addr: hw[31:13], j: hw[12:9],
                                       code: code, idx: hw[3:0] })
    : tagged Invalid;
endfunction

function Maybe#(DecodedInstr) tryImmIndex(HalfWord32 hw);
  // literal 10000 at bits 23-27 (local): hw[8:4]
  return (hw[8:4] == litImmIndex)
    ? tagged Valid (tagged ImmIndex { imm: hw[31:13], j: hw[12:9],
                                       code: hw[3:0] })
    : tagged Invalid;
endfunction

function Maybe#(DecodedInstr) tryCountBranch(HalfWord32 hw);
  // literal 1001 at bits 25-28 (local): hw[6:3]
  return (hw[6:3] == 4'b1001)
    ? tagged Valid (tagged CountBranch { addr: hw[31:13], j: hw[12:9],
                                          v: hw[8:7], refill: hw[2:2],
                                          branchIfZero: hw[1:1], idx: hw[0:0] })
    : tagged Invalid;
endfunction

function Maybe#(DecodedInstr) tryBranchInd(HalfWord32 hw);
  // literal 1000 at bits 25-28 (local): hw[6:3]
  return (hw[6:3] == 4'b1000)
    ? tagged Valid (tagged BranchInd { addr: hw[31:13], indNum: hw[12:7],
                                        clear: hw[2:2], branchOn: hw[1:1],
                                        idx: hw[0:0] })
    : tagged Invalid;
endfunction

function Maybe#(DecodedInstr) tryBranchOrMisc(HalfWord32 hw);
  Bit#(3) op  = hw[12:10];
  Bit#(6) lit = hw[9:4];
  if (lit == 6'b000000 && isValidUncondBranchOp(op))
    return tagged Valid (tagged BranchOrMisc { addr: hw[31:13], code: op,
                                                misc: False, idx: hw[3:0] });
  else if (lit == 6'b100000 && isValidMiscOp(op))
    return tagged Valid (tagged BranchOrMisc { addr: hw[31:13], code: op,
                                                misc: True, idx: hw[3:0] });
  else
    return tagged Invalid;
endfunction

// Floating point, Figure 6 "FLOATING POINT" row: half-word,
// ADDRESS[0:17](18b) + a(N/U)[18] + b[19] + c[20] + code[21:27](7b) +
// I[28:31](4b). abc occupy local bits 18-20 = hw[13:11]; the 7-bit code
// is hw[10:4].
function Maybe#(DecodedInstr) tryFpFixed(HalfWord32 hw);
  Bit#(7) code = hw[10:4];
  return isValidFpCode(code)
    ? tagged Valid (tagged Fp { addr: hw[31:14], unnorm: hw[13:13],
                                 absSign: hw[12:12], invSign: hw[11:11],
                                 code: code, idx: hw[3:0] })
    : tagged Invalid;
endfunction

function DecodedInstr decodeHalfWord(HalfWord32 hw);
  if (tryDirIndex(hw) matches tagged Valid .d) return d;
  else if (tryImmIndex(hw) matches tagged Valid .d) return d;
  else if (tryCountBranch(hw) matches tagged Valid .d) return d;
  else if (tryBranchInd(hw) matches tagged Valid .d) return d;
  else if (tryBranchOrMisc(hw) matches tagged Valid .d) return d;
  else if (tryFpFixed(hw) matches tagged Valid .d) return d;
  else return tagged Invalid;
endfunction

// ---------------------------------------------------------------------
// Top-level decode: caller supplies the first half-word always, and the
// second half-word when instrLen(hw0) == Full.
// ---------------------------------------------------------------------
function DecodedInstr decode(HalfWord32 hw0, Maybe#(HalfWord32) hw1);
  if (instrLen(hw0) == Full)
    case (hw1) matches
      tagged Valid .h1: return decodeFullWord({hw0, h1});
      tagged Invalid:   return tagged Invalid; // caller fetch bug
    endcase
  else
    return decodeHalfWord(hw0);
endfunction

endpackage
