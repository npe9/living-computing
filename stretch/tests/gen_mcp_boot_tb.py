#!/usr/bin/env python3
"""gen_mcp_boot_tb.py -- boot MCP's own bootstrap on the model, from a
tape image in a host file.  docs/boot_plan.md M3, the step after the
transcription.

IT RUNS.  MCP's bootstrap executes from end to end on this model,
off a tape built from the thirteen transcribed pages, and hands off
to printed p.15's MCP INITIALIZATION -- which is not transcribed, so
it then executes the zeros past X BS END and halts.

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
from mcp_image import build
from opcodes import INDICATOR_BITS


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


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} ModuleName", file=sys.stderr)
        sys.exit(1)
    module_name = sys.argv[1]

    prog, src, defined, external = build()

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
        ("mcp_end_of_prosa_bit_X0", "16", (1 << (63 - 25)) | (131070 << 18)),

        # >>> THE ONE THAT SAYS IT NEVER STUMBLED <<<
        # X ERR AD, printed p.13 line 37, "-LOCATION OF ERROR +1.0".
        # Every error site on pp.3-6 does "SIC,X ERR AD" before
        # branching to X ERROR, and the instruction counter is never
        # zero inside the bootstrap -- so zero here means NO ERROR
        # SITE EVER RAN.
        ("mcp_x_err_ad", str(sym("XERRAD")), 0),

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
        ("mcp_indicators_word11", str(IND_WORD),
         _ind("RZ") | _ind("XVZ") | _ind("XF") | _ind("AD")),

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
        ("mcp_x15_word31", "31", 0x0004400A06480000),

        # THE LOAD ITSELF, and only the last word is a fair witness.
        # X IPL BS used to be checked here and cannot be: the program
        # legitimately overwrites it, because printed p.3's CCW copies
        # the channel's control word to exactly that address.  The
        # last word of the 368-word record is never written by the
        # bootstrap, so a truncated load fails here and nowhere else.
        ("mcp_loaded_last_word", str(sym("XBSEND") - 1),
         prog.words[sym("XBSEND") - 1]),
    ]

    print(generate(module_name, prog, checks,
                   # IT STOPS IN MCP'S OWN DELAY LOOP.
                   # 169 is half-word 169 = 000124.40, which is
                   # printed p.4 line 32's "CB,0,$" -- count and
                   # branch to ITSELF, the wait MCP does after
                   # RELEASE DISK.  The harness stops on "an
                   # instruction branched to its own address", which
                   # is the BEW,$ idiom it was built for and is also
                   # exactly this loop, so the run ends after one
                   # decrement.  THAT IS A HARNESS LIMIT, NOT A MODEL
                   # ONE, and it is why the count in word 16 is
                   # 131,070 rather than 0.
                   #
                   # IT USED TO BE 0, by a different route: see the
                   # indicator check above for why that route was an
                   # artifact of there being no disk.
                   pc_check=169,
                   step_cap=12000000,
                   ipl=True))


if __name__ == "__main__":
    main()
