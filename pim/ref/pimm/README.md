# PIM/m reference model (scaffold)

`pimm.py` is a host-side model of the PIM/m KL1-B machine that executes
the PIMOS binaries' own cells: it loads `pimm_ipl.kbn` through
`asm/kbn.py` and runs instructions with the machine's tags, encodings
and relative labels. It is the scaffold of roadmap decision 3
(`docs/pimos_roadmap.md`): it exists to find out what the instructions
do, cheaply, and to be the trace the Bluespec model is diffed against.
Nothing is claimed for the project on this model alone.

Rules it keeps:

- An instruction it does not implement raises `Unimplemented`. It never
  guesses and never skips.
- Every operand reading comes from object code paired with KL1 source,
  and is written down in `docs/pimm_semantics.md` with what checked it.

State: all machine state is registers and memory cells (goal records,
the ready queue, suspension records, hooked variables; layouts in
`asm/pimm_layout.py`, the project's design). One processor, newest
goal first, no priorities; body built-ins that wait become goals of a
stub (`asm/pimm_stubs.py`); 8- and 16-bit strings; 28 instructions. No
garbage collection, no MRB, no shoen, no exceptions.

    python3 ref/pimm/test_jtoa.py

runs module `jis_to_ascii` from the image against an oracle built from
its source and PIMOS's own ASCII-to-JIS table: `convert_element/2` for
every 16-bit key, and `convert/2` on strings, where it turns
full-width "PIMOS 3.6" into the 8-bit string `PIMOS 3.6`.

## Lockstep

With `m.tr = []` the model writes one line per event (instruction
taken, register write, memory write, end of reduction; the format is in
`docs/pimm_semantics.md`). `lockstep_jtoa.py` compares that trace with
the Bluespec core's (`bsv/PimmJtoaTb.bsv`), line for line:

    bsv/run_pimm_jtoa.sh

`convert_element/2` is in lockstep, including a goal suspending on an
unbound argument and waking when it is bound. `convert_loop/4` and
`convert/2` are not yet on Bluespec: they need the string built-ins,
waiting built-ins, `enqueue_goal` and `execute` there.

Next: those, then `convert/2` in lockstep; then the next module with
source (`builtin_utility`, `scsi_common`). The reference model is
kept no more than one such step ahead of the Bluespec.
