# INMOS IMS T800 transputer (1987)

The IMS T800, designed by INMOS in Bristol, combined a 32-bit processor,
on-chip floating-point unit, scheduler and timer support for concurrent
processes, and four serial links intended to compose computers from
many identical chips. Its compact instruction encoding uses a small set
of direct opcodes plus prefix instructions, while the execution model
and links were designed alongside occam. This directory fixes the T800
as the initial transputer target; the T414/T425/T801/T805 and support
chips are related machines whose differences must remain explicit.

Bluespec implementation: `bsv/` (not started).

See [`plan.md`](plan.md) for the evidence gates and staged model.
The primary-source acquisition manifest is [`docs/README.md`](docs/README.md).

Sources: INMOS, *Transputer Architecture Reference Manual*; *Transputer
Databook*, second edition (1989), including "Transputer architecture"
and "IMS T800 engineering data"; INMOS Technical Note 6, *IMS T800
Architecture* (March 1987); the INMOS occam language and toolset manuals.
