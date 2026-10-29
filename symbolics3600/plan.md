# Symbolics 3600 reproduction plan

## Scope

Model the original Symbolics 3600 architectural and microarchitectural
contract. Genera is an eventual software oracle, not permission to make
the hardware behave however a later Genera release expects. Variations
among the 3600, later 36xx systems, and Ivory must be recorded explicitly.

## Evidence gates

1. Acquire and checksum the Symbolics manuals, December 1983 microcode,
   block diagram, hardware memos, and any legally redistributable boot
   images or diagnostics. Create a revision matrix before combining
   claims from documents of different dates.
2. Transcribe the data types and word representation, virtual address
   and memory maps, registers, macroinstruction and microinstruction
   formats, dispatch rules, stack/cache behavior, traps, and bus/device
   interfaces. Cite printed pages and record unresolved contradictions.
3. Parse the printed microcode into a lossless intermediate form and
   check every printed field. If the listing contains assembled words,
   use them as the bit-exact oracle; otherwise keep inferred packing out
   of executable code until a second source confirms it.
4. Establish the minimum boot-visible device set and locate an original
   diagnostic or cold-load path. Keep host conveniences outside the
   architectural model.

## Staged implementation

1. Implement checked microcode and macroinstruction
   assemblers/disassemblers. Reserved encodings and unimplemented paths
   fail loudly.
2. Model the tagged datapath, register files, microsequencer, dispatch
   memory, and writable control store as separate Bluespec modules.
3. Add stack/cache, virtual memory, transport and type checks, traps,
   and cycle timing only where the hardware documents specify it.
4. Add the memory bus and the smallest diagnostic-visible devices. Use
   deterministic device models and keep workstation peripherals outside
   the CPU until software reaches them.
5. Run original microcode first, then a cold-load/diagnostic, and only
   then attempt an appropriately revisioned Genera image. Trace each
   boot failure to a documented hardware or device contract.

## Definition of the first milestone

The document/revision matrix is checked in; both instruction formats
are inventoried; the microcode parser preserves a complete listing
round-trip; and a Bluesim microsequencer executes a short sourced
sequence through the tagged datapath. The full repository test suite
remains green.
