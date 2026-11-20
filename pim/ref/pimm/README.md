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

State: goals on one LIFO ready stack (no priorities, one processor);
suspension on unbound variables, kept in a side table and not as the
machine's HOOK cells; body built-ins that wait for their inputs; 8-
and 16-bit strings; 28 instructions. No garbage collection, no MRB, no
shoen, no exceptions.

    python3 ref/pimm/test_jtoa.py

runs module `jis_to_ascii` from the image against an oracle built from
its source and PIMOS's own ASCII-to-JIS table: `convert_element/2` for
every 16-bit key, and `convert/2` on strings, where it turns
full-width "PIMOS 3.6" into the 8-bit string `PIMOS 3.6`.

Next: the same module on the Bluespec side (rung R2), then the next
module with source (`builtin_utility`, `scsi_common`).
