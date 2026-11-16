> **STATUS: A SECOND READER'S CHECK of main_boxes_27_62.md**, by an independent
> reading agent on 2026-11-15 from fresh page renders. Still an agent reading:
> re-read in the ink before relying on a quote.

# Second-reader verification of notes_main_boxes_27_62.md (C22-6729)

Method: pages rendered fresh with pdftoppm into scratchpad/v2 (250 dpi tiles for text, 400 dpi
region crops for charts; the scan's native resolution is 400 dpi, 1-bit CCITT, so nothing above 400
adds information). The Read tool shows a whole 250 dpi page scaled to about 200 dpi effective, so "whole page" below
means about 200 dpi; tiles are shown at full 250 dpi.
Order of reading: pp.15-18, 23-27 and 32 were read and (for the charts) transcribed BEFORE the notes were opened.
pp.14, 19-22, 33, 83, 173, 175, 189, 195-196 were read AFTER, with the notes' quotes already seen, so those
confirmations are not blind. The first reader's crops were not used. Nothing was written outside the scratchpad.

## A. Independent chart readings (made before opening the notes)

### p.15 Chart AB (right column)
- Connector `AB 18` (top) -> long line -> Box 27, label `ME`: `EST. LOC. WHERE CODED EXPRES- SIONS FOR THE ADDRESS FIELDS ARE TO BE PUT`
- 27 -> 30A `AN MCP OP`; YES -> 31 (subroutine box `MIOD` / `MAIN'S IOD,ETC. PROCESSING`) -> connector `AC 23`; NO -> 30B
- 30B `A COMMENT`; YES leaves on the LEFT and rejoins the main line below Box 32 (X at the join, above Box 33); NO -> 32
- 32 `SET FIOD SWITCH TO SHOW THAT SUBSEQUENT MCP INSTR. WILL BE OUT OF ORDER` -> 33
- 33 `A PSEUDO-OP`; printed: `NO` on the LEFT exit -> connector `AE 29`; `YES` on the RIGHT exit -> connector `AC 28`.
  (AE 29 enters Box 63 / the pseudo-op branch table on p.18; AC 28 enters Box 34 on p.16. So the ink's YES/NO
  labels are the reverse of what the destinations require. The ink is unambiguous at 400 dpi.)

### p.16 Chart AC
- `AC 28` -> 34 label `MEA`: `LENGTH, IF AVAILABLE, IS PUT IN UNIT. SET PASS 2 SWITCHES`
- 34 -> 35 `INCREASE FIELD COUNT` -> 36A label `MEDAD`, subroutine `GETFLD` / `GET A FIELD ENCODED`
- 36A has two lines to the right: upper to 36B `CPLTSY` / `COMPLETE A SYMBOL` (X at both ends), lower to 36C `CPLTNM` / `COMPLETE A NUMBER` (X at both ends)
- 36A -> 37 `IS THERE ANOTHER STATE- MENT FIELD`; YES -> left, up, rejoins above Box 35 (X at join between 34 and 35); NO -> 38
- 38 label `MEDAF`: `COLLECT REMAINING CHARACTERS THROUGH THE SEMICOLON`; connector `AC 23` enters Box 38 from the left (X at box 38)
- 38 -> 39 label `MEDB`: `EST. LOC. OF FIRST BIT AFTER LAST CODED EXPRESSION`
- 39 -> 40 `DOES THIS INST. HAVE A NAME (FNAME = 1)`; YES -> 41 `FLAG UNIT AS ONE WITH NAME` -> rejoins below 40; NO -> 42
- 42 `COMPUTE LENGTH OF SYMBOLIC STATEMENT` -> 43 subroutine `MOVE` / `PUT SYMBOLIC STATEMENT IN THE UNIT` -> 44 label `MEDC`: `COMPUTE LENGTH OF CODED EXPRESSIONS` -> connector `AD 30`

### p.17 Chart AD
- `AD 30` -> 45 `FIRST INSTRUCTION OF A CARD BLOCK (FBLENA=1)`; YES -> 46; NO -> down to 50
- 46 `DOES INSTRUCTION HAVE A NAME (FNAME=1)`; YES -> 48; NO -> 47. Beside the NO exit is printed `TURN` over `(OFF)` (reads `.NO (OFF)` with `TURN` on the line above)
- 48 label `MEDD`: `TURN OFF FNOSYM, NO-SYMBOL- TABLE-ENTRY INDICATOR` -> 49 `FORM SYMBOL TABLE ENTRY`
- 47 `SET ON FNOSYM, NO-SYMBOL- TABLE-ENTRY INDICATOR`
- Line between 49 and 47: `*X........*` -- the X (arrowhead) is at Box 47's right edge, the plain end at Box 49's left edge. As printed, 49 -> 47.
- 47's left side: line to the left ending in X on the main vertical (45-NO line) -> 50. No arrow from 49 bypasses 47.
- 50 label `MEE`: `LAST INSTRUCTION OF A CARD BLOCK (FBLEND=1)`; YES -> 51A; NO -> 54
- 51A `SYMBOL TABLE ENTRY READY (FNOSYM=0)`; YES -> 52A; NO -> 51B
- 51B `SET ON FNOSYM, NO-SYMBOL- TABLE-ENTRY INDICATOR` -> right (X) onto a vertical that rises to the join above Box 54
- 52A subroutine `ADDORD` / `INSERT SYMBOL TABLE ENTRY IN SYMBOL TABLE` -> 52B `MULTIPLE DEFINED`; YES -> 52C subroutine `MULTI` / `MULTIPLE DEFINED SYMBOL PROCESSING` -> 53; NO -> left, down, rejoins above 53
- 53 subroutine `GNLOAD` / `SAVE FILE OF NAMES OUTSIDE OF CORE` -> right along a line to the same vertical -> join above Box 54
- 54 label `MEF`: `PUT SPECIAL SET OF ERROR FLAGS INTO THE UNIT` -> 57 subroutine `INTOUT` / `SAVE FILE OF UNITS OUTSIDE OF CORE` -> 58 `INCREASE UNIT COUNT` -> 59
- 59 `IS THIS THE END PSEUDO-OP`; YES -> 60; NO -> connector `AA 12`
- 60 subroutine `INTOUT` / `SAVE FILE OF UNITS OUTSIDE OF CORE` -> 61 `ENTER THE $ SYMBOL IN THE SYMBOL TABLE` -> 62 label `ZZXY`: `BETWEEN PASS PROCEDURE` -> terminal `GO TO PASS 2 FLOW CHART`
- There are no boxes numbered 55 or 56 on the chart.

### p.18 Chart AE
- `AE 29` -> 63 label `ME+` (third character prints as a plus sign; not a letter in the ink): `DD`; YES -> 64; NO -> 67
- 64 label `MQDD`: `TYPE OF DD`; `(ALPHABETIC)` down -> 65; `(NUMERIC)` right/down -> 66A
- 65 subroutine `MQDALF` / `MAIN'S ALPHABETIC DD PROCESSING` -> `AC 23`
- 66A subroutine `MQDD` / `MAIN'S DD PROCESSING`; a line leaves 66A's LEFT side and joins (X) the 65 -> AC 23 line; 66A<->66B two verticals (left with X at 66B, right with X at 66A)
- 66B subroutine `MQDNUM` (ink damaged: `MC?NUM`) / `EVALUATE A NUMERIC DD`; 66B<->66C two verticals likewise
- 66C subroutine `DNUM` / `COMPLETE A DD'S NUMERIC FIELD`
- 67 `DIGIT SELECT PSEUDO-OP BRANCH TABLE`; rows, top to bottom:
  1. `PUNFUL,PUNNOR,PUNORG,PRNS,PRND,PRNID` -> AC 23 (the P of PRND prints broken, like `FRND`)
  2. `SKIP,NOPUN,NOPRNT,PRNOR` -> AC 23
  3. `PUNALL,SPNUS,PRNTALL,DUPLI,NOSEQ,RESEQ` -> AC 23
  4. `PUNID` -> box `NPUNID` / `MAIN'S PUNID PROCESSING` (P broken, like `FUNID`) -> AC 23
  5. `TLB,SLC,END,SLCR` -> box `MQL` / `MAIN'S TLB,SLC, END,SLCR PROCESSING` -> AC 23
  6. `EXT` -> box `MX` / `MAIN'S EXT PROCESSING` -> AC 23
  7. `SYN` -> box `MQS` / `MAIN'S SYN PROCESSING` -> AC 23
  8. `DR,DRZ` -> box `MQR` / `MAIN'S DR,DRZ PROCESSING` -> box `MDIMRF` / `MAIN'S DIMENSION PROCESSING` -> AC 23
  9. `PUNSYM` -> box `MQP` / `MAIN'S PUNSYM PROCESSING` -> AC 23
  10. `SEM,REM` -> box `MQ?` / `MAIN'S SEM,REM PROCESSING` -> AC 23 (third letter is a damaged slug; see section C)
  11. `TAIL,UNTAIL` -> box `MQTAIL` / `MAIN'S TAIL, UNTAIL PROCESSING` -> AC 23
  12. `LINK` -> box `MQLINK` / `MAIN'S LINK PROCESSING` -> AC 23
  The table's vertical line continues a few dots below LINK and ends with no further row.

(Addendum to A, p.14 bottom, read at 250 dpi whole page: Box 24 label `MC` `FMODIF = 1` NO, Box 25 `AN EXTRACT OPERATION` YES,
and Box 26 all run into connector `AB 18`. Connector `AA 12` enters Box 2, label `MAIN`, `INITIALIZE FOR NEXT INSTRUCTION`.
Box 3 carries `YES (TURN OFF)`.)

## B. Quote-by-quote verdicts

Verdicts: C = CONFIRMED character for character (line-end hyphens aside, which the notes also drop except where they
mark them); X = CORRECTED; U = UNREADABLE in the ink at that spot. "Notes line" = line in notes_main_boxes_27_62.md.

### p.15 (chart AB) -- 400 dpi crops
| Notes line | Item | Verdict | Remark |
|---|---|---|---|
| 57 | Box 27 text, label ME, from AB 18 | C | |
| 68 | 30A `AN MCP OP`, YES->31, NO->30B | C | |
| 69 | 31 `MIOD` / `MAIN'S IOD,ETC. PROCESSING` -> AC 23 | C | printed with `.` after ETC: `IOD,ETC.` |
| 70 | 30B `A COMMENT`, YES bypasses 32 | C | |
| 71, 79 | 32 `SET FIOD SWITCH ...` | **X** | Ink is `SET F1OD SWITCH`: the second character is the digit one (flag at top left, flat foot), unlike the `I` of `SWITCH`, `INSTR.` and `WILL` in the same box (symmetric serifs) and like the `1` of `31`. The notes flagged it as uncertain; at 400 dpi it is a `1`. The text (p.23 R) has `Fiod`. |
| 83-84 | 33 `A PSEUDO-OP`, NO -> AE 29 (left), YES -> AC 28 (right) | C | Ink unambiguous. |

### p.16 (chart AC) -- 400 dpi crop of 34-37, 250 dpi for the rest
| Notes line | Item | Verdict | Remark |
|---|---|---|---|
| 98 | 34 text, label MEA, from AC 28 | C | |
| 109 | 35 `INCREASE FIELD COUNT`, loop from 37 YES | C | the loop joins the 34->35 line (X at the join) just above Box 35, not the box's side |
| 111-113 | 36A `GETFLD`/`GET A FIELD ENCODED`, 36B `CPLTSY`/`COMPLETE A SYMBOL`, 36C `CPLTNM`/`COMPLETE A NUMBER` | C (texts) / **X** (lines) | "36B and 36C have no exits drawn" is not the whole picture: each connecting line carries an `X` at BOTH ends (`*X....` at 36A and `....X*` at 36B; `*X......X*` 36A-36C), i.e. call and return on the one line. |
| 114 | 37 `IS THERE ANOTHER STATE-MENT FIELD` YES back, NO -> 38 | C | |
| 174 | 38 text, label MEDAF, entered from 37 NO and AC 23 | C | |
| 183 | 39 text, label MEDB | C | |
| 194-195 | 40 `DOES THIS INST. HAVE A NAME (FNAME = 1)`; 41 `FLAG UNIT AS ONE WITH NAME` | C | |
| 209-210 | 42, 43 `MOVE` / `PUT SYMBOLIC STATEMENT IN THE UNIT` | C | |
| 228 | 44 text, label MEDC -> AD 30 | C | |

### p.17 (chart AD) -- 400 dpi crops of 45-49 and 50-58, 250 dpi for the rest
| Notes line | Item | Verdict | Remark |
|---|---|---|---|
| 239 | 45 | C | |
| 240-242 | 46, `TURN` / `(OFF)` beside NO | C | printed `.NO (OFF)` with `TURN` on the line above, to the right of the NO exit |
| 243-245 | 47, 48 (MEDD), 49 | C | |
| 246-251 | 49 -> 47 (X on 47's right edge); 47 -> X on the 45-NO vertical | C | See section C. |
| 252-258 | 50 (MEE), 51A, 51B, 52A, 52B, 52C, 53 and their exits | C | |
| 302 | 54 (MEF), entered from 50 NO, 51B, 53 | C | |
| 320-325 | 57, 58, 59, 60, 61, 62 (ZZXY), terminal | C | |
| 46 | no boxes numbered 28, 29, 55, 56 | C | |

### p.18 (chart AE) -- 400 dpi crops
| Notes line | Item | Verdict | Remark |
|---|---|---|---|
| 44, 351 | Box 63 label "ME+" [uncertain] | C | It is `ME+` in the ink: M, E, and a plus sign. Not uncertain at 400 dpi. Whether the plus is a chart-program artifact cannot be told from the page. |
| 352 | 63 `DD` YES->64, NO->67 `DIGIT SELECT PSEUDO-OP BRANCH TABLE` | C | |
| 357 | row 1 `PUNFUL,PUNNOR,PUNORG,PRNS,PRND,PRNID` | C (normalised) | ink has a broken P: `FRND`; the notes normalise without saying so here |
| 358-359 | rows 2, 3 | C | |
| 360 | `NPUNID` [N/M uncertain] / `MAIN'S PUNID PROCESSING` | C (N is certain) | First letter is `N`: no centre V, unlike the `M` of `MAIN'S` directly below it. `PUNID` in the box prints `FUNID` (broken P), normalised silently. |
| 361-365 | MQL, MX, MQS, MQR -> MDIMRF, MQP | C | `MAIN'S TLB,SLC,` first M and the B print damaged |
| 366 | SEM,REM box `MQM` [third letter uncertain] | U in the ink; see C | |
| 367-368 | MQTAIL, MQLINK | C | |
| 370-371 | trunk "runs off the bottom of p.18" | **X** (description) | The trunk continues about five print rows below the LINK branch and then simply stops, level with the bottom of the last AC 23 connector; it does not reach the paper edge (the folio `18` is below it). No branch label follows. |
| 504-511 | 63-66C: MQDD label, `(ALPHABETIC)`/`(NUMERIC)`, MQDALF, MQDD, 66A-left line into AC 23, paired lines 66A/66B/66C, `DNUM` | C | 66B's name prints `MC?NUM`/`MO?NUM` (damaged); text p.26 R gives MQDNUM. The left line of each pair has its X at the lower box, the right line at the upper box. |

### p.14 (chart AA)
| Notes line | Item | Verdict | Remark |
|---|---|---|---|
| 37, 40 | AA 12 -> Box 2 (MAIN); Box 24 NO, 25 YES, 26 -> AB 18 | C | whole page (~200 dpi) |
| 242 | Box 3 legend `YES (TURN OFF)` | C | whole page |

### p.15 left and middle columns -- whole page only (~200 dpi), not cropped
| Notes line | Item | Verdict | Remark |
|---|---|---|---|
| 38-39 | AB 11 -> 9H (label MAAB); AB 17 -> 7B (label MAABAB) | C | |
| 41 | 9D (label MAABA) `MAKE OTHER MISCELLANEOUS ADJUSTMENTS` -> AC 23 | C | |
| 37, 284-285 | 9F `DID PREVIOUS CARD BLOCK HAVE A NAME` -> 9G `MAKE SYMBOL TABLE ENTRY` -> AA 12 | C | 9F NO also goes to AA 12 |
| 76 | 9C `MAKE A UNIT FOR A 'DRZ(N),1'` | C | |

### p.23 (text)
| Notes line | Quote | Verdict |
|---|---|---|
| 61 | Box 27 paragraph | C |
| 74 | Boxes 30A, 30B, 31, 32 paragraph | C |
| 91 | "See description under Box 67." | C |
| 101 | Box 34 paragraph | C |
| 119 (first two sentences) | Boxes 35-37 ¶1, p.23 R part | C |
| 578 | `Bsymbx` on p.23 L as CPLTSY's index word | C |

### p.24 (text)
| Notes line | Quote | Verdict | Remark |
|---|---|---|---|
| 119 | Boxes 35-37 ¶1 incl. "detec t", "syntatical", "occuring", `Bcfxtx`, `Zifall` ... off | C | `Bcfxtx` re-read at 400 dpi: B-c-f-x-t-x |
| 133 | ¶2 "ambiguous op" | C | |
| 136 | ¶3 dollar sign | C | |
| 139 | ¶4 "(maintained in $6 and $7 respectively during Pass 2)" | C | 400 dpi |
| 153 | ¶5 "the current setting of $6 and $7 respectively" | C | 400 dpi |
| 156-159 | ¶6 and items 1-3 incl. "absoute" | C | |
| 178 | Box 38 paragraph | C | |
| 186 | Box 39 paragraph (to p.25 L) | C | |

### p.25 (text)
| 198 | Boxes 40, 41 | C | no comma after `Zifname`, as the notes have it |
| 215, 218 | Boxes 42, 43 ¶1, ¶2 | C | |
| 231 | Box 44 | C | |
| 263 | Boxes 45-53 ¶1 incl. "can an `MAIN`" | C | |
| 266, 269, 272, 275 | ¶2-¶5 | C | |
| 305 | Box 54 (to p.26 L), circled $ | C | |

### p.26 (text)
| 328 | Boxes 57-61 | C | |
| 331-335 | Box 62 items 1-4 | C | `Fpass1`: the final character is this face's l/1 glyph; `Fpass2` and p.173 settle it |
| 516 | Boxes 63-66C ¶1 incl. "`Ziotpt`. 32", "IQS, A8, and A6", `Gcaz` | C | |
| 519, 522 | ¶2, ¶3 | C | |
| 381 | Box 67 ¶1 (to p.27 L) incl. "con sidered" | C | |

### p.27 (text)
| 384 | Box 67 ¶2 incl. "PRINID" | C | |
| 413, 415 | DUPLI, both paragraphs incl. `Xrepl`, `Xrep2`, `Xsp3`, `ZINPUT` | C | see C for the two glyph questions |
| 422 | PUNID incl. `MPUNID` twice | C | |
| 430 | TLB, SLC, END, SLCR incl. `Hhcom4` | C | |
| 437 | EXT | C | |
| 445 | SYN ¶1 incl. "exits", `Bcfxtx`, `GFLONG` | C | `Bcfxtx` re-read at 400 dpi |
| 448 | SYN ¶2 incl. `MDIMRT`, DECODE not underlined | C | |
| 460 | DR paragraph (to p.32 L) | C | |

### p.32 (text)
| 470 | PUNSYM incl. `NQBTP`, `NPNSYM` | C | |
| 476 | "REM, SEM: For REM and SEM processing ..." | **X** (heading only) | The run-in heading is printed `REM,SEM:` with no space after the comma. Body identical. |
| 482 | TAIL, UNTAIL incl. `MQT` | C | |
| 489 | LINK incl. "-- LVI, 15, $+2 --" and "`Zifbo`, `Zifall`, and `Zifp2`" | C | 400 dpi |
| 7-11 | Pass 1 text ends p.32 R with LINK; "DESCRIPTION ... OF PASS 2" follows | C | |

### pp.19-22 (text)
| 122-128 | p.19 R - p.20 L `Bcfxtx` upper-limit quote | C |
| 571-577 | p.19 R `Ibuffw` quote | C |
| 338 | p.19 R unit counter "initially defined as one ..." | C |
| 311 | p.19 R "mask containing the five error symbol indicators and the suppress-error-message indicator" zeroed | C |
| 278-282 | p.20 L `Fblend`/`Fblena` quote | C |
| 425 | p.20 L-R `Gcaz` quote | C |
| 77 | p.21 L "However, three things must be done ..." | C |
| 283-284 | p.21 R "If this immediately previous card block has a name, `MAIN` makes the entry into the symbol table now" | C |
| 528-529 | p.21 R `Bem`, `Bemt`/`Bemu`/`Bemv`, "This information is picked up later when `MQDD` or `MQDALF` processes the DD." | C |
| 549 | p.22 L `Fmodif` "if-modi-fier-exists", `Modif` once | C |
| 721 | p.22 L "is set up as a -- SIC, $15; BE, 0 -- instruction" | C |
| 166-168 | p.22 R "The first 24 bits in the actual string ..." | C |
| 495-498 | p.22 R $5 quotes | C |
| 439-440 | p.22 R "Since the EXT parameters ..." | C |
| 578 | p.22 R `Bop2x` | C |
| 387 | p.22 L Box 23: the pseudo-op's entry is the source of "the "digit select" numbers assigned to the pseudo-op" | C |
| 586 | p.20 R question blocks, symbols beginning `Qc` | C |

### p.33 (text)
| 144-146 | "The unit counter of the error message routine and $4 and $6 are set to zero. The absolute counter is set to its initial 41.[sub 8] location (0 if in PUNREL mode)." | C |
| 146-148 | "... immediately if $6 is zero, i. e. , if there is no symbolic portion of the location counter." | C |
| 148-149 | "$4 will be set to zero again; and $6 will contain the location of the new STRAP symbolic counter symbol." | C |
| 308 | "the multiply defined with contraditions" | C |

### p.173 (not on my list, checked anyway at 250 dpi)
| 164-165 | Field counter quote | C |
| 203-205 | "a digit from 0-9"; "`Ziname` field of the unit and in the `Zstcnt` field ..." | C -- it is `Zstcnt` (c, n, t) |
| 291-292 | "During Pass 1 `Symbol` always holds the value, `Msyte`, where ..." | C |
| 339-340 | Unit counter "set to one at the start of each pass ... after the use of `INTOUT`" | C |
| 550 | `Fpass1`, `Fuiter`, `Fpass2`, `Fpass3` | C |

### p.175
| 142-144 (400 dpi crop) | $4 "Absolute portion of the location counter."; $6 "Symbolic portion of the location counter (i. e. , current 3 character STRAP II special symbol)."; $7 "Used randomly." | C |
| 537-545 | the other rows as summarised ($0, $2, $3, $5, $6, $10, $11, $13, $14, $15) | C | Not mentioned in the notes: $12 Pass 2 "Used by NAMEIN", $13 Pass 2 "Used by OUTPUT", $14 Pass 2 "Used by NAMEIN". The page's own preamble says "index registers other than $7, $8, and $9 are at the special disposal of specific routines". |

### p.189 (Fig. 20) -- whole page at 250 dpi plus 400 dpi crop of the rotated labels
| 103-105, 161-163, 200-202, 223, 233, 310-311, 343-344, 552-565 | field names, tick labels, legend a-p, captions | C | ZIFNME (not ZIFNAME) confirmed at 400 dpi; ticks `24 25`, `31 32`, `56 58 60`, `63` / `24 26 28 30 32`, `56 57` / `24 25`, `28`, `31 32`, `49 50`, `62 63` / `2425`, `2930` as the notes give them |

### pp.195-196 (Appendix B)
| 390 | title with footnote marks 1, 2 | C |
| 392-397 | Pseudo-Ops list and order, footnote marks (3 on the heading; 4 on "Conditional No Operation" and "Extract"), NOPRINT, "PUNSYN(or PUNSYM)"; General Instructions; MCP Instructions | C | Not mentioned in the notes: p.195 also has "Input-Output Instructions: OP, A7(I) ..." and p.196 lists the I/O mnemonics and "SECONDARY OPERATIONS" (CCR ... SCDSC). |
| 399-402 | footnotes 1-4 | C |
| 391 | "gives no pseudo-op numbers" | C |

## C. Independent readings of the contested items

1. **Box 33 exits (p.15), 400 dpi.** Ink: `NO` left -> `AE 29`; `YES` right -> `AC 28`. AE 29 heads Chart AE (Box 63 DD test, then
   the pseudo-op branch table); AC 28 heads Box 34. The legends are reversed against the destinations. The text gives no
   help ("See description under Box 67"). First reader's reading confirmed; nothing to correct.
2. **Box 49 -> Box 47 (p.17), 400 dpi.** The line between them is printed `*X........*`: the X sits against Box 47's right-hand
   asterisk and the dots run to Box 49's left-hand asterisk. Box 47's left side then has dots running to an X on the
   45-NO vertical. So as drawn: 48 -> 49 -> 47 -> (line to 50). There is no separate line from 49 to the vertical that
   avoids 47. First reader's reading confirmed. (Whether the chart program meant "through 47's row" cannot be told from
   the ink.)
3. **`Bcfxtx` vs `Bcfldx`, p.24 L (Boxes 35-37 ¶1), 400 dpi.** The print is `Bcfxtx`. Same word, same spelling, on p.19 R, p.20 L
   and p.27 R (all read). NEW corroboration from a page the first reader did not read: **p.83 (GETFLD, LINKAGE)** prints
   "Since the index words, `Bcfldx` and `Bcfxtx`, define the buffer area ... a. the value field of `Bcfldx` locates the full
   word address of the buffer and b. the value field of `Bcfxtx` locates the first bit after the buffer." and, under
   **On Exit**, "1. The value field of `Bcfldx` will have been updated accordingly." So the word GETFLD updates on exit is
   `Bcfldx`; p.24's "does not have to reset `Bcfxtx` because `GETFLD` updates this index word" is the ink, and it disagrees
   with p.83. (p.84 Box 1 does say GETFLD rounds `Bcfxtx` down to a full word, which is not an "update" in p.24's sense.)
   The three p.83 lines were re-read from a 400 dpi crop: `Bcfldx` (l, d) and `Bcfxtx` (x, t) are distinct and as quoted.
   p.24's `Bcfxtx` stays the ink; p.83/p.84 are evidence for the caller to weigh, since GETFLD also touches `Bcfxtx` (rounds it down).
4. **"$6 and $7", p.24 L and p.24 R, 400 dpi.** Both print `$6 and $7 respectively`; the characters are a dollar sign and the
   digits 6 and 7, no doubt. p.175 prints $4 = absolute portion, $6 = symbolic portion, $7 = "Used randomly" in Pass 2;
   p.33 L and R use $4 and $6 the same way (three sentences, all confirmed). The contradiction is real and is in the ink.
5. **LINK's `Zifall`, p.32 R, 400 dpi.** Prints "Processing indicators for Pass 2 are turned on in the unit: `Zifbo`, `Zifall`,
   and `Zifp2`." All three underlined. Confirmed as printed.
6. **NPUNID / MPUNID.** Chart p.18 box name: `NPUNID`, N certain at 400 dpi. Text p.27 L: `MPUNID`, twice, M certain. A
   chart/text disagreement in the ink, not a reading doubt.
7. **`Xrepl` / `Xrep1`, p.27 L, 400 dpi.** The last character is the typewriter face's single l/1 glyph, identical to the
   "1" of "0-17" on the next line (which also prints as "0-l7"). The ink cannot distinguish them: UNREADABLE as between l
   and 1; `Xrep2` on the following line makes `Xrep1` the sensible reading.
8. **`ZINPUT`, p.27 L, 400 dpi.** Printed with Z, clearly, underlined; `XINPUT` is printed with X three times in the same
   paragraph. Confirmed as printed.
9. **SEM/REM box name (p.18).** At 400 dpi the third glyph is a damaged slug: narrower than the clean `M` that begins the same
   name, with two stems and a filled middle; it resembles the damaged `N` in `MQLINK` two boxes below. From the chart ink
   alone: UNREADABLE (M or N). NEW corroboration: **p.83** (GETFLD, USER(s)) prints in ordinary type "Subroutines using
   `GETFLD` include: `MQM`, `MDIMRF`, `MDIMRT`, `MIOD`, `MDUP`, `MX`, `MQS`." -- and p.32 L says the SEM-REM subroutine uses
   GETFLD. (400 dpi crop: M, Q, M, the two M's alike.) So the name is `MQM`. (The OCR also has MQM against error messages 110/111 in the message table; OCR locator
   only, not checked in the image.) The same p.83 sentence is a second printed occurrence of `MDUP`, which the notes list
   as "not located".
10. **Box 46 `TURN (OFF)`.** Read as the first reader has it. What is turned off is not printed.
11. **`ME+` (Box 63).** Clear in the ink: `ME+`.
12. **`FIOD` in Box 32.** Ink is `F1OD` with the digit one. Compared at 400 dpi, enlarged 4x, against the `1` of `31` and of
    `(FNAME=1)` (flag at top left, single foot: same glyph) and the `I` of `SWITCH` (bar serifs top and bottom: different glyph).
13. **66B name.** Ink damaged in letters 2-3 (`MC?NUM`); text p.26 R `MQDNUM` twice.
14. **`Zstcnt` (p.173 R).** `Zstcnt` at 250 dpi tile; the fourth letter is c, not e.

## D. Counts and coverage

Unit = one row of the tables in section B (a row may group several boxes or several short quotations).
- Rows: 110. CONFIRMED 105; CORRECTED 4; UNREADABLE in the ink 1.
- The four corrections: (1) p.15 Box 32 ink `SET F1OD SWITCH` (digit one), notes `FIOD`; (2) p.16 the 36A-36B and 36A-36C lines
  each have an X at both ends, notes "no exits drawn"; (3) p.18 the branch-table trunk stops about five rows below LINK, it does
  not run off the page; (4) p.32 heading printed `REM,SEM:`, notes `REM, SEM:`.
- Silent normalisations in the notes (not misreadings): p.18 `FRND` for PRND in row 1, `FUNID` for PUNID in the NPUNID box,
  `MC?NUM` for MQDNUM (this one the notes do flag).
- The one UNREADABLE row is the SEM/REM box name in the chart ink (settled as MQM by p.83). Glyph-level, also undecidable in the
  ink: the last character of `Xrepl`/`Xrep1` (p.27 L), a "C" row because the notes already quote it with that caveat.
- Every exit of every box from 27 to 67 on pp.15-18 was traced and agrees with the notes apart from corrections (2) and (3).
- NOT checked: the Contents (p.3) page numbers and all chart page numbers in section 7; Charts FA-FD pp.28-31 (incl. NPNSYM on
  p.31); the p.38, p.63, p.100, p.102, p.122, p.180, p.183 mentions; Figs. 21-24 pp.190-192; Appendix D p.202; the notes'
  section 8 (host code line references) and section 10 (pass1.md), which are not readings of the Guide.
- Pages rendered and read: 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 32, 33, 173, 175, 189, 195, 196, plus 83
  (three passages at 400 dpi) and 84 (whole page only). Not read closely: p.19 top quarter, and the parts of pp.20-22 that the
  notes do not cite.
