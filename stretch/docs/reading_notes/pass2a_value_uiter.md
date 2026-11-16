> **STATUS: UNVERIFIED FINDING AID.** Written by a reading agent on 2026-11-15
> from page images. Nothing here may be cited as a source: every quote must be
> re-read in the ink (the page image) before it is relied on, as AGENTS.md
> requires. Passages the agent could not read confidently are listed at the end.

# Reading notes for step 5: Pass 2a (pp.28-36), VALUE (pp.54-60), UITER (pp.135-137)

Source: `stretch/docs/C22-6729_7030_STRAP_II_Sys_Analysis_Guide.pdf` (PDF page = printed page),
read from page images. The charts were re-read from 220- and 300-dpi crops. Which text pages were
re-read at zoom and which only at page resolution is listed in Part F; a name quoted from a page read
only at page resolution has not had its l/1 and letter order checked at zoom.

Conventions in these notes
- `CHART:` = text printed inside/next to a chart box, in the chart's capitals.
- `QUOTE (p.N L|R):` = verbatim from the prose, page N, left or right column. Line-end hyphens are
  joined ("be-/tween" -> "between"); nothing else is normalised. Names IBM underlines are written
  plain (the underline is not reproduced). `[sic]` marks something printed that way.
- `READING:` = my own inference. Not IBM's words. Treat as unverified.
- `[uncertain: ...]` = a glyph I could not read with confidence.

No numbered error message is printed anywhere on pp.28-36, 54-60 or 135-137. The pages say only
"an error message" or name MACHER / ERRNUM / ERRPRT. The numbered list is pp.176-179; Part G gives
the entries that bear on step 5, with my matching marked READING.

---------------------------------------------------------------------------------------------------
## PART A. PASS 2 (Charts FA-FD pp.28-31; text pp.32-36)

Pass 2a and Pass 2b share the four charts. Each box below is tagged [2a], [2b] or [both] from the
"PASS 2A" diamonds on the chart.

### A.0 The tail of the Pass 1 description that Pass 2 depends on (pp.27 R, 32 L, 32 R top)

DR and Ziotpt (sentence runs from p.27 R bottom onto p.32 L top):
- QUOTE (p.27 R): "During MQR which handles the DR pseudo-op, the presence of a null dds will cause
  the dds, (N, 64, 4) to be assigned to the unit of the DR. If the address field is not null, MQR has
  the basic dimension entry made by MDIMRF. This entry is put in the unit. If the DR has a name, the
  basic dimension entry prefixed by the appropriate header bits will also be put later into the vle
  table. (See Appendix A.) The location of the basic portion of the vle dimension entry in the unit is
  saved in Ziotpt field of the unit. Before returning to main flow to complete the processing of the
  statement, MQR has VDIMEN try to evaluate the products of the dimensions. The intermediary products
  of the dimensions are kept in the dimension entry. When the final product is available (now possibly
  or later in Pass 2), it is put as a negative number into the value field of Ziotpt. The negative"
  (p.32 L) "sign of the Ziotpt value field in a DR unit is the indicator that the dimension has been
  completely computed."
- QUOTE (p.27 R, about SYN, just above): "...the error message field counter must be incremented. The
  Zifall indicator is turned off to indicate to Pass 2 that there are coded expressions associated
  with this instruction which are not yet evaluated. Zifp2 is not turned on because the coded
  expressions will get directly decoded in UITER through VALUE rather than in Pass 2 through DECODE.
  If there is a dimension in the address field, MQS uses the MDIMRT subroutine to make the separate
  dimension entry in the vle table. The dimension reference address will be saved in the vle entry of
  the SYN. (See Appendix A.)"
  (The start of this SYN paragraph is higher on p.27 R; I read only the lower half of that column.)

PUNSYM (p.32 L):
- QUOTE: "PUNSYM: The PUNSYM pseudo-op causes MQP to collect the requested symbols from the address
  field(s) of the PUNSYM through CPLTSY, and then stores each symbol preceded by its character length
  in the variable section of the PUNSYM unit. The format of the SYN cards punched by STRAP II for the
  symbols requested by the PUNSYM is included in the description of the NQBTP subroutine. The
  instruction field counter in the fixed format of the unit and the error message field counter are
  each incremented for each PUNSYM symbol. The list of symbols will always follow the fixed format of
  the unit, so the location of the list is easily computed in Pass 2. (location of unit + length of
  fixed format = location of list.) NPNSYM and NQBTP process the PUNSYM's symbols during Pass 2."

REM, SEM (p.32 L):
- QUOTE: "REM, SEM: For REM and SEM processing, a four word intermediate error message mask is set up
  in the unit of the REM or SEM; each bit in the mask will correspond to the status of the
  corresponding numbered error message (0=restore, 1=suppress). As a result of the current
  instruction, the major error mask used by the error message routine is updated by the current
  intermediate mask whenever each SEM or REM unit is being processed. The location of the intermediate
  message mask in the variable part of the unit is in the value field at Ziotpt. The SEM-REM
  subroutine in Pass 1 uses GETFLD and VALUE to establish the number of each message in absolute form.
  There will be no decoding necessary for this unit in Pass 2."

TAIL, UNTAIL (p.32 L): Pass 1 only (MQTAIL, tail table with its own TABMAN control block, CPLTSY
appends the suffix, UNTAIL by MQT). Not transcribed; no Pass 2 action beyond "box 20" wind-up.

LINK (p.32 R top):
- QUOTE: "LINK: When Pass 1 encounters the LINK pseudo-op in a program being assembled, the MQLINK
  subroutine is used to put the corresponding coded expression of the instruction -- LVI, 15, $+2 --
  into the LINK unit. The location of the op question bits, which is carried both in the unit and in
  $5, is changed in both places to address the op index of an LVI type instruction. Processing
  indicators for Pass 2 are turned on in the unit: Zifbo, Zifall, and Zifp2."
  (Zifbo here; p.34 R prints "Zilbo" for the length field. Both read at zoom; they are two names.)

### A.1 Chart FA (p.28), "PASS 2---PAGE 1 OF 4"

Labels beside boxes are printed above the box's top-left corner.

| Box | Label | CHART text | Exits as drawn |
|---|---|---|---|
| (entry) | | FROM END OF PASS 1 | -> 1 |
| 1 | | UITER / ITERATION OF SYMBOL TABLE AFTER PASS 1 (subroutine box) | down, then right into 2 |
| 2 | | PASS 2A (decision) | YES (up) -> 3; NO (down) -> 4 |
| 3 | NPS2 | INITIALIZATION NECESSARY FOR PASS 2A | down -> 4 |
| 4 | NPS3 | INITIALIZATION NECESSARY FOR PASS 2B | down -> 5A |
| 5A | NGUNTB | INTIN / INTERMEDIATE EXPANDED INSTR UNIT FETCH (subroutine box) | down -> 5B. Off-page connector "FA 14" enters 5A from the right |
| 5B | | EOF (decision) | YES (left) -> 23; NO (down) -> 6 |
| 6 | | INITIALIZATION FOR EACH UNIT | -> 7 |
| 7 | | PASS 2A (decision) | NO (right) -> 8; YES (down) -> 9 |
| 8 | | FIRST UNIT THROUGH PASS 2A [sic] (decision) | YES -> 25; NO (down) -> joins line into 9 |
| 25 | | NMCPA1 / PUNCH LIM AND GO CARDS (subroutine box) | down, joins line into 9 |
| 9 | | MCP UNIT (decision) | YES (left) -> 26; NO (right) -> 10 |
| 26 | | NMCP / PROCESS MCP OPS IN PASS 2B (subroutine box) | down -> connector FB 27 |
| 10 | | SET ON SWITCH TO PREVENT PUNCHING SUBSEQUENT MCP INSTRUCTIONS | down -> connector FB 27 |
| 23 | | PASS 2A (decision) | YES (up) -> 24 (the line enters 24 from below); NO (down) -> 31 |
| 24 | | UITER / ITERATION OF SYMBOL TABLE AFTER PASS 2A (subroutine box) | up, joins box 1's line into 2 |
| 31 | NPS2B | END OF ASSEMBLY PROCEDURE | (none) |

READING on the chart:
- Box 8 says "FIRST UNIT THROUGH PASS 2A" but is on the NO branch of box 7 "PASS 2A", and the text
  (p.35 R, Boxes 7, 8, 25) says "On the first cycle through Pass 2b". The chart text looks like a
  misprint for 2B; record as printed.
- Box 2 "PASS 2A" is tested after UITER and before box 3; with box 24 feeding the same test, YES
  means "UITER just ran after Pass 1" and NO means "after Pass 2a". The text (p.33 L) says Np2ind "is
  set on now" in boxes 3,4 and (p.35 R) that UITER returns with Np2ind off and Fpass3 on. How box 2
  can read YES before box 3 sets Np2ind is not explained on these pages. [open]
- Box 3 flows into box 4 as drawn, i.e. the Pass 2b initialization box is also passed through for
  Pass 2a. The text treats "Boxes 3, 4" as one paragraph.
- Box 26 NMCP is labelled "IN PASS 2B" but sits on both passes' path (box 9 is reached from 7 YES
  too). Text p.33 R: "Master control program's units are processed during Pass 2b."

### A.2 Chart FB (p.29), "PASS 2---PAGE 2 OF 4"

| Box | Label | CHART text | Exits as drawn |
|---|---|---|---|
| (entry) | | connector FB 27 | -> 11 |
| 11 | NA | IS THIS THE 2ND OF TWO EXT UNITS | YES (left, long line down) -> 13; NO -> 12A |
| 12A | | IS ROUNDING NECESSARY FOR LOCATION COUNTER | YES -> 12B; NO (down) -> 13 |
| 12B | | ROUND THE LOCATION COUNTER | down -> 12C |
| 12C | | CNOP UNIT | NO (left) -> joins 12A's NO line -> 13; YES (down) -> 12D |
| 12D | | DOES LOCATION COUNTER STILL NEED ADJUSTING | NO (right) -> connector FC 31; YES (down) -> 12E |
| 12E | | MAKE THE CNOP UNIT INTO A NOP UNIT | left -> joins line -> 13 |
| 13 | | SAVE LOCATION COUNTER SETTING IN VLE OF THE DOLLAR SIGN SYM TABLE ENTRY | -> 14A |
| 14A | | UNIT CONTAIN CODED EXPRESSNS TO BE DECODED | YES -> 14B; NO (down) -> 15 |
| 14B | | DECODE / DECODE CODED EXPRESSIONS IN THE UNIT (subroutine box) | two lines out of its right side to subordinate boxes VALUE and INSERT; down -> connector 22 |
| (unnumbered) | | VALUE / EVALUATE A CODED EXPRESSION (subroutine box, reached from 14B) | |
| (unnumbered) | | INSERT / INSERT VALUE INTO BINARY OUTPUT IN UNIT (subroutine box, reached from 14B) | |
| 14C | | (entered from connector 22) INST IN CURRENT UNIT PRODUCE BINARY OUTPUT | YES -> 14E; NO (down) -> 14D |
| 14D | | DR UNIT | YES (right, up) -> joins line into 14E; NO (down) -> connector 28 |
| 14E | | PASS 2A | YES -> 14F; NO (down) -> 27 |
| 14F | | STORE COUNTERS | down -> 14G |
| 27 | | CHECK COUNTERS | down, right -> joins line into 14G |
| 14G | | IS THIS THE FIRST OF THE 2 EXT UNITS | YES (left) -> 14L; NO (down) -> 14H |
| 14L | | NEXT2 / PROCESS EXTRACT (subroutine box) | -> connector FC 31 |
| 14H | | DD OR A DR UNIT | NO (left) -> 14K; YES (down) -> 14I |
| 14I | | IS ABSOLUTE TOTAL LENGTH COMPUTED | YES (left, up) -> joins line into 14K; NO (down) -> 14J |
| 14K | | UPDATE LOCATION COUNTER BY ABSOLUTE LENGTH OF BINARY OUTPUT | -> connector FC 31 |
| 14J | | SET UP A NEW RELATIVE SYMBOLIC COUNTER, ZERO ABSOLUTE CNTR | -> connector FC 31 |
| 15 | | (entered from 14A NO and from connector 28) PASS 2A | YES -> 16; NO (down) -> connector FC 32 |
| 16 | | SYN UNIT | NO -> 17; YES (down) -> joins line -> FC 32 |
| 17 | | STORE COUNTERS | down -> joins line -> FC 32 |

READING: connector 28 on this page (14D NO -> box 15) is an on-page connector and is not Chart FC's
box 28 "CHECK COUNTERS". Likewise connector 22 is not box 22.

READING: boxes 14A and 14C are most likely tests of unit flags, not of the op: p.140 says "DECODE is
entered from pass 2a and 2b if Zifp2 is one", and Fig. 20's legend has d (ZIFP2) "DECODE gets unit"
and e (ZIFBO) "binary output". So 14A = Zifp2, 14C = Zifbo, 14D/14H = the DR / DD op (f = ZIFDD
"DD"). The pages do not state this mapping box by box.

### A.3 Chart FC (p.30), "PASS 2---PAGE 3 OF 4"

| Box | Label | CHART text | Exits as drawn |
|---|---|---|---|
| (entry) | | connector FC 32 | -> 18A |
| 18A | NUPDT [uncertain: NUPDT or NUPOT] | PSEUDO-OP SPECIFIED IN EXT STMNT | YES -> 18B; NO (down) -> 19A |
| 18B | | NEXT2 [strip reads "N=XT2", taken as NEXT2 as in 14L] / EXTRACT ZEROS (subroutine box) | right, long line down -> joins line into 21 |
| 19A | | PSEUDO-OP | YES (left) -> 19B; NO (down) -> 20 |
| 19B | | DIGIT SELECT PSEUDO-OP BRANCH TABLE | -> connector FD 41 |
| 20 | NPOB | (also entered from connector FC 25) PASS 2A | NO (right) -> 28; YES (down) -> 21 |
| 28 | | CHECK COUNTERS | down -> joins line into 21 |
| 21 | NGUNT | (also entered from connector FC 31) PUT SPECIAL SET OF ERROR FLAGS INTO THE UNIT | -> 22 |
| 22 | | PASS 2A | NO (right) -> 30; YES (down) -> connector FA 14 |
| 30 | | OUTPUT / PRODUCE THE DOCUMENTS OF THE ASSEMBLY (subroutine box) | down, left -> joins line -> FA 14 |

Subordinate boxes hung off box 30 on the right-hand side (all subroutine boxes, unnumbered):
ERRNUM / GET ERROR PAGE AND LINE NUMBER; "CPPUN" [sic; text and contents page say OPPUN] / PUNCH;
OEDIT / SET UP CARRIAGE CONTROL CHARACTER; OPLIST / LIST; NQBTP / PUNCH SYN CARDS;
NUNDSY / SPECIAL SYMBOL LISTS; ERRPRT / PRINT ERROR MESSAGES; NAMEIN / GET LISTING NAME FOR EACH
NAMED UNIT.

### A.4 Chart FD (p.31), "PASS 2---PAGE 4 OF 4"

Entry: connector FD 41 -> box 19B, label NPOC, "DIGIT SELECT PSEUDO-OP BRANCH TABLE". A vertical line
runs down from 19B; each named exit leaves it to the right:

| Exit name on chart | Box (strip / body) |
|---|---|
| PRNID | NPRNID / PASS 2'S PRNID PROCEDURE |
| SYN | NSYN / PASS 2'S SYN PROCEDURE |
| SLC,SLCR | NSLC / PASS 2'S SLC,SLCR PROCEDURE |
| END | NEND / PASS 2'S END PROCEDURE |
| EXT | NEXT / PASS 2'S EXT PROCEDURE |
| NOPRNT,TAIL,UNTAIL ,PUNID,PUNFUL,PUNNOR ,PUNORG,PRNS,PRND,SKIP ,NOPUN,TLB,DDI ,PRNOR,PUNALL,PRNTALL ,DUPLI,NOSEQ,RESEQ | (no box; straight to 19C) |
| PUNSYM | NPNSYM / PASS 2'S PUNSYM PROCEDURE |
| SEM | NBSEM / PASS 2'S SEM PROCEDURE |
| REM | NBREM / PASS 2'S REM PROCEDURE |
| SPNUS | NSPRES / PASS 2'S SPNUS PROCEDURE |

All ten lines join into box 19C "PASS 2A": NO (up) -> connector FC 25 (= box 20); YES (down) ->
connector FC 31 (= box 21). The vertical line from 19B continues below SPNUS and runs off the bottom
of the chart with no further exit drawn.

READING: the chart list (2a and 2b share it) has 19 names with no box. The p.34 list for 2a and the
p.36 list for 2b differ from it and from each other (see A.5, Boxes 19A-19B and 19A-19C): the chart
has DDI but not DD, DR, DRZ, PUNSYM or SPNUS in the no-box list.

### A.5 The prose, box by box (pp.32 R - 36 R), verbatim

Heading (p.32 R): "DESCRIPTION OF THE ACTION INDICATED ON THE FLOW CHART OF PASS 2"

**Box 1** [between Pass 1 and 2a] (p.32 R - p.33 L)
- QUOTE (p.32 R): "A program using STRAP II can have instructions containing symbols in the data
  description and/or address fields, which symbols have not been previously defined in the program.
  Therefore, the value of each symbol is not available at the end of Pass 1. Thus, the establishing of
  values for the binary output and the settings of the location counter must be done during a two-part
  Pass 2."
- QUOTE (p.32 R): "UITER inspects the symbol table twice, once between the end of Pass 1 and the
  beginning of Pass 2a, and again between the end of Pass 2a and the beginning of Pass 2b."
- QUOTE (p.32 R): "After Pass 1, UITER iterates over the symbol table to establish a data description
  and value for each symbol. Each symbol table entry is examined and any symbol which is not complete,
  but still needed to evaluate the original symbol, is kept in a push down list and in turn evaluated
  in an attempt to complete both the data description and the value of the original symbol. A non-P
  mode symbol initiates a new level. As UITER analyzes each entry in the symbol table, UITER updates
  the symbol counter for the error message procedure which may be used during UITER."
- QUOTE (p.32 R): "UITER plays the major role in evaluating each SYN instruction. Only UITER can
  detect the undefined symbols in a SYN chain. During the first scan of the symbol table, UITER marks
  these entries of the undefined symbols. Furthermore, while completing each symbol table entry in
  the first scan, UITER also turns on the appropriate symbol error flags in the symbol table entry if
  a symbol is either circularly defined or contagiously defined. UITER assigns a value of zero to the
  base symbol in a circularly defined symbol chain."
- QUOTE (p.32 R - p.33 L): "The general detection of error symbols occurs so: After Pass 1, UITER
  turns on an indicator to inform VALUE that it can now make an undefined-type entry in the symbol
  table during each UITER or Pass 2 evaluation of any symbol which VALUE can not find in the symbol
  table. (When Pass 1 used VALUE to evaluate a coded expression formed by GETFLD, it was allowable for
  VALUE not to find the symbol in the symbol table since the symbol table was incomplete during
  Pass 1. But at the end of Pass 1, the symbol table contains an entry for each name that has appeared
  in the name field of a card block.) Note that all the regular symbol table entries have been made
  before Pass 2a, but Pass 2a does make entries in the symbol table for the undefined symbols
  appearing in non-SYN address fields, for the location counter values that are candidates for hi-lo
  values, and for the STRAP II symbolic counter symbols that are needed until absolute increments are
  known. Whenever VALUE is asked to evaluate a symbol, VALUE marks the symbol as having been
  referenced from an address field. The multiply-defined symbols are detected in ADDORD and are
  resolved and marked in MULTI during Pass 1. On the final scanning of the symbol table, NUNDSY can
  easily recognize the error symbols marked for special listing. Of the five different type of
  irregular symbols, only the multiply defined and the multiply defined with contraditions [sic] are
  mutually exclusive."
  READING: "an indicator to inform VALUE" is Vcundf by the VALUE text (p.57 R); the page does not
  name it here.

**Boxes 3, 4** [3 = 2a; 4 = 2b by the chart; the text does not separate them] (p.33 L)
- QUOTE: "Because of the overlapping functions of Pass 2a and Pass 2b, there are unique indicators
  associated with each of the phases of Pass 2. The Pass 2a indicator, Np2ind, is set on now. It will
  be turned off between Pass 2a and Pass 2b."
- QUOTE: "Pass 2a goes to INTIN an additional time after receiving the END unit, so INTIN by its
  end-of-file condition thus obtained, can set up the recycling through the units during Pass 2b. The
  entry into the between passes procedure is made from INTIN. This re-entry location is set now."
- QUOTE: "Also included in this initialization process is the saving of the location of the ($)
  [a $ in a circle] symbol table entry since the setting of the location counter for each instruction
  must be put into this entry. The subroutine for bringing in the units into internal storage and the
  error message subroutines are initialized. Miscellaneous indicators are set. The unit counter of the
  error message routine and $4 and $6 are set to zero. The absolute counter is set to its initial
  41.₈ location (0 if in PUNREL mode). This initial setting of the absolute counter is entered into
  the hi-lo table now as the first entry. If the first unit is that of an SLC pseudo op, this low
  entry will be overruled."
  ("41." is followed by a subscript 8: octal 41.)
  READING: the paragraph says $4 is set to zero and then that "the absolute counter" is set to 41(8);
  p.34 R calls $4 "the absolute counter" and $6 "the symbolic counter". The order of the two
  statements is as printed.

**Boxes 5A - 6** [both] (p.33 L - R)
- QUOTE: "For each new unit INTIN brings into process, the following takes place at this point: The
  field counter for field identification in the error message is zeroed; the unit counter is
  incremented and the symbol counter is updated. (The field counter is incremented during the Pass 2
  procedures which process address fields, e.g., generally by DECODE.) $3 is set up with the location
  of the new unit. $5 is set up with the location of the op index for the new instruction. The five
  error flags for an erroneous symbol are zeroed. If the unit has a name associated with it, the
  location of the function portion of the vle part of the symbol table is computed and saved."

**Boxes 9, 10, 26** [text: 2a action] (p.33 R)
- QUOTE: "Master control program's units are processed during Pass 2b. At this point in Pass 2a, the
  first op that is not an MCP op (comments excepted) causes a switch to be set which will prevent
  non-contiguous MCP ops from being punched in Pass 2b, although they will be listed."

**Box 11** [both] (p.33 R)
- QUOTE: "During the processing of EXTract units, the location counter is adjusted only for the first
  of the two units."

**Boxes 12A, 12B** [text: 2a] (p.33 R)
- QUOTE: "Since the processing of a previous instruction only incremented the location counter by the
  length of the binary output, rounding tests must be made at the beginning of processing of each new
  unit in Pass 2a. If the unit is one for a DD or for a DR in a non-floating point mode, there is no
  rounding necessary. Either of these type of units is sent on to the next processing step. If not,
  tests are made by using the op question bits to see if the instruction in the unit must have a full
  or half word address. Once the type of op has been established, the counter can be rounded, if
  necessary, immediately if $6 is zero, i.e., if there is no symbolic portion of the location
  counter."
- QUOTE: "If however there is a symbolic counter portion, changes may have to be made on the symbolic
  counter. If the present symbolic counter symbol is at the required type location, then only the
  absolute counter is adjusted for any necessary rounding. Otherwise a new symbolic counter symbol is
  entered into the symbol table marked with the appropriate full or half word indicator; $4 will be
  set to zero again; and $6 will contain the location of the new STRAP symbolic counter symbol."

**Boxes 12C - 12E** [text gives no pass] (p.33 R - p.34 L)
- QUOTE: "Further adjustment to the location counter may be necessary if the present unit is a CNOP.
  The CNOP unit will be effectively processed as a NOP unit if the adjustment is necessary."

**Box 13** [both] (p.34 L)
- QUOTE: "The current setting of the absolute and symbolic portion of the location counter are put in
  the function portion of the symbol table entry for the ($) [circled $]"
  (The sentence ends with the circled $ and no full stop.)

**Boxes 14A - 14L** [text: "Here in Pass 2a"] (p.34 L - R)
- QUOTE: "Here in Pass 2a the unit which contains any coded expressions that have to be decoded is
  sent to DECODE. (Any unit which produces binary output — including the DR, DRZ, EXT, LINK, DD and
  DDI ops — will necessarily go to DECODE in Pass 2a.) Note that SYN and MCP-type ops will not be
  decoded at this point but in their own specialized subroutines in Pass 2."
- QUOTE: "DECODE uses VALUE in decoding the coded expression(s) in each unit. Included in the
  information from VALUE is whether the coded expression just evaluated, contained any "error"
  symbols. If so, DECODE OR's the error symbol indicators set up by VALUE into the intermediate
  error-symbol mask. During the later processing of the unit in the pass, the intermediate
  error-symbol mask will be OR'd into the unit so that when the instruction is picked up from the unit
  to be printed, the instruction will be preceded on the listing by the appropriate error-symbol
  message."
- QUOTE: "A fact about DDI processing should be mentioned now. A DDI is processed as a DD during
  Pass 1. In Pass 2, DECODE will get the DDI evaluated by using special facilities in OUTPUT. Then
  DECODE adjusts the unit of the DDI so that subsequently Pass 2 will recognize and treat the unit as
  one for a SYN."
- QUOTE: "If a unit has just been to DECODE the setting of the location counter (absolute and symbolic
  counter) is put into the unit and into the corresponding symbol table entry, if any. If the unit
  produces binary output or is a DR, the location counter must be advanced, also, in preparation for
  the new unit."
- QUOTE: "Furthermore, after coming from DECODE, the absolute length of the binary output may or may
  not be established. If it is, the length is added to the contents of $4 (absolute portion of the
  location counter). The symbolic error flags will then be OR'd into the unit and the Pass 2a cycle is
  repeated."
- QUOTE (p.34 L - R): "On the other hand, if the op is a DD or a DR, the length of the binary output
  could very easily still be unestablished. Note that the final length of the binary output for a DD
  or a DR is kept in Ziotpt field of the unit instead of the usual Zilbo. So a special STRAP II symbol
  is entered into the symbol table. In the function portion of its vle will be set up a special coded
  expression in which the sum of the current symbolic counter and the absolute counter is encoded. The
  location of the vle portion of this new STRAP II symbol replaces the previous contents of the
  symbolic counter ($6) and zero replaces the previous contents of the absolute counter ($4). Thus a
  cascading of STRAP II special symbols can be built up to refer to the actual setting of the location
  counter in a relative way whenever the length of the binary output is not available at update time
  or whenever the symbolic counter is not at the appropriate type of address at rounding time. Again
  the final OR'ing of the symbol error flags into the unit is performed and the Pass 2a cycle is
  repeated."
  READING (gap): the "special coded expression" encodes "the sum of the current symbolic counter and
  the absolute counter". The pages read here do not say how the still-unknown length of the DD/DR
  enters the new symbol (presumably by a reference to the unit's/dimension's value); see DECODE
  pp.139-140 and Appendix A before implementing. [open]

**Boxes 15 - 17** [2a] (p.34 R)
- QUOTE: "Now to finish the Pass 2a processing of a unit which contains an instruction which is a
  pseudo-op. The contents of the absolute and symbolic location counters are put into the unit and the
  vle portion of any companion symbol table entry. This is not done if the unit contains a SYN op."

**Boxes 18A, 18B** [both] (p.34 R)
- QUOTE: "STRAP II does not prevent extracting from a pseudo-op, but instead supplies zeros and gives
  an error message."  (No message number printed.)

**Box 21** [2a] (p.34 R)
- QUOTE: "If the op is not a pseudo-op the present setting of the five error flags for an erroneously
  used symbol is OR'ed into the unit now rather than later and the cycle through Pass 2a is repeated.
  Note the MCP ops, the DD and the DR ops which have already been treated with [sic] follow this
  action, immediately, too."

**Boxes 19A - 19B** [2a] (p.34 R)
- QUOTE: "The pseudo-op number which was put in the unit of the pseudo-op during Pass 1, is again used
  in another digit select type branch to determine the specialized treatment of the pseudo-op during
  Pass 2a. The specific treatment for each pseudo-op that still needs treatment in Pass 2a before the
  next unit is brought in is described below. The following pseudo-ops only need the wind up procedure
  in box 20: PUNID, PUNFUL, PUNNOR, PUNORG, PRNS, PRND, SKIP, NOPUN, TLB, DDI, NOPRNT, TAIL, UNTAIL,
  PRNOR, PUNALL, PRNTALL, DUPLI, NOSEQ and RESEQ."
  READING: the text says "box 20", but Chart FD sends Pass 2a (19C YES) to connector FC 31 = box 21,
  and only Pass 2b (19C NO) to FC 25 = box 20. Box 20's own YES exit also goes to 21, so the 2a
  effect is the same.

Per-pseudo-op Pass 2a text (p.35 L - R):
- QUOTE "PRNID: For PRNID, the unit must also be given to the output phase in Pass 2a as well as in
  Pass 2b. The setting of the error flags are OR'ed into the unit before the output phase gets
  control. Since the PRNID statements are the only assembly material printed during Pass 2a, all the
  PRNID's will precede the major listing; the PRNID will also appear in its specified location through
  the Pass 2b printing."
- QUOTE "SLC: For SLC, Pass 2a adjusts the absolute and symbolic counters and makes an entry in the
  hi-lo table. (The SCLR [sic] indicator is turned off, and the hi-lo-entry can-be-made indicator will
  be set on.)"
- QUOTE "SLCR: For an SLCR, Pass 2a adjusts the absolute and symbolic counters. No entry is made in
  the hi-lo table. (The SCLR [sic] indicator is turned on and the hi-lo-entry-can-be-made indicator is
  turned off.)"
- QUOTE "END: For the END unit Pass 2a enters the location of the END as a possible hi-lo candidate
  into the hi-lo table."
- QUOTE "EXT: For an EXT unit Pass 2a has evaluated the coded expressions for the parameters and saved
  their values in the unit. The location counter is incremented by the length indicated by the N
  parameter and the rounding procedure for the next of the EXT units will not be performed. The output
  phase will pick up the value of the parameter and do the actual extracting from the next unit later
  in Pass 2b. If the statement of the EXT op is a multiple field DD, then the location counter will be
  incremented the extra amount."
- QUOTE "SYN: For a SYN op, Pass 2a tests if the value is complete; if so, then Pass 2a now performs
  the action as described in box 21. If the SYN is not completely evaluated at this point, then there
  is another try to get the value of the SYN by using a section of UITER."
- QUOTE "PUNSYM: For each symbol appearing in a PUNSYM pseudo op, the corresponding symbol table entry
  must be marked for the later punching (to be more exact a bit must be turned on in the function
  portion of the vle). Since by Pass 2a all the symbols have been entered into the symbol table, the
  necessary vle's can be marked now during NPUNSYM [sic; chart strip and p.32 say NPNSYM] in Pass 2a.
  The SYN cards will be punched in Pass 2b during the OUTPUT subroutine through NQBTP."
- QUOTE "SEM, REM: For a SEM or a REM the message numbers in the major error mask of the error
  subroutine are adjusted by the intermediate error mask in the current unit."
- QUOTE "SPNUS: For a SPNUS, all that Pass 2a does in [sic] turn on an indicator for NUNDSY before
  performing the end of Pass 2a procedure."

**Box 24** [between 2a and 2b] (p.35 R)
- QUOTE: "If an end-of-file condition occurs when INTIN is fetching the next unit for Pass 2a to
  process, INTIN will branch to the between passes procedure. (This EOF exit was set up at the
  beginning of Pass 2a.) Between Pass 2a and Pass 2b, UITER concludes the evaluation of the data
  description and the value of the symbols in the symbol table. In addition, at this time UITER
  evaluates the memory bounds of the program being assembled by using the Uhl subroutine which
  inspects each hi-lo entry in the vle table. On completion of the iteration, UITER returns to Pass 2b
  with the Pass 2a indicator, Np2ind, off and Pass 2b indicator, Fpass3, on. At this time all the
  names of the assembly are evaluated."

The Pass 2b walk (p.35 R - p.36 R). Not step 5's subject, but the same boxes; quoted where it fixes
what 2a must leave behind.
- QUOTE (p.35 R): "Again we shall follow the flow through the Pass 2 flow chart. Only this time we
  shall take all the Pass 2b branches. By the beginning of Pass 2b all the symbols will have been
  evaluated in the symbol table. During Pass 2b the floating point format of all numeric DD's will be
  adjusted and any general parenthetical field entries on the DD's will be treated, the binary output
  for an EXTract will be extracted, and finally the documents for the program being assembled will be
  produced."
- Boxes 7, 8, 25 [2b] QUOTE (p.35 R): "On the first cycle through Pass 2b the GO and the LIM cards are
  produced and punched by NMCPA1. This is the only output that is not punched by OUTPUT. The GO and
  LIM cards will not appear on the listing (nor will the SKIP and NOPRNT pseudo ops appear on the
  listing). Note that the GO and LIM cards precede each binary deck produced by STRAP."
- Boxes 14E, 27 [2b] QUOTE (p.35 R - p.36 L): "In Pass 2b, the location counter value previously
  stored in the unit and in the symbol table entry are checked against the present setting of the
  location counter. For a non-binary producing unit the checking is done later. If a discrepancy
  occurs, an error message will be given and the Pass 2a setting of the location counter will be
  used."  (No message number printed.)
- Boxes 20, 28 [2b] QUOTE (p.36 L): "During the processing of a unit which does not contain a binary
  output producing instruction, the checking of the location counter value is done at this point."
- Boxes 22, 30 [2b] QUOTE (p.36 L): "Now before bringing in the next unit, Pass 2b gives OUTPUT
  control at this point. The function of OUTPUT is to set up the listing and the binary card images
  which are printed and punched by the I-O subroutines. For the listing of the instruction, OUTPUT
  gets the location counter, binary output, and symbolic statement including the comment from the
  corresponding unit. OUTPUT gets the name for each instruction from the name file brought into
  internal storage by NAMEIN. OUTPUT has the tilting [sic] and the page numbering done by OEDIT.
  ERRNUM sets up and ERRPRT has printed the error messages for OUTPUT. The I-O subroutines, OPLIST and
  OPPUN, perform the actual printing and punching. If SYN cards have to be made, OUTPUT has the PUNSYM
  procedure in Pass 2b, the NQBTP subroutine, make them after all the regular binary cards have been
  produced. NUNDSY is responsible for collecting and having printed those symbols in the symbol table
  which are undefined, multiply-defined with or without contradictions, circularly defined, or never
  used in the program. Since OUTPUT uses a digit select type branch technique in determining the
  appropriate pseudo-op procedure, new pseudo-ops can be added with a minimum alteration to OUTPUT.
  Note this is the third of the three digit select type pseudo-op tables in STRAP II."
- Boxes 19A - 19C [2b] QUOTE (p.36 L): "During Pass 2b the following pseudo ops will need no further
  treatment at this point: PRNID, PUNID, PUNFUL, PUNNOR, PUNORG, PRNS, PRND, SKIP, NOPUN, TLB, DDI,
  DD, DR, DRZ, NOPRNT, PUNSYM, TAIL, UNTAIL, PRNOR, PUNALL, SPUNS [sic], PRNTALL, DUPLI, NOSEQ, and
  RESEQ. Their units will go on to box 20 immediately for processing. Their major effect on the
  Pass 2b process happens in OUTPUT."
- QUOTE (p.36 R) "SLC, SLCR: For an SLC and SLCR, the location counter is adjusted at this point. The
  absolute value of the location will be available now. (As with most of the other pseudo-ops, OUTPUT
  performs a specific action later with a SLC and SLCR. If OUTPUT receives a unit of an SLCR, OUTPUT
  stops punching cards until the next SLC unit is encountered.)"
- QUOTE (p.36 R) "END: For an END op, the current symbolic and absolute counters are checked and the
  end of file location for INTIN is now set up."
- QUOTE (p.36 R) "EXT: For an EXT op, similarly as in Pass 2a, switches are set to prevent rounding
  and to detect extraction from a psuedo-op [sic] in the second of the EXTract's units. The length of
  the binary output has now been established for the EXT instruction and is saved. Then the counters
  will be checked in box 28."
- QUOTE (p.36 R) "SYN: For every SYN, its value is now available in Pass 2b. These bit and integer
  values are taken from the absolute and symbolic counters of the symbol table and put into the
  absolute and symbolic counter fields of the corresponding unit of the SYN. Also, the setting of the
  five error symbol flags that have been accumulated with the symbol are now OR'd into the unit of the
  SYN. Furthermore, if the symbol has a dimension, the dimension reference address is moved to the
  unit, too."
- QUOTE (p.36 R) "SEM, REM: For a SEM or REM unit, the same action takes place now as happened in Pass
  2a. Actually the updating of the error mask must take place in each pass of STRAP II since a
  condition causing an error message to be given can be detected in any pass of STRAP II."
- Boxes 5B, 23, 31 [end] QUOTE (p.36 R): "The end-of-assembly procedure for STRAP II includes the
  following actions: 1. The end-of-assembly procedure prints on the listing the total time and the
  total number of units used. 2. The end-of-assembly procedure prints the message, THE END, on a page
  by itself, and by using an additional SKIP pseudo-op, displays the message to the operator. 3. The
  end-of-assembly procedure updates the Communication Record with the information where the STRAP II
  documents are located. 4. After returning the Communication Record to MCP, the end-of-assembly
  procedure gives MCP full control to continue the processing."

### A.6 Pass 2: registers, indicators, fields, tables named on these pages

| Name | What the page says | Where |
|---|---|---|
| $3 | "set up with the location of the new unit" (each unit) | p.33 R, Boxes 5A-6 |
| $5 | "set up with the location of the op index for the new instruction"; also "the location of the op question bits, which is carried both in the unit and in $5" | p.33 R; p.32 R (LINK) |
| $4 | "absolute portion of the location counter"; "the absolute counter ($4)"; zeroed at init | p.34 L, p.34 R, p.33 L |
| $6 | "the symbolic counter ($6)"; zero = "no symbolic portion of the location counter"; holds "the location of the new STRAP symbolic counter symbol" / "the location of the vle portion of this new STRAP II symbol" | p.33 R, p.34 R |
| Np2ind | "The Pass 2a indicator"; on in 2a, off between 2a and 2b; "Np2ind is zero if we are in Pass 1" | p.33 L, p.35 R, p.135 L |
| Fpass3 | "Pass 2b indicator" turned on by UITER's return after 2a | p.35 R |
| Zifbo, Zifall, Zifp2 | "Processing indicators for Pass 2 ... in the unit"; Zifall off = "coded expressions associated with this instruction which are not yet evaluated"; Zifp2 not on for SYN | p.32 R, p.27 R |
| Ziotpt | unit field: DR dimension-entry location, negative value field = "dimension has been completely computed"; SEM/REM mask location; "final length of the binary output for a DD or a DR" | p.27 R/32 L, p.32 L, p.34 R |
| Zilbo | "the usual" unit field for the length of binary output | p.34 R |
| ($) entry | symbol table entry of the location counter; its location saved at init; counters stored in its "function portion" each unit | p.33 L, p.34 L |
| hi-lo table / hi-lo entries "in the vle table" | first entry = initial absolute counter; SLC makes an entry, SLCR none, END a candidate; read back by Uhl | p.33 L, p.35 L, p.35 R |
| "SCLR indicator", "hi-lo-entry-can-be-made indicator" | SLC: off / on. SLCR: on / off. No symbolic names printed. | p.35 L |
| intermediate error-symbol mask; "the five error flags for an erroneous symbol" | zeroed per unit, OR'ed by DECODE from VALUE's flags, OR'ed into the unit at box 21 | p.33 R, p.34 L, p.34 R |
| major error mask / intermediate (four word) error message mask | SEM/REM | p.32 L, p.35 R, p.36 R |
| "a switch ... which will prevent non-contiguous MCP ops from being punched" | set by first non-MCP op in 2a (comments excepted). No name printed. | p.33 R |
| "an indicator for NUNDSY" | set by SPNUS in 2a. No name printed. | p.35 R |
| Entry labels on the charts | NPS2 (3), NPS3 (4), NGUNTB (5A), NPS2B (31), NA (11), NUPDT? (18A), NPOB (20), NGUNT (21), NPOC (19B) | Charts FA-FD |
| Subroutines | UITER, INTIN, NMCPA1, NMCP, DECODE, VALUE, INSERT, NEXT2, OUTPUT (+ERRNUM, OPPUN, OEDIT, OPLIST, NQBTP, NUNDSY, ERRPRT, NAMEIN), NPRNID, NSYN, NSLC, NEND, NEXT, NPNSYM, NBSEM, NBREM, NSPRES | Charts FA-FD |

No calling sequence (index register for the return, parameter words) is printed for any Pass 2
routine on pp.28-36.

---------------------------------------------------------------------------------------------------
## PART B. VALUE (Chart RD p.54; text pp.55-59; Fig. 9 p.58; Fig. 10 p.60)

### B.1 Purpose and the four entries (p.55 L)

QUOTE (p.55 L, PURPOSE):
"VALUE evaluates a coded expression
 VSKIP skips over a coded expression.
 VDIMEN evaluates a dimension statement.
 VMOVE moves a coded expression."

### B.2 Linkage, verbatim (pp.55-56)

**VSKIP** (p.55 L)
- On Entry: "1. The calling sequence is: LVI, 15, $+2; B, VSKIP" / "2. The index word Valinx locates
  the first bit of the coded expression."
- On Exit: "1. Valinx will be updated to locate the first bit after the coded expression." / "2. If
  the using program has turned on bit, Vcundf, VSKIP also will have made a symbol table entry for any
  undefined symbol encountered in the coded expression."

**VDIMEN** (p.55 L)
- On Entry: "1. The calling sequence is:
      LVI, 15, $+2; B, VDIMEN
      B, a fix-up subroutine        @not evaluated exit
      Normal Return                 @not evaluated exit"
  ([sic], confirmed at zoom: BOTH lines carry the comment "@not evaluated exit", each broken over
  two lines as "@not evaluated / exit"; compare VALUE's "@break return" on the first line and no
  comment on the second. The second is presumably a misprint.)
  "2. $1 locates the first bit of the dimension statement."
- On Exit: "1. If the dimension statement was evaluated, $1 contains the location of the product of
  the dimensions." / "2. If the dimension statement could not be evaluated, $1 still locates the first
  bit of the dimension statement." / "3. If the using program has turned on bit Vcundf, VDIMEN also
  will have made a symbol table entry for any undefined symbol encountered in the coded expression."

**VMOVE** (p.55 R)
- On Entry: "1. The calling sequence is: LVI, 15, $+2; B, VMOVE / Normal Return" / "2. The index word,
  Valinx, locates the first bit of the coded expression." / "3. The index word, Vmovex, contains the
  location where the expression is to be moved."
- On Exit: "1. After the expression has been moved, Valinx and Vmovex will be updated accordingly." /
  "2. If the using program has turned on bit, Vcundf, VMOVE also will have made a symbol table entry
  for any undefined symbol encountered in the coded expression."

**VALUE** (p.55 R)
- On Entry: "1. The calling sequence is:
      LVI, 15, $+2; B, VALUE
      B, a fix-up subroutine        @break return
      Normal Return"
  "2. The index word Valinx locates the first bit of the coded expression."
  "3. Bit Vcbv = 1 if VALUE is not to attempt to get value and index information.
      Bit Vcbsx = 1 if VALUE is not to attempt to get S/X type information.
      Bit Vcbdim = 1 if VALUE is not to attempt to get dimension information.
      Bit Vcbdds = 1 if VALUE is not to attempt to get dds information."
- On Exit (p.55 R - p.56): "1. If while attempting to do its job, VALUE discovers that a symbol table
  entry is lacking needed information, VALUE will exit to the break exit and provide the using program
  with the following information:
   a. $1 will locate the function part of the symbol table entry causing the trouble.
   b. Bit Vnbv = 1 if value and index information is needed.
      Bit Vnbsx = 1 if S/X type information is needed.
      Bit Vnbdim = 1 if dimension information is needed.
      Bit Vnbdds = 1 if dds information is needed.
   c. Bit Vfbv = 1 if the value and index information is affected.
      Bit Vfbsx = 1 if S/X type of information is affected.
      Bit Vfbdim = 1 if dimension information is affected.
      Bit Vfbdds = 1 if dds information is affected.
   d. Bits Vcbc [sic; read at zoom, elsewhere Vcbv], Vcbsx, Vcbdim, Vcbdds, are not changed."
- "2. When VALUE exits to the normal return, VALUE provides the using program with the following
  information:" then the table (p.56):

  | group | Location | dds | Contents |
  |---|---|---|---|
  | value and index information | Sini | (B, 25) | integer value |
  | | Sinb | (B, 25) | bit style value |
  | | Sinx | (BU, 4) | index |
  | | Sinxq | (BU, 1) | = 1 if there is an index / = 0 if there is no index |
  | | Sinrl1 | (BU, 1) | relocation indicators* (one brace over both) |
  | | Sinrl2 | (BU, 1) | |
  | S/X type information | Sinsx | (BU, 2) | 00 integer style (S) / 10 bit style (X) / 01 / 11 (the last two have no meaning printed) |
  | dimension information | Sindim | (B, 25) | dimension reference |
  | dds information | Sindds | (B, 25) | dds reference |
  | | Sindsq | (BU, 1) | = 1 if the dds reference is known / = 0 if it is not known |
  | | Sinser | (BU, 4) | symbol error flags |

  "* See Section on relocation ops."
  ("Sinrl1": the last glyph may be l or 1; Fig. 9 prints SINRL1, so digit one.)
- "3. If VALUE had been unable to find some of the desired information, the bit Vfbnot will be on to
  indicate this fact and the appropriate Vfb bits will be set to show what information could not be
  found."
- "4. If the using program had turned on bit Vcunfd [sic; read at zoom; elsewhere Vcundf], VALUE also
  will have made a symbol table entry for any undefined symbol encountered in the coded expression."
- "5. Valinx will be updated to locate the first bit after the coded expression."

READING on linkage: $15 holds the return (LVI, 15, $+2 puts the address of the word after the branch
in $15). For VALUE and VDIMEN the word at ($15) is the break/"not evaluated" branch and the next is
the normal return; for VSKIP and VMOVE the word at ($15) is the normal return. Fig. 10 confirms the
entry point is "c($15)vf when VALUE is entered" (see B.6). How VALUE chooses +0 or +1 (half or full
words) is not stated on these pages.

### B.3 DETAILS, verbatim (pp.56-57)

Break exit (p.56 L - R, p.57 L):
- QUOTE: "Break exit: Following a break exit, the using program may take any action it desires,
  including (perhaps): 1. changing the setting of Vcbv, Vcbsx, Vcbdim and Vcbdds to show that certain
  information is no longer desired, or 2. filling in missing information into the symbol table. If
  desired, VALUE may be used at this time to evaluate other coded expressions. Eventually, the using
  program must return to one of the locations, Vpunt or Vrtrn, after the break exit from VALUE. By a
  Vrtrn return if the situation has improved (i.e., if any of the Vcb bits have been turned on, or if
  further information has been added to the symbol table or both), then VALUE tries again where it
  previously ran into trouble. If the situation has not been improved, VALUE notes what items can no
  longer be evaluated, and then proceeds with the evaluation of the others, if any. By using the Vpunt
  return to VALUE after a break exit, the user program effectively has all the Vcb bits turned on and
  the Vrtrn procedure performed."

Undefined symbols (p.57 L):
- QUOTE: "Treatment of Undefined Symbols: The treatment is dependent on the setting of the control bit
  Vcundf. 1. If Vcundf is on when an undefined symbol is encountered, a standard symbol table entry
  will be made, and then VALUE will proceed as though it had found this entry there. Note: Even if all
  the Vcb bits are on, VALUE will still look at all symbols and make this entry when needed. 2. If
  Vcundf is off when an undefined symbol is encountered, VALUE will note what items can no longer be
  computed, and will proceed without making a break."

Example (p.57 L):
- QUOTE: "Example: The coded expression is for A+B. The using program wants all the information
  available from VALUE about the expression. Discovering that no information is in the symbol table
  for A, VALUE makes a break exit with all the Vfb and Vnb bits on. Then the program fills in values
  into the symbol table, and goes to Vrtrn. Whereupon, VALUE discovers that the situation is improved,
  but still all the desired information is not yet there. Again VALUE makes a break exit, now with the
  bits Vfbsx, Vfbdim, Vfbdds, Vnbdim, and Vnbdds on. The user program decides to ignore the dimension
  reference and returns to Vrtrn with bit Vcbdim on. Once again VALUE sees that the situation is
  improved, but still some desired information is lacking. Therefore VALUE makes a break exit with the
  bits Vfbsx, Vfbdds, Vnbsx, and Vnbdds on. On this occasion the user program returns directly back to
  Vrtrn. Seeing that there is no improvement VALUE makes note that the S/X type and dds type
  information is not available and continues through the coded expression of the B datum. VALUE makes
  no further attempt to look up S/X type information. However, if B has a dimension reference, the
  fact that A was ambiguous on this point is no longer relevant. Note: When a break is taken, it is
  not meaningful for the user program to turn off any of the Vcb bits. If the user program does this,
  his action will be ignored by VALUE."
  (Re-read at zoom: second break "Vfbsx, Vfbdim, Vfbdds, Vnbdim, and Vnbdds"; third break "Vfbsx,
  Vfbdds, Vnbsx, and Vnbdds" - both as printed.)
  READING: the second break's Vnb set (dim, dds) omits Vnbsx while the third break's includes it.
  As printed. An implementer cannot derive a Vnb rule from this example without more evidence.

The Item / Type / Purpose table (p.57 L bottom - R):

| Item | Type | Purpose |
|---|---|---|
| Valinx | XW | "Locates coded expression." |
| Vmovex | XW | "Locates the position to which the coded expression is to be moved." |
| Vcbv, Vcbsx, Vcbdim, Vcbdds | bits | "Tell VALUE what information not to attempt to get." |
| Vnbv, Vnbsx, Vnbdim, Vnbdds | bits | "Tell the using program what information could not be found in the symbol table (when a break exit is made)." |
| Vfbv, Vfbsx, Vfbdim, Vfbdds | bits | "Tell the using program what is not computable in the coded expression unless information stated by the Vnb bits is supplied (when a break exit is made)." |
| Vfbnot | bit | "Is on if anything was not found that should have been found (when the normal exit is made)." |
| Vcundf | bit | "Is on if VALUE is to enter undefined symbols in the symbol table." |

### B.4 FLOW CHART DESCRIPTION, verbatim (pp.57 R - 59 R)

- QUOTE (p.57 R): "VALUE has a 'push' type list with values being 'pushed' upwards as they are
  computed or combined. The first five words of the list are called the heading; the workspace
  follows. After the first workspace there is a sequence of headings and workspaces determined by the
  number of existence bits encountered by VALUE in the coded expression. $10 points to the location of
  the current heading; $11 points to the location in the workspace."
- Box 12 QUOTE (p.57 R): "Branch-on-zero-bit Valdfg (indicating special entry made by VDIMEN) to box
  13. The VDIMEN subroutine deals with the dimension reference statement for a user outside of VALUE."
- Box 17 QUOTE (p.57 R): "Get address of dimension reference, set control bits, and branch to VALUE to
  evaluate the coded expression. If VALUE evaluates the expression, form product of dimensions, and
  turn on completed bit; if not, go to VBREAK."
- Box 13 QUOTE (p.58 L): "Branch to MACHER subroutine if existence bit is off. (Existence bit is the
  first bit in the coded expression and must be on.)"
- Box 8 QUOTE (p.58 L): "Pick up the coded expression prefix (bits two, three, and four in the coded
  expression), space the pointer over the prefix, and branch according to the prefix."

  | Coded Expression Prefix | Type of Coded Expression |
  |---|---|
  | 000 | Normal case |
  | 001 | Special case |
  | 010 | Padded case |
  | 011 | Special signed |
  | 100 | Super special |
  | 101 | Fully evaluated |
  | 110--- | Long prefix |
  | 111 | Null |

- Box 14 QUOTE (p.58 L): "If the coded expression prefix is 110, then we must branch according to the
  next three bits (bits five, six, and seven in the expression) as we had a long prefix."

  (p.58 R) | Additional Bits in a Long Prefix | Type of Coded Expression |
  |---|---|
  | 000 | Integer |
  | 001 | Absolute |
  | 010 | Absolute integer |
  | 011 | Seventeen bit constant |

- Box 3 QUOTE (p.58 R): "Test for another datum by seeing if the no-more-datum bit was set off by
  GETFLD. If off, go to box 4. If there is another datum, turn off Vvsymb (1 - if last datum is a
  symbol) and the dimension reference flags: Vvcdr (1 - if current datum is a symbol whose dimension
  was asked for and obtained), Vvcdrl (1 - if current datum is a symbol whose dimension was asked for
  and not obtained), and Vvcdrm (1 - if current datum is a symbol whose dimension was not asked for).
  Then branch to box 9."
  ("Vvcdrl": Fig. 10 prints the field VVCDR1 with a digit; the text glyph reads as lower-case l.
  Same name; l/1 not decidable from the text face alone.)
- Boxes 4, 5 QUOTE (p.58 R - p.59 L): "If either Vcbv or Vtbv [sic: Vtbv, read at zoom] is on, we do
  not want to pute [sic] the value of the total coded expression. So we see if Vcbsx is on (indicating
  we do not want subscript/index type). If neither the value nor the S/X is desired, go to box 6. If
  either Vcbv or Vcbsx is on, set up correct table address for arithmetic (or S/X) routine. If there
  is another operator, pick up the operator code from the coded expression and get both the section
  entry and the operand type from the table. Then after picking up the datum number from the coded
  expression and getting the location of the right and/or left operand if needed, perform the
  indicated operation. When there is no other operator, go to box 6."
  READING: "Vtbv" (and "Vtbsx" in Box 6) are "trouble bits" by Box 6's own words ("set on trouble bit,
  Vtbsx"); they are not in the p.57 Item table and are not in Fig. 10. Whether Vtb* are the same
  storage as Vfb* is not stated. "If either Vcbv or Vcbsx is on, set up correct table address" reads
  oddly (one would expect "off"); as printed.
- Box 6 QUOTE (p.59 L - R): "Reset $11 (current location in workspace) with $10 (location of current
  heading). If S/X type is unknown, set on trouble bit, Vtbsx. If no values were computed, go to Vz.
  Mark index as existing if Vvspx is on. If Vvspx is off and Vvabs is on (indicating result is to be
  made), set signs of the integer and of the bit values to plus, and continue. If the result is not to
  be made an integer, i.e., Vvint is off, then exit; otherwise combine integer and bit values, and set
  bit value to zero. Skip the pointer over the padding in the coded expression. Put integer and bit
  values into VALUE's output words, Sini and Sinb."
  ("(indicating result is to be made)" is as printed; a word such as "absolute" appears to be
  missing. "Vz" is a label with no other mention on these pages.)
- Box 9 QUOTE (p.59 R): "Pick up datum prefix (usually bits five, six, and seven in the coded
  expression), space the pointer over the prefix and branch according to the prefix."

  | Datum Prefix | Type of Datum |
  |---|---|
  | 100 | Symbol |
  | 101 | Subexpression |
  | 110 | Absolute |
  | 111-- | Long |
  | 11100 | System symbol |

**The prose stops here (p.59 R).** Chart RD boxes with NO descriptive sentence anywhere on pp.55-59:
1, 2, 7, 10, 11, 15, 16, 18, 19, 20, 21, 22, 23, 24 and every unnumbered box (SPECIAL INDEX BIT TO 1;
VA2 PADDING BIT TO 1; SET ZERO IN LIST; VA3; VA5; VA63; SET INT BIT TO 1; VA61; SET ABSOLUTE BIT TO 1;
PUT 24 BITS IN LIST AS INTEGER VALUE; VSS; SEARCH; the recursive VALUE). They are chart-only.

### B.5 Chart RD (p.54), "VALUE", box by box

| Box | Label | CHART text | Exits as drawn |
|---|---|---|---|
| 1 | | VALUE / EVALUATE A CODED EXPRESSION (subroutine box) | -> 7 |
| 7 | | INITIALIZE | -> 12 |
| 12 | | PROCESSING DIMENSION | YES -> 17; NO (down) -> 13 |
| 17 | | FORM PRODUCT IF POSSIBLE | right -> a junction; from the junction down -> EXIT terminal. (300-dpi trace: the arrowhead on the junction-to-21 segment sits at the junction end, so that segment is 21 -> junction, not 17 -> 21.) |
| 21 | | MACHER / ERROR ROUTINE (subroutine box) | entered from below (13 NO); left -> the same junction -> EXIT |
| 13 | | EXISTENCE BIT ON | YES (left, up, over) -> top of 8; NO (right, up, right, up) -> 21 |
| 8 | VA | BRANCH ACCORDING TO PREFIX | exits labelled under/beside the box: "001" (left) -> SPECIAL INDEX BIT TO 1; "000 OR 100" -> down to the VB junction -> 3; "010" -> VA2; "110" -> 14 (VA6); "111" -> SET ZERO IN LIST; "011" -> VA3; "101" (right side) -> VA5 |
| (unnumbered) | | SPECIAL INDEX BIT TO 1 | down -> 2 |
| 2 | | SPACE VI BY 3 [uncertain: "VI"; could be V1] | down -> junction (connector 40, label VB) -> 3 |
| (unnumbered) | VA2 | PADDING BIT TO 1 ("TC 1" as printed, = TO 1) | left -> joins the 000/100 line -> VB -> 3 |
| 14 | VA6 | BRANCH ACCORDING TO NEXT 3 BITS | "000" -> SET INT BIT TO 1; "010" -> VA61; "001" -> SET ABSOLUTE BIT TO 1; "011" (right side) -> VA63 |
| (unnumbered) | | SET INT BIT TO 1 | down -> common line -> (left, up) joins the 000/100 line -> VB -> 3 |
| (unnumbered) | VA61 | SET ABS AND INTEGER BIT TO 1 | same common line |
| (unnumbered) | | SET ABSOLUTE BIT TO 1 | same common line |
| (unnumbered) | VA63 | SET 17 BIT CONSTANT IN LIST | right -> 23 |
| (unnumbered) | | SET ZERO IN LIST (prefix 111) | down, right -> 23 |
| (unnumbered) | VA3 | PUT NEXT 25 BITS IN LIST AS B VALUE (prefix 011) | down -> 23 |
| 23 | | SPACE OVER PADDING | -> EXIT |
| (unnumbered) | VA5 | PUT NEXT 2 WORDS IN LIST (prefix 101) | right -> 22 |
| 22 | | SPACE INDEX 2 WORDS | -> EXIT |
| 3 | VB | ANOTHER DATUM (entered at connector 40) | YES (right) -> 9; NO (down) -> 4 |
| 4 | | ANY OPERATORS | NO (left, down) -> 6; YES (down) -> 5 |
| 5 | | COMBINE DATA ACCORDING TO OPERATORS | down -> 6 |
| 6 | | "MACHER" in the subroutine strip [sic, read at zoom] / PUT RESULTS IN RESULT INDEX WORDS | down -> EXIT |
| 9 | | BRANCH ACCORDING TO NEXT 3 BITS | "100" -> SEARCH; "101" -> VALUE (sub expression); "110" -> PUT 24 BITS IN LIST AS INTEGER VALUE; "111" -> VSS |
| (unnumbered) | | SEARCH / LOOK UP SYMBOL (subroutine box) | down -> 10 |
| 10 | | IN SYMBOL TABLE | NO (right) -> 15; YES (down, right) -> 16 |
| 15 | | OK TO ENTER IN TABLE | YES -> 19; NO -> EXIT terminal |
| 19 | | ADDORD / MAKE ENTRY (subroutine box) | down, left -> joins line into 16 |
| 16 | | REQUESTED INFO ESTABLISHED | YES -> 20; NO (left) -> 11 |
| 11 | | VBREAK / GIVE USER OPPORTUNITY TO FIX SYMBOL (subroutine box) | left, up -> back to the top of 10 |
| 20 | | PUT INFO IN LIST | right -> connector 40 |
| (unnumbered) | | VALUE / EVALUATE SUB EXPRESSION (subroutine box) | right -> 18 |
| 18 | | PUT VALUE IN WORK AREA | right -> connector 40 |
| (unnumbered) | | PUT 24 BITS IN LIST AS INTEGER VALUE | right -> connector 40 |
| (unnumbered) | VSS | PUT SYSTEM SYMBOL VALUE IN LIST | down -> 24 |
| 24 | | PUT DDS IN LIST | down -> connector 40 |

READING on the chart:
- Box 6's strip "MACHER" sits over a box whose body is the normal result path; box 21 is the real
  MACHER. Probably a chart-drawing slip; record as printed.
- Box 15 NO -> EXIT is drawn. The text (p.57 L, Vcundf off) says VALUE "will note what items can no
  longer be computed, and will proceed without making a break". The two do not agree as drawn; the
  text is the fuller statement. [open]
- Box 11 VBREAK returns above box 10 ("IN SYMBOL TABLE"), i.e. after the user's fix the symbol is
  looked at again; this matches Vrtrn ("tries again where it previously ran into trouble").
- Chart exits "000 OR 100" both go to box 3 directly: the chart draws nothing different for "Normal
  case" and "Super special". 001 "Special case" sets a "special index bit" and spaces by 3 more.
- Prefix 101 "Fully evaluated": "PUT NEXT 2 WORDS IN LIST", "SPACE INDEX 2 WORDS", EXIT, so a fully
  evaluated expression is the prefix followed by two words (presumably Fig. 9's two output words).

### B.6 Fig. 9 (p.58), "Format of VALUE's Output (without Relocation Fields)", read at zoom

Word 1: bit scale marks 0, 24, 29, 31, 32, 56, 57, 63. "B Value" under bits 0-24; "I Value" under
32-56. Vertical names above: SINB at 0; SINSX, SINRL1, SINRL2 at about 29-31; SINI at 32.
Word 2: marks 0, 24, 28, 31, 32, 56, 57, 59, 63; a "0" drawn in the last bit cell. "DDS Reference"
under 0-24; "DIM Reference" under 32-56. Vertical names: SINDDS at 0; SINM about 25; SINX about 28;
SINDIM at 32; SINMQ, SINXQ, SINSER at about 56-59.

Printed table under the figure:
| name | dds | meaning |   | name | dds | meaning |
|---|---|---|---|---|---|---|
| SINDDS | (BU,25) | DDS Reference | | SINSER | (BU,4) | Symbol Error Flags |
| SINM | (BU,3) | Mode Bits | | SINB | (BU,25) | B Value |
| SINX | (BU,4) | Index | | SINSX | (BU,1) | Subscript/Index |
| SINDIM | (BU,25) | Dimension Reference | | SINRL1 | (BU,1) | Relocation Flag 1 |
| SINMQ | (BU,1) | Mode Bits Given | | SINRL2 | (BU,1) | Relocation Flag 2 |
| SINXQ | (BU,1) | Index Given | | SINI | (BU,25) | I Value |

Disagreements between p.56's table and Fig. 9, both as printed:
- Sinsx: (BU, 2) with codes 00/10/01/11 on p.56; SINSX (BU,1) in Fig. 9.
- Sini, Sinb, Sindim, Sindds: (B, 25) on p.56; (BU,25) in Fig. 9.
- p.56 lists Sindsq (dds reference known) and no mode bits; Fig. 9 lists SINM, SINMQ and no SINDSQ.
- Exact bit positions of SINSX/SINRL1/SINRL2 (three names over marks 29..31) and of
  SINMQ/SINXQ/SINSER (over 56..59, SINSER 4 bits to 62, bit 63 drawn "0") are my reading of the tick
  marks: SINSX 29, SINRL1 30, SINRL2 31; SINM 25-27, SINX 28-31; SINMQ 56, SINXQ 57, SINSER 59-62
  with 58 unassigned. [uncertain: the ticks are fine; verify against the ink before fixing layouts.]
- A third output word exists with relocation: Fig. 18 p.185 "Format of the Third Word in VALUE's
  Output": SINCOM bits 0-17 ("Number of named common."), SINUA bit 18 ("0-if at exit from VALUE, the
  address is to be relocated as a lower address. 1-if ... as an upper address."), "19-63 Not used."

### B.7 Fig. 10 (p.60), "Format of VALUE's Internal Tables", read at zoom

HEADING preceding a work area (four words drawn; the fifth is Fig. 19 p.186):
- Word 1: VVE at 0, "Entry Point", bracketed note under it "[c ($15)vf when VALUE is entered]" (the
  opening glyph is a bracket followed by "c"; "vf" is a subscript: contents of $15's value field);
  marks 24 25 26 27 28: cells a, b, c = VVCDR, VVCDR1, VVCDRM; then VCH [sic, one V] "Storage for VCB
  Bits" (bits 28-31 by the marks); VVBRK at 32 "Break Point" (32-56); VVSYMB at 57, cell d; zeros to 63.
- Word 2: VVHUP at 0 "Next Heading Above"; marks 24 25 26 27: cells e, f, g = VVPAD, VVINT, VVABS;
  zeros 28-31; VVHDN at 32 "Next Heading Below"; zeros 57-63.
- Word 3: VVINX at 0 "Input Index at External Break Only"; marks 24 25 26 27: cells h, i, j = VVSPX,
  VVSUBQ, VVTOP; zeros; VVSYX at 32 "Location of Symbol Table Entry in Error"; zeros 57-63.
- Word 4: VVDDS at 0 "Dds Reference Address"; a "0" cell at 24/25; marks 26 27 28: cells k, l =
  VVXQ, VVMQ; VVX "Index" (28-31); VVDIM at 32 "Dimension Reference Address"; marks 56 57 58 59:
  cells m, n = VINRL1, VINRL2 [sic, VIN not VVN]; VVSER "Symbol Error Flags" (59-62); "0" at 63.
- Word 5 (Fig. 19 p.186, "Format of the Fifth Word in VALUE's Heading"): VVCOM 0-17, VINUA 18, zeros
  19-63; "The bit assignment is the same as that in the third word in VALUE's output."

DATUM in work area (two words): "I-Value (Normalized floating point)" and "B-Value (normalized
floating point)", each Exponent 0-11, Fraction 12-59, marks 59 60 63, a "0" in the last cell.
SUBSCRIPT in work area (one word): "Subscript (normalized floating point)", same layout, a "1" in
the last cell.
READING: the last bit (63) appears to tell a datum word (0) from a subscript word (1).

Legend (verbatim): "a. dimension requested and obtained / b. dimension requested and not obtained /
c. dimension not requested / d. last datum symbol / e. padding / f. result integer / g. result
absolute / h. result index / i. datum with subscripts / j. entry from outside / k. index / l. mode
known / m. relocation / n. relocation". A stray fragment "ABLE!" [uncertain] is printed after item b
(looks like print-through; not part of the legend). Footer: "See section on relocation ops for format
of fifth word in heading."

READING: legend/letter pairing gives VVSPX = h "result index", VVSUBQ = i "datum with subscripts",
VVTOP = j "entry from outside", VVPAD = e, VVINT = f, VVABS = g, VVXQ = k "index", VVMQ = l "mode
known". This agrees with Box 6's use of Vvspx, Vvabs, Vvint.

### B.8 VALUE: names and where each is defined

| Name | Kind | Defined / described |
|---|---|---|
| Valinx, Vmovex | index words (XW) | p.55, p.57 table |
| Vcbv/Vcbsx/Vcbdim/Vcbdds | control bits in | p.55 R, p.57 R; stored per heading in "VCH Storage for VCB Bits" Fig. 10 |
| Vnbv.., Vfbv.., Vfbnot | bits out | pp.55-57 |
| Vcundf | control bit | p.57 L/R (also printed "Vcunfd" p.56 L) |
| Vpunt, Vrtrn | re-entry locations after a break | p.56 R, p.57 L |
| VBREAK / Vbreak | break routine (chart box 11; "returns through Vbreak" p.135) | Chart RD; p.57 R Box 17; p.135 L |
| Valdfg | bit, "special entry made by VDIMEN" | p.57 R Box 12 |
| Vtbv, Vtbsx | "trouble bit" | p.58 R, p.59 L (not in any table) |
| Vz | label | p.59 L Box 6 |
| VA, VA2, VA3, VA5, VA6, VA61, VA63, VB, VSS | chart labels | Chart RD |
| Vvsymb, Vvcdr, Vvcdr1, Vvcdrm, Vvspx, Vvabs, Vvint, + VVE, VVBRK, VVHUP, VVHDN, VVPAD, VVINX, VVSUBQ, VVTOP, VVSYX, VVDDS, VVXQ, VVMQ, VVX, VVDIM, VINRL1, VINRL2, VVSER, VCH, VVCOM, VINUA | heading fields | Fig. 10 p.60, Fig. 19 p.186; p.58 R, p.59 L |
| Sini, Sinb, Sinx, Sinxq, Sinrl1, Sinrl2, Sinsx, Sindim, Sindds, Sindsq, Sinser, SINM, SINMQ, SINCOM, SINUA | output words | p.56, Fig. 9 p.58, Fig. 18 p.185 |
| $10 | "location of the current heading" | p.57 R; p.175 "Used by VALUE" |
| $11 | "the location in the workspace" | p.57 R; p.175 |
| $15 | return linkage (value field) | p.55; Fig. 10; p.175 |
| $1 | VDIMEN's in/out pointer; at a break "the function part of the symbol table entry causing the trouble" | p.55 L, p.55 R |
| MACHER | "SIC, Machez; B, MACHER" ... "The location to be inserted in the message is obtained from the location, Machez." ... "when UITER uses MACHER, MACHER marks the vle as completed." | p.173 L |
| SEARCH, ADDORD | TABMAN, pp.47-48 (not re-read here) | Chart RD boxes after 9, 19 |

Error messages raised by VALUE: none numbered on pp.54-60. Only MACHER (box 21, entered from 13 NO;
see B.5: no line from 17 into 21 is drawn). The list on p.177 gives VALUE messages 69-78 and 86
(Part G).

---------------------------------------------------------------------------------------------------
## PART C. UITER (text pp.135, 137; Chart GB p.136)

### C.1 Linkage and details, verbatim (p.135 L)

- Section head: "MAJOR LOGIC AREA IN THE BETWEEN-PASSES PHASES OF STRAP II"; index line: "UITER /
  ITERate over the symbol table / Iterates over the symbol table to establish a data description and
  value for each symbol in the table."
- LINKAGE QUOTE: "UITER inspects the symbol table twice, once between the end of Pass 1 and the
  beginning of Pass 2a, and again between the end of Pass 2a and the beginning of Pass 2b. Each time
  it is entered with a--B, UITER."
  (That is the whole linkage: a plain branch; no return register is given.)
- DETAILS QUOTE: "UITER iterates over the symbol table to establish a data description and value for
  each symbol. UITER also computes the memory bounds of the program being assembled."
- QUOTE: "UITER maintains a pushdown type table at the symbolic location, Utab. The 64 bit entry in
  the Utab table contains: in positions 0-23 the location in the symbol table of the problem symbol
  and in positions 32-56 the level in the symbolic chain. An entry in the Utab table is made each time
  VALUE returns through Vbreak while UITER is processing a SYN chain. In coordination with the Utab
  table, UITER uses three index registers which have the following significance:"

  | Symbolic | Field | Contents |
  |---|---|---|
  | U3 ($3) | Value | "The location in the symbol table of the base symbol in the chain" |
  | U4 ($4) | Value | "The location of the latest entry made in the Utab table." |
  | | Count | "The current level of evaluation." |
  | U9 ($5) | Value | "The location in the symbol table of the symbol currently being evaluated by UITER." |

  ("U9 ($5)" is as printed, read at zoom: the symbolic name says 9 and the register says $5.)
- FLOW CHART DESCRIPTION QUOTE: "After initialization we determine whether or not we are in Pass 1.
  (Np2ind is zero if we are in Pass 1.)"  Footnote: "*Flow chart of UITER on next page".

From p.32 R (see A.5 Box 1) and p.35 R (Box 24): the push-down list, "A non-P mode symbol initiates a
new level", the symbol counter for the error message procedure, marking undefined symbols in a SYN
chain, circular / contagious flags, zero for the base symbol of a circular chain, the indicator that
lets VALUE make undefined entries, Uhl and the hi-lo entries, return with Np2ind off and Fpass3 on.
From p.35 R (SYN in Pass 2a): "another try to get the value of the SYN by using a section of UITER."
From p.173 R: "Fuiter = 1, when the iteration between Pass 1 and Pass 2a is in process. when the
iteration between Pass 2a and Pass 2b is in process."; "The Symbol counter during the UITER
subroutine holds the address of the function portion of the variable length entry part of the symbol
table entry currently being analyzed by UITER"; "when UITER uses MACHER, MACHER marks the vle as
completed." (p.173 L)

### C.2 Chart GB (p.136), "UITER", box by box

Traced at 300 dpi. In this chart the arrowhead "X" is printed at the DESTINATION end of a line and
the YES/NO word at the SOURCE vertex; several lines run right-to-left, so the direction below is
taken from where the X sits, not from left-to-right order. Circles 40, 41, 42, 43 are on-page
connectors; each number appears once as a "go to" circle (arrowheads into it) and once as a landing
(a line leaving it into a box).

| Box | Label | CHART text | Exits as drawn |
|---|---|---|---|
| 1 | | UITER / ITERATION THROUGH THE SYMBOL TABLE (subroutine box) | -> 2 |
| 2 | | INITIALIZE | -> 3 |
| 3 | | ERRIN / INITIALIZE ERROR MESSAGE ROUTINE (subroutine box) | "PASS1" (right) -> the long vertical line that ends at 7; "PASS2" (down) -> 4 |
| 4 | UHL | ANEXT / GET HI LO ENTRIES IN VLE (subroutine box) | "NO MORE" (right) -> the long vertical line -> 7; "MORE" (down) -> 5 |
| 5 | | ESTABLISH HI LO VALUES | left, up -> back into 4 |
| 6 | | MACHER / ERROR ROUTINE (subroutine box) | entered from below (landing 41); right -> the long vertical line -> 7 |
| 7 | UGOA | ANEXT / GET SYMBOL TABLE ENTRY (subroutine box) | "NO MORE" (right) -> 15; "MORE" (down) -> 8 |
| 15 | | EXIT | |
| 8 | | SPACE TO LOCATION OF FUNCTION | down -> 9 |
| 9 | | EVERYTHING DEFINED AND COMPUTED | YES (down, left) -> the long vertical line -> 7; NO (right, up, right) -> 16 |
| 16 | | DDS REFERENCE ADDR DECIDED | NO (right) -> 23; YES (down) -> 17 |
| 23 | UDDS | TRY TO ESTABLISH DDS REFERENCE ADDRESS | right -> 31 |
| 31 | | DDS REFERENCE ADDR DECIDED | YES (up) -> circle 40 (-> 10); NO (down) -> circle 41 (-> 6) |
| 17 | | SHOULD DDS REFERENCE ADDR BE USED | YES (left, long line down) -> joins landing 40 -> 10; NO (right) -> 24 |
| 24 | | MODE KNOWN | NO (right) -> circle 41 (-> 6); YES (down) -> 25 |
| 25 | | FIELD LENGTH ESTABLISHED | YES (left, up, over) -> top of 18; NO (right) -> 32 |
| 18 | | SYMBOLIC FIELD LENGTH EXIST | YES (down) -> 19; NO (right, down) -> joins 19's line -> circle 42 (-> 27). Also entered at its left side from 20's "F. L. ESTAB" line |
| 19 | | VSKIP / SPACE OVER CODED EXPRESSION (subroutine box) | right -> circle 42 (-> 27) |
| 32 | | SYMBOLIC FIELD LENGTH EXIST | YES (right, down) -> 33; NO (down, left) -> top of circle 42 (-> 27) |
| 33 | UEVALA | GET VALUE OF SYMBOLIC ENTRY | down -> 34 |
| 34 | | REAL VALUE COMPUTED AND ENTERED | YES (down, left) -> 20 (enters 20 from below); NO (left) -> 26 |
| 26 | | EVERYTHING DEFINED AND COMPUTED | YES (up) -> bottom of circle 42 (-> 27); NO (left) -> 20 |
| 20 | | KAMMS / ADD AND COMPARE RESULTS (subroutine box) | "F.L.NOT. ESTAB" (up, right) -> joins the line into the bottom of circle 42 (-> 27); "F. L. ESTAB" (left, up) -> left side of 18 |
| 27 | UBS1 [first glyph unclear: prints like "LBS1"; U by the U-prefix rule p.202] | BYTE SIZE ESTABLISHED (entered from landing 42 at its right) | YES (left) -> 21; NO (down) -> 28 |
| 21 | | SPACE OVER CODED EXPR IF SYMBOLIC BYTE SIZE EXISTS | down -> top of circle 43 (-> 30). Also entered at its left side from 29's "B.S. ESTAB" line |
| 28 | | SYMBOLIC BYTE SIZE EXIST | NO (left) -> circle 43 (-> 30); YES (right) -> 35 |
| 35 | UEVALA | GET VALUE OF SYMBOLIC ENTRY | right, down -> 36 |
| 36 | | REAL VALUE COMPUTED AND ENTERED | YES (left) -> 29; NO (up, left) -> the line into the bottom of circle 43 (-> 30) |
| 29 | | KAMMS / ADD AND COMPARE RESULTS (subroutine box) | "B.S.NOT.ESTAB" (up) -> joins the line into the bottom of circle 43 (-> 30); "B.S. ESTAB" (left, long line left and up) -> left side of 21 |
| 30 | UVALC | RESTORE ORIGINAL ENTRY TO LOC IN U3 (entered from landing 43 at its right) | left -> 22 |
| 22 | | EVERYTHING DEFINED AND COMPUTED | YES (up, left) -> bottom of circle 40 (-> 10); NO (left) -> 14 |
| 14 | | PASS 2 | "NO" (up) -> bottom of circle 40 (-> 10); YES (left) -> circle 41 (-> 6) |
| 10 | UVAL | REAL VALUE COMPUTED AND ENTERED (entered from landing 40 above it, joined by 17 YES) | YES (left) -> the long vertical line -> 7; NO (down) -> 11 |
| 11 | | TRY TO ESTABLISH A VALUE | down -> 12 |
| 12 | | REAL VALUE COMPUTED AND ENTERED | YES (left) -> the long vertical line -> 7; NO (down) -> 13 |
| 13 | | PASS 2 | NO (left) -> the long vertical line -> 7; YES (down, left, up) -> landing 41 -> 6 MACHER |

READING, the chart as one flow (mine; each arrow is in the table above):
7 ANEXT -> 8 -> 9 (Zst0 on: next symbol). Else dds reference: 16 decided? no -> 23 try -> 31 (still
not decided -> MACHER 6; decided -> value, 10). Decided -> 17 use the dds reference? yes -> value
(10). No -> 24 mode known? no -> MACHER. Yes -> field length: 25 established? yes -> 18 (symbolic
one exists? VSKIP it) -> 27. Not established -> 32 symbolic one exists? no -> 27; yes -> 33 evaluate
-> 34 real value? yes -> 20 Kamms (established -> 18 -> VSKIP -> 27; not -> 27); no -> 26 (Zst0
test-and-set: YES -> 27, NO -> 20 Kamms). Byte size: 27 established? yes -> 21 (space over) -> 30;
no -> 28 symbolic one exists? no -> 30; yes -> 35 evaluate -> 36 real value? yes -> 29 Kamms
(established -> 21 -> 30; not -> 30); no -> 30. 30 "restore original entry to loc in U3" -> 22
(Zst0 test-and-set: YES -> 10; NO -> 14: Pass 2? no -> 10, yes -> MACHER). Value: 10 real value?
yes -> next symbol; no -> 11 try -> 12 real value? yes -> next; no -> 13 Pass 2? no -> next (left
for the second iteration), yes -> MACHER -> next symbol.
Things in this flow that look odd and are as drawn, not smoothed: 26 NO -> 20 (Kamms reached with no
real value); 31 NO -> MACHER in both passes (no PASS 2 test on that path); 24 NO -> MACHER likewise.
The parent should confirm these three arrows in the ink (p.136, middle and top right).

### C.3 The prose, box by box (pp.135 R, 137), verbatim, in the order printed

- "Boxes 7, 15 (after Pass 1)" QUOTE (p.135 R): "Get each symbol table entry by branching to ANEXT.
  When there are no more symbol table entries, leave UITER."
- "Box 8" QUOTE: "Space to location of function in order to investigate the entry. The delete mark,
  the field indicating the length of the entry, the ID field, the field indicating the length of the
  remainder of the argument, and the remainder of the argument precede the function field in the vle."
- "Box 9" QUOTE: "Branch-on-bit-and-set-to-one Zst0 (everything defined and computed) and then go to
  ANEXT to get the next symbol table entry. By "everything" it is meant value, dds, and dimension
  properties."
- "Boxes 16, 31" QUOTE: "Branch-on-zero-bit Zst3 (existence of dds reference has been decided). By dds
  reference address, it is meant a location to find the address of a dds."
- "Box 23" QUOTE: "Test for circular value by seeing if Zst17 (processing bit for mode) is on. If
  value is circular, give reference address of zero. Branch to VALUE subroutine to establish dds
  reference address."
- "Box 17" QUOTE: "Branch-on-bit Zst32 (use dds reference address) to box 10. The dds reference
  address is only used if the dds is implicit."
- "Box 24" QUOTE (p.137 L): "Branch-on-bit Zst10 (mode known) to box 25."
- "Boxes 10, 12" QUOTE: "Branch-on-bit Zst26 (real value computed and entered). By real value it is
  meant that we know the value of a symbol."
- "Box 11" QUOTE: "Test for circular value. If circular value, assign a value of zero; otherwise
  branch to VALUE to attempt to establish a value. In the case of a DR whose dimension product has not
  yet been formed, branch to VDIMEN. If the product of dimensions is not formed by VDIMEN, turn off
  Zst0, and continue."
- "Box 13" QUOTE: "Branch-on-zero-bit Np2ind (Pass 2 indicator) to box 7. The value should be
  established by the end of Pass 2a; if it is not, branch to MACHER (error subroutine)."
- "Box 25" QUOTE: "Branch-on-bit Zst11 (field length has been established) to box 18."
- "Box 32" QUOTE: "Branch-on-bit Zst12 (symbolic field length exists) to box 33."
- "Box 18" QUOTE: "Branch-on-zero-bit Zst12 to box 27."
- "Box 19" QUOTE: "Branch to VSKIP subroutine to skip the pointer over the coded expression for the
  field length because the field length has already been established."
- "Box 20" QUOTE: "Branch to Kamms procedure in DECODE to test whether the field length was properly
  specified, i.e., to see if it is not more than 64 bits and not in bit style. An illegal condition
  causes both an error message to be given and the field length to be truncated. (Bit and integer
  values are combined.)"
- "Box 27" [first of two headings so numbered] QUOTE (p.137 R): "Branch-on-bit-and-set-to-one Zst0
  (everything defined and computed) to box 27."
- "Boxes 33 and 34" QUOTE: "Described under boxes 11 and 10, respectively."
- "Box 27" [second] QUOTE: "Branch-on-bit Zst14 (byte size has been established) to box 27."
- "Box 28" QUOTE: "Branch-on-bit Zst15 (symbolic byte size exists) to box 35."
- "Box 21" QUOTE: "Branch to box 30 if symbolic byte size does not exist. If symbolic byte size does
  exist, branch to VSKIP subroutine to skip the pointer over the coded expression for the byte size
  because of [sic] the byte size has already been established."
- "Boxes 35 and 36" QUOTE: "Described under boxes 11 and 10, respectively."
- "Box 29" QUOTE: "Branch to Kamms procedure in DECODE to test whether the byte size was properly
  specified, i.e., to see if it is not more than 8 bits and not in bit style. An illegal condition
  causes both an error message and the byte size to be truncated. (Bit and integer values are
  combined.)"
- "Box 22" QUOTE: "Branch-on-bit-and-set-to-one Zst0 (described under box 9) to box 10."
- "Box 14" QUOTE: "Branch-on-zero-bit Np2ind (Pass 2 indicator) to box 10" (no full stop printed).
- "Boxes 4, 5, (after Pass 2a)" QUOTE: "Branch to ANEXT subroutine to get each hi-lo entry made by
  Pass 2 in the vle table; establish the memory bounds of the assembly."

p.137 against Chart GB (as printed; do not normalise in a transcription):
- Two headings "Box 27". The first ("Branch-on-bit-and-set-to-one Zst0 (everything defined and
  computed) to box 27") is chart box 26 by its test, and the chart's 26 YES does go to 27 (through
  connector 42): the HEADING is the misprint (26), the target is right.
- The second "Box 27" ("Branch-on-bit Zst14 (byte size has been established) to box 27") is chart
  box 27 by its test; the chart's 27 YES goes to box 21: the TARGET is the misprint.
- "Box 18: Branch-on-zero-bit Zst12 to box 27" agrees with the chart (18 NO -> 42 -> 27).
- "Box 21: Branch to box 30 if symbolic byte size does not exist" agrees (21 -> 43 -> 30).
- "Box 22 ... to box 10", "Box 14 ... to box 10", "Box 13 ... to box 7", "Box 17 ... to box 10",
  "Box 24 ... to box 25", "Box 25 ... to box 18", "Box 32 ... to box 33", "Box 28 ... to box 35" all
  agree with the chart.
- No text for boxes 1, 2, 3, 6, 30, and none for 26 under its own number. Box 30's chart text
  ("RESTORE ORIGINAL ENTRY TO LOC IN U3") is the only statement of what UVALC does. Nothing on
  pp.135-137 says where a Utab entry is pushed or popped in terms of boxes; p.135 L says only "each
  time VALUE returns through Vbreak while UITER is processing a SYN chain".
- "Np2ind (Pass 2 indicator)" here, "The Pass 2a indicator, Np2ind" on p.33 L. Box 3's chart exits
  are "PASS1"/"PASS2".

### C.4 UITER: names and where defined

| Name | What | Where |
|---|---|---|
| Utab | pushdown table; entry: 0-23 location of the problem symbol, 32-56 level | p.135 L |
| U3 ($3), U4 ($4) value+count, U9 ($5) | index registers | p.135 L |
| Np2ind | zero in "Pass 1" (i.e. the first iteration) | p.135 L, p.137 |
| Uhl | label of box 4; "the Uhl subroutine which inspects each hi-lo entry in the vle table" | Chart GB; p.35 R |
| UGOA (7), UVAL (10), UDDS (23), UEVALA (33, 35), UBS1? (27), UVALC (30) | chart labels | Chart GB |
| Zst0 | "everything defined and computed" (value, dds, dimension) | p.135 R |
| Zst3 | "existence of dds reference has been decided" | p.135 R |
| Zst10 | "mode known" | p.137 L |
| Zst11 | "field length has been established" | p.137 L |
| Zst12 | "symbolic field length exists" | p.137 L |
| Zst14 | "byte size has been established" | p.137 R |
| Zst15 | "symbolic byte size exists" | p.137 R |
| Zst17 | "processing bit for mode" (on = circular) | p.135 R |
| Zst26 | "real value computed and entered" | p.137 L |
| Zst32 | "use dds reference address" | p.135 R |
| (other Zst named elsewhere) | Zst13, Zst35, Zst36, Zstcom, Zstcon (relocation, p.185); Zst24 (p.140: "Turn the Zst24 of the symbol table entry to mark as used"); Zstcnt (p.173 R: number associated with each name) | pp.140, 173, 185 |
| ANEXT, VALUE, VDIMEN, VSKIP, MACHER, ERRIN, Kamms (in DECODE) | subroutines used | Chart GB, p.137 |

The layout of the function part (which bit is Zst-n, where the value sits) is NOT given on any page
read: Fig. 22 p.191 says only "Function (Format of function defined by the ZST...bits)" "231
minimum"; Appendix D p.202: "ZST... SYN's defining the relative locations in the function portion of
the variable length entry part of a symbol table entry". The names read as relative bit numbers
(Zst0, Zst3, ...Zst36) but nothing printed says so.

Error messages raised by UITER: none numbered. "an error message" from Kamms (boxes 20, 29), MACHER
(boxes 6/13). The "symbol error flags" (circular, contagious, undefined) are set, not messages.

---------------------------------------------------------------------------------------------------
## PART D. Definitions read elsewhere, bounded (for the "where defined" column)

**Fig. 20 p.189**, "Format of the Fixed Portion of an Expanded Instruction Unit (not including
relocation fields)" - control word and first three words re-read at zoom; ZICDID, ZIOPX, ZIOTPT and
the legend at page resolution:
- Control word: "Address of Next Word" 0-17; zeros from 18; cells a, b at about 25, 26, then a 0;
  "Number of Words in Unit" 28-45; "Address of Next Control Word" 46-63.
- Word: ZIADAB at 0 (0-24) "Absolute Portion of the Location Counter is Put here in Pass 2"; ZILBO at
  25 (25-31) "Length of Binary Output"; ZIADSY at 32 (32-56) "Symbolic Portion of the Location Counter
  is Put here on [sic] Pass 2"; ZIFNME, ZIFP2, ZIFBO, ZIFDD over cells c, d, e, f (scale marks 56, 58,
  60; the host takes them as bits 57, 58, 59, 60, `unit.py:20-23`); zeros to 63.
- Word: ZILCFD at 0 "Length of Coded Fields"; ZIFDDS, ZIFPMN, ZIFFLF, ZIFSFL, ZIFBSF, ZIFSBS, ZIFDSF
  over cells g, h, i, j, k, l, m (marks 24, 26, 28, 30, 32: bits 25-31); ZILSST at 32 "Length of
  Symbolic Statement" (32-56); ZINXBO at 57 "No. of Extra Words of Binary Output" (57-63).
- Word: ZILPMS at 0 "Length of P-Mode Symbol"; ZIFALL at 25 (cell n), then two 0 cells; ZINAME at 28
  "Name Check Digit" (28-31); ZINFLD at 32 "Number of Fields" (32-49); ZIDDS at 50 "Dds Information"
  (50-62); mark "62 63".
- Word: ZICDID "Card ID in Absolute Form".
- Word: ZIOPX 0-24 "Location of Operation Question Bits"; "Error Flags" 25-29; cell p at 30.
- Word: ZIOTPT "Binary Output" (0-31 and 32-63 marked).
- Legend: "a. on if last control word / b. on if last control word in file / c. name / d. DECODE gets
  unit / e. binary output / f. DD / g. explicit dds / h. P-mode / i. f.l. filled in / j. symbolic f.l.
  / k. b.s. filled in / l. symbolic b.s. / m. dds filled in / n. nothing left for DECODE / p. suppress
  e.m."
  READING: ZIFP2 = d "DECODE gets unit"; ZIFBO = e "binary output"; ZIFALL = n "nothing left for
  DECODE"; so p.32's "Zifbo, Zifall, and Zifp2" are these three flags, and Zilbo (p.34) is ZILBO.
- Fig. 17 p.184: one more word, ZICOMM (relocation), "Format of the Last Word in the Fixed Position
  [sic] of a Unit".

**Fig. 21 p.190** (dictionary part): symbol table entry = delete bit, vle bit, 64 "First Eight
Characters of the Name", 25 "Signed Address of its vle"; special-symbol entry: "2^8-1", "n", "0" in
the 64 ("n = 0 for the $ itself"), captioned "Internal STRAP II Special Symbolic Counter Symbol".

**Fig. 22 p.191** (vle table): symbol vle = delete indicator, 13 "Length of this Entire vle", 6 ID
"S" (A6), 12 "Length of the Rest, if any, of the Name", 8n rest, "231 minimum" Function; special
symbol: ID "Y", 12-bit field 0, function "231 minimum"; dimension entry ID "D", 5-bit field then a
"1" "Evaluation Indicator", then "n1, n1 x n2, n1 x n2 x n3" "Products of Dimensions"; hi-lo entry:
13, 6 ID "H", 25 "Signed Value from Absolute Counter", 25 "Signed Value from Symbolic Counter".

**p.175**, "Index Register Assignment in STRAP II", Pass 2 column: 0 "Value field used for calling
sequence reads in TABMAN; refill field used during the execution of a RNX instruction."; 1 "- - -";
2 "Used in the RNX instruction."; 3 "Address of the unit being processed."; 4 "Absolute portion of
the location counter."; 5 "Address of the question bits for instruction being processed."; 6
"Symbolic portion of the location counter (i.e., current 3 character STRAP II special symbol)."; 7,
8, 9 "Used randomly."; 10, 11 "Used by VALUE."; 12 "Used by NAMEIN."; 13 "Used by OUTPUT."; 14 "Used
by NAMEIN."; 15 "Value field used for subroutine linkages; refill field used to point to the table of
exits for maskable interrupts."
(p.175 text: "index registers other than $7, $8, and $9 are at the special disposal of specific
routines ... not used generally in STRAP II unless their contents are saved on entrance into and
restored on exit from the routine using them.")
READING: UITER's U3/U4/U9 = $3/$4/$5 reuse Pass 2's unit / absolute counter / question-bit registers;
that is consistent only because UITER runs between passes. VDIMEN's $1 is listed "- - -".

**p.173** (Serviceability): Fpass1, Fuiter, Fpass2, Fpass3 indicators (quoted in C.1); counters
"Unit", "Field", "Symbol"; MACHER linkage "SIC, Machez; B, MACHER".

**DECODE p.140** (step 6's, only the linkage, because boxes 14A/14B call it): "DECODE is entered from
pass 2a and 2b if Zifp2 is one." "The calling sequence is: SIC, Decodz; B, DECODE. Zifall is set to
one on entry by DECODE." "If DECODE is unable to completely assemble the binary output, Zifall is set
to zero before returning." Chart DC p.139 has KE, KEBA, KEE, KEF, KF, KDDI, KFA, KFA4, KFB, KFNA,
KXAB, KB, KAB labels; "Kamms" is not on Chart DC or p.140 as far as I could see at page resolution.

---------------------------------------------------------------------------------------------------
## PART E. The host (strap/strap2/) against the pages

Paths are under `stretch/strap/strap2/`. "MATCH" = does what the page says; "DIFFERS" = the page says
something else; "BEYOND" = the page is silent or defers and the host supplies it; "CHOSEN" = the host
source marks it CHOSEN at that line. Only pp.28-36, 54-60, 135-137 (and the definition pages of Part
D) are the yardstick; where the host cites another source (C28-6129, N28-1081, p.177...) I say so and
did not check that source.

An earlier specification by the project exists: `stretch/docs/strap2/pass2.md` (sections 3, 4, 8.1,
13). My independent chart traces of GB and RD agree with its section 3.1 and 8.1 except:
- Chart RD box 19 (ADDORD): I trace 19 -> 16 (REQUESTED INFO ESTABLISHED); pass2.md 8.1 says
  "-> 19 ADDORD -> 11". [check in the ink: the line from under box 19 goes left to an X above 16.]
- pass2.md 8.1 writes `VVCDRL`; Fig. 10 prints VVCDR1 (digit) as I read it at zoom.
- pass2.md 13 lists p.27 as not read; A.0 above quotes its lower right column (Ziotpt/DR, Zifall,
  Zifp2 for SYN).

### E.1 VALUE (`value.py`)

| # | Page | Host | Verdict |
|---|---|---|---|
| V1 | Break exit, Vnb/Vfb bits, re-entry at Vrtrn / Vpunt (pp.55-57); chart boxes 11, 16 | No break. `value.py:14-16`: "VBREAK ... is here simply "not available": VALUE goes on through the expression ... and the caller decides." A datum that is not known sets `V.avail = False` (`value.py:418-419, 565`). No Vcb*, Vnb*, Vfb*, Vfbnot. | DIFFERS (stated in the header, not tagged CHOSEN) |
| V2 | Push list of headings and workspaces, $10/$11; values as normalized floating point words (p.57 R, Fig. 10) | Python recursion and Python integers (`value.py:14`; `_normal` `value.py:393-567`). | DIFFERS (stated, not tagged) |
| V3 | Four entries VALUE / VSKIP / VDIMEN / VMOVE with Valinx, Vmovex, $1 (p.55) | One reader, `read_field(mem, addr)` (`value.py:342-359`), returning `V.next` as the updated pointer. VSKIP = callers using `.next` (`pass2.py:523, 550, 604`). VMOVE = `coded(p2, start, end)` (`pass2.py:1479`) copying bit strings. VDIMEN has no counterpart: dimension products are recomputed on each use (`value.py:261-271` `_special`, `value.py:297-303` `array_of`, `pass2.py:553-568` `dr_size`); the D vle's "Evaluation Indicator" is written 0 at `symtab.py:280` and no other line of the package writes that bit (grep), so it is never turned on and no products are stored (CHOSEN at `symtab.py:47` covers only the before-evaluation layout). The DR's "negative ... value field of Ziotpt" (p.27/32) is not written. | DIFFERS |
| V4 | Calling sequence LVI, 15, $+2; B, VALUE; B, fix-up; normal return (p.55) | Python calls. | n/a on the host; the 7030 version must follow p.55 |
| V5 | Box 13: existence bit off -> MACHER ("must be on") | `value.py:346-348`: an expression whose first bit is 0 returns an empty, available V (value 0) and `next = p + 1`. | DIFFERS |
| V6 | Box 8 prefixes 000, 001, 010, 011, 100, 101, 110(+000/001/010/011), 111 | `value.py:349-357`: only 000 and 111; anything else `raise ValueError("prefix %o")`. So special (001), padded (010), special signed (011), super special (100), fully evaluated (101) and the long prefixes are not read. | DIFFERS (fails loud) |
| V7 | Box 9 datum 100 symbol, 101 subexpression, 110 absolute (24 bits as integer), 11100 system symbol (value then dds) | `value.py:395-446`: one bit then two: 00 symbol, 10 absolute 24 bits -> I, 11 + 00 system symbol (24 bits -> B, then 13 bits dds, `value.py:441-444`), 01 `raise ValueError("sub-expression datum")`. The symbol datum's 7-bit count and A8 characters (`value.py:403-406`), the lone `$` (`value.py:407-412`), S/X chains (`value.py:447-454`) and the g.p. chain (`value.py:361-376`) come from Appendix C / Fig. 14, not from pp.54-60. Widths "24 bits ... as integer value" match the chart; the system symbol's 24 + 13 is not on pp.54-60. | MATCH for 100/110/11100 as far as the pages go; DIFFERS for 101 (fails loud); BEYOND for the layouts |
| V8 | Boxes 4, 5: operators by a table giving "section entry and the operand type"; arithmetic not described | `value.py:510-562`. Header `value.py:7-12`: arithmetic "UNSPECIFIED on the guide's pages", taken from C22-6531 pp.10-12 and C22-6578 p.64; "CHOSEN: * and / apply to both parts; a quotient of two bit addresses is an integer." | BEYOND + CHOSEN (`value.py:11`) |
| V9 | Box 6: Vvspx / Vvabs / Vvint post-processing (index mark, absolute = signs plus, integer = combine and zero the bit value), padding skipped, results to Sini / Sinb | None of the three result modes exists (they belong to prefixes 001/010/110 the host refuses). Results are `V.B`, `V.I`. | DIFFERS (follows from V6) |
| V10 | Output words Sini, Sinb, Sinx, Sinxq, Sinsx (S/X type), Sindim (reference), Sindds (reference), Sindsq, Sinser, Sinrl1/2 | `class V` (`value.py:43-69`): B, I, X, xq, avail, dds (the 13-bit dds itself, not a reference address), sym, gps, next, dims (the evaluated list, not a reference), nullf, lc, reg. No S/X type result, no Sindsq, no Sinrl bits (relocation is `lc`/`reg`, `value.py:59-65`, from p.185 and bss_loader_spec). Flags are returned in `Value.flags` (`value.py:81`), not in a Sinser field. | DIFFERS in form |
| V11 | Sinser is (BU, 4); "five error flags" elsewhere | Five flags `FLAG_NAMES` and their bit order: "CHOSEN: their order in the five bits" (`value.py:27-31`). | CHOSEN (`value.py:28`) |
| V12 | Vcundf on: "a standard symbol table entry will be made, and then VALUE will proceed as though it had found this entry"; chart 15 -> 19 ADDORD | `lookup_or_enter` (`value.py:332-339`): SEARCH, then `addord(name, KIND_UNDEF)` if `vcundf`. | MATCH |
| V13 | "Whenever VALUE is asked to evaluate a symbol, VALUE marks the symbol as having been referenced from an address field." (p.33 L) | `value.py:338` sets ZST24. (p.140 names Zst24 as the "used" mark, for DECODE box 6.) | MATCH; the bit number is from p.140, not pp.54-60 |
| V14 | VALUE asks for a symbol's value; if the entry lacks it VALUE breaks and the USER (UITER) evaluates the defining SYN, with Utab levels | `symbol_value` (`value.py:114-155`) evaluates the defining expression itself, recursively: `_syn` (`value.py:221-251`), `_special` (`value.py:253-282`), labels from stored counters (`value.py:120-126`). Circularity is found by the host's own use of ZST17 as an "in progress" mark (`value.py:129-134, 146`), zero is assigned there (`value.py:133`), ZST4 is set as the circular flag (`value.py:132`) and ZSTCTG as contagious (`value.py:149-152`). The pages give Zst17 as "processing bit for mode" tested in UITER box 23 for the dds reference; they name no bit for the circular or contagious FLAGS. | DIFFERS in where it happens (UITER's work is inside VALUE); bit names ZST4, ZSTCTG are the host's (symtab.py:6 "CHOSEN, README gap 1") |
| V15 | `$`: Box 13 of Pass 2 puts the counters "in the function portion of the symbol table entry for the ($)"; VALUE would then find `$` like any symbol | `value.py:407-412` evaluates the lone `$` from `Value.abs` / `Value.sym` (copies of $4/$6 set by `pass2.py:180-182` `_set_dollar`, commented "Box 13" at `pass2.py:266`); no ($) entry is written. | DIFFERS |
| V16 | MACHER from box 13/21 | Never called from value.py. | DIFFERS |
| V17 | (not on pp.54-60) | Subscript scaling and messages 75, 76, 77 raised through `Value.notes`, 71 refused (`value.py:455-501`), sources C28-6129 p.40 and p.177; index from an earlier definition (`value.py:245-250`, chart RE); relocation counting (`value.py:173-210`). | BEYOND |

### E.2 UITER (`pass2.py:120-156`)

| # | Page | Host | Verdict |
|---|---|---|---|
| U1 | Utab pushdown, U3/U4/U9 ($3/$4/$5), levels, an entry per Vbreak return (p.135) | "Python's recursion stands in for UITER's Utab, whose mechanics the guide does not give" (`pass2.py:6-8`); the recursion is in `value.py:114-155`. | DIFFERS (stated, not tagged) |
| U2 | Box 9: branch-on-bit-AND-SET-to-one Zst0 before the entry is worked on; box 11 turns Zst0 off again if VDIMEN fails; boxes 22, 26 test-and-set it again | `pass2.py:149-150` skips if ZST0; sets ZST0 only after a value is obtained (`pass2.py:156`). | DIFFERS |
| U3 | dds reference chain: boxes 16, 23, 31, 17 (Zst3, Zst17, Zst32), VALUE for the reference | Not in UITER. A SYN's dds is copied when its value is evaluated (`value.py:235-238`); `symbol_dds` (`value.py:309-330`) resolves on demand. ZST10, ZST11, ZST12, ZST14, ZST15 and ZST32 are declared (`symtab.py:63-65`) and used nowhere in the package (grep). | DIFFERS |
| U4 | mode known (box 24, Zst10) else MACHER | Not done. | DIFFERS |
| U5 | field length / byte size: boxes 25, 18, 19, 32-34, 20, 26 and 27, 28, 35, 36, 29, 21 (Zst11, 12, 14, 15), Kamms with "error message" and truncation | Not in UITER. Symbols: `symbol_dds` evaluates ZFLX / ZBSX on demand and masks silently, `(fl & 63)`, `(bs & 15)`, no message (`value.py:319-330`). Units: `dd_dds` (`pass2.py:468-506`) gives message 87 "THE FL IS GREATER THAN 64" and 88 "BYTE SIZE GREATER THAN 8" (p.177 lists both under DECODE with those texts; that Kamms is what raises them is a READING, p.137 prints no number) and masks `& 63`, `& 15`; a CC-mode DD allows 12 (`pass2.py:493-494`, source C28-6129 p.30). | DIFFERS in place; message numbers and masks BEYOND p.137 |
| U6 | Box 11: circular -> zero; else VALUE; a DR with unformed product -> VDIMEN | `value.py:129-133` (circular -> zero); no VDIMEN. | partly MATCH (zero for the base of a circular chain), DIFFERS (VDIMEN) |
| U7 | Box 13/14: after Pass 2a a symbol with no value -> MACHER; boxes 31, 24 -> MACHER on either iteration | `pass2.py:152-155`: second iteration only, and not for undefined symbols: `msg.add(7, f"NO VALUE FOR {name}", 0)  # MACHER`. p.176 prints 7 as MACHER's, with the text "ASSEMBLY ERROR"; the host's text here is its own (elsewhere it uses "ASSEMBLY ERROR", e.g. `pass2.py:1166`). | DIFFERS / BEYOND |
| U8 | Boxes 4, 5 (Uhl): ANEXT over the hi-lo entries "in the vle table" (H vles, Fig. 22), memory bounds | A Python list `self.hilo` of (abs, sym) pairs (`pass2.py:67, 163, 314, 428`), reduced at `pass2.py:132-137` to the highest, rounded up to a full word. No H vle is written. An extra entry is appended at the end of Pass 2a (`pass2.py:167`) which no page read here mentions. | DIFFERS in form; BEYOND for the end-of-pass entry and the reduction rule |
| U9 | (pp.135-137 do not say where undefined symbols get a location) | `pass2.py:138-146`: in the second UITER every undefined symbol not yet valued gets ZST1, dds (N, 0, 4), and the next full word above the upper limit (sources cited there: p.205, C28 p.20). `pass2.py:906`: "the undefined symbols' words counted (CHOSEN)". | BEYOND (pass2.md Gap 3) |
| U10 | UITER "turns on an indicator to inform VALUE that it can now make an undefined-type entry" (p.32 R) | `pass2.py:123` `self.val.vcundf = True`. | MATCH |
| U11 | Box 3 ERRIN; the Symbol counter (p.32 R, p.173 R); Np2ind off / Fpass3 on at return (p.35 R) | ERRIN, the Symbol counter and Fpass3 are not modelled. `np2ind` is set True at `pass2.py:160` and cleared at the start of `pass_b` (`pass2.py:894`), not by UITER's return. | DIFFERS (host bookkeeping) |
| U12 | Walk by ANEXT over the vle table (boxes 7, 8) | `for f in list(st.vles)` (`pass2.py:139, 147`), described as "UITER's ANEXT over the vles" (`pass2.py:129-131`). | MATCH in order; the 7030 version uses ANEXT itself |

### E.3 Pass 2a (`pass2.py:158-345` and helpers)

| # | Page | Host | Verdict |
|---|---|---|---|
| P1 | Boxes 3,4: $4, $6 zero; absolute counter 41 octal, "0 if in PUNREL mode"; that setting entered as the first hi-lo entry | `ABS_START = 0o41 * 64` (`pass2.py:23`); `pass_a` (`pass2.py:159-164`) sets abs = origin, sym = 0, first hilo. PUNREL is found by a scan ahead of Pass 2: "CHOSEN: the mode holds when PUNREL comes before any statement that takes a location" (`pass2.py:101-118`). | MATCH; PUNREL rule CHOSEN (`pass2.py:103`) |
| P2 | Boxes 5A-6: field counter zeroed, unit counter incremented, $3, $5, five flags zeroed, location of the name's function "computed and saved" | `unit_a` zeroes `val.flags` (`pass2.py:222-227`). The function of a named unit comes from a Pass 1 map: "CHOSEN: a host map from Pass 1, which the 7030 version replaces with that scan" (`pass2.py:405-411`). Counters not modelled. | CHOSEN (`pass2.py:409`) |
| P3 | Boxes 9, 10: first non-MCP op (comments excepted) sets a switch so non-contiguous MCP ops are not punched in 2b, "although they will be listed" | Pass 1 sets `self.fiod` at the first non-MCP op (`pass1.py:181`) and gives message 102 "ILLEGAL SEQ. OF MCP CARDS" for a later MCP op (`pass1.py:555-556`; p.178 gives 102 to MIOD). Pass 2a has no switch. In 2b `_punch_unit` punches the card of every MCP unit (`pass2.py:1047-1050`) with no test for contiguity. | DIFFERS: a non-contiguous MCP card is punched by the host |
| P4 | Box 11: the second EXT unit gets no location-counter adjustment | `rounding` returns 0 for ZIEXT2 (`pass2.py:208-209`); `_unit_a` returns for it (`pass2.py:333-334`). ZIEXT2 is set in Pass 1 (`pass1.py:122`). | MATCH |
| P5 | Boxes 12A/B: no rounding for "a DD or for a DR in a non-floating point mode"; else by the op question bits full or half word; with a symbolic counter, a new special symbol "marked with the appropriate full or half word indicator" unless the present one is "at the required type location" | `rounding` / `_round_a` (`pass2.py:187-220`): DD/DR/DRZ round to 64 only if ZIFDSF is on and the unit's ZIDDS mode is N or U. ZIFDSF is Fig. 20's cell m, "dds filled in" (`unit.py:31`; explicit dds is cell g, ZIFDDS, `unit.py:25`), so this is "the dds is known and floating", which is what the page says; a DD/DR whose dds is not yet filled in at 2a is not rounded. Other ops by `e.align` (host op table, not the op question bits). Special symbol with ZROUND 1 half / 2 full (`pass2.py:200-204`); "have >= unit_bits" keeps the present one. | MATCH in outline; question bits replaced by the host op table |
| P6 | Boxes 12C-12E: CNOP: "may be necessary"; "effectively processed as a NOP unit if the adjustment is necessary" | `rounding` returns 64 for CNOP (`pass2.py:216-217`), so 12B's rounding has already put the counter on a full word; `cnop_a` is empty (`pass2.py:430-431`); 2b fills the gap with NOPs (`pass2.py:1340-1343`, `_fill_gap`). Box 12D's test (counter still needs adjusting after the rounding) cannot come out YES in the host. What CNOP adjusts TO is not on pp.33-34. | DIFFERS / BEYOND |
| P7 | Box 13: counters saved in the function of the ($) entry | `_set_dollar` copies them into the Value object (`pass2.py:180-182, 266`). | DIFFERS (see V15) |
| P8 | Boxes 15-17, 14F: counters into the unit and the name's vle; "This is not done if the unit contains a SYN op." | Unit: ZIADAB, ZIADSY written for all but SYN (`pass2.py:289-292`): MATCH. Symbol: for a SYN the host DOES put ZABS / ZSYM / ZCTR in the SYN's entry (`pass2.py:278-284`), so that a `$` in its expression is the counter at the SYN ("NSYN: its $ is the counter here"). ZIADSY's content: "CHOSEN, the special symbol's function address, which 2b needs" (`pass2.py:413-415`); `pass2.py:291` first writes it 0. | SYN-entry write DIFFERS from p.34 R (untagged); ZIADSY CHOSEN |
| P9 | 14A/B: units with coded expressions go to DECODE in 2a ("DR, DRZ, EXT, LINK, DD and DDI"); SYN and MCP-type not | `_unit_a`: pseudo-ops other than DD, DDI, DR, DRZ, EXT return (`pass2.py:327-328`); instructions go to `decode(unit, final=False)` (`pass2.py:344`); DD/DR/EXT/DDI go to their own helpers, not through `decode`. LINK is presumably an ordinary op entry by then (p.32 R) [not traced]. | MATCH in effect; structure differs (DECODE's boxes 16-23 are separate host methods) |
| P10 | 14H-14K: binary length known -> add to $4; DD/DR length unknown -> new special symbol whose vle holds "a special coded expression in which the sum of the current symbolic counter and the absolute counter is encoded"; $6 = its vle location, $4 = 0 | `advance_dd` / `_dd_later` (`pass2.py:508-542`), `advance_dr` (`pass2.py:570-587`): a special symbol with fields ZABS, ZSYM (the two counters, as fields not as a coded expression) plus ZDIMX/ZDIMN/ZFLM (a D vle of the unknown dimension expressions and a multiplier), evaluated by `value.py:253-282`. The representation is the host's (pass2.md Gap 6); the lines are not tagged CHOSEN. | BEYOND (representation invented); effect MATCH |
| P11 | DDI: "DECODE will get the DDI evaluated by using special facilities in OUTPUT. Then DECODE adjusts the unit of the DDI so that subsequently Pass 2 will recognize and treat the unit as one for a SYN." | `ddi_a` (`pass2.py:347-403`): runs `dd_b` into a scratch image, enters the 24-bit value in the symbol, keeps `self.ddi_values[unit]`; the unit is not changed to a SYN (2b tests `name in ("SYN", "DDI")`, `pass2.py:1248`). Message 132 and the refusals come from C28-6129 pp.16-17 / p.178. | MATCH in effect; DIFFERS (unit not rewritten); BEYOND |
| P12 | SLC: adjust counters, hi-lo entry; SLCR: adjust, no entry; the "SCLR" and "hi-lo-entry-can-be-made" indicators | `nslc` (`pass2.py:417-428`): entry for SLC only. No indicators. An SLC whose operand is not yet known makes a special symbol holding a copy of the operand expression (`pass2.py:423-426`), which the page does not describe. "CHOSEN: an SLC leaves the common" (`pass2.py:299`). | MATCH; indicators absent; BEYOND for the unknown operand; CHOSEN (`pass2.py:299`) |
| P13 | END: its location a hi-lo candidate | `pass2.py:310-315` (also FEND; and it reads the address field so undefined symbols are entered, citing p.19). | MATCH (+BEYOND for FEND) |
| P14 | EXT: parameters evaluated and "saved ... in the unit"; counter advanced "by the length indicated by the N parameter"; "If the statement of the EXT op is a multiple field DD, then the location counter will be incremented the extra amount." | `decode_ext_a` / `ext_params` (`pass2.py:433-457`): abs += count; `raise Unresolved("EXT parameters are not known in Pass 2a")`; any two of I, J, COUNT (C28-6129 p.19). Values are recomputed in 2b, not saved in the unit. I found no "extra amount" for a multiple-field DD in the 2a path. | partly MATCH; DIFFERS (not saved; multi-field DD) [the second point not fully traced] |
| P15 | SYN in 2a: "tests if the value is complete; if so ... box 21. If ... not ..., another try to get the value of the SYN by using a section of UITER." | `pass2.py:278-288`: `self.val.symbol_value(f)` once more, then reads its expression for the flags. | MATCH in effect |
| P16 | PUNSYM in 2a (NPNSYM marks each symbol's vle; p.178: message 124 "SYM ON PUNSYM NOT IN PROG." is NPNSYM's) | No implementation in the package: PUNSYM occurs only in the op list (`optable.py:33`) and the error texts (`errtab.py`); `_unit_a` returns at `pass2.py:327-328`. | not implemented |
| P17 | SEM, REM in 2a: major mask updated from the unit's mask | No implementation in the package (same grep: SEM/REM only in `optable.py:32`). | not implemented |
| P18 | PRNID: the unit goes to OUTPUT in 2a too (PRNIDs precede the listing) | No implementation in the package (PRNID only in `optable.py:32`). | not implemented |
| P19 | SPNUS: "turn on an indicator for NUNDSY" | `pass2.py:323-324` `self.spnus = True`. PRNTALL likewise (`pass2.py:325-326`, source N28-1081). | MATCH |
| P20 | Box 21: the five flags OR'ed into the unit each cycle | `_or_flags` (`pass2.py:229-240`) into ZIFLAGS, plus `definition_flags`: "CHOSEN: QUEST on every definition ... PSEUDO on the base of a circular chain" (`pass2.py:242-259`). In 2b: "CHOSEN: the flags are ORed again in 2b" (`pass2.py:1007`). | MATCH + CHOSEN (`pass2.py:244, 1007`) |
| P21 | TLB is in the "only need the wind up procedure" list (p.34 R) | `pass2.py:316-319` reads TLB's field in 2a (to enter undefined symbols). | BEYOND |
| P22 | Hi-lo "first entry" only at init | extra entry at the end of the pass (`pass2.py:167`). | BEYOND (see U8) |
| P23 | (2b, for context) boxes 14E/27: 2b checks the stored 2a setting against "the present setting of the location counter" | Header `pass2.py:10-13`: "CHOSEN, the guide's gap 2: Pass 2b starts its counter where 2a did and runs it again ... On a disagreement 2a's setting wins and message 6 is given (p.36)." p.176: 6, NPS2, "PASS 2A AND 2B LOC. CTR. DO NOT AGREE". But grep finds no `msg.add(6` anywhere in the package (only the text in `errtab.py:30`): 2b takes each unit's location from what 2a stored (`location_2a`, `pass2.py:1000-1004, 1250`), and a unit with none gets message 7 "NO LOCATION IN PASS 2B" (`pass2.py:1252`). So the header's "message 6 is given" is not what the code does, as far as grep shows. [2b is step 6; not traced further] | CHOSEN (`pass2.py:10`) |
| P24 | COMBLOCK, SLCRCOM, regions | `pass2.py:269-277, 301-309` (pp.185-187). "CHOSEN: an integer, that number" (`pass2.py:305`). | BEYOND the pages read; CHOSEN (`pass2.py:305`) |

| P25 | 14A, 14C as unit-flag tests (Zifp2 "DECODE gets unit", Zifbo "binary output", Zifall; p.140, Fig. 20) | The flags are written in Pass 1 (`pass1.py:106, 186-187, 331, 483, 495-496, 501, 557-558, 606, 674, 683-685, 739-740, 750-753, 906-908, 935-937`) and never read in `pass2.py` (grep: no ZIFP2 / ZIFALL / ZIFBO / ZIFDD there). `_unit_a` decides by op name (`pass2.py:327-344`), and `decode` never sets or tests Zifall (p.140: "Zifall is set to one on entry", zero if not completely assembled). | DIFFERS in mechanism |

Host unit fields (`unit.py`) with no counterpart in Fig. 20 as printed: ZIEXT2, bit 31 of the ZIOPX
word ("CHOSEN: bits of the ZIOPX word that Fig. 20 draws zero, for what Pass 2's text keeps in
indicators: the second of two EXT units (FB/11) ...", `unit.py:43-46`); DD_LEN, DD_NUMERIC, DD_CC,
DD_LOC, sub-fields of ZIOTPT for a DD or DR (`unit.py:50-54`, "formats.md 3.4"; p.34 R says only that
the final length of a DD or DR is kept in Ziotpt). ZIFLAGS (5 bits at 25) and ZISUPP (bit 30) are Fig.
20's "Error Flags" and cell p. `unit.py` has that one CHOSEN mark.

`symtab.py:6-10` in full: "CHOSEN, README gap 1: the guide names Zst bits ... and tabulates none. So
Zst<n> is simply bit n of the function, which gives every printed name a place, and the fields it
needs beyond the printed names follow them." So ZST0/3/10/11/12/14/15/17/26/32/35/36 are at the bit
their number says (CHOSEN), and ZKIND, ZVALB, ZVALI, ZABS, ZSYM, ZCTR, ZROUND, ZEXPR, ZFLX, ZBSX,
ZDIMX, ZDIMN, ZFLM, ZSTCTG, ZOLDF, ZST1, ZST4, ZST22, ZST23, ZST37 are host fields with no printed
name on the pages read here (`symtab.py:61-87`).

CHOSEN marks in the host that bear on step 5, collected: `value.py:11` (operator arithmetic),
`value.py:28` (flag bit order), `value.py:177` (lc count of a circular SYN), `pass2.py:10` (2b
counters), `pass2.py:103` (PUNREL), `pass2.py:244` (definition flags), `pass2.py:299` (SLC leaves the
common), `pass2.py:305` (SLCRCOM integer), `pass2.py:409` (unit -> function map), `pass2.py:414`
(ZIADSY), `pass2.py:906` (undefined symbols counted in the bounds), `pass2.py:1007` (flags in 2b),
`symtab.py:6` (the Zst layout itself, "README gap 1"), `symtab.py:47` (D vle before evaluation),
`symtab.py:246` (special symbol's n), `unit.py:43` (ZIEXT2). Host departures NOT tagged CHOSEN though they are choices: V1,
V2, V5, V14, V15, U1, U2, U7 (message 7's text), U8, P3, P6, P8 (SYN entry), P10 (special symbol's
representation), P11 (DDI unit not rewritten), P25.

The host files did not change between the commit at the start of this run (3204601) and the one at
its end (ca0b746): `git diff --stat` over `stretch/strap/strap2` and `stretch/docs/strap2` is empty,
so the file:line cites hold at ca0b746.

---------------------------------------------------------------------------------------------------
## PART G. The numbered error messages that bear on step 5 (pp.176-178, page resolution)

Heading p.176: "LIST OF THE STRAP II NUMBERED ERROR MESSAGES*", columns "Number / Logic Area Detecting
Error Condition / Message"; each message text ends with its own number. Footnote: "* Error Messages
numbered 1-28 can be made to appear on the console typewriter by the use of a Correction card."
Rows copied as printed (number, logic area, text):

| No. | Logic area | Message | READING: where it belongs in step 5 |
|---|---|---|---|
| 6 | NPS2 | PASS 2A AND 2B LOC. CTR. DO NOT AGREE | boxes 14E/27 and 20/28 (2b check; p.35 R - 36 L) |
| 7 | MACHER | ASSEMBLY ERROR | every MACHER box: RD 21; GB 6 |
| 19 | ANEXT | SYMBOL TABLE IS INCORRECT | ANEXT, used by GB 4 and 7 |
| 69 | VALUE | TRUNCATION IN INDEX VALUE | VALUE (no box named) |
| 70 | VALUE | INDEX IN WRONG PLACE, IT IS IGNORED | " |
| 71 | VALUE | SUBSCRIPT WRITTEN AS BIT | " |
| 72 | VALUE | CANT SUBSCRIPT CONSTANT, TRY INDEX | " |
| 73 | VALUE | SUBSCRIPT OR INDEX INCORRECT | " |
| 74 | VALUE | CANNOT SUBSCRIPT SYMBOL WITH NO DDS | " |
| 75 | VALUE | 1 SUBS. TOO MANY, LAST USED AS INDEX | " |
| 76 | VALUE | TOO MANY SUBSCRIPTS, EXTRA IGNORED | " |
| 77 | VALUE | TOO FEW SUBSCRIPTS, OTHERS TAKEN 0 | " |
| 78 | VALUE | DIVISION BY ZERO, DIVISOR IGNORED | RD box 5 (operators) |
| 86 | VALUE | ONLY INTEGER VALUES ALLOWED | " |
| 87 | DECODE | THE FL IS GREATER THAN 64 | Kamms, GB 20 ("not more than 64 bits") |
| 88 | DECODE | BYTE SIZE GREATER THAN 8 | Kamms, GB 29 ("not more than 8 bits") |
| 89 | DECODE | BIT TYPE NOT ALLOW. | Kamms "not in bit style"? (89 or 97; cannot tell) |
| 97 | DECODE | BIT TYPE UNUSUAL | " |
| 98 | DECODE | NEGATIVE PARAMETERS ON EXT | DECODE boxes 22-23 (EXT in 2a) |
| 99 | DECODE | PARAMETER GREATER THAN 64 | " |
| 100 | NPS2 | ADDR LESS THAN 33. | Pass 2 main flow; no box on pp.32-36 mentions it |
| 101 | NSYN | ERR IN DDS | NSYN (chart FD) |
| 122 | NEXT | INSTR. NOT ALLOWED IN EXT | boxes 18A/18B? ("supplies zeros and gives an error message") |
| 124 | NPNSYM | SYM ON PUNSYM NOT IN PROG. | NPNSYM in 2a |
| 130 | DECODE | FIELD LENGTH MORE THAN 24 | DECODE |
| 132 | DECODE | CANNOT EVALUATE DDI | DECODE boxes 16-17 |
| 133 | NEXT | INCONSISTENCY IN EXT PARAMETERS | NEXT |

No row has UITER or Kamms as its logic area. Host against this list: of the VALUE rows the host
raises only 75, 76, 77 (`value.py:482-488`) and refuses 71; 69, 70, 72, 73, 74, 78, 86 have no
`msg.add` in the package (grep). 19, 89, 97, 98, 99, 100, 101, 124, 133 likewise have none. 122 is
given by the host with its own text "EXTRACT FROM A PSEUDO OP" (`pass2.py:1458`), not the printed
"INSTR. NOT ALLOWED IN EXT". Division by zero: the host divides by 1 silently (`value.py:555`).

---------------------------------------------------------------------------------------------------
## PART F. What was read, and what could not be read with confidence

Pages read from the image.
- At zoom (220 dpi crops or better): 27 (lower right column), 32 R top, 33 L lower half, 34 R top,
  35 L, 36 L lower half, 55 (all), 56 (both tables and items 3-5, DETAILS start), 57 (L all, R lower
  half: flow chart description, Boxes 12, 17), 58 (figure; R column lower), 59, 60, 135, 137, 189
  (upper four words of Fig. 20).
- Charts: 28, 29, 30, 31 at 220 dpi; 54 and 136 at 220 and 300 dpi.
- At page resolution only: 1-6, 32 L, 33 R, 34 L, 35 R, 36 R and 36 L upper, 57 R upper (the Item
  table), 58 L (Boxes 13, 8, 14 and the prefix table), 138, 139, 140, 173-175, 176-179, 184-186, 189
  lower, 190, 191, 202.
NOT read: p.27 left column and upper right; pp.44-53 (TABMAN, ANEXT); Appendix C (pp.197-201). Kamms
has no description on pp.139-140.

Go to the ink for these (page, column, item):
1. p.136 Chart GB, middle: the arrows 26 NO -> 20, 34 NO -> 26, 34 YES -> 20 (from below), 20
   "F. L. ESTAB" -> 18 (left side) and "F.L.NOT. ESTAB" -> connector 42; lower: 29 "B.S. ESTAB" ->
   21, 29 "B.S.NOT.ESTAB" -> 43, 30 -> 22, 22 YES / 14 NO -> 40. Direction taken from the X
   positions; agrees with docs/strap2/pass2.md 3.1, but both are traces of a dot-matrix chart.
2. p.136, label above box 27: "UBS1" or "LBS1" (pass2.md reads LBS1).
3. p.54 Chart RD, top right: box 17's exits (I read 17 -> EXIT and 21 -> EXIT at one junction; no
   line 17 -> 8 or 17 -> VBREAK is drawn although the text of Box 17 says "branch to VALUE" and "go to
   VBREAK"). Box 19 -> 16 (not 11). Box 2 "SPACE VI BY 3": "VI" or "V1".
4. p.54, box 6: the subroutine strip reads "MACHER".
5. p.30 Chart FC: label at 18A "NUPDT" / "NUPOT"; strip of 18B ("N=XT2"); strip "CPPUN".
6. p.57 R upper, the Item/Type/Purpose table continuation (Vcbv ... Vcundf): page resolution only.
7. p.58 L: Box 13, Box 8 and its prefix table, Box 14: page resolution only.
8. pp.33 R, 34 L, 35 R, 36 R: the box paragraphs quoted in A.5 from those columns were read at page
   resolution; the names in them (INTIN, DECODE, OUTPUT, Np2ind, Fpass3, Uhl, NMCPA1, Ziotpt) are
   plain, but a parent re-check of quotes should start there.
9. p.58 Fig. 9: which tick each of SINSX / SINRL1 / SINRL2 and SINMQ / SINXQ / SINSER sits on.
10. p.58 R: "Vvcdrl" (letter l) against Fig. 10's VVCDR1 (digit).
11. p.60 Fig. 10: the bracketed note under VVE ("[c ($15)vf when VALUE is entered]"), the bit numbers
    of VCH (28-31?) and of VVSER (59-62?), the stray "ABLE!" after legend item b.
12. p.189 Fig. 20: the lower three words (ZICDID, ZIOPX with "Error Flags" and cell p, ZIOTPT) and
    the legend were read at page resolution only. The flag names of the upper words are confirmed.
13. p.33 L: "41.₈" (read at zoom as 41 with a subscript 8 after a full stop).
14. p.34 R Box 21: "which have already been treated with follow this action" (as printed, garbled).
15. p.36 L: "SPUNS" in the 2b list and "tilting" (zoomed for "tilting"; "SPUNS" page resolution only;
    pass2.md contradiction 24 also records SPUNS).
