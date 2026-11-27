package StretchLaParts;

// =====================================================================
// THE LOOK-AHEAD LEVELS OF ONE INSTRUCTION, AS TABLE A-2 GIVES THEM
// (fidelity_plan.md A5 "what is left" item 3 (a); ebox_roadmap.md step 7,
// "split whole-instruction look-ahead entries"; 2026-11-27).
//
// Source: IBM 7030 Performance Characteristics Vol. 1 (Mar 61), Table A-2
// "Summary of 7030 instruction execution", the E-box sheet, printed A-12
// (PDF 71), read from the page image; its legend is on PDF 69. Transcribed
// in docs/spec_lookahead.md section 1.7; section 5 maps it onto this
// model's DecodedInstr.
//
// A level of Table A-2 is a PART of an instruction ("op", "opnd", "store",
// "op + opnd" ...), not the instruction (spec_lookahead.md section 5: a VFL
// ST occupies three). laParts gives the parts in the order the table
// lists them, with the sheet's own note applied (verbatim, PDF 71):
//   "For all VFL operations, if opnd crosses over full word boundary, the
//    no. of LA opnd and/or store levels is doubled.  Progressive indexing
//    required one more IX box."
// so for VflInt and Connective: each opnd and store part twice when the
// field crosses, and one LaIxRec more when the instruction is progressive.
// Buchholz, Planning a Computer System, printed p.246 (PDF 271): "a VFL
// ADD TO MEMORY instruction with progressive indexing ... may require six
// successive levels" -- 3 + 2 + 1 = 6 by this rule, the cross-check.
//
// WHAT IT DOES NOT DO.  It is DATA: no rule allocates by it yet (the
// look-ahead still loads one level per E-box instruction).  It maps the
// E-box sheet only (Fp, VflInt, Connective, IoOp); every other class --
// the I-box sheets A-10/A-11 (PDF 69-70), whose levels the I-box loads
// itself or not at all -- answers tagged Invalid, as does any code the
// sheet has no row for.  Invalid is "not mapped", never a guess.
//
// READINGS AND INFERENCES, each labelled:
//   * D* (fpop_D_STAR) is not named on the sheet; its first FP row names
//     "*" and the double forms of the add and load (D+, DL, DLWF, D+MG).
//     INFERENCE: D* is a one-level op + opnd like *.
//   * VFL M+ (add to memory, without MG): the VFL row reads "ST, SRD / CM,
//     M+- MG, M+1"; whether "M+- MG" names M+- as well as M+-MG is not
//     clear from the print.  Buchholz's six-level ADD TO MEMORY above
//     needs M+ to be op / opnd / store, so M+ is put in that row (READING,
//     from Buchholz, not from the sheet alone).
//   * VFL / (binary): the sheet has "/ (Dec.)" only.  Binary VFL divide
//     answers Invalid.
//   * The ORDER of the progressive LaIxRec within the sequence is not
//     given by the note; it is put last (INFERENCE, order only -- the
//     count is the note's).
//   * The doubled parts are put next to each other (op, opnd, opnd,
//     store, store): the note gives counts, not order (INFERENCE, order).
//   * Floating point is full-word: no crossing, no progressive indexing
//     (Ref. Manual printed pp.19-20), so neither modifier applies to Fp.
// =====================================================================

import Vector::*;
import StretchTypes::*;

typedef struct {
  Bit#(3)            n;     // levels, 1..6
  Vector#(6, LaKind) kinds; // kinds[0 .. n-1] in Table A-2's order
} LaParts deriving (Bits, Eq, FShow);

// A sequence from a list of up to three base kinds (Table A-2's rows have
// at most three levels on the E-box sheet), doubling opnd/store parts on
// a crossing and appending LaIxRec when progressive.
function LaParts laSeq(Integer nb, LaKind k0, LaKind k1, LaKind k2, Bool crosses, Bool prog);
  Vector#(3, LaKind) b = cons(k0, cons(k1, cons(k2, nil)));
  Vector#(6, LaKind) s = replicate(Whole);
  Bit#(3) n = 0;
  for (Integer i = 0; i < 3; i = i + 1)
    if (i < nb) begin
      s[n] = b[i]; n = n + 1;
      if (crosses && (b[i] == LaOpnd || b[i] == LaStore)) begin
        s[n] = b[i]; n = n + 1;
      end
    end
  if (prog) begin
    s[n] = LaIxRec; n = n + 1;
  end
  return LaParts { n: n, kinds: s };
endfunction

function Maybe#(LaParts) laParts(DecodedInstr d, Bool crosses, Bool prog);
  Maybe#(LaParts) r = tagged Invalid;
  case (d) matches
    tagged Fp .f: begin
      Bit#(7) c = f.code;
      if (c == fpop_PLUS || c == fpop_PLUS_MG || c == fpop_L || c == fpop_LWF
          || c == fpop_D_PLUS || c == fpop_D_PLUS_MG || c == fpop_DL || c == fpop_DLWF
          || c == fpop_K || c == fpop_KMG || c == fpop_KR || c == fpop_KMGR
          || c == fpop_STAR || c == fpop_D_STAR || c == fpop_SLASH || c == fpop_R_SLASH
          || c == fpop_F_PLUS || c == fpop_E_PLUS || c == fpop_E_PLUS_I)
        r = tagged Valid laSeq(1, LaOpOpnd, Whole, Whole, False, False);
      else if (c == fpop_SHF)
        r = tagged Valid laSeq(1, LaOpCount, Whole, Whole, False, False);
      else if (c == fpop_ST || c == fpop_SLO || c == fpop_SRD || c == fpop_SRT)
        r = tagged Valid laSeq(1, LaStore, Whole, Whole, False, False);
      else if (c == fpop_M_PLUS || c == fpop_M_PLUS_MG || c == fpop_LFT || c == fpop_D_SLASH)
        r = tagged Valid laSeq(2, LaOpOpnd, LaStore, Whole, False, False);
      else if (c == fpop_STAR_PLUS)
        r = tagged Valid laSeq(2, LaOpOpnd, LaCft, Whole, False, False);
    end
    tagged VflInt .v: begin
      Bit#(6) c = v.code;
      Bool dec = (v.m.decimal == 1);
      // + +MG L LWF K KF KE KFE KR KFR LCV: op / opnd
      if (c == 6'b000001 || c == 6'b100001 || c == 6'b000101 || c == 6'b100101
          || c == 6'b010001 || c == 6'b110001 || c == 6'b010011 || c == 6'b110011
          || c == 6'b010101 || c == 6'b110101 || c == 6'b000011)
        r = tagged Valid laSeq(2, LaOp, LaOpnd, Whole, crosses, prog);
      // CV, DCV: op / INT
      else if (c == 6'b011011 || c == 6'b111011)
        r = tagged Valid laSeq(2, LaOp, LaInt, Whole, crosses, prog);
      // ST SRD M+ M+MG M+1 LFT LTRS LTRCV: op / opnd / store
      else if (c == 6'b001101 || c == 6'b101101 || c == 6'b001001 || c == 6'b101001
               || c == 6'b101011 || c == 6'b001011 || c == 6'b111101 || c == 6'b100011)
        r = tagged Valid laSeq(3, LaOp, LaOpnd, LaStore, crosses, prog);
      // * : binary op / opnd; decimal op / opnd / store
      else if (c == 6'b011001)
        r = tagged Valid (dec ? laSeq(3, LaOp, LaOpnd, LaStore, crosses, prog)
                              : laSeq(2, LaOp, LaOpnd, Whole, crosses, prog));
      // *+ : binary op / opnd / C($FT); decimal op / opnd / store
      else if (c == 6'b111001)
        r = tagged Valid (dec ? laSeq(3, LaOp, LaOpnd, LaStore, crosses, prog)
                              : laSeq(3, LaOp, LaOpnd, LaCft, crosses, prog));
      // / : decimal only on the sheet
      else if (c == 6'b011101 && dec)
        r = tagged Valid laSeq(3, LaOp, LaOpnd, LaStore, crosses, prog);
    end
    tagged Connective .cn: begin
      if (cn.suffix == conn_C || cn.suffix == conn_CT)
        r = tagged Valid laSeq(2, LaOp, LaOpnd, Whole, crosses, prog);
      else if (cn.suffix == conn_CM)
        r = tagged Valid laSeq(3, LaOp, LaOpnd, LaStore, crosses, prog);
    end
    tagged IoOp .*:
      r = tagged Valid laSeq(2, LaOp, LaLaop, Whole, False, False);
    default: r = tagged Invalid;
  endcase
  return r;
endfunction

// ---------------------------------------------------------------------
// mkLaPartsTb: laParts against rows typed from the page image of Table
// A-2's E-box sheet (printed A-12, PDF 71), one vector per row or
// modifier, each with its LITERAL level count and kinds:
//   0  FP +            op + opnd                       1
//   1  FP E+I          op + opnd                       1
//   2  FP SHF          op + count                      1
//   3  FP ST           store                           1
//   4  FP M+           op + opnd / store               2
//   5  FP *+           op + opnd / C($FT)              2
//   6  FP LFT          op + opnd / store               2
//   7  VFL + (binary)  op / opnd                       2
//   8  VFL * binary    op / opnd                       2
//   9  VFL * decimal   op / opnd / store               3
//  10  VFL CV          op / INT                        2
//  11  VFL ST          op / opnd / store               3
//  12  VFL *+ binary   op / opnd / C($FT)              3
//  13  VFL LTRS        op / opnd / store               3
//  14  CT              op / opnd                       2
//  15  CM              op / opnd / store               3
//  16  I/O             op / LAOP                       2
//  17  VFL + crossing  op / opnd / opnd                3   (the note)
//  18  VFL ST crossing op / opnd x2 / store x2         5   (the note)
//  19  VFL M+ crossing + progressive: 3 + 2 + 1        6   (Buchholz PDF 271)
//  20  CV crossing     op / INT (no opnd/store part)   2
//  21  VFL / binary    no row: Invalid
//  22  DirIndex (LX)   I-box sheet: Invalid
//  23  FP crossing flag ignored (full-word FP): M+     2
// INJECTIONS, OBSERVED 2026-11-27 (each in laParts / laSeq, reverted by
// the exact inverse edit, the file byte-identical after):
//   no doubling on a crossing (`False &&`)       17, 18, 19 FAIL
//   progressive ignored (`if (False)`)           19 FAILS (5, want 6)
//   INT doubled too                              20 FAILS (3, want 2)
//   VFL decimal ignored (`dec = False`)          9 FAILS (2, want 3)
//   FP M+ dropped from the two-level row         4, 23 FAIL (Invalid)
//   FP given the VFL modifiers                   23 FAILS (4, want 2)
// and nothing else in each case.
// ---------------------------------------------------------------------
typedef 24 NLaPartsVec;

function DecodedInstr fpI(Bit#(7) c) =
  tagged Fp { addr: 0, unnorm: 0, absSign: 0, invSign: 0, code: c, idx: 0 };
function DecodedInstr vflI(Bit#(6) c, Bit#(1) dec) =
  tagged VflInt VflInstr { a: VflAddr { addr: 0, i1: 0, p: 0, length: 8, bs: 0, offset: 0, i2: 0 },
                           m: VflMod { unsign: 0, invert: 0, decimal: dec }, code: c };
function DecodedInstr connI(Bit#(5) s) =
  tagged Connective ConnInstr { a: VflAddr { addr: 0, i1: 0, p: 0, length: 8, bs: 0, offset: 0, i2: 0 },
                                conn: 4'b0110, suffix: s };

function Maybe#(LaParts) lp(Bit#(3) n, LaKind k0, LaKind k1, LaKind k2,
                            LaKind k3, LaKind k4, LaKind k5);
  Vector#(6, LaKind) s = replicate(Whole);
  s[0] = k0; s[1] = k1; s[2] = k2; s[3] = k3; s[4] = k4; s[5] = k5;
  return tagged Valid LaParts { n: n, kinds: s };
endfunction

(* synthesize *)
module mkLaPartsTb(Empty);
  Reg#(Bit#(5)) idx   <- mkReg(0);
  Reg#(Bit#(8)) fails <- mkReg(0);

  function Tuple3#(DecodedInstr, Bool, Bool) inOf(Bit#(5) i) =
    case (i)
      0:  tuple3(fpI(fpop_PLUS), False, False);
      1:  tuple3(fpI(fpop_E_PLUS_I), False, False);
      2:  tuple3(fpI(fpop_SHF), False, False);
      3:  tuple3(fpI(fpop_ST), False, False);
      4:  tuple3(fpI(fpop_M_PLUS), False, False);
      5:  tuple3(fpI(fpop_STAR_PLUS), False, False);
      6:  tuple3(fpI(fpop_LFT), False, False);
      7:  tuple3(vflI(6'b000001, 0), False, False);
      8:  tuple3(vflI(6'b011001, 0), False, False);
      9:  tuple3(vflI(6'b011001, 1), False, False);
      10: tuple3(vflI(6'b011011, 0), False, False);
      11: tuple3(vflI(6'b001101, 0), False, False);
      12: tuple3(vflI(6'b111001, 0), False, False);
      13: tuple3(vflI(6'b111101, 0), False, False);
      14: tuple3(connI(conn_CT), False, False);
      15: tuple3(connI(conn_CM), False, False);
      16: tuple3(tagged IoOp IoInstr { addr1: 0, i1: 0, addr2: 0, op: 0, i2: 0 }, False, False);
      17: tuple3(vflI(6'b000001, 0), True, False);
      18: tuple3(vflI(6'b001101, 0), True, False);
      19: tuple3(vflI(6'b001001, 0), True, True);
      20: tuple3(vflI(6'b011011, 0), True, False);
      21: tuple3(vflI(6'b011101, 0), False, False);
      22: tuple3(tagged DirIndex DixInstr { addr: 0, j: 1, code: dixop_LX, idx: 0 }, False, False);
      default: tuple3(fpI(fpop_M_PLUS), True, True);
    endcase;
  function Maybe#(LaParts) wantOf(Bit#(5) i) =
    case (i)
      0, 1: lp(1, LaOpOpnd, Whole, Whole, Whole, Whole, Whole);
      2:  lp(1, LaOpCount, Whole, Whole, Whole, Whole, Whole);
      3:  lp(1, LaStore, Whole, Whole, Whole, Whole, Whole);
      4, 6, 23: lp(2, LaOpOpnd, LaStore, Whole, Whole, Whole, Whole);
      5:  lp(2, LaOpOpnd, LaCft, Whole, Whole, Whole, Whole);
      7, 8, 14: lp(2, LaOp, LaOpnd, Whole, Whole, Whole, Whole);
      9, 11, 13, 15: lp(3, LaOp, LaOpnd, LaStore, Whole, Whole, Whole);
      10, 20: lp(2, LaOp, LaInt, Whole, Whole, Whole, Whole);
      12: lp(3, LaOp, LaOpnd, LaCft, Whole, Whole, Whole);
      16: lp(2, LaOp, LaLaop, Whole, Whole, Whole, Whole);
      17: lp(3, LaOp, LaOpnd, LaOpnd, Whole, Whole, Whole);
      18: lp(5, LaOp, LaOpnd, LaOpnd, LaStore, LaStore, Whole);
      19: lp(6, LaOp, LaOpnd, LaOpnd, LaStore, LaStore, LaIxRec);
      default: tagged Invalid;
    endcase;

  rule rl_check (idx < fromInteger(valueOf(NLaPartsVec)));
    match {.d, .cr, .pg} = inOf(idx);
    Maybe#(LaParts) got  = laParts(d, cr, pg);
    Maybe#(LaParts) want = wantOf(idx);
    // Compare the count and the first n kinds only (the slots past n are
    // not part of the answer).
    Bool ok = isValid(got) == isValid(want);
    if (ok &&& got matches tagged Valid .g &&& want matches tagged Valid .w) begin
      ok = (g.n == w.n);
      for (Integer k = 0; k < 6; k = k + 1)
        if (fromInteger(k) < w.n && g.kinds[k] != w.kinds[k]) ok = False;
    end
    if (ok) $display("PASS laparts[%0d]", idx);
    else begin
      $display("FAIL laparts[%0d]: got ", idx, fshow(got));
      $display("                 want ", fshow(want));
    end
    if (!ok) fails <= fails + 1;
    idx <= idx + 1;
  endrule

  rule rl_finish (idx == fromInteger(valueOf(NLaPartsVec)));
    if (fails == 0) $display("ALL TESTS PASSED");
    else $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule
endmodule

endpackage
