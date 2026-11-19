# AT&T 92010 Hobbit (1993)

The AT&T 92010 Hobbit, the second-generation implementation of Bell
Laboratories' CRISP (C-language Reduced Instruction Set Processor)
architecture, is a 32-bit memory-to-memory microprocessor with no
programmer-visible general registers. The top of the stack lives in a
64-register, 256-byte on-chip stack cache that the hardware allocates
as the stack grows, so operands are named by stack offsets or memory
addresses and the compiler does no register allocation. Instructions
are built from 16-bit parcels and encode in one, three or five parcels
(2, 6 or 10 bytes); the one-parcel form is restricted to the 32 opcode
and addressing-mode combinations that frequency analysis of compiled
UNIX C source found most common. A static prediction bit per
conditional jump and branch folding — the branch target is stored in
the next-address field of the preceding decoded instruction — remove
the branch penalty.

The chip integrates a 3 Kbyte three-way set-associative prefetch buffer
cache, a 32-entry decoded-instruction cache, dual 32-entry TLBs for text
and data, and an MMU with paged and non-paged segments; it consumes
250 mW at 3.3 V and 20 MHz and runs from 5 V at 30 MHz, in a 132-pin
PQFP on 0.9 µm double-level-metal CMOS. It was built for pen-based
"personal communicators": Apple paid AT&T to develop the low-power
second-generation CRISP for the Newton and then shipped the Newton on
ARM instead, EO chose the Hobbit for its personal communicators, and
Be, Inc.'s original BeBox was a dual-Hobbit machine with three DSP
chips until AT&T cancelled the Hobbit line and Be moved to PowerPC.
This directory fixes the ATT92010 as the target; the earlier ATT2100
hardware specification (March 1991) and the CRISP ancestor are related
machines whose differences must remain explicit.

Bluespec implementation: `bsv/` (not started).

See [`plan.md`](plan.md) for the evidence gates and staged model.
The primary-source acquisition manifest is [`docs/README.md`](docs/README.md).

Sources: AT&T Microelectronics, *ATT92010 Hobbit Microprocessor
Programmer's Reference Manual* (January 1993); *ATT92010 Hobbit
Microprocessor Advance Data Sheet* (December 1992); AT&T, *ATT2100
Microprocessor Hardware Specification*, release 1.7.2 (31 March 1991);
M. Slater, "AT&T Sampling Low-Power 'Hobbit' Processor", *Microprocessor
Report* 6:2 (12 February 1992); S. Horowitz, "'Our' Toy Story", *Be
Newsletter* 3 (20 December 1995).
