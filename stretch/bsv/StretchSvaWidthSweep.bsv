// StretchSvaWidthSweep -- SVA's address replacement, and StretchDecode's
// instruction formats, against the length tag the diagnostic STATES,
// exhaustively.
//
// Named "...Sweep" and not "...Tb" on purpose: .gitignore drops
// bsv/Stretch*Tb.bsv, which is how generated testbenches from
// strap/gen_tb.py stay out of the tree.  Hand-written ones have to sit
// outside that pattern -- StretchSmoke.bsv is the other.
//
// jb_ax3a p.140 closes routine 1222's SVA data-bit series by writing
// out the machine's own length tag, read outward from bit 27:
//
//   1. IF BIT 27 IS 1, INSTRUCTION IS DIRECT INDEX, STORE 19 BITS.
//   2. IF BITS 26 AND 27 ARE 10, INSTRUCTIO IS FP, STORE 18 BITS.
//   3. IF BITS 25-27 ARE 100, INSTRUCT IS CB OR BIND, STORE 19 BITS.
//   4. IF BITS 24-27 ARE 1000, INSTRUCT IS FULL WD, STORE 24 BITS.
//   5. IF BITS 23-27 ARE 10000, INSTRUCT IS IMMED IX, STORE 19 BITS.
//   6. IF BITS 23-27 ARE 00000, INSTRUCT IS MISC, STORE 19 BITS.
//
// Those six patterns partition bits 23-27 exactly (xxxx1, xxx10,
// xx100, x1000, 10000, 00000), so this is a five-bit decision that
// names the format of EVERY half-word, assigned or not.
//
// WHY THIS EXISTS.  dirIndexOp's SVA arm picks its address width
// straight off those bits, because real hardware selects it
// combinationally from the length tag and cannot consult a table of
// which operation codes are assigned.  Writing it that way is only
// safe if StretchDecode's format tables agree with the tag -- if
// tryFpFixed ever accepted a code whose bits 26-27 were not 10, or
// tryDirIndex one without bit 27, the two would part company and SVA
// would silently use the wrong width.  So that agreement is the thing
// to pin, and it is a property of all 2^14 half-words, not of the
// three points the transcribed blocks (ibox3_sva_fp, _dix, _full) hit.
//
// The reverse direction -- tag class to decode -- deliberately is NOT
// checked, because it does not hold and should not: p.140 names a
// format for every bit pattern, while isValidFpCode lists only the 29
// assigned floating point codes of the 32 that end in 10.  Asking the
// decode for the width is what made those three unassigned codes come
// out 19 bits where p.140 says 18; asking the bits is what fixed it.
//
// Also checked, and the reason this file is named for SVA: the model's
// own svaReplaceAddr -- the function dirIndexOp calls -- is probed at
// every half-word by substituting an all-zero and an all-one value and
// XORing the results, which marks exactly the bits it replaced.  That
// pins the width, that the replaced field is the TOP of the half-word,
// and that the bits below it survive.  And a full-word length tag must
// not decode as any half-length format.
//
// NOTE ON WHAT THE DECODE SWEEP DOES AND DOES NOT PROTECT.  Since SVA
// no longer consults decodeHalfWord, the format check below is not
// guarding SVA's width -- svaReplaceAddr's own probe is.  What it
// guards is the decode tables' agreement with the deck's tag, which
// fetch and execute do depend on, and which is what made the old
// decode-based width wrong in the first place.
//
// WHAT THE NEGATIVE CONTROL TAUGHT.  The first attempt to break this
// sweep -- adding a bogus code ending in 00 to isValidFpCode -- changed
// NOTHING, because tryFpFixed is tried last and every code ending in 00
// is already claimed: hw[5:4] = 00 forces hw[6:4] = 000 (or it is a
// CB/BIND tag), hw[7:4] = 0000 (or it is the full-word tag), hw[8:4] =
// 00000 (or it is the immediate index literal), and what is left is
// exactly tryBranchOrMisc's two literals.  So the FP table alone cannot
// break the tag structure; only an edit to one of the EARLIER formats
// can, and that is what the working control does.  Changing
// tryCountBranch's literal from 1001 to 0001 produces 1536 mismatches,
// all of them "CountBranch needs bits 25-27 = 100".
//
// Every case runs twice, with the address field zeroed and all ones,
// to show the classification depends on bits 18-31 alone.
package StretchSvaWidthSweep;

import StretchTypes::*;
import StretchDecode::*;

(* synthesize *)
module mkStretchSvaWidthSweep(Empty);
  Reg#(Bit#(32)) i     <- mkReg(0);
  Reg#(Bit#(32)) bad   <- mkReg(0);
  Reg#(Bit#(32)) shown <- mkReg(0);
  Reg#(Bit#(32)) seenDix <- mkReg(0);
  Reg#(Bit#(32)) seenFp  <- mkReg(0);

  // The deck's table as a width, and as dirIndexOp spells it.
  function Bit#(8) tableWidth(HalfWord32 hw);
    return (hw[7:4] == 4'b1000) ? 24 : (hw[5:4] == 2'b10) ? 18 : 19;
  endfunction

  rule sweep (i < 32768);
    HalfWord32 hw = (i[14] == 0) ? {18'b0, i[13:0]} : {18'h3ffff, i[13:0]};
    DecodedInstr d = decodeHalfWord(hw);

    // What p.140 requires of each format's tag bits.
    Bool ok = True;
    String why = "";
    case (d) matches
      tagged DirIndex .*:    begin ok = (hw[4]   == 1'b1);      why = "DirIndex needs bit 27 = 1"; end
      tagged ImmIndex .*:    begin ok = (hw[8:4] == 5'b10000);  why = "ImmIndex needs bits 23-27 = 10000"; end
      tagged CountBranch .*: begin ok = (hw[6:4] == 3'b100);    why = "CountBranch needs bits 25-27 = 100"; end
      tagged BranchInd .*:   begin ok = (hw[6:4] == 3'b100);    why = "BranchInd needs bits 25-27 = 100"; end
      tagged BranchOrMisc .*:begin ok = (hw[8:4] == 5'b00000);  why = "BranchOrMisc needs bits 23-27 = 00000"; end
      tagged Fp .*:          begin ok = (hw[5:4] == 2'b10);     why = "Fp needs bits 26-27 = 10"; end
      default:               begin ok = True;                   why = ""; end
    endcase

    // A full-word length tag must not decode as a half-length format.
    Bool decodedSomething = True;
    case (d) matches
      tagged Invalid: decodedSomething = False;
      default:        decodedSomething = True;
    endcase
    if (instrLen(hw) == Full && decodedSomething) begin
      ok = False; why = "full-word tag (bits 24-27 = 1000) decoded as a half-length format";
    end

    // THE MODEL'S OWN REPLACEMENT, probed rather than restated.
    // Substituting an all-zero and an all-one value and XORing the two
    // results marks exactly the bits svaReplaceAddr replaced, so this
    // checks three things at once: how many bits move, that they are
    // the TOP bits of the half-word, and that everything below them is
    // preserved. Comparing a copy of the formula against another copy
    // of the formula, which is what stood here first, checks nothing.
    Bit#(32) moved = svaReplaceAddr(hw, 24'h000000) ^ svaReplaceAddr(hw, 24'hffffff);
    Bit#(8)  t     = tableWidth(hw);
    Bit#(32) want  = (t == 24) ? 32'hffffff00    // bits 0-23
                   : (t == 18) ? 32'hffffc000    // bits 0-17
                   :             32'hffffe000;   // bits 0-18
    if (moved != want) begin
      ok = False; why = "svaReplaceAddr moved the wrong bits for this tag";
    end

    // Coverage counters, so a decode that silently stopped matching
    // anything cannot pass this by classifying nothing.
    case (d) matches
      tagged DirIndex .*: seenDix <= seenDix + 1;
      tagged Fp .*:       seenFp  <= seenFp + 1;
      default:            noAction;
    endcase

    if (!ok) begin
      bad <= bad + 1;
      if (shown < 8) begin
        $display("MISMATCH hw=0x%08x bits18-31=0x%04x: %s", hw, hw[13:0], why);
        shown <= shown + 1;
      end
    end
    i <= i + 1;
  endrule

  rule done (i == 32768);
    if (seenDix == 0 || seenFp == 0) begin
      $display("FAIL sweep classified nothing: DirIndex=%0d Fp=%0d", seenDix, seenFp);
      $display("1 TEST(S) FAILED");
    end else if (bad == 0)
      $display("ALL TESTS PASSED (32768 half-words; DirIndex=%0d Fp=%0d; formats agree with jb_ax3a p.140)",
               seenDix, seenFp);
    else
      $display("%0d TEST(S) FAILED (of 32768 half-words)", bad);
    $finish(0);
  endrule
endmodule

endpackage
