# IBM 7030 "Stretch" (1961)

Stephen Dunwell (project), Werner Buchholz, Gerrit Blaauw, Fred Brooks, John Cocke, Harwood Kolsky, Erich Bloch. IBM's first transistorized supercomputer; delivered to Los Alamos, April 1961. Introduced instruction pipelining and lookahead, multiprogramming/interrupts, memory protection, a 64-bit word, the 8-bit byte (word coined here), bit-addressable variable-field-length arithmetic, and the STRAP assembler.

Key facts (Reference Manual 22-6530-2):
- 64-bit word; memory 16,384 × 64-bit modules, up to 262,144 words (18-bit word address).
- Instructions are half-word (32-bit) or full-word (64-bit); the instruction counter is a 19-bit half-word address.
- 16 index registers (X0–X15; X0 = "no index"), each holding value (24 bits), count (18 bits) and refill (18 bits) fields.
- Floating point: 64-bit, 10-bit exponent + sign, 48-bit fraction + sign, three flag bits (T, U, V); single and double precision (96-bit fraction) .
- Variable field length: bit addresses (24 bits = 18-bit word + 6-bit bit offset), field length 1–64 bits, byte size 1–8 bits, binary or decimal, signed or unsigned.
- 64 indicator bits, interrupt system with mask register, address boundary registers for protection, interval timer and clock.

## Layout

| directory | what is in it |
|---|---|
| `bsv/` | the Bluespec model of the machine — see `bsv/README.md` |
| `strap/` | the assembler and the host-side tools it needs: `strap_asm.py`, `opcodes.py`, `charsets.py`, `cards.py`, `mktape.py`, `mcp_image.py`, `listing_oracle.py`, `line_addresses.py`, `iocd.py`, `prosa.py`, `mcp_crop.sh` — see `strap/README.md` |
| `decks/` | 353 STRAP card decks: transcriptions of the scanned diagnostic and MCP listings, plus the test programs written to pin model behaviour |
| `tests/` | the harness — one `verify_*.py` per transcribed listing, the `gen_*_tb.py` testbench generators, the `run_*.sh` runners, the coverage audits, and `run_tests.sh`, which runs all of it |
| `docs/` | the scanned primary sources, and this project's structured notes on them |

The split between `strap/` and `tests/`+`decks/` is the one rule to
keep: `strap/` is code the machine's tooling needs, and nothing in it
imports from `tests/` (checked: every `import` in `strap/*.py` names
either the standard library or another `strap/` module).

Running the harness: `cd tests && ./run_tests.sh`. **The verifiers are
written to be run from `tests/`** — they open their decks as
`../decks/NAME.strap`, and `run_tests.sh` exports
`PYTHONPATH=$TESTS_DIR/../strap:$TESTS_DIR` so `import strap_asm`
resolves wherever it is run from — but it does not `cd` to `tests/`
itself, so the decks are found only when you are already there. Two things
that are *not* invoked from a known directory — `strap/mcp_image.py`,
which is a tool, and `tests/verify_mktape.py`, which shells out to
another script — resolve their paths against `__file__` instead. A
CWD-relative path in the wrong one of those two places is exactly what
broke on the 2026-10-18 reorganisation, and `strap/mcp_crop.sh` had
the same bug the day before.

The codesign loop: real historical Stretch programs, taken from the
Programming Examples manual and from scanned IBM diagnostic listings,
are assembled by `strap/` and run on `bsv/`, and any decode/execute gap
they exercise is a genuine finding about the hardware model.

Sources (bitsavers.org/pdf/ibm/7030/): *IBM 7030 Data Processing System Reference Manual* (22-6530-2); Buchholz (ed.), *Planning a Computer System: Project Stretch* (1962); X22-6533 pocket card; 7030 Opcode List.
