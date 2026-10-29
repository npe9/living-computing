# Symbolics 3600 Lisp machine (1983)

The Symbolics 3600 was a purpose-built workstation for Lisp, developed
in Cambridge, Massachusetts by Symbolics. Its architecture carried type
information with data and used a writable microprogrammed processor to
implement Lisp operations, stack and control machinery, memory
management, and traps directly beneath the Genera software environment.
It is the first target for the repository's Lisp-machine work because a
technical summary, microcode listing, block diagram, field-maintenance
manual, and Lisp Machine Summary survive together. Later 36xx and Ivory
systems are descendants and comparison targets, not substitutes for
the original 3600.

Bluespec implementation: `bsv/` (not started).

See [`plan.md`](plan.md) for the evidence gates and staged model.
The primary-source acquisition manifest is [`docs/README.md`](docs/README.md).

Sources: Symbolics, *3600 Technical Summary* (February 1983), *Lisp
Machine Summary, 3600 Edition* (August 1983), *3600 Microcode*
(December 1983), *3600 Block Diagram* (1985), and *Symbolics 3600 Series
Basic Field Maintenance* (July 1986); Symbolics hardware memoranda. The
dates are retained because later 3600-series documents may describe
revisions not present in the first machine.
