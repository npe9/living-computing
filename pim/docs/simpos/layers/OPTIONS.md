# Routes to running SIMPOS code

The constraint that decides between the routes is not the engine. It is that **no route has SIMPOS
itself**:

- The held `.ptf` templates name 143 distinct `simpos##` classes (FORMATS.md §2), and none of them
  is held as template or source.
- The SIMPOS IPL image and the librarian/loader (which linearises inheritance and builds object
  descriptors) are also not held.

Whatever executes KL0 must therefore be paired with a reconstructed loader and a reconstructed
SIMPOS class library. What any route can run first is the held classes with no path to `simpos##`:

- 102 of 554 transitively (172 directly), MEASURED with the caveats of FORMATS.md §2;
- mostly paragraph icon/data classes, pimmcsp console tables, and `fep_command_code_table`.

## (a) PSI-III emulator running the held microcode

| | |
|---|---|
| Held | `syspsi`, the 32K control store, version 50.17 (FORMATS.md §3). `sysidat`, the KL0 decode table. `pimm.MEkbn`, the KL1 firmware. The boot script showing the console sequence. Thesis chapter 3 on the PSI-III pipeline and tag architecture |
| Missing | Bit-exact microword format and hardware semantics (other agent's work). `sysinit` meaning. The `.kbn` IPL-image format and the expected initial memory: PCBs, area tables, interrupt vector, heap layout. The object-descriptor and class-object layout the microcode dereferences. All of SIMPOS |
| What it would give | The authoritative KL0 semantics, including opcode ↔ behaviour, built-ins, tags, method dispatch and exceptions, with no reliance on missing manuals. It is the only route that is faithful by construction |
| Verification | (1) Reach the KL0 dispatch through `sysidat` for each used opcode. (2) Execute hand-built KL0 for `fep_command_code_table:convert/3` (no SIMPOS dependency, output known: 98 of 100 names agree with PIMOS numbering, binary_reverse_engineering.md §4.3). (3) Pseudo-PIM: boot `pimm.MEkbn` the way `boot.init` does, if a PIMOS IPL image is held elsewhere in the repo |
| Cost / risk | Highest. Every unknown about memory layout must be guessed before the first instruction runs. A blank machine with nothing to load |

## (b) KL0 interpreter running the `.ptf` code

| | |
|---|---|
| Held | The six `.ptf` packages, fully parsed at container level. The tag names (KL0.md §2; pairing INFERENCE, 6 anchors). The instruction word format (TR-265). WAM-level semantics with stack frames (TH App C, TM-444). Method-dispatch scheme (TH App A). Header kinds (FORMATS.md §2). About 10 opcode readings |
| Missing | Opcode ↔ mnemonic for about 100 class-0 and 110 class-1 opcodes. Built-in semantics per opcode. The trailer grammar in full. Loader rules (linearisation and after-demon order, ESP.md §5). The `simpos##` library |
| What it would give | Execution of the held compiled code at the abstraction SIMPOS was written for, with descriptors laid out freely |
| Verification | (1) `fep_command_code_table:convert/3`: run each of 102 codes and compare with `pimos.vmac` names. (2) Run `kl0_tag:integer_to_mnemonic/3` over keys 0–57. It must return the six anchored pairs (KL0.md §2) and a total function on the 49 keys. This tests the hash-switch and atom-return instructions; it would *establish*, not check, the other 43 pairings (3) The 55 transitively SIMPOS-free paragraph classes (mostly data classes, so this checks constants and vectors more than control) against their held `.esp` source: behaviour predicted from source. (4) Each opcode reading gets the discriminating-test treatment: two or more independent known-plaintext witnesses |
| Cost / risk | Medium. Opcode naming is a known-plaintext grind with an oracle. Built-ins are the long tail |

## (c) ESP compiler or interpreter on a host

| | |
|---|---|
| Held | The language spec (ESP.md: TM-388 and PRG normative, TR-044 history). 83 source files with a matching template package. Worked inheritance and method-combination examples |
| Missing | Exact operator table tail and standard-macro constant tables. After-demon order. Built-in semantics, the same gap as (b), but only at name level, which the docs cover better than opcodes. The SIMPOS library |
| What it would give | A way to *write* the missing SIMPOS classes. Every reconstruction of `simpos##symbolizer`, `string`, `process`, `window` and the rest needs this, whichever engine runs it |
| Verification | (1) Compile paragraph `.esp` and compare header kinds, predicate set, `$or$N` count, slot-init predicates and trailer nature vectors class-by-class with `paragraph.ptf`. This is structural; a version skew of 3200 against 3500 is expected. (2) Inheritance and combination tests from TM-388 pp.39 and 42. (3) If (b) exists: KL0 back-end output byte-compared to `paragraph.ptf` per predicate |
| Cost / risk | Medium. The spec is good. Fidelity risk if the host interpreter's semantics drift from KL0's (e.g. OR-local cut, cdr-first lists, slot restrictions) |

## Recommendation

Build **(b) + (c) together**, sharing one KL0 term and stack model and one reconstructed loader;
keep **(a)** as the long-term authority.

1. **Loader first** (shared). Parse templates, linearise natures per TM-388, combine methods, and
   build descriptor hash tables with key `n·2^24+a+n`. Make the after-demon order a switch.
2. **(b) on SIMPOS-free classes.** Start with `kl0_tag` and `fep_command_code_table` (known
   outputs), then the paragraph classes with source. Each opcode is named only with
   known-plaintext witnesses.
3. **(c) as an ESP→KL0 compiler**, targeting the same instruction encoding. It is validated
   structurally against `paragraph.ptf`. It is then used to write the minimal `simpos##` classes
   the held packages need, ordered by the reference counts in `C/x/deps.txt`: symbolizer, string,
   process, font, and so on.
4. **(a)** when the microword work lands. It can then replace guesses in (b): per-opcode behaviour
   read from microcode via `sysidat` is the authority over inference.

This order gets runnable, checkable results soonest. The reconstructed SIMPOS classes must be
labelled as stand-ins (scaffolding) and not as recovered SIMPOS. The goal remains finding the real
SIMPOS (IPL image, librarian, the KL0 manual MP7002-1, Ueda et al. 1984).
