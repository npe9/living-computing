> **STATUS: UNVERIFIED FINDING AID.** Written by a reading agent on 2026-11-15
> from page images. Nothing here may be cited as a source: every quote must be
> re-read in the ink (the page image) before it is relied on, as AGENTS.md
> requires. Passages the agent could not read confidently are listed at the end.
> A second reader (main_boxes_27_62_second_reader.md) checked 110 rows: the four
> corrections it found (F1OD, the 36A lines, the AE trunk, `REM,SEM:`) and the
> MQM settlement are applied below, marked "second reader".

# MAIN (Pass 1), Boxes 27-67: reading notes from C22-6729

Source: `stretch/docs/C22-6729_7030_STRAP_II_Sys_Analysis_Guide.pdf` (PDF page = printed page).

## 0. How these notes were made, and how far to trust them

- **Pages read.** Charts AA-AE are pp.14-18 (AD = p.17, AE = p.18). The Pass 1 text
  ("DESCRIPTION OF THE ACTION INDICATED ON THE FLOW CHART OF PASS 1") starts p.19 col.L and
  **ends p.32 col.R with the LINK paragraph**; pp.28-31 are the Pass 2 charts FA-FD, which
  interrupt it. "DESCRIPTION ... OF PASS 2" starts p.32 col.R. So the MAIN text is pp.19-27 + p.32,
  not pp.19-36.
- **Resolution.** Every quote in sections 2-6 was read from a 200-dpi crop of the page image
  (half a column at a time); the charts from 200-500 dpi crops. Also re-read at 200 dpi, to check the cross-references below:
  p.19 R lower half, p.20 L upper half (`Bcfxtx`), p.21 L Boxes 8-9H (`Bcfldx`, `Fiod`), p.22 R
  upper half ($5, op index), p.33 L lower half and p.33 R ($4, $6), p.175 rows 0-7. The rest of
  pp.14, 19-22 was read only at the Read tool's whole-page resolution and is marked "(whole-page
  read)" where cited. pp.3, 173, 190-192, 195-196, 202 were read at whole-page resolution (p.189
  Fig. 20 also at 220 dpi) and are used only for "where defined".
- **The project already has reading notes for these boxes**: `stretch/docs/strap2/pass1.md`
  (section 2 "Order of processing", section 8 "Gaps and contradictions"). Section 10 below says
  which of my findings are already recorded there and which are new.
- **OCR** (`docs/ocr/C22-6729_*.txt`) was used only to locate pages. Anything known only from OCR is
  marked "(OCR locator only)".
- **Conventions.** Quotes are verbatim, including the print's own slips, marked [sic]. Names the
  print underlines are given in `code`. "L"/"R" = left/right column; "¶n" counts paragraphs under
  the box heading. `[...]` inside a quote is mine.
- **Chart glyphs.** The charts are chain-printer output; O/C/Q/D and M/N/H are often
  indistinguishable ("SEMICCLON", "REMAINING" with a broken N, "MODD"). Ordinary words are transcribed as the
  evident word. Subroutine names and labels that depend on a doubtful glyph are flagged one by one.
- **Not read:** the subroutines' own charts and descriptions (pp.43-134), Figs. 25-27
  (pp.193-194). Their start pages are given in section 7 from the Contents (p.3).

## 1. Chart topology (connectors are NOT box numbers)

| Connector | Lands on | Where it is drawn |
|---|---|---|
| AA 12 | Box 2, label MAIN ("INITIALIZE FOR NEXT INSTRUCTION") | p.14; left from Box 59 NO (p.17) and from 9G/9F (p.15) |
| AB 11 | Box 9H (label MAAB) | p.15 |
| AB 17 | Box 7B (label MAABAB) | p.15 |
| AB 18 | Box 27 (label ME) | p.15; on p.14 (whole-page read) Box 24 NO, Box 25 YES and Box 26 all join into it |
| AC 23 | Box 38 (label MEDAF) | p.16; from 9D, 31 (MIOD), and every Chart AE route |
| AC 28 | Box 34 (label MEA) | p.16, from Box 33 "YES" as printed |
| AD 30 | Box 45 | p.17, from Box 44 |
| AE 29 | Box 63 (label "ME+" [second/third glyphs uncertain]) | p.18, from Box 33 "NO" as printed |

There are **no boxes numbered 28, 29, 55 or 56** on pp.15-18, and 30 exists only as 30A/30B.
Boxes 63-67 are on Chart AE; the pseudo-op subroutine boxes on AE carry **no box numbers**.

Labels printed beside boxes: ME (27), MEA (34), MEDAD (36A), MEDAF (38), MEDB (39), MEDC (44),
MEDD (48), MEE (50), MEF (54), ZZXY (62), MQDD (64) [printed "MODD"-like].

---

## 2. Boxes 27-33 (Chart AB, p.15, right-hand column)

### Box 27 (label ME)
Chart (p.15): `EST. LOC. WHERE CODED EXPRES-SIONS FOR THE ADDRESS FIELDS ARE TO BE PUT`.
Entered from connector AB 18; exits down to 30A.

Text, p.23 R, heading "Box 27" (whole paragraph):
> "The index word, `Bcfldx`, which indicates to `GETFLD` where a coded expression is to be placed is now reset by `Ibuffw`. `GETFLD` will shortly start to encode the address fields which will probably go into the unit. If the coded expression for the address fields are not to go into unit, `Bcfldx` will be changed later appropriately."

Names: `Bcfldx` (GETFLD's "where to put" index word; first seen p.21 L Boxes 9-9H, quoted under
Boxes 30A-32 below), `Ibuffw` (p.19 R Box 2, quoted in section 7), GETFLD (p.83).

### Boxes 30A, 30B, 31, 32
Chart (p.15):
- 30A decision `AN MCP OP`: YES -> Box 31; NO -> 30B.
- 31 subroutine box `MIOD` / `MAIN'S IOD,ETC. PROCESSING` -> connector **AC 23** (= Box 38).
- 30B decision `A COMMENT`: YES -> bypasses Box 32, rejoining just above Box 33; NO -> 32.
- 32 `SET F1OD SWITCH TO SHOW THAT SUBSEQUENT MCP INSTR. WILL BE OUT OF ORDER` -> 33.

Text, p.23 R, heading "Boxes 30A, 30B, 31, 32" (whole paragraph):
> "Tests are made for a master control program op or a pseudo-op now because the processing of the address fields of each is handled by specialized subroutines. If it is not a master control op and not a comment, then the `Fiod` switch is set so any subsequent master control op will receive an error message because any later MCP instruction will be out of order. (MCP instructions that are out of order will be printed on the listing, but not punched.) Therefore, comments excepted, the initial instructions of the program being assembled by STRAP II must be master control ops if all the master control ops specified in the program being assembled are to be punched. `MIOD` handles the MCP ops, REEL and IOD, during Pass 1."

Related, p.21 L, heading "Boxes 9-9H" (200 dpi), for the `;` that becomes DRZ(N),1:
> "However, three things must be done before the transfer to box 38: First, $5 is set up with the location of the appropriate op index. Second, since the usual encoding of `GETFLD` will not take place for this DR, index word `Bcfldx` must be adjusted so that later redefinition of `Ibuffw` by `Bcfldx` will be correct. Third, `Fiod` is turned on to indicate a non-MCP instruction has occurred."

Names: `Fiod` (p.21 L, p.23 R; chart spells it "F1OD", digit one, per the second reader at 400 dpi [first reading: the I could be a 1: "F1OD"/"FIOD",
glyph uncertain]), MIOD (chart p.96 OCR locator; text p.97).

### Box 33
Chart (p.15): decision `A PSEUDO-OP`. **As printed: the exit marked NO goes left-down to
connector AE 29; the exit marked YES goes right-down to connector AC 28.**
AE 29 is the head of Chart AE (the DD test and the pseudo-op branch table); AC 28 is Box 34 (MEA),
the ordinary-instruction path. So the YES/NO legends look **reversed on the chart** against the
sense of the question. Recorded as printed; the text (Box 67, below) says pseudo-ops are
dispatched by the digit-select table, which is on AE.

Text, p.23 R: heading "Box 33", then one line:
> "See description under Box 67."

---

## 3. Boxes 34-39 (Chart AC, p.16)

### Box 34 (label MEA)
Chart: `LENGTH, IF AVAILABLE, IS PUT IN UNIT. SET PASS 2 SWITCHES`. Entered from AC 28.

Text, p.23 R, heading "Box 34" (whole paragraph):
> "The length of the binary output of a non-ambiguous binary producing instruction (DD and DR are handled separately) is put in the unit. Also the indicators frequently referenced in Pass 2 can be turned on now, `Zifbo` on because the unit has binary output; and `Zifp2` on because the unit will contain coded expressions which must be decoded in Pass 2. Note both these indicators are in the format part of the unit."

Names: `Zifbo` = Fig. 20 ZIFBO, bit 59 of fixed word 1, legend "e. binary output";
`Zifp2` = ZIFP2, bit 58, legend "d. DECODE gets unit"; the length field is ZILBO, bits 25-31
"Length of Binary Output" (all p.189).

### Boxes 35-37
Chart:
- 35 (hexagon-like "modify" box) `INCREASE FIELD COUNT`. Entered from 34 and, from the left, by
  the loop back from Box 37 YES.
- 36A (label MEDAD) subroutine box `GETFLD` / `GET A FIELD ENCODED`, with two lines to the right:
  to 36B `CPLTSY` / `COMPLETE A SYMBOL` and to 36C `CPLTNM` / `COMPLETE A NUMBER`
  (GETFLD's own subroutines; second reader: each line 36A-36B and 36A-36C has an X at both ends, call and return on the one line, not "no exits drawn").
- 37 decision `IS THERE ANOTHER STATE-MENT FIELD`: YES -> back to 35; NO -> 38.

Text, p.23 R bottom to p.24 L, heading "Boxes 35-37":

¶1 (p.23 R -> p.24 L):
> "The get-a-field subroutine, `GETFLD`, is now called upon to encode in the unit each of the allowed address fields in this op. `GETFLD` performs a legality test to detec t [sic] syntatical [sic] errors in a field. If the datums in a field are combined in an illegal manner, `GETFLD` encodes a null coded expression which later will be evaluated as zero for the field. Since `GETFLD` encodes only one field per request, `MAIN` sets up a counter of the maximum number of times it should go to `GETFLD`. The initial contents of this counter is determined by the first of this op's fill index words which is located by the value field of the op index word. For each address field encountered, `MAIN` increments the field counter which is used by the error message subroutines to identify the field of an occuring [sic] error. Also a field counter in the format part of the unit is updated for each field encoded so `DECODE` will know how many times to go to `VALUE` to get a coded expression encoded during Pass 2. On each re-entry into `GETFLD` through this loop, `MAIN` does not have to reset `Bcfxtx` because `GETFLD` updates this index word. `MAIN` turns the `Zifall` indicator off so Pass 2a will know that there are coded expressions in this unit to be evaluated."

  NOTE: the print has **`Bcfxtx`** here (p.24 L), clearly, not `Bcfldx`. p.19 R - p.20 L (200 dpi)
  makes `Bcfxtx` GETFLD's *upper limit* index word: "The upper limit of the buffer reserved for the
  units is put in `GETFLD`'s index word, `Bcfxtx`, since this is one of the index words that have to
  be set up for using the encoding subroutine. ... Since `GETFLD` will probably put more than one
  coded expression into the unit for this instruction, the upper boundary is set this one time to
  include all the uses of `GETFLD` for this purpose. `Bcfxtx` has to be reset for each instruction
  because `GETFLD` can be asked to put coded expression(s) in places other than in the unit (e. g. :
  in variable length entry portion of the symbol table for a SYN)." `Bcfldx` (pp.21, 23, 24) is the
  *where-to-put* word. Which one GETFLD "updates" is therefore not settled by this sentence;
  Box 39 (below) says GETFLD loads the unit "under the control of the index word `Bcfldx`".

¶2 (p.24 L):
> "If `GETFLD` is called upon to encode more than one statement field for an "ambiguous op" then the "ambiguous op" must be of the vfl type and `MAIN` changes the unit, etc. , accordingly."

¶3 (p.24 L):
> "Whenever `GETFLD` encounters a dollar sign chara-cter in an address field followed by a semicolon, comma, plus, minus, asterisk, or slash character, `GETFLD` forms a coded expression which contains at least the two datums to represent the dollar sign character. One datum is a symbolic datum containing the $ symbol itself represented internally by the STRAP II special symbol $00. The 24 bits occupied by the $00 configuration now, will later contain the contents of the symbolic portion, if any, of the associated location counter value. The second datum is an absolute datum presently containing 24 bits of all zeros but eventually holding the absolute portion of the location counter value. The operator to be later used with these two datums during the decoding is set up as a "L and plus" operation, so that the two datums will be combined to give the bit value of the $ setting, i. e. , the present setting of the location counter value when the value of the field is established by `VALUE`."

¶4 (p.24 L):
> "For such cases, `MAIN` enters the $ symbol into the symbol table after all the units have been processed in Pass 1. The symbol entry will be for the symbol $00, with the function portion of the variable length entry part of the entry containing a SYN-like coded expression made up of two datums, one for the symbolic portion and one for the absolute portion of the current Pass 2 setting of the running location counter value (maintained in $6 and $7 respectively during Pass 2)."

  NOTE: "$6 and $7 respectively" is what p.24 L prints (and again p.24 R ¶5). The Index Register
  Assignment table on p.175 (200 dpi) gives, for Pass 2, **$4** "Absolute portion of the location
  counter.", **$6** "Symbolic portion of the location counter (i. e. , current 3 character STRAP II
  special symbol).", and $7 "Used randomly." p.33 L (200 dpi, Pass 2 Boxes 3, 4): "The unit counter
  of the error message routine and $4 and $6 are set to zero. The absolute counter is set to its
  initial 41.[subscript 8] location (0 if in PUNREL mode)." p.33 R (Boxes 12A, 12B): "the counter
  can be rounded, if necessary, immediately if $6 is zero, i. e. , if there is no symbolic portion
  of the location counter." and "$4 will be set to zero again; and $6 will contain the location of
  the new STRAP symbolic counter symbol." So p.24's "$6 and $7" (symbolic, absolute) disagrees
  with pp.33 and 175 ($6 symbolic, $4 absolute). Not resolved here.

¶5 (p.24 R top):
> "During Pass 2 in the initial processing of each unit, Pass 2 OR's into the fields (reserved for the symbolic and absolute portions of the location counter in the function portion of the $00's variable length entry) the current setting of $6 and $7 respectively."

¶6 (p.24 R):
> "Thus, later whenever `VALUE` is called upon by `DECODE` to establish the value of a coded expression in the unit and `VALUE` encounters the symbolic datum $00, `VALUE` recognizes the $ situation and does the following:
> 1. `VALUE` looks up the $00 in the symbol table to obtain the current absolute and symbolic values to be associated with this $.
> 2. `VALUE` inserts these values into the corresponding absoute [sic] and symbolic datums of the coded expression in this unit.
> 3. If there is no symbolic portion in the current contents of the $00 symbol table entry, `VALUE` changes the symbolic field in the unit's coded expression from $00 to all zeros. Later if `VALUE` has to look at this coded expression again, `VALUE` makes a special check for a symbolic datum of all zeroes, so that `VALUE` will ignore this type of symbolic datum rather than looking it up in the symbol table."

Names: GETFLD (p.83), CPLTSY (p.74), CPLTNM (p.71), DECODE (p.140), VALUE (p.55), `Zifall`
(= ZIFALL, bit 25 of fixed word 3, legend "n. nothing left for DECODE", p.189), the unit's
field counter (= ZINFLD, bits 32-49 "Number of Fields", p.189), the error-message Field counter
(p.173 R item 2: "set to zero at the start of processing each unit and is increased by one as each
address field is processed", whole-page read), "fill index words" / "op index word" (p.22 R, 200
dpi: "The first 24 bits in the actual string contains the address of the first control word in the
chain of control words which are used in Pass 2 to insert the address fields into the binary output
saved in the fixed format part of this op's unit."; Appendix A p.192 Fig. 23; Appendix D p.202 "TOPA Operation fill control words for
INSERT").
No sentence on these pages says what MAIN does when the counter of permitted GETFLD calls runs out
and a comma still follows.

### Box 38 (label MEDAF)
Chart: `COLLECT REMAINING CHARACTERS THROUGH THE SEMICOLON`. Entered from Box 37 NO and from
connector AC 23.

Text, p.24 R, heading "Box 38" (whole paragraph):
> "After `MAIN` has processed all the characters contributing to the instruction itself, the comment character (or any characters of the instruction that are to be treated as a comment) must now be processed. Their only processing consists of having them included in the symbolic statement buffer being built up by `GETCHA`. `MAIN` accomplishes this by relooping into `GETCHA` until `GETCHA` gives `MAIN` a semicolon in the value field of $3. This semicolon may be either one picked up from the card image or the "false" semicolon indicating an end of card block. Later the symbolic statement buffer, i. e. , the picture of the statement field of the card image, is transmitted into the unit."

Names: GETCHA (p.79), $3 (p.20 L Box 5; p.175: Pass 1 "A8 character from GETCHA").

### Box 39 (label MEDB)
Chart: `EST. LOC. OF FIRST BIT AFTER LAST CODED EXPRESSION`.

Text, p.24 R -> p.25 L, heading "Box 39" (whole paragraph):
> "Using `GETFLD`'s index word, `Bcfldx`, `MAIN` updates `Ibuffw` to address the first bit after the coded expressions with which `GETFLD` has been loading the unit under the control of the index word `Bcfldx`. Note `GETFLD` does not update `Ibuffw`; the user program must do this. Just as `Ibuffw` was used to locate the initially available area in the unit for the coded expression, so `Ibuffw` must be updated to locate available area in the unit for the symbolic statement."

---

## 4. Boxes 40-54 (Charts AC p.16 and AD p.17): name, statement image, symbol entry

### Boxes 40, 41
Chart (p.16):
- 40 decision `DOES THIS INST. HAVE A NAME (FNAME = 1)`: YES -> 41; NO -> 42.
- 41 `FLAG UNIT AS ONE WITH NAME` -> 42.

Text, p.25 L, heading "Boxes 40, 41" (whole paragraph):
> "At this point if this is the first unit of a card block and has a name, the if-a-name indicator, `Zifname` is turned on and the name check digit is stored in the unit. The name check digit is one of the built-in checking features in STRAP. The check digit is carried in the symbol table entry and also in the name field entry. The synchronous matching of these files in Pass 2 is cross-checked by the use of the check digit. Note the DDI and SYN instructions, when used, must each have a name."

Names: FNAME (chart only: pp.15, 16, 17; p.122 "Fname" OCR locator only). `Zifname` is the text's
spelling; **Fig. 20 (p.189) labels the bit ZIFNME** (bit 57 of fixed word 1, legend
"c. name"). Name check digit = ZINAME, bits 28-31 of fixed word 3 (p.189). p.173 L/R
(whole-page read) says the digit is "from 0-9" and is carried "in the `Ziname` field of the unit and
in the `Zstcnt` field of the function portion of the variable length entry part of the symbol table
entry" [`Zstcnt` spelling uncertain at that resolution: "Zstcnt"/"Zstent"]. Note the chart tests
only FNAME; the text adds "the first unit of a card block".

### Boxes 42, 43
Chart: 42 `COMPUTE LENGTH OF SYMBOLIC STATEMENT`; 43 subroutine box `MOVE` /
`PUT SYMBOLIC STATEMENT IN THE UNIT`.

Text, p.25 L, heading "Boxes 42, 43":

¶1:
> "The length (count of 8-bit characters) of the symbolic statement which `GETCHA` has built up with each of the statement field characters in this operation is now computed and saved in the format part of the unit so `OUTPUT` in Pass 2b will know the length of the statement field to be printed on the listing."

¶2:
> "The index word, `Ibuffw`, is rounded to a full word location so that the symbolic statement will go into the unit at a full word location, except for a comment card block and a B-type card block, the symbolic statement will not necessarily be a true image of the statement field of the op. The blanks following the last non-blank character in the statement field do not go into the statement buffer. Furthermore, `MAIN` adjusts the symbolic statement to eliminate the semicolon from the print image stored in the unit. After the symbolic statement has been moved into the unit, `Ibuffw` is updated to address available area for the next unit since no more data will go into the current unit."

  (The first sentence is a run-on as printed; "except for a comment card block and a B-type card
  block" may belong to either half.)

Names: ZILSST "Length of Symbolic Statement", bits 32-56 of fixed word 2 (p.189);
MOVE (p.41); OUTPUT (p.157); the statement buffer and its index word `Bsystx` (p.19 R, whole-page
read).

### Box 44 (label MEDC)
Chart: `COMPUTE LENGTH OF CODED EXPRESSIONS` -> connector AD 30.

Text, p.25 L, heading "Box 44" (whole paragraph):
> "The bit length of the encoded fields in the unit is also computed and saved in the unit so `OUTPUT` in Pass 2 will be able to locate the statement field characters in the unit. (In Pass 2, Location of unit in the value field of $3 + size of fixed format + bit length of encoded fields = location of statement field characters.)"

Names: ZILCFD "Length of Coded Fields", bits 0-24 of fixed word 2 (p.189). Note the
formula adds the bit length directly although ¶2 of Boxes 42-43 says the statement starts at a full
word; nothing here says the saved length is rounded.

### Boxes 45-53 (Chart AD, p.17)
Chart, as printed:
- 45 decision `FIRST INSTRUCTION OF A CARD BLOCK (FBLENA=1)`: YES -> 46; NO -> down to 50.
- 46 decision `DOES INSTRUCTION HAVE A NAME (FNAME=1)`: YES -> 48; NO -> 47. Beside the NO exit is
  printed `TURN` / `(OFF)` (i.e. "NO (TURN OFF)", the same form of legend Box 3 carries on its YES
  exit on p.14). **What is turned off is not said. Unresolved.**
- 47 `SET ON FNOSYM, NO-SYMBOL-TABLE-ENTRY INDICATOR`.
- 48 (label MEDD) `TURN OFF FNOSYM, NO-SYMBOL-TABLE-ENTRY INDICATOR` -> 49.
- 49 `FORM SYMBOL TABLE ENTRY`.
- **Lines out of 47 and 49 as drawn:** a dotted line leaves the left edge of 49 and ends in an
  arrow-head `X` **on the right edge of 47**; a second line leaves the left edge of 47 and ends in an
  `X` on the vertical line from 45 NO down to 50. Read literally that is 49 -> 47 -> 50, which would
  set FNOSYM on again right after 48 turned it off and make 51A always NO. It is more likely the
  chart program routing 49's exit to the 45-50 line across Box 47's row. **Recorded as drawn;
  flagged; not resolved by the text.**
- 50 (label MEE) decision `LAST INSTRUCTION OF A CARD BLOCK (FBLEND=1)`: YES -> 51A; NO -> 54.
- 51A decision `SYMBOL TABLE ENTRY READY (FNOSYM=0)`: YES -> 52A; NO -> 51B.
- 51B `SET ON FNOSYM, NO-SYMBOL-TABLE-ENTRY INDICATOR` -> joins the line into 54.
- 52A subroutine box `ADDORD` / `INSERT SYMBOL TABLE ENTRY IN SYMBOL TABLE` -> 52B.
- 52B decision `MULTIPLE DEFINED`: YES -> 52C; NO -> bypass to 53.
- 52C subroutine box `MULTI` / `MULTIPLE DEFINED SYMBOL PROCESSING` -> 53.
- 53 subroutine box `GNLOAD` / `SAVE FILE OF NAMES OUTSIDE OF CORE` -> joins the line into 54.

Text, p.25 L bottom -> p.25 R, heading "Boxes 45-53":

¶1 (p.25 L -> R):
> "Now if the unit is the first unit of the card block and if it has a name, a symbol table entry must be set up. Furthermore, if this is the end of a named card block (only at the end of a card block can an [sic] `MAIN` be sure that the entire name has been collected), `MAIN` makes an entry into the symbol table which remains in memory throughout the assembly. If the symbol collected from the name field of the card block is in the sphere of influence of a previous TAIL pseudo op still in effect, a NOP/Branch instruction before the calling sequence to `ADDORD` will be a Branch as set previously by `MQTAIL`. The internal STRAP II characters indicating the tails in effect will be appended to the symbol before `ADDORD` inserts the entire entry in the symbol table. `GETCHA` makes the entry in the name file which does not remain in memory and is only recalled into memory to be printed on the listing in Pass 2b."

¶2 (p.25 R):
> "At this time certain information in the unit must also be included in the set up symbol table entry for a symbol referencing done by Pass 2 in establishing the final value. Some of the data to be moved to the symbol table entry are: length of binary output, coded expressions for a P-mode data description on a still "ambiguous" op, explicit data description information of a DD or the coded expression for its symbolic data description, and coded expression for a dimension of a DR. (See Appendix A.)"

¶3 (p.25 R):
> "Note the set up symbol table entry for a SYN or a MCP op has already been made in their respective pseudo-op subroutines."

¶4 (p.25 R):
> "A special (or "phoney") symbol table entry is set up for a pseudo op which should not have a name but yet does have one. A named pseudo op which should not have a name is not guaranteed to have a full or half word address when referenced."

¶5 (p.25 R):
> "If `ADDORD` of table management informs `MAIN` that the entry just requested to be put in the symbol table is multiply-defined, `MAIN` has the subroutine `MULTI` adjust the symbol table entry of the multiply-defined symbol."

Related earlier text (whole-page reads, not re-read at 200 dpi): p.20 L "Boxes 3, 4" defines
`Fblend` ("if-block-end indicator"; the "false" semicolon) and `Fblena` (eligible for a name), and
says "During the final processing of a unit in Pass 1, if `Fblena` is on, then the symbol table
entry, if any, can be prepared and set up; if `Fblend` is on, then the name and the symbol (name
without blanks for internal processing) associated with the card block can be entered into each of
its respective files." p.21 R (Boxes 9-9H table): for the false semicolon after an unnecessary real
one, "If this immediately previous card block has a name, `MAIN` makes the entry into the symbol
table now ..." (chart p.15: 9F "DID PREVIOUS CARD BLOCK HAVE A NAME" -> 9G "MAKE SYMBOL TABLE
ENTRY").

Names and where defined:
- FBLENA, FBLEND: p.20 L (Boxes 3, 4). FNAME: chart only. **FNOSYM: chart p.17 only; no sentence of
  pp.19-27/32 names it.**
- The intermediate entry area: `Msyte` (named on p.27 R under SYN, and p.173 R: "During Pass 1
  `Symbol` always holds the value, `Msyte`, where the variable length entry part of the symbol table
  entry is built up", whole-page read). The Boxes 45-53 text does not name it.
- ADDORD p.48 (TABMAN p.44, chart RA p.43 OCR locator); MULTI p.127 (chart RE p.126 OCR locator);
  GNLOAD p.88 (chart GN p.87 OCR locator); MQTAIL p.125; symbol-table formats Appendix A pp.190-191
  (Figs. 21, 22), ZST... bits (p.202; their figure is on pp.193-194, not read).
- **No text sentence names GNLOAD (Box 53) or Boxes 51A/51B.** The only related sentence is ¶1's
  "`GETCHA` makes the entry in the name file ...", which credits GETCHA, not GNLOAD.
- The "NOP/Branch instruction before the calling sequence to `ADDORD`" is a switch in MAIN's own
  code, set by MQTAIL (see TAIL, section 6).

### Box 54 (label MEF)
Chart: `PUT SPECIAL SET OF ERROR FLAGS INTO THE UNIT`. Entered from 50 NO, 51B and 53.

Text, p.25 R -> p.26 L, heading "Box 54" (whole paragraph):
> "A set of six error flags is OR'ed into each unit after a unit is processed in Pass 1 and after a unit is processed in Pass 2a. (During each pass processing there is an intermediate error flag buffer where the occurrence of the errors is recorded as detected.) The first five flags denote whether a symbol is undefined, multiply-defined without contradictions, circularly defined or defined in terms of an error symbol. The sixth flag denotes whether the suppress error message, ($) [a circled $], appeared before the instruction. At the end of Pass 1, only the sixth flag could be on. Later in Pass 2 when `VALUE` is evaluating a coded expression which contains error symbol(s), `VALUE` informs the using program which in turn sets on the appropriate error flag(s). `UITER`, too, does some detecting. However, while the undefined, circularly defined, and contagiously defined symbols are detected after Pass 1, the multiply-defined type symbols are detected and recorded by `MULTI` in the symbol table during Pass 1."

  (The sentence lists four conditions for "the first five flags"; p.33 L, whole-page read, names the
  fifth: "the multiply defined with contraditions".)

Names: the flags are Fig. 20's "Error Flags", bits 25-29 of fixed word 5 (the ZIOPX word), and
"p. suppress e.m." at bit 30 (p.189; five flags and a sixth, as the text says). The "mask containing the five error symbol indicators and the
suppress-error-message indicator" is zeroed at Box 2 (p.19 R, whole-page read); it is not named.
UITER p.135.

---

## 5. Boxes 57-62 (Chart AD, p.17): INTOUT, END, between passes

Chart:
- 57 subroutine box `INTOUT` / `SAVE FILE OF UNITS OUTSIDE OF CORE` (from 54).
- 58 `INCREASE UNIT COUNT`.
- 59 decision `IS THIS THE END PSEUDO-OP`: NO -> connector AA 12 (Box 2); YES -> 60.
- 60 subroutine box `INTOUT` / `SAVE FILE OF UNITS OUTSIDE OF CORE`.
- 61 `ENTER THE $ SYMBOL IN THE SYMBOL TABLE`.
- 62 (label ZZXY) `BETWEEN PASS PROCEDURE` -> terminal `GO TO PASS 2 FLOW CHART`.

Text, p.26 L, heading "Boxes 57-61" (whole paragraph):
> "The unit is now given to `INTOUT` to be put out on an external storage unit. The counter of the units is incremented. (During the trouble-shooting of the Pass 1 processing, the contents of this counter is available in the general work area as an indication of which unit is being processed. The counter is also available in Pass 2 to give the total number of units in the assembly.) If this is not the unit for the END pseudo-op, the Pass 1 procedure repeats itself and begins processing the next instruction at `MAIN`. Now if Pass 1 has just received the semicolon character from `GETCHA` while processing the END unit, Pass 1 will have the file of units terminated by going to the `INTOUT` subroutine with a special calling sequence. After Pass 1 has processed the unit for the END pseudo-op, `INTOUT` terminates the file of units with an index word of particular format. This end-of-file indication enables `INTIN` to know when the last unit has been processed in Pass 2a and in Pass 2b. The final action taken by Pass 1 is to enter the symbol $00 in the symbol table."

Text, p.26 L, heading "Box 62" (whole section):
> "The between-passes procedure that occurs after Pass 1 includes the following actions:
> 1. The between-passes procedure has MCP bring in all of STRAP II's Pass 2 from disk.
> 2. The between-passes procedure turns off the internal Pass 1 indicator, `Fpass1`, and turns on its Pass 2 counterpart, `Fpass2`.
> 3. The between-passes procedure writes the current pass indication on the numeric display lights of the console.
> 4. The between-passes procedure now enters `UITER` for the iteration of the symbol table."

Names: INTOUT p.90 (chart p.89 OCR locator; $13 "Used by INTOUT", p.175); INTIN p.143; the Unit
counter (p.19 R Box 2, whole-page read: "initially defined as one, is incremented by Pass 1 during
its end processing of the former unit"; p.173 R item 1: "set to one at the start of each pass ...
This incrementing is done in Pass 1 after the use of `INTOUT`"; p.38 OCR locator: "Unit (BU, 20)");
`Fpass1`, `Fpass2` (p.26 L; p.173 R); the $/$00 entry format Fig. 21 p.190 ("Entry in the Symbol
Table Especially for the $ Symbol or for an Internal STRAP II Special Symbol ... (n = 0 for the $
itself)") and Fig. 22 p.191. The last-control-word bits are Fig. 20's a ("on if last control
word") and b ("on if last control word in file"), p.189.

---

## 6. Chart AE (p.18) and the pseudo-operation routes

### Box 63 and Box 67: the dispatch
Chart (p.18): connector AE 29 -> Box 63 (label "ME+" [uncertain]) decision `DD`: YES -> Box 64;
NO -> Box 67 `DIGIT SELECT PSEUDO-OP BRANCH TABLE`. From Box 67 a vertical trunk runs down the left
margin with one labelled branch per group, in this order:

| Branch label (as printed) | Route |
|---|---|
| `PUNFUL,PUNNOR,PUNORG,PRNS,PRND,PRNID` | straight to AC 23 |
| `SKIP,NOPUN,NOPRNT,PRNOR` | straight to AC 23 |
| `PUNALL,SPNUS,PRNTALL,DUPLI,NOSEQ,RESEQ` | straight to AC 23 |
| `PUNID` | box `NPUNID` [first letter N/M uncertain; text has MPUNID] / `MAIN'S PUNID PROCESSING` -> AC 23 |
| `TLB,SLC,END,SLCR` | box `MQL` / `MAIN'S TLB,SLC, END,SLCR PROCESSING` -> AC 23 |
| `EXT` | box `MX` / `MAIN'S EXT PROCESSING` -> AC 23 |
| `SYN` | box `MQS` / `MAIN'S SYN PROCESSING` -> AC 23 |
| `DR,DRZ` | box `MQR` / `MAIN'S DR,DRZ PROCESSING` -> box `MDIMRF` / `MAIN'S DIMENSION PROCESSING` -> AC 23 |
| `PUNSYM` | box `MQP` / `MAIN'S PUNSYM PROCESSING` -> AC 23 |
| `SEM,REM` | box `MQM` [third letter not decidable in the chart ink; p.83 names `MQM` among GETFLD's callers, per the second reader] / `MAIN'S SEM,REM PROCESSING` -> AC 23 |
| `TAIL,UNTAIL` | box `MQTAIL` / `MAIN'S TAIL, UNTAIL PROCESSING` -> AC 23 |
| `LINK` | box `MQLINK` / `MAIN'S LINK PROCESSING` -> AC 23 |

The trunk line continues below the LINK branch and, per the second reader, **stops about five rows below
LINK**; it does not run off the page (the first reading said it did). The page is headed "PAGE 5 OF 5"; no further branch is printed.
Every route ends at AC 23 = Box 38 (MEDAF), so the address fields of a pseudo-op never pass
through Boxes 34-37.
**Chart/text disagreement:** the chart puts DUPLI among the ops that go straight to AC 23; the
text (p.27 L) gives DUPLI its own routine MDUP and leaves it out of the "collect the statement
characters" list. The text's list has "PRINID" [sic] where the chart has PRNID.

Text, p.26 R bottom -> p.27 L, heading "Box 67":

¶1 (p.26 R -> p.27 L):
> "Using the pseudo-op number and a digit-select-type branch technique, `MAIN` now determines what action must be taken by Pass 1 on the units of the individual pseudo-ops. Note the pseudo-op term was formerly applied to an instruction that could not be executed during the run of a program. However, during STRAP II processing, any code that produces a single piece of binary output of predetermined length is not con sidered [sic] a pseudo-op. Thus the operations such as XW, CF, RF, VF, CW, INDMK, and CNOP are not in the pseudo-op branch table. (See Appendix B.)"

¶2 (p.27 L):
> "For many of the pseudo-ops, all that `MAIN` has yet to do before performing the end-of-instruction procedure is to collect the statement characters. This is accomplished by a tight reloop into `GETCHA` until `GETCHA` "kicks out" a semicolon character. The pseudo-ops are: PUNFUL, PUNNOR, PUNORG, PRNS, PRND, PRINID [sic], SKIP, NOPUN, NOPRNT, PRNOR, PUNALL, SPNUS, PRNTALL, NOSEQ, and RESEQ."

Names: the pseudo-op number is Fig. 23's "Digit-Select Pseudo Op Number ... in Bits 32-50" of the
pseudo-op's primary-table entry (p.192; p.22 L "Box 23", whole-page read). Appendix B: section 6a.

### 6a. Appendix B, pp.195-196 (whole-page read; large type, but not re-read at 200 dpi)
Title: "APPENDIX B--ADDITIONAL INSTRUCTIONS AND PSEUDO-OPS ACCEPTED BY STRAP II" with footnote marks
1, 2. **It gives no pseudo-op numbers**: nothing here says what the digit-select digits are.
Under "PRIMARY OPERATIONS", "Pseudo-Ops" (footnote 3), in the printed order: COMBLOCK, CNOP
(footnote 4), DDI, DR, DRZ, DUPLI, END, ENTER, EXT (footnote 4), FEND, LINK, NOPRINT [sic: the
charts and p.27 have NOPRNT], NOPUN, NOSEQ, ORIGIN, PRND, PRNID, PRNOR, PRNS, PRNTALL, PUNALL,
PUNCDC, PUNFPC, PUNFUL, PUNID, PUNNOR, PUNORG, PUNREL, "PUNSYN(or PUNSYM)", REM, RESEQ, SEM, SKIP,
SLC, SLCR, SLCRCOM, SPNUS, SYN, TAIL, TLB, UNTAIL.
"General Instructions": CF, CW, DD, INDMK, RF, VF, XW. "MCP Instructions": IOD, REEL.
Footnotes (p.196):
> "1 Additional is used in the sense that the instructions and pseudo-ops are not specified in the IBM-7030 Reference Manual."
> "2 An operation mnemonic cannot exceed 8 characters in length."
> "3 These pseudo-ops are in each of STRAP II's three-digit select pseudo-op tables."
> "4 With the exception of the EXT and CNOP instructions, STRAP II considers an instruction to be a pseudo-op if it does not produce binary output."

Against the Box 67 text: p.27 L says CNOP is **not** in the pseudo-op branch table, while p.195
lists CNOP under Pseudo-Ops with footnote 3 ("in each of ... three digit select pseudo-op tables").
DD is a "General Instruction" here although Chart AE reaches it through the pseudo-op connector
(Box 63, before the branch table). Chart AE has no branch for COMBLOCK, ENTER, FEND, ORIGIN,
PUNCDC, PUNFPC, PUNREL, SLCRCOM (the relocation set, p.183 ff.) -- the stub of trunk below LINK
(second reader: it stops, it does not run off p.18) may be where they would hang.

### DUPLI (text only: MDUP)
p.27 L:
> "DUPLI: For a DUPLI, `MDUP` saves the pseudo-op's parameters, n and d. The index word `Xrepl` [last character l-or-1 uncertain; this face prints the digit one as "l" elsewhere, e.g. "Pass l", and `Xrep2` follows, so `Xrep1` is likely], in positions 0-17 will contain the number (n) of the input cards to be duplicated; the count field, `Xrep2`, will contain the number (d) of duplications for each of the n input cards. `MDUP` also turns on the indicator, `Xsp3`, to tell `XINPUT` that it is in the duplicating mode."
>
> "`XINPUT` will stack each of the next n card images in a special memory block before giving each of these n card images to `GETCHA`. After `XINPUT` has stacked n card images, then `ZINPUT` [sic: Z, not X] gets the next n times d card images from its own duplicating block rather than from the regular input source. `XINPUT` resumes fetching card images from the regular source after it has cycled through its duplicating block d times."

Names: MDUP (no Contents entry; not found elsewhere), XINPUT p.133 (chart XE p.132 OCR locator),
`Xrep1`/`Xrep2`/`Xsp3` (defined only here as far as read).

### PUNID (chart: NPUNID; text: MPUNID)
p.27 L:
> "PUNID: For the PUNID, `MPUNID` gets the characters from the address field for the ID from `GETCHA` and stores them in the available work area of the current unit. The value field of `Ziotpt` in the unit is set to contain the location of the ID in the unit which `OUTPUT` will later pick up. Blanks are significant in the ID symbol, so `MPUNID` has the `Gcaz` indicator on while requesting characters from `GETCHA`. An ID of less than eight characters is padded with blanks."

Names: `Ziotpt` = ZIOTPT, fixed word 6 of Fig. 20 ("Binary Output"), p.189; `Gcaz` p.20 L/R
(Box 5, whole-page read: GETCHA "does not give blanks to main flow unless main flow has turned on
the indicator, `Gcaz`"). MPUNID: no Contents entry.

### TLB, SLC, END, SLCR (MQL)
p.27 L:
> "TLB, SLC, END, SLCR: For the pseudo-ops, TLB, SLC, END, and SLCR, Pass 1 has the Pass 2 indicators set on and then has the statement field of the op encoded by `GETFLD`. Note since there is not a set of `INSERT` index words for these pseudo-ops, this subroutine sets up here the counter for the number of times to go to `GETFLD`. (The END instruction must be the only instruction in its card block whenever STRAP II is running with the indicator, `Hhcom4`, on.)"

Names: MQL (chart only; no Contents entry); `Hhcom4` (p.27 L; coprocessor section p.180, OCR
locator only); INSERT p.144. Which "Pass 2 indicators" are meant is not said.

### EXT (MX)
p.27 L:
> "EXT: For the pseudo-op, EXT, STRAP II forms two internal processing units. The EXTract procedure in `MAIN`, `MX`, builds up the first unit with the coded expressions of the parameters. After `MX` has returned to main flow, `MAIN` will form another unit for the material being extracted upon."

Earlier (p.22 R "Boxes 24, 25, 26", whole-page read): "Since the EXT parameters are handled in the
EXT pseudo-op subroutine later, this type of case is postponed for the later treatment."
Names: MX p.129 (chart p.128 OCR locator).

### SYN (MQS)
p.27 R ¶1:
> "SYN: The main purpose of `MQS`, which processes each SYN in Pass 1, is to build up the symbol entry in the `Msyte` area. (The symbol is actually entered in the symbol table at the end of the card block.) The dds information of the SYN op is transferred from the unit to the `Msyte` area. If any coded expression exits [sic] for an undetermined byte size and/or field length, it is moved to the `Msyte` area from the unit. Since the only coded expressions that could be in the variable part of the unit now are those for the dds, and these are now in `Msyte`, the available area in the unit buffer is redefined to be the first bit after the fixed portion of the current unit. Since `MQS` wants the coded expression to be made by `GETFLD` for the single address field of the SYN op put in `Msyte`, the upper boundary location of the buffer for the encoding has to be changed because the encoding is not going into the unit. The previous setting of `Bcfxtx` does not have to be saved because no more coded expressions will go into this unit for this instruction. Besides changing the upper buffer limit, an indicator has to be turned on to tell `GETFLD` that the encoding is not being put in the usual unit area because `GFLONG` is only set up to handle the overflow of the unit buffer area, but not the overflow of `Msyte`."

p.27 R ¶2:
> "STRAP II main flow knows that there is only one address field to be considered on a SYN unit, but the error message routine does not; the error message field counter must be incremented. The `Zifall` indicator is turned off to indicate to Pass 2 that there are coded expressions associated with this instruction which are not yet evaluated. `Zifp2` is not turned on because the coded expressions will get directly decoded in `UITER` through `VALUE` rather than in Pass 2 through DECODE. If there is a dimension in the address field, `MQS` uses the `MDIMRT` subroutine to make the separate dimension entry in the vle table. The dimension reference address will be saved in the vle entry of the SYN. (See Appendix A.)"

  ("DECODE" is not underlined in this one place. `MDIMRT`, with a T, is as printed; the Contents has
  "MDIMRF (and MDIMRT)" p.119, and p.63 distinguishes them: MDIMRF for a DR/DRZ without a name,
  MDIMRT for a SYN or a named DR/DRZ -- p.63 from OCR locator only.)

Names: MQS p.122 (chart DE p.121 OCR locator); `Msyte` (p.27 R; p.173 R); `Bcfxtx` (p.19 R-20 L,
whole-page read); GFLONG (not located; a GETFLD routine by its GF prefix, p.202); MDIMRF/MDIMRT
p.119 (chart p.118 OCR locator).

### DR, DRZ (MQR, MDIMRF)
p.27 R ¶3, continuing p.32 L top:
> "During `MQR` which handles the DR pseudo-op, the presence of a null dds will cause the dds, (N, 64, 4) to be assigned to the unit of the DR. If the address field is not null, `MQR` has the basic dimension entry made by `MDIMRF`. This entry is put in the unit. If the DR has a name, the basic dimension entry prefixed by the appropriate header bits will also be put later into the vle table. (See Appendix A.) The location of the basic portion of the vle dimension entry in the unit is saved in `Ziotpt` field of the unit. Before returning to main flow to complete the processing of the statement, `MQR` has `VDIMEN` try to evaluate the products of the dimensions. The intermediary products of the dimensions are kept in the dimension entry. When the final product is available (now possibly or later in Pass 2), it is put as a negative number into the value field of `Ziotpt`. The negative sign of the `Ziotpt` value field in a DR unit is the indicator that the dimension has been completely computed."

  (This paragraph has no heading of its own; it follows the SYN paragraphs. It names "the DR
  pseudo-op" only; DRZ is on the chart branch label.)

Names: MQR p.117 (chart p.116 OCR locator); MDIMRF p.119; VDIMEN (a VALUE routine by its V prefix;
not located); dimension entry format Fig. 22 p.191 ("An evaluated dimension entry", D-type vle).

### PUNSYM (MQP)
p.32 L:
> "PUNSYM: The PUNSYM pseudo-op causes `MQP` to collect the requested symbols from the address field(s) of the PUNSYM through `CPLTSY`, and then stores each symbol preceded by its character length in the variable section of the PUNSYM unit. The format of the SYN cards punched by STRAP II for the symbols requested by the PUNSYM is included in the description of the `NQBTP` subroutine. The instruction field counter in the fixed format of the unit and the error message field counter are each incremented for each PUNSYM symbol. The list of symbols will always follow the fixed format of the unit, so the location of the list is easily computed in Pass 2. (location of unit + length of fixed format = location of list.) `NPNSYM` and `NQBTP` process the PUNSYM's symbols during Pass 2."

Names: MQP p.115 (chart p.114 OCR locator); CPLTSY p.74; NQBTP p.169; NPNSYM (Chart FD p.31).

### REM,SEM (chart box "MQM"; p.83)
p.32 L:
> "REM,SEM: For REM and SEM processing, a four word intermediate error message mask is set up in the unit of the REM or SEM; each bit in the mask will correspond to the status of the corresponding numbered error message (0=restore, 1=suppress). As a result of the current instruction, the major error mask used by the error message routine is updated by the current intermediate mask whenever each SEM or REM unit is being processed. The location of the intermediate message mask in the variable part of the unit is in the value field at `Ziotpt`. The SEM-REM subroutine in Pass 1 uses `GETFLD` and `VALUE` to establish the number of each message in absolute form. There will be no decoding necessary for this unit in Pass 2."

  The text never names the subroutine; only the chart does, and its third letter is doubtful.

### TAIL, UNTAIL (MQTAIL, MQT)
p.32 L:
> "TAIL, UNTAIL: To handle a tail, `MQTAIL` collects the characters of the tail, sets up a tail entry, and enters it into the tail table. (See Appendix A.) Note that the tails are not in the regular symbol table and thus the tail table has its own control block for the table management subroutines of `TABMAN`. While a TAIL pseudo-op is in effect, any subsequent symbol appearing in the name field or in an instruction field will be appended with a suffix. A name to be tagged will be treated prior to its entry into the symbol table if a usual NOP instruction had been set to a Branch by `MQTAIL`. This switch indicates that the name is in the sphere of influence of a TAIL op and thus must be adjusted before being put into the symbol table. `CPLTSY`, the subroutine which collects the characters of a symbol appearing in an instruction field, appends the STRAP II tailing suffix, when necessary, to the collected symbol before giving the user routine the requested symbol. The UNTAIL pseudo-op is handled by `MQT`."

Names: MQTAIL and MQT p.125 (charts pp.123-124, "TAILOR (MQT)" OCR locator); tail table entry
Fig. 21 p.190 and Fig. 22 p.191; TABMAN p.44. The chart shows one box (MQTAIL) for both ops.

### LINK (MQLINK)
p.32 R (last Pass 1 paragraph):
> "LINK: When Pass 1 encounters the LINK pseudo-op in a program being assembled, the `MQLINK` subroutine is used to put the corresponding coded expression of the instruction -- LVI, 15, $+2 -- into the LINK unit. The location of the op question bits, which is carried both in the unit and in $5, is changed in both places to address the op index of an LVI type instruction. Processing indicators for Pass 2 are turned on in the unit: `Zifbo`, `Zifall`, and `Zifp2`."

  NOTE: the print says `Zifall` is **turned on** here, with a `$+2` expression in the unit. Elsewhere
  (p.24 L, p.27 R) Zifall is turned *off* when coded expressions remain to be evaluated, and Fig. 20
  calls it "nothing left for DECODE". Recorded as printed.

Names: MQLINK (no Contents entry); $5 (p.22 R, 200 dpi: "Information from the op entry is put in
the unit and the location of the op index is also put in $5 for common referencing during Pass 1.
During the processing of a unit in Pass 1 and Pass 2, $5 has the constant function of addressing
the op index."; p.175: "Address of the question bits for
instruction being processed"); ZIOPX "Location of Operation Question Bits", bits 0-24 of fixed
word 5 (p.189).

### Boxes 63-66C: DD and DDI
Chart (p.18, upper right):
- 63 decision `DD`: YES -> 64.
- 64 (label MQDD) decision `TYPE OF DD`: `(ALPHABETIC)` down -> 65; `(NUMERIC)` right-down -> 66A.
- 65 subroutine box `MQDALF` / `MAIN'S ALPHABETIC DD PROCESSING` -> AC 23.
- 66A subroutine box `MQDD` / `MAIN'S DD PROCESSING`; a line from 66A's left edge joins 65's exit
  into AC 23; two lines join 66A and 66B (down on the left, back up on the right).
- 66B subroutine box `MQDNUM` [printed "MCDNUM"/"MODNUM"-like] / `EVALUATE A NUMERIC DD`; two lines
  join 66B and 66C in the same way.
- 66C subroutine box `DNUM` / `COMPLETE A DD'S NUMERIC FIELD`.

Text, p.26 L bottom -> p.26 R, heading "Boxes 63-66C":

¶1 (p.26 L -> R):
> "The type of processing for DD's during Pass 1, of course, depends on whether the DD is alphabetic or numeric. (Even though a DDI unit is marked as such, the unit of a DDI receives the same processing as that of a DD during Pass 1.) Since the output of a DD is variable in length, the binary output for a DD is not built up in the usual skeleton op area in the fixed format of the unit. Instead the binary output will be built up in the currently available free area in the unit. The current setting of `Ibuffw` is saved in the fixed format field at `Ziotpt`. 32 for the later location of the binary output. If it is an alphabetic DD, the Pass 1 processing is rather straightforward. After some indicator settings are fixed by `MQDD`, `MQDALF` handles the alphabetic DD's. The comma is in the value field of $3 when `MQDD` goes to `MQDALF`. After completing the conversion `MQDALF` returns to main flow of Pass 1 with the value field of $3 containing the next non-blank character after the terminating character of the DD. `MQDALF` converts the characters of the alphabetic DD [sic: no "to"] output code and puts the results in the next available area in the variable length portion of the unit. The length and character count will also be inserted in the unit. The byte size is significant in the assembling of an alphabetic DD in codes: IQS, A8, and A6. If an absolute byte size of less than eight had been specified, `MQDALF` truncates the characters accordingly. On the other hand, if a symbolic byte size had been specified, truncation if any, will be done by `OUTPUT` in the final pass after the byte size has been evaluated. An end of card block terminates a DD if the terminating character specified in the entry mode was not included in the D field. (Also, the value field of $3 still contains the false semicolon when `MQDALF` returns to `MAIN`.) While `MQDALF` is requesting the A8 characters from `GETCHA`, `MQDALF` has the bit indicator, `Gcaz` on so that `GETCHA` will give the input blanks to `MQDALF`."

¶2 (p.26 R):
> "Now for the numeric DD's, there are three subroutines responsible for their processing in Pass 1. These subroutines are `MQDD`, `MQDNUM`, and `DNUM`. `MQDD` has the responsibility of taking care of the radix, which may be 2-16 in STRAP II, the entry mode, multiple numeric cases, the special sign (S), the special exponent (X), and the regular exponent (E). `DNUM` converts each operand in the statement (after collecting the characters from `GETCHA`) to a double precision floating point number, and `MQDNUM` evaluates the field to the semicolon, comma, or comment character."

¶3 (p.26 R):
> "Note that during Pass 1 the binary output in the unit for a numeric DD is in a floating point form. For all numeric types of DD's, except for Fn-type, the form is that of a double precision normalized floating point number. For the Fn-type numeric DD, the form is that of a double precision unnormalized floating point number. (See Appendix A.) Therefore, `OUTPUT` must always adjust the binary output in the unit of numeric DD to the specified mode, etc. , in order to obtain the final binary output."

Names: "`Ziotpt`. 32" = bit 32 of the ZIOTPT word (p.189; p.100 "relative location Ziotpt. 32" and
p.102's Ziotpt bits 24-27 are OCR locators only). MQDD p.100 (charts CJ/CK pp.98-99); MQDALF p.102
(chart p.101); MQDNUM p.107 (charts pp.104-106); DNUM p.110 (charts pp.108-109); MQDDPA p.112
(chart p.111) -- chart pages from OCR headers. The entry-mode buffer `Bem` and its
`Bemt`/`Bemu`/`Bemv` bits are on p.21 R (Boxes 10, 11, whole-page read): "This information is
picked up later when `MQDD` or `MQDALF` processes the DD."
The DDI is "marked as such": Fig. 20 has ZIFDD (bit 60, "f. DD"); no separate DDI bit was seen.

---

## 7. Index of names and where each is defined

Registers (p.175 "Index Register Assignment in STRAP II", whole-page read; plus first use in text):
- $0: value field for calling-sequence reads in TABMAN; refill field used during RNX.
- $2: used in the RNX instruction.
- $3: Pass 1 "A8 character from GETCHA" (p.20 L Box 5); Pass 2 "Address of the unit being processed" (p.25 L Box 44).
- $4: Pass 1 unused ("- - -"); Pass 2 "Absolute portion of the location counter".
- $5: both passes "Address of the question bits for instruction being processed" (p.22 R; p.32 R LINK).
- $6: Pass 1 "Address of unit being processed" (p.19 R Box 2); Pass 2 "Symbolic portion of the location counter".
- $7, $8, $9: "Used randomly". (`docs/strap2/pass1.md` line 31 has $7 as GNLOAD's parameter register, from p.88, not read here. But p.24 L/R twice says the location counter is in "$6 and $7 respectively" in Pass 2 -- see Boxes 35-37 note.)
- $10, $11: "Used by VALUE". $13: Pass 1 "Used by INTOUT". $14: Pass 1 "Used by GETCHA".
- $15: value field for subroutine linkages; refill field points to the table of exits for maskable interrupts (p.19 L item 6).

Flags and indicators:
- `Fblend`, `Fblena`: p.20 L (Boxes 3, 4). FNAME: charts pp.15-17 only. FNOSYM: chart p.17 only.
- `Fmodif` ("if-modifier-exists"; also printed `Modif` once): p.22 L, whole-page read. `Fiod`: p.21 L, p.23 R.
- `Fpass1`, `Fpass2`: p.26 L; p.173 R (with `Fuiter`, `Fpass3`).
- `Gcaz`: p.20 L-R. `Hhcom4`: p.27 L. `Xsp3`: p.27 L.
- Unit indicators (Fig. 20, p.189): ZIFNME (text "Zifname") c; ZIFP2 d; ZIFBO e; ZIFDD f; ZIFDDS g
  explicit dds; ZIFPMN h P-mode; ZIFFLF i f.l. filled in; ZIFSFL j symbolic f.l.; ZIFBSF k b.s.
  filled in; ZIFSBS l symbolic b.s.; ZIFDSF m dds filled in; ZIFALL n nothing left for DECODE;
  p suppress e.m. (unnamed, bit 30 of fixed word 5).
- Unit fields (Fig. 20, p.189; "fixed word n" = the n-th word after the control word). Tick labels
  as printed, with the host's `unit.py:17-47` reading beside them:
  word 1: ZIADAB from 0, ticks "24 25" (host 0-24); ZILBO 25-31; ZIADSY from 32, tick "56" (host
  32-56); c,d,e,f at ticks "56 58 60" = ZIFNME 57, ZIFP2 58, ZIFBO 59, ZIFDD 60 (host the same).
  word 2: ZILCFD from 0, tick "24" (host 0-24); g-m = ZIFDDS 25, ZIFPMN 26, ZIFFLF 27, ZIFSFL 28,
  ZIFBSF 29, ZIFSBS 30, ZIFDSF 31; ZILSST from 32, ticks "56 57" (host 32-56); ZINXBO 57-63.
  word 3: ZILPMS from 0, ticks "24 25" (host 0-24); ZIFALL 25; "0 0" at 26-27; ZINAME 28-31;
  ZINFLD from 32, ticks "49 50" (host 32-49); ZIDDS from 50, ticks "62 63" (host 50-62).
  word 4: ZICDID 0-63. word 5: ZIOPX from 0, ticks "24 25" (host 0-24); Error Flags 25-29; p 30;
  zeros 31-63. word 6: ZIOTPT 0-63 "Binary Output".
  The figure's name-to-letter pairing for the rotated labels (ZIFNME/ZIFP2/ZIFBO/ZIFDD over c-f;
  ZIFDDS ... ZIFDSF over g-m) is by position and agrees with the legend and the host.

Buffers and index words:
- `Ibuffw`, `Bcfxtx`, `Bsystx`, `Bop`, `Bopx`, `Bem`: p.19 R - p.20 L (Box 2). p.19 R (200 dpi):
  "The index word, `Ibuffw`, locates available area in the buffer reserved for the units. Since
  `Ibuffw` is now addressing the starting location of a new unit, `MAIN` adjusts this address to a
  full word location and saves this address in $6. (The fixed format fields in the unit are
  referenced by $6 during Pass 1.) Next `MAIN` updates `Ibuffw` to address the available area after
  the fixed format where the coded expression(s), if any, followed by the statement field characters
  will be put. This location of the starting point of the coded expression(s) is saved for the later
  computation of the total length of the coded expression(s) in this unit." `Bcfldx`: p.21 L, p.23 R, p.24 R.
- `Bop2x`: p.22 R. `Bsymbx`: p.23 L (CPLTSY's index word; p.74).
- `Msyte`: p.27 R; p.173 R. `Xrep1` [uncertain], `Xrep2`: p.27 L.
- Prefix conventions: Appendix D p.202 (B buffers and index words; F control flags; EF error flags;
  GC GETCHA; GF GETFLD; M main flow of Pass 1; X I-O; ZI... unit; ZO... op question bits; ZST...
  function portion of a symbol's vle).

Tables: primary op table and op index / question bits (`Zo...`), p.22 L-R, Fig. 23 p.192; secondary
op table Fig. 24 p.192; symbol table, tail table, indicator table Fig. 21 p.190; vle table Fig. 22
p.191; question character blocks (`Qc...`) p.20 R; pseudo-op branch table p.26 R-27 L, Appendix B
p.195 (section 6a).

Subroutines (description start page from the Contents, p.3; chart page from OCR page headers, not
checked in the image):
ADDORD 48 · BOPSER 67 · CPLTNM 71 · CPLTSY 74 · DECODE 140 · DNUM 110 (108) · GETCHA 79 (77) ·
GETFLD 83 (80) · GNLOAD 88 (87) · INSERT 144 · INTIN 143 · INTOUT 90 (89) · MBSPEC 93 (92) ·
MDIMRF and MDIMRT 119 (118) · MIBA 95 (94) · MIOD 97 (96) · MOVE 41 · MQDALF 102 (101) ·
MQDD 100 (98) · MQDDPA 112 (111) · MQDNUM 107 (104) · MQP 115 (114) · MQR 117 (116) ·
MQS 122 (121) · MQTAIL and MQT 125 (123) · MULTI 127 (126) · MX 129 (128) · NQBTP 169 ·
OUTPUT 157 · TABMAN 44 (43) · UITER 135 · VALUE 55 (54) · XINPUT 133 (132).
**Not in the Contents and not located:** MDUP, MPUNID/NPUNID, MQL, MQLINK, the SEM/REM routine
("MQM"?), GFLONG, VDIMEN, NPNSYM (appears only on Chart FD p.31).

---

## 8. Host `stretch/strap/strap2/pass1.py` against these pages

Line numbers are of the working tree as read on 2026-11-15. Three lists.

### (a) Host behaviour differs from what the page says

1. **LINK's Zifall.** p.32 R: "Processing indicators for Pass 2 are turned on in the unit: `Zifbo`,
   `Zifall`, and `Zifp2`." Host `_mqlink` puts ZIFALL **0** (pass1.py:937). (The print may itself be
   loose; see the note under LINK.) NEW: `docs/strap2/pass1.md` line 803 records the page's "on" but
   not that the host does the opposite.
2. **When the symbol is entered.** Chart 45-53 / p.25: the entry is *formed* on the block's first
   unit (46-49) and ADDORD is called at the block's *last* unit (50-52A). Host enters it on the
   first unit (pass1.py:355-360), declared CHOSEN at pass1.py:366-368. No FNOSYM. GNLOAD (Box 53)
   has no counterpart; the host keeps `print_names` (pass1.py:359).
3. **Fiod.** p.23 R sets it for anything "not a master control op and not a comment"; p.21 L sets it
   for the `;` that becomes DRZ(N),1. Host sets `self.fiod` only at pass1.py:181, after a successful
   table lookup. Not set by: `_make_drz` (pass1.py:487-503; p.21 L says it is), and EXT, which
   returns through `_mx` at pass1.py:150-151 before line 181 (p.23 R's rule covers it). Also not set
   by `_illegal` (pass1.py:531-540) -- INFERENCE only: no sentence says what Fiod does for an
   illegal op.
4. **Ambiguous op with two fields.** p.24 L: MAIN "changes the unit, etc., accordingly" in Pass 1.
   Host leaves it to Pass 2 (`pass2.py:647-651`); `_collect_fields` (pass1.py:317-331) does nothing.
5. **Box 34's length.** p.23 R: the length "of a non-ambiguous binary producing instruction" is put
   in the unit. Host puts `entry.length` for every entry (pass1.py:185), an ambiguous one included.
6. **Alphabetic DD conversion.** p.26 R: MQDALF converts the characters to the output code in Pass 1
   and truncates for an absolute byte size under eight. Host stores the characters as 8-bit host
   codes and leaves conversion to OUTPUT (pass1.py:790-796).
7. **Alphabetic DD, no terminator.** p.26 R: "An end of card block terminates a DD if the
   terminating character ... was not included in the D field." Host raises FieldError 85
   (pass1.py:786-789), and a FieldError is not a message: `strap2/__init__.py:28-31` catches it
   round the whole of `p1.run()` and raises StrapError, so Pass 1 stops at that card. (Whether the
   7030 also gives a message is in p.102-103, not read.)
8. **SYN's unit.** p.27 R: the dds coded expressions are moved to `Msyte` and the unit's available
   area is reset to the first bit after the fixed portion, so the SYN unit carries no coded
   expression. Host leaves a symbolic dds expression in the unit (pass1.py:300, called at 178) and
   copies it to the entry later (pass1.py:386-396); the address expression is kept only in
   `self.syn_expr` (pass1.py:735).
9. **PUNID's pointer.** p.27 L: "The value field of `Ziotpt`" holds the ID's location. Host writes
   the bit address into the whole 64-bit ZIOTPT field, i.e. right-justified (pass1.py:657;
   `unit.py:47`), not into the value field.
10. **CNOP.** p.27 L: CNOP is "not in the pseudo-op branch table". Host handles it inside `_pseudo`
    (pass1.py:605-606). But Appendix B p.195 lists CNOP as a pseudo-op in the digit-select tables
    (section 6a), so the pages disagree with each other here.
11. **EXT's place in the flow.** Chart: EXT is reached through Boxes 30A-33 and Box 67. Host
    intercepts the mnemonic at pass1.py:150-151, before the modifier loop, the table lookup and Fiod.
12. **Unit counter.** p.19 R / p.173 R: starts at one. Host `Units.units` starts at 0
    (`unit.py:64`), and messages are keyed by the unit's bit address, not its number
    (e.g. pass1.py:536).
13. **TLB/SLC/END/SLCR.** p.27 L: "Pass 1 has the Pass 2 indicators set on". Host `_mql` sets none
    on; it only turns ZIFALL off (pass1.py:671-674). Which indicators the page means is not said.

### (b) The page states something the host has no counterpart for

1. **REM/SEM** (p.32 L): four-word mask in the unit, GETFLD + VALUE in Pass 1, location in Ziotpt.
   `_pseudo` (pass1.py:585-610) has no branch; the unit goes straight to the wind-up at line 610,
   so the address field is collected as statement characters and nothing else. Both mnemonics are
   in the host's pseudo-op list (`optable.py:32`). Not in README.md's "Not yet written" list
   (README.md:155-162); whether Pass 2 or the listing handles them from the print image was not
   traced (a grep of pass2.py and listing.py for SEM/REM/PUNSYM found nothing).
2. **PUNSYM** (p.32 L): MQP collects symbols through CPLTSY, each preceded by its character length,
   both field counters incremented. No branch in `_pseudo`; same remarks as for REM/SEM
   (`optable.py:33`).
3. **$00 at END** (Box 61, p.24 L, p.26 L): the `$00` entry with a SYN-like two-datum expression.
   The host writes the `$` datum pair in GETFLD (`getfld.py:380-388`) but makes no symbol entry;
   Pass 2 sets VALUE's counters directly (`pass2.py:180-182`).
4. **Box 60, the END's second INTOUT**: "terminates the file of units with an index word of
   particular format". Host ends by count (`unit.py:72-90`); pass1.py:364 just returns True.
5. **Error-message field counter** (pp.24 L, 27 R, 32 L, 173 R): never counted; `Messages.add`
   takes `field=0`, CHOSEN (pass1.py:34-39). Already declared: README.md:160-161 "the field number
   in an error record (always 0)".
6. **GETFLD call counter from the op's first fill index word** (p.24 L). Host loops while a comma
   follows and compares with `sum(n for _r, n in entry.fills)` (pass1.py:320-329); whether that sum
   equals the first fill word's count is not checked here. The page does not say what happens to an
   extra field; the host's FieldError 40 is its own, and like every FieldError it ends Pass 1
   (`strap2/__init__.py:28-31`) rather than giving a message and going on.
7. **"DDI ... must ... have a name"** (p.25 L): no test in `_mqdd` (pass1.py:742-764). SYN's is
   message 43 (pass1.py:731-732).
8. **The "phoney" entry** for a named pseudo-op that should have no name (p.25 R): `_form_symbol`
   makes an ordinary KIND_LABEL entry (pass1.py:373).
9. **SYN with a dimension -> MDIMRT** (p.27 R): `_mqs` takes one field (pass1.py:733-735) and makes
   no dimension entry.
10. **DR: the basic dimension entry, Ziotpt, VDIMEN** (p.27 R, p.32 L): host stores the encoded
    fields and ZINFLD only (pass1.py:686-706); nothing in ZIOTPT, no products in Pass 1. The
    dimension goes to the symbol entry at pass1.py:407-419.
11. **`Hhcom4` / END alone in its card block** (p.27 L): no coprocessor in the host (declared at
    pass1.py:6 and README.md:157).
12. **Box 54's intermediate error-flag buffer**: the host writes ZISUPP straight into the unit when
    the `$` is read (pass1.py:132-133). Equivalent result at the end of Pass 1.
13. **MQS's upper-limit change and "not in the unit" indicator for GFLONG** (p.27 R): no host
    counterpart (no buffer limits).
14. **LINK changes $5** (p.32 R): n/a on the host; ZIOPX is changed (pass1.py:933).

### (c) The host does something these pages do not cover

1. **Numeric DD look-ahead**: `_field_entry` reads `g.card` directly up to column 72
   (pass1.py:876-897); `_numeric_field` calls `gf._peek_gp()` (pass1.py:845, 853) and `gp_chain`
   (pass1.py:870). pp.19-32 say only that MQDD handles "the radix ..., the entry mode, multiple
   numeric cases, (S), (X), (E)". See MQDD charts CJ/CK pp.98-99 and text p.100; MQDNUM pp.104-107.
2. **DR dimension-list look-ahead**: `_dim_parens` (pass1.py:708-724, used at 689). Not covered; see
   MQR p.117, MDIMRF pp.118-120.
3. **Numeric DD form** (this one belongs with list (a) as far as Fn goes). The module docstring
   says a numeric DD "keeps its text for OUTPUT, not Fig. 26's double precision form"
   (pass1.py:7-8); that comment is stale: `_numeric` converts each field and `store_entry` writes a
   12-bit exponent and a 96-bit fraction (pass1.py:804-827, 874; `dnum.py:420-453`), and README.md:312
   says the same. `dnum.py:4` says "Pass 1 keeps every numeric entry as a floating number of 96
   bits, normalized", and `store_entry` writes `v.frac` the same way whether or not `fn` is given
   (`dnum.py:428-438`); the unnormalized form appears only at `dnum.py:377`, on the OUTPUT side. So
   as far as read, **the host holds an Fn-type number normalized in the unit**, where p.26 R says
   "the form is that of a double precision unnormalized floating point number". Not traced further
   (Fig. 26 p.193 not read). `store_entry`'s CHOSEN sign bit (`dnum.py:423-425`) is not from these
   pages.
4. **Zifall with no fields**: host turns ZIFALL off after the loop even when no field was read
   (pass1.py:331). p.24 L ties turning it off to there being coded expressions; the zero-field case
   is not stated.
5. **Check digit sequence**: incremented mod 10 per named block (pass1.py:357). The pages say only
   "a digit from 0-9" (p.173 L).
6. **DR null dds "error 46 (p.27)"** in `_mqr`'s docstring (pass1.py:677): p.27 prints no message
   number.
7. **Comment and illegal-op units carried as PRNOR** (pass1.py:481, 537); p.22 L (whole-page read)
   says an illegal op's unit "is set up as a -- SIC, $15; BE, 0 -- instruction" (CHOSEN at
   pass1.py:531-535).
8. **Extra mnemonics**: FEND (pass1.py:364), REPEAT (pass1.py:599), ORIGIN/PUNFPC/ENTER/COMBLOCK/
   SLCRCOM through `_mql` (pass1.py:594-596), `EXT,(I,J,N)` (pass1.py:909-910). From N28-1081 and
   the relocation section (p.183 ff.), not from pp.19-32.
9. **No END card** tolerated (pass1.py:94-96, 997-999).
10. **DUPLI**: `_mdup` (pass1.py:612-632) follows the p.27 text, not the chart's straight-to-AC 23
    route; its argument checks are from N28-1081.
11. **TAIL/UNTAIL level syntax** (pass1.py:953-995): p.32 L gives no syntax; see p.125.
12. **MIOD details** (pass1.py:543-583): p.23 R says only that MIOD handles REEL and IOD; see p.97.

---

## 9. Passages not read with confidence

- Box 33's YES/NO legends: read clearly, but they look reversed (YES -> AC 28, NO -> AE 29).
- Boxes 47/49: the line from 49 ends in an arrow-head on Box 47's right edge. Drawn so; meaning
  doubtful.
- Box 46's side legend "TURN / (OFF)": what it turns off is not stated.
- Chart box names with a doubtful glyph: "NPUNID" (N or M), the SEM/REM box "MQM" (third letter),
  "ME+" at Box 63 (second reader: clear), "F1OD" in Box 32 (second reader: digit one), "MQDNUM" in 66B (printed like "MCDNUM").
- `Xrepl` / `Xrep1` (p.27 L): final character l or 1.
- "`ZINPUT`" (p.27 L): printed with Z; presumably XINPUT.
- "`Bcfxtx`" on p.24 L (Boxes 35-37 ¶1): clearly printed, but possibly the print's slip for `Bcfldx`. Second reader (400 dpi): the print is `Bcfxtx`, and it disagrees with p.83, where GETFLD updates `Bcfldx`;
  p.84 Box 1 has GETFLD round `Bcfxtx` down to a full word. Both readings stay open; p.24's ink is `Bcfxtx`.
- "$6 and $7" (p.24 L and R) against p.175's $6 and $4.
- "`Zifall`" turned *on* for LINK (p.32 R): clearly printed; sense doubtful.
- `Zstcnt` / "Zstent" on p.173 R: whole-page resolution only.
- Fig. 20: where a field's left end is bit 0 and the next tick label is "24 25", whether the field is 0-23 or 0-24 (the host takes 0-24).
- Everything marked "(whole-page read)" or "(OCR locator only)": the parts of pp.19-22 not listed in
  section 0, p.14, pp.173, 190-192, 195-196, p.63, the p.100/102/122 mentions, and all chart page
  numbers in section 7.
- The left-hand column of p.26 was cropped one character short on the left at 200 dpi; the missing
  first letters were taken from the whole-page image (no word was in doubt).

---

## 10. What `stretch/docs/strap2/pass1.md` already records, and what is new here

`docs/strap2/pass1.md` (943 lines; section 2 lines 144-366 walks the same boxes, section 8 lines
890-943 lists gaps and contradictions) was found after these notes were drafted; it was grepped and
its section 8 read, not the whole file. It paraphrases; it has no verbatim quotes.

Already recorded there:
- Box 33's reversed YES/NO (contradiction 10: "Reading at 170 dpi confirms the labels. Text followed").
- Box 46's "TURN ... NO (OFF)" not saying what is turned off (gap 9, with an INFERRED reading that
  `Fname` is reset; and that `Fblena`'s reset is nowhere stated).
- GNLOAD (Box 53) against "GETCHA makes the entry in the name file" (gap 8, contradiction 12).
- `Zifname` / ZIFNME (contradiction 11).
- DUPLI chart/text, MPUNID / NPUNID (contradiction 13).
- No write-up for MQM, MDUP, MPUNID, MQL, MQLINK, GFLONG (gap 3); it reads the SEM/REM box as MQM.
- "six vs. five flags listed by name" on p.25 (gap 5).
- The "24 bits" of $00 against Fig. 14 (contradiction 26-27; `getfld.py:381-383` cites "gap 27").
- The page statements themselves for Boxes 34-62 and LINK (lines 289-361, 802-803), e.g. line
  294-295 "No reset of `Bcfxtx`, which GETFLD updates", line 803 "ZIFBO, ZIFALL, ZIFP2 on [32]".

New here (not in its section 8):
- `Bcfxtx` on p.24 L where the sense wants `Bcfldx` (recorded there as fact, not as a doubt).
- "$6 and $7" on p.24 against $4/$6 on pp.33 and 175.
- `Zifall` turned **on** for LINK against its meaning elsewhere, and the host doing the opposite.
- Boxes 47/49: the arrow from 49 into 47.
- `Xrepl`/`Xrep1`, "`ZINPUT`", "an `MAIN`", "PRINID", "exits" for exists.
- CNOP: p.27 L against Appendix B p.195; Appendix B gives no pseudo-op numbers.
- The trunk of Chart AE below LINK (second reader: it stops about five rows down).
- Host list (a) items 1, 3, 5, 7, 9, 12, 13 and (b) items 1-4, 7-10, and the Fn point in (c)3, as
  far as its section 8 and README.md's "Not yet written" list go. (a)2 is the host's declared
  CHOSEN; (b)5 and (b)11 are declared in README.md.
