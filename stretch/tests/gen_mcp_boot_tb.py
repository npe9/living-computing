#!/usr/bin/env python3
"""gen_mcp_boot_tb.py -- boot MCP's own bootstrap on the model, from a
tape image in a host file.  docs/boot_plan.md M3, the step after the
transcription.

IT RUNS.  MCP's bootstrap executes from end to end on this model,
off a tape built from the thirteen transcribed pages, and hands off
to printed p.15's MCP INITIALIZATION.

>>> AND p.15 IS TRANSCRIBED NOW -- the whole listing from printed p.2
through p.36 is, as of 2026-10-22 -- so the hand-off lands on real
instructions instead of the zeros past X BS END.  strap/prosa.py puts
printed pp.15-18 in the PROSA record, the TRANSMIT on printed p.4
line 28 moves them to 000621.00, and the run continues into MCP
INITIALIZATION, reports "-NO IOCD DETECTED", enters the error
routine and stops at PC 239 = 000167.40, printed p.6 line 1's
"BD,$ -LOOP". <<<

This file began as a DIAGNOSTIC whose expectations were all zero, so
that every value would print and the model could say what was
missing.  It said three things, in this order, and none of them was
top of the predicted list: Address Invalid was never raised on a
store past installed core (printed p.2's core-sizing loop has no
terminating count, so nothing else ends it); LVE was unimplemented;
and SPACE FILE was unimplemented.  WITH THOSE THREE IN, THE
BOOTSTRAP RUNS.  The expectations below are now MEASURED VALUES with
a reason each, and this is a test.

THE IMAGE IS THE COMMITTED ONE.  mcp_image.py merges the eight page
transcriptions, verify_mcp_image.py checks the merge, and mktape.py
--cw-in-image writes it out with MCP's OWN control word as word 0 --
not a reconstruction of it.  Reference Manual printed p.126: the
fixed control word the IPL hardware plants reads ONE word into
location 4 and refills from location 4, so word 0 of the tape has to
BE the program's control word.  MCP's source puts one at 000040.00
for exactly that reason.

WHAT HALTING MEANS HERE.  core.halted() is "the last instruction
branched to itself", and MCP uses `BD,$` as its halt: printed p.5
line 11 ("IPL CONTAMINATED"), printed p.6 line 1, and the two error
sites X ERR 20 and X ERR 21.  So a halt is informative -- the PC says
WHICH give-up it reached.  Reaching the step cap instead means it is
still running or looping.

READ THE PC BEFORE READING ANYTHING ELSE.  If it is at or past
000133.00 the bootstrap took the ERROR ROUTINE exit, and whatever it
stopped on there is a symptom of an earlier failure, not the next
thing to implement.
"""
import os
import subprocess
import sys

from gen_tb import generate
from mcp_image import build, build_mcp_ipl
from opcodes import INDICATOR_BITS
import iocd
import prosa
import struct


def _ind(name):
    """Weight of an indicator in the 64-bit word: IBM bit n is 1 << (63-n).
    Same helper gen_io_tb.py has; named the same so a reader who has
    seen one recognises the other."""
    return 1 << (63 - INDICATOR_BITS[name])

# Resolved against this file's own location: mktape.py lives in
# ../strap/ and this generator is run from tests/, but a bare name
# here breaks the moment either moves (it did, on 2026-10-18).
MKTAPE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      os.pardir, "strap", "mktape.py")

# Word 11 is the indicator register (strap_asm's SYSTEM_SYMBOLS maps
# the system symbol IND to word 11), and StretchTypes.bsv puts
# Operation Code Invalid at ind_OP = 15.
IND_WORD = 11


def _sca6_word(n):
    """Word `n` of SCA6's output for the fixture's IOD card.

    The card is converted to the A set as a continuous six-bit stream,
    high-order character first, and the separator is mapped to the
    COMMA's code -- both facts measured against the model; see the
    comment at the mcp_ucbf1_* checks.
    """
    import charsets, iocd, prosa
    # The LAST IOD Uncode processed: printed p.25 line 51 tests the
    # next card's 12-zone BEFORE looping, so the MCPP card that ends
    # the scan is never converted and the buffer holds IOD number N.
    text = iocd.iod_card_text(**prosa.MCP_IODS[-1])
    sep_code = charsets.A[","]
    bits, nbits = 0, 0
    for ch in text:
        code = sep_code if ch == iocd.IOD_SUBFIELD_SEPARATOR else charsets.A.get(ch, 0)
        bits = (bits << 6) | code
        nbits += 6
    pad = (-nbits) % 64
    bits <<= pad
    nbits += pad
    return (bits >> (nbits - 64 * (n + 1))) & 0xFFFFFFFFFFFFFFFF


def _image_index(octal_word):
    """The index into prosa.MCP_IPL_WORDS of a word named by its
    printed octal address.  Written this way so the two checks below
    say WHICH WORD they mean -- "002147", the one printed p.36's last
    datum runs into and printed p.37's first CNOP sits in -- rather
    than an offset from an end that moves whenever a page is added."""
    return int(octal_word, 8) - prosa.MCP_IPL_AT


def _middle_index():
    """The first non-zero word at or after the middle of the moved
    image -- see mcp_moved_middle."""
    for k in range(prosa.IPL_WORDS // 2, prosa.IPL_WORDS):
        if prosa.MCP_IPL_WORDS[k]:
            return k
    raise SystemExit("gen_mcp_boot_tb: the image's upper half is all zeros")


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} ModuleName", file=sys.stderr)
        sys.exit(1)
    module_name = sys.argv[1]

    prog, src, defined, external = build()

    # THE pp.15-18 IMAGE, for the checks that describe what MCP did
    # after it moved itself.  Built here from the same decks
    # strap/prosa.py puts on the tape, so a check cannot drift from
    # the thing it describes.
    ipl_prog, _, _, _ = build_mcp_ipl()
    ipl_hw = lambda n: ipl_prog.symtab[n] // 32

    out = os.environ.get("STRETCH_TAPE")
    if not out:
        print("error: set STRETCH_TAPE to the image path", file=sys.stderr)
        sys.exit(1)
    merged = os.path.join(os.path.dirname(out) or ".", "mcp_merged.strap")
    with open(merged, "w") as f:
        f.write(src)
    # THE LAYOUT THE TRANSCRIPTION ESTABLISHED: the bootstrap record,
    # then a TAPE MARK.  Printed p.3's SPACE OVER TAPE MARK block
    # spaces past one before reading anything else, so a tape without
    # it is a tape MCP cannot boot from.
    r = subprocess.run([sys.executable, MKTAPE, merged, out,
                        "--cw-in-image", "--tape-mark"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr, file=sys.stderr)
        sys.exit(1)

    # ---- AND A PROSA RECORD AFTER THE MARK ------------------------
    # Printed p.3 SPACEs over the tape mark and printed p.4's FETCH
    # PROSA then reads from where that left the tape, so everything
    # appended here lands at X BUFER through printed p.14's control
    # word chain.
    #
    # >>> THE RECORD IS A FIXTURE <<<  Its SHAPE is derived from
    # printed p.4 lines 19-27; its CONTENTS are chosen.  strap/prosa.py
    # says which is which at length, and the checks below are written
    # so that a wrong derivation fails with the real offset in hand
    # rather than passing on a coincidence.
    #
    # Appended here rather than by mktape.py because mktape.py is
    # about the IPL tape -- a control word and an image -- and this is
    # a second record that has nothing to do with initial program
    # loading.
    #
    # >>> IT IS WRITTEN IN prosa.tape_words()'s CHUNKED FORM, NOT
    # FLAT.  printed p.14's control words read 513 words each with a
    # 512-word stride, so consecutive records overlap by one word and
    # the tape must carry every chunk boundary TWICE.  Writing the
    # buffer image out flat was invisible while the record was 92
    # words -- shorter than one chunk -- and shifted everything after
    # the first 513 words down by one the moment printed pp.19-36
    # joined the image. <<<
    with open(out, "ab") as f:
        for w in prosa.tape_words():
            f.write(struct.pack(">Q", w & 0xFFFFFFFFFFFFFFFF))

    sym = lambda n: prog.symtab[n] // 64

    checks = [
        # >>> THE ONE THAT SAYS IT FINISHED <<<
        # Printed p.4 line 37 is "CM1111(BU,1),$0 +.25  -END OF PROSA
        # FILE": connective 1111, all ones, into a ONE-BIT field at
        # word 16 bit 25, which is index register X0's flag bit.  That
        # instruction is on the LATE path -- after FETCH PROSA has run
        # and X DONE has seen End Exception -- and NOTHING EARLIER IN
        # ALL THIRTEEN PAGES WRITES IT.  So this bit is the difference
        # between "the bootstrap got to the end of its own work" and
        # "it stopped somewhere quiet".
        # >>> AND IT NOW CARRIES A COUNT TOO, WHICH IS THE DISK <<<
        # Word 16 is index register X0 and holds TWO things at the
        # end of the run: bit 25, the flag above, and 131,070 in its
        # count field (bits 28-45).  That count is printed p.4 lines
        # 31-32, "LCI,0,(8)377777.0" then "CB,0,$" -- MCP's DELAY LOOP
        # after RELEASE DISK, loaded with 0o377777 = 131,071 and
        # decremented once.
        #
        # BEFORE THE DISK EXISTED THIS RUN NEVER GOT HERE.  Printed
        # p.4 line 29 is "REL(SEOP),0.0($X0) -RELEASE DISK", channel
        # ZERO, and with nothing installed there the model rejected it
        # with Unit Not Ready; line 30's "BUNRJ,X ERR 12" then branched
        # out of the image entirely.  Channel 0 now holds the disk
        # (StretchIO.bsv chanDisk, read off printed pp.15-16's own
        # assembled code), the RELEASE succeeds, and MCP runs the
        # path it was written to run.
        # Word 16 is index register X0: bit 25 is the flag above, and
        # the count field is now ZERO rather than the 131,070 it held
        # when the run stopped after one turn of the delay loop.
        # **The loop ran to completion** -- printed p.4 line 31 loads
        # 0o377777 = 131,071 and line 32's "CB,0,$" counts it down --
        # which is what let everything below here happen at all.
        # AND ITS REFILL FIELD NOW HOLDS THE MACHINE'S SIZE, which
        # is printed p.15 line 22, "LR,$0,X S ROOF" -- load index 0's
        # REFILL from the word printed p.2 line 39 saved the measured
        # 7030 size into.  LR takes bits 0-17 of the addressed
        # half-word, and X S ROOF holds 6,291,456 bits in its value
        # field, whose top 18 bits are 98,304 -- the word count, and
        # StretchMemory's InstalledWords.
        #
        # >>> AND SINCE 2026-10-22 THE COUNT FIELD IS FIFTEEN, not
        # zero: printed p.15 line 20's "LC,$0,X BUFER+.32($9)  -GET
        # SIZE OF COMM REGION" now finds a real size there, because
        # the record carries a comm-region descriptor.  Before that
        # the field read zero, and Reference Manual printed p.30 makes
        # a direct count of zero mean 2**18. <<<
        # >>> AND IT IS REMOVED, 2026-10-24, FOR DRIFTING -- the
        # second check this project has retired for that reason. <<<
        #
        # It read word 16, $X0, at the END of the run, and asserted
        # the measured size MCP had loaded into it.  That was a fact
        # about a MID-RUN state, and it held only while the run
        # stopped before anything reused the register.  With printed
        # p.65 in the image the run executes MCP's ASSIGN entry and
        # goes on to T A9, and $X0 ends holding whatever that path
        # left -- 0x1C000000000 rather than the size.
        #
        # NOTHING IS LOST, and that is why it is removed rather than
        # re-measured.  Three checks still cover the same fact from
        # places the program does not reuse:
        #   mcp_x_s_roof                       -- printed p.15 line
        #     23's "SR,$0,S ROOF  -PLACE 7030 SIZE IN COMM REGION",
        #     the size where the REST of MCP looks for it
        #   mcp_comm_size_fixture_and_listing_agree
        #   mcp_placed_at_dest_first
        # All three pass on the run that broke this one.
        #
        # THE PRECEDENT IS mcp_qsav_last_after_swap, retired on
        # 2026-10-23 because its count tracked the IMAGE SIZE.  The
        # lesson is the same and worth stating once more: a check
        # pinned to a register's value at the end of a run is pinned
        # to WHERE THE RUN STOPS, and the whole point of this project
        # is that the run keeps going further.  Pin a check to
        # STORAGE THE PROGRAM WROTE ON PURPOSE, not to a register it
        # happened to leave alone.

        # >>> AND MCP PUT THE SIZE WHERE THE REST OF MCP LOOKS <<<
        # Printed p.15 line 23 is "SR,$0,S ROOF  -PLACE 7030 SIZE IN
        # COMM REGION", the row after the LR above.  S ROOF is a
        # communication-region symbol at 002162.00, read off printed
        # p.15's own binary output (the deck says so), and SR stores
        # a refill into bits 0-17 of the addressed half-word -- so
        # 98,304 lands back as 0x6000000000000000, the same shape it
        # had in X S ROOF.
        #
        # THIS IS MCP USING A NUMBER IT MEASURED ITSELF.  Printed p.2
        # sized core by running a clearing loop off the end of it and
        # taking the Address Invalid; eleven pages later the answer is
        # in the communication region for the supervisor to use.
        #
        # THE REST OF THE WORD IS ZERO, and for one commit it was the
        # fixture's filler instead.  S ROOF is the eleventh word of
        # the comm region, so whatever the record carries there
        # arrives first and SR then overwrites only bits 0-23.  The
        # record carries ZEROS there now, deliberately -- see
        # strap/prosa.py, where a filler word six places earlier had
        # MCP believing in a console on a channel made of 0x5A5A.
        ("mcp_size_in_comm_region", str(0o2162), 98304 << 46),

        # >>> WHERE MCP STOPPED, AND IT STOPPED FOR A GOOD REASON <<<
        # X ERR AD, printed p.13 line 37, "-LOCATION OF ERROR +1.0".
        # Every error site does "SIC,X ERR AD" before branching to
        # X ERROR, so this half-word names the site.
        #
        # THIS USED TO BE ASSERTED ZERO -- "no error site ever ran" --
        # and that was true only because the run stopped in MCP's
        # delay loop before any of printed pp.15-18 executed.  Now it
        # names **printed p.17's "-NO IOCD DETECTED"**, which is the
        # correct diagnosis of this machine: p.17 hunts the buffer for
        # an IOCD card, there are none, "CB+,$4,X13 A A" exhausts the
        # search, and line 15's SIC and line 16's "B,X ERROR" report
        # it.  **MCP ran its whole initialization and told us what is
        # missing.**
        #
        # The stored value is a 19-bit half-word address in bits 0-18
        # of the word, which is why this is written as a shift rather
        # than as a number nobody could check.
        # X ER 16C is printed p.17 line 15's "SIC,X ERR AD", and the
        # value stored is the instruction counter ONE WORD past it --
        # printed p.13 line 37 calls the datum "LOCATION OF ERROR
        # +1.0", and one word is two half-words.  Derived from the
        # assembled image rather than written as a number, so it moves
        # if the page is ever re-transcribed.
        #
        # >>> AND THE SITE MOVED ON 2026-10-22, from printed p.17's
        # "NO IOCD DETECTED" to printed p.19's.  With five IOCD cards
        # at X IN END the hunt succeeds, all five are processed, and
        # the run ends at line 25's "BZAEZ,X ERROR  -NOT AN IOD CARD
        # EITHER" -- the sixth group is zeros and is neither.  THE
        # CONSOLE PRINTS THE SAME NUMBER: the message checked below
        # reads "000760|0 INCORRECT CARD TYPE". <<<
        # >>> AND SINCE THE DECK GREW AN IOD CARD IT IS ZERO AGAIN,
        # WHICH IS THE STRONGEST FORM OF THIS CHECK.  Every error
        # site in MCP does "SIC,X ERR AD" before branching, and the
        # instruction counter is never zero inside the program, so
        # ZERO MEANS NO ERROR SITE EVER RAN.  The run before this one
        # ended at printed p.19 line 25's "NOT AN IOD CARD EITHER";
        # the card deck is terminated now and that row is not
        # reached. <<<
        #
        # >>> AND IT IS NO LONGER ZERO: WITH TRANSMIT BACKWARD BUILT,
        # MCP GETS PAST THE TABLE RELOCATION, FINDS THE CONSOLE,
        # TYPES ITS DATE MESSAGE -- and then its I/O TEST finds a
        # status bit on. <<<
        #
        # printed p.3 line 28 is "X7 3  BRZ,0.0  -SUCCESSFUL" and
        # line 29 "X ERR 05  SIC,X ERR AD" at 000067.00, so this is
        # the shared I/O status routine the whole program calls --
        # printed p.30 line 13 and printed p.34 line 13 both do
        # "SIC,X7 3 / B,X7 1  -IO TEST" after a WRITE.  printed p.7
        # line 12's error table maps X ERR 05 + 1.0 to X MSG 05,
        # "UNSUCCESSFUL COMPLETION".
        #
        # >>> IT WAS ZERO FOR TWO COMMITS.  WITH PRINTED p.45 IN THE
        # IMAGE IT IS NOT, AND WHAT IT HOLDS IS AN ADDRESS THAT NAMES
        # THE ERROR. <<<
        #
        # Until 2026-10-23 this check said "NO ERROR SITE EVER RAN",
        # and that was true while the run stopped dead at S BRK8 on a
        # zero word.  printed p.45 fills S BRK8, MCP runs the whole
        # UNCODE path, and it comes back out through printed p.25
        # line 44 -- "B,X 223  -NOT IOD OR REEL CARD" -- whose target
        # is line 46's "SIC,X ERRAD / B,X ERROR  -ERROR IN UNCODE".
        #
        # SIC and the branch after it are ONE 64-bit instruction
        # (Reference Manual printed p.41), so the counter SIC stores
        # points at the half word after the pair: 001441.40, which
        # printed p.25 line 48 names X224.  The stored form is that
        # bit address in bits 0-23, so the word reads
        # 0x00C8600000000000.
        #
        # SO THE CHECK NOW NAMES THE ERROR SITE INSTEAD OF DENYING
        # ONE.  It is a ratchet with a reason, not a weakening: any
        # OTHER error site, and any return to zero, fails it.
        #
        # >>> AND IT IS ZERO AGAIN, 2026-10-24, FOR THE OPPOSITE
        # REASON TO THE FIRST TIME. <<<
        #
        # It was zero because MCP stopped dead on a zero word before
        # any error site ran.  It is zero now because MCP DOES NOT
        # TAKE THE ERROR EXIT AT ALL: the card is accepted.
        #
        # THE REJECTION WAS THE MODEL'S, NOT MCP'S.  printed p.38
        # line 26 compares the card's type field against Y TYPMK, and
        # the field MCP had to compare was one character long -- the
        # crossing-field store refusal above (mcp_ucbf1_*) stopped
        # the Hollerith converter after ten characters, so "IOD"
        # arrived as "I".  With the store built, mcp_ucbf2_0 is
        # bit-for-bit Y IOD MK, line 28's "BZAEZ,Y MKEAR" is not
        # taken, and printed p.25 line 44's "B,X 223  -NOT IOD OR
        # REEL CARD" -- the branch that filled this word -- is never
        # reached.
        #
        # SO THIS CHECK HAS SAID THREE DIFFERENT THINGS and the third
        # is the strongest: no error site ran, on a run that reaches
        # printed p.54's tape IOD routine and executes five swaps.
        # Any return to the error path fails it.
        #
        # >>> AND ON 2026-10-25 IT RETURNED TO THE ERROR PATH, WHICH
        # IS THE FOURTH THING AND THE BIGGEST. <<<  printed p.80
        # completed MCP's ASSIGN routine, so ASSIGN now RUNS TO ITS
        # OWN RETURN -- p.80 line 31's "B,1.00($15)" -- and lands
        # back in printed p.27, its caller, at 001470.00.  Two
        # instructions later p.27 line 12 is "XERR24  SIC,X ERR AD"
        # and line 13 is "BZXCZ,XERROR  -IF ASSIGNMENT ERROR".
        #
        # THE BRANCH IS TAKEN, AND THIS WORD IS WHAT THE SIC STORED:
        # 001471.40, the instruction after it.  That is not a failure
        # of the model -- it is MCP's own diagnostic recording where
        # the error was detected, in the field the routine exists to
        # fill.  The fixture's machine cannot satisfy the assignment
        # and MCP says so in the way it was written to.
        ("mcp_x_err_ad", str(sym("XERRAD")),
         # 001471.40 in bits 0-23, which is printed p.27 line 13.
         0x00CE600000000000),

        # >>> THE CARD TYPE, OUT OF MCP'S OWN HOLLERITH CONVERTER <<<
        #
        # These three checks are the reason the model can store a VFL
        # field that crosses a word boundary.  They were written
        # BEFORE the arm was built, with the values computed in
        # Python from strap/iocd.card_text, and they failed in the
        # exact way a stuck output pointer fails.
        #
        # THE PATH.  printed p.38 lines 11-15 call S CA6 with a
        # three-word block: the card's address, "CF,80" -- eighty
        # columns, printed as 000120 and reproduced bit-exactly by
        # decks/mcp_bootstrap_p38.strap -- and Y UCBF1 (002327.00) to
        # convert into.  printed p.43 is the converter: line 19's
        # "CT0011(V+I)(BU,3)" and line 23's "LF(V+I)(BU,9)" read
        # TWELVE BITS -- one card column, twelve rows -- line 49's
        # "ST(V+I)(BU,6,6),.6($5)" stores SIX, and line 52's
        # "CB,$4,Q P" counts the eighty down.
        #
        # SIXTY-FOUR IS NOT A MULTIPLE OF SIX.  Character ten lands
        # at bits 60-65 of Y UCBF1 and straddles the word boundary.
        # The model refused that store -- bsv/StretchExecute's ST arm
        # called setOpInvalid on any crossing field -- and a
        # suppressed VFL operation also skips its progressive index
        # advance, so $5 STAYED at bit 60 and every one of the
        # remaining seventy characters was refused at the same place.
        #
        # MEASURED BEFORE THE FIX: ucbf1_0 = 0xc800000000000390,
        # ucbf1_1 = 0, ucbf2_0 = 0xe400000000000000.  The card is
        # punched "B", eight blanks, "IOD" (strap/iocd.py, columns
        # 10-13 per C22-6728 printed p.88), so that is "B" + blanks +
        # "I" and then nothing: EXACTLY TEN CHARACTERS, and ten is
        # the word boundary and nothing else.
        #
        # THE INPUT SIDE IS THE SELF-CHECK THAT MAKES "TEN" MEAN THE
        # BOUNDARY.  Twelve bits per column into a 64-bit word
        # straddles too -- column 6's nine-bit LF sits at bits 63-71 --
        # so if crossing LOADS were refused as well, $4 would have
        # stuck at column 6 and character 9 would be a blank.  It is
        # 0o71, "I", read from column 10.  Crossing loads worked; the
        # store was the sole governor.
        #
        # AND MCP IS THE PRIMARY SOURCE.  Rule 4 wants an encoding or
        # a semantic from a document, and printed p.43 line 49 is one:
        # IBM's own operating system stores a crossing VFL field in
        # its card converter, so the refusal was never a documented
        # restriction -- it was a one-write-per-rule toolchain limit,
        # recorded as such in bsv/StretchExecute's header next to
        # "Transmit moves only one word", which was the same limit
        # and was lifted the same way.
        #
        # WHAT EACH CHECK IS FOR, and the two are not
        # interchangeable:
        #  * ucbf1_0's low four bits are the TOP of character ten --
        #    "O", 0o46 = 100110 -- and they live in the HEAD word, so
        #    this check catches a store that wrote NEITHER word.
        #  * ucbf1_1's top eight bits are the BOTTOM of character ten
        #    and all of character eleven, "D" = 0o64, and they live
        #    in the TAIL word -- so this is the check that catches a
        #    store that wrote the head and dropped the tail, which is
        #    the failure StretchStorage's one-clock tail exists to
        #    avoid.  THE INJECTION IS THAT: drop the
        #    st.writeWordTail call in StretchExecute's ST arm and
        #    ucbf1_0 passes while ucbf1_1 fails.
        #  * ucbf2_0 is the payoff: S BRK8 (printed p.38 lines 16-20)
        #    breaks the card from Y UCBF1+.54 -- bit 54, character
        #    ten, column 10, where C22-6728 printed p.88 puts the
        #    card type -- into Y UCBF2 (002337.00).  Its expected
        #    value 0xe66d000000000000 IS NOT A PREDICTION FROM THE
        #    CARD: it is the value MEASURED at Y IOD MK, the literal
        #    printed p.38 line 26's "K(BU,48),Y TYPMK($13)" compares
        #    against.  So this check says the type field MCP reads
        #    out of the card is bit-for-bit the type mark MCP tests
        #    it with.
        # >>> DERIVED FROM THE CARD, NOT RECORDED FROM A RUN. <<<  These
        # two words used to be hardcoded against a card whose statement
        # was blank.  The fixture now punches a real IOD card, so the
        # buffer legitimately has content -- and rather than re-record
        # two magic numbers, they are COMPUTED from the card text, which
        # turns the check into a test of SCA6's conversion and cannot
        # drift when the card changes.
        #
        # SCA6 packs the card as a CONTINUOUS six-bit stream, not ten
        # characters per word with padding: word 0's low four bits carry
        # the top of character eleven.  Established by computing it both
        # ways and comparing against the model (0xca4ce7a74a400399
        # matches the continuous form exactly and the padded form in all
        # but its low nibble).
        #
        # AND THE SEPARATOR MAPS TO THE A-SET COMMA, which is the
        # measured disagreement with `C22-6678` Appendix F recorded in
        # strap/iocd.py: the character cards.py punches 0-3-8 comes out
        # of SCA6 as code 27, the comma, not code 12, the quote.  With
        # code 27 substituted both words match bit for bit; with code 12
        # word 1 does not.
        ("mcp_ucbf1_0",
         str(sym("XBSEND") + _image_index("002327")), _sca6_word(0)),
        ("mcp_ucbf1_1",
         str(sym("XBSEND") + _image_index("002327") + 1), _sca6_word(1)),
        ("mcp_ucbf2_0",
         str(sym("XBSEND") + _image_index("002337")), 0xe66d000000000000),

        # >>> THE ONE SWAP MCP EXECUTES, OBSERVED IN STORAGE. <<<
        #
        # printed p.43 line 53 is "Q FIN  SWAPI,6,Q SAV,$1  -RESTORE
        # INDEXES" and StretchCore announces it -- "SWAP started at
        # half-word 2649, 6 words" -- but an announcement is a
        # $display, not a check.  These two read what it left.
        #
        # Q SAV is six words at 002472 and line 10's "TI,6,$1,Q SAV"
        # filled it on the way IN with index registers 1-6.  The SWAP
        # on the way out EXCHANGES them, so Q SAV ends holding what
        # the conversion loop left in $1-$6, not what the TI put
        # there.  A model that refused the SWAP again -- which is
        # what every version before 2026-10-23 did -- would leave the
        # TI's values standing, and these two checks are the only
        # place in the suite where the difference is visible on the
        # REAL program rather than on swap_scope's synthetic data.
        #
        # EXPECTED VALUE MEASURED, NOT PREDICTED.  Q SAV+0 decodes as
        # an index word (value 0-23, sign 24, flags 25-27, count
        # 28-45, refill 46-63): value 000000.00, COUNT 7.  Seven is
        # what the conversion loop left in $1, not what line 10's TI
        # put there.
        ("mcp_qsav_first_after_swap",
         str(sym("XBSEND") + _image_index("002472")), 0x00000000001C0000),

        # >>> AND Q SAV+5 IS NOT CHECKED, DELIBERATELY. <<<
        #
        # It was, for one commit, at 0x0001200011480000 -- value
        # 000004.40, count 1106.  Adding printed p.48 moved the count
        # to 1125, EXACTLY NINETEEN MORE, which is the number of words
        # p.48 adds to the image.  So $6's count tracks the image
        # SIZE, and a check on it would have to be re-measured on
        # every page transcribed and would say nothing new each time.
        #
        # This project has been bitten by a drifting check before --
        # two comm-region checks that walked onto MCP's own working
        # storage as the image grew -- and the lesson is the same
        # one: a ratchet nobody can predict is a ratchet nobody reads.
        # Q SAV+0's count does not move, and one word is enough to
        # say the swap ran.

        # >>> AND THIS IS THE PROOF THAT MCP *USED* THE SWITCHES,
        # which is a different claim from "the read returned". <<<
        #
        # X LR IN is the three-word buffer printed p.21 line 26
        # reserves and printed p.22 line 5 reads the switches into.
        # After initialization its first word reads
        #
        #     0xAAAAAA00AAAAAA00
        #
        # which is BCD ZERO in six nibbles across bits 0-23 and six
        # more across bits 32-55 -- and those are not arbitrary
        # ranges.  C22-6678-1 printed p.29: "Set up the time in
        # binary keys 0-23, and the date in binary keys 32-55."  The
        # nibble is MCP's own: printed p.24 line 13 is
        # "X VZER  LFI(BU,4),(2)1010,46  - BCD ZERO", under the
        # banner "replace a blank character with a BCD zero".
        #
        # SO THE WHOLE PATH IS VISIBLE IN ONE WORD: the switches
        # were read (all zero -- printed p.22 line 12's
        # "KFI(BU,24),0,40  -NO TIME ENTERED"), MCP took the
        # no-time-entered branch, and its blank-to-BCD-zero routine
        # filled exactly the two fields p.29 names.  A model that
        # returned the card reader's image instead would have to
        # produce this by accident.
        # >>> AND THE TIME FIELD IS NO LONGER ALL BLANK, 2026-10-25,
        # BECAUSE MCP NOW COMPUTES THE TIME. <<<
        #
        # This expected every one of the twelve digits to be a BCD
        # zero, and that was right for a machine that REFUSED printed
        # p.24's time conversion: `/`, `CV` and `LTRCV` were
        # unimplemented, line 30's "ST(BU,24),XLRIN" never ran, every
        # position stayed blank, and the fill routine wrote 0xA into
        # all twelve.
        #
        # With the three operations built, a probe on word 540
        # (octal 1034, the address the listing itself prints as
        # ST(BU,24),XLRIN's operand) shows fifteen writes, and they
        # tell the whole story:
        #
        #    4: 0000010000000000   <- ONE 24-bit store: 0x000001
        #    5: a000010000000000   }
        #    6: aa00010000000000   }  the blank-fill, ONE NIBBLE AT
        #    7: aaa0010000000000   }  A TIME, SKIPPING position 5
        #    8: aaaa010000000000   }  because it is no longer blank
        #    9: aaaaa10000000000   }
        #   10-15: ...aaaaaa00        the date field, same routine
        #
        # Write 4 is the conversion depositing 00:00:01.  The fill
        # then replaces only the BLANK digits, which is why five
        # zeros read 0xA and the seconds' units digit reads 1.
        # decks/vfl_convert.strap confirms the arithmetic
        # independently: the same eleven instructions on a clock of 1
        # produce 0x000001, and on 45296 produce 0x123456.
        #
        # >>> THIS CHECK IS NOW TIMING-SENSITIVE, AND THAT IS A REAL
        # COST. <<<  The last digit is the SECONDS READ OFF THE
        # MODEL'S OWN TIME CLOCK during the boot, so anything that
        # changes how much simulated time the boot takes -- the
        # interval timer, the look-ahead of stage 3, a different step
        # cap -- will change it.  If this check fails after a TIMING
        # change, read the digit before assuming a regression: a
        # value of the shape 0xaaaaaN00aaaaaa00 is this same success
        # with a different clock.  The date field staying all-blank
        # is the part that must not move.
        ("mcp_switch_words_became_bcd_zero",
         str(ipl_hw("XLRIN") // 2),
         (sum(0xA << (60 - 4 * i) for i in range(5)) | (0x1 << 40))
         | sum(0xA << (28 - 4 * i) for i in range(6))),  # keys 32-55, date

        # >>> AND MCP WROTE THE CONSOLE'S CHANNEL INTO ITS
        # COMMUNICATION REGION. <<<
        #
        # S YCOCH is the comm-region word that names the console.
        # It holds 35 in bits 0-18, and 35 is where
        # bsv/StretchIO.bsv's chanConsole is -- MCP learned that from
        # the IOCD cards it read off the tape, since nothing in this
        # fixture tells it directly.
        #
        # THE DECODING IS NOT LOAD-BEARING HERE, which is why this
        # check is worth having: printed p.21 line 5 is
        # "X DATE  LV,$15,S YCOCH  -GET CONSOLE CHANNEL" and every
        # console WRITE in the program addresses "0.0($15)".  The
        # date message checked above came out, so $15 IS the console
        # whatever one calls its bit fields.
        #
        # S YPRCH, the printer slot, holds the same 35 and that is
        # NOT explained.  strap/prosa.py's IOCD deck puts the printer
        # on channel 33, and printed p.25 lines 22-24 store a
        # DIFFERENCE ("SX,$10,$R" / "-(BU,19),S XCHAN,45" /
        # "ST(BU,19),S YPRCH"), not a channel address.  Left
        # unchecked and written down rather than guessed at.
        # AND THE TWO WORDS THE SWITCH REGISTER DELIVERED UNTOUCHED.
        # The testbench sets console switch words 1 and 2 to markers
        # (see console_switches below); MCP reads all three into
        # X LR IN and never looks at these two, because they are
        # p.29's NUMERIC switches and only the I/O-status-report path
        # reads them.  So they are still there at the end of the run.
        #
        # THIS IS THE CHECK THAT DISCRIMINATES.  Everything else about
        # the console READ is satisfied by zeros, and the first
        # injection written against it -- serving the READ out of the
        # card reader's image, which is what the model did before the
        # switch register existed -- SURVIVED, because both images
        # were zero.  With the markers it fails on these two words.
        ("mcp_switch_word1_arrived",
         str(ipl_hw("XLRIN") // 2 + 1), 0x5A5A5A5A5A5A5A5A),
        ("mcp_switch_word2_arrived",
         str(ipl_hw("XLRIN") // 2 + 2), 0xA5A5A5A5A5A5A5A5),

        ("mcp_console_channel_in_comm_region",
         str(ipl_hw("SYCOCH") // 2), 35 << (63 - 18)),

        # AND THIS IS THE CONTROL WORD THE LINE ABOVE TRIPPED ON.
        # printed p.3 line 23 is "X7 1 CCW  CCW,0($15),X IPL BS", so
        # X IPL BS holds MCP's own copy of the channel's control word
        # as of the last I/O TEST -- the one that failed.  Checking it
        # here turns the diagnosis into a MEASUREMENT: bits 18-24 are
        # the status field (Reference Manual printed p.107, Figure 35,
        # and its prose: 18 unit ready, 19 exchange program check, 20
        # unit check, 21 end exception, 22 end of operation, 23 channel
        # signal, 24 suppress end of operation).
        #
        # printed p.3 line 27's "CT0011(BU,5),X IPL BS+.19" tests bits
        # 19-23 and line 28 returns only if they are all zero, which is
        # the same set p.107 groups: "bits 19 through 23 have
        # corresponding indicators in the indicator register".
        #
        # MEASURED 0x008A920000000000, AND EVERY FIELD OF IT HAS A
        # REASON.  This was derived from the model's source first and
        # then measured, in that order, because the two readings before
        # it were derived and WRONG -- see docs/NEXT.md.
        #
        #   bits 19 and 22, EXCHANGE PROGRAM CHECK and END OF
        #     OPERATION, both ON.  StretchExecute's "wrongUnit" guard
        #     leaves the console out of RD's legal units and sets
        #     exactly these two, citing Reference Manual printed p.113
        #     ("an instruction is received that the selected unit is
        #     not designed to perform, such as a READ given to a
        #     printer").  THIS IS THE FAILURE, and the instruction is
        #     printed p.22 line 5's "RD(SEOP),0.0($15),X DCW 2" --
        #     a three-word read of the operator's console switches,
        #     which this model does not have.  printed p.150: "A READ
        #     instruction received by the console with the keyboard not
        #     enabled is automatically terminated when the three words
        #     scanned from the switches have been sent to the
        #     exchange", and the console's word weight is 3.
        #
        #   bits 20, 21, 23 and 24 OFF -- no unit check, no end
        #     exception, no channel signal, and SEOP already cleared.
        #     So the WRITE before it finished cleanly; the message came
        #     out and the model says so in the same word.
        #
        #   DATA WORD ADDRESS = X DATE 1 + X DATE K, one past the end
        #     of the date message, which is the only field here that
        #     could have come from anywhere else.  The exchange steps
        #     it per word and the program check does not touch it, so
        #     it still holds where the chained WRITE stopped.  X DATE K
        #     is printed p.21 line 42's "SYN,$-X DATE 1" -- five words
        #     -- and five is how many console words this test checks
        #     above.  It also lands exactly on X IO, because printed
        #     p.22 opens with "SLC,(8)1052.0" right after the message.
        #
        #   COUNT, REFILL, CHAIN all zero: the chain's last control
        #     word, printed p.21 line 30's "X DCW 1  CW,X DATE 1,X
        #     DATE K,0", is exhausted.

        # >>> AND IT READS 0x0087C00000000000 NOW, WHICH IS THE SAME
        # WORD WITH THE FAILURE TAKEN OUT.  The switch register is
        # built, so the console READ runs: data word address
        # X LR IN + 3, count stepped to zero, and NOT ONE STATUS BIT
        # ON.  EPGK and EOP are gone -- the two bits that were the
        # whole diagnosis -- and bits 20, 21, 23, 24 stay off as they
        # already were.  The last I/O TEST on printed p.3 therefore
        # returns through "X7 3  BRZ,0.0  -SUCCESSFUL". <<<
        #
        # THE OLD VALUE AND WHY IT WAS WORTH KEEPING is below, because
        # it is the only reason the gap was found at all:
        #
        #   0x008A920000000000 -- EXCHANGE PROGRAM CHECK (bit 19) and
        #   END OF OPERATION (bit 22) on, every other status bit off,
        #   data word address X DATE 1 + X DATE K.  printed p.3 line
        #   23's "CCW,0($15),X IPL BS" had put MCP's own copy of the
        #   control word in storage, so the machine was already
        #   holding the answer; nothing had to be added to the model
        #   to see it.  The data word address said the date WRITE had
        #   finished cleanly, and bits 19 and 22 are exactly the pair
        #   StretchExecute's "wrongUnit" guard sets -- which named the
        #   failing instruction without a trace.
        ("mcp_x_ipl_bs_control_word", str(sym("XIPLBS")),
         (ipl_hw("XLRIN") // 2 + 3) << 46),   # data word address, no status

        # The indicator register, word 11: RZ, XVZ, XF and **OP**.
        #
        # THIS USED TO READ 0xA040 -- RZ, XVZ, XCZ, with OP CLEAR --
        # AND THAT WAS AN ARTIFACT.  The value is exact on purpose,
        # as a ratchet, and the ratchet did its job: adding the disk
        # changed it, and chasing why found a gap that had been there
        # all along.
        #
        # WHAT THE OLD VALUE WAS HIDING.  Without a disk at channel 0,
        # printed p.4 line 29's RELEASE DISK was rejected with Unit
        # Not Ready, line 30 branched to X ERR 12 -- which is on
        # printed p.15, OUTSIDE the loaded image -- and the machine
        # ran into zeros.  A zero half-word is BRANCH ENABLED, which
        # enables the interrupt system with UNRJ pending; the
        # interrupt was taken and it RESET THE INDICATOR REGISTER.
        # Everything the bootstrap had set was wiped, including OP,
        # and what the test measured was the register AFTER that
        # reset.  Three result indicators and a clean OP bit, all of
        # it meaningless.
        #
        # >>> NO OP BIT.  THE MODEL REFUSES NOTHING MCP EXECUTES. <<<
        #
        # That sentence was in this file before and was not true: it
        # was reading the indicator register after an interrupt had
        # reset it (see below).  It is true now, and it took closing
        # TWO gaps that the wipe had been hiding, both localised by
        # bisecting the step cap and then reproduced standalone:
        #
        #   printed p.4 line 28, "T,$11,X BUFER($X1),X BS END  -MOVE
        #   MCP IPL", an eleven-word direct-count TRANSMIT.  Built
        #   2026-10-18.
        #
        #   printed p.4 line 23, "LVS,$X1,$X12,$X14  -WORDS PRECEEDING
        #   MCP", multiple indexing.  Built 2026-10-19.  The two
        #   belong together: $X1 is the index the TRANSMIT five rows
        #   later uses to find MCP inside the buffer.
        #
        # AND AD IS THE TRANSMIT NOW RUNNING, which is the useful
        # detail.  Line 24 loads index 11 from the PROSA record's
        # dictionary and THIS TAPE HAS NO PROSA ON IT -- mktape.py
        # writes the 369-word bootstrap and a tape mark, nothing more
        # -- so the dictionary is zeros and the count field is zero.
        # Reference Manual printed p.30: "A count field of zero is
        # interpreted as 2^18... such a count is never valid.  It is
        # not detected, however, until the data transmission actually
        # encounters an invalid or protected address."  The transmit
        # therefore walks up out of installed core and stops with
        # Address Invalid, exactly as the manual describes.  AD here
        # is the tape being short, not the model being wrong.
        #
        # `mcp_x_err_ad` still reads zero on the line below: AD is an
        # indicator, X ERR AD is MCP's own variable, and no error site
        # ran.
        # The indicator register at the stop.  Five of the six are
        # ordinary result indicators left by the last few index and
        # VFL operations of the ERROR ROUTINE.  The sixth is **OP**,
        # and it is attributable and expected: printed p.5's error
        # routine does not know which channel the console is on, so it
        # walks all 32 of them with a deliberately invalid CTL, then
        # LOC(SEOP) to see which answer TAPE, then GONG to find the
        # console.  **Exchange LOC and GONG are both unimplemented**
        # (docs/boot_plan.md M3++ item A4 builds them with the
        # console), so a machine with no console makes MCP walk the
        # whole exchange and be refused.  AD is the same walk reaching
        # channels with nothing at them.
        # XCZ IS GONE AND THAT IS THE HEADLINE.  It was set because
        # the channel walk EXHAUSTED its count of 32 without finding
        # a console: printed p.5 line 54's "CBH,$X1,X1AERR  -NOT DONE
        # TESTING" counted down to zero.  Now the walk STOPS at
        # channel 35, so the count is still positive -- which is the
        # arithmetic evidence that **MCP found the console**, beside
        # the message it then printed.
        #
        # >>> OP IS GONE.  THE MODEL REFUSES NOTHING MCP EXECUTES. <<<
        #
        # It was M+MG, isolated rather than guessed: printed p.5 lines
        # 15 and 17 are "M+MG(BU,48,8)" and "M+MG(BU,8,8)", the two
        # adds that fill the error address into the console message,
        # and a four-line scratch deck reproduced the OP on either of
        # them alone.  The model's VFL arm implemented L, ST, +, M+, K
        # and M+1; the MG forms were not among them.  M+MG is the
        # seventh arm as of 2026-10-19 (Reference Manual printed p.62,
        # decks/m_plus_mg.strap), and this bit going out is the whole
        # evidence that the arm is reached by the real program.
        #
        # THE SENTENCE ABOVE HAS BEEN TRUE BEFORE AND WAS NOT.  Twice.
        # Once because an interrupt had reset the register (see
        # above), once because fixing the TRANSMIT left LVS standing.
        # What makes it different this time is that the bit went out
        # without the register being wiped and without any other bit
        # moving: XE, XVGZ, RGZ and AD are all unchanged.
        #
        # "+MG", the to-accumulator form, is still unimplemented, and
        # tests/audit_opcode_coverage.py still cannot see that -- it
        # compares what the assembler EMITS against what a deck USES
        # and says nothing about what the model EXECUTES.
        #
        # AD was READ, not measured: printed p.15 line 20 takes the
        # communication region's size out of the PROSA record with
        # "LC,$0,X BUFER+.32($9)" and line 21 transmits that many
        # words.  The size came from strap/prosa.py, which chose the
        # dictionary and left everything else as filler, so the count
        # was arbitrary and the transmit ran until it left installed
        # core.  This comment ended "A fixture artifact; it goes away
        # when the record is real."
        #
        # >>> IT WENT AWAY ON 2026-10-22, and the prediction is the
        # reason it is quoted rather than deleted.  The record now
        # carries a comm-region descriptor whose bit-32 field is the
        # region's size, LC loads FIFTEEN instead of zero, the
        # transmit moves fifteen words, and ADDRESS INVALID IS NO
        # LONGER RAISED ANYWHERE IN THE RUN.  AD is out of the
        # expected set below. <<<
        #
        # >>> OP IS BACK, AND THIS TIME IT NAMES A MISSING
        # INSTRUCTION RATHER THAN A FIXTURE ARTIFACT.  printed p.19
        # line 41 is "TB,3,0.0($11),0.0($13)  -MOVE BIASED CTS" -- a
        # TRANSMIT BACKWARD -- and StretchExecute's Transmit arm
        # refuses it outright: "if (t.backward == 1 || t.swap == 1)
        # ind = setOpInvalid(ind)".  Reference Manual printed p.30
        # specifies it ("modifier bit 55.  A zero specifies forward
        # transmission; a one specifies backward"), so the gap is an
        # unbuilt arm and not an unknown.
        #
        # AND IT IS ON THE CRITICAL PATH.  Without that move the
        # channel status table is never relocated, so printed p.20's
        # walk looks for a console in a table that was not brought
        # along -- which is why the run halts where it does. <<<
        # >>> OP IS GONE.  It was printed p.19 line 41's "TB" -- a
        # TRANSMIT BACKWARD the model refused -- and the arm is built
        # now (Reference Manual printed p.30, "obtained by
        # DECREMENTING the previous addresses by one").  The channel
        # status table is relocated, printed p.20 finds the console
        # it was told about, and the run goes on. <<<
        # >>> AND IT MOVED AGAIN, 2026-10-23, BECAUSE THE RUN GOES
        # FURTHER AGAIN.  AE out, XCZ back in; MOP, RGZ, XVGZ and XH
        # unchanged.  All five are RESULT indicators -- the last index
        # and arithmetic operations' outcomes -- and the run now ends
        # one subroutine call deeper than it did, so there is no
        # reason for them to have stayed the same.
        #
        # THE HISTORY, because the value is a ratchet and a ratchet
        # that is silently re-fitted is not one:
        #   0xA040  RZ, XVZ, XCZ        -- an ARTIFACT, read after an
        #                                  interrupt reset the register
        #   0x9424  XCZ, XVGZ, XE, RGZ, AE   -- run ends in X ERROR
        #   0x1324  XH, XVGZ, MOP, RGZ, AE   -- run ends at S PRIME
        #   0x9320  XCZ, XVGZ, MOP, RGZ, XH  -- run ends at S CA6
        #   0x9240  XCZ, XVGZ, RZ, XH        -- run ends at S BRK8
        #
        # WHAT THE CHECK IS STILL FOR is the bit that is NOT here:
        # OP is clear, so the model still refuses nothing MCP
        # executes -- now through printed p.38's UNCODE subroutine
        # AND printed p.43's Hollerith-to-BCD conversion, including
        # p.43's own SWAPI, which the model would refuse if the run
        # reached it.  It does not: line 53's SWAP is on Q FIN, the
        # RESTORE path, and the run leaves through the call to
        # S BRK8 before it gets there.
        #
        # RZ REPLACED MOP AND RGZ.  All three are result indicators;
        # RZ is "R register zero" and the last thing S CA6 does
        # before the call is arithmetic on $R, so the set moving is
        # what going one subroutine further looks like.
        # >>> THE SET MOVED AGAIN WITH printed p.45, AND OP IS IN IT.
        # <<<  The run no longer stops at S BRK8; it finishes through
        # MCP's own error routine, which ends at printed p.6 line 1's
        # "BD,$" -- X6ERR having displayed X ERRAD in the CE console
        # -- so the indicators are whatever that path leaves.
        #
        # OP IS SET AND IT IS NOT printed p.45's SWAP.  tests/gen_tb's
        # `op_trail` says the bit is first raised at half-word 1304,
        # 001214.00, after six million steps -- printed p.24's TIME
        # CONVERSION -- and a CONTROL RUN WITH p.45 TAKEN BACK OUT
        # raises it at the same address.  So the refusal predates this
        # page.  docs/NEXT.md carries which instruction it is.
        #
        # >>> AND OP IS OUT OF THE WORD AGAIN, 2026-10-24, WITHOUT
        # THAT REFUSAL HAVING GONE AWAY. <<<  The crossing-field store
        # (mcp_ucbf1_*) carries the run past MCP's error exit and into
        # printed p.54's tape IOD routine, and something on that path
        # rewrites the indicator register; `op_trail` still reports
        # exactly one rise, still at half-word 1304.  So this check no
        # longer witnesses that refusal AND THE TRAIL STILL DOES,
        # which is why op_trail stays on.
        #
        # IT IS ALSO A NEGATIVE RESULT WORTH THE LINE: the p.24
        # refusal is NOT the crossing-field store.  Building the store
        # would have cleared it if it were, and the trail is
        # unchanged.  docs/NEXT.md carries what that leaves.
        #
        # THE HISTORY CONTINUES (see the ratchet above):
        #   0x1248  AL, RZ, XH, XVGZ    -- run ends at L NORM, a SYN
        #                                  for a page not transcribed
        #   0x1524  AE, MOP, RGZ, XE, XVGZ -- printed pp.55-58 are in
        #                                  the image; the run goes
        #                                  THROUGH L NORM and ends at
        #                                  T ASIGN
        #   0x200C544  AE, MOP, RZ, XCZ, XE, XF, XVLZ -- printed
        #                                  pp.61-65 too; the run
        #                                  EXECUTES MCP's ASSIGN
        #                                  entry and ends at T A9
        #   0x009544   AE, MOP, RZ, XCZ, XE, XVGZ -- printed pp.66-72
        #                                  as well, so T A9's own
        #                                  code runs: XF out, XVLZ
        #                                  out, XVGZ in.  All six are
        #                                  result indicators and the
        #                                  run is 16 MILLION STEPS
        #                                  longer, so there is no
        #                                  reason for them to have
        #                                  stayed the same.
        #   0x200A448  AL, RZ, XCZ, XE, XF, XVZ -- printed p.73 too.
        #                                  The step count barely
        #                                  moves but the SET does:
        #                                  the three that leave (AE,
        #                                  MOP, XVGZ) and the three
        #                                  that arrive (AL, XF, XVZ)
        #                                  are what a bubble sort
        #                                  over an index leaves
        #                                  behind -- XF and XVZ are
        #                                  set by the CBH pair on
        #                                  lines 16 and 18, and AL by
        #                                  the KF on line 11 that
        #                                  decides each swap.
        #   0x009448   AL, RZ, XCZ, XE, XVGZ -- printed p.74 too, and
        #                                  only TWO instructions more
        #                                  ran: its lines 55 and 56,
        #                                  "T AREJX LVI,T X1,T MESSY"
        #                                  and "SV,T X1,0.0(T IXE)".
        #                                  An LVI of 004451.0 into an
        #                                  index leaves that index
        #                                  GREATER than zero, so XVZ
        #                                  goes out and XVGZ comes
        #                                  in, and the SV that
        #                                  follows clears XF.  TWO
        #                                  ROWS, THREE INDICATOR
        #                                  BITS, and all three are
        #                                  what those two rows do.
        #   0x200A448  AL, RZ, XCZ, XE, XF, XVZ -- printed p.75 too,
        #                                  and the set returns to
        #                                  what printed p.73 left.
        #                                  The reject path reloads
        #                                  T IXA, counts it down to
        #                                  zero through line 36's
        #                                  "CB+,T IXA,T AREJ1" and
        #                                  leaves the index zero and
        #                                  flagged again.  A value
        #                                  that comes BACK is as much
        #                                  a measurement as one that
        #                                  moves.
        #   0x1000000001428  AL, OP, RGZ, XE, XVGZ -- printed p.80
        #                                  too, and the run now ends
        #                                  in MCP's ERROR ROUTINE
        #                                  rather than on an address
        #                                  it cannot reach.  OP is
        #                                  the single "operation
        #                                  invalid" the OP trail has
        #                                  reported since printed
        #                                  p.24 landed; the error
        #                                  path does not reset the
        #                                  indicators the way
        #                                  ASSIGN's entry does, so it
        #                                  is still showing at the
        #                                  halt.
        #   0x1000000001422  AH, OP, RGZ, XE, XVGZ -- ONE BIT, AL ->
        #                                  AH, and it is the bit the
        #                                  IMAGE BUG was hiding.  Three
        #                                  "CM1111,<bit>(index)" rows
        #                                  on printed pp.66, 75 and 80
        #                                  were compiling with length 0
        #                                  -- SIXTY-FOUR -- because the
        #                                  merge had taken a stand-in
        #                                  declared without its dds, so
        #                                  the model refused them as
        #                                  crossing-field writes and
        #                                  MCP never set its reject or
        #                                  job-processed bits.  With
        #                                  every declaration carrying
        #                                  its documenting page's dds
        #                                  the three run, and the
        #                                  accumulator comparison they
        #                                  leave behind goes the other
        #                                  way.  docs/NEXT.md has the
        #                                  whole chain.
        ("mcp_indicators_word11", str(IND_WORD),
         # >>> AND "OP" IS OUT OF THIS WORD FOR GOOD, 2026-10-25. <<<
         # Operation Code Invalid was in this expectation because
         # printed p.24's time conversion used five operations the
         # model did not have -- two `/`, a `CV` and two `LTRCV` --
         # and every one of them set it.  All five are built, and the
         # boot now reports "OP TRAIL: operation invalid never set".
         # MCP'S BOOTSTRAP EXECUTES WITH NOTHING REFUSED.
         #
         # If OP ever comes back, something REGRESSED or MCP reached
         # code it had never reached before; either way the OP
         # locator in StretchExecute.bsv prints the half-word address
         # of the instruction that set it, and that address is the
         # first thing to look at.
         _ind("AH") | _ind("RGZ") | _ind("XE")
         | _ind("XVGZ")),

        # >>> THE MOVE ITSELF, AND IT IS THE POINT OF THE FIXTURE <<<
        # Printed p.4 line 28, "T,$11,X BUFER($X1),X BS END  -MOVE MCP
        # IPL", with a real count for the first time.  What makes
        # these checks worth more than "something was copied" is that
        # every fixture word CARRIES ITS OWN BUFFER OFFSET in its low
        # bits (strap/prosa.py), so the destination says WHICH source
        # words arrived -- and MCP computed that offset itself, out of
        # the dictionary, through SC and LVS.  If the derivation of
        # the record's shape were wrong this fails with the actual
        # offset in hand.
        #
        # X BS END is the first word past the bootstrap image, so
        # everything at and above it was ZERO before the move.
        # >>> AND WHAT IT MOVES IS MCP <<<  The seven hundred and
        # twenty-seven words are printed pp.15-36 ASSEMBLED, and they
        # are assembled at 000621.00 because printed p.15 line 7 is
        # "SLC,X BS END" -- the same address this TRANSMIT delivers
        # them to.  So the check is the image word for word, from the
        # same assembler the transcriptions are verified with.
        #
        # IT WAS EIGHTY WORDS AND pp.15-18 UNTIL 2026-10-22.
        ("mcp_moved_first", str(sym("XBSEND")), prosa.MCP_IPL_WORDS[0]),
        # >>> AND THE LAST WORD IS NOT THE LAST WORD OF THE IMAGE ANY
        # MORE, 2026-10-23, because printed p.37 joined it and MCP
        # OVERWRITES WHAT p.37 PUTS THERE. <<<
        #
        # p.37 is the COMMUNICATION REGION, 002150.00 through
        # 002165.00, and MCP's initialization spends pp.15-36 filling
        # it: printed p.15 line 23 is "SR,$0,S ROOF  -PLACE 7030 SIZE
        # IN COMM", printed p.20 line 11 is "SV,$10,S MCP  -SET BASE
        # OF MCP IN...", and printed p.15 line 21 is
        # "T,$0,X BUFER($9),S MCP  -MOVE COMM REGION" with its count
        # loaded the row before from the record.  So those fourteen
        # words end the run holding what MCP WROTE, not what the
        # image carried, and a check on them measures the fixture's
        # comm-region block rather than the move.
        #
        # SO THE PAIR MOVED DOWN to the last two words BEFORE the
        # communication region -- which are also the two that
        # straddle the join between two source decks.  printed p.36's
        # last datum is "X ABN  DD(BU,36),(8)440042002020" at
        # 002146.74, thirty-six bits, so it RUNS INTO 002147; printed
        # p.37's first row is a CNOP at 002147.40.  One word, two
        # decks, and it is only right if both are.
        ("mcp_moved_last", str(sym("XBSEND") + _image_index("002147")),
         prosa.MCP_IPL_WORDS[_image_index("002147")]),
        # >>> THE FIXTURE'S INVENTED FIELD AND IBM'S COMPILED WORD,
        # IN THE SAME THIRTY-TWO BITS. <<<
        #
        # 002150's LOW half is S COM SZ.  printed p.37 line 9 compiles
        # it to 000016.00+ -- FOURTEEN words as a bit address, 896,
        # which is 0x00038000 once the value field is placed.  And
        # strap/prosa.py's comm_descriptor, written a week before p.37
        # was opened, puts "size_words << 14" in a word MCP reads with
        # printed p.15 line 20's "LC,$0,X BUFER+.32($9)".  LC takes a
        # half-word's bits 31:14 (StretchExecute's dixop_LC,
        # "count: h[31:14]"), so 14 << 14 IS 0x00038000.  The two are
        # BIT-IDENTICAL, from opposite directions.
        #
        # SO THIS IS A CROSS-CHECK, NOT A MEASUREMENT OF THE MOVE, and
        # it was nearly committed as the opposite.  The low half is
        # unchanged at the end of the run and the obvious reading is
        # "the comm-region TRANSMIT never reached it".  IT DID REACH
        # IT AND WROTE THE SAME BITS.  What settles it is the
        # two-minute read of LC against index_word, not the fact that
        # the word did not change.
        #
        # The HIGH half is MCP's own, written by printed p.20 line
        # 11's "SV,$10,S MCP  -SET BASE OF MCP IN COMM REGION" -- so
        # one word carries the fixture's number, IBM's number and
        # MCP's answer at once.
        ("mcp_comm_size_fixture_and_listing_agree", str(0o2150),
         0x02BF800000038000),
        # A word from the middle, so the check is not two endpoints
        # and a hope.
        #
        # IT HAS TO BE A NON-ZERO ONE, and the plain midpoint stopped
        # being that when the image grew to printed pp.15-36: index
        # 363 lands at 001374, inside printed p.24's
        # "X VSTOR DRZ(BU),100", a hundred words of deliberate zeros.
        # A check whose expected value is zero over a region that was
        # zero before the move as well proves nothing at all.  So the
        # index is the first NON-ZERO word at or after the midpoint,
        # computed rather than written down, which keeps it honest if
        # the image changes again.
        ("mcp_moved_middle",
         str(sym("XBSEND") + _middle_index()),
         prosa.MCP_IPL_WORDS[_middle_index()]),
        # THE SECOND-TO-LAST WORD, so that the top of the image is
        # pinned by a PAIR and not by one endpoint.  "mcp_moved_last"
        # alone would pass if the move were one word short AND the
        # record happened to repeat a value.
        ("mcp_moved_second_last",
         str(sym("XBSEND") + _image_index("002146")),
         prosa.MCP_IPL_WORDS[_image_index("002146")]),

        # >>> THE WORD AFTER THE LAST ONE USED TO BE CHECKED AS STILL
        # ZERO, and that check had to go -- because MCP now runs far
        # enough to write it. <<<
        #
        # printed p.15 line 21 is "T,$0,X BUFER($9),S MCP -MOVE COMM
        # REGION", and S MCP is 002150.00, which is EXACTLY one word
        # past the image's last word at 002147.  So the first thing
        # MCP INITIALIZATION does after being moved is overwrite the
        # word this check used to require to be zero.  The old check
        # was not wrong; it was measuring a machine that stopped
        # sooner.
        #
        # WHAT REPLACES IT IS STRONGER, because it pins the offset MCP
        # COMPUTED ITSELF.  printed p.15 line 17 is
        # "X10 LVS,$9,$12,$11,$14 -COMPUTE NUMBER OF WORDS PRECEEDING
        # MCP" -- the sum of THREE dictionary counts, 3 + 727 + 5 --
        # and line 21 moves from X BUFER($9).  Every fixture word
        # carries its own buffer offset, so if that sum is wrong the
        # value landing at S MCP says by how much.
        #
        # The address is written as the image's own end rather than as
        # a constant, and the two ARE the same thing: printed p.28
        # line 11's "SV,$12,S MCP" compiles 002150.00, and
        # 000621 + 727 is 002150.  If the image grows by a page this
        # check moves with it and stops being about S MCP -- which is
        # the right failure, because the record would then need a
        # comm region of its own.
        # >>> THE WITNESS THAT USED TO LIVE HERE HAD TO MOVE.  S MCP
        # held the descriptor the comm-region move delivered, and
        # printed p.20 line 11 -- "X20 A 1  SV,$10,S MCP  -SET BASE
        # OF MCP IN COM REG" -- now runs and overwrites it.  The
        # move's EXTENT is still pinned by X0's count (fifteen, the
        # size LC read out of the descriptor) and by
        # mcp_comm_region_one_past_is_zero; the descriptor's ARRIVAL
        # is still pinned by mcp_placed_at_dest_first, which printed
        # p.15 line 24 delivers to an address nothing overwrites. <<<
        # AND THE REST OF THE REGION CAME WITH IT.  The descriptor
        # alone would arrive even if the count were wrong, because it
        # is the first word; the LAST word of the fifteen is what says
        # the count was read out of bits 32-49 and not left at zero.
        # Every one of these carries its own buffer offset.
        # >>> THESE TWO MOVED TO FIXED ADDRESSES ON 2026-10-23, AND
        # THE OLD ONES HAD DRIFTED ONTO MCP'S OWN WORKING STORAGE.
        # <<<
        #
        # They used to sit at "MCP_IPL_AT + IPL_WORDS +
        # COMM_REGION_WORDS", which assumed the comm region lands
        # immediately after the image -- true while the image ended
        # at 002147 and printed p.37's region began at 002150.  Seven
        # pages later IPL_WORDS is 925 and that expression points at
        # 002473, which is inside Q SAV, the six words printed p.43
        # line 10 saves its index registers into.  The comment above
        # said "if the image grows by a page this check moves with it
        # and stops being about S MCP -- which is the right failure";
        # the failure was right and this is the fix.
        #
        # THE MOVE'S EXTENT IS NOW PINNED FROM BOTH SIDES, at
        # addresses that do not move:
        #
        #   002165 is the LAST word the fourteen-word comm-region
        #     move covers (002150 through 002165 inclusive is 0o16).
        #     The record's block is a descriptor and thirteen zeros,
        #     so this reads ZERO -- and the image delivers printed
        #     p.37 line 43's S TODAY here, "  /  /63" in BCD, which
        #     is NOT zero.  A move one word short leaves that datum
        #     standing.
        #
        #   002166 is ONE PAST, and it is printed p.38 line 4 --
        #     Y UNCOD's TRANSMIT, the first word of the UNCODE
        #     subroutine.  A move one word long destroys the
        #     instruction MCP branches to, which is the sharpest
        #     possible statement of the upper edge.
        #
        # Both were zero in the old formulation; now one is a
        # specific instruction word.  The pair is strictly stronger
        # and neither drifts.
        ("mcp_comm_move_covers_s_today", str(0o2165), 0),
        ("mcp_comm_move_stops_before_yuncod", str(0o2166),
         prosa.MCP_IPL_WORDS[0o2166 - prosa.MCP_IPL_AT]),
        # >>> AND MCP IS PLACED.  printed p.15 line 24,
        # "T,$10,X BUFER($9),0.0($8)  -PLACE MCP IN STORAGE": X10 is
        # the dictionary's MCP SIZE and $8 is the address LVE pulled
        # out of the descriptor's bits 0-23.  So this check is the
        # whole descriptor read back through two different
        # instructions -- LC for the size, LVE for the address. <<<
        # The first word placed is the descriptor itself, because
        # printed p.15 line 24 moves from X BUFER($9) -- the SAME
        # source as line 21's comm-region move.  That is what the
        # listing says and the fixture reproduces it rather than
        # tidying it: the comm region's leading words ARE MCP's.
        ("mcp_placed_at_dest_first", str(prosa.MCP_DEST_WORD),
         prosa.comm_descriptor(prosa.MCP_DEST_WORD,
                               prosa.COMM_REGION_WORDS)),
        ("mcp_placed_one_past_is_zero",
         str(prosa.MCP_DEST_WORD + prosa.MCP_SIZE_WORDS), 0),

        # >>> AND THE IOCD CARD IS AT X IN END, which is the whole
        # reason MCP's destination is no longer a free choice. <<<
        # printed p.17 line 8 points $4 at X IN END and line 12 tests
        # fourteen words from there for the first card; printed p.13
        # line 38 reserves what follows as "SLOTS LEFT FOR IOCD +
        # IODS".  strap/prosa.py puts the cards at the END of the
        # block printed p.15 line 24 places, and MCP_DEST_WORD is
        # X IN END minus the body, so the first card lands exactly
        # where the hunt starts.
        #
        # The card's FIRST word is the class column: "B" in column 1
        # is a 12-2 punch, so the word reads 0x8800... and nothing
        # else in the region does.
        ("iocd_card_first_word_at_x_in_end",
         str(prosa.XINEND_WORD),
         iocd.card(*prosa.IOCD_CARDS[0][:2],
                   units=prosa.IOCD_CARDS[0][2])[0]),
        # And the word carrying columns 10-17 -- "IOCD", the channel
        # digits and the equipment code -- because the first word
        # alone would pass on a card that was all class column.
        ("iocd_card_identifier_word",
         str(prosa.XINEND_WORD + 1),
         iocd.card(*prosa.IOCD_CARDS[0][:2],
                   units=prosa.IOCD_CARDS[0][2])[1]),
        ("iocd_card_last_word",
         str(prosa.XINEND_WORD + iocd.WORDS_PER_CARD - 1),
         iocd.card(*prosa.IOCD_CARDS[0][:2],
                   units=prosa.IOCD_CARDS[0][2])[-1]),

        # Printed p.2 line 39, "SV,15,X S ROOF -TEMPORARILY SAVE 7030
        # SIZE".  The value field holds 6291456 bits = word 98304,
        # which is StretchMemory's InstalledWords -- six units.  MCP
        # MEASURED THE MACHINE AND GOT THE RIGHT ANSWER.  Change the
        # memory configuration and this fails with the new size in it,
        # which is the most useful way for it to fail.
        ("mcp_x_s_roof", str(sym("XSROOF")), 0x6000000000000000),

        # Printed p.3's FIND IPL CHANNEL walks the channel field of
        # its own CCW one channel at a time.  It starts at 15.32 = 992
        # = channel 31 and stops at 1088 = channel 34, which is where
        # StretchIO puts the tape.  The word straddles: X1 CCW is at
        # 000053.40, so this word's LOW half is its first half-word.
        ("mcp_x1_ccw_after_walk", str(sym("X1CCW")), 0x098012B000044080),

        # LVE's own result, printed p.3 line 10: index register 15 --
        # word 31, "the words in storage locations 16-31" (RefMan
        # printed p.28) -- holds 1088, the channel-34 address, which
        # every "0($15)" on pp.3-6 then uses.
        #
        # >>> SUPERSEDED 2026-10-22.  The premise was that $15 still
        # held LVE's result from printed p.3; it does not, because
        # printed p.17 lines 18-20 load it with X BUFER + 64 words as
        # the base of the unit status table area and printed p.19
        # advances it per unit.  A check on a register that later
        # code reuses measures only how far the run got. <<<
        #
        # What replaces it is the field printed p.19 line 27 SAVES
        # that pointer into -- "SV,$15,S LR BU  -SAVE BASE OF IO
        # ASSIGNMENT TABLES" -- which is a named communication-region
        # word rather than a scratch register, and which printed
        # pp.28 and 30 both read back.
        #
        # >>> AND IT IS NO LONGER ZERO: the deck grew an IOD card, so
        # printed p.19 line 27's "SV,$15,S LR BU  -SAVE BASE OF IO
        # ASSIGNMENT TABLES" runs.  The value is the unit-status-table
        # pointer printed p.17 line 20 started at X BUFER + 64 words
        # and printed p.18's unit loop advanced.
        #
        # EXACT ON PURPOSE, AS A RATCHET, and the arithmetic that
        # produces it is NOT derived here -- it runs through printed
        # p.18's unit loop and printed p.19's relocation, neither of
        # which this file has worked out.  If it moves, something in
        # those pages changed, and that is what the check is for. <<<
        ("mcp_s_lr_bu", str(0o2155), 0x04D3000000000000),

        # THE LOAD ITSELF, and only the last word is a fair witness.
        # X IPL BS used to be checked here and cannot be: the program
        # legitimately overwrites it, because printed p.3's CCW copies
        # the channel's control word to exactly that address.  The
        # last word of the 368-word record is never written by the
        # bootstrap, so a truncated load fails here and nowhere else.
        ("mcp_loaded_last_word", str(sym("XBSEND") - 1),
         prog.words[sym("XBSEND") - 1]),
    ]

    # ===============================================================
    # >>> WHAT MCP PRINTED ON THE OPERATOR'S CONSOLE <<<
    # ===============================================================
    # Decoded with strap/charsets.py's IQS table (Reference Manual
    # printed p.166), 0o375 being the CARRIAGE RETURN control code and
    # 0o376 END OF MESSAGE -- both named by the message decks
    # themselves (decks/mcp_bootstrap_p9_p12.strap and p13):
    #
    #     <CR>000000.0 NO IOCD CARD DETECTED<EOM>
    #
    # MCP walked the basic exchange from channel 32 (printed p.5 line
    # 21, "ENTER FIRST CHANNEL OF BASIC EXCHANGE"), rejected the card
    # reader and the printer because GONG program-checks on them,
    # rejected the tape because LOCATE does NOT (printed p.5 line 42,
    # "-TEST IF TAPE UNIT"), found the console at 35 because GONG
    # there does not program-check (line 51, "-IF CONSOLE * NO EPGK"),
    # and wrote the message with "W(SEOP),0.0($X1),X MS CW1".
    #
    # WORDS 0-2 ARE ZERO AND THAT IS THE MESSAGE'S OWN HEADER:
    # printed p.8 line 34 is "X MS CW1  CW,X ZEROS,3,..." -- three
    # words from X ZEROS -- chained to printed p.8 line 35's
    # "X MSG CW  CW,0,10,0", whose data address printed p.5 line 18
    # fills in with SVA.
    #
    # TWO THINGS IN THIS OUTPUT ARE NOT RIGHT YET, and they are
    # asserted as they are rather than quietly trimmed:
    #
    #   THE ERROR ADDRESS SLOT IS WRONG, AND IT IS NOW WRONG IN A
    #   DIFFERENT WAY.  The slot's string is the message's own
    #   placeholder -- the decks write "(IQS*)DD(BU,64,8),000000.0*
    #   -SLOT FOR ERROR ADDRESS" -- and printed p.5 lines 12-17 fill
    #   it, breaking X ERR AD into eight-bit bytes with LF and adding
    #   the octal digits in with two M+MG.  Until M+MG existed the
    #   slot printed the placeholder untouched; now the adds run and
    #   deposit bytes that are not IQS digits at all.
    #
    #   WHAT THE DIGITS ARE, derived rather than guessed.  X ERR AD is
    #   a 19-bit HALF-WORD address in value-word bits 0-18 -- the same
    #   number `mcp_x_err_ad` above checks, written there as a shift
    #   so it tracks a re-transcription.  LF reads bits 0-20, which is
    #   that half-word address times four, and its seven octal digits
    #   are the seven character slots.  For this image the address is
    #   869 = 000662.40, so bits 0-20 are 3476 = octal 0006624 and the
    #   digits are 0 0 0 6 6 2 then 4.
    #
    #   WHERE THEY GO IS NOT WHERE THE SLOT WAS DRAWN, and that is a
    #   fact about MCP rather than about this model.  Console word 3
    #   IS memory word 000440, the start of message X MS 16C (three
    #   earlier words of the ten-word write occupy console words
    #   0-2), and printed p.11 lines 44-48 show that entry has only
    #   ONE control code:
    #
    #       000440.00  375   DD(BU,8),(2)1111 1101  -CARRIAGE RETURN
    #       000440.10        (IQS*)DD(BU,64,8),000000.0*  -SLOT
    #
    #   -- no RED code, so its slot starts at BYTE 1.  Every other
    #   message has CR then RED and starts its slot at byte 2, and
    #   printed p.5 line 15's address field is 000000.20, sixteen
    #   bits, byte 2 unconditionally ("SKIPPING OVER CONTROL CODES",
    #   plural).  So the six digits land at bytes 2-7, over this
    #   message's second through sixth zeros and its ".".  The model
    #   put them exactly there.
    #
    #   (IQS digit n is 0x60+n, "." is 0x74, " " is 0x00.)  Compute
    #   the expectation from ipl_hw("XER16C") the way mcp_x_err_ad
    #   does if this is ever turned into a check, and check it against
    #   where MCP writes rather than where the slot was drawn.
    #   docs/NEXT.md works the whole layout through, including the
    #   second M+MG, which does NOT fit the same story -- it targets
    #   byte 8, the "." of a normal two-code message.
    #
    #   WHAT IT SAYS, as of 2026-10-19, AND EVERY DIGIT IS DOUBLED:
    #
    #       w3 = 0xfd606060606c6c78   <CR> 0 | 0 0 0 <+12> <+12> <.+4>
    #       w4 = 0x68004749003d4931   <+8> _ N O _ I O C
    #
    #   Bytes 2-7 and the first byte of w4 received 0, 0, 0, 12, 12,
    #   4 and 8.  The address is octal 0006624 -- digits 0, 0, 0, 6,
    #   6, 2, 4 -- so every one of them is exactly twice what it
    #   should be.  That is what a one-bit misalignment does to a
    #   field of small byte values, and it is attributable: printed
    #   p.5 line 12's "LF(BU,21,3),X ERR AD,1" carries OFFSET 1 while
    #   lines 15 and 17 consume the result at offsets 8 and 0, which
    #   want the seven result bytes byte-aligned.
    #
    #   THE OBVIOUS FIX IS WRONG AND THE SUITE PROVED IT.  Rounding
    #   the connective offset down to a byte makes this message come
    #   out perfect -- 0, 0, 0, 6, 6, 2, 4, measured -- and p.75 and
    #   p.57 can both be read to support it.  It was built that way
    #   and **fifty-six sections failed**: all of jb_af1c and the PAU
    #   gates, because the floating-point diagnostic checks every
    #   result with "CT0110(BU,60),ROS,4", a connective at offset 4.
    #   The offset is bits.  What is left is a question about MCP's
    #   four instructions, not about the model; docs/NEXT.md carries
    #   it.
    #
    #   THE BYTES ARE EIGHT BITS WIDE AT ALL only because of printed
    #   p.75's other rule.  Line 12's own comment is "-BREAK ADDRESS
    #   INTO EIGHT BIT BYTES", and p.75 says "If the byte size of the
    #   storage operand is less than eight, each byte is converted
    #   into an eight-bit byte before processing by the addition of
    #   high-order zeros... Consequently, the result bytes always
    #   have a byte size of eight."  The model's connectives ignored
    #   byte size entirely and worked on a flat bit field, so these
    #   two words used to hold the raw 21-bit address smeared across
    #   the slot (w3 came out 0xfd6021e06061a08f).  Built, with
    #   injections, in decks/connective_byte_size.strap.
    #
    #   THE WRITE RUNS PAST THE END-OF-MESSAGE CODE.  The control
    #   word counts ten words and the message is four, so words 7-12
    #   are whatever follows in the message table -- here the start of
    #   "WRONG EQUIPMENT CODE". A real 7152 presumably stops at 0o376;
    #   Reference Manual printed p.150 says the console has control
    #   functions "initiated during WRITE instructions" but does not
    #   list them, so the model prints all ten and this is a gap with
    #   no source yet rather than a behaviour invented to fit.
    # WORDS 3 AND 4 ARE CHECKED AGAIN, because they are attributable
    # again.  They were dropped for one commit while the address came
    # out as noise; every exact value in this file has to be a
    # statement about something, and the output of an unexplained bug
    # is not one.  Now every byte is accounted for: the seven octal
    # digits of X ERR AD, each exactly doubled by LF's offset of 1,
    # landing one byte late because X MS 16C has no RED control code.
    # Both of those are explained above and neither is the model's.
    # >>> AND NOW NOTHING IS PRINTED, WHICH IS THE POINT.  For one
    # commit this read
    #
    #   <CR><RED>000760|0 INCORRECT CARD TYPE <EOM>
    #
    # -- MCP's own diagnosis of a card deck with no terminator, out
    # of printed pp.7-8's error table, with 000760 being printed p.19
    # line 25's own address.  The deck has an IOD card now, no error
    # site runs, the error routine is never entered, and the console
    # stays silent.  The checks stay, asserting silence, because an
    # empty console is only good news next to the run that explains
    # it. <<<
    # >>> AND MCP TYPES A MESSAGE TO ITS OPERATOR.  Five words, out
    # of printed pp.21-24's date routine, through the console it
    # found in the relocated channel status table:
    #
    #   <CR><RED> DATE OF IPL TAPE <CR>00 MONTH 00 DAY  <CR><EOM>
    #
    # The date reads 00/00 because printed p.24's constants are
    # "(A*)DD(BU,,6),00,00,00,*" -- placeholders MCP fills from the
    # clock, which this fixture has no source for.  What the check
    # pins is that the MESSAGE got there: the right characters, in
    # the right order, in the IQS console code, which means the
    # relocation, the console hunt and the WRITE all worked. <<<
    console_checks = [
        ("console_date_w3", 3, 0xfd0200332d533500),  # <CR><RED> DATE
        ("console_date_w4", 4, 0x4937003d4b430053),  # " OF IPL T"
        ("console_date_w5", 5, 0x2d4b3500fd606000),  # "APE <CR>00 "
        ("console_date_w6", 6, 0x454947533b006060),  # "MONTH 00 "
        ("console_date_w7", 7, 0x00332d5d0000fdfe),  # "DAY <CR><EOM>"
        # >>> AND MCP TYPES ITS OWN ERROR REPORT, 2026-10-26. <<<
        #
        # This check used to be the last word on the console and was
        # named `console_nothing_after`, asserting word 8 is zero. It
        # still asserts exactly that -- but the NAME claimed the
        # console was empty from here on, and it is not. The write at
        # printed p.5 line 52 goes through `X MS CW1`, which printed
        # p.8 line 34 defines as `CW,X ZEROS,3` -- THREE WORDS OF
        # ZEROS -- chaining to `X MSG CW`'s ten-word message. Word 8
        # is where the FIRST ZERO lands, so this check passing was
        # always consistent with MCP WRITING, never with it failing.
        #
        # "The console write produces nothing" was one sentence from
        # being recorded as a model defect on the strength of it.
        # A name is an assertion too, and it is the one people read.
        ("console_word8_is_first_of_three_zeros", 8, 0),
        ("console_word9_zero",  9, 0),
        ("console_word10_zero", 10, 0),
        # The message itself, words 11-20, decoded with the same
        # strap/charsets.py IQS table that reads the date message:
        #
        #   <CR><RED>001471.0  IO ASSIGNMENTS CAN NOT BE MADE <EOM>
        #   <CR><RED>000000.0  IO TABLES CAN NOT BE FORMED
        #
        # Both strings are TRANSCRIBED LISTING TEXT --
        # decks/mcp_bootstrap_p9_p12.strap lines 311 and 327 are
        # "(IQS*)DD(BU,64,8), IO ASSIGNMENTS CAN NOT BE MADE *" and
        # "... IO TABLES CAN NOT BE FORMED *".
        #
        # >>> AND 001471 IS X ERR AD, ARRIVED AT FROM THE OTHER END.
        # <<<  mcp_x_err_ad above reads 0x00CE600000000000, whose top
        # 24 bits are the bit address 52832 = word 825 = 001471.40 =
        # printed p.27 line 13's "BZXCZ,X ERROR -IF ASSIGNMENT
        # ERROR".  The machine types the same number out of its own
        # console.  Neither derivation was consulted for the other.
        #
        # WHAT THESE TEN WORDS ASSERT is the whole error path:
        # ASSIGN rejecting (printed p.76 line 93's reason, "I/O REQ.
        # INCOMP WITH MACH CONF."), returning without p.80 line 25's
        # disposition bit, p.27 line 13 branching, XERROR finding the
        # console in S YCOCH, GONG identifying it, and the chained
        # write landing.  If any link breaks, these move.
        #
        # >>> 0x7C IS NOT A CHARACTER AT ALL, AND THAT IS AN OPEN
        # QUESTION, NOT A TABLE GAP. <<<
        #
        # Word 11's separator reads 0x7C where word 18's, in the same
        # position of the same message format, reads 0x74 = ".".
        # The first guess was that charsets.py lacked an italic or
        # zoned variant.  Reference Manual printed p.166's 89-set
        # grid was then rendered and read, and column 0111 is:
        #
        #   row 0000  8     row 0100  .     row 1000  (blank)
        #   row 0001  8it   row 0101  :      ...
        #   row 0010  9     row 0110  -     row 1100  (blank)  <- 0x7C
        #   row 0011  9it   row 0111  ?      ...
        #
        # **That cell is EMPTY.**  charsets.py is right; 0x7C is not
        # a printable 89-set code, so MCP emitted a byte the console
        # typewriter has no glyph for.  Either the model renders the
        # error address wrongly, or MCP writes a byte the real
        # typewriter ignores.  Both messages otherwise decode
        # perfectly and both are transcribed listing text, so this is
        # ONE BYTE in an otherwise exact match.
        #
        # Checked here as the raw word either way, so that whichever
        # answer turns up, the change is visible.
        ("mcp_console_err_w11", 11, 0xfd02606062686e62),  # <CR><RED>001471
        ("mcp_console_err_w12", 12, 0x7c60003d49002d51),  # .0  IO AS
        ("mcp_console_err_w13", 13, 0x513d394745354753),  # SIGNMENT
        ("mcp_console_err_w14", 14, 0x5100312d47004749),  # S CAN NO
        ("mcp_console_err_w15", 15, 0x53002f3500452d33),  # T BE MAD
        ("mcp_console_err_w16", 16, 0x3500fe0000001800),  # E <EOM>
        ("mcp_console_err_w17", 17, 0xfd02606060606060),  # <CR><RED>000000
        ("mcp_console_err_w18", 18, 0x7460003d4900532d),  # .0  IO TA
        ("mcp_console_err_w19", 19, 0x2f43355100312d47),  # BLES CAN
        ("mcp_console_err_w20", 20, 0x00474953002f3500),  #  NOT BE
        ("mcp_console_silent_after_the_report", 21, 0),
    ]

    # ---- THE OPERATOR'S CONSOLE SWITCHES -------------------------
    # Reference Manual printed p.150: a console READ with the keyboard
    # not enabled returns "the three words scanned from the switches",
    # and the console's word weight is 3.  printed p.22 line 5 is the
    # READ -- "RD(SEOP),0.0($15),X DCW 2" with
    # "X DCW 2 = CW,X LR IN,3,0".
    #
    # WORD 0 STAYS ZERO AND THAT IS THE CONFIGURATION, NOT AN
    # OMISSION.  C22-6678-1 printed p.29 puts the time in binary keys
    # 0-23 and the date in 32-55, with 28-31 the four report options;
    # printed p.22 line 12's "KFI(BU,24),0,40  -NO TIME ENTERED" is
    # MCP's own name for all-zero, and taking that branch is what
    # exercises printed p.24's "replace a blank character with a BCD
    # zero" routine.  An operator who sets nothing is a real operator.
    #
    # WORDS 1 AND 2 CARRY A MARKER, AND THEY ARE WHY THE CHECK ON
    # X LR IN+1 BELOW DISCRIMINATES.  p.29 describes the NUMERIC
    # switches -- columns 7-8 the channel number, 15-16 the tape unit
    # -- and MCP reads them only on the I/O-status-report path, which
    # binary key 29 selects and which is not taken here.  So these two
    # words should arrive in storage and then be left alone, and
    # anything else serving the READ (the card reader's image is the
    # one that nearly did) delivers zeros instead.
    #
    # THE MARKER HAD TO EXIST AT ALL because an all-zero fixture
    # cannot tell a correct implementation from a wrong one: the first
    # injection written against this check SURVIVED, with the console
    # READ served out of the card reader, for exactly that reason.
    console_switches = [0, 0x5A5A5A5A5A5A5A5A, 0xA5A5A5A5A5A5A5A5]

    print(generate(module_name, prog, checks,
                   console_switches=console_switches,
                   console_checks=console_checks,
                   # >>> IT STOPS WHERE IBM TOLD IT TO <<<
                   # 239 is half-word 239 = 000167.40, and that is
                   # **printed p.6 line 1, "BD,$  -LOOP"** -- the last
                   # instruction of MCP's own ERROR ROUTINE, a BRANCH
                   # DISABLED to its own address.  The row before it
                   # is line 56, "TI,1,X ERR AD,$R  -DISPLAY ERROR
                   # ADDRESS IN", which puts the failing address in
                   # the R register for the operator to read off the
                   # console lights.
                   #
                   # So the machine is not stuck and it has not
                   # wandered: it diagnosed a configuration with no
                   # IOCD cards, tried to print the message, found no
                   # console, left the address on display and stopped
                   # the way the program says to stop.
                   #
                   # IT USED TO BE 169 -- printed p.4 line 32's
                   # "CB,0,$", MCP's delay loop -- because `halted()`
                   # meant "branched to its own address" and that loop
                   # is one.  A COUNT AND BRANCH makes progress, so it
                   # is no longer a halt (StretchCore.bsv's `isHalt`),
                   # and everything pp.15-18 do was behind it.
                   # >>> AND IT MOVED AGAIN ON 2026-10-22, from the
                   # error routine's halt to one ELEVEN PAGES
                   # FURTHER ON.  1035 is half-word 1035 = 001005.40,
                   # and that is **printed p.20 line 18, "XERR 20
                   # BD,$  -YES *ERROR* NO CONSOLE"** -- IBM's own
                   # stop for a machine whose channel status table
                   # has no console in it.
                   #
                   # THE CONSOLE IS DECLARED: strap/prosa.py punches
                   # a CN card for channel 35, which is where
                   # bsv/StretchIO.bsv puts the console.  What is
                   # missing is printed p.19 line 41's
                   # "TB,3,0.0($11),0.0($13)  -MOVE BIASED CTS", a
                   # TRANSMIT BACKWARD the model refuses -- so the
                   # table p.20 walks was never relocated.  OP in the
                   # indicator check above is that refusal.
                   #
                   # So the halt is MCP being right about the machine
                   # the MODEL presents, and the next thing to build
                   # is the backward arm.
                   # >>> AND IT IS 239 AGAIN, WHICH IS NOT A STEP
                   # BACKWARD.  1035 was printed p.20 line 18's
                   # "XERR 20  BD,$  -YES *ERROR* NO CONSOLE", a
                   # halt MCP took because TRANSMIT BACKWARD was
                   # missing and the channel status table had never
                   # been relocated.  With the arm built the console
                   # IS found, the date message IS typed, and the run
                   # ends at printed p.6 line 1's "BD,$" -- the end
                   # of the error routine -- after the I/O test on
                   # printed p.3 finds a status bit on.
                   # >>> AND IT IS 0, WHICH IS NOT A WORSE PLACE TO
                   # STOP BUT A MUCH LATER ONE.  239 was printed p.6
                   # line 1's "BD,$", the end of MCP's ERROR ROUTINE,
                   # taken because the console READ on printed p.22
                   # line 5 program-checked.  With the switch
                   # register built NO ERROR SITE RUNS (X ERR AD is
                   # zero above) and MCP goes on through printed p.25
                   # and the pages after it, filling its
                   # communication region -- S YCOCH, S YPRCH,
                   # S MARK, S MCP, S XCHAN, S MAXRN, S DKMCP and
                   # S SYRFT are all non-zero at the end of the run.
                   #
                   # WHAT PC 0 MEANS, AND IT IS NOT A MYSTERY: a
                   # zero half-word is BRANCH ENABLED to 0.0 --
                   # UNCOND_BRANCH_CODES["BE"] is 0b000 and the
                   # address field is zero, so "BE,0.0" assembles to
                   # all zeros and all zeros disassemble to it.
                   # (The same fact is spelled out in the indicator
                   # comment above, where it explained a wiped
                   # indicator register.)  So MCP has branched into
                   # storage this project has not transcribed, where
                   # every word is a branch to location zero, and
                   # location zero is another one -- which the model
                   # reports as "the last instruction branched to
                   # itself".
                   #
                   # MCP LEFT THE TRANSCRIBED PAGES.  Printed p.36 is
                   # the last page in the image; the next source deck
                   # begins at printed p.37.  THAT IS THE NEXT
                   # TRANSCRIPTION, and this check is what will
                   # notice when it lands.
                   # >>> IT NO LONGER HALTS AT PC 0. <<<  printed
                   # p.45 fills S BRK8, so the run stops where MCP
                   # MEANS to stop: half-word 239 = 000167.40, which
                   # is printed p.6 line 1's "BD,$  -LOOP", one
                   # instruction after printed p.5 line 56's
                   # "X6ERR  TI,1,X ERRAD,$R  -DISPLAY ERROR ADDRESS
                   # IN CE CONSOLE".  A deliberate error stop, not a
                   # branch into zeros.
                   # >>> AND IT BRANCHES INTO ZEROS AGAIN,
                   # 2026-10-24, HAVING GOT MUCH FURTHER. <<<  The
                   # crossing-field store (see mcp_ucbf1_* above)
                   # makes MCP accept the IOD card, so it never takes
                   # the error exit this check was pinned to; it goes
                   # on into printed p.54's TAPE IOD ROUTINE and
                   # branches to L NORM, which p.54 line 87 compiles
                   # as "L NORM  SYN,(8)3237.40" -- A STAND-IN FOR A
                   # SYMBOL DEFINED ON A PAGE NOT YET TRANSCRIBED.
                   # 003237.40 holds zeros, so the run ends the way
                   # the note above describes.
                   #
                   # SO THE PC IS ZERO AND THE TRAIL IS THE DATUM,
                   # which is exactly the case gen_tb's pc_trail was
                   # written for.  pc_trail_check pins it: half-word
                   # 3391 = 003237.40 = L NORM.  PRINTED p.55 ONWARD
                   # IS THE NEXT TRANSCRIPTION, and the page that
                   # defines L NORM is the one to find first.
                   #
                   # >>> AND THE TRAIL MOVED TO 3970, 2026-10-24,
                   # BECAUSE printed pp.55, 56, 57 AND 58 ARE IN THE
                   # IMAGE. <<<  Half-word 3970 is 003701.00, which
                   # decks/mcp_bootstrap_p27.strap carries as
                   # "T ASIGN SYN,(8)3701.0" -- a stand-in for a page
                   # still unread, around printed p.65.  The run no
                   # longer stops AT L NORM; it goes THROUGH it, and
                   # NINE swaps execute where five did, including
                   # L NORM's own SWAPI,8 at half-word 3391 twice and
                   # printed p.58 line 38's SWAPI,3 at 3388.
                   #
                   # >>> AND IT MOVED TO 4378, 2026-10-24: THE RUN
                   # EXECUTES MCP's ASSIGN ROUTINE. <<<  printed p.65
                   # line 6 IS T ASIGN -- "SWAPI,12,$1,T ASAVE  -SAVE
                   # INDEXES" at 003701.00 -- so the branch the trail
                   # had been stopping at now lands on code.  MCP
                   # saves twelve index registers into printed p.61's
                   # fifteen-word save area, reads the caller's XW
                   # through $15 exactly as printed p.59's LINKAGE
                   # FORMAT says it will, resets its indicators, and
                   # branches on a machine-configuration change to
                   # T A9.
                   #
                   # Half-word 4378 is 004215.00, which is T A9 --
                   # p.65 line 9's forward reference, on printed p.66
                   # or after.  THAT IS THE NEXT TRANSCRIPTION.
                   #
                   # >>> AND IT MOVED TO 4454, 2026-10-25, BECAUSE
                   # printed p.72 IS T A9 ITSELF. <<<  p.72 line 4 is
                   # that address and its heading three lines above
                   # reads "MACHINE CONFIGURATION CHANGE / ADJUST THE
                   # NECESSARY TABLES" -- so the fixture's machine
                   # DOES report a configuration change and MCP now
                   # walks the channel status table adjusting it.
                   #
                   # THE STEP COUNT IS THE TELL: 6.05 MILLION before
                   # this page, 22.04 MILLION after.  p.72's line 51
                   # is "CB+,T IXF,T A9A", a count-branch over the
                   # whole table, and line 12 loops the machine
                   # configuration count table as well.
                   #
                   # >>> AND IT MOVED AGAIN TO 4576, 2026-10-25,
                   # BECAUSE printed p.73 IS IN THE IMAGE. <<<  4454
                   # was 004263.00, p.73's own first word, so the run
                   # was stopping ON the page.  It now executes it --
                   # the bubble sort on lines 8-18 and the MULTI UNIT
                   # SCAN on lines 25-36.
                   #
                   # THE STEP COUNT SAYS SO TOO, by NOT moving:
                   # 22,045,771 against p.72's 22.04 million.  p.73's
                   # loops are over the MULTI-UNIT count table, which
                   # this fixture's machine barely fills, so the page
                   # costs almost nothing to run -- in contrast to
                   # p.72, which cost sixteen million.
                   #
                   # 004360.00 HAS A NAME: it is T AREJX, which
                   # printed p.66 line 16 ("BB,T RJECT(T IXE),
                   # T AREJX  -IF PP WAS REJECTED") and printed p.71
                   # line 47 ("BXF,T AREJX  -NOT OVERLAP ASSIGNED")
                   # both branch to and both carry as a stand-in.
                   # The run TAKES that branch and stops because the
                   # page holding it is not in the image.
                   #
                   # >>> AND THEN TO 4578, THE SAME DAY, BECAUSE
                   # printed p.74 HOLDS IT. <<<  T AREJX is p.74 line
                   # 55.  Its two half words run -- "LVI,T X1,T
                   # MESSY" and "SV,T X1,0.0(T IXE)" -- and the trail
                   # advances by EXACTLY TWO half words, to
                   # 004361.00, for 424 more steps.  004361.00 is
                   # printed p.75 line 1, "T AREJ R,T IXA  -RELOAD
                   # IX".
                   #
                   # >>> AND THEN TO 4872, THE SAME DAY, BECAUSE
                   # printed p.75 IS IN THE IMAGE. <<<  4872 is
                   # 004604.00, and p.75 line 50 NAMES IT:
                   #
                   #     T L   B,T PICA   -NOT OVERLAP JOB NOT
                   #                       ASSIGNED
                   #
                   # The run walks p.75's reject path -- clearing the
                   # reel slot, the assigned bits and the mount bits
                   # -- counts T IXA down through line 36's
                   # "CB+,T IXA,T AREJ1", falls out at line 40's
                   # "B,T L" and dispatches to T PICA, 703 steps
                   # later.  THE DISPATCH TABLE IS BEING USED, and
                   # the exit it takes is the one whose comment says
                   # this job is not overlap and not assigned.
                   #
                   # >>> AND THEN IT LEFT ALTOGETHER, 2026-10-25,
                   # BECAUSE printed p.80 IS T PICA AND THE END OF
                   # THE ASSIGN ROUTINE. <<<
                   #
                   # p.80 line 30 is "SWAPI,12,$1,T ASAVE  -RESTORE
                   # INDEXES" and line 31 is "B,1.00($15)  -RETURN".
                   # printed p.65 line 6 -- the routine's FIRST
                   # instruction, fifteen pages back -- is
                   # "SWAPI,12,$1,T ASAVE  -SAVE INDEXES", and the
                   # two rows are BYTE FOR BYTE IDENTICAL, because
                   # SWAP is an exchange.  The simulator logs both:
                   # "SWAP started at half-word 3970" is p.65's and
                   # "at half-word 4908" is p.80's.
                   #
                   # THE RETURN WAS PREDICTED BEFORE IT WAS RUN.
                   # printed p.27 is ASSIGN's caller -- "X24
                   # LVI,$15,X242" then "X241 B,T ASIGN" -- so $15
                   # holds X242 = 001467.00 throughout, and
                   # "B,1.00($15)" is one word past it: 001470.00,
                   # p.27 line 11.  X ERR AD now holds 001471.40,
                   # which is what p.27 line 12's "SIC,X ERR AD"
                   # stores there, so the path is confirmed to the
                   # instruction.
                   #
                   # p.27 line 13 is "BZXCZ,XERROR  -IF ASSIGNMENT
                   # ERROR" AND THE BRANCH IS TAKEN.  The run enters
                   # the IPL bootstrap's error routine at XERROR
                   # (000133.00) and HALTS at 000167.40, which
                   # assembles 000167.44 00 -- "BD,$", a deliberate
                   # stop -- and is the last half word of X6ERR.
                   # printed p.5 lines 29, 37, 40 and 46 all branch
                   # there with the comment "-EXHAUSTED ALL CHANNELS
                   # OR ...".
                   #
                   # SO THE RUN NO LONGER ENDS BY FALLING INTO ZEROS.
                   # It ends on a halt MCP chose, in a routine MCP
                   # wrote, having recorded in X ERR AD where the
                   # decision was made.  pc_check is no longer 0: the
                   # instruction counter is SITTING on the halt.
                   pc_check=239,
                   pc_trail_check=239,
                   step_cap=40000000,
                   pc_trail=True,
                   op_trail=True,
                   ipl=True))


if __name__ == "__main__":
    main()
