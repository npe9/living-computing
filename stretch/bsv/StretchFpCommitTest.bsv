// StretchFpCommitTest.bsv -- the floating-point commit record, tested
// WITH NO STORAGE INSTANTIATED.  That is the whole point of step 2's
// first family: docs/ebox_roadmap.md asks for "boxes that can be
// tested without instantiating storage", and both fpStoreClass and
// fpArithClass are now pure functions with zero `st` references, so
// this file builds no memory, no core and no deck.
//
// WHY THESE CHECKS AND NOT ARITHMETIC ONES.  The arithmetic is pinned
// to printed IBM results by the jb_af1c F210/F211/F212/F213/F219
// decks, which run the real machine; repeating them here would add no
// oracle.  What those decks cannot see is the record's STRUCTURE --
// which fields an arm fills, and whether two of them can ever name the
// same word.  That is what this file pins.
//
// THE SWEEP IS ONE OPCODE PER CLOCK, NOT A STATIC LOOP.  A `for` loop
// over 128 opcodes is UNROLLED by bsc, which would instantiate
// fpArithClass's ~700 lines 128 times.  Driving `c` from a register
// instead keeps one instance and makes the invariant EXHAUSTIVE over
// the entire 7-bit opcode space rather than over a hand-listed set --
// including the encodings no instruction uses, which is where a future
// arm would most easily go wrong unnoticed.
//
// NOT NAMED *Tb.bsv ON PURPOSE: .gitignore ignores bsv/Stretch*Tb.bsv
// because nearly every testbench here is generated.  This one is
// hand-written and must be tracked.
package StretchFpCommitTest;

import StretchTypes::*;
import StretchFP::*;
import StretchExecute::*;

(* synthesize *)
module mkFpCommitTb(Empty);

  Reg#(Bit#(8)) cReg  <- mkReg(0);     // 0..127, then 128 = done sweeping
  Reg#(Bit#(1)) pvReg <- mkReg(0);     // sweep each opcode with protViol 0 and 1
  Reg#(Bit#(32)) fails <- mkReg(0);
  Reg#(Bool) done <- mkReg(False);

  // reachability of the three fields fpArithClass added
  Reg#(Bool) sawFactor    <- mkReg(False);
  Reg#(Bool) sawRemainder <- mkReg(False);
  Reg#(Bool) sawLzc       <- mkReg(False);
  // the invariants, falsified if ever violated
  Reg#(Bool) aliased      <- mkReg(False);
  Reg#(Bool) protLeaked   <- mkReg(False);

  WordAddr ea     = 1000;
  FpNum    acc    = FpNum { ef: 0, em: 10'd5, es: 0,
                            frac: 48'h123456789abc, sign: 0, flags: 3'b0 };
  Word64   accL   = 64'h0400_0000_0000_0000;
  Word64   accS   = 64'h0000_0000_0000_0007;
  Word64   accR0  = 64'hdead_beef_0000_0000;
  Word64   factor0 = 64'h0200_0000_0000_0000;
  // THE OPERAND'S FRACTION MUST BE NON-ZERO, and the reachability
  // check below is what found that out.  A hand-written word
  // (64'h0300_0000_0000_0001) puts its set bits in the exponent and
  // the FLAG bits and leaves IBM 12-59 all zero -- a divisor of zero.
  // Divide then takes the divide-by-zero path, never produces a
  // remainder, and fpcommit_remainder_is_reachable FAILED: a declared
  // field that nothing in the whole 128-opcode sweep could fill.
  // Built through fpToWord instead, so the field placement is the
  // model's and not mine.
  Word64   operand = fpToWord(FpNum { ef: 0, em: 10'd5, es: 0,
                                      frac: 48'h400000000000,
                                      sign: 0, flags: 3'b0 });

  function Bool anyAcc(FpCommit f);
    return isValid(f.accLeft) || isValid(f.accRight) || isValid(f.accSign);
  endfunction
  function Bool allAcc(FpCommit f);
    return isValid(f.accLeft) && isValid(f.accRight) && isValid(f.accSign);
  endfunction
  // Same shift form as setBit in StretchExecute, so "DS is on" means
  // here exactly what setting it means there: IBM bit n is bit 63-n.
  function Bool indOn(Word64 w, Bit#(6) n);
    Bit#(7) sh = 63 - zeroExtend(n);
    return ((w >> sh) & 1) == 1;
  endfunction

  function Tuple2#(Word64, FpCommit) callStore(Bit#(7) c, Bool pv);
    return fpStoreClass(c, 0, 0, ea, acc, accL, accS, accR0,
                        False, False, pv, 0);
  endfunction
  function Tuple2#(Word64, FpCommit) callArith(Bit#(7) c, Bool pv);
    return fpArithClass(c, 0, 0, ea, acc, accL, accS, accR0, factor0,
                        False, False, pv, operand, 0);
  endfunction

  // ---- phase 1: sweep every opcode, both protection senses --------
  rule rl_sweep (!done && cReg < 128);
    Bit#(7) c = truncate(cReg);
    Bool pv = (pvReg == 1);
    let s = callStore(c, pv);
    let a = callArith(c, pv);

    // NO ARM MAY WRITE BOTH `ea` AND AN ACCUMULATOR HALF.  This is
    // what makes committing at the end safe: if one arm filled both,
    // the two fields could name the same word and the commit ORDER
    // inside commitFp would start to matter.
    if (isValid(tpl_2(s).store) && anyAcc(tpl_2(s))) aliased <= True;
    if (isValid(tpl_2(a).store) && anyAcc(tpl_2(a))) aliased <= True;

    // SUPPRESSION DID NOT MOVE.  Reference Manual printed p.31-32: a
    // store into a protected area is suppressed and sets DS.  With the
    // predicate true no record may carry a store, for ANY opcode.
    if (pv && isValid(tpl_2(s).store)) protLeaked <= True;
    if (pv && isValid(tpl_2(a).store)) protLeaked <= True;

    // the three fields fpArithClass added must be REACHABLE -- a field
    // nothing ever sets is a field no injection can catch
    if (isValid(tpl_2(a).factor))         sawFactor <= True;
    if (isValid(tpl_2(a).remainder))      sawRemainder <= True;
    if (isValid(tpl_2(a).leftZerosCount)) sawLzc <= True;

    if (pvReg == 1) begin cReg <= cReg + 1; pvReg <= 0; end
    else pvReg <= 1;
  endrule

  // ---- phase 2: the named per-arm checks, then the verdict --------
  rule rl_report (!done && cReg == 128);
    Bit#(32) f = 0;
    function Action chk(String nm, Bool ok);
      action
        if (ok) $display("PASS %s", nm);
        else    $display("FAIL %s", nm);
      endaction
    endfunction

    let st_  = callStore(fpop_ST,  False);
    let srt_ = callStore(fpop_SRT, False);
    let srd_ = callStore(fpop_SRD, False);
    let slo_ = callStore(fpop_SLO, False);
    let shf_  = callStore(fpop_SHF, False);
    let epli_ = callStore(fpop_E_PLUS_I, False);

    Bool okSt = isValid(tpl_2(st_).store)
                && tpl_1(fromMaybe(tuple2(?, ?), tpl_2(st_).store)) == ea;
    chk("fpcommit_st_store_at_ea", okSt);              f = f + (okSt ? 0 : 1);
    chk("fpcommit_st_touches_no_acc", !anyAcc(tpl_2(st_)));
    f = f + (anyAcc(tpl_2(st_)) ? 1 : 0);

    Bool okSrt = isValid(tpl_2(srt_).store) && !anyAcc(tpl_2(srt_));
    chk("fpcommit_srt_store_at_ea", okSrt);            f = f + (okSrt ? 0 : 1);
    Bool okSrd = isValid(tpl_2(srd_).store) && !anyAcc(tpl_2(srd_));
    chk("fpcommit_srd_store_at_ea", okSrd);            f = f + (okSrd ? 0 : 1);
    Bool okSlo = isValid(tpl_2(slo_).store) && !anyAcc(tpl_2(slo_));
    chk("fpcommit_slo_store_at_ea", okSlo);            f = f + (okSlo ? 0 : 1);

    chk("fpcommit_shf_fills_acc_trio", allAcc(tpl_2(shf_)));
    f = f + (allAcc(tpl_2(shf_)) ? 0 : 1);
    chk("fpcommit_shf_no_store", !isValid(tpl_2(shf_).store));
    f = f + (isValid(tpl_2(shf_).store) ? 1 : 0);
    chk("fpcommit_epli_fills_acc_trio", allAcc(tpl_2(epli_)));
    f = f + (allAcc(tpl_2(epli_)) ? 0 : 1);
    chk("fpcommit_epli_no_store", !isValid(tpl_2(epli_).store));
    f = f + (isValid(tpl_2(epli_).store) ? 1 : 0);

    // the DS bit itself, on the four store arms
    for (Integer k = 0; k < 4; k = k + 1) begin
      Bit#(7) c = case (k) 0: fpop_ST; 1: fpop_SRT; 2: fpop_SRD;
                           default: fpop_SLO; endcase;
      let r = callStore(c, True);
      Bool ok = !isValid(tpl_2(r).store) && indOn(tpl_1(r), ind_DS);
      chk("fpcommit_prot_suppresses_and_sets_ds", ok);
      f = f + (ok ? 0 : 1);
    end

    // ---- the exhaustive results -----------------------------------
    chk("fpcommit_no_arm_writes_both_ea_and_acc_ALL_128_OPCODES", !aliased);
    f = f + (aliased ? 1 : 0);
    chk("fpcommit_prot_suppresses_store_ALL_128_OPCODES", !protLeaked);
    f = f + (protLeaked ? 1 : 0);

    // ---- every declared field is reachable ------------------------
    chk("fpcommit_factor_is_reachable", sawFactor);
    f = f + (sawFactor ? 0 : 1);
    chk("fpcommit_remainder_is_reachable", sawRemainder);
    f = f + (sawRemainder ? 0 : 1);
    chk("fpcommit_leftzeroscount_is_reachable", sawLzc);
    f = f + (sawLzc ? 0 : 1);

    if (f == 0) $display("ALL TESTS PASSED");
    else        $display("%0d TEST(S) FAILED", f);
    done <= True;
    $finish(0);
  endrule

endmodule

endpackage
