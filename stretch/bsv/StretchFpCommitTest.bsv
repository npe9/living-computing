// StretchFpCommitTest.bsv -- fpStoreClass tested WITHOUT INSTANTIATING
// STORAGE, which is the whole point of step 2's first family.
//
// docs/ebox_roadmap.md step 2 wants the benefit stated as "boxes that
// can be tested without instantiating storage".  Before this change
// fpStoreClass took a StretchStorage interface and made ten
// st.writeWord calls, so exercising one arm of it meant building the
// machine.  It now takes eleven plain values and RETURNS an FpCommit,
// so this file instantiates nothing at all: no memory, no core, no
// deck.  That is the property under test as much as any single answer.
//
// WHY THESE CHECKS AND NOT ARITHMETIC ONES.  The arithmetic is already
// pinned to printed IBM results by the jb_af1c F212/F213/F219 decks,
// which run the real machine; duplicating them here would add no
// oracle.  What those decks CANNOT see is the record's structure --
// which fields an arm fills, and whether two of them can ever name the
// same word.  That is what this file pins.
//
// NOT NAMED *Tb.bsv ON PURPOSE: .gitignore ignores bsv/Stretch*Tb.bsv
// because almost all testbenches here are generated.  This one is
// hand-written and must be tracked, like StretchDivBox.bsv's
// mkDivBoxTb is tracked by living inside a real source file.
package StretchFpCommitTest;

import StretchTypes::*;
import StretchFP::*;
import StretchExecute::*;

(* synthesize *)
module mkFpCommitTb(Empty);

  Reg#(Bool) done <- mkReg(False);

  // Arbitrary but non-degenerate inputs.  No arm's STRUCTURE depends on
  // the fraction's value, and the values that do matter are pinned by
  // the printed decks, so these exist only to be distinguishable.
  WordAddr ea     = 1000;
  FpNum    acc    = FpNum { ef: 0, em: 10'd5, es: 0,
                            frac: 48'h123456789abc, sign: 0, flags: 3'b0 };
  Word64   accL   = 64'h0400_0000_0000_0000;
  Word64   accS   = 64'h0000_0000_0000_0007;
  Word64   accR0  = 64'hdead_beef_0000_0000;

  function Tuple2#(Word64, FpCommit) call(Bit#(7) c, Bool protViol);
    return fpStoreClass(c, 0, 0, ea, acc, accL, accS, accR0,
                        False, False, protViol, 0);
  endfunction

  function Bool anyAcc(FpCommit f);
    return isValid(f.accLeft) || isValid(f.accRight) || isValid(f.accSign);
  endfunction

  // Same shift form as setBit in StretchExecute, so "DS is on" means
  // here exactly what setting it means there: IBM bit n is bit 63-n.
  function Bool indOn(Word64 w, Bit#(6) n);
    Bit#(7) sh = 63 - zeroExtend(n);
    return ((w >> sh) & 1) == 1;
  endfunction

  function Bool allAcc(FpCommit f);
    return isValid(f.accLeft) && isValid(f.accRight) && isValid(f.accSign);
  endfunction

  rule rl_run (!done);
    Bit#(32) fails = 0;

    function Action chk(String nm, Bool ok);
      action
        if (ok) $display("PASS %s", nm);
        else    $display("FAIL %s", nm);
      endaction
    endfunction

    // --- the four store arms put the word at `ea` and touch no acc ---
    let st_  = call(fpop_ST,  False);
    let srt_ = call(fpop_SRT, False);
    let srd_ = call(fpop_SRD, False);
    let slo_ = call(fpop_SLO, False);

    Bool okStStore = isValid(tpl_2(st_).store)
                     && tpl_1(fromMaybe(tuple2(?, ?), tpl_2(st_).store)) == ea;
    chk("fpcommit_st_store_at_ea", okStStore);
    fails = fails + (okStStore ? 0 : 1);

    chk("fpcommit_st_touches_no_acc", !anyAcc(tpl_2(st_)));
    fails = fails + (anyAcc(tpl_2(st_)) ? 1 : 0);

    chk("fpcommit_srt_store_at_ea",
        isValid(tpl_2(srt_).store) && !anyAcc(tpl_2(srt_)));
    fails = fails + ((isValid(tpl_2(srt_).store) && !anyAcc(tpl_2(srt_))) ? 0 : 1);

    chk("fpcommit_srd_store_at_ea",
        isValid(tpl_2(srd_).store) && !anyAcc(tpl_2(srd_)));
    fails = fails + ((isValid(tpl_2(srd_).store) && !anyAcc(tpl_2(srd_))) ? 0 : 1);

    chk("fpcommit_slo_store_at_ea",
        isValid(tpl_2(slo_).store) && !anyAcc(tpl_2(slo_)));
    fails = fails + ((isValid(tpl_2(slo_).store) && !anyAcc(tpl_2(slo_))) ? 0 : 1);

    // --- SUPPRESSION DID NOT MOVE.  Reference Manual printed p.31-32:
    // a store into a protected area is suppressed and sets DS.  With
    // the predicate true the record must carry NO store, and DS must
    // be on -- the same two effects the old `if/else` had, now one
    // decided value instead of a write that did or did not happen.
    for (Integer k = 0; k < 4; k = k + 1) begin
      Bit#(7) c = case (k) 0: fpop_ST; 1: fpop_SRT; 2: fpop_SRD;
                           default: fpop_SLO; endcase;
      let r = call(c, True);
      Bool ok = !isValid(tpl_2(r).store)
                && indOn(tpl_1(r), ind_DS);
      chk("fpcommit_prot_suppresses_and_sets_ds", ok);
      fails = fails + (ok ? 0 : 1);
    end

    // --- the two accumulator arms fill all three halves, no store ---
    let shf_  = call(fpop_SHF, False);
    let epli_ = call(fpop_E_PLUS_I, False);

    chk("fpcommit_shf_fills_acc_trio", allAcc(tpl_2(shf_)));
    fails = fails + (allAcc(tpl_2(shf_)) ? 0 : 1);
    chk("fpcommit_shf_no_store", !isValid(tpl_2(shf_).store));
    fails = fails + (isValid(tpl_2(shf_).store) ? 1 : 0);

    chk("fpcommit_epli_fills_acc_trio", allAcc(tpl_2(epli_)));
    fails = fails + (allAcc(tpl_2(epli_)) ? 0 : 1);
    chk("fpcommit_epli_no_store", !isValid(tpl_2(epli_).store));
    fails = fails + (isValid(tpl_2(epli_).store) ? 1 : 0);

    // --- NO ARM CAN ALIAS, which is what makes committing at the end
    // safe.  If some future arm wrote both `ea` and an accumulator
    // half, the two fields could name the same word and the commit
    // order would start to matter.  The comment on FpCommit asserts
    // this; this check is what makes the assertion load-bearing.
    Bool aliased = False;
    for (Integer k = 0; k < 6; k = k + 1) begin
      Bit#(7) c = case (k) 0: fpop_ST; 1: fpop_SRT; 2: fpop_SRD;
                           3: fpop_SLO; 4: fpop_SHF;
                           default: fpop_E_PLUS_I; endcase;
      for (Integer p = 0; p < 2; p = p + 1) begin
        let r = call(c, p == 1);
        if (isValid(tpl_2(r).store) && anyAcc(tpl_2(r))) aliased = True;
      end
    end
    chk("fpcommit_no_arm_writes_both_ea_and_acc", !aliased);
    fails = fails + (aliased ? 1 : 0);

    if (fails == 0) $display("ALL TESTS PASSED");
    else            $display("%0d TEST(S) FAILED", fails);
    done <= True;
    $finish(0);
  endrule

endmodule

endpackage
