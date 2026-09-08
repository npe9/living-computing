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
   (D+MG / D-MGA) and STORE ROUNDED (SRD) -- and it only gets to F+
   (add to fraction) and E+I (add immediate to exponent) later still,
   with multiply later than that. (This sentence used to name those
   two as "F212" and "F213 ... around pp.128-135". Falsified from the
   page 2026-09-07: F212 is the SHIFT FRACTION TEST ROUTINE and it
   begins on p.115, immediately after F211. The routine numbers for
   F+ and E+I were a guess; they are left unnamed here rather than
   guessed a second time.) So the next codesign
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
   jb_af1c F209D6-D9 (p.107) is the Lost Significance half, and D7 --
   DL(U) FPK0 + D+MG(U) FPK0, a zero result that must NOT set LS -- is
   the printed source of the exception clause in the F208D5 LS fix,
   which until now rested on p.96's wording alone. Dropping that clause
   halts D7 (SIC stores 015661.00) and leaves F209D1-D5 and F208D7-D11
   green. D9 is the first LS question put to the flagged path; setting
   r.ls on fpAddDouble's flagged-path return halts it (015670.00), so
   that path's silence on LS is pinned rather than merely untested.
   BLSZ (46) was new encoding ground -- the first branch-on-indicator
   with both the clear and branch-on bits set -- and assembled right
   unchanged. Transcribed as printed: D8's header says "LS INDICATOR
   OFF" while its question is BZLS, "error if LS ind off", which
   requires it ON; the encodings settle it.
   Checking the label column while transcribing turned up a fidelity
   slip worth remembering. F209D1-D5 carried FADM4 as its entry label,
   but p.106 prints NO label at 015614.40, and the listing's real FADM4
   is at 015672.00, on F209E1. FADM2 (015365.40) and FADM3 (015576.40,
   confirmed by the exit's B,FADM3) are genuine. Both F209D programs
   now use ENTRY, with a note; F209E uses FADM4 at its true address.
   jb_af1c F209E "TEST FORCED ZERO RESULT" (pp.107-108) is the block
   the whole D+MG series was heading toward: E1-E4 (015672.00) is the
   first thing anywhere in jb_af1c that reaches fpAddDouble's UNFLAGGED
   forced zero. FPK37 and FPK38 share exponent 0031 with |FPK37| >
   |FPK38|, so subtracting FPK37 from the accumulator's magnitude
   gives the negative sum p.95 replaces with a zero fraction.
   Constant-folding the forced-zero guard to False halts E1 at
   015677.00 and leaves F209A, F209C, F209D1-D5 and F209D6-D9 all
   green: nothing else in the suite covers it, and the path had been
   written from the manual and never executed. E3 and E4 load the
   accumulator negative, putting the forced zero and the F209D1
   sign-restore ordering in the same instruction.
   E5-E8 (p.108) reach the same forced zero from the other side. FPK43
   is FPK37 with its sign bit set -- same exponent, same magnitude,
   negative -- so D+MG ADDS a larger negative operand where E1-E4
   subtracted a positive one. E6 and E8 use D-MGA, whose A-then-minus
   double inversion lands on the same arithmetic through a different
   route in strip_fp_sign. All eight passed on the first run.
   **The exponent question survives F209E untouched, and the earlier
   expectation that F209E would settle it was wrong.** Every CT0110 in
   E1-E8 is 48 bits at offset 20 or 68, together covering IBM 12-107 --
   the fraction only. IBM 0-11 is never compared. And both operands
   share an exponent throughout, so the manual's reading (keep the
   accumulator's) and fpAdd's (keep the larger operand's) would agree
   here even if the exponent were checked. Whether anything in jb_af1c
   distinguishes them is still unknown.
   jb_af1c F209E9 (pp.108-109) closes F209 out in six rows: clear LS
   with BLSZ, re-run E8's arithmetic (which the listing itself
   annotates "FORCED ZERO RESULT"), ask once with BLS that LS came out
   OFF. It is the oracle for the last unverified term in the
   double-precision LS rule -- F208D5 forced the res.frac term and
   F209D7 the both-zero term, but a forced zero HAS a zero result
   fraction, so without !forcedZero LS would come on and nothing until
   now both produced a forced zero and asked about LS. Dropping it
   halts E9 at 015770.00 with F209D6-D9 and F208D7-D11 green. All
   three terms are now under a run.
   One more injection pins the D-MGA claim in E5-E8: dropping the abs
   bit from strip_fp_sign's D-MGA rule halts E6 (015744.00), while
   F209E1-E4 stays green (its D-MGA operand FPK37 is already positive,
   so abs is a no-op) and F209E9 stays green (its question is blind to
   it -- no abs means no forced zero, and LS is off either way). E6/E8
   are the only place in the suite where the A-then-minus ordering is
   observable.
   METHOD NOTE, learned the hard way this session. A killed injection
   script left stale artifacts in bsv/build, bsv/simbuild and the _sim
   binaries, and a subsequent run reported PASS from a stale
   simulator. The give-away was the PC: 14314, which belongs to
   F209E5-E8, not E9's 14320. Every run_program.sh result prints the
   PC alongside the program's own PASS symbol -- if they disagree, the
   binary is stale. Delete the three artifacts and rebuild before
   trusting anything.
   jb_af1c F210A1-A2 (p.110) drove SRD's execute arm, which is the
   first model work since the D+MG rules -- SRD decoded but set
   OP-invalid. It passed on the first implementation, and three
   injections say precisely how much of it the block pins. Removing
   the rounding entirely halts A1 at 016002.40. But rounding one place
   LOW (IBM 59) and one place HIGH (IBM 61) BOTH PASS, because A1 and
   A2's accumulator fraction is 96 ONES: a +1 anywhere in the
   discarded low half carries the whole way out to the same zero
   result. So they pin that rounding happens, that the overflow is
   lost, that the XFP/XFN exponent is unchanged, and the stored sign
   -- but not the bit position their own comment names.
   AN OPEN QUESTION FOR F210A3, worth stating before it is run. A3 is
   DL(U) FPK0 -- a zero accumulator -- then SRD(U) ROS, expecting
   FPK68 = 0000000000000000000020, whose fraction is 1 in its LEAST
   significant bit, IBM 59. Adding 1 at IBM 60 to a zero fraction sets
   a bit in the DISCARDED half and stores a zero fraction, not a one.
   Either SRD really rounds at IBM 59, or A3's CT0110 offset (68,
   where A1/A2 use 4) means something other than it appears. The model
   rounds at IBM 60 on the manual's own words ("adding one to the
   fraction in the accumulator in bit position 60", p.96); A3 is the
   run that decides. Note that whichever way it goes, A1/A2 stay green
   -- so A3 is not redundant with them, it is the only thing that can
   settle it.
   jb_af1c F210A3-A4 (p.110) answers it, and the answer is that the
   model was right and the question above was mis-posed: both passed
   on the first run with the rounding at IBM 60. A3's offset-68 check
   reads what the manual implies; the reading that FPK68's low-order
   one had to come from the rounding was simply wrong.
   The coverage it adds is real but narrower than "pins the position".
   Injecting the rounding one place LOW (IBM 59, inside the KEPT
   fraction) halts A3 at 016020.40 while A1-A2 stays green -- the
   complement of A1-A2's blindness. But rounding one place HIGH (IBM
   61) leaves BOTH green, because for these operands any one placed
   below IBM 60 propagates the same carry: A3's fraction is zero so
   nothing carries either way, and A4's low half is all ones so
   everything does. So A1-A4 together pin the BOUNDARY -- the rounding
   one lands in the discarded half, not in the kept fraction -- and
   nothing in the routine so far distinguishes IBM 60 from IBM 61 or
   lower. Worth remembering if a later SRD sub-test ever disagrees.
   jb_af1c F210A5 (p.110) closes F210A "ARITHMETIC CHECKS" in eleven
   rows, and it is the unflagged analogue of A1: a 96-bit all-ones
   fraction in the N range at exponent +2, so the rounding overflows
   out of the kept 48 bits, and the expected result FPK67 still has
   exponent +2. That is the unnormalized rule -- "the overflow bit
   does not enter storage but sets LC" -- and A5 is the only place it
   meets an exponent that would move if the carry were absorbed.
   Absorbing it halts A5 at 016037.40 with F210A1-A2 and F210A3-A4
   both green.
   STILL UNCOVERED in F210A: the lost carry indicator itself. A5
   produces the overflow that sets LC and never asks about it; there
   is no BLC or BZLC anywhere in A1-A5. The routine's "TEST
   NORMALIZATION MODIFIER" section (F210A6, from 016041.40) is the
   next candidate, and it is also the first thing that will exercise
   SRD's NORMALIZED path -- every sub-test so far is SRD(U).
   jb_af1c F210A6-A7 (p.111), the routine's "TEST NORMALIZATION
   MODIFIER" section, is the FIRST SRD(N) in the diagnostic -- every
   sub-test through A5 is SRD(U), so the model's normalized path had
   never run. A6/A7 run it in the XFP and XFN ranges, where p.96 says
   normalization is suppressed, and their expected results FK109 and
   FK110 are still UNNORMALIZED (four and two leading zeros). Both
   passed first run. Honouring the modifier for flagged operands halts
   A6 at 016047.00 with A1-A5 all green -- A1/A2 are flagged too but
   round to a ZERO fraction, and normalizing zero shifts nothing, so
   A6/A7 are the first flagged sub-tests whose result is nonzero AND
   unnormalized, which is what it takes to tell the behaviours apart.
   Note SRD's normalized path on the UNFLAGGED side is still
   unexercised: F210A8 "TEST NORMALIZATION PROCESS" (016054.40) is
   where that starts, and it is also still the first candidate for LC.
   jb_af1c F210A8 (p.111) closes F210A and is the ONE sub-test in the
   routine where SRD actually normalizes: FK47 (exponent +50, fraction
   000fffffffff) with FK22's all-ones low half rounds to
   001000000000, which shifts eleven places left to 800000000000 and
   takes the exponent to +39 -- exactly FK52, pre-computed before the
   run. Forcing the unflagged path never to normalize halts it at
   016062.00 with A1-A7 green; A6/A7 survive because they are flagged,
   where the shift was already suppressed.
   jb_af1c F210B "TEST UNCHANGED REGISTERS" (p.111, 27 rows) guards
   p.96's "the entire accumulator and its sign byte register remain
   unchanged". B2's questions are live -- redirecting SRD's write to
   the accumulator's left half halts B2A (016103.40) and to the sign
   byte halts B2C (016107.40) -- while B1's do not fire, its registers
   being zero and a zero write leaving them zero.
   A STRUCTURAL FINDING from trying to break it the other way. SRD
   cannot be made to violate the rule by ADDING a write: an
   st.writeWord(addrAccSignByte, ...) alongside the existing
   st.writeWord(ea, ...) is a COMPILE error (bsc G0004, "methods that
   conflict in parallel"), because the variable-address write may
   itself target the sign byte -- the manual's own "unless used as the
   effective address". So the current write-port arrangement enforces
   the rule that F210B checks. That guarantee belongs to the
   arrangement, not to SRD, so F210B stays in the suite even though no
   single-line mutation isolates it today: it is the guard that would
   catch the rule being lost if the write ports are ever rearranged.
   (This previously named "section 1c step 5c's refactor" as the thing
   that would rearrange them. That refactor has since been withdrawn --
   see the 1c-audit -- so no such change is planned; the guard is kept
   against any future one.)
   jb_af1c F210C "ACCUMULATOR FLAGS TO MEMORY FLAGS" (pp.111-112, 22
   rows) guards the other half of p.96's storage-word sentence -- the
   accumulator flag bits go to storage bits 61-63, where F210A's BZB
   questions covered only bit 60, the sign. C1 pre-loads ROS with ONES
   before zeroing the accumulator, making it a test of COPYING rather
   than of leaving alone. Forcing the unflagged branch to write flags
   111 halts C1 at 016116.40 with F210A3-A4 green.
   A NARROW GAP found while probing C: the same forcing applied to the
   FLAGGED branch changes nothing anywhere. C1's accumulator is zeroed
   so it takes the unflagged path; C2's is all ones so it takes the
   flagged path but already expects flags of 7. Nothing in F210
   distinguishes the flagged branch's flag handling, because the two
   readings agree everywhere the routine looks.
   jb_af1c F210D "TESTS OF INDICATORS" (p.112, 13 rows) closes F210
   out, and D2 is the LOST CARRY oracle recorded as missing since A5.
   D1 clears MOP with BMOPZ and asks with BZMOP that a to-memory
   operation set it; D2 clears LC with BLCZ, runs the same 96-ones
   operand at exponent +2 that A5 uses, and asks with BZLC that the
   rounding overflow set LC. Suppressing MOP halts D1 (016133.40),
   suppressing LC halts D2 (016137.40) -- and under the LC suppression
   F210A5 and F210C both stay GREEN. A5 and D2 are complementary
   halves of one rule: what the overflow did to the stored word, and
   what it did to the indicator.
   F210 IS NOW TRANSCRIBED END TO END, 015775.00 to 016137.40 across
   seven programs, each ending exactly where the next begins.
   SLO (STORE LOW ORDER) IMPLEMENTED, driven by jb_af1c F211 "STORE
   LOW ORDER TEST ROUTINE" -- the second instruction this series has
   written from its own diagnostic. Per Ref. Manual p.97 the stored
   fraction is the accumulator's LOW half (bits 60-107) and the stored
   exponent is the accumulator's MINUS 48; sign and flags go to
   storage bits 60-63; the accumulator is not written. A flagged
   accumulator exponent is kept and normalization suppressed
   (propagated flags); an underflow of the -48 gives a GENERATED flag,
   and p.97 is explicit that normalization then DOES occur, which is
   why the shift precedes fpMakeExp rather than being suppressed by
   it. p.97 lists no LC for SLO, unlike SRD.
   SLO needed its own fpNormalize48. p.97 says "if noisy mode is also
   specified, ONES are entered from the right during the normalization
   shifting", where p.96 says of SRD that "noisy mode does not affect
   this operation" -- and fpNormalize96Wide could not serve, because
   its noisy fill lands in the low 48 bits, exactly the half SLO does
   not have.
   F211A1-A2 (p.113, 21 rows) are the flagged case and drove the
   implementation. F211A3-A4 (20 rows) are the first UNFLAGGED SLO and
   the only exercise of the -48: A3 takes FPK28 at +256 to FPK44 at
   +208, A4 takes FPK38 at +50 to FPK39 at +2, and the listing's own
   comments say "EXP+208" and "EXPONENT++2". Changing the subtraction
   to 47 halts A3 at 016170.00 with A1-A2 green.
   STILL UNEXERCISED in SLO: the normalized path, and with it the
   noisy-mode fill that fpNormalize48 exists for, and the
   generated-flag case where the -48 underflows. Everything so far is
   SLO(U). F211A5 onward (016201.00) is where to look.
   jb_af1c F211A7-A10 (p.114, 28 rows, the "TEST NORMALIZATION
   MODIFIER" section) is the first SLO(N) anywhere and CAUGHT A REAL
   MODEL BUG -- in fpMakeExp, which predates both new instructions.
   A7 and A8 check that a flagged accumulator exponent suppresses the
   shift; A9 is the real normalization, FPK53's fraction having 46
   leading zeros so +50 goes through -48 to +2 and then 46 places left
   to -44 (FK51). A10 drives the exponent to -1073, out of range, and
   expects FK112 -- whose exponent field is -49, and 1073 - 1024 = 49.
   So the machine keeps the LOW TEN BITS of an out-of-range magnitude
   and uses EF only to mark the overflow, where fpMakeExp wrote
   "em = gen ? 10'd0 : truncate(pack(mag))" and stored XFN -0. A10
   halted at 016243.00 with A7-A9 green (A9 normalizes too but stays
   in range), and the fix -- always keeping the low ten bits -- leaves
   the whole suite green, so nothing had been written against the
   wrong behaviour.
   Worth noting how it was found: the arithmetic was pre-computed
   against every expected constant BEFORE the run, which is what made
   the -49 visible as a discrepancy rather than as a mysterious halt.
   That step is cheap and has now paid for itself twice.
   jb_af1c F211B-C (p.114, 20 rows) closes F211. B1 is the SLO
   analogue of F210B -- all three registers set to ones, one SLO(U),
   three questions that none moved -- and has no zero-pattern
   sub-test, which F210B's probing showed never fires anyway. C is
   interesting by OMISSION: its whole indicator test is BMOPZ/BZMOP,
   and there is no LC question anywhere in F211 where F210D2 had one
   for SRD. That matches p.97, which lists no LOST CARRY among SLO's
   indicators because a shift has no carry to lose. The model was
   written that way from the page and the listing agrees by leaving
   the question out.
   F211 is transcribed A1-A4, A7-A10 and B-C; A5-A6 are deliberately
   skipped as more SLO(U) exponent-walking (2-48=-46, then -94), with
   no behaviour A3-A4 does not already cover.
   SHIFT FRACTION MADE 96-BIT, driven by jb_af1c F212 "SHIFT FRACTION
   TEST ROUTINE" (pp.115-121), the block immediately after F211.
   Reference Manual p.102: "Only accumulator bits 12-107 participate
   in the shifting; all other accumulator bits remain unchanged" -- 96
   bits across BOTH accumulator halves. The model's SHF arm shifted
   the 48-bit high half only and wrote back accLeft alone, so a bit
   starting in the low half could neither move nor be lost. F212A12 is
   the row that sees it: Z,$IND clears the indicators, FPK0 goes in
   the high half and FPK34 in the LOW (its fraction is 000000000001,
   one bit at IBM 107), then SHFL(U),107 must leave both halves +0 and
   turn LC ON (BZLC,SERS "ERROR IF LC INDICATOR OFF"). Injecting the
   old behaviour back -- reading the low half as zero -- halts A12 at
   016365.40 (SEN = 016366.00, the instruction after that BZLC) while
   A1-A11 STAYS GREEN. That green is the point, not a disappointment:
   A1-A11 load with DL (which zeroes the low half) and shift LEFT, so
   the low half is zero before and after and they cannot discriminate.
   Shift counts wider than the field are capped before forming "what
   fell off the top" -- A12 shifts left 107, A24 right 107.
   ALSO FIXED, MANUAL-PINNED NOT DIAGNOSTIC-PINNED: the arm used to OR
   ones into the vacated positions under noisy mode. p.102 rules that
   out -- "The operation is not affected by the normalization
   modifier. No noisy mode one bits are entered on left shift if noisy
   mode is specified" -- but every SHF in F212 is (U) and none selects
   noisy mode, so nothing transcribed would have caught it. Recorded
   as a manual reading, not a diagnostic result.
   ENCODING: SHF's amount rides in the address field as amount<<7 and
   its DIRECTION is spelled with the SIGN MODIFIERS, not with address
   bit 11 -- p.102, "the sign of the shift ... is subject to
   modification by the sign modifiers". The listing prints SHFL(U),1
   and SHFR(U),1 with the SAME address (200 octal, direction bit
   CLEAR), differing only in bits 19-20: SHFL/SHFA = A (.67),
   SHFR/SHFNA = A+N (.77), SHFN = N (.57), bare SHF = neither (.47).
   Emitting amount*128+64 for SHFR would have been wrong twice -- the
   address would not match the page, and N would invert a set bit back
   to a LEFT shift, which for a symmetric operand can pass silently.
   strap_asm gained SHFL and SHFR; SHFA/SHFN/SHFNA need no rule, since
   the generic suffix loop strips them to SHF, itself a real FP op.
   The listing's "Z,SIND" is Z,$IND -- STRAP's dollar sign scanned as
   an S -- and $IND is the Appendix A system symbol for word 11.
   F212A IS COMPLETE (A1-A11, A12-A23, A24-A30). A24 is the LC-OFF row
   (SHFR 107 after BLCZ, "ERROR IF LC INDICATOR ON") -- it closes the
   coverage gap noted above for the RIGHT-shift side only; nothing in
   F212A still asks for LC off after a LEFT shift. A26 pins "NORM MOD
   IGNORED" with SHFL(N),1 ("200.27 20", the unnormalized bit CLEAR)
   behaving as SHFL(U),1, which is p.102's "not affected by the
   normalization modifier". A27-A30 run flagged XFP/XFN operands and
   check SIXTY bits at offset 68 rather than 48 -- the exponent
   together with the fraction -- because the question there is that the
   shift leaves the EXPONENT alone.

   TWO REAL I-BOX BUGS, both found by F212A25 and neither reachable by
   anything else in the suite. A25 is SELF-MODIFYING CODE: a CM1111
   writes six ones into the address field of the VERY NEXT instruction
   and then executes it.
     (1) PROGRAM STORE COMPARE DID NOT REWIND THE FETCH STREAM. The
     I-box invalidated a buffered word on a matching store, but
     prefetch only ever issues at `nextFetch` and moves FORWARD, so a
     word at or ahead of the instruction counter was dropped and never
     re-read -- and mkStretchCore's prepare arm simply retries when
     lookup misses. The model livelocked at 016500.00, the modified
     instruction's own address. Fixed by rewinding `nextFetch` to the
     invalidated word, guarded by `sw >= pcw` so a store to a word the
     counter has already passed cannot drag the stream backward.
     (2) THE REWIND THEN BROKE `nextFetch`'s INVARIANT, and the stall
     merely MOVED to 016501.40. `nextFetch` means "the lowest word not
     yet buffered"; after a rewind the word after the invalidated one
     is usually still held by the other Y, and re-requesting it put
     BOTH buffers on the same address. Only strictly-lesser addresses
     are freed by "the counter has passed it", so neither slot ever
     freed, the word after them was never fetched, and the core wedged
     again. Fixed by skipping addresses already held or outstanding
     when advancing `nextFetch`. Diagnosed from a temporary trace of
     the prepare arm (prepared=0 with everything else clear) plus one
     of the Y buffers, not by reading -- the second bug was invisible
     until the first was fixed.
   ORDERING IS CORRECT BY CONSTRUCTION and is a SEPARATE claim from
   those two: a re-fetch cannot read a stale word, because
   StretchStorage issues no read at all while the store queue is
   non-empty (`!busUsed && !issued && !storeQ.notEmpty`), and
   mbcu.canAccept requires the target unit free, so a read cannot
   overtake the store inside its memory unit either.
   A25 CANNOT GUARD EITHER FIX ON ITS OWN, which is why
   programs/store_then_execute.strap was added beside it. A25 patches
   effective-address bits 12-17, which the shift ignores by
   definition, so the stale and the modified instruction are BOTH
   no-op shifts: the row proves the machine does not hang, not that
   the re-fetch saw the new word. The new program has the same shape
   -- a CM1111 into the next instruction's address field -- but sets a
   bit that MATTERS, turning "L(U), SRC0" into "L(U), SRC1" so stale
   and fresh give different answers. store_close_to_fetch.strap
   covered store-then-LOAD; store-then-EXECUTE had no test at all,
   which is why this survived.

   F212B AND F212C DONE. B "TESTS OF SIGN AND MODIFIER COMBINATIONS"
   (p.119) runs the four spellings, all at the same address 200 octal
   with the direction bit CLEAR, so the direction is entirely the
   modifiers' doing: SHFR ".77" A+N right, SHFA ".67" A left, SHFN
   ".57" N right, SHFNA ".77" A+N right. B1 and B4 assemble to the
   IDENTICAL word -- the page prints it twice -- so between them they
   pin the STRAP spellings, not the machine. B3 IS THE ONLY
   DISCRIMINATING ROW: it is the one place N acts WITHOUT A, so it is
   what separates "invert the address bit" from "ignore N unless A is
   present". Injecting exactly that (invert only when absSign is also
   set) halts B3 at its first check -- SEN 016557.40, the BRGZ after
   the high-order question -- while F212A12-A23 STAYS GREEN, because
   every SHFR there carries A and cannot see the difference.
   C "TEST UNCHANGED REGISTERS" (pp.119-120) is the guard on the new
   three-write SHF arm, and it earns that name: fill both accumulator
   halves and the sign byte with ones, SHFL 1, then ask three separate
   questions -- C1 CT1010(BU,12) at offset 116 (IBM 0-11, the
   EXPONENT), C2 CT1010(BU,20) at offset 0 (IBM 108-127, the part of
   the right half OUTSIDE the fraction), C3 CT1100(BU,8) on word 10
   (the sign byte). Injecting the obvious way to break the new arm --
   fpdAccRight(v, 0) instead of fpdAccRight(v, accRs), dropping
   oldRight[19:0] -- halts C2 (SEN 016602.00) while F212B stays green,
   since B never looks at those bits. So the two blocks are not
   redundant: each catches what the other cannot.
   ENCODING NOTE worth keeping: the page prints C's third row as
   "BBZ,8,13,$+1." -- that comma is STRAP's word.bit POINT, scanned
   wrong. It is BBZ,8.13 (word 8, bit 13), which is exactly the 0o10 /
   0o15 pair in the assembled "10.15 80 016573.74 06".

   F212D DONE, AND F212 IS COMPLETE (A, B, C, D). D1 is LOST CARRY in
   three sub-cases, each preceded by a BLCZ clearing LC: ones in both
   halves + SHFL 1; L(U),FK134 + SHFL 1; L(U),FK134 + SHFL 2, closed
   with BZLCZ. D2-D5 cover all four arithmetic result indicators, each
   after a Z,$IND, asking that the right one came on AND the other
   three stayed off: D2 FK55 negative nonzero -> RLZ+RN; D3
   DLN(U),FPK0 a NEGATIVE ZERO -> RN+RZ with RLZ and RGZ off; D4
   positive zero -> RZ; D5 FK21 positive nonzero -> RGZ. D2's SHF(U),3
   (".47 20") is the only shift in all of F212 carrying NEITHER sign
   modifier, so its direction comes from address bit 11 alone.
   D3 IS THE INTERESTING ROW and it is verified by injection: the
   model's setResultIndicatorsFp has RLZ = !zero && negative but RN =
   sign outright, so a negative zero sets RN WITHOUT RLZ. Making RN
   depend on !zero as well halts D3 at its BZRN (SEN 016627.00, the
   check immediately after DLN(U),FPK0) while F212B stays green.

   CORRECTION TO THIS DOCUMENT'S OWN NOTE ABOVE. The "ONE TRAP WAITING
   IN F212D1" paragraph said D1 is where the carried-forward low half
   "starts to matter" and to pre-compute D1 by carrying accRight
   forward. The MECHANISM is real -- L(U) is single-precision, writes
   only the high half and sign byte, and leaves the low half holding
   what the previous shift left (fffffffffffe after D1a) -- but the
   CONCLUSION was wrong: at shift counts of 1 and 2 the bits that
   leave IBM 12 come from the high half alone, and FK134's top
   fraction bit is 1, so D1's LC answers do not depend on the low half
   at all. Computed before running, not discovered by a halt. D1 tests
   LOST CARRY, not the carry-forward; nothing transcribed so far tests
   the carry-forward.

   THE LC COVERAGE GAP PERSISTS ACROSS THE WHOLE ROUTINE, and that is
   now measured rather than inferred from A alone: with lc forced True
   unconditionally on a left shift, F212D and F212A24-A30 BOTH stay
   green. So no row anywhere in F212 requires LC to be OFF after a
   LEFT shift -- A24 is the LC-off row and it shifts RIGHT, and every
   LC question in D1 wants LC ON. Still open, and no longer expected
   to close inside F212.

   NEXT IN THE LISTING: p.122 banners "----F212-X---ADD TO FRACTION
   ROUTINE", so F+ (ADD TO FRACTION, opcode 1010010, not yet
   implemented) is what immediately follows F212, beginning at SAP14
   016651.00 with F212XA1. That settles the question the older
   paragraph above left open by guessing -- F+ is next, and it is a
   MODEL-DRIVING block rather than a pure transcription.
   COVERAGE LIMIT, measured not assumed: NOTHING in A1-A23 requires LC
   to be OFF after a LEFT shift. A12 wants it ON; A24 is the "ERROR IF
   LC INDICATOR ON" row but shifts RIGHT, where the model cannot set
   it at all. Forcing lc = True unconditionally on the left branch
   leaves BOTH blocks green -- so the sh == 0 case (which leans on
   BSV's >> 96 being zero) is currently unguarded by any test. A24 and
   D1 are where that closes. Noted in the arm and in both program
   headers rather than left as an assumption.
   ONE TRAP WAITING IN F212D1, worth writing down before it becomes a
   mysterious halt: now that SHF is 96-bit, THE ACCUMULATOR'S LOW HALF
   IS LIVE STATE ACROSS SUB-TESTS. The single-precision FP arms write
   only addrAccLeft and addrAccSignByte -- fpAccLeft(x, oldLeft)
   preserves IBM 60-63 and nothing touches addrAccRight -- so an L or
   a + leaves whatever the previous instruction put in the low half,
   and a subsequent left shift pulls accRight[63:20] up into the high
   half. This is faithful (D+'s own p.95 text has bits 108-127 remain
   unchanged), and it was invisible while SHF was 48-bit. F212D1 is
   where it starts to matter: it does C1111(BU,64),FPK1,64 and
   C1111(BU,64),FPK1 (both halves all ones), SHFL(U),1, then later
   L(U),FK134 and another SHFL(U),1 -- and that L does NOT clear the
   low half. Pre-compute D1 by carrying accRight forward from
   sub-test to sub-test, not by assuming zero the way A1-A23 could.

   F212-X (ADD TO FRACTION) STARTED, SUB-BLOCK F212XA DONE (pp.122-123,
   016651.00-016740.00, nine sub-tests XA1-XA9). This is the first
   model-driving block since F210: F+ was in opcodes.py and in the
   decoder's valid-op list but not in StretchExecute's `known` set, so
   it set OP INVALID.

   F+ IS D+ WITH ONE SUBSTITUTION, and the substitution has to happen
   at the right moment. Reference Manual p.101: "the exponent of the
   operand in the accumulator is used for both the addressed operand
   and the operand in the accumulator... When the accumulator operand
   is a value in the XFP or XFN range, the fraction addition is not
   performed." Implemented by copying ef/em/es (NOT the flags, which
   stay the addressed operand's, because that is what the TF/UF/VF
   indicators and D+'s flagged-survivor path read) from the
   accumulator onto the storage operand and then calling fpAddDouble
   unchanged. The second sentence then needs no code: equal exponents
   put both operands in the same range, so a flagged accumulator takes
   fpAddDouble's like-flagged branch, which returns `a`.

   ORDER IS THE LOAD-BEARING PART, AND XA4 IS THE ROW THAT PINS IT.
   Six of the nine sub-tests (XA1-XA3 with an XFP accumulator, XA7-XA9
   with XFN) demand the accumulator back untouched, and they pass
   whether the range test happens before or after the substitution.
   XA4 is the discriminator: an N accumulator with an XFP OPERAND,
   where the addition must be performed. Test the ranges first and the
   operand's own XFP exponent sends it down the no-addition path and
   the sub-test fails. Verified by injection, not by reading.

   NEW COVERAGE, MEASURED: F+ IS THE ONLY OP IN THE TREE THAT FORCES
   TWO OPERANDS TO EQUAL EXPONENTS, and that turns out to reach a line
   nothing else did. fpAddDouble's flagged path sets `res` in an
   else-if ladder over the range combinations and then, for LIKE-
   flagged pairs, OVERWRITES it unconditionally with the tie-break
   `res = (fpExp(hb) > fpExp(ha)) ? b : a`. (Unconditionally: the
   second `if` is not a rung of the ladder above it. Reading it as an
   else -- which is easy to do and I did -- makes the tie-break look
   like a no-op at equality, and predicts the opposite of what
   happens.) Because F+ makes the two exponents exactly equal, the
   strict `>` is what returns the ACCUMULATOR; `>=` returns the
   storage operand, whose fraction is {w[51:4], 48'b0}. Injected: XA1
   then compares 555555555555/000000000000 against FK23/FK22 and
   halts at 016654.40, its first BRGZ. Scanning every FP add in every
   program for a like-flagged operand pair finds them in five
   programs and an EQUAL-exponent one in none, so before F212XA
   nothing pinned that comparison at equality.

   THREE INJECTIONS, EACH HALTING ON THE ROW IT SHOULD (SIC's stored
   address decoded from SEN):
     tie-break `>` -> `>=`          016654.40  XA1's high-half check
     drop the exponent substitution 016676.40  XA4's high-half check
     F+ does not report LC          016715.40  XA6's BZLC
   The second is the order test: with the substitution gone, XA4's
   XFP operand keeps its own exponent, the pair goes down the flagged
   path, and the addition that must happen does not.

   A COVERAGE LIMIT, MEASURED FROM THE PRINTED CODE RATHER THAN THE
   MNEMONICS: every F+ in the whole of F212-X is unnormalized. The
   unnorm bit is bits-18 of the FP format, printed as the first octal
   digit of the pair -- .45 for XA1-XA9, XC1 and XC2, .65 for XB1
   (F+A) and .75 for XB2 (F-A, which is F+ with both sign-modifier
   bits). All thirteen have it set, so F+'s NORMALIZED path never
   executes in this routine and will not be closed by finishing XB or
   XC. Alongside the LC-after-a-left-shift gap from F212D.

   XA6 IS THE ONE ARITHMETIC EDGE: 000000000001_ffffffffffff +
   ffffffffffff_000000000000 over the 96-bit fraction carries out of
   IBM bit 12. The listing demands high 000000000000 (FPK67), low
   ffffffffffff (FPK32), the exponent UNCHANGED at +2, and
   "BZLC,SERS -- ERROR IF LC INDICATOR OFF": the carry is dropped, not
   renormalized, and LC records it. All nine expected results were
   computed from the pool constants against the listing's own
   comparison operands before the model ran, and the block passed
   first try.

   TRANSCRIPTION NOTES. (a) XA2's comment reads "-EXP++50" but writes
   FK38 at 022210, whose exponent is +1023; FPK38 at 022053 is the
   +50 constant and XA5 is the row that uses it. The range annotation
   "XFP + N RNGS" is right and FK38 is in the N range, so only the
   "+50" is loose, and it cannot matter: XA2's accumulator is XFP so
   the operand's exponent is discarded either way. (b) On p.123 the
   two connective rows of XA8 print their third field as "30" where
   all 34 other occurrences of the identical instruction print "80";
   read as OCR damage. (c) FPK23 is transcribed with two different
   values in this tree -- ...525250 in three programs, ...525230 in
   fp_compare_f202g.strap -- and the discrepancy is already SETTLED:
   F205B's own note records that 3 and 5 are near-identical in the
   pool's typewriter font and that the block's arithmetic decides it
   (B20/B22 add FPK4 to the magnitude of FPK23 and expect the
   all-ones FPK22, which only "250" gives; the model on the "230"
   reading came out one unit short and halted). Reading p.176 again
   here reproduced "230" in both the source and the assembled-value
   column, which is a good reminder that re-OCRing the same scan is
   not independent evidence. So fp_compare_f202g.strap is the outlier
   and was corrected to ...250; its KR compares pass either way, which
   is why it went unnoticed. XB uses FPK23, hence the check.

   F212XB AND F212XC DONE, AND F212-X IS COMPLETE (XA, XB, XC;
   016651.00-017005.40). XB "SIGN AND MODIFIERS" is two sub-tests that
   address the SAME operand and differ only in the invSign bit: F+A
   forces it positive so the magnitudes subtract, F-A inverts it back
   so they add, and each closes with "BB,10.4,$+2.0 -TEST SIGN BIT 1"
   demanding a negative result either way. F-A is the sixth
   written-minus mnemonic (after M-, M-A, -MG, M-MG, D-, D-MG) and
   strap_asm gained the rule; F+A needed none, the generic "A" suffix
   strips to F+.

   XB CLOSES A GAP XA COULD NOT REACH. Every F212XA row is a plain F+,
   so nothing there separates db.sign = opnd.sign (sign modifiers
   already applied) from the raw storage word's sign bit. Injecting
   the raw bit halts XB at 016746.00 -- XB1's first BRGZ -- and leaves
   XA green.

   XC "TEST UNCHANGED REGS" zeroes $L/$R/$SB, runs an F+, and checks
   that R 44-63 (IBM 108-127) and sign byte bits 0-3 and 5-7 survive;
   then repeats it with everything set to ones. Bit 4 is deliberately
   excluded, being the result sign. Injecting the loss of
   fpdAccRight's oldRight[19:0] halts XC2 at 017001.40, its "DOES
   R44-63 REMAIN+1-S" check; XC1 cannot see it, its low 20 bits being
   zero either way, which is why the block runs both polarities.

   A CLAIM OF MINE THAT THE INJECTION FALSIFIED, recorded because the
   commit message for XB/XC (7579bc6) asserts it and is already
   pushed. I read XC1's "MEM FLAGS+7" comment -- FPK21's flag bits are
   111 against a just-zeroed accumulator -- as the row that catches an
   implementation taking the sign byte's flags from the ADDRESSED
   OPERAND rather than from accS, and said so. It does not. Injecting
   sbWith(accS, sign, r.res.flags) leaves BOTH XC sub-tests green.
   The reason is structural and specific to F+: fpAddDouble's
   unflagged path builds its result with `flags: a.flags` always, and
   on the flagged path F+'s exponent substitution makes the two
   operands like-flagged with equal exponents, so the tie-break
   returns `a`. There is no F+ input for which r.res.flags differs
   from the accumulator's, so the two expressions are equivalent and
   nothing can separate them. For D+ they are NOT equivalent -- its
   flagged path can return the storage operand whole with its own
   flags, which is what F208C2 pinned -- and that remains the only
   cover the sbFlags(accS) choice has. XC1's check is still a real
   test of a MACHINE; it just cannot fail on this model.

   THE UNIFYING MECHANISM, and it is worth stating precisely because
   it has now bitten three times in this one routine: F+ makes the two
   operands identical in exponent, which silently MERGES paths a
   reader expects to be distinct. Everything downstream that
   discriminates on an exponent difference collapses.
     - fpAddDouble's like-flagged tie-break becomes an equality test,
       so the strict `>` -- and only the strict `>` -- returns the
       accumulator.
     - r.res.flags becomes provably a.flags on both paths, so
       sbFlags(accS) and r.res.flags are indistinguishable for F+.
     - r.psh = (adiff > 48) is DEAD for F+: adiff is always 0. So is
       the `adiff > 95` early return. The arm still carries the PSH
       line, deliberately -- keeping it shaped like D+'s is worth more
       than removing dead uniformity -- but nothing can exercise it.
   The two mistakes were not the same mistake, either. One was reading
   an unconditional `if` as an `else`; the other was taking a
   listing comment that names an interesting input ("MEM FLAGS+7") as
   evidence that the input discriminates. Only the injections
   separated them.

   OPEN COVERAGE ON F+, all three of which F212-X cannot close:
   the normalized path (every one of the thirteen F+ rows is %U); LS,
   which IS reachable -- an exact cancellation gives a zero result
   fraction with non-zero operands -- but which no row here produces;
   and PSH, which is not reachable at all, per above.

   F213 (ADD TO EXPONENT) DONE, AND IT FOUND THREE BUGS IN AN
   INSTRUCTION THAT HAD BEEN GREEN FOR MONTHS. E+ was implemented long
   ago as a plain exponent sum and nothing had ever contradicted it.
   A1-A9 (pp.125-126) walk Fig.32's range table exhaustively and A10-A13
   (pp.126-127) the normalization modifier; commit 1e11abd.

     1. No flagged-range table. p.102 defines E+'s flagged behaviour by
        reference to MULTIPLY -- Fig.32, XFP over everything, XFN over
        N, ties to the accumulator. fpMul already had the selector; it
        is now fpExpRangeWinner and both callers share it.
     2. Normalization was 48-bit where p.102 says "the accumulator
        exponent and fraction bits 12-107 are normalized", and the arm
        never wrote addrAccRight at all. Same paragraph, third clause,
        also wrong: a generated EF suppressed normalization for either
        sign, where the rule is "occurs if ES is 0 and is suppressed if
        ES is 1".
     3. fpExp DROPS EF. An exponent that has to be arithmetic across
        the flagged boundary loses 1024.

   BUG 3 WAS UNREACHABLE UNTIL BUG 2 WAS FIXED -- the old guard never
   normalized a flagged value, so the path was dead code. That is the
   second time in two routines that a fix has uncovered a fault beneath
   it (F212's PSH deadness was the other shape of the same thing), and
   it is an argument for re-running the diagnostic after every fix
   rather than batching them.

   fpExp IS DELIBERATELY LEFT WRONG-LOOKING. It returns the ten-bit
   magnitude field, which is what every existing caller wants: a
   comparison between two operands of the SAME range sees the same EF
   on both, so the missing 1024 cancels. fpExpFull adds it and is used
   only where a value must survive the boundary. The two coincide
   exactly when ef == 0, which is WHY L/LWF/E+I are still correct with
   the plain one -- each guards normalization on v.ef == 0. Recorded
   next to fpExpFull, because loosening such a guard without switching
   the function reintroduces A12.

   WHAT THE INJECTIONS MEASURED, and the one place the block is blunt:
     plain exponent sum (the arm as it stood)   halts A1  017017.00
     generated EF always suppresses (old rule)  halts A12 017150.40
     normalize only the high 48                 halts A12 017150.40
   The last two, AND bug 3, all halt at the SAME row with byte-identical
   SEN. A12 carries three distinct faults and cannot separate them;
   what separated them was reading the accumulator, where ACCR came
   back exactly right and ACCL's exponent field was 37 against FK57's
   1061. Worth remembering: a halt address identifies a row, not a
   cause, and when several faults converge on one row the register dump
   is the only thing that distinguishes them.

   Modelling the injected arm over all nine A-rows (fpExp's dropped EF
   included) says A5 is the ONLY sub-test a plain sum satisfies -- it
   is the only one that adds anything -- so eight of nine carry the
   range table. A9 is the narrowest miss, failing by one in em (766
   against 767, since -767-1023 = -1790 and 1790-1024 = 766).

   COVERAGE GAP IN F213A, CLOSED BY THE VERY NEXT BLOCK. No E+ row in
   A1-A13 carries a sign modifier (A1-A9 print ".45 60", A10-A13 ".05
   60"; absSign and invSign zero in both), so nothing there tests "the
   sign modifiers are ignored if either one or both of the exponents
   are in the XFP or XFN range" -- which matters because es is exactly
   what separates XFP from XFN. F213B "TESTS OF SIGN AND MODIFIER
   VARIATIONS" (p.128, from 017163.00) is that test, and its own header
   states the rule the other way round: "THE SIGN MODIFIERS APPLY TO
   THE SIGN OF THE EXPONENTS ONLY". So the gap is a to-do, not a
   permanent hole -- do not cite it as unclosable the way the F+
   normalized-path gap genuinely is. F213B also brings E-, a written-
   minus mnemonic the assembler has not seen (E-%U prints "22020.55
   60", E+ with invSign; E-A%U prints ".75 60"), which will be the
   seventh of that family after M-, -MG, M-MG, D-, D-MG and F-.

   STILL GENUINELY OPEN after F213: E+I, which p.102 makes the same
   operation as E+ but which no transcribed block drives.

   F213B AND F213C DONE, F213 COMPLETE (A, B, C), commit f134a1d. B is
   sixteen sign-and-modifier sub-tests, C the unchanged-registers pair;
   both green on the model first run, suite 156.

   THE GAP FROM d2b730d IS CLOSED, AND MEASURED. F213A could not test
   p.102's "the sign modifiers are ignored if either one or both of the
   exponents are in the XFP or XFN range", because every A row is a
   plain E+. B10 and B11 pair an N accumulator (+256) with FPK48, whose
   -1791 exponent is XFN, and demand -1791 back. Injecting the fault --
   apply the modifiers BEFORE the Fig.32 range test -- halts F213B at
   017221.00, which is B10, and leaves F213A1-A9 green. So the rule the
   E+ arm followed on the manual's authority alone is now pinned by the
   diagnostic.

   THE 2x2 IS NOT AS EXHAUSTIVE AS IT LOOKS, and this is the third time
   in three routines that a suggestive row turned out not to
   discriminate, so it is worth stating as a pattern rather than an
   anecdote. Four B sub-tests address the flagged FPK48 across all four
   modifier combinations, but only two can detect the fault:
     B13  no modifier   es untouched, FPK48 stays XFN      blind
     B16  N+A           A clears es, N sets it again --
                        they CANCEL, FPK48 stays XFN       blind
     B10  A alone       es cleared -> XFP +1791            discriminates
     B11  N alone       es cleared -> XFP +1791            discriminates
   The general shape, seen now at F212XC1 (a substitution had collapsed
   the two flag sources), at F212XA (an unconditional if read as an
   else) and here (two modifiers cancelling): WHEN AN INSTRUCTION
   REWRITES ONE OPERAND FIELD FROM ANOTHER, OR WHEN TWO MODIFIERS TOUCH
   THE SAME BIT, COUNT THE CASES THAT ACTUALLY REACH THE CODE, NOT THE
   CASES THE LISTING ENUMERATES.

   Assembler: E-/E-A -> E+ with N / N+A, the seventh and last of the
   written-minus family (M-, M-A, -MG, M-MG, D-, D-MG, F-, E-).

   F213C checks the sign byte in ONE eight-bit connective where F212XC
   needed two pieces: E+ never writes the sign, so bit 4 need not be
   excluded, and the printed code shows it ("010000.07" against
   F212XC's "004000.07"). Both its sub-tests take the flagged path from
   opposite sides -- C1's zeroed accumulator against an all-ones FPK1
   (XFN memory wins), C2's all-ones accumulator, itself XFN, against
   FPK0 -- which neither comment says.

   Next after F213C: F213D "INDICATOR TESTS" (017265.00), D1-D4 the
   arithmetic result indicators and D5 onward the exponent range ones
   (XPFP/XPO/XPH/XPL/XPU through BB,11.28-11.32, plus ZM at 11.33) --
   the first block to exercise fpRangeBits on E+'s flagged path, which
   the F213A change made set `propagated`. Then D*, LFT and *+, then
   D/ -- which is the one that needs a
   multi-cycle unit, because an unrolled combinational 48-place divide
   is a different proposition from the 48x48 multiplies already in
   fpMul. (This paragraph previously called that "section 1c step 5c's
   E-box refactor" and "the gating item for the rest of double
   precision". Both were wrong, corrected 2026-09-07: step 5c is
   routing STORAGE through request/response methods so mkEBox can be
   synthesized, which the 1c-audit has since withdrawn as unjustified
   and unwanted; what D/ needs is a divide BOX -- Piccolo's
   mkMBox/mkFPU idiom, plan steps 2-3 -- which is a separate and much
   smaller piece of work. And it gates D/ only, not D*, LFT or *+.)
   Its prologue is FSR1 (015772.00) and F210A1 begins at SAP11
   (015775.00): DL(U) FPK26, C0011 FK40+.12 into offset 20, then
   SRD(U) ROS, L(BU) FK35, CT0110(BU,60) ROS,4 -- "error if 1 not
   added in bit pos 60". So unlike everything since F204 this one is
   not a pure transcription: SRD is not implemented yet, and F210 is
   the diagnostic driving it. Still open in double
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

The model was one ~1450-line combinational `execute()` (the whole
E-box) inlined into a single monolithic `StretchCore.step()` rule. It
had to be rewritten to the structure of Bluespec's own RISC-V cores
(Piccolo/Flute): separate pipeline-stage modules, expensive datapath in
multi-cycle "box" sub-modules, off-pipe paths as separate rules.
Reference cores are studied (bsv/README.md item 9). The correctness
oracle throughout is the existing regression suite: every step keeps it
green (behavior unchanged) and is a committed milestone.

**Correction (2026-09-07), from reading Piccolo's own source rather
than describing it from memory.** Earlier revisions of this section and
of README item 9 said the target was "separate pipeline-stage modules
communicating through FIFOs". That is NOT Piccolo's idiom and the
wording was wrong. In `src_Core/CPU/CPU.bsv`, stages hand off through
combinational `.out` bundles and `enq`/`deq` methods inside one
`rl_pipe` rule -- `stage3.enq(stage2.out.data_to_stage3); stage2.deq;`
-- and the only FIFOs are at the edges: `f_reset_reqs`/`f_reset_rsps`,
the GDB `f_run_halt_*`/`f_gpr_*` pairs, and `f_trace_data`. Nothing
between stages. Anyone reading the old wording would have refactored
the model AWAY from the reference. See the audit at the end of this
section.

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
   rules, and the E-box interaction, communicating through registers
   -- the `rl_pipe` + off-pipe-rules shape. **Done** (suite
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
into per-stage RULES, then STAGE MODULES with register hand-off,
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

### 1c-audit. Measured against Piccolo, 2026-09-07

Asked directly: "is the structure still wrong?" Answer: **no, not in the
way README item 9 meant it.** This is a point-by-point measurement, not
a recollection. The eight rows score **5 match, 1 n/a, 2 differ**.

(The first draft ended "with one genuine gap left" and named the
E-box's storage access as that gap; both halves of that were withdrawn
the same day -- see "The gap that isn't one" below. A replacement line
then claimed "seven of eight rows match, and the eighth differs by a
decision that is still deliberate", which is the same overclaim with
the sign flipped, and is also withdrawn: it silently dropped the
`stage body` row. Two rows differ, and only ONE of them is a deliberate
decision. The other -- `execute()` at 1679 lines against Piccolo's
largest stage function at 310 -- is README item 9's "giant
combinational FUNCTION" half, and it is still genuinely open. Nothing
measured on 2026-09-07 touches it: a synthesis boundary was never what
would shorten a 1679-line function, which is exactly why withdrawing
the boundary plan does not close this row.) Piccolo numbers are from
`raw.githubusercontent.com/bluespec/Piccolo/master/src_Core/CPU/`.

| | Piccolo | Stretch today | |
|---|---|---|---|
| `(* synthesize *)` | `mkCPU` only; `mkCPU_Stage1/2/3` have none | `mkStretchCore` only; `mkInstrBuffers`, `mkLookAhead`, `mkEBox` have none | match |
| stage hand-off | combinational `.out` bundles + `enq`/`deq` in `rl_pipe` | combinational method calls + `mkReg`/`mkCReg(2)`/`mkConfigReg` | match |
| FIFOs between stages | **none** | none | match |
| FIFOs at edges | reset, GDB (`f_gpr_*`, `f_run_halt_*`), `f_trace_data` | none yet (no debug/trace edges exist) | n/a |
| stage deps | module arguments (`mkCPU_Stage2(verbosity, csr_regfile, near_mem.dmem)`) | module arguments (`mkEBox #(StretchStorage st, StretchIO io)`) | match |
| rule shape | one `rl_pipe` + off-pipe rules (`rl_trap`, `rl_stage1_interrupt`, FENCE/WFI) | 9 rules: `rl_clock`/`rl_la_fetch`/`rl_ic_controls` + 6 mutually-exclusive decision arms, largest `rl_prepare` 122 lines | match |
| stage body | combinational `fv_out`: Stage1 75 lines, **Stage2 310**, Stage3 41 | `execute()` **1679 lines** (StretchExecute.bsv:412) | **differs, 5.4x** |
| expensive datapath | `mkMBox` and `mkFPU` ARE `(* synthesize *)`, multi-cycle `rg_state` FSMs behind `Server` req/rsp | `fpAddDouble` etc. are plain combinational functions; multi-cycle-ness lives in TIMING as E-box budgets | **differs, by prior decision** |

**What this changes.** The plan and README item 9 both said the target
was "stage modules communicating through FIFOs". Piccolo does not do
that; it hand-offs combinationally and reserves FIFOs for the reset,
debug and trace edges (and for the `Server` faces of its boxes). Both
lines are corrected above. Anyone building to the old wording would have
inserted FIFOs Piccolo does not have.

**The gap that isn't one (corrected 2026-09-07, same day, after
measuring).** An earlier draft of this section called `execute()`'s
direct `st.` calls "the one real gap" and named routing storage through
request/response methods -- so that `mkEBox` could carry its own
`(* synthesize *)` -- as "the concrete, Piccolo-grounded next move, and
the only one." **That was wrong on its own evidence, twice over.**

1. *It contradicts row 1 of the table above.* Piccolo's
   `mkCPU_Stage1/2/3` carry no `(* synthesize *)`; neither does
   `mkEBox`; the row scores that a match. Giving `mkEBox` a synthesis
   boundary would move this model AWAY from the stage idiom, not toward
   it. The modules Piccolo *does* synthesize are `mkMBox` and `mkFPU` --
   multi-cycle `rg_state` FSMs behind `Server` faces -- which is plan
   steps 2-3, deferred on separate measured grounds, not step 5c.
2. *The call count was miscounted.* "74 direct `st.` calls" is the whole
   of `StretchExecute.bsv`, dominated by the `execute()` *function*,
   which takes `StretchStorage st` as a parameter -- and Piccolo does
   exactly the same thing (`mkCPU_Stage2(verbosity, csr_regfile,
   near_mem.dmem)`, whose `fv_out` calls the memory argument directly;
   row "stage deps" scores that a match too). `mkEBox` itself makes
   **four**: `st.readWordReq` x2, `st.responseReady`, `st.readWordResp`.

**And the surviving justification was measured and does not hold.**
README item 9's real argument for splitting is elaboration cost: it
"splits the design across compilation units so no single rule elaborates
everything." Item 9 already records two *disproven* cost hypotheses
(replication; the FP datapath). Measured 2026-09-07 on a clean tree,
this is the third:

| | cost | paid |
|---|---|---|
| all `.bo` compiles + `mkStretchCore` elaboration + testbench | 139s wall / 117s user | once per clean tree |
| `mkStretchCore.cxx` (5.9 MB generated C++) -> `.o` | ~10s | once per clean tree |
| per-testbench elaborate, core cached | **0.73s** | x66 program runs |
| per-testbench link, core `.o` cached | **1.29s** | x66 program runs |

Measured end to end rather than inferred, because the inference was
wrong: `run_tests.sh` on a WARM tree is **228.77s wall (3.81 min)**,
129 sections, zero failures. Its 66 `run_program.sh` invocations account
for ~133s of that (66 x ~2.0s elaborate+link); the balance is Bluesim
runtime plus the ~63 non-`bsc` sections. A COLD tree adds the ~149s
one-time column on top, so a from-scratch suite is ~6.3 min, not 3.5.
The recorded "~3.5 min suite" is the warm figure and is about right for
that; it was never the cold one. (An earlier draft of this paragraph
wrote "~2.5 min one-time against ~2.2 min of per-test work -- which is
where the recorded ~3.5 min comes from". 2.5 + 2.2 = 4.7, not 3.5;
that sentence claimed a re-derivation it had not done, which is the
same species of error as the ones this section exists to correct.)

None of that changes the verdict, and it sharpens it: the one-time
column is ~40% of a cold run and the refactor could shave only part of
its elaboration half. The `(* synthesize *)` boundary on `mkStretchCore`
(item 10) already captured essentially all of the available win: it is
what makes the per-testbench elaboration 0.73s instead of ~120s. A
second boundary at `mkEBox` could shave only a fraction of the
elaboration half of a one-time 2.5 min, in exchange for a structure
further from the reference. **Not worth doing, and not done.**

A measurement trap worth recording: the *first* testbench link after a
clean tree takes 11.7s, because that is when `mkStretchCore.cxx` gets
compiled. Every link after it takes 1.29s and does not rebuild
`mkStretchCore.o`. Timing one link off a fresh tree and multiplying by
66 overstates the suite's link cost by ~9x -- it was very nearly the
number this section was going to be written around.

**What is still genuinely open** is BOTH differing rows, and withdrawing
the boundary plan closes neither.

*`stage body`* -- `execute()` at 1679 lines vs Stage2's 310 -- is
untouched by anything measured here; shortening it is a decomposition
problem, not a synthesis-boundary one. No work is scheduled against it
and none should be until there is a reason beyond the line count.

*`expensive datapath`* -- the multi-cycle boxes. That stays
deferred for FP add/multiply on the 2026-09-04 grounds. It becomes live
the moment `D/` is transcribed, because an unrolled combinational
48-place divide is a different proposition from a 48x48 multiply -- and
the Piccolo-idiomatic answer there is a small divide box (one
`(* synthesize *)` multi-cycle FSM behind a `Server`), NOT a wholesale
E-box refactor. Those two were conflated; they are separate pieces of
work and only the second one is justified.

**Not a gap:** the FBox/MBox item. Piccolo's boxes really are multi-cycle
synthesized FSMs, so the idiom is confirmed -- but the 2026-09-04
reassessment above stands on its own two measured grounds (Stretch
already models FP as multi-cycle via E-box TIMING budgets, and the FP
datapath was disproven as the elaboration cost). Restating, not
reopening.

**Measured after all.** The line that stood here said build and suite
times "were not re-taken for this audit." They have been -- see the
table above. The 2026-09-04 figures hold up: 139s wall for a clean
build of everything (the old "~117s core" is exactly the user-time
figure, 117.40s), and the suite's shape is one-time-heavy, not
per-test-heavy. Nothing added since 2026-09-04 (SRD, SLO, the whole
F209-F211 block) moved the elaboration cost measurably.

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
