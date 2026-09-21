#!/usr/bin/env python3
"""line_addresses.py -- print the address of every instruction line in a
STRAP program, so a hang address can be checked against its source row.

WHY THIS EXISTS.  Every hand-written test in this suite records the
addresses at which its injections must halt, and those addresses are the
whole evidence that an injection was caught by the check written for it
rather than by something downstream.  They were being derived by hand,
which is the one thing this project has learned not to do with octal:
every address written by eye here has been wrong.  Worse, an address
derived by a throwaway script is unverifiable by the next reader.

HOW IT WORKS, and why it is honest.  The assembler has no listing mode
and reports only the symbol table, so this puts a unique label on every
instruction line, assembles THAT, and reads the labels back.  The
program is not re-implemented or approximated: the addresses come from
the same `assemble()` every test uses.  Lines that already carry a label
keep it and are reported under their own name.

Lines that set or consume the location counter (SLC, END) and data
lines (DD) are left alone: a label on an SLC binds before the counter
moves, which would report the wrong address rather than fail loudly.

THE BIT OFFSET IS PRINTED IN OCTAL, like the listings and like every
address recorded in run_tests.sh: 004107.40 is word 04107, bit 32.  The
ASSEMBLER's own source syntax is decimal unless a "(8)" radix prefix
says otherwise, so "3.57" in a program is IBM bit 57 while this tool
prints that same place as 3.71.  Mixing the two is an easy way to write
down an address that is off by eight, and this tool exists partly to
stop that being done by hand.

Usage:  python3 line_addresses.py programs/some_program.strap
Output: one row per instruction --
    hw=4239  004107.40  BB,  WLOW, $   ! hang if on -- must be suppressed
"""

import re
import sys

from strap_asm import assemble, AssemblerError

# SLC moves the location counter and END takes a target; a label on
# either binds at the wrong moment.  DD lines are data, and this tool
# reports instructions.
SKIP = re.compile(r'^(SLC|END|DD)\b')


def line_addresses(source):
    """Return [(address_in_bits, label_or_None, source_line)] per instruction."""
    src = source.split('\n')
    relabelled = []
    generated = {}       # generated label -> source line index
    existing = {}        # existing label  -> source line index
    for i, line in enumerate(src):
        indented = re.match(r'^(\s+)(\S.*)$', line)
        labelled = re.match(r'^(\S+)\s', line)
        if not line.strip() or line.lstrip().startswith('!'):
            relabelled.append(line)
        elif indented and not SKIP.match(indented.group(2)):
            name = '_LA%04d' % i
            generated[name] = i
            pad = indented.group(1)
            # Keep the operand column where it was; the label only
            # occupies space the original indentation already had.
            if len(pad) > len(name):
                relabelled.append(name + pad[len(name):] + indented.group(2))
            else:
                relabelled.append(name + ' ' + indented.group(2))
        else:
            if labelled and not SKIP.match(line.split(None, 1)[-1]):
                existing[labelled.group(1)] = i
            relabelled.append(line)

    prog = assemble('\n'.join(relabelled))
    rows = []
    for name, i in list(generated.items()) + list(existing.items()):
        if name in prog.symtab:
            rows.append((prog.symtab[name],
                         None if name.startswith('_LA') else name,
                         src[i]))
    # Sort by ADDRESS ONLY.  Sorting the whole tuple compares the
    # label next when two rows share an address -- which happens as
    # soon as a program has both a labelled row and an unlabelled one
    # at the same place (a SYN, or a CNOP that emits nothing) -- and
    # then str vs None raises.  Python's sort is stable, so ties keep
    # their source order.
    rows.sort(key=lambda r: r[0])
    return rows


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} program.strap", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        source = f.read()
    try:
        for bits, label, line in line_addresses(source):
            text = line.strip()
            if label:                      # don't print the label twice
                text = text[len(label):].strip()
            print(f"hw={bits // 32:<6d} {bits // 64:06o}.{bits % 64:02o}"
                  f"  {label or '':<8}{text}")
    except AssemblerError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
