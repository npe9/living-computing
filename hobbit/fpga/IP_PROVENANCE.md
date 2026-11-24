# IP provenance for the ULX3S build (append-only)

Every file under `hobbit/fpga/` that was not written for this project, or
that was derived from someone else's code, is listed here with its source,
licence and what was changed.  The repository is public: only permissively
licensed material is copied in.  Entries are appended, never rewritten;
each agent adds its own section.

## Quart and interrupt path (`fpga/dev/quart/`, `fpga/dev/intc/`), 2026-11-24

**Nothing third-party is copied.**  `HobbitQuart.bsv` (including its 8N1
transmitter and receiver), `HobbitIntc.bsv`, the testbenches and
`quart_trace.py` were written for this project.

Reviewed and *not* used:

- `~/src/ulx3s-experiments/flute-m50/src/Uart_Pins.bsv` (an 8N1 pin bridge
  for Flute's UART, 175 lines).  The file carries no copyright or licence
  line and its tree has no LICENSE file, so its terms are unknown; nothing
  was copied from it.  The Quart's pin logic is its own (2-flop
  synchroniser, mid-bit sampling, a one-byte hold as the SC68C94's receive
  shift register).

Used as tools or libraries, not copied into the tree:

- The Bluespec compiler's standard library (`FIFOF`, `RegFile`, `Vector`,
  `GetPut`, `StmtFSM`), and at synthesis time its Verilog cells
  (`$BLUESPECDIR/Verilog/FIFO2.v`, `RegFile.v`), read by `synth.sh` from the
  bsc 2026.01 installation.  bsc's `COPYING`: copyright Bluespec Inc.,
  BSD-3-Clause.

Behaviour sources (documents, not code): the SC68C94 product specification
(Philips, 27 April 1994) and the 1990 SC26C94/SC68C94 preliminary
specification, held out of git per `hobbit/docs/devices/MANIFEST.md`;
1st Edition Plan 9's `io.h`, `deveia.c`, `trap.c`, `devincon.c`
(`hobbit/tools/plan9-1e/`); `hobbit/tools/p9boot.py`'s device models.
