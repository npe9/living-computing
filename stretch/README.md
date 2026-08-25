# IBM 7030 "Stretch" (1961)

Stephen Dunwell (project), Werner Buchholz, Gerrit Blaauw, Fred Brooks, John Cocke, Harwood Kolsky, Erich Bloch. IBM's first transistorized supercomputer; delivered to Los Alamos, April 1961. Introduced instruction pipelining and lookahead, multiprogramming/interrupts, memory protection, a 64-bit word, the 8-bit byte (word coined here), bit-addressable variable-field-length arithmetic, and the STRAP assembler.

Key facts (Reference Manual 22-6530-2):
- 64-bit word; memory 16,384 × 64-bit modules, up to 262,144 words (18-bit word address).
- Instructions are half-word (32-bit) or full-word (64-bit); the instruction counter is a 19-bit half-word address.
- 16 index registers (X0–X15; X0 = "no index"), each holding value (24 bits), count (18 bits) and refill (18 bits) fields.
- Floating point: 64-bit, 10-bit exponent + sign, 48-bit fraction + sign, three flag bits (T, U, V); single and double precision (96-bit fraction) .
- Variable field length: bit addresses (24 bits = 18-bit word + 6-bit bit offset), field length 1–64 bits, byte size 1–8 bits, binary or decimal, signed or unsigned.
- 64 indicator bits, interrupt system with mask register, address boundary registers for protection, interval timer and clock.

Bluespec implementation: `bsv/` — see `bsv/README.md`.

STRAP assembler (codesign loop: assembles real programs from the
Programming Examples manual and runs them on the Bluespec model):
`strap/` — see `strap/README.md`.

Sources (bitsavers.org/pdf/ibm/7030/): *IBM 7030 Data Processing System Reference Manual* (22-6530-2); Buchholz (ed.), *Planning a Computer System: Project Stretch* (1962); X22-6533 pocket card; 7030 Opcode List.
