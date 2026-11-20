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

State: one goal run to completion. No scheduler, no suspension queue
(a goal that must wait raises `Suspend`), no garbage collection, 13
instructions.

    python3 ref/pimm/test_jtoa.py

runs `jis_to_ascii:convert_element/2` from the image for every 16-bit
key against an oracle built from the predicate's source and PIMOS's own
ASCII-to-JIS table.

Next, in order: `convert_loop/4` (goals, `enqueue_goal`/`execute`, the
string built-ins, and a body built-in waiting on an unbound variable),
then `convert/2`.
