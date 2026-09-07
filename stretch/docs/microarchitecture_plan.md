# Stretch microarchitecture plan: from ISA model to the real machine

Written 2026-09-03 on the owner's instruction: *"make the microarchitecture
the same as the original stretch, this includes pipelining and the other
tricks they did."* This supersedes the founding scope statement in
`bsv/README.md` ("ISA-level correctness, not the famous pipelined
microarchitecture"). Everything the project built up to this point --
the STRAP assembler, the listing oracle, and above all the suite of
verbatim 1961 diagnostic programs -- becomes the correctness oracle for
the rewrite.

## 1. Scope: a cycle-accurate replica, every documented feature, and the folklore

**Target (owner's instruction, 2026-09-03): a cycle-accurate replica of
the IBM 7030 Stretch that corresponds to every documented feature and
to the folklore.** That means:

- *Cycle-accurate*: for any program, the model's clock count matches
  what the real machine's documented timing says -- IBM's Performance
  Characteristics tables and worked examples, Blosk's and the CE
  manual's timing charts, and vol.2's measured benchmarks are the
  oracles; a discrepancy is a bug in the model until a source shows
  the document was wrong.
- *Every documented feature*: everything the Reference Manual, the
  pocket card, Buchholz, Blosk, the CE manuals and the diagnostics
  describe the machine as doing -- the whole instruction set including
  what is unimplemented today (floating-point arithmetic, decimal VFL,
  radix conversion, EX/EXIC, LVE/SVA/RNX/LVS, bit branching, swap and
  backward transmit, all I/O and channel functions), the interrupt
  system with its mask and left-most-one priority, boundary
  protection, the interval timer and time clock, the maintenance
  console's manual controls and repeat mode, ECC and parity checking
  with their indicators, memory interleaving and the bus priorities,
  the look-ahead's forwarding, recovery and housecleaning, the
  I-box's branch guess and updated indicators, index storage's
  destructive read and two-cycle write, the two arithmetic units and
  their register sharing.
- *The folklore*: the behaviors the machine was known for, which the
  documents describe as consequences rather than features -- that
  successful branches empty the buffers and cost a refetch; that a
  store close to a fetch stalls or forwards; that consecutive stores
  fight over the single LAAR; that a VFL crossing a word boundary
  costs extra levels; that I-box instructions load recovery levels
  and can leave the E-box idle; that the machine appears sequential
  despite everything in flight; that it delivered less than the
  promised speed (the performance figures in Perf. Char. §2 and
  Buchholz §15.7 are part of the record, not embarrassment to hide).
  §1a below is the running inventory of both, each with its source
  and status, and grows whenever a source turns up something new.

The 7030 was built from ~170,000 transistors in current-mode logic with
ECC on every memory word and parity on every internal register. The
model reproduces the machine at the level its own designers described
it: the functional units, their registers and buses, the buffering
between them, the interlocks that keep out-of-sequence execution
invisible, branch guessing and recovery, and the cycle timing of each
unit. It does not reproduce gate-level logic or physical clock
distribution; the error-checking hardware is modeled as the pipeline
stages it occupied plus the indicators and interrupts it raised (the
"I checker" takes a cycle whether or not there is an error), with the
correction algorithms themselves modeled only insofar as a diagnostic
exercises them.

### 1a. Feature and folklore inventory (living)

Status: **done** = modeled and tested; **partial**; **planned** (stage
in parentheses); **open** = no stage assigned yet.

| Item | Source | Status |
|---|---|---|
| Six interleaved 16K-word 2.1 µs memory units, MBCU busy handling | Buchholz §14.1/14.3 | done (stage 1); 8-channel priority partial |
| Bus return tags per requester | Blosk p.19 | done for operand/1Y/2Y; LA levels planned (3) |
| 1Y/2Y instruction buffers, I-checker cycle, program-store compare | Blosk pp.10, 15, 21 | done (2a); compare is conservative |
| Successful branch empties the buffers and refetches | Perf. Char. p.3-17, Blosk p.35 | done (2a); overlap of the refetch inside CB's sequence planned (2b/3) |
| Per-class I-box instruction times (tables 4-8) | Perf. Char. §3 | done as budgets (2b) |
| FP/VFL preparation cycles; VFL SAU equation | Blosk figs 6-7; Perf. Char. tables 2-3 | done as budgets (2b); overlap with E-box planned (3/4) |
| Y-to-Z transfer, index fetch, modification, WBC as explicit register stages | Blosk pp.13-14, 31; CE figs 3.1.6-3.1.24 | planned (2b/2c) |
| Index storage destructive read, 2-cycle write, word 17 timer/clock | Blosk p.11 | planned (2c) |
| Updated indicator register; index-indicator branches resolved in the I-box | Blosk p.17 | planned (2c) |
| Arithmetic-conditional branch guessed not taken; wrong-way recovery | Buchholz §15.2; Perf. Char. p.3-23 | done (3c), by snapshot rather than per-instruction recovery levels |
| Four look-ahead levels, five counters, tags, indicators, IC per level | Buchholz §15.3 | partial (3a): levels, in-order removal, fetch-ahead; the five counters' separate interlocks are collapsed into head/tail |
| LAAR, forwarding, store-close-to-fetch cases (1)-(3) | Buchholz §15.4; Perf. Char. pp.3-20..21 | partial (3a/3b): same-word waits and Y invalidation; no data forwarding yet |
| I-box instructions load index-recovery pseudo-store levels | Perf. Char. p.3-22; Blosk p.33 | partial (3c): one snapshot per guess stands in for them; their per-level cost is not charged |
| Interrupt recovery / housecleaning | Buchholz §15.6; CE figs 3.2.22-23 | planned (3) |
| Serial and parallel arithmetic units, A/B and C/D registers | Buchholz §14.4 | planned (4) |
| Floating-point arithmetic (all ops), timing per table 2 and CE figs 3.8.x | Ref. Manual pp.78-94; CE 3.3.x/3.8.x | partial (4c): single-precision L/LWF/+/+MG/M+/M+MG/ST/K/KMG/KR/KMGR/*/E+/E+I/SHF; divide, double precision, root (SRT), LFT, *+, F+ open. K compare VERIFIED against jb_af1c F202A1-6/A15-20 (all of AL/AE/AH, normal + XFN/XFP ranges). jb_af1c F202G (KR Compare-for-Range, p.45) RUNS and passes (`fp_compare_f202g.strap`, `verify_fp_compare_g_listing.py`): `Z,$IND` clears indicators (b1a6ad0), `BB1,$AH` sets the gate (63721f1), and KR was fixed to p.91 -- it sets AE to "accumulator low" and leaves AL and AH unchanged (the range path had wrongly set AH := acc>=opnd). Discriminating on KR's AE via G15. (F202G's own operands do not distinguish the AH-leave-vs-set aspect -- its AH-preset sub-tests all have cmp>=0 -- but p.91 mandates leaving AH.) |
| Decimal VFL, radix conversion, VFL multiply/divide | Ref. Manual; CE 3.11.x | open |
| Branch on Bit (BB/BB1/BBN/BBZ/BZB/BZB1/BZBN/BZBZ): test one bit anywhere in storage, take the branch if it matches instruction bit 62, then set the bit per bits 60-61 whether or not the branch was taken | Ref. Manual p.41; X22-6533 pocket card "BRANCH ON BIT" | executed, including a BB that changes an INDICATOR-register bit (word 11, positions 20-63, p.41 -- folded into `ind` rather than the no-op writeWord(11)) (StretchExecute BitBranch arm; `strap/programs/bb_branch_on_bit.strap`, `bb_indicator.strap`, `verify_bb_encoding.py`, `verify_bb_listing.py`) |
| EX/EXIC (with LA drains, table 6; Ref. Manual pp.49-50: subject instruction may not change the interruption state or the IC -- EXE indicator; pseudo-IC stepped after fetch, before execution), LVE, SVA, RNX, LVS, swap/backward transmit | Ref. Manual pp.26-30 (LVE: indirect addressing, 1 ms limit -> USA; SVA: replaces the 18/19/24-bit address field per the target's class; RNX: rename via X0's refill; LVS: sum of the value fields selected by address bits 0-15; T/SWAP: count rules, backward stepping); Perf. Char. table 6 | open, specified |
| Interrupt system: indicators, mask, left-most-one, the "free instruction" | Ref. Manual pp.43-50 (indicator list with mask/class per indicator, definitions, mask register: bits 0-19 always 1, 20-47 settable, 48-63 always 0; interruption address register; the single interruption instruction fetched from IA + leftmost indicator number, IC not stepped, executed before a second interruption); Blosk pp.16-17; Buchholz ch.10 | open, specified |
| Address Invalid (AD): effective word address beyond installed core -> AD + no-op | Ref. Manual p.20 | partial: floating-point operand addresses (StretchExecute Fp arm); other classes open |
| Storage protection: two address boundary registers (word 3: UB bits 0-17, LB 32-49, control bit 57), alarm on an effective address inside OR outside the region (control-bit selectable), storing in protected areas suppressed, indicators DS (store)/DF (fetch)/IF (instruction fetch), gated by the interrupt system + mask | Ref. Manual p.15 "Address Monitoring", indicator defs pp.44-45, Appendix C (word 3 layout) | specified (overview); the control-bit polarity (which value protects inside vs outside) still needs Appendix C / the CE manual before implementing -- the closest 7030 analogue to a mandatory-access-control model |
| Interval timer and time clock | Ref. Manual p.15 "Clocks" (interval timer measures a short interval, settable, sets an indicator (Time Signal, TS) when the period ends, can cause an interrupt; time clock runs continuously, not programmer-alterable, for logging/time-of-day); word 1 = timer bits 0-18 + clock 28-63 (Appendix C); rate per Blosk p.6 | specified; needs the exact step rate confirmed before implementing |
| ECC/parity: check cycles, correction, indicators, I-checker conflicts | Blosk p.15; Perf. Char. p.3-19 | partial (check cycle only) |
| Exchange as a bus requester with real overlap; disk synchronizer | Buchholz ch.16 | open (I/O is a synchronous FSM today) |
| Maintenance console: start/stop, display/store, single step, repeat mode, index-storage test | Blosk p.6 | open |
| Measured benchmark timings (GERB2 etc.) | Perf. Char. vol.2 | planned (5) |

### 1b. Execution roadmap (prioritized)

The order below is the intended attack, most-actionable first. It is
codesign-driven: each item is validated by running real historical
source (the `jb_af1c` FP diagnostic, the I-Box decks, the DCP) with the
listing-oracle-then-run-then-injection pattern (AGENTS.md), not by
hand vectors alone. "Enables" notes the dependency chain.

1. **Finish the FP-compare family.** DONE (`20edcf9`): KR/KMGR range
   path fixed per Ref. Manual p.91 and `jb_af1c` F202G (p.45) runs
   bit-exact; K/KMG were already verified via F202A1-6/A15-20. The
   whole COMPARE family (K/KMG/KR/KMGR, all of AL/AE/AH, normal and
   extreme ranges) is now validated against the diagnostic.
2. **FP arithmetic against the diagnostic** — the largest FP gap and
   the E-box's core; **the current focus now that item 1 is done.**
   The routine is LOCATED (no hunting needed): `jb_af1c` F204 "ADD TO
   MEM TEST ROUTINE" / F204A "ARITHMETIC CHECKS", p.53, octal
   012325.40+ (sub-tests F204A1-A7). Each does L/ST to set a memory
   operand, then M+ (Add to Memory) an operand across the XFP/XFN/N
   exponent ranges, then a CT0110 connective test of the result and
   BRGZ (result-greater-zero) to the error routine -- "ERROR IF
   FRACTIONS ADDED" (it checks that far-apart exponents do not add the
   fractions). All instructions it uses (L, ST, M+, CT0110, SIC, BRGZ)
   are implemented; F204A1-3 are transcribed (`fp_arith_f204a.strap`)
   and assemble BIT-EXACT (`verify_fp_arith_f204a_listing.py`, in the
   suite) and run to PASS -- but only as encoding checks, because
   F204A1-3's "error if fractions added" passes even for an M+ that
   leaves the sum unchanged (far-apart exponents drop the low operand).
   The DISCRIMINATING M+ test is DONE: F204A5 (`fp_arith_f204a5.strap`,
   in the suite as encoding + model run) uses N-range operands and
   checks the sum FPK35+FPK39 against a precomputed FPK32 via
   CT0110+BRGZ; the model passes, and an injection making fpAdd drop the
   added operand halts at SERS, so it genuinely catches a broken M+. So
   M+ (FP add to memory) is now verified against the diagnostic.
   F204B "TEST SIGN + MOD COMBS" (pp.55-58) is DONE too
   (`fp_arith_f204b.strap`, 183 words bit-exact, all sixteen sub-tests
   pass on the model): M+/M+A/M-/M-A over every memory-sign /
   accumulator-sign combination, establishing p.81-82's rule (A on the
   storage operand, N on the accumulator) -- and its first run caught a
   real bug, the order-of-magnitude-zero sign on an exponent tie
   (p.82: the modified ACCUMULATOR sign; fpAdd took its first operand's,
   which for the M+ family is the storage word). F204C "TEST UNCHANGED
   REGS" (p.59) and F204D "INDICATOR TESTS" (pp.60-64, sixteen
   sub-tests: MOP, RLZ/RN, RZ, RGZ, PSH, LC, LS, XPFP/XPO/XPH/XPL/XPU)
   are DONE and in the suite; each caught a real bug on its first run:
   F204C the accumulator layout (the VFL sign lived in bit 0 of word 8
   over a 127-bit magnitude, and word 10 held its low byte -- now 128
   magnitude bits and the sign byte at IBM bits 0-7 of word 10, sign
   in bit 4, shared by VFL and FP), F204D a look-ahead ordering bug
   (Z,$IND ran ahead of the unretired E-box load that sets XPL; an
   I-box store to words 7-15 now drains the look-ahead, StretchIBox
   `eboxRegister`). F204E "TEST NORMALIZATION MODIFIER" (p.65, six
   sub-tests of M+(N)) is DONE too; its first run caught fpAdd
   suppressing post-normalization of the unflagged survivor of
   XFN + N (the modifier is ignored only when the RESULT is flagged).
   The whole F204 family (A-E: add to memory) is now verified against
   the diagnostic. F205 (ADD TO MAGNITUDE, pp.66-74) is DONE as well:
   F205A (nine arithmetic checks; caught the flagged-operand path
   skipping the forced-zero rule), F205B (thirty-two sign/modifier
   combinations; the result keeps the accumulator's own sign, forced
   zeros included -- and its arithmetic disambiguated the scan of
   FPK23, "230" vs "250"), F205C/D (unchanged registers, the LS
   indicator). F206A (ADD MAGNITUDE TO MEMORY, pp.75-77, fifteen
   arithmetic checks) follows: it caught fpAdd running ONE forced-zero
   rule for both directions. p.89 gives the to-memory form its own --
   the sum's sign is compared with the ADDRESSED operand's, and the
   forced zero takes that operand's sign and exponent, not the
   surviving operand's (A9: XFN -2047 negative in storage under XFN
   -1791 positive in the accumulator wants -2047 with sign 1). The
   accumulator operand's sign is also the one assumed positive there,
   and assumed positive BEFORE the negative-sign modifier (the M-MG
   mnemonic, not the (N) that selects normalization), so that had to
   move out of fpAdd into the M+ arm. F206B (pp.78-84, thirty-two sign
   and modifier combinations, the mirror of F205B) followed and caught
   the last piece: the result keeps the ADDRESSED operand's own
   original sign whatever the sum's, the mirror of p.88's "in an ADD TO
   MAGNITUDE operation, the sign byte register bit position 4 never
   changes" and of F205B's rule for the accumulator direction. B19/B24
   are the discriminating pair -- A makes the memory operand's sign
   positive for the arithmetic only. B23 vs B24 also confirms that the
   forced-zero comparison uses the A-modified sign, and B9-B16 that the
   accumulator operand's sign is the one assumed positive. Assembler:
   M-MG / M-MGA accepted as M+MG with N / N+A (.52 / .72). F206C
   (p.85, unchanged registers) and F206D (pp.86-88, the LS indicator
   and the five exponent-range indicators) close the family; both
   passed as the model stood, and F206D1 against F206D3 is what earns
   the `sum != 0` forced-zero guard written blind for F206A -- removing
   it halts D1 at 014304.40. The whole ADD MAGNITUDE TO MEMORY family
   (F206A-D) is now verified against the diagnostic.
   **Correction to the order (established 2026-09-05 by reading the
   routine banners of pp.89-140): the multiply block is NOT next.**
   What jb_af1c reaches after F206 is DOUBLE PRECISION -- F207 LOAD
   DOUBLE (A arithmetic, B unchanged registers, C, E load double with
   flag, pp.89-96), F208 ADD DOUBLE (D+), F209 DOUBLE ADD TO MAGNITUDE
   (D+MG / D-MGA) and STORE ROUNDED (SRD) -- and it only gets to F212
   F+ (add to fraction) and F213 E+I (add immediate to exponent)
   around pp.128-135, with multiply later still. So the next codesign
   step is not another transcription but the double-precision datapath
   the model does not have: the 96-bit fraction across the
   accumulator's two halves, DL/DLWF, D+/D+MG/D-/D-MGA, SRD/SLO/LFT.
   Transcribing F207 needs only DL/DLWF plus connectives already in
   hand, so that is the natural first increment, and it is DONE: DL and
   DLWF are implemented (StretchExecute's Fp arm writes all three
   accumulator words -- left, right, sign byte -- clearing IBM bits
   60-107 and keeping 108-127; `fpNormalize96Wide` in StretchFP now
   returns the whole 96-bit normalized fraction, since noisy mode's
   one-bits land in bits 60-107 for the double-precision family, and
   the old 48-bit `fpNormalize96` is a slice of it). F207A (p.89, five
   sub-tests) passes, and its bits-60-107 check is discriminating --
   making DL leave the right half alone halts it at 014461.00. The
   assembler already encoded DL/DLWF from FP_CODES, verified against
   the listing's own 22205.44 60 / 22006.44 60 / 22167.04 60 -- all
   three DL forms. CORRECTION to 057e47d's commit message, which also
   listed 22205.46 60 for DLWF(U) as one of "the listing's own": that
   one is this assembler's output and has not been checked against any
   printed line. F207E carries real DLWF encodings and will settle it.
   Untested in what 057e47d shipped, worth knowing before building on
   it: DLWF has no coverage at all; noisy mode has none (it is the only
   case where DL leaves bits 60-107 non-zero); and neither does the
   generated-EF path where a DL(N) normalization drives the exponent
   past -1024. The last is safe by inspection -- fpMakeExp passes its
   fraction argument through untouched, so the high half taken from
   `v.frac` and the low half taken from `f96` cannot disagree -- but
   that is inspection, not a run.
   F207B (bits 108-127 survive) and F207C/F207D (the sign byte's flag
   bits zeroed; the data flag indicators follow the addressed operand)
   are DONE too. F207C1 found a REAL INTERLOCK BUG -- see the
   store-close-to-fetch note in §7: the look-ahead's fetch wait
   compares against earlier levels' STORE targets, and storeTarget()
   reports only stores to storage, so an FP write to one of the
   E-box's own registers (words 7-15) did not hold a following VFL or
   connective fetch of that word. A level fetching 7-15 now waits for
   the newest earlier level whatever it does.
   F207E (DLWF) is DONE too and passed as the model stood, which also
   settles the encoding note above: 22007.46 60 and 22142.46 60 are
   now listing-verified. Its E2 is the discriminating case -- FK0 is
   zero everywhere but its three flag bits, so a DLWF that ignored
   them passes every arithmetic check and fails only the sign byte
   (halts at 014602.40). The whole LOAD DOUBLE family (F207A-E) is now
   verified against the diagnostic. **D+ (ADD DOUBLE) is implemented
   and verified too**: `FpDouble`/`fpAddDouble` in StretchFP work on
   the accumulator's whole 96-bit fraction (IBM 12-107) against a
   storage operand extended with 48 low-order zeros, with the three
   differences from ADD the manual states -- the fractions are 96 bits
   rather than 48 extended to 96, so a preparatory shift LOSES what it
   pushes past the right end; PSH is still "difference exceeds 48";
   and noisy mode does not pre-extend the operands. The WHOLE of
   jb_af1c F208A (pp.93-96, A1-A20: nine unflagged, five flagged, five
   normalization-modifier and A20) passes, and the block's address
   arithmetic closes on 015026.40, where the listing's own exit
   sequence (BD,$+1.0 / B,FAD1 / SIC,SENO+.32 / B,SSW) begins.
   Four injections, each halting in its own quarter: D+ reading
   only the accumulator's high 48 bits halts at 014617.40 (A1); the
   flagged path dropping the surviving operand's low half halts at
   014732.00 (A10) while A1-A9 still pass -- worth having, since that
   path returns an operand whole rather than computing anything, so
   nothing unflagged would have noticed it losing 48 bits;
   normalizing only the high 48 bits halts at 015014.00 (A19); and
   dropping the normalization exponent adjustment on the UNFLAGGED
   branch halts at A20's own exponent check while A1-A19 pass.
   That last one separates two things that read alike. A15-A19 all use
   D+(N), but every one of them has a flagged operand, so the
   normalization they do (or, for A15-A18, the suppression of it)
   happens inside the flagged branch. A20 is the only sub-test in the
   routine that normalizes an unflagged 96-bit sum -- and the only one
   whose result exponent is checked on its own, 12 bits at accumulator
   offset 116 (IBM 0-11), with the fraction checked as two separate
   48-bit fields at offsets 68 and 20 rather than folded into a
   60-bit check. Its arithmetic sits exactly on the PSH boundary: the
   exponents differ by 48, so the operand shifts out of the high half
   into the low half exactly, and the 12-place normalization then
   pulls bits back across that boundary (50 - 12 = 38, the exponent
   FK101 checks).
   Constant-pool addressing worth recording: FKn (n decimal) sits at
   octal 022141 + n, not 022142 + n -- one FK number is skipped
   between FK48 and FK101, so the later constants run one address
   below the naive formula. Verified: FK46=022220, FK47=022221,
   FK48=022222, FK101=022306, FK105=022312.
   jb_af1c F208B (pp.96-98, B1-B7: "TESTS OF SIGN AND MODIFIER
   COMBINATIONS") passes too, closing on 015123.00 where the listing's
   own exit begins. It sweeps D+, D+A, D-, D-A against both
   accumulator signs -- the two accumulator signs from DL versus DLN,
   the two memory signs from FPK39 versus FPK40, which is the same
   word with the sign bit set -- and checks each result on both
   fraction halves AND on the sign bit itself, with BB/BZB on the
   accumulator sign byte at 10.04. The model needed nothing: D+
   already took its operand's sign from the modifier-applied FpNum and
   DL already did the same. Only the assembler did -- D- and D-A had
   no rule, exactly as M-/M-A and -MG/-MGA had none before their own
   blocks; D+A needed none, since the generic "A" suffix strips to D+.
   Two injections halt at B3's low order check (015055.40) with the
   whole of F208A still passing: D+ reading the raw operand sign
   instead of the modifier-applied one, and the unlike-signs magnitude
   subtraction replaced by an addition. The second is the one worth
   recording -- every operand F208A adds is positive on the unflagged
   path, so until F208B the unlike-signs branch of fpAddDouble had
   never been entered at all. Three hundred passing rows of ADD DOUBLE
   arithmetic that never subtracted.
   Still unreached in double precision, and stated rather than
   assumed: the sub-branch where the SMALLER-exponent operand has the
   larger magnitude, so the result takes ITS sign. Forcing that arm to
   the wrong sign leaves both F208A and F208B green, so no check in
   either block distinguishes it.
   jb_af1c F208C (p.98, C1-C2, "TEST UNCHANGED REGISTERS") found a
   real bug -- the first one in this stretch of work that the listing
   caught rather than confirmed. D+ works on IBM bits 12-107, so two
   fields must survive it untouched: accumulator right bits 44-63
   (IBM 108-127) and sign byte bits 5-7, the data flags. C1 checks
   both from zero, C2 from ones: C1111 forces both accumulator halves
   to all ones and CM1111 forces the whole sign byte to ones, then
   D+(U) FPK0.
   That is the discriminating case, and it discriminates twice over.
   FPK1 is all ones INCLUDING its flag bits, so the accumulator's
   flags are 111 going in while FPK0's are 000; and an all-ones
   accumulator has EF = 1, so the add takes the FLAGGED path, where
   Figure 23 hands back one operand WHOLE. The model wrote that
   operand's flags into the sign byte and C2 halted at 015141.00's
   check. The fix is to take bits 5-7 from accS and say so, rather
   than from the result -- on the unflagged path the two agree, which
   is why nothing before noticed.
   The same hole was in fpAdd's flagged path, reached by + and +MG
   through the identical fpSignByte(r.res, accS) call, and is fixed
   the same way. That half is NOT under the oracle and should not be
   claimed as such: jb_af1c has no "TEST UNCHANGED REGISTERS" routine
   for plain ADD -- F203 ends at F203B, the exponent-range indicator
   test, with F204 beginning straight after -- and F205C checks +MG's
   sign byte bits 0-3 only, not 5-7. It rests on p.86 being ADD's own
   page and on the code path being the same one F208C2 proved.
   jb_af1c F208D1-D6 (pp.98-99, "INDICATOR TESTS") caught a second
   real bug, in Lost Significance. D1 against D2 is the same addition
   one modifier apart -- FPK21 + FPK21 unnormalized sets LC, and
   normalized does not, because the normalizing right shift keeps the
   carry. D3 against D4 is p.96's "at least one operand is non-zero"
   clause: an exact cancellation sets LS, FPK0 + FPK0 does not.
   D5 is the one that bit. Its accumulator is
   0xffffffffffff400000000000 and its operand shifts right 47 places
   to 0xc00000000000, so the 97-bit sum is a 1 followed by 96 zeros:
   the carry is lost and what lands in the accumulator is 96 zeros.
   LS was testing the 97-bit intermediate, saw a non-zero value and
   stayed off; p.96 asks whether "the 96 bits of the RESULT fraction
   are zero", and the listing demands LS on. Fixed by testing
   res.frac. zeroResult, on the 97-bit sum, is left alone -- it serves
   the separate normalization-suppression rule.
   D6 is the only sub-test in the block that says anything about the
   flagged path's indicators: FK35 is flagged and FK32 is in the N
   range, so Figure 23 returns one operand whole rather than adding,
   and although that operand's fraction is zero, LS must stay off,
   because nothing was lost. The model already did this (the flagged
   branch never sets ls) and D6 now holds it in place.
   The same LS fix was applied to single-precision fpAdd. As with the
   sign-byte flags in F208C, that half is NOT under the oracle: no
   single-precision sub-test in the suite distinguishes the two forms,
   because F204D's and F206D's LS tests reach the indicator only
   through exact cancellations, where the intermediate sum and the
   result fraction are both zero. That is now twice in this series
   that double precision has proved a rule single precision states but
   does not test -- worth remembering as a standing asymmetry in
   jb_af1c's coverage rather than a claim about the model.
   jb_af1c F208D7-D11 (pp.99-100) completes F208 and closes on
   015265.00, the listing's own exit. Five sub-tests, one per
   exponent-range indicator -- XPFP, XPO, XPH, XPL, XPU -- each
   asserting its own is on and the others off after a single D+, with
   Z,$IND clearing everything first. All five passed on the first run.
   Their value is coverage rather than a fix: this is the only place
   in the suite that checks D+'s range indicators at all. Making D+
   never report a propagated exponent flag leaves F208A, F208B, F208C
   and F208D1-D6 all green and halts at D7's XPFP check, SIC storing
   015173.00.
   The "off" lists are not uniform and are transcribed as printed: D7
   checks five, including ZM at 11.33, while D8-D11 check only the
   four other exponent-range bits. Nothing in the listing explains why
   D7 alone looks at ZM.
   With that, ADD DOUBLE is done end to end: A (arithmetic), B (signs
   and modifiers), C (unchanged registers), D (indicators), every
   block closing on the listing's own exit address, and 342 code rows
   read off the printed encoding column individually.
   jb_af1c F209A (pp.101-102, A1-A9) adds ADD DOUBLE TO MAGNITUDE.
   fpAddDouble gained an `addMag` flag -- no accIsB, since there is no
   ADD DOUBLE MAGNITUDE TO MEMORY -- forcing the accumulator's sign
   positive before the add, forcing a zero when the sum comes out
   negative (with the `sum != 0` guard F206A pinned, since an exact
   cancellation is an order-of-magnitude zero, not a sign reversal),
   and leaving LS off for a forced zero. The D+MG arm restores the
   accumulator's own sign afterward, as +MG's does. All nine passed on
   the first run.
   What F209A does NOT do is worth more than what it does. Every
   operand in all nine sub-tests is positive, so no sum is ever
   negative and the forced zero is never reached; eight of the nine
   take the flagged path, and the one unflagged sub-test (A5) does not
   force a zero either. Disabling every addMag rule -- the sign
   forcing, both forced-zero arms, and the sign restore -- leaves the
   program passing. So F209A proves D+MG is decoded and computes what
   D+ computes, and nothing about ADD TO MAGNITUDE's own behaviour.
   That also leaves unresolved the question of which exponent a forced
   zero keeps on the unflagged path: fpAdd uses `big`'s, the manual's
   words say the accumulator's, and F205A7 settled the FLAGGED case in
   favour of the survivor's. No sub-test yet reaches the unflagged
   forced zero in either precision.
   Two more things the diagnostic itself gets odd, transcribed as
   printed: A1's low order check has no SIC/BRGZ after it, so its
   result is computed and never acted on (the address arithmetic
   confirms it -- A2 starts eleven half-words after A1, not thirteen);
   and sub-tests 5 and 6 are labelled F209D5/F209D6 between A4 and A7,
   almost certainly a typo in the SSIP source.
   jb_af1c F209B1-B8 (pp.102-104) is the block F209A could not be. It
   sweeps D+MG, D+MGA, D-MG and D-MGA against both accumulator signs
   -- DL versus DLN -- and checks each result on both fraction halves
   and then on the sign bit itself. D-MG and D-MGA needed rules in
   strap_asm.py's strip_fp_sign, the same shape as D-/D-A before them
   (D+MG = .46, D+MGA = .66, D-MG = .56, D-MGA = .76). All eight
   passed on the first run.
   Two of D+MG's four magnitude-specific rules are now covered, both
   by B5, the first sub-test with a DLN accumulator: not forcing the
   accumulator's sign positive before the add halts at B5's low order
   fraction check (SIC stores 015433.40), and not restoring the
   accumulator's own sign afterward halts at B5's sign bit check
   (015437.40).
   The other two are still NOT covered, and this was checked rather
   than assumed: disabling either forced-zero arm, flagged or
   unflagged, leaves all eight passing. Every sub-test here uses FPK39
   as its memory operand and checks a non-zero result, so no sum comes
   out negative and no zero is ever forced. The unflagged forced zero
   is also what would settle which exponent it keeps -- fpAdd's `big`
   against the manual's "accumulator operand" -- still open.
   jb_af1c F209B9-B13 (pp.104-105) does the same sweep with the MEMORY
   operand negative -- FPK40, and FK119 at 022330, which holds
   identical bits. All five passed on the first run, and they do not
   reach the forced zero either. The reason is now clear rather than
   incidental: throughout F209B the accumulator sits at exponent +50
   and the memory operand at +2, so the accumulator dominates by 48
   places and no sum can come out negative. Only the sign forcing is
   covered (halt 015537.00).
   The forced zero has its own routine, which the page scan turned up:
   F209E "TEST FORCED ZERO RESULT" (p.107). Its E1 is DL(U) FPK38 then
   D-MG(U) FPK37 -- two constants at the SAME exponent, which is what
   lets a negative sum happen -- and it checks the result fraction
   against FPK0 at both offsets. That is the block to transcribe if
   the forced zero is the target, and it is also what would settle
   which exponent the unflagged forced zero keeps.
   The same scan corrected a claim: F209B runs to B16, not B13, so
   015543.00 is where B14 begins and not the routine's exit. The
   program and verifier say so. Between B13 and F209E lie B14-B16,
   F209C ("UNCHANGED REGISTERS", C1-C2) and F209D ("TESTS OF
   INDICATORS", D1-D8).
   jb_af1c F209B14-B16 (p.105) closes the routine: both signs negative
   -- DLN accumulator and FPK40 operand -- completing the grid. F209B
   is now transcribed end to end, 015365.40 to 015574.40 across three
   programs, each ending exactly where the next begins, and the last
   closing on the listing's own exit. All sixteen sub-tests pass and
   none of them reaches the forced zero.
   jb_af1c F209C (pp.105-106, C1-C2, "UNCHANGED REGISTERS") passes,
   and its C2 is the strongest single check in the D+MG work. Where
   F208C looked at only sign byte bits 5-7 with a 3-bit field at 10.5,
   F209C checks all EIGHT bits at 10.0, so C2 covers the sign (bit 4)
   as well as the flags. Two separate injections halt on it: not
   restoring the accumulator's own sign after the add, and taking the
   sign byte's flag bits from the result instead of from accS. F208C2
   caught the second for D+ but could not have caught the first.
   C2's accumulator is all ones, so EF = 1 and the add takes the
   flagged path -- which makes it a check of what "hand back the
   operand whole" may touch in the magnitude direction too.
   jb_af1c F209D1-D5 (pp.106-107) covers D+MG's arithmetic result
   indicators -- RLZ, RZ, RGZ, RN -- one SIC/branch pair per question.
   D1 and D2 pin an ordering nothing before them could: their
   accumulators are loaded NEGATIVE with DLN, and D+MG assumes the
   accumulator positive for the addition, so the sign must be restored
   before the INDICATORS are set, not merely before the sign byte is
   written. Restoring it only at the byte write leaves F209C -- which
   checks all eight sign byte bits -- passing, and halts at D1's first
   question, BZRLZ. The byte is correct in that state; only an
   indicator test can see it.
   Transcribed as printed: D1's third question is BRGZ (1304.35 42)
   where its comment says "error if RZ on", and D2 asks that question
   with BRZ (1304.34 C2). The encodings distinguish them, so it is the
   listing's own inconsistency; D1 asks about RGZ twice and never
   about RZ.
   Next: F209D6-D9 (the Lost Significance half, from 015652.00), then
   F209E -- still the one block that covers D+MG's forced zero and the
   one that should settle which exponent it keeps. Then SRD. Still
   open in double
   precision: D+MG, D-, SRD, SLO, D*, D/, LFT -- the first real double-precision
   ARITHMETIC, which needs the 96-bit adder and the accumulator's low
   half as a genuine operand rather than something only cleared.
   Related nearby routine also located and runnable-with-effort: F203B
   "EXP RNG INDIC TEST" (p.52, octal 012260+) verifies the exponent-
   range indicators XPFP/XPH/XPL/XPU (set by ST, cleared by Z,$IND)
   via BB/BZB on the indicator register -- exercises this session's
   BB-on-indicator and Z,$IND-clear work.
   After F204A, run the add/subtract/multiply blocks to
   verify +/+MG/-/M+/* on real operands (result checked by a following
   K compare, the pattern already validated), then implement the open
   ops in the order the diagnostic reaches them: `*+` (multiply-add),
   `F+` (add to fraction), double precision, `SRT` (root), `LFT`,
   and finally `divide` (multi-cycle; the combinational form blows up
   elaboration — needs the serial/parallel E-box of item 5).
3. **The interrupt system** — the biggest single documented feature
   still absent, and a prerequisite for EX/EXIC, storage protection,
   the timer, and any diagnostic that traps. Indicators → mask →
   left-most-one priority → the single "free" interruption instruction
   at IA+indicator#, IC not stepped; enable/disable via BE/BD. Ref.
   Manual pp.43-50, Blosk pp.16-17, Buchholz ch.10.
4. **Remaining instruction gaps** (mostly self-contained): EX/EXIC
   (needs item 3's interrupt-state rules), LVE/SVA/RNX/LVS, swap and
   backward Transmit + crossing-field VFL stores (needs a multi-cycle
   store), decimal VFL and radix conversion. Also finish Address
   Invalid for all operand classes (only FP today).
5. **Microarchitecture fidelity / the folklore** — the "cycle-accurate"
   half. Split the E-box into the real serial (SAU) and parallel (PAU)
   units sharing A/B and C/D; look-ahead data forwarding via the LAAR
   (today it drains/waits, no forwarding); per-level index-recovery
   levels with their real cost; the five ring-counter interlocks;
   ECC/parity check cycles; the Exchange as a real bus requester;
   the maintenance console. Validate against Perf. Char. vol.2
   measured timings (GERB2 etc.).
6. **DCP-scale transcription** — now unblocked on memory (BRAM, 98,304
   words). Remaining blockers are I/O and print macros: `CTL` SPACE
   FILE / WRITE TAPE MARK / BACKSPACE FILE, channel chaining/multi-
   block, and the `%IQSZ` print-formatting macros; then the
   self-contained Memory Compare (G5) and Panel Dump (H7) routines.
   See `docs/archival_inventory.md`.

Cross-cutting throughout: keep the regression suite green at every
commit; every timing claim carries a documented number; every new
feature gets a discriminating test proven by a reverted injection.

### 1c. Idiomatic Bluespec rewrite plan (mandatory -- AGENTS.md)

The model is currently one ~1450-line combinational `execute()` (the
whole E-box) inlined into a single monolithic `StretchCore.step()`
rule. It must be rewritten to the structure of Bluespec's own RISC-V
cores (Piccolo/Flute): separate pipeline-stage modules through FIFOs,
expensive datapath in multi-cycle "box" sub-modules, off-pipe paths as
separate rules. Reference cores are studied (bsv/README.md item 9). The
correctness oracle throughout is the existing regression suite: every
step keeps it green (behavior unchanged) and is a committed milestone.

Staged, each step green and committed:

1. **E-box as a module.** Wrap `execute()` in a singleton module
   `mkEBox(st, io)` exposing `method ActionValue exec(...)`; the four
   (mutually-exclusive) call sites in `step()` call the shared method.
   Behavior-neutral scaffolding for the box structure. **Done**
   (suite green; build time unchanged at ~121s, as item 9 predicted).
2. **FP box.** Move the floating-point datapath (`StretchFP`) behind a
   singleton module `mkFPU`. Piccolo's `mkFBox` interface is the model:
   `method Action req(op, a, b)`, `method Bool valid`, `method result
   word` -- the stage issues `req` once, reports BUSY while `! valid`
   (stalling the pipe), then consumes `word`. Do it in two sub-steps so
   each stays green:
   - 2a (behavior-neutral): `mkFPU` with a COMBINATIONAL `compute`
     method that just dispatches to the existing `StretchFP` functions;
     `execute`'s FP arm calls `fpu.compute(...)`. Idiomatic structure,
     no timing change.
   - 2b (cycle-accurate, changes timing): make `mkFPU` MULTI-CYCLE
     (req/valid/word, a state machine reusing a small datapath -- the
     real serial SAU / parallel PAU), and have the E-box/look-ahead
     stall for it like Stage2 stalls on `! fbox.valid`. Update the
     timing-bound tests to the new cycle counts. This is cycle-accuracy
     item 5.
3. **VFL / connective / integer boxes.** Same treatment for the
   variable-field-length unit and the connectives (and eventually VFL
   multiply/divide), each a singleton module.
4. **Split `step()` into per-stage rules.** Replace the one giant
   method with an I-box (fetch/decode/prepare/index) rule, look-ahead
   rules, and the E-box interaction, communicating through FIFOs /
   registers -- the `rl_pipe` + off-pipe-rules shape. **Done** (suite
   green, every CYCLES<= bound unchanged). How the harness contract
   was kept: `step()` is now an `Action` that sends a `tick` pulse and
   every core rule is gated on it, so one call is still exactly one
   clock and the core never moves while the harness loads or inspects;
   the halt is a register the executing arms write, read through a new
   `halted()` method that the harness's run rule polls in its guard --
   which yields the same step count at halt as the old returned Bool.
   The rules: `rl_clock`, `rl_la_fetch` (look-ahead operand collect /
   fetch issue) and `rl_ic_controls` (1Y/2Y), every clock; then one of
   six `(* mutually_exclusive *)` decision arms, the old if/else-if
   ladder: `rl_recover`, `rl_io`, `rl_idx_write`, `rl_exec_resume`,
   `rl_au_remove`, `rl_prepare`. The intra-clock ordering the single
   method had implicitly is explicit in two places: the look-ahead
   levels are `mkCReg(2)` (collect on port 0, arms on port 1) and the
   Y buffers are `mkConfigReg` (the IC controls write them while the
   preparation arm reads them and writes `pcReg`/`branchSeq` that the
   IC controls read -- all pre-clock reads, which ConfigReg states
   without a scheduling cycle). Build time: ~121s, unchanged -- the
   arms are still elaborated in full, as item 9 predicted; the win is
   structure, and step 5 (stage modules) is where compilation units
   actually split.
5. **Stage modules.** Extract the I-box, the look-ahead, and the E-box
   into separate modules with interfaces (the `mkCPU_Stage1/2/3`
   shape), so no single rule elaborates the whole design.
   - **5a done: the core as its own compilation unit.** `(* synthesize
     *)` on `mkStretchCore` (Piccolo synthesizes `mkCPU` and each stage
     the same way). Measured: the core elaborates ONCE per suite run
     (~117s, `build/mkStretchCore.ba`) and every testbench then builds
     against it in ~0s elaboration + ~10s link, versus ~120s per
     testbench before -- the whole suite went from ~12 min to
     ~3.5 min. Two harness facts fell out of the boundary: (i) bsc must
     assume the harness could call the exported bus-channel methods in
     a ticked clock, so `fire_when_enabled` is off `rl_la_fetch` and
     `rl_ic_controls` (the harness never does; the suite's CYCLES<=
     bounds are the check, and `bsv/check_schedule.py`, run by
     `build.sh` on the `-show-schedule` output, fails the build if any
     core rule is ever blocked by another core rule); (ii) a parent
     rule may not call `setPC`
     together with a `mem` method (bsc orders `rl_prepare` between
     them: KPNS #29 "dynamic scheduling"), even from exclusive case
     arms -- `StretchSmoke.bsv`'s setup now has `setPC` in its own
     rule, as `gen_tb.py`'s runners always did.
   - **5b done: stage modules inside the core.** `StretchIBox.bsv`
     holds `mkInstrBuffers` (the 1Y/2Y buffers with their IC controls:
     `advance(pcw, restart)` once per clock, `lookup(word)` for the
     preparation arm) plus the instruction classification and the
     I-box hazard test as functions; `StretchLookAhead.bsv` holds
     `mkLookAhead` (the four-level ring: `collect()` every clock,
     `levels/head/tail/count/headLevel`, and the three mutations the
     arms perform -- `retireHead`, `load`, `cancelAll`);
     `StretchTiming.bsv` holds the time-budget tables as functions.
     The stages take the storage interface as a module argument and
     are flattened into the synthesized `mkStretchCore`, exactly the
     Piccolo `mkCPU_Stage1/2/3(gpr_regfile, csr_regfile, ...)` shape;
     the core's rules are now orchestration (`rl_la_fetch` is
     `la.collect()`, `rl_ic_controls` is `ibuf.advance(...)`) plus the
     six decision arms calling the stages' methods. StretchCore.bsv
     went from 884 to 573 lines. Behavior-neutral: suite green, every
     CYCLES<= count unchanged. `mkEBox` keeps taking the storage and
     I/O interfaces as module arguments, so it too is flattened; to
     make the E-box its own compilation unit it would have to route
     its storage traffic through exported request/response methods
     instead of calling `st` directly -- the real `mkFBox` shape, a
     larger change, and only worth it together with steps 2-3.
   - **5c done: the E-box as a request/busy/result box.** `mkEBox` now
     owns the operand-read bail/resume state that was the core's
     `execPending`/`execPrefetch`/`auActive`: `start(pc, len, di,
     words, n, owner)` returns the result at once (Valid) or issues the
     operand read, holds the instruction and reports `busy` /
     `busyFor(owner)`; `canResume` says the word is back; `resume()`
     collects it, re-runs, and either completes or bails again for a
     second word. The core's arms are now `ebox.start`/`ebox.resume`
     calls plus the retire-or-advance-the-counter decision by owner
     tag; the bare `exec` stays for the preparation arm's side-effect-
     free operand-address probe. This is the mkFBox req/valid/result
     protocol with the box's multi-cycle time being its operand
     fetches (the arithmetic itself is still one clock: step 2b, the
     serial/parallel unit timing, remains the optional refinement).
     Behavior-neutral: suite green, every CYCLES<= count unchanged.

Note on the ~120s build: profiling (item 9) showed elaborating the
E-box logic ONCE is the cost, and neither replication nor the FP
arithmetic specifically is it -- so the primary payoff of this rewrite
is idiomatic structure and cycle-accuracy; a build-time win is likely
(splitting across modules/rules and genuinely multi-cycle iterative
units reduce per-rule elaboration) but is to be MEASURED at each step,
not assumed.

**Reassessment (2026-09-04), which reorders the above.** The FP box
(step 2) is LOWER value for Stretch than the Piccolo comparison
suggested, for two measured reasons: (a) Stretch already models FP as
multi-cycle in TIMING via the E-box time budgets (`ebusy`/`eboxClocks`/
`iboxCycles`), so a real multi-cycle FP unit would largely duplicate
that; (b) the FP datapath is not the elaboration cost (item 9's stub
experiment). Boxing combinational FP into a module is also not more
idiomatic than keeping it as `StretchFP` functions -- Bluespec cores
use plain functions for combinational ALU work (`EX_ALU_functions`) and
reserve modules for genuinely multi-cycle units. So the REAL remaining
"weird Verilog" for Stretch is the monolithic `step()` method itself:
one giant rule doing fetch + look-ahead + execute + I/O. The
highest-value idiomatic work is therefore steps 4-5 (split `step()`
into per-stage RULES, then STAGE MODULES with FIFO/register hand-off,
the `rl_pipe` + off-pipe-rules shape), not step 2. Step 1 (E-box as a
module) still stands as the foundation; steps 2-3 (multi-cycle boxes)
become an OPTIONAL cycle-accuracy refinement, done only if/when a
serial iterative unit is wanted, not as the primary idiom fix. The hard
part of 4-5 is that `step()` returns a "halted" Bool per call to the
test harness (`gen_tb.py`), and its state updates (pcReg, the four
look-ahead levels, execPending, the Y buffers) are interdependent and
currently atomic in one method -- splitting them into rules that keep
the exact cycle behavior and the harness contract is the work.

Concretely, "the same" means these things, each with a primary source:

| Aspect | Real machine | Source |
|---|---|---|
| Memory | 16,384-word units, 2.1 µs read-write cycle, each with its own addressing and data registers; typical system 6 units: 4 interleaved (consecutive addresses in different units) for data + 2 interleaved for instructions | Buchholz ch.14 §14.1 (p.202); Blosk fig.1 |
| Memory bus control unit (MBCU) | Arbitrates 8 requesters with priority exchange > disk > look-ahead > instruction unit; accepts one store/fetch per 0.3 µs; returns a word ~1.6 µs after request when the unit is free; holds requests for busy units; each request carries a 3-bit return address (which Y register or LA level) | Buchholz §14.3 (pp.205-206); Blosk p.19 |
| Instruction unit (I-box) | ICR (19 bits) with +2 adder giving n..n+3; two 64-bit instruction/data buffers 1Y, 2Y; index storage: 17-word × 73-bit core array (word 17 = timer/clock) with one data register XR; preparation/execution register ZR (64 bits + 3-bit P for progressive indexing); working register WR (19 bits); 24-bit index adder with in-buses A (IC, WR, XR, ZR, complementable) and B (Y registers, ZR); shared I checker; up to six instructions in progress | Blosk TR00.722 pp.7-15, fig.3 |
| I-box responsibilities | Fetches and checks every instruction; indexes (normal and progressive); pre-decodes; executes index arithmetic, branches, transmit and misc itself; initiates operand fetches for FP/VFL and loads them into look-ahead; monitors all addresses against the boundary registers; runs the interrupt mechanism; steps the timer/clock | Blosk pp.4-6, Appendix B |
| Branch guessing | Conditional branches on arithmetic results are assumed *not* taken; the I-box continues; index-indicator branches (CB family, B on XF/XVLZ/XVZ/XVGZ/XCZ/XL/XE/XH) are resolved in the I-box from an "updated indicator register" of eight triggers | Buchholz §14.3 p.207, §15.2 p.238; Blosk p.17; Perf. Char. vol.1 p.3-22 |
| Look-ahead (LA) | Four levels, each: op code, 8 tag bits (level filled, level checked, internal operand, IC valid, LA op code, word-boundary crossover, no-op, from), 15 indicators, instruction counter, 64-bit operand; five ring counters (instruction-unit, operand-check, transfer-bus, arithmetic-bus, store-check) advancing under interlocks; one look-ahead address register (LAAR) with forwarding; all stores to memory and internal registers performed by LA; index-recovery pseudo-store levels; recovery ("housecleaning") on interrupt or wrong-way branch | Buchholz ch.15 §15.3-15.6 (pp.238-247), figs 15.6-15.10 |
| Arithmetic unit (E-box) | Serial unit (VFL add/subtract, connectives, FP exponent) and parallel unit (FP fraction add/multiply/divide, VFL multiply/divide), sharing the 128-bit accumulator A/B and 128-bit operand register C/D; slave to LA (receives op + operand, signals termination, returns store results to LA); basic cycle 0.3 µs | Buchholz §14.4 (pp.208-216); Perf. Char. vol.1 ch.3 |
| Timing | E-box cycle 0.3 µs; I-box control cycle 0.5 µs as designed (Blosk p.23) and 0.6 µs as shipped (Perf. Char. p.3-17: "decoding time of I-box instructions is 0.6 µs", table entries in multiples of 0.6); FP preparation one instruction per 1.2 µs; VFL preparation 3.6 µs minimum loading two LA levels, +0.6 per extra level or indexing; per-instruction pre-execution/execution cycle counts | Perf. Char. vol.1 ch.3 tables 2-9; Blosk figs 6-10 |
| Clocks | Units asynchronous with respect to each other, synchronous within; one master oscillator | Buchholz §14.2 p.204; Blosk p.21 |

Sources are all in `docs/` (downloaded from bitsavers 2026-09-03; the
site refuses non-browser user agents): `Planning_A_Computer_System.pdf`
(Buchholz, 1962; ch.14 = PDF pp.227-250, ch.15 = PDF pp.253-272),
`TR00.722_Stretch_I-Unit_Design_Mar60.pdf` (Blosk), `TR00.03000.703_
StretchVM_59.pdf` (Cocke & Kolsky, the look-ahead simulation study),
`Bloch_EngrDesOfStretch_1959.pdf`, `7030_Performance_Characteristics_
Vol1_Mar61.pdf` and `_Vol2_` (vol.2 is benchmark listings with measured
times -- a timing validation set), `ADescriptionOfStretch_Dec59.pdf`,
and the CE manuals `R23-9732_Manual04_7101_CPU_Jan63.pdf` (section 3:
flow, block and timing charts) and `R23-9694/9695` (CE programming
introduction). Only Buchholz and the two Performance Characteristics
volumes have text layers; the rest are read as page images.

## 2. Where the current model stands

(As of 2026-09-05; the paragraph this replaces described the
2026-09-03 starting point, a single non-pipelined `step()` core with
one BRAM and no timing.) `bsv/` today is the synthesized core
`mkStretchCore` orchestrating stage modules with per-clock rules:
`StretchMemory` (six interleaved 2.1 µs units behind the MBCU),
`StretchStorage` (the CPU's bus client: store queue, tagged read
channels, special registers, index storage), `StretchIBox`
(`mkInstrBuffers`: 1Y/2Y and the IC controls, plus classification and
the I-box hazard test), `StretchLookAhead` (`mkLookAhead`: the
four-level ring), `StretchExecute` (`mkEBox`: the execute datapath as
a start/busy/resume box holding its own operand reads), and
`StretchTiming` (the per-class time budgets). The core's rules are
the every-clock `rl_la_fetch`/`rl_ic_controls` and six mutually
exclusive decision arms (§1c step 4). `step()` is a clock enable,
`halted()` the halt flag, and the step count at halt is the clock
count the `CYCLES<=` bounds check. What is still not modeled is the
list in §1b item 5 (the SAU/PAU split and their real cycle timing,
LAAR forwarding, index-recovery levels, the ring-counter interlocks,
ECC cycles, the Exchange as a bus requester) and the functional gaps
in §1b items 3-4. The 44-section suite is the correctness oracle every
change must keep green.

## 3. Target structure (Bluespec modules)

```
                    +----------------------------------------------+
  memory units      |  mkMemoryUnit x6  (16K words, 2.1 µs cycle)   |
                    +----------------------------------------------+
                                       ^ requests / data
                    +----------------------------------------------+
  bus               |  mkMBCU  priority arbiter, interleave map,   |
                    |          busy tracking, 3-bit return tags    |
                    +----------------------------------------------+
                        ^ fetch (I-box)      ^ store / fetch (LA)
   +--------------------+------+     +--------+--------------------+
   |  mkInstructionUnit         |     |  mkLookAhead                |
   |  ICR, 1Y/2Y, XS+XR, ZR+P,  | --> |  4 levels, 5 ring counters, |
   |  WR, IAU, I checker,       |     |  LAAR + forwarding, store   |
   |  updated indicator reg,    |     |  path, recovery             |
   |  tags, boundary compare    | <-- |                             |
   +----------------------------+     +-------------+---------------+
                                                    | transfer bus / arithmetic bus
                                      +-------------v---------------+
                                      |  mkArithmeticUnit           |
                                      |  serial (VFL/conn/exp) +    |
                                      |  parallel (FP fraction,     |
                                      |  mul/div); A/B, C/D regs    |
                                      +-----------------------------+
   +----------------------------+
   |  mkInterruptMechanism      |  indicator reg (64), mask (20),
   |                            |  left-most-one detect
   +----------------------------+
   +----------------------------+
   |  StretchIO (exchange) --   |  becomes an MBCU requester with
   |  existing simulated devices|  highest priority
   +----------------------------+
```

Cycle base: one Bluespec clock = one E-box cycle = 0.3 µs. Units that
are asynchronous in the real machine are modeled as separately-clocked
FSMs on that common base (I-box control stages advance every 2 clocks;
a memory unit is busy for 7 clocks; the MBCU accepts one request per
clock). A global cycle counter exposed to the testbench gives every run
a time, and per-unit trace output (`$display` under a flag) gives the
same view Blosk's figures 6-10 draw.

## 4. Stages, each ending green on the full suite

The order follows the data: memory first (everything else waits on it),
then the unit that drives everything (I-box), then the buffering between
I-box and E-box (look-ahead), then splitting execution. Each stage is a
separate commit series with the full `run_tests.sh` suite green before
the next begins; the suite checks only architectural results, so a
stage that changes timing but not results is exactly what "green"
should mean.

**Stage 0 -- observability.** Add the cycle counter, a `PC=`-style
`CYCLES<=` bound check to `gen_tb.py`, and a per-unit trace flag. No
behavior change. (Small; lets every later stage report its timing.)

**Stage 1 -- memory units and the MBCU.** Replace `StretchStorage`'s
single BRAM with six `mkMemoryUnit`s behind `mkMBCU`: interleave map
(4-way over the data block, 2-way over the instruction block, per
Buchholz §14.1), per-unit busy for 7 clocks, priority arbitration,
return tags, and the request/response latency the rest of the machine
sees (~5 clocks when free). The 0-31 special-register words stay
register-backed inside the CPU (they are, on the real machine: index
storage and internal transistor registers -- Blosk p.19). The existing
core keeps working with a longer, variable memory latency; its
bail/resume design already tolerates that.

**Stage 2 -- the instruction unit.** New `mkInstructionUnit` replacing
the core's fetch/decode/step loop: ICR with n..n+3 addressing; 1Y/2Y
buffers filled ahead by the IC controls; I checker stage; Y-to-Z
transfer with the half-word criss-cross that aligns full-word
instructions; index storage as a 17-entry array with its 1-cycle read
and 2-cycle write through XR; ZR/P/WR; the index adder; pre-decoding
and the tag triggers; execution of the I-box instruction classes
(Blosk Appendix B: index arithmetic, branches, transmit, misc, SIC);
the updated indicator register for I-box-resolved branches; the
not-taken guess for arithmetic-conditional branches. At this stage the
E-box-class instructions (VFL, FP, connectives, I/O) are still executed
in order by the old execute path fed from ZR, so the suite must stay
green while instruction fetch and I-box execution become real.
Timing target: Blosk fig.6 (FP preparation one per two I-box cycles),
fig.8 (CB in six cycles), Perf. Char. tables 4-9 for I-box instruction
times.

**Stage 3 -- the look-ahead.** `mkLookAhead` with four levels of the
exact register set (op code, 8 tags, 15 indicators, IC, operand), the
five ring counters with the interlocks of Buchholz figs 15.7-15.10,
the LAAR with forwarding and store-close-to-fetch handling (Perf. Char.
pp.3-20..3-21: prefetched-instruction invalidation, delayed operand,
forwarding), all stores routed through LA, index-recovery pseudo-store
levels for every I-box instruction, and recovery/housecleaning on
interrupt and on wrong-way branch (I-box IC and index registers
restored from LA, intervening operations cancelled). The old execute
path becomes the consumer of LA levels. This is the largest stage and
the one the suite's SIC/CB/branch programs exercise hardest: every
verbatim I-Box 1 group is a sequence of I-box branches interleaved
with LA-loaded operations, and the p.50-51 SIC groups in particular
store into instructions that have just been prefetched.

**Stage 4 -- the arithmetic unit.** Split execution into the serial
and parallel units with A/B and C/D, driven by LA's transfer-bus
counter and reporting termination to the arithmetic-bus counter;
pre-execution vs. execution cycle accounting per Perf. Char. table 2
(FP) and the VFL tables; VFL word-boundary-crossover operands
arriving in two LA levels. Floating-point arithmetic beyond L/ST
(unimplemented today) is added here, since the parallel unit's timing
is the reason the machine exists.

**Stage 5 -- timing validation.** Reproduce Perf. Char. vol.1 ch.4's
worked timing examples and vol.2's benchmark programs (STRAP source
with measured times) as tests with `CYCLES<=` bounds; compare Blosk's
figures 6-10 against the trace output cycle by cycle. The aggregate
oracle is vol.1 Table 10 (p.4-9), the "Execution Frequency Chart for
Stretch Programs": per benchmark it gives the count of each operation
executed, the total execution time in ms, and the average us/op.
Benchmarks (source in vol.2): matrix inversion GERB2 (10x10 0.02s ...
100x100 14.61s), matrix multiply MXM16 (25x25 0.20s ... 125x125
21.44s), prime sieve PRIMC (106.7s, two-thirds of it an interruption
table -- the interrupt-system timing test), Monte Carlo (10,000
particles, 33s), the weather inner loop (AO 5.98 ms / 1711 ops / 3.5
us-op, A1 5.57, A2 7.0135, grid 7.07 ms), elementary functions
(.38/.309 ms). Table 10's operation counts also check the model's
cycle attribution independently of the totals.

Deferred, in scope, after stage 5: the interrupt system as a whole
(indicator/mask/left-most-one, the "free instruction"), boundary
protection alarms, the timer/clock stepping through index storage word
17, the exchange as an MBCU requester with real overlap (the current
synchronous I/O FSM is a stage-1 compatibility path).

## 5. Oracles and how each stage is verified

1. **Architectural**: `strap/run_tests.sh` -- 20 blocks, ~600 listing
   rows, seven verbatim diagnostic programs with the deck's own pass/
   fail mechanisms. Green before every commit, as now.
2. **Discriminating checks for the microarchitecture**: programs whose
   *result* depends on the machine doing the trick correctly rather
   than merely fast -- store-into-prefetched-instruction (the SIC
   groups already do this; add Perf. Char.'s three "store close to
   fetch" sequences as programs), forwarding (`LOAD a; MULTIPLY a;
   MULTIPLY a` per Buchholz §15.4), wrong-way branch recovery with
   index registers modified by prefetched I-box instructions, and
   interrupt recovery once interrupts exist.
3. **Timing**: `CYCLES<=` bounds from Perf. Char. tables, Blosk's
   diagrams, and vol.2's measured benchmarks. Timing checks are
   separate from architectural checks so a timing regression cannot
   masquerade as a correctness failure or vice versa.
4. **Bug injection** stays the rule: every interlock gets a test that
   fails when the interlock is removed (e.g. remove the instruction-
   unit-counter/store-check interlock and watch a store be lost).

## 6. Known risks

- **bsc scheduling.** The single-rule `step()` design was chosen partly
  because bsc rejected same-rule combinations of storage and index
  writes (README "Toolchain" item 7). Six concurrently firing units
  with shared buses will need explicit arbitration modules and FIFOs/
  RWires rather than one big rule; expect to rediscover G0004
  conflicts early in stage 2 and design the buses as modules with
  single-writer methods from the start.
- **Fidelity vs. documentation gaps.** Blosk's report predates the
  shipped machine (0.5 µs vs 0.6 µs I-box cycle); where Buchholz,
  Blosk and Performance Characteristics disagree, the 1961
  Performance Characteristics (measured on the built machine) wins
  for timing and the CE manual (1963) wins for structure. Record each
  such choice in this document.
- **Elaboration size.** Four LA levels × 64-bit operands, two Y
  registers, a 17-word index array and six memory units are modest;
  the earlier Vector-of-Reg blowup came from a 256-entry register
  file with dozens of read ports, which none of these are.
- **Suite runtime.** A cycle-level model runs the same programs in more
  simulated cycles; the suite's ~10-minute wall time is dominated by
  bsc compilation, not simulation, so this should stay tolerable.

## 6a. Stage 2 design: the instruction unit

Written after reading Blosk TR00.722 in full and the CE manual's
section-3 figure index. The CE manual's I-unit flow diagrams are the
sequencer-level reference: figures 3.1.1-3.1.5 (IF 1Y / IF 2Y
sequencers, IC 1Y/2Y triggers, IWC1/IWC2, IC Adv and ICOR), 3.1.6-3.1.9
(Y-Z start trigger and the four YL/YR to ZL/ZR transfer sequencers),
3.1.10-3.1.21 (ZR/ZL Mod Req triggers and Mod sequencers, block/suspend
triggers, the ZL/ZR FP triggers 1-6), 3.1.22 (IHW = "instruction half-
word" triggers, 1-bit mod, FP Z ALT), 3.1.23 (WBC+DEC and XF+DEC
sequencers), 3.1.24-3.1.28 (WBC trigger, FW/FWS/FW-not-S triggers, ZL
DEC trigger). The LA's are 3.2.1-3.2.27 (IAUC load, LA load pulses,
operand check, TBC advance, SAU/VFL/FP levels, LAOP codes, ABC actions
and indicator timers, houseclean timers, SCC advance/actions/stores).
PAU data flow 3.3.x, FP timing 3.8.x, error conditions 3.7.x/3.9.x.

**Time base.** The I-box control cycle is two clocks (0.6 µs as
shipped, Perf. Char. p.3-17); sequencers advance on I-box cycles,
memory on clocks. A `phase` toggle in the unit selects the A/B pulse.

**Registers** (Blosk pp.7-15): `ICR` (19); `Y1`, `Y2` (64 + valid +
checked + word address + fetch-outstanding); index storage `XS`
(Vector of 16 words + word 17 timer/clock) with data register `XR`;
`Z` (64, with `P` 3 bits) and its two halves; `W` (19); the index
adder `IAU` as functions over bus-A/bus-B selections; the updated
indicator register `UIR` (XL XE XH XCZ XVLZ XVZ XVGZ XF). The I
checker is a one-cycle stage between a Y register's arrival and its
`checked` flag (no error paths yet).

**Control areas** (Blosk p.25-27), each an FSM stepping on I-box
cycles:
- *IC controls*: keep 1Y/2Y filled -- when a Y is empty and no fetch
  is outstanding for it, request the next instruction word (the ICR
  and adder give n..n+3) through the MBCU with that Y as return tag;
  on a taken branch or recovery, invalidate both and restart at the
  target. Interlocks: a store whose address compares equal to a
  prefetched word invalidates the Y registers (program store compare,
  Blosk p.21; Perf. Char. p.3-21 sequence (1)).
- *Preparation controls*: when Z is free and the next half-word (per
  ICR) is in a checked Y, transfer Y->Z (one cycle; a full-word
  instruction straddling 1Y/2Y needs both), fetch the index word (XF,
  one cycle, reading XS into XR) when I != 0, modify (MOD, one cycle
  through the IAU; progressive indexing takes its two-step form); for
  VFL, the word-boundary-crossover test (WBC) adds the length to the
  24-bit address and gates the second word's address into W. The ICR
  advances as Z is loaded.
- *Look-ahead load controls*: for FP/VFL/I-O (E-box class) the
  prepared instruction leaves Z for execution. **Stage-2 simplification:**
  there is no look-ahead yet, so the existing `execute()` runs the
  instruction to completion in order, performing its own operand
  fetches through the storage handshake; its cycle cost is therefore
  unoverlapped. Stage 3 replaces this with the four levels.
- *Instruction-execution controls*: I-box instructions (Blosk
  Appendix B: direct and immediate index arithmetic, unconditional
  branches, branch on indicator, branch on bit, count-and-branch
  family, SIC, transmit/swap, refill, execute, store zero) execute in
  the I-box. Their *semantics* come from the existing `execute()`
  arms (already verified by the suite); their *timing* comes from a
  per-class I-box cycle count taken from Blosk's figures 8-10 and
  Perf. Char. tables 4-8 (e.g. CB successful 4.2 µs + decode = 8 I-box
  cycles; LVI 2.4 µs + dec = 5; LX from external memory 4.8 µs + dec =
  9, of which the operand fetch's real memory time is charged as it
  happens). Index-storage stores take two cycles.
- *Branches*: unconditional and index-indicator branches (CB family;
  B on XF/XVLZ/XVZ/XVGZ/XCZ/XL/XE/XH) are resolved in the I-box from
  the UIR at preparation time and cost a Y refill. Branches on other
  indicators are guessed not taken: the I-box goes on fetching and
  preparing the fall-through path. **Stage-2 simplification:** since
  the guess cannot yet be undone for index registers (no pseudo-store
  recovery levels), the I-box does not *execute* an I-box instruction
  past an unresolved arithmetic-conditional branch; it prepares and
  waits. When the executor resolves the branch as taken, the prepared
  fall-through work is discarded and fetching restarts at the target
  (the wrong-way recovery cost of Perf. Char. p.3-23).

**Deliverables**: `bsv/StretchIBox.bsv` (new) replacing
`StretchCore.step()`'s fetch/decode loop; `StretchCore` becomes the
composition of I-box + executor + storage + I/O. Suite green. Timing
tests: Blosk fig.6 (four indexed FP loads prepared in eight I-box
cycles), fig.8 (CB in six), tables 4-8 spot checks, all as `CYCLES<=`
programs. Trace flag showing, per I-box cycle, the IC/Y/Z/XF/MOD
activity in the format of Blosk's diagrams.

## 6b. Stage 3a design: the look-ahead, first cut

Four levels in a ring (`LaLevel`: instruction, IC value, operand
address, operand, fetch-issued, wait-for). The instruction unit loads
an E-box-class instruction (VFL, connective, floating point) into the
tail level at preparation: if it fetches a memory operand, the
operand address is obtained by running `execute()` with no operand,
which bails out with the address of the first read it needs and no
side effects (the contract established in the BRAM migration) -- so
the address arithmetic lives in one place; instructions that fetch
nothing (immediate VFL, FP store) are loaded without a probe and run
only at removal. Levels issue their fetches ahead on their own bus
channels (tags 3-6, priority above the Y buffers); a level whose
operand address equals an earlier unretired level's waits for that
level to retire (store-then-load ordering, the LAAR's job -- Cocke &
Kolsky fig.6A's compare/forward, done conservatively for any earlier
level rather than only stores). The arithmetic unit removes the head
level when its operand is present, executing with the operand
pre-supplied; further reads (crossing words, refills) go through the
existing resume path. E-box time (`eboxClocks`) holds the next
removal, the I-box budget holds the next preparation, so preparation
and fetch-ahead overlap execution. Conservative rules of this cut,
to be relaxed in 3b/3c: an I-box-class instruction waits for the
levels to drain before executing (no index-recovery levels yet, so
nothing the I-box does can run ahead of an E-box store or a
progressive-indexing modification); a load waits while a
progressive-indexing instruction is in the levels; branches on
non-index indicators are I-box-class and therefore also wait, which
is Cocke & Kolsky's "hold up on every branch" option -- the
not-taken guess comes with recovery in 3b.

## 6c. Stage 3b design: I-box instructions running ahead

Perf. Char. p.3-17: "I-box operations usually do not involve the
E-box, and the I-box time can be covered largely by neighboring
floating point operations" -- the folklore item that index arithmetic
and count-and-branch hide behind arithmetic. In 3a every I-box-class
instruction waits for the levels to drain; 3b lets it execute while
levels are pending unless a hazard exists:

- *Memory it reads* (LX/LV/LC/LR/KV/KC/V+ family, R/RCZ and CBR's
  refill word, Transmit's source): wait if any unretired level's
  operand address is that word (an E-box store ahead in program order
  may not have happened yet -- Cocke & Kolsky fig.5's "does index
  address compare with an address in a virtual memory").
- *Memory it writes* (SX/SV/SC/SR, Z, SIC's store, Transmit's
  destination): wait if any unretired level's operand address is that
  word (a level ahead in program order must fetch the old value).
- *Arithmetic indicators* (branch on a non-index indicator): wait for
  the levels to drain -- this stays "hold up on every branch" until 3c
  adds the not-taken guess with recovery.
- *Index registers*: free -- pending E-box levels were indexed at
  preparation and only progressive indexing modifies an index register
  at execution, and a progressive-indexing level already blocks further
  loading (3a rule), so it also blocks I-box run-ahead until it retires.

The operand word of an I-box-class instruction is computed at
preparation with the same effective-address arithmetic execute() uses
(index value plus address; refill from the index word), the second
place that arithmetic appears, kept to the one-line cases; anything
not in the list above waits for a drain. Its time budget and Y-buffer
restart behave as before. No recovery levels are needed yet because
nothing the I-box does ahead can be wrong: no guessed branches, no
interrupts.

## 6d. Stage 3c design: the not-taken guess and wrong-way recovery

Buchholz §15.2 item 4 and Blosk p.28: "for a branch instruction
conditional on the result of arithmetic-unit operations, the
instruction unit proceeds as if the branch will fail"; Perf. Char.
p.3-23: "all changes in the index registers and/or index indicators due
to the advance processing by the I-box must now be undone ... The
correct instruction counter value is also shipped back to the I-box."

- A branch on a non-index indicator (Perf. Char. p.3-22: everything but
  XF/XVLZ/XVZ/XVGZ/XCZ/XL/XE/XH) is loaded into a look-ahead level as a
  *branch level* -- the real machine uses four levels (instruction,
  indicator fetch, store, recovery); the model charges their time and
  keeps one level -- with its target address computed at preparation.
  The instruction unit records the guess (a snapshot of the sixteen
  index words and the index indicators, standing for the recovery
  pseudo-store levels the machine would have loaded one at a time) and
  continues down the fall-through path. Only one guess is outstanding
  at a time; a second arithmetic branch waits.
- While a guess is unresolved the I-box executes index arithmetic and
  index branches ahead, as 3b allows, but stalls anything whose effect
  could not be undone by the snapshot: stores to memory (SX/SV/SC/SR,
  Z, SIC, Transmit -- on the real machine these become store levels
  that the store-check counter does not release before the branch
  level), unconditional branches and halts (so a halt is never reported
  under a wrong guess), and a second guess.
- When the arithmetic unit reaches the branch level, all earlier
  operations are complete, so the indicators are final: the branch
  executes with its normal semantics (test, optional clear). Guess
  right: retire the level. Guess wrong: cancel every younger level,
  restore the index registers and index indicators from the snapshot,
  set the instruction counter to the target, invalidate the Y buffers,
  and charge the recovery time (Blosk fig.10: the branch's own five
  cycles; plus the refetch).

Cost model: the branch level's four-level load is charged as the
branch's I-box time (6 cycles); a wrong guess adds a Y refill. The
interrupt system, when it arrives, uses the same recovery path
(Buchholz §15.6: "the interruption action is quite similar to branch
recovery except that in addition a new instruction has to be fetched").

## 6e. Stage 4 design: the arithmetic unit

Buchholz §14.4 (pp.208-216), Perf. Char. tables 2-3, CE manual figs
3.3.x (PAU data flow) and 3.8.x (FP timing):

- *Registers*: the 128-bit accumulator A/B and the 128-bit operand
  register C/D, shared by both units, plus the parallel unit register,
  shifter, and the sum/carry registers of the multiply tree. The model
  already keeps the accumulator as one 128-bit sign-magnitude value
  (`readAcc`/`writeAcc`); C/D become explicit so the transfer-bus
  counter's "operand to C/D" step has a place.
- *Serial arithmetic unit (SAU)*: two symmetrical byte-extraction paths
  (16-of-128 then 8-of-16 switch matrices) into one binary adder or
  logic unit, true-complement switches before and after, a decimal
  corrector, one byte pair per clock (0.6 µs "clock" in Buchholz's
  1959 description; the shipped SAU equation of table 3 charges 0.6
  µs per byte, i.e. two of this model's clocks). Handles VFL add/
  subtract/compare/load/store, connectives, decimal arithmetic and
  radix conversion, and floating-point exponent arithmetic. The
  model's `StretchVFL`/`StretchALU` do the arithmetic as whole fields;
  stage 4 wraps them in a per-byte timing loop (bytes = ceil(length /
  byte size), plus the unlike-sign and recomplement extra cycles table
  3 lists) rather than re-deriving the byte datapath.
- *Parallel arithmetic unit (PAU)*: 100-bit carry-propagate adder with
  4-bit carry look-ahead (0.15 µs for 96 bits), shifter (4 right / 6
  left per step), true-complement switch, and the multiply tree (four
  carry-save adders taking 12 multiplier bits per cycle as four 3-bit
  groups of ±multiplicand multiples), divide by table-selected
  multiples (1, 3/2, 3/4 of the divisor, skipping over 1s and 0s,
  ~3.5 quotient bits per cycle). Handles FP fraction add/multiply/
  divide (48-bit single, 96-bit double) and VFL binary multiply/
  divide. Floating-point arithmetic beyond L/ST is unimplemented today,
  so stage 4 is also where the FP instruction set is completed
  (Reference Manual ch. on floating point; Buchholz ch.8 for the
  format, normalization, singularities and the flags), with per-
  instruction pre-execution/execution cycles from table 2 and the CE
  timing charts 3.8.1-3.8.20, and multiply/divide cycle counts derived
  from the 12-bits-per-cycle and ~3.5-bits-per-cycle rules rather than
  fixed numbers.
- *Interface to the look-ahead*: the transfer-bus counter's hand-off
  (op code + operand to the unit; "was it accepted?"), the arithmetic-
  bus counter's completion (indicators into the indicator register,
  store results back into the level), per Buchholz figs 15.9-15.10 --
  replacing the model's direct call of `execute()` at removal with a
  unit that accepts an instruction, runs for its cycle count, and
  reports. Pre-execution (before any addressable register changes)
  vs. execution matters for interrupt timing and is kept as two
  phases.
- *Checking*: duplicate arithmetic and parity on the switch matrices
  (Buchholz p.209, p.216) modeled as the cycles they occupy only.

Order within stage 4: (a) SAU per-byte timing wrapper and explicit
C/D, (b) the LA/AU hand-off protocol, (c) FP add/subtract/compare with
normalization timing, (d) multiply, (e) divide, (f) decimal and radix
conversion, each with `CYCLES<=` tests from table 2/3 and the CE
timing charts.

### 6f. Stage 4c note: floating-point arithmetic, and why divide waits

`StretchFP.bsv` is the single-precision arithmetic, pure functions over
the Reference Manual's format (pp.78-94): add and its magnitude/to-
memory variants, load, compare (plain/magnitude/range), and multiply,
with normalization (noisy mode included), the sign modifiers, the
flagged-exponent range tables (Fig.23-24), and the LC/LS/PSH/ZM/range
indicators. It is wired into `execute()`'s Fp arm and tested by
`fp_arith.strap` (2 -> x3 -> +3, each stored and checked against the
Python-derived format). **Divide and reciprocal-divide are deferred to
the multi-cycle arithmetic unit (stage 4e).** A combinational
full-width divide unfolds hugely in bsc, and the real divide is
iterative (~3.5 quotient bits per cycle) -- it belongs in
`mkArithmeticUnit` once execute()'s combinational hand-off becomes the
staged one of §6e, not inlined here. Measured: the FP arithmetic adds
~12s to the smoke build; the ~270s baseline is the look-ahead logic
inlined at the smoke test's two step() call sites, not the FP.

## 6g. Stage 4b implementation design: splitting execute() into an arithmetic-unit module

Stage 4b is now the highest-value step: it is the structural prerequisite
for divide/double precision AND the fix for the ~45-minute suite. The
build cost is `execute()` -- a single monolithic combinational function
carrying every instruction arm including the floating-point multiply and
(future) divide -- being inlined at FOUR call sites in `StretchCore.step()`
(startExecute, the operand-resume path, the look-ahead removal path, and
the E-box-class preparation probe). The floating-point logic is paid four
times over.

**The split.** Divide `execute()` into two functions:
- `executeIbox(...)` -- the I-box-class arms (DirIndex, ImmIndex,
  CountBranch, BranchInd, BranchOrMisc, Sic, Transmit, and the AD/OP
  fall-throughs). These are cheap and are called from `step()`'s
  preparation path (and the shared `evalBranch`).
- `executeEbox(...)` -- the heavy arms (VflInt, Connective, Fp, IoOp).
  These are called ONLY from the new arithmetic-unit module.

**The arithmetic-unit module** `mkArithmeticUnit`:
```
interface ArithmeticUnit;
  method Bool ready();                       // idle, can accept
  method Action start(HWordAddr pc, InstrLen len, DecodedInstr di,
                      Vector#(2, Word64) prefetch, Bit#(2) prefetchCount);
  method Bool needsRead();                   // bailed for an operand
  method WordAddr readAddr();
  method Action resume(Word64 data);         // supply the operand, continue
  method Bool done();                        // result ready
  method AuResult result();                  // next PC, index write, io start, indicator word
endinterface
```
It instantiates `executeEbox()` at its one call site, holds the result
for the instruction's E-box cycle count (`eboxClocks`), and reports
`done`. The operand-read bail/resume moves inside the AU (done in
§1c step 5c: `mkEBox` holds it as `start`/`busy`/`resume`). The
look-ahead removal path becomes: when the head level's operand is
present and `au.ready()`, `au.start(...)`; while `!au.done()`, wait;
on `done`, commit `au.result()` and retire.

**Divide becomes multi-cycle here.** Inside the AU, a divide (or
double-precision, root) runs an iterative FSM -- the 7030's own
~3.5-quotient-bits-per-cycle SRT-style loop (Buchholz pp.213-215),
producing the quotient a few bits per clock over a bounded number of
cycles -- instead of a combinational `/`. Its cycle count is then real,
not a table lookup, and the combinational blowup disappears. The
`executeEbox` Fp arm's divide case, currently deferred, calls this FSM.

**Why this is safe to stage.** Step 1: split `execute()` into
`executeIbox`/`executeEbox` with NO behavior change (the two are called
exactly where the one was) -- rebuild, full suite green, commit. The
build should already shrink, since the preparation probe and I-box paths
no longer inline the FP arms. Step 2: introduce `mkArithmeticUnit`
wrapping `executeEbox`, route the removal path through it -- suite green,
commit. Step 3: add the iterative divide FSM inside the AU and enable the
Fp divide case -- a divide test (a/b with a known quotient) plus a
`CYCLES<=` bound from the ~3.5-bits/cycle rule. Each step is one revert
from green, per the project's rule.

**Risk.** The `executeEbox` arms set indicators and do index writes
through the same locals `execute()` uses; the split must carry those out
of both functions identically (an `AuResult`/`IboxResult` struct each).
bsc's one-write-per-rule scheduling means the AU's single `executeEbox`
call site and `step()`'s single `executeIbox` call site must not both
write storage in one rule -- they are in different rules (the AU is its
own module), so this is naturally satisfied.

## 7. Status

- **Stage 0 -- done** (2026-09-03): `CYCLES<=N` check in `gen_tb.py`;
  `stepCount` at halt is the clock count. Per-unit trace flag still
  to add.
- **Stage 1 -- done** (2026-09-03): `StretchMemory.bsv` (six units,
  interleave map, 7-clock cycle, 5-clock read-out, single-requester
  MBCU with nonexistent-address handling) and `StretchStorage.bsv`
  reworked as the bus client (in-order store queue of 8, one
  outstanding read, `responseReady`/`writeReady` handshake). Three
  stall guards in `StretchCore.step()`, and the generated and hand-
  written testbenches poll the handshake instead of assuming one-cycle
  latency. Full 20-block suite green unchanged; first cycle bounds
  recorded (Problem 2.1: 94 clocks; pp.43-51 span: 2714). Found on the
  way: Bluesim's BRAM is not zero-initialized (0xAA..), so tests must
  not rely on unwritten storage reading as zero -- the smoke test now
  halts on its own data word instead of on fall-through. Not yet
  modeled: the eight-channel priority arbitration (one requester so
  far), address-invalid indication for nonexistent addresses.

- **Stage 2a -- in test** (2026-09-03): tagged bus responses
  (`RetTag`: operand, 1Y, 2Y) in `StretchMemory.bsv`; three read
  channels with priority order stores > operand > 1Y > 2Y in
  `StretchStorage.bsv`, instruction fetches held while stores are
  queued (conservative program-store compare); `StretchCore.step()`
  now begins with the IC controls -- two `YReg` buffers filled ahead
  through their own channels, a two-clock I-checker delay, freeing
  behind the instruction counter, invalidation on a taken branch, on
  `setPC`, and on a store to a buffered word (`recentStore`), with
  in-flight fetches for invalidated buffers discarded on arrival --
  and prepares each instruction from the buffers (a full word may
  straddle 1Y/2Y). The old one-fetch-at-a-time FSM is gone. Two
  real findings from the suite on the way: (1) reads on the operand
  channel must still wait for queued stores (the first channel
  generalization dropped that and a testbench read a control word
  before its store reached memory); (2) a 16-word tape transfer
  streams stores faster than four interleaved 2.1 µs units absorb
  them and overflowed the 8-deep store queue -- the exchange now
  waits for queue space per word, and an instruction does not start
  while the queue is full (the LAAR-busy wait of Perf. Char. p.3-21
  in miniature). Cycle counts with prefetch overlap: Problem 2.1 94
  -> 54 clocks, the pp.43-51 span 2714 -> 2065.
- **Stage 2b -- done** (2026-09-03): per-class time budgets (§6a),
  `ibox_timing_cb.strap` (250 table clocks, measured 291).
- **Store-close-to-fetch: found 2026-09-03 by the floating-point
  diagnostic's sign-modifier test, FIXED same day.** A load whose
  operand word was written by an immediately preceding store read the
  stale value: the look-ahead's same-word wait compared fetch addresses
  (`da`) only, and an E-box store (ST/M+) writes at removal, so a younger
  load to that word fetched before the store retired. Fix: each E-box
  level now carries `storeAddr` (its store target, `storeTarget()` --
  Fp ST/M+/M+MG, VflInt ST/M+/M+MG/M+1), a load `waitFor`s the newest
  earlier level whose `storeAddr` equals its fetch word (every current
  level is program-earlier than a new one, and they retire head-first,
  so the newest such store covers all older ones), and `levelHolds`
  (the I-box hazard check) also matches `storeAddr`. Test
  `store_close_to_fetch.strap`: `ST(N),X ; L(N),X` now reads the new
  value; the same pattern failed before the fix. This is the
  store-into-a-nearby-operand case of Perf. Char. pp.3-20..21; genuine
  operand FORWARDING (returning the store data without a re-fetch) is a
  later refinement -- the load currently waits for the store to retire
  rather than being handed the value. Residual gap: Connective CM's
  store target is not tracked (no current program stores via CM then
  reloads).
- **E-box-register-close-to-fetch: found 2026-09-06 by jb_af1c F207C1,
  fixed same day.** The sibling hazard for the E-box's OWN registers,
  words 7-15. `storeTarget()` reports only stores to storage --
  deliberately, since an FP load or add writes the accumulator, not
  memory -- so nothing made a following VFL or connective fetch of one
  of those words wait. F207C1 is `CM1111(BU,8),10.0` / `DL(U),FPK1` /
  `CT0011(BU,3),10.5`: the CT read the sign byte one half-word after
  the DL that zeroes its flag bits, and got the pre-load value. The
  sign byte itself was correct at the halt, which is what pointed at
  ordering rather than arithmetic; three half-words of separation and
  the same pair passed. Fix: a level whose fetch word is 7-15 waits
  for the newest earlier valid level whatever that level does (there
  is no address to compare against). Conservative and free -- every
  measured cycle count in the suite is unchanged, since no benchmark
  fetches those words in a hazardous position. Test:
  `programs/ebox_register_close_to_fetch.strap`.
- **Stage 3a -- done** (2026-09-03; full 21-block suite green, Problem
  2.1 113 -> 92 clocks, pp.43-51 span 4006 -> 3985, the CB loop
  unchanged at 291 since it holds no E-box work): the look-ahead of §6b, seven
  bus tags, level channels in `StretchStorage`, `LaLevel` in
  `StretchTypes`, the engine in `StretchCore.step()` (levels
  collected/issued at the top of every clock; removal and preparation
  as branches of the one instruction chain so at most one `execute()`
  runs per clock). Follow-up: the E-box busy wait and the resume wait
  had preempted preparation (four loads measured 162 clocks against
  ~115); fixed, 120 clocks, benchmark `la_timing_loads.strap`.
- **Stage 3b -- done** (2026-09-03; 23-block suite green): I-box-class instructions run
  ahead of pending levels under §6c's hazard checks (`iboxHazard`:
  operand-word compare against every level's address for the direct
  index ops, refills, Z, SIC's store and its embedded branch; drain
  for branches on arithmetic indicators and for everything else).
  Benchmark `la_timing_loop.strap`: L/+/ST/V+/CB x10 in 807 clocks
  vs ~1120 serialized. Caught by the suite: the halt (a branch to
  itself) is unconditional and hazard-free, so it executed ahead of
  pending stores and the run ended before they retired -- unconditional
  branches now drain the levels first (the machine's "BD empties the
  LA" behavior, Perf. Char. p.3-18).
- **Stage 3c -- done** (2026-09-03; 24-block suite green): branch levels for branches on
  arithmetic indicators, guessed not taken; snapshot of the sixteen
  index words and the indicators at the guess (`snapshotIndex`/
  `restoreIndex` in `StretchStorage`); I-box stores stall while a
  guess is unresolved; wrong guess cancels the younger levels and
  recovers on the next clock (index words and index indicators
  restored, instruction counter to the target, Y buffers refetched,
  12 clocks charged). `la_branch_guess.strap`: one wrong and one right
  guess, 197 clocks; injection without the restore fails the wrong-
  guess check.
- **Idiomatic-Bluespec rewrite (§1c) steps 1, 4, 5a, 5b, 5c -- done**
  (2026-09-04/05, commits cc0d401, 0068366, 59a9627, aa6d8aa, 035e385;
  suite green with every cycle count unchanged at each step): the
  E-box as a module, `step()` split into per-clock rules, the core as
  its own compilation unit (suite ~12 min -> ~3.3 min cold, ~80 s
  warm), the instruction buffers / look-ahead / timing tables as their
  own packages, and the E-box as a start/busy/resume box owning its
  operand reads. Details and the measured numbers are in §1c.

## 8. Immediate next steps

1. The codesign roadmap, §1b item 2: FP arithmetic against the
   `jb_af1c` diagnostic -- the multiply and remaining add/subtract
   blocks, then the open ops in the order the diagnostic reaches them.
2. Optional structural refinements left by §1c: the multi-cycle
   SAU/PAU timing (steps 2b/3), the branch-guess snapshot into the
   look-ahead module, `mkEBox` as its own compilation unit.
3. Per-unit trace flag (stage 0 leftover).

---

# Appendix A. Gathered specifications (the knowledge base)

This appendix captures, cited by page, the primary-source facts gathered
for the rebuild, so the plan is self-contained and no knowledge lives
only in a session transcript or a code comment. Page numbers are printed
pages; PDF page = printed + 3 for the Reference Manual (22-6530-2) and
for C22-6531. Buchholz = *Planning a Computer System* (1962). Blosk =
TR00.722. Perf. Char. = 7030 Performance Characteristics vol.1 (Mar 61).

## A.1 Word formats and addressing (Ref. Manual pp.12-21)

- **Bit/word addressing**: 24-bit bit address = 18-bit word address (high)
  + 6-bit bit-in-word (low). The whole core is one consecutively
  numbered bit string; word boundaries may be ignored. Instructions use
  18-bit (full-word ops), 19-bit (half-word/branch/index/transmit), or
  24-bit (VFL integer/connective) address parts, with zeros filling the
  missing low-order bits.
- **Index word** (p.19): VALUE (bits 0-23) + sign (24), index flag XF
  (25), two unused bits (26-27), COUNT (28-45), REFILL (46-63). VALUE is
  a signed 24-bit field interpreted as a bit address. In I/O the flag +
  bits 26-27 become control bits and part of VALUE is status.
- **Indexing** (p.20): the index VALUE is added algebraically to the
  instruction address part (a positive unsigned field). Carry out of
  bit 0 (overflow) is ignored. X0 (word 16) is not available for
  address modification; I=0 means no modification. XF/XCZ/XVLZ/XVZ/
  XVGZ/XL/XE/XH are NOT changed when an index is used for address
  modification (only when modified by an index-arithmetic op).
- **Progressive indexing** (p.21, field P bits 32-34): P=0 direct, P=4
  immediate (effective address IS the operand), P in {1,2,3,5,6,7}
  progressive. The effective address is the index VALUE directly; then
  the instruction address part is added (1-3) or subtracted (5-7) into
  the VALUE; count stepped down (2,3,6,7); refilled on count zero (3,7).
  Index result indicators set from the new index before any refill.
  Only for variable-field-length ops. Executed in two parts (prepare,
  then modify) -- the model's `pendingIdxWrite` two-step.

## A.2 The floating-point instruction set (Ref. Manual pp.78-102)

- **Format**: exponent field bits 0-11 = EF flag (0), EM magnitude
  (1-10), ES sign (11); fraction bits 12-59 magnitude, 60 sign; data
  flags T/U/V bits 61-63. Value = (-1)^s * F * 2^((-1)^es * EM). Binary
  point left of bit 12; a 1 in bit 12 = one-half. Accumulator: exponent
  bits 0-11, fraction 12-59; fraction sign in the sign byte register
  (address 10) bit 4, flags in bits 5-7. Double precision: fraction
  12-107 (96 bits), accumulator bits 60-107 the low fraction.
- **Ranges** (Fig.22, p.79): N (EF=0, |E| <= 1023, magnitudes ~10^-308
  to 10^308), XFP ("infinity-like": EF=1, ES=0, E >= 1024), XFN
  ("zero-like": EF=1, ES=1, E <= -1024). Result exponent tables for
  flagged operands: Fig.23 (add/multiply/divide), which range dominates.
- **Normalization** (p.81, bit 18 modifier, 0 = normalized): a
  normalized fraction is 1 > F >= 1/2 or zero. Left shift subtracts from
  the exponent, a right shift for fraction overflow adds one. Zero
  fractions are not normalized. Pre-normalization aligns operands in add
  and divide.
- **Sign control** (p.81-82): bit 19 "absolute sign" forces the
  operand's sign positive before the op; bit 20 "negative sign" inverts
  the sign of the unreplaced operand. For accumulator-changing ops both
  apply to the storage operand; for stores, to the accumulator.
- **Data flags** (p.82): T/U/V of the addressed operand set TF/UF/VF for
  any op that fetches. Stores put the accumulator flags into the stored
  word's bits 61-63. Only LOAD/LOAD-DOUBLE/-WITH-FLAG set the sign
  byte's flag positions.
- **Zero definition** (p.82-83): order-of-magnitude zero keeps the
  exponent of the larger-exponent operand; a forced zero (ADD TO
  MAGNITUDE with a negative sum) sets RZ but not LS.
- **Noisy mode** (indicator NM, program-set only): ones instead of zeros
  enter the low-order bits during left-shift normalization.
- **Indicators** (pp.85-86): result RLZ/RZ/RGZ/RN (from the fraction
  sign/zero); to-memory MOP; LC (unnormalized overflow / left-shift-out
  of SHF / lost remainder bit); LS (add giving a zero from cancellation,
  with exceptions); PF (unnormalized divide, |dividend fraction| >=
  |divisor fraction|); ZD (zero divisor, division suppressed); PSH
  (exponent difference > 48 in add); ZM (normalized order-of-magnitude
  zero from multiply with exponent > -1024); exponent range XPFP
  (propagated EF, ES=0), XPO (generated EF, ES=0), XPH (1024 > E >= 512),
  XPL (512 > E >= 64), XPU (generated EF, ES=1); IR (STORE ROOT of a
  negative), RU (remainder underflow, divide double). Fig.24/27
  comparison-result tables (AL/AE/AH).
- **Operations** (arithmetic action, sign result altered):
  - *Single, cheap (no big multiply/divide) -- DONE or DOABLE now*:
    `+`/`+MG` (add, add-to-magnitude); `L`/`LWF` (load, load-with-flag);
    `M+`/`M+MG` (add-to-memory, add-magnitude-to-memory); `ST` (store);
    `K`/`KMG`/`KR`/`KMGR` (compare, magnitude, for-range, magnitude-for-
    range); `E+` (add addressed operand's exponent to the accumulator's,
    fraction ignored); `E+I` (add bits 0-11 of the effective address as
    an exponent; no storage access, not boundary-monitored); `SHF`
    (shift the fraction, bits 0-10 amount / bit 11 direction; LC on a
    left-shift-out; no storage access); `F+` (add to fraction -- like
    add but both operands take the accumulator's exponent, no pre-shift).
    DONE: `+ +MG L LWF M+ M+MG ST K KMG KR KMGR * E+ E+I SHF`.
  - *Single, heavy (full multiply/divide) -- stage 4e AU*: `*` (DONE,
    48x48 multiply), `/`, `R/` (reciprocal divide), `SRT` (store root,
    exponent halved + fraction square root).
  - *Double precision -- stage 4e AU*: `D+`/`D+MG` (add double), `DL`/
    `DLWF` (load double), `SRD` (store rounded, +1 at bit 60 then
    truncate to 48), `SLO` (store low-order half), `D*` (multiply
    double), `LFT` (load factor into the FT register, address 14, for a
    following `*+`), `*+` (multiply FT by the operand, add to
    accumulator, 96-bit intermediate), `D/` (divide double, 49-bit
    quotient + remainder in RM register address 13).
  - Multiply: exponents added, 96-bit product, post-normalized up to 96
    places. Divide: divisor and dividend pre-normalized, 48-bit quotient
    (49 for double), exponent difference +1 on quotient overflow.

## A.3 The interrupt and indicator system (Ref. Manual pp.43-53)

- **Indicator register** (word 11): 64 bits, Fig.11 lists each with a
  mask class. Equipment check (MK/IK/IJ/EK, mask permanent 1), attention
  (TS/CPUS), I/O reject (EKJ/UNRJ/CBJ) and status (EPGK/UK/EE/EOP/CS),
  instruction exception (OP/AD/USA/EXE/DS/DF/IF), result exception
  (LC/PF/ZD and the FP-only IR/LS/PSH/XPFP/XPO/XPH/XPL/XPU/ZM/RU), data
  flags (TF/UF/VF/XF), transit (BTR/DTR), program (PG0-6 program-set),
  index result (XCZ/XVLZ/XVZ/XVGZ/XL/XE/XH), arithmetic result (MOP/RLZ/
  RZ/RGZ/RN), accumulator compare (AL/AE/AH), mode (NM). Indicators are
  temporary (reset by the next relevant result) or permanent (stay until
  interrupt or programmed reset). Class T/P/C/H/S = when actuated
  relative to the instruction.
- **Mask register** (word 12): bits 0-19 permanently 1, 20-47 program-
  settable, 48-63 permanently 0. A masked (mask=1) indicator turning on
  while the interrupt system is enabled causes an interruption.
- **Interruption address register** (18 bits): the interruption develops
  the number of the left-most actuated masked indicator, adds it to the
  interruption address, and fetches ONE instruction executed before a
  second interruption can occur. The instruction counter is not stepped;
  a successful branch in that instruction can replace it. IF cannot be
  turned on by the fetch of that instruction even in protected storage.
- **Enable state**: BRANCH ENABLED (BE) enables the interrupt system,
  BRANCH DISABLED (BD) disables it, BRANCH ENABLED AND WAIT (BEW)
  enables and stops (there is no machine stop; only BEW). The model
  treats BE/BD/BEW as plain branches today -- the enable flag is the
  small state to add (a Reg#(Bool)), a prerequisite for DS/DF/IF and
  interruptions.
- **Correction-routine patterns** (p.48-49): single instruction; a
  subroutine entered by STORE-INSTRUCTION-COUNTER-IF-BRANCH-DISABLED and
  returned by BRANCH ENABLED; up to 48 routines addressed from the
  interruption address register.
- **EX / EXIC** (pp.49-50): EXECUTE gives the address of a subject
  instruction fetched and executed without stepping the instruction
  counter; EXECUTE INDIRECT AND COUNT uses a pseudo-instruction counter
  stepped after the fetch. A subject instruction may not change the
  interrupt state or the instruction counter (EXE indicator). Table 6
  (Perf. Char.) gives their timing: decode + LA drain + fetch (per an
  address-dependent table) + the subject op + LA drain + 3.0 us refetch.

## A.4 Remaining instruction semantics (Ref. Manual pp.22-33, 55-77)

- **Refill (R) / Refill on Count Zero (RCZ)** (p.26): replace the full
  word at the effective address's word with the word at that index
  word's REFILL field (bits 46-63). RCZ only if the count field (28-45)
  is zero. Index flag / index result indicators set from the original.
- **Count and Branch (CB) / Count, Branch, Refill (CBR)** (p.26): count
  down index J, increment VALUE per the advance code (bits 23-24: 00
  none, 01 add one in bit 18 = a half-word = 32 bits, 10 add one in bit
  17 = a word = 64 bits, 11 subtract one in bit 17), then branch on the
  resulting count being non-zero (or zero, bit 30). CBR also refills if
  the count reached zero.
- **Rename (RNX)** (p.27): store the index word in J into X0's REFILL-
  addressed location, put the effective address's word into J, replace
  X0's refill with bits 0-17 of the effective address. AD/DS/DF rules
  for names in 0-31.
- **Load Value with Sum (LVS)** (p.28): add (into bits 0-24 of J) the
  value fields of the index registers selected by ones in address bits
  0-15 (multiple indexing); no address modification.
- **Load Value Effective (LVE)** (p.28-29): indirect addressing -- the
  effective address selects another instruction whose own effective
  address (+ sign) is placed in J; chains through further LVEs; a loop
  is broken after ~1 ms by USA. The final non-LVE instruction is not
  executed, only its effective address computed.
- **Store Value in Address (SVA)** (p.29-30): replace the address field
  (18/19/24 bits per the target op's class) of the instruction at the
  effective address with bits 0-17/18/23 of J's value field. Used for
  self-modifying setup in the diagnostics.
- **Transmit (T) / Swap (SWAP)** (p.30-31): move a block of `count` full
  words (count from index J bits 28-45, 0 meaning 2^18; or immediate,
  bits 51-54, 0 meaning 16) from the left effective address to the right.
  Modifier bits 55-57: 57 = bidirectional (swap), 56 = immediate count,
  55 = backward (addresses decrement). Only forward, one-word-at-a-time,
  non-swap is modeled today.
- **VFL integer** (pp.55-77): L/ST/+/M+/K and variants, byte size 1-8,
  offset (accumulator bit position), signed/unsigned/decimal/binary
  modifiers; immediate addressing (P=4) with the operand left-justified.
  Decimal mode and radix conversion decode but are OP-invalid today.
- **Connectives** (Fig.20, p.75-77): 16 boolean functions x {CONNECT
  (to accumulator), CONNECT TO MEMORY, CONNECT FOR TEST}; byte size 8
  assumed; the left-zeros / all-ones counts at word 7 and partial-field
  padding not modeled.
- **Bit branching** (p.100): a full-word op testing/optionally modifying
  a single indicator bit anywhere in storage. Decoded, not executed.

## A.5 The arithmetic units (Buchholz pp.208-216, Perf. Char. ch.3)

- **Serial arithmetic unit (SAU)**, Fig.14.6: symmetric byte extraction
  (16-of-128 then 8-of-16 switch matrices) from A/B (accumulator) and
  C/D (operand), a binary adder OR a logic unit, true-complement switches
  before and after, a decimal corrector, one byte-pair per clock. Handles
  VFL add/subtract/compare/load/store, connectives, decimal, radix
  conversion, FP exponent arithmetic. SAU equation (Perf. Char. table 3):
  pre-execution 1.8 us, execution 0.6 us per byte, termination 0.6 us
  (7.2 us full-word), plus unlike-sign/recomplement/forced-zero extras.
- **Parallel arithmetic unit (PAU)**, Fig.14.7: 100-bit carry-propagate
  adder with 4-bit carry look-ahead (0.15 us for 96 bits, 1s-complement
  subtraction with end-around carry to absolute-value form); a shifter
  (4 right / 6 left per step); the multiply tree -- 12 multiplier bits
  per cycle decoded as four 3-bit groups selecting +-multiplicand
  multiples fed to four carry-save adders (S = A xor B xor C, C' = AB or
  AC or BC), two in parallel then two in series; divide by table-selected
  multiples 1, 3/2, 3/4 of the divisor skipping over 1s/0s (~3.5 quotient
  bits per cycle, Figs 14.11-14.13). Handles FP fraction add/multiply/
  divide (single 48-bit, double 96-bit) and VFL binary multiply/divide.
  FP instruction times: Perf. Char. table 2 (pre-execution + execution
  cycles at 0.3 us).

## A.6 The instruction unit and look-ahead (Blosk, Buchholz ch.15, Perf. Char.)

- **I-box registers** (Blosk pp.7-15): ICR (19) + adder giving n..n+3;
  1Y/2Y (two 64-bit instruction buffers, four half-word instructions);
  index storage XS (17-word x 73-bit core, word 17 = timer/clock, 500 ns
  read, 2 cycles to store) with data register XR; preparation/execution
  register Z (64 + 3-bit P); working register W (19); 24-bit index adder
  IAU with in-buses A (IC/W/XR/Z, complementable) and B (Y/Z); shared
  I-checker (ECC->parity, 0.6 us); updated indicator register (XF/XCZ/
  XVLZ/XVZ/XVGZ/XL/XE/XH). Up to six instructions in progress.
- **Control areas** (Blosk pp.25-27): IC controls (keep 1Y/2Y full,
  program-store compare invalidates a prefetched word); preparation
  controls (Y->Z transfer, XF index fetch, MOD modification, WBC word-
  boundary-crossover test); look-ahead load; instruction-execution
  (I-box ops execute here); branch (index-indicator and unconditional
  resolved in the I-box; arithmetic-conditional guessed not taken).
- **Look-ahead** (Buchholz ch.15, Cocke/Kolsky III.C): four levels, each
  {op code, 8 tags (level filled/checked, internal operand, IC valid, LA
  op code, word-boundary crossover, no-op, from), 15 indicators, IC,
  64-bit operand + forwarding bit F + forwarding address FA}; five ring
  counters C1 (I-unit/IAU load), C2 (operand fetch), transfer-bus, C4
  (arithmetic remove), C3 (store check), advancing under interlocks I1
  (unexecuted store), I2 (store), I3 (all fetches started), I4 (next
  ready), I5 (unexecuted arithmetic op); one LAAR with store forwarding
  (store-close-to-fetch cases (1)-(3), Perf. Char. pp.3-20..21); all
  stores done by LA; index-recovery pseudo-store levels; recovery
  (housecleaning) on interrupt or wrong-way branch. Bus priority:
  exchange > disk > look-ahead > I-box (8 requesters).
- **I-box timing tables** (Perf. Char. ch.3, dec = 0.6 us, at 0.3 us
  clocks): table 4 direct index (LX 4.8, LV/LC/LR/SV/SC/SR/V+/V+C/KV/KC
  4.2, SX 1.2, V+CR 8.4 us + dec), table 5 immediate (LVI/LCI 2.4,
  V+IC 3.0, V+ICR 7.2), table 6 misc (R/RCZ/Z, EX/EXIC with LA drains),
  table 7 unconditional branch (B 3.6, BR 4.8, NOP 1.2, BD +2 LA drains),
  table 8 index branch (CB successful 4.2 / unsuccessful 3.6, CBR 6.6/
  6.0). FP prep one per 1.2 us; VFL prep 3.6 us min + 0.6 per level or
  index. Table 9 transmit.

## A.7 Memory, address monitoring, clocks, states (Buchholz ch.14, Ref. Manual pp.15,20,51-54)

- **Memory** (Buchholz §14.1): 16,384-word units, 2.1 us read-write
  cycle, own clock/addressing/data registers; six units typical -- four
  4-way interleaved (65,536 addresses) + two 2-way (32,768). MBCU
  (§14.3): 8 requesters, priority as above, one request per 0.3 us,
  ~1.6 us return when free, holds requests for busy units, 3-bit return
  tag.
- **Address Invalid** (p.20): an effective word address not physically
  installed sets AD; the instruction executes as a NO OPERATION. A
  branch to an invalid address is also a no-op; a negative effective
  address is not invalid (its magnitude is used).
- **Address monitoring / storage protection** (p.15): two boundary
  registers (word 3: upper 0-17, lower 32-49, control bit 57) define a
  region; an alarm (DS store / DF fetch / IF instruction fetch, gated by
  the interrupt system enabled + mask) fires for an effective address
  inside OR outside the region, control-bit selectable; storing in
  protected areas is suppressed. (Control-bit polarity still to source
  from Appendix C.)
- **Clocks** (p.15): interval timer measures short intervals, settable,
  sets Time Signal (TS) when the period ends, can interrupt; time clock
  runs continuously, not programmer-alterable. Word 1 = timer bits 0-18,
  clock 28-63 (Appendix C). Step rate still to confirm.
- **System states** (pp.51-54): running, programmed waiting (BEW),
  initial program load (IPL key: terminate current op, disable
  interrupts, run from a channel signal), initial power on (registers
  0-12 random, interrupts disabled). Two status lights (running /
  inactive). At power-on registers 0,2-12 hold random bits.

## A.8 Timing oracles (Perf. Char. vol.1 ch.4 + vol.2)

- **Table 10** (p.4-9), "Execution Frequency Chart": per benchmark, the
  count of each operation, total execution time (ms), average us/op.
  Weather inner-loop AO: 1711 ops (FP 1364, VFL 98, index 100, branch 97,
  misc 52), 5.98 ms, 3.5 us/op; A1 5.57; A2 7.0135; grid param 1883 ops,
  7.07 ms, 3.8; elementary functions .38/.309 ms.
- **Benchmarks** (source in vol.2, 189 pp): GERB2 matrix inversion (10x10
  0.02 s ... 100x100 14.61 s), MXM16 matrix multiply (25x25 0.20 s ...
  125x125 21.44 s), PRIMC prime sieve 106.7 s (two-thirds an
  interruption table -- the interrupt timing test), Monte Carlo 10,000
  particles 33 s. These are the stage-5 `CYCLES<=` oracles once their
  source is transcribed.

## A.9 Complete instruction mnemonic set (pocket card X22-6533)

The authoritative enumeration of every documented instruction, from the
STRAP mnemonic operation-code tables on the pocket card. "(A)" = sign
modifiers N/A/NA apply; "(I)" = index field; "(dds)" = data description.
This is the master checklist for "every documented feature"; each
non-modeled entry is a future target.

**Floating point (full word).**
Add/subtract family: `+ -` , `+MG -MG` (to/from magnitude). Multiply:
`* *+ *A+ *N+ *NA+` (multiply, multiply-and-add and its absolute/negative
variants). Divide: `/ R/` (divide, reciprocal divide). Double precision:
`D+ D- D+MG D-MG DL DLWF D* D/`. Exponent: `E+ E+I E+AI E- E-I E-AI`
(add/subtract, immediate, absolute-immediate). Fraction: `F+ F-`. Shift:
`SHF SHFL SHFR` (by address / dedicated left / dedicated right). Load:
`L LWF LFT DL DLWF`. Store: `ST SLO SRD SRT SNRT Z` (store, low-order,
rounded, root, negative root, zero). Compare: `K KMG KR KMGR`. Misc:
`NOP R RCZ`. Branch: `B BD BE BEW BR`. `SIC` (store instruction counter
if). `EX EXIC` (execute, execute indirect and count).
*Modeled now*: `+ +MG - -MG L LWF ST K KMG KR KMGR M+ M+MG * E+ E+I SHF`
(SHF by address) `B BD BE BEW BR NOP R RCZ Z SIC`. *Open (stage 4e /
later)*: `* variants *+ / R/ SRT SNRT`, all double precision, `E±I/AI
E-`, `F+ F-`, `SHFL SHFR`, `LFT`, `EX EXIC`.

**Variable field length (full word).** `+ +MG - -MG` , `* *+ *I+ *N+
*NI+ /` (multiply/divide, immediate/negative variants), `C CM CT` (the
16 connectives x connect / to-memory / for-test), `CV DCV LCV LTRCV`
(convert, convert double, load converted, load transit converted),
`K KE KF KFE KFR KR` (compare and compare-field family), `L LF LWF LFT
LTRS` (load, load field, with flag, factor, load transit and set),
`M+ M+1 M+MG M+A M- M-1 M-MG M-A` (to-memory add/subtract, one, magnitude,
absolute), `SF SRD ST` (store field, rounded, store). Modes: B/BU/D/DU
(binary/unsigned, decimal/unsigned) and P (progressive). *Modeled*: `L
ST + M+ K`, binary modes, connectives (BS=8), immediate (P=4),
progressive. *Open*: decimal, radix conversion (`CV/DCV/LCV`), multiply/
divide, compare-field variants, `SF`, `M±1`, `M±A`, transit ops.

**Direct index arithmetic (half word).** `LX LV LC LR SX SV SC SR`
(load/store value/count/refill/index-word), `V+ V+C V+CR V- V-C V-CR`
(advance value, count, count+refill), `KV KC` (compare value/count),
`RNX LVE LVS SVA` (rename, load value effective, load value with sum,
store value in address). *Modeled*: `LX LV LC LR SX SV SC SR V+ V+C V+CR
KV KC`. *Open*: `V- V-C V-CR` (subtract), `RNX LVE LVS SVA`.

**Immediate index arithmetic (half word).** `LVI LVNI LCI LRI C+I C-I
V+I V+IC V+ICR V-I V-IC V-ICR KVI KVNI KCI LVS`. *Modeled*: all but
`LVS`.

**Count and branch (half word).** `CB[R][Z][H|+|-]` -- the 16 variants
(count, +refill, +branch-on-zero, +half/plus-one/minus-one value).
*Modeled*: all 16 encode; CB and CBR executed and tested.

**Branch on indicator (half word).** `B[Z]<indicator>[Z]` for each of
the 64 indicators (branch on, or on zero of, optionally clearing).
*Modeled*: full grammar, index and arithmetic indicators.

**Branch on bit (full word).** `BB BB1 BBN BBZ BZB BZB1 BZBN BZBZ`
(branch on bit, set-to-one, negate, zero, and the zero-bit forms).
*Open*: decoded, not executed.

**Transmit (full word).** `T T] SWAP SWAP]` (transmit / swap, forward /
backward with the "]" backward marker), immediate or index count.
*Modeled*: forward `T`, one word, non-swap.

**Input-output (full word).** `RD W CCW REL CTL LOC` (read, write, copy
control word, release, control, locate) each with an optional `(SEOP)`;
control functions `BS SP SPFL ERG REW UNLOAD WEF CRDRUN` (backspace,
space, space file, erase gap, rewind, unload, write end of file, card
run-out), density/parity `HD LD ECC EVEN NOECC ODDECC ODDNEC`, and light/
gong `KLN RLF RLN TILF GONG`. *Modeled*: `RD W CCW REL`, `CTL` for the
tape's REWIND/BACKSPACE codes; the rest of the control functions open.

## A.10 Special storage assignment and indicator list (pocket card X22-6533-1)

The exact special-storage layout (addresses 0-31) and the complete
indicator list, read off the reference card. This supersedes the
approximate bit positions given above where they differ.

**Special storage assignment** (Length = field width in bits, then bit
positions; P = permanently protected area):
| Addr | Name | Bits |
|---|---|---|
| 0 | Zero | 0-63 |
| 1 (P,a) | Interval Timer | 0-18 |
| 1 (P,b) | Time Clock | 28-63 |
| 2 (P) | Interruption Address | 0-17 |
| 3 (P) | Upper Boundary | 0-17 |
| 3 (P) | Lower Boundary | 32-49 |
| 3 (P) | Boundary Control Bit | 57 |
| 4 | Maintenance Bits | 0-63 |
| 5 (b) | Channel Address | 12-18 |
| 6 | Other CPU Bits | 0-18 |
| 7 | Left Zeros Count | 17-23 |
| 7 | All Ones Count | 44-50 |
| 8 | Left Half of Accumulator | 0-63 |
| 9 | Right Half of Accumulator | 0-63 |
| 10 | Accumulator Sign Byte | 0-7 |
| 11 (c) | Indicators | 0-63 |
| 12 (d) | Mask | 0-63 |
| 13 | Remainder | 0-63 |
| 14 | Factor | 0-63 |
| 15 | Transit | 0-63 |
| 16-31 | Index Registers X0-X15 | 0-63 |

Footnotes: a = read-only except for store-value/count/refill/address;
b = read operation only; c = indicator bits 0-19 are read-only;
d = mask bits 0-19 always one, 48-63 always zero. (This is why the
model keeps word 11 read-only via generic STORE and word 12's mask
forced.) The interval timer and time clock are BOTH in word 1 (a
19-bit down-counter in 0-18 and a 36-bit up-counter in 28-63); the
boundary control bit is bit 57 -- its inside/outside polarity is the
one storage-protection detail still to source. The timer/clock STEP
RATE is not on the card and remains to source.

**Indicator list** (No. / mnemonic / mask / class): mask 1 = permanently
masked (0-19), m = program-settable (20-47), 0 = permanently unmasked
(48-63). Class: P permanent (off only by interruption or branch-on-
indicator), T temporary (reset by a later relevant operation), C when
set the instruction still completes, H when set execution terminates,
S when set execution is suppressed (except EX/EXIC/T/SWAP).
0 MK(P,H) machine check; 1 IK(P,H) instruction check; 2 IJ(P,S)
instruction reject; 3 EK(P,C) exchange control check; 4 TS(P,C) time
signal; 5 CPUS(P,C) CPU signal; 6 EKJ(P,S) exchange check reject; 7
UNRJ(P,S) unit not ready reject; 8 CBJ(P,S) channel busy reject; 9
EPGK(P,C) exchange program check; 10 UK(P,C) unit check; 11 EE(P,C) end
exception; 12 EOP(P,C) end of operation; 13 CS(P,C) channel signal; 14
reserved; 15 OP(P,S) operation code invalid; 16 AD(P,S) address invalid;
17 USA(P,S) unended sequence of addresses; 18 EXE(P,S) execute
exception; 19 DS(P,S) data store; 20 DF(P,* ) data fetch; 21 IF(P,* )
instruction fetch (* = class S when mask one, else C); 22 LC(P,C) lost
carry; 23 PF(P,C) partial field; 24 ZD(P,C) zero divisor; 25 IR(P,C)
imaginary root; 26 LS(P,C) lost significance; 27 PSH(P,C) preparatory
shift > 48; 28 XPFP exp flag positive (E >= 2^10); 29 XPO exp overflow
(E >= 2^10); 30 XPH exp high (2^10 > E >= 2^9); 31 XPL exp low (2^9 > E
>= 2^6); 32 XPU exp underflow (E <= -2^10); 33 ZM exp flag negative (E
<= -2^10); 34 RU remainder underflow (E <= -2^10) -- all P,C; 35 TF, 36
UF, 37 VF data flags T/U/V (T,C, reset by VFL/FP ops needing a data
fetch); 38 XF(T,* ) index flag (* = class S with index branching + mask
one + system enabled, else C); 39 BTR(P,C) binary transit; 40 DTR(P,C)
decimal transit; 41-47 PG0-PG6(P,C) program indicators; 48 XCZ, 49 XVLZ,
50 XVZ, 51 XVGZ index count/value zero/less/greater (T,C, reset by
index arithmetic other than comparisons); 52 XL, 53 XE, 54 XH index
low/equal/high (T,C, reset by index comparisons); 55 MOP(T,C) to-memory
op; 56 RLZ, 57 RZ, 58 RGZ, 59 RN result less/zero/greater/negative
(T,C, reset by VFL/FP non-comparison ops); 60 AL, 61 AE, 62 AH
accumulator low/equal/high (T,C, reset by comparisons); 63 NM(P,C)
noisy mode.

**Transmit/Swap and index-arithmetic mnemonics** (completing A.9 from
the card's own tables): `T TI TB TBI` (transmit, immediate, backward,
backward-immediate) and `SWAP SWAPI SWAPB SWAPBI`; count-and-branch
`CB/CBR/CBZ/CBRZ` each with `+`/`-`/`H` (add one / subtract one / add
half to value), `K` meaning index register 1 only; index arithmetic
`C+I C-I KC KV LC LR LV LVE LVS LX RNX SC SR SV SVA SX V+ V+C V+CR V+I
V+IC V+ICR V-I V-IC V-ICR` (`*` codes = immediate or, in OP2,
progressive indexing).
