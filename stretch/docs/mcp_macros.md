<!-- PROVENANCE (2026-11-08).  Transcribed from page images of C22-6678-1
by a delegated agent of the Claude session, at 200 dpi with 400-600 dpi
crops; OCR used only to find pages.  Re-checked in the ink by the session
itself: printed p.21 ($FETCH) in full, and Figure 4 (p.47) line by line
at 250 dpi.  The rest has not been independently re-read: treat any
single reading here as one reader's, and re-read the page before relying
on a character.  Used by strap/smac_mcp.py and decks/mcpref_example1.smac.
One correction to the text below: the apostrophe BEGINS A COMMENT in
STRAP II (C28-6129 printed p.2); it is not an end-of-statement mark. -->

# MCP macro-instructions and their calling sequences — IBM 7030 MCP Reference Manual C22-6678-1 (June 1964)

Source: `stretch/docs/C22-6678-1_7030_MCP_Reference_Jun64.pdf`. The printed page number is the PDF page number.
Every character was read from rendered page images (200 dpi, with 400 or 600 dpi crops for small type). The OCR
text was used only to find pages. Where the OCR disagrees with the ink, the ink is recorded here, and a few such
cases are noted.

Conventions in this file:
- `(I)` is the manual's index marker. In the typeface the closing paren and the I touch, so it looks like "(I)" or "(D".
  It is always (I) in the ink. Appendix B uses `(J)` for the second operand.
- **Spacing after commas has been NORMALIZED in §1 and is not a faithful record.** The manual is inconsistent.
  pp.14–21 mostly print "B, $MCP" / ", $OP" with a space. pp.21–28 mostly print "B,$MCP" / ",$COMM", ",$EOJ",
  ",$TIME" and so on with no space, and macros such as "MTIME,A. (I)", "MSIT,A. (I)", "MEDUMP,FWA. (I)",
  "MDUMP,ADDR(I)". I don't think the space carries meaning. Characters, periods and index markers are faithful.
  Only the blank after a comma is not.
- `'` inside a calling sequence is the printed apostrophe (the SMAC/STRAP end-of-statement mark). Text after it on the
  same line is a printed remark.
- `[?]` marks a character I'm not sure of.

## 0. The general rules (printed p.14 and p.15)

p.14, left column:

    MOP, parameter 1, parameter 2, etc.
"MOP represents the STRAP II mnemonic for the requested operation, prefixed by the character M. Any parameters
required, including null parameters, are written in a specified order separated by commas."
"The macro-instructions are expanded to calling sequences by the macro-generator (SMAC), in the general form:"

    B, $MCP
    , $OP
"followed, in consecutive half-words, by the specified parameters."
"If SMAC is not in the compiling chain, pseudo-operations must be specified as calling sequences in the STRAP II form."
"$MCP is a STRAP II system symbol assembled as address 32." (Location 32 is protected, so the branch causes an IF interrupt. The program must be enabled and the IF mask bit must be one.)

p.14, right column (I/O form):

    MOP, IODNAME (I)
    ->
    B, $MCP
    , $OP
    , IODNAME (I)
"I represents any index register, excluding index register zero, ($0)." "IODNAME will be assembled by STRAP II as an
integer, the I/O Reference Number." Worked example:

    MWEF, PPSYMB ($4)
    ->
    B, $MCP
    , $WEF
    , PPSYMB ($4)

p.15 (control-word form):

    MOP, IODNAME (I), CTLWD (I)
    ->
    B, $MCP
    , $OP
    , IODNAME(I)
    , CTLWD(I)
    (return)
"I indicates the use of an index register and not the register itself so that I for IODNAME (I) is any register and I
for CTLWD (I) may be the same or any other register excluding $0."

Appendix A (p.42): "All have DDS of (BU, 24)." So each `,$OP` half-word is a 24-bit binary-unsigned field. The codes
are listed in §3.

Note: from p.15 on, the manual adds a line "(return)" (Appendix B: "(Return)") after the parameters. It marks where
control comes back. It is not a half-word that SMAC generates. Some ops print no (return) line (see the per-op notes).

## 1. Per-pseudo-op transcription (body of the manual, pp.14–28)

Column "Rule" means the op follows p.14 exactly: B,$MCP, then ,$OP, then each macro parameter in order, one per
half-word, with nothing added.

### $WEF — p.14 (worked example; also Appendix B p.45)
See §0. Follows the rule.

### $WAIT — p.17
Macro: `MWAIT, IODNAME (I)`

    B, $MCP
    , $WAIT
    , IODNAME (I)
    (return)
Rule: yes.

### $RET — p.17
Macro: `MRET`

    B, $MCP
    , $RET
Rule: yes, with no parameters. No (return) line is printed. Control goes to "the address in mainstream where the
interrupt occurred", or to the next queued interrupt. "If $RET is used when the auto-stacked mode is not in effect, it
is treated as a no-operation."

### $SIO — pp.17–18
Macro: `MSIO`

    B, $MCP
    , $SIO
    (return)
Rule: yes, with no parameters.

### $RIO — p.18
Macro: `MRIO`

    B, $MCP
    , $RIO
    (return)
Rule: yes.

### $CHEX — p.18
Macro: `MCHEX, IODNAME(I), NEXIT(I)`

    B, $MCP
    , $CHEX
    , IODNAME (I)
    , NEXIT (I)
    (return)
Rule: yes.

### $ATID — p.18
Macro: `MATID, IODNAME(I), NDISP`

    B, $MCP
    , $ATID
    , IODNAME(I)
    , NDISP
    (return)
Rule: yes. NDISP has no index marker. "The NDISP must be specified in a full-word address form". The codes are
NSAVE = 0.0, CSAVE = 1.0, ISAVE = 2.0, SAVE = 3.0, PSAVE = 4.0.

### $FELR — p.18
Macro: `MFELR, FWA. (I)`  (the ink has a period after FWA; the OCR reads "FWA, (I)")

    B, $MCP
    , $FELR
    , FWA. (I)
    (return)
Rule: yes. FWA.(I) is the 18-bit full-word address of a 31-word buffer.

### $STLR — p.19
Macro: `MSTLR, FWA. (I)`

    B, $MCP
    , $STLR
    , FWA. (I)
    (return)
Rule: yes. It may be used only in the auto-stacked mode.

### $IODEF — p.19
Macro: `MIODEF, IODNAME (I), ADDR. (I)`

    B, $MCP
    , $IODEF
    , IODNAME (I)
    , ADDR. (I)
    (return)
Rule: yes. ADDR.(I) is the full-word (18-bit) address that receives the IQS statement "CHXX UNY".

### $FREE — p.19
Macro: `MFREE, IODNAME (I)`

    B, $MCP
    , $FREE
    , IODNAME (I)
    (return)
Rule: yes.

### $SCR (System Card Read) — p.19 (macro and first two lines) and p.20 (rest)
Macro: `MSCR, FWA. (I), N. (I), END`

    B, MCP                                   <- printed WITHOUT the "$" (confirmed at 400 dpi); misprint for B, $MCP
    , $SCR
    , FWA. (I)
    , N. (I)
    , 0.            (described as "M." following)
    B, END'         END RETURN
    (normal return)
Rule: NO. It differs in three ways:
1. A half-word is inserted after the parameters. It is printed as the literal `, 0.`. "The macro-generator reserves a
   half-word for M., which will contain the number of cards that were actually transmitted if there were fewer than
   N. (I) cards remaining."
2. The END parameter is not passed as `, END`. SMAC builds a branch instruction `B, END`: "the end return is given to
   the half-word preceding the normal return, where a branch instruction has been constructed by the macro-generator,
   using the programmer symbol END as the address."
3. There are two returns: the end return (the B,END half-word) and the normal return after it. "If there are at least
   N. (I) cards remaining ... 15N. (I) words are transmitted and the normal return is given."
Order: FWA, N, M, B,END. The macro parameters keep their order, and M. sits between N and END.
The first line printed as "B, MCP" looks like a typo (every other expansion and the Fig. 5 hand-coded $SCR have
B,$MCP).

### $SPR (System Print) — p.20
Macro: `MSPR, FWA. (I), N. (I)`

    B, $MCP          (the ink shows "B,$MCP" with a misformed P that looks like "MCF"; it is $MCP)
    , $SPR
    , FWA. (I)
    , N. (I)
    (return)
Rule: yes. N.(I) is the number of 17-word lines.

### $SPU (System Punch) — p.21
Macro: `MSPU, FWA. (I), N. (I)`

    B,$MCP
    , $SPU
    , FWA. (I)
    , N. (I)
    (return)
Rule: yes.

### $FETCH — p.21
Macro, printed across two lines:

    MFETCH, TTAAAAAA, RELFWA. (I), FWA. (I),
    , N. (I), ERROR, END
(The first line ends with a comma and the second begins with one. This is probably a typographic continuation and not a
null parameter, but the page doesn't say. FWA is followed by a period in the ink (checked at 400 dpi). The OCR reading
"FWA, (I)" is wrong. TTAAAAAA is TT plus six A's: eight characters.)

    B, $MCP
    , $FETCH
    (AX)DD(BU, 48, 6), TTAAAAAAX
    , RELFWA. (I)
    , FWA. (I)
    , N. (I)
    , 0.            (described as "M." following)
    B, ERROR'       Error return
    B, END'         End return
    (normal return)
Rule: NO. It differs in four ways:
1. The first parameter (the 8-character PROSA type-area name) is not a half-word. It becomes a data-definition
   statement `(AX)DD(BU,48,6),TTAAAAAAX`: a 48-bit field of eight 6-bit characters. In the DD line the name is followed
   by an `X` (TT + AAAAAA + X, nine characters, counted at 400 dpi). My reading: `(AX)` declares alphanumeric data
   with `X` as the closing delimiter, the same pattern as `(IQSX)DD(BU),...DOWNX` and `(IQS*)DD(BU),...*` in Fig. 4.
   So X is a terminator, not part of the name. The manual does not say this.
   The manual also does not say how the 48-bit field is aligned against the half-words that follow.
2. A reserved half-word `, 0.` (M.) comes after N. "M. is a half word reserved by the macro-generator for the case
   when $FETCH cannot transmit N. (I) full words or when N. (I) = 0. In either event, M. will then contain the number
   of full words that were actually transmitted."
3. ERROR and END are not passed as parameters. Each becomes a branch: "The error return slot in the calling sequence
   consists of a branch instruction constructed by the macro-generator whose address is that specified by the
   programmer symbol ERROR ... Similarly, the end return slot consists of a branch instruction whose address is the
   programmer symbol END."
4. There are three returns: error, end and normal.
Null/zero: "RELFWA. (I) should be zero if fetching is to begin with the first word of the type-area". "If N. (I) is
zero, fetch will read in all of the specified type-area from RELFWA. (I) to the end of the type-area." "The effective
RELFWA. (I) must be an integer."

### $COMM — pp.21–22
Macro: `MCOMM, FWA. (I), N. (I)`

    B, $MCP
    , $COMM
    , FWA. (I)
    , N. (I)
    (return)
Rule: yes. N.(I) is the number of words, a multiple of full words, at most ten. Usage on p.28: `MCOMM, FWA. (I), 1.`.
Fig. 4 uses `MCOMM,MESG1,3.`.

### $RESLD — p.22
Macro: `MRESLD`

    B, $MCP
    , $RESLD
Rule: yes, with no parameters. No (return) line: control goes to the address on the next section's branch card.

### $EOJ — p.22
Macro: `MEOJ`

    B, $MCP
    , $EOJ
Rule: yes. No return: "under no circumstances will control be returned".

### $ABEOJ — p.22
Macro: `MABEOJ`

    B, $MCP
    , $ABEOJ
Rule: yes. No return line.

### $ABEX — p.23
Macro: `MABEX`   (printed alone, with NO parameter)

    B, $MCP
    , $ABEX
    , FWA. (I)
    (return)
Rule: NO, apparently because of a misprint. The expansion has a parameter half-word `, FWA. (I)` (the 32-word table)
but the macro as printed has no parameter. Probably the macro should read `MABEX, FWA. (I)`. FWA.(I)+31. "must be
set-up by the problem program" (the return address).

### $HOLD — p.23
Macro: `MHOLD`

    B, $MCP
    , $HOLD
Rule: yes. No return line. Continuing is done from the console (Start key = binary key 48, Enter, End).

### $DUMP — p.24
Macro: `MDUMP,ADDR(I)`   (no period after ADDR, no space after the comma)

    B, $MCP
    , $DUMP
    ,ADDR(I)
    (return)
Rule: yes. "ADDR (I) is the (19 bit) address" (no period: a bit address, not a full-word address) "of the first word
in a string of dump requests". The request string printed as an example:

    ADDR      ,A. (I)
              ,B. (I)
              ,FORMAT (I)
              ..........
              ,C. (I)
              ,D. (I)
              NOP, FORMAT (I)
"the requests are terminated by a NOP,FORMAT (I)." FORMAT is 0.0, 0.32, 1., 1.32, 2., 2.32, 15. or 15.32.

### $EDUMP — p.24
Macro: `MEDUMP,FWA. (I)`

    B, $MCP
    , $EDUMP
    , FWA. (I)
    (return)
Rule: yes. "FWA. (I) is the first word (19 bit) address of a string of dump requests similar to that used by $DUMP."
At most six requests. "If there is an error in the calling sequence, the $EDUMP will be ignored".

### $RAM — p.27
Macro: `MRAM`

    B, $MCP
    , $RAM
Rule: yes. No return line: MCP branches enabled to the instruction-counter slot of the PTOE.

### $FIXUP — p.27
Macro: `MFIXUP, A(I), B(I)`

    B, $MCP
    , $FIXUP
    , A(I)
    , B(I)
    (return)
Rule: yes. Zero value: "A(I) may either be zero or may specify the first word (19 bit) address of a table of N + 1
words ... If A(I) is zero, it is ignored". "If the replacement word is all zeros, the standard MCP instruction will be
restored".

### $TIME — p.28
Macro: `MTIME, A. (I)`

    B, $MCP
    , $TIME
    , A. (I)
    (return)
Rule: yes.

### $SIT — p.28
Macro: `MSIT, A. (I)`

    B, $MCP
    , $SIT
    , A. (I)
    (return)
Rule: yes.

## 2. Appendix B, I/O operations (pp.43–46): macro and calling sequence

Every entry here follows the p.14/p.15 rule. Each pair op/opS (S = suppress end of operation, SEOP) shares one entry.
Appendix B writes the second operand as `CTLWD. (J)` / `ARC. (J)`, with a period and J. The body text (p.15) writes it
as `CTLWD (I)`. Per-entry status-bit lists are not transcribed here.

### $RD / $RDS — p.43 (Read)
`MRD or MRDS, IODNAME(I), CTLWD. (J)`

    B, $MCP
    , $RD or $RDS
    , IODNAME(I)
    , CTLWD. (J)
    (Return)
Note: "A maximum of 13 words can be read when IODNAME(I) defines a console."

### $W / $WS — p.43 (Write)
`MW or MWS, IODNAME(I), CTLWD. (J)`

    B, $MCP
    , $W or $WS
    , IODNAME(I)
    , CTLWD. (J)
    (Return)

### $CCW — p.43 (Copy Control Word)
`MCCW, IODNAME(I), CTLWD. (J)`

    B, $MCP
    , $CCW
    , IODNAME(I)
    , CTLWD. (J)
    (Return)

### $REL / $RELS — p.43 (Release)
`MREL or MRELS, IODNAME(I)`

    B, $MCP
    , $REL or $RELS
    , IODNAME(I)
    (Return)

### $LOC / $LOCS — p.43 (Locate Arc)
`MLOC or MLOCS, IODNAME(I), ARC. (J)`

    B, $MCP
    , $LOC or $LOCS
    , IODNAME(I)
    , ARC. (J)
    (Return)

### $FC / $FCS — p.44 (Feed Card)
`MFC or MFCS, IODNAME(I)` -> `B, $MCP` / `, $FC or $FCS` / `, IODNAME(I)` / `(Return)`

### $TIF / $TIFS — p.44 (Tape Indicator Off)
`MTIF or MTIFS, IODNAME(I)` -> `B, $MCP` / `, $TIF or $TIFS` / `, IODNAME(I)` / `(Return)`

### $ERG / $ERGS — p.44 (Erase Long Gap)
`MERG or MERGS, IODNAME(I)` -> `B, $MCP` / `, $ERG or $ERGS` / `, IODNAME(I)` / `(Return)`

### $SP / $SPS — p.44 (Space Record)
`MSP or MSPS, IODNAME(I)` -> `B, $MCP` / `, $SP or $SPS` / `, IODNAME(I)` / `(Return)`

### $BSP / $BSPS — p.44 (Backspace Record)
`MBSPor MBSPS, IODNAME(I)` (printed with no space in "MBSPor") -> `B, $MCP` / `, $BSP or $BSPS` / `, IODNAME(I)` / `(Return)`

### $SPFL — p.44 (Space File)
`MSPFL, IODNAME(I)` -> `B, $MCP` / `, $SPFL` / `, IODNAME(I)` / `(Return)`
(Only the non-S form is shown. $SPFLS appears in Appendix A only.)

### $BSFL — p.44 (Backspace File)
`MBSFL, IODNAME(I)` -> `B, $MCP` / `, $BSFL` / `, IODNAME(I)` / `(Return)`
(Only the non-S form is shown. $BSFLS appears in Appendix A only.)

### $WEF / $WEFS — p.45 (Write Tape Mark)
`MWEF or MWEFS, IODNAME(I)` -> `B, $MCP` / `, $WEF or $WEFS` / `, IODNAME(I)` / `(Return)`

### $REW / $REWS — p.45 (Rewind)
`MREW or MREWS, IODNAME(I)` -> `B, $MCP` / `, $REW or $REWS` / `, IODNAME(I)` / `(Return)`

### $UNLD / $UNLDS — p.45 (Rewind and Unload)
`MUNLD or MUNLDS, IODNAME(I)` -> `B,$MCP` / `,$UNLD or $UNLDS` / `,IODNAME(I)` / `(Return)`

### $RLF / $RLFS — p.45 (Reserve Light Off)
`MRLF or MRLFS, IODNAME(I)` -> `B, $MCP` / `, $RLF or $RLFS` / `, IODNAME(I)` / `(Return)`

### $RLN / $RLNS — p.45 (Reserve Light On)
`MRLN or MRLNS, IODNAME(I)` -> `B, $MCP` / `, $RLN or $RLNS` / `, IODNAME(I)` / `(Return)`

### $KLN / $KLNS — p.45 (Check Light On)
`MKLN or MKLNS, IODNAME(I)` -> `B, $MCP` / `, $KLN or $KLNS` / `, IODNAME(I)` / `(Return)`

### $GONG / $GONGS — p.45 (Sound Gong)
`MGONG or MGONGS, IODNAME(I)` -> `B, $MCP` / `, $GONG or $GONGS` / `, IODNAME(I)` / `(Return)`

### $HD / $HDS — p.45 (High Density)
`MHD or MHDS, IODNAME(I)` -> `B,$MCP` / `,$HD  or  $HDS` / `,IODNAME(I)` / `(Return)`

### $LD / $LDS — p.46 (Low Density)
`MLD or MLDS, IODNAME(I)` -> `B,$MCP` / `,$LD  or  $LDS` / `,IODNAME(I)` / `(Return)`

### $EVEN / $EVENS — p.46 (Even Parity, No ECC)
`MEVEN or MEVENS, IODNAME(I)` -> `B,$MCP` / `,$EVEN  or  $EVENS` / `,IODNAME(I)` / `(Return)`

### $ODD / $ODDS — p.46 (Odd Parity, No ECC; the expansion continues at the top of the right column)
`MODD or MODDS, IODNAME(I)` -> `B,$MCP` / `,$ODD  or  $ODDS` / `,IODNAME(I)` / `(Return)`

### $ECC / $ECCS — p.46 (Error Checking and Correction)
`MECC or MECCS, IODNAME(I)` -> `B,$MCP` / `,$ECC  or  $ECCS` / `,IODNAME(I)` / `(Return)`

### $NOECC / $NOECCS — p.46 (No Error Checking and Correction)
`MNOECC or MNOECCS, IODNAME(I)` -> `B,$MCP` / `,$NOECC  or  $NOECCS` / `,IODNAME(I)` / `(Return)`

## 3. Appendix A (p.42): code list, and which ops have no macro form

"The following list specifies mnemonic and absolute codes for MCP pseudo-operations that are available for use by the
problem program. All have DDS of (BU, 24)."

| op | code | op | code | op | code | op | code |
|---|---|---|---|---|---|---|---|
| $RD | 1.0 | $SPFL | 6.32 | $GONG | 11.0 | $ATID | 17.0 |
| $RDS | 1.01 | $SPFLS | 6.33 | $GONGS | 11.01 | $SIO | 32.0 |
| $W | 1.32 | $BSFL | 7.0 | $WAIT | 11.32 | $RIO | 32.32 |
| $WS | 1.33 | $BSFLS | 7.01 | $CHEX | 12.0 | $RET | 33.0 |
| $CCW | 2.0 | $WEF | 7.32 | $IODEF | 13.0 | $RAM | 33.32 |
| $REL | 2.32 | $WEFS | 7.33 | $HD | 14.0 | $STRG | 34.0 |
| $RELS | 2.33 | $REW | 8.0 | $HDS | 14.01 | $FECRG | 34.32 |
| $LOC | 3.0 | $REWS | 8.01 | $LD | 14.32 | $TIME | 35.0 |
| $LOCS | 3.01 | $UNLD | 8.32 | $LDS | 14.33 | $COMM | 35.32 |
| $FC | 3.32 | $UNLDS | 8.33 | $EVEN | 15.0 | $SIT | 36.0 |
| $FCS | 3.33 | $RLF | 9.0 | $EVENS | 15.01 | $FIXUP | 36.32 |
| $TIF | 4.0 | $RLFS | 9.01 | $ODD | 15.32 | $STLR | 37.0 |
| $TIFS | 4.01 | $RLN | 9.32 | $ODDS | 15.33 | $FELR | 37.32 |
| $ERG | 5.0 | $RLNS | 9.33 | $ECC | 16.0 | $ABEX | 38.0 |
| $ERGS | 5.01 | $KLN | 10.00 | $ECCS | 16.01 | $DUMP | 64.0 |
| $SP | 5.32 | $KLNS | 10.01 | $NOECC | 16.32 | $EDUMP | 64.32 |
| $SPS | 5.33 | $FREE | 10.32 | $NOECCS | 16.33 | $EOJ | 65.0 |
| $BSP | 6.0 | | | | | $HOLD | 65.32 |
| $BSPS | 6.01 | | | | | $RESLD | 66.0 |
| | | | | | | $FETCH | 66.32 |
| | | | | | | $SPU | 67.0 |
| | | | | | | $SPR | 67.32 |
| | | | | | | $ABEOJ | 68.0 |
| | | | | | | $SCR | 68.32 |

(The table is regrouped for width. The manual prints two columns: $RD…$FREE on the left, $GONG…$SCR on the right.
$KLN is printed "10.00", not "10.0". The decimal codes are word.bit addresses.)

77 codes in total. Ops in Appendix A for which the manual gives NO macro form or calling sequence anywhere:
- **$SPFLS** (6.33) and **$BSFLS** (7.01). Appendix B shows only `MSPFL` and `MBSFL`, with no "or ...S" variant.
  The p.22 text says Space File / Backspace File "can only be released by operator intervention".
- **$STRG** (34.0) and **$FECRG** (34.32). They are never described in the text. Their names suggest
  "store registers" and "fetch registers". They are separate from $STLR (37.0) and $FELR (37.32), which are described
  (pp.18–19). Both pairs were checked at 400 dpi: "$STRG", "$FECRG", "$STLR", "$FELR" are all clearly printed.

All other 73 Appendix A ops have a macro and calling sequence, either in the body (pp.14–28) or in Appendix B
(pp.43–46). Fig. 4 also uses `MEND,INIT'`. MEND is not an MCP pseudo-op (it is not in Appendix A); it looks like the
SMAC form of STRAP END (Fig. 5 uses `END,START'`).

Cross-check (not requested, but it bears on the expansions): Fig. 5 (p.48), "Programming Example 2: Card-to-Tape
Routine", is an assembled STRAP listing of calling sequences coded by hand (TYPE,COMPILGO,STRAP, no SMAC). It shows
B,$MCP assembled as `000040.10 00` (address 32.0 = octal 40.0) and each ,$OP half-word as its Appendix A code in octal
with flag field `80`: $SCR = 000104.40 (= 68.32), $WAIT = 000013.40 (= 11.32), $WS = 000001.41 (= 1.33),
$WEFS = 000007.41, $EOJ = 000101.00, $ABEOJ = 000104.00, $RET = 000041.00, $BSPS = 000006.01, $ERGS = 000005.01,
$W = 000001.40, $UNLDS = 000010.41, $IODEF = 000015.00, $COMM = 000043.40. Its hand-coded $SCR is:
`B,$MCP' / ,$SCR' / LVE,,CW+1.0' / ,1.0' / ,0' / B,EOJ'`. That is FWA, N, the reserved M (written `,0`), then a branch
to the END routine, which agrees with p.20. In it, the FWA half-word is written as an `LVE` instruction with address
CW+1.0, not as `,FWA`. I did not transcribe Fig. 5 line by line.

## 4. Appendix C, Figure 4 (p.47): "PROGRAMMING EXAMPLE 1: BUFFERED TAPE INPUT", SMAC source

Columns were measured from a 600 dpi render. The character pitch is about 36.3 px.
- Column 1: class character (B or T on the control cards; blank otherwise).
- Name field: starts in column 2, except `SUEJEAN`, which starts in column 3 (see the note below).
- Statement field: starts in column 10.
- Remarks: start in column 30 (±1), or immediately after the apostrophe when the statement runs into column 29.
- Comment lines: `'` in column 2, text from column 5. Each star line has 49 asterisks (columns 5–53).
Below, the text is placed at those columns in a monospace block. Line 1 of the block is the first line of the figure.

```
         1         2         3         4         5
12345678901234567890123456789012345678901234567890123
B        JOB, ANYID
B        TYPE,COMPILGO,SMAC
T        SUBTYPE,A1
B SUEJEANIOD,TAPE,EXIT,,,ODD,HD
B        REEL,PLB12345
 INIT    LX,$1,BSTRY'        UK RETRY COUNTER
 READ    MRD,SUEJEAN,CW1'
         B,WAIT'
 START   LVI,$2,15.
 '  *************************************************
 '  ANY COMPUTATION TO BE DONE WOULD BE INSERTED HERE
 '  *************************************************
         BZB,EXIT+1.11,WAIT' TEST EE BIT
         MEOJ'               IF ON GIVE EOJ
 WAIT    MWAIT,SUEJEAN'
         BB,EXIT+1.9,EPGK'   TEST FOR EPGK
         BBZ,EXIT+1.10,UKFIX'TEST FOR UK
         R,$1'               RESET COUNTER
         SWAPI,1,CW1,CW2'    SWITCH BUFFERS
         MRD,SUEJEAN,CW1'    INITIATE READ
         B,START'
 UKFIX   BZB,EXIT+1.12,UNITBAD' NOT UK-EOP, UNIT FAILURE
         MBSP,SUEJEAN'       BACKSPACE AND WAIT
         MWAIT,SUEJEAN'
         BB,EXIT+1.9,EPGK'
         BBZ,EXIT+1.10,UNITBAD'
         CB,$1,READ'         TRY READ AGAIN
         MCOMM,MESG1,3.'     QUIT ON THIRD TRY
         MABEOJ'
 UNITBAD MIODEF,SUEJEAN,MESG2+2.0'
         MCOMM,MESG2,4.'
         MABEOJ'
 EPGK    MCOMM,MESG3,5.'
         MABEOJ'
 CW1     CW,BUFFER1,N,0'     CW FOR BUFFER ONE
 CW2     CW,BUFFER2,N,0'     CW FOR BUFFER TWO
 BUFFER1 DR(BU),N'
 BUFFER2 DR(BU),N'
         CNOP'
 MESG 1  (IQS*)DD(BU), DATA ERROR UNCORRECTIBLE*'
         CNOP'
 MESG 2  (IQSX)DD(BU),****OPERATOR****CH UN IS DOWNX'
         CNOP'
 MESG3   (IQS*)DD(BU), THIS PROGRAM HAS BEEN CONTAMINATED.*'
 BSTRY   XW,,3,$'
 EXIT    DR(N),2'            TABLE OF EXITS
         MRET'
         MRET'
         MRET'
         MRET'
 N       SYN,1'
         MEND,INIT'
```
(52 printed lines. The ruler above is mine and is not in the figure.)

Notes and uncertainties for Fig. 4:
- **Letter O / digit 0.** In this listing font they look the same. I chose by context: O in JOB, COMPILGO, IOD, ODD,
  OPERATOR, DOWNX, ERROR, TO, DONE, CONTAMINATED, OF, COUNTER, EOJ, MEOJ, MABEOJ, CNOP, MIODEF, EOP, ONE, TWO;
  zero in `CW,BUFFER1,N,0'`, `CW,BUFFER2,N,0'`, `MESG2+2.0'`. The page itself can't settle these.
- **Digit 1 / letter I / letter l.** I read `$1`, `CW1`, `A1`, `BUFFER1`, `MESG1`, `1.11`, `1.10`, `1.12`, `1.9`,
  `SYN,1`, `SWAPI,1` as the digit 1. The glyph has the flag-and-foot form of a 1, distinct from the serifed I in INIT.
  `SWAPI` ends in the letter I.
- **Letter B / digit 8.** These are also an ambiguity class in this font. I read B in `PLB12345`, `BUFFER1/2`, `BSTRY`,
  `BZB`, `BB`, `BBZ`, `DD(BU)`, `MABEOJ`, `MBSP`, `CB`, judging by the flat left side in the 600 dpi crops and by
  context. None was read as an 8.
- `MBSPor MBSPS` (Appendix B p.44, no space before "or") was read at 200 dpi only.
- **`MESG 1` / `MESG 2`** in the name field have a printed blank in column 6 (M E S G at columns 2–5, digit at column 7).
  The reference in the statement field is `MESG1` / `MESG2`, with no blank. `MESG3` has no blank in either place. I'm
  reporting the print as it stands. Either the blank is ignored in names, or it is a listing artifact.
- **`B SUEJEANIOD,...`**: B in column 1, blank in column 2, SUEJEAN in columns 3–9, IOD from column 10, with no space
  before IOD (measured). Every other name starts in column 2.
- **`*` inside the IQS strings** (`(IQS*)`, `...UNCORRECTIBLE*`, `...CONTAMINATED.*`, `****OPERATOR****`): the printer's
  asterisk, a small star or lozenge. In `(IQS*)` and `(IQSX)` the character after IQS is, by my reading, the
  string-terminator character, which closes the string (`*` and `X` respectively). It is the same character as the
  trailing `*` / `X` before the apostrophe.
- **`.` vs `,`** in `LVI,$2,15.`, `3.'`, `4.'`, `5.'`, `CONTAMINATED.*'`: the listing prints the period as a small
  centered dot. I read all of these as periods. The commas have tails.
- The apostrophes print as small raised marks ("'" / "•"). `BBZ,EXIT+1.10,UKFIX'TEST FOR UK` has no space between the
  apostrophe and the remark, because the statement fills column 29.
- `UK-EOP` uses a hyphen/minus.
- The left-hand `'` on the three comment lines is in column 2. The asterisks and text start in column 5.
- Remark-column positions are ±1 column. The left edges are measured as columns 29.4–30.
