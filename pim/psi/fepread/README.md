# psi/fepread: pimfep.ptf's method bodies, read (OURS)

Scripts behind `docs/fep_services.md` §6: what the PSI's front-end
package `pimfep.ptf` does with each FEP command, read from its compiled
ESP (KL0) code. Nothing is executed; the packages are read in memory
from `docs/nonlocal/` through `psi/held.py`. `asm/ptfdump.py` and
`psi/librarian.py` are imported read-only.

Rerun (from `pim/`, under a second):

    python3 -I psi/fepread/check.py

It prints one PASS line, or a FAIL line per fact of §6 that no longer
holds. It is not yet in `run_tests.sh`; it should be.

| File | What it is |
|---|---|
| `ptfread.py` | Lists a predicate cell by cell with its constant pool, class references, selectors, local calls and hash-switch tables resolved. `ptfread.py PKG [CLASS [NAME[/N]]] [--skel]`, `PKG --strings`, `PKG --keys` |
| `witness.py` | The 40 opcode readings §6 rests on, each beside the source that shows it (36 from `paragraph.ptf` against its held ESP source, 4 from PIMOS's source for the other end of a message), and the opcodes used with no witness. `witness.py --check` |
| `fepfacts.py` | The facts of §6 computed from the cells. `fepfacts.py handlers` prints §6.2's 63-row table, `extra` what the PSI handles and PIMOS never sends, `strings` the login classes' strings, `facts` the rest |
| `check.py` | Pins all of it |

Opcode NUMBERS are not printed in any held document; the MNEMONICS are
(TM-444 PDF p6-16, 30-31; TR-236 PDF p5), so a number is tied to a
mnemonic only by a witness (`psi/kl0_opcodes.tsv`). A reading that
rests on an unwitnessed opcode is graded INFERENCE in §6.
