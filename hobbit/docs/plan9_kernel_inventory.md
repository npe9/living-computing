# Plan 9 1e Hobbit kernel: boot path, memory map, device inventory, build requirements

This is the A3 (build the kernel) and Goal B (every device) reference. It is
written so that the kernel build step and each device model can be implemented
without re-reading the 1e tree.

## Provenance and how to read a cite

* Archive: `/tmp/p9/plan9-1e.tar.bz2`,
  `sha256 8718e279aa35b10a9391f330976d31c177bad00de40e7f0f67232ffa54fb7d77`
  (matches `docs/plan9_boot_plan.md`), extracted with
  `tar xjf plan9-1e.tar.bz2` into `/tmp/p9inv/`, producing
  `/tmp/p9inv/plan9-1e/`.
* The kernel port itself is also vendored. Verified byte-identical:

  ```
  diff -rq tools/plan9-1e/sys/src/9/hobbit /tmp/p9inv/plan9-1e/sys/src/9/hobbit   # no output
  ```

  So `K/` below means **both** `tools/plan9-1e/sys/src/9/hobbit/` and the
  archive's `sys/src/9/hobbit/`.
* `P/` = `sys/src/9/port/`, `B/` = `sys/src/9/boot/`, `I/` =
  `hobbit/include/` **in the 1e release** (only `K/` is vendored; `P/`, `B/`,
  `I/` are read from the pinned archive and are **not** added to this repo).
* `PRM p. x-y` = printed page of
  `docs/ATT92010_Hobbit_Programmers_Reference_Jan93.pdf`.
* Every cite is `file:line`. Values in the *computed* column are arithmetic on
  a cited macro and are labelled as such; nothing else is inferred. Anything
  the sources do not print is in §5, never filled in silently.
* The release ships **no kernel image**: the archive has no `/9/` tree and no
  `9cpu`/`9rom` binary (`docs/plan9_boot_plan.md`, "What the sources say").
  A3 produces the image; this document fixes what it must contain.

---

## 1. Boot path, file by file and address by address

### 1.1 Reset state (what the model must produce before any 1e code runs)

| Fact | Cite |
|---|---|
| Reset disables interrupts, flushes PFB and IC, sets `SHAD=0` (external reset), `PSW=0`, `CONFIG=0`, `PC=0`, enables NMI | PRM p. 1-35 (§1.11.1) |
| `PSW=0` means kernel level, physical addressing, tracing off, interrupts inhibited, **CSP = ISP** | PRM p. 1-35 |
| `CONFIG=0` means all caches off, timer interrupts off, demand prefetch | PRM p. 1-35 |
| `SP` and `MSP` are **undefined** after an external reset | PRM p. 1-35 (Note) |
| `_startup` re-initialises everything anyway | `K/raml.s:12-49` |

### 1.2 How a `9cpu` image is started

The 1e RAM kernel is not self-starting at address 0. It is loaded and started
by the ROM monitor (`9rom`) as a file:

| Fact | Cite |
|---|---|
| The monitor's boot command reads an `Fhdr`-format file and copies `txtsz` bytes to `txtaddr`, `datsz` to `dataddr`; `bsssz` is not written | `B/romboot.c:518-527` |
| It then sets `ppage0->argc/argv` in physical page 0 and **clears `ppage0->vectors`** so a fault returns to the ROM | `B/romboot.c:536-546` |
| It starts the program by writing the 4-byte `f.entry` to `#B/boot` | `B/romboot.c:550-553` |
| `#B/boot` turns that write into `gotopc(pc)` | `P/devboot.c:99-118` |
| `gotopc` sets `PSW = PSW_VP|PSW_UL`, `SHAD = ISP`, `ENTER R-16`, loads PC from the argument slot and **PSW = 0**, `VB = 0`, `CONFIG = PM|PE|IE|SE|PX|KL`, `FLUSH`, `KRET` | `K/roml.s:173-186` |
| Default `bootfile` for the ROM monitor is `/hobbit/9cpu` | `B/romboot.c:32-39` |

Consequence for A3/A4: **the kernel entry is `Fhdr.entry`, and it is entered
with `PSW=0` (physical, kernel level, CSP=ISP), `VB=0`, caches enabled**, which
is exactly the state `raml.s`'s first instructions assume. The model can boot a
`9cpu` image directly: load text/data at the Fhdr addresses, zero `bsssz`, set
`ppage0` (see §1.6) and jump to `entry`.

### 1.3 `K/raml.s` — `_startup` at `KTZERO` (file order: first text symbol)

Link base for `9cpu` is `-T0x80004000 -E0x80004000` (`K/mkfile:52`), and
`raml.z` is the first object on the link line, so `_startup` is the first text
and therefore at **0x80004000** (its own address is not printed; the base is).
Everything below is the section from `K/raml.s:12-49` and `:51-100`.

| Step | Instruction (cite) | Effect | Address (computed where marked †) |
|---|---|---|---|
| 1 | `FLUSH` (`raml.s:13`) — `FLUSHP; FLUSHI` (`raml.s:10`) | flush prefetch buffer + decoded-instruction cache | — |
| 2 | `MOV $(PM\|PE\|IE\|SE\|PX\|KL),%CONFIG` (`:14`) | prefetch mode+enable, instruction cache, stack cache, PC extension, kernel little-endian (`K/machine.h:24-29`) | — |
| 3 | `MOV $0,%PSW` (`:15`) | kernel, physical, CSP=ISP, IPL 0 | — |
| 4 | `MOV $PHYSADDR(MACHADDR+ISPOFFSET),%ISP` (`:16`) | set the interrupt stack | †`0x80002FE0` |
| 5 | `MOV %ISP,%SHAD` (`:17`) | SHAD = ISP (`K/machine.h:12`) | — |
| 6 | `WAIT` (`:18`) = `NOP;NOP;NOP` (`:9`) | settle | — |
| 7 | `ENTER R-16` (`:20`) | reserve a 16-byte frame. With `PSW=0` the current stack pointer **is** `ISP` (PRM p. 1-35) and `ENTER` alters the CSP (PRM pp. 3-19…3-21), so this is the frame CRET consumes at step 19; it is also why `_virtual` reloads `ISP` at `:52` after CRET has popped it | †ISP becomes `0x80002FD0` |
| 8 | `MOV $PHYSADDR(KSTBADDR),R0` (`:22`) | R0 = segment-table address | †`0x80001000` |
| 9 | `MOV R0,%STB` (`:23`) | **STB = 0x80001000**; 1024 four-byte STEs, i.e. 0x80001000..0x80001FFF | PRM p. 2-4 (1,024 entries, 4 KB) |
| 10 | `SUB3 $16,%ISP` (`:25`) | accumulator (`CSP+4`, i.e. `R4`) = ISP−16; `ADD3`/`SUB3` write the **accumulator**, not the named destination (PRM p. 3-43 `SUB3`, p. 3-5 `ADD3`), so the loop below decrements `R4` and `ISP` is unchanged | †`0x80002FC0` |
| 11 | clear loop `l0:` (`:26-30`) | `DQM $0,*R4` then `SUB $16,R4` until `R4 == 0x80001000`; 508 quad-words, i.e. exactly the two pages *below* the frame (the source's "clear two pages" (`:25`) is approximate: the frame itself, `0x80002FD0..0x80002FFF`, and the first 16 bytes of `KSTBADDR` are not touched) | †`0x80001010..0x80002FCF` |
| 12 | kernel STE (`:32-33`) `NPSTE(RAMBASE,1024,STE_C\|STE_W\|STE_V)` | segment 0x200 (0x80000000) → 4 MB identity, cacheable, writable, **not user** | written at †`0x80001800`, value †`0x803FF80B` |
| 13 | ROM STE (`:35-36`) `NPSTE(PROMBASE,128,STE_U\|STE_V)` | segment 0x300 (0xC0000000) → 512 KB at physical 0, user+valid, non-writable | at †`0x80001C00`, value †`0x0007F00D` |
| 14 | I/O **ACK** STE (`:38-39`) `NPSTE(IOBASE,4,STE_U\|STE_W\|STE_V)` — source comment `/* IIC hack */` | segment 0x2C0 (0xB0000000) → 16 KB identity, **user** accessible | at †`0x80001B00`, value †`0xB000300F` |
| 15 | I/O **NAK** STE (`:41-42`) `NPSTE(IOBASE+0x08000000,4,STE_W\|STE_V)` | segment 0x2E0 (0xB8000000) → 16 KB identity, kernel only | at †`0x80001B80`, value †`0xB800300B` |
| 16 | `MOV $(MACHADDR+SPOFFSET),R0` / `MOV R0,R4` (`:44-45`) | CRET frame word 0 **and** word 4 both get SP, so CRET's `SP` and `MSP` become equal (empty stack cache) | †`0x80002F00` |
| 17 | `MOV $_virtual(SB),R8` (`:46`) | CRET PC = `_virtual` | link-assigned |
| 18 | `MOV $(PSW_VP\|PSW_UL\|PSW_S),R12` (`:47`) | CRET PSW: virtual, user little-endian, CSP=SP | — |
| 19 | `FLUSH; CRET` (`:48-49`) | CRET loads SP/MSP from `*(ISP+0)`/`*(ISP+4)`, CATCHes to `*(ISP+8)`, restores PSW from `*(ISP+12)`, ISP += 16 | PRM p. 3-15 |

`STE`/`NPSTE` bit layout is `K/machine.h:86-97`; the hardware layout is PRM
Table 2-2 (p. 2-6, nonpaged: base 31:22, bound 21:12, cache 11, segment 3,
user 2, writable 1, valid 0).

### 1.4 `K/raml.s` — `_virtual` (now running virtually)

| Step | Cite | Effect |
|---|---|---|
| `MOV $(MACHADDR+ISPOFFSET),%ISP` | `raml.s:52` | ISP = 0x80002FE0 (virtual = physical, identity mapped by step 12) |
| `MOV $VBADDR,R4; MOV R4,%VB` | `raml.s:54-55` | **VB = 0x80000000** = `VBADDR` = `KDATABASE+0` (`K/mem.h:79`) |
| 14 × `MOV $_vectorN(SB),*R4` + `ADD $4,R4` | `raml.s:57-83` | install the **hardware** vector table at 0x80000000..0x80000037 (`VBSIZE 0x38`, `K/machine.h:136`) |
| `MOV *$PPAGE0(0x74),*$PPAGE0(0x08)` and `...0x0C)` | `raml.s:85-86` | copy the boot page's FP-interpreter entry into hardware vector slots 2 and 3 (niladic trap, unimplemented instruction) — offset **0x74**, see O2 |
| `MOV $MACHADDR,m(SB)` / `mach0(SB)` | `raml.s:88-89` | globals `m`, `mach0` = 0x80002000 (`K/rammain.c:14-15`) |
| clear BSS `edata`→`end` | `raml.s:91-97` | C runtime init |
| `CALL main(SB)` | `raml.s:99` | **control first reaches C here** → `K/rammain.c:89` |
| `RETURN` | `raml.s:100` | "better not" — must never return |

Hardware vector table (what the CPU reads, PRM Table 1-14 p. 1-20; entries are
`K/raml.s:57-83`). Two different "addresses" must not be confused: the *entry*
for `_vector0` is the word at **0x80000000** (VB+0), while the *code* of
`_vector0` lives somewhere in `raml.z` and its address is assigned by `zl` —
the sources do not print it, and nothing in the kernel depends on its value
(the CPU reads only the table).

| VB offset | index | stub | goes to |
|---|---|---|---|
| +0x00 | 0 | `_vector0` (`:230`) | syscall: `MOV $0,R0`, fall into `_exception` |
| +0x04 | 1 | `_vector1` (`:226`) | exception |
| +0x08 | 2 | `_vector2` (`:222`) | niladic trap (overwritten by `*0x74`) |
| +0x0C | 3 | `_vector3` (`:218`) | unimplemented instruction (overwritten by `*0x74`) |
| +0x10 | 4 | `_vector4` (`:214`) | NMI (level 0) |
| +0x14…+0x24 | 5…9 | `_vector5.._vector9` (`:210…:194`) | interrupt levels 1…5 |
| +0x28 | 10 | `_vectorA` (`:190`) | interrupt level 6 — **all board interrupts** |
| +0x2C | 11 | `_vectorB` (`:186`) | TIMER1 (a Plan 9 extension, see O5) |
| +0x30 | 12 | `_vectorC` (`:182`) | TIMER2 |
| +0x34 | 13 | `_vectorD` (`:178`) | FP exception |

### 1.5 The software vector table `_vectors` (`K/raml.s:286-300`)

`GLOBL _vectors(SB), $VBSIZE` + 14 `DATA` words. This is the table the stubs
dispatch through; index = the event number the stub writes to `R0`, i.e. the
stack-cache slot at `CSP+0` (the integer *accumulator* is `CSP+4`; the
stack-cache register mapping is stated in `sem/README.md` with PRM p. 1-7
Figure 1-4 and p. 1-28).

| `_vectors` offset | event (source comment) | target | cite |
|---|---|---|---|
| +0x00 | syscall | `$syscall` | `raml.s:287` |
| +0x04 | exception | `$trap` | `:288` |
| +0x08 | niladic trap | `$trap` | `:289` |
| +0x0C | unimplemented instruction | `$trap` | `:290` |
| +0x10 | non-maskable interrupt | `$trap` | `:291` |
| +0x14…+0x24 | interrupt 1…5 | `$trap` | `:292-296` |
| +0x28 | interrupt 6 | **`$interrupt`** | `:297` |
| +0x2C | timer 1 interrupt | `$trap` | `:298` |
| +0x30 | timer 2 interrupt | `$trap` | `:299` |
| +0x34 | FP exception | `$trap` | `:300` |

### 1.6 `K/rammain.c` — `main()` and the boot page

`main()` (`K/rammain.c:89-122`) runs in this order (all cites are that file):

| Order | Call | What it needs from the model |
|---|---|---|
| 1 | `active`/`machinit()` (`:91-93`) | nothing |
| 2 | `arginit()` (`:94`) | `ppage0->argc`, `->argv`, `->env` (`:51-56`, `:82-85`) |
| 3 | `confinit()` (`:95`) | `ppage0->memsize` (`:142`) |
| 4 | `xinit()` (`:96`) | RAM only |
| 5 | `printinit()` (`:97`) | `P/devcons.c:31-42` |
| 6 | `*IOCTLADDR = 0; IRQADDR->mask0 = mask1 = 0; delay(10); *IOCTLADDR = IOENABLE` (`:103-107`) | 0xB8000000 write port, 0xB8000080/84 |
| 7 | `eiasetup(0, EIAADDR)` (`:109`) | the Quart at 0xB0000100; installs IRQ1 (`K/deveia.c:523`) |
| 8 | `screeninit(0)` (`:110`) | **for `CONF=cpu` this is the stub in the config file** `K/cpu:47-53`, which does `eiaspecial(0,&printq,&kbdq,19200)` — this is what connects `print()` to the UART |
| 9 | `mmuinit()` (`:112`) | STB, `%STB` (`K/mmu.c:129-142`) |
| 10 | `pageinit(); procinit0(); initseg(); clockinit()` (`:113-116`) | `clockinit()` programs the DUART counter (`K/deveia.c:527-543`) |
| 11 | `chandevreset(); streaminit(); swapinit(); userinit(); schedinit()` (`:117-121`) | device resets in devtab order (§4.4) |

Boot parameter page `PPage0` (`I/rom.h:21-47`) is at `KZERO` —
`#define ppage0 ((PPage0*)KZERO)` (`K/rammain.c:18`), i.e. **0x80000000**, which
is the same memory as `VBADDR`. Field addresses (offset from `I/rom.h`):

| Field | Offset | Address (computed) | Writer |
|---|---|---|---|
| `vectors[16]` | 0x000 | 0x80000000 | `raml.s:57-83`; cleared by `B/romboot.c:546` |
| `msp`/`isp`/`sp`/`config`/`psw` | 0x040/44/48/4C/50 | 0x80000040… | saved by `roml.s:19-27` on reset; read by the monitor's `r` command (`B/romboot.c:561-572`) |
| `shad`/`vb`/`stb`/`fault`/`id` | 0x054…0x064 | 0x80000054… | `roml.s:23-27` |
| `r0`/`r16` | 0x068/0x06C | 0x80000068… | `roml.s:29` region / monitor |
| FP vector slot | **0x074** in asm, **0x084** in the header | 0x80000074 / 0x80000084 | `raml.s:85`, `roml.s:29` vs `I/rom.h:36-39` — O2 |
| `memsize` | 0x080 | 0x80000080 | `K/rommain.c:79`, read at `K/rammain.c:142,168` |
| `argc` | 0x200 | 0x80000200 | `B/romboot.c:536` |
| `argv[8]` | 0x204 | 0x80000204 | `B/romboot.c:537-539` |
| `argbuf[220]` | 0x224 | 0x80000224 | `B/romboot.c:747-749` |
| `env` (11 entries) | 0x300 | 0x80000300 | `B/romboot.c:46,93` (from `#r/nvram`) |

Minimum page-0 contents for a model boot of `9cpu`: `memsize` (bytes of RAM),
`argc ≥ 1`, `argv[]`, and `env` optional. `vectors` must be zero before
`raml.s` fills slots 0…13.

### 1.7 `K/mmu.c` — tables and the addresses they are built at

| Fact | Cite |
|---|---|
| `mmuinit`: `upte = xspanalloc(BY2PG,BY2PG,0)` — one page for the per-process user PTE page | `K/mmu.c:135` |
| `stb[SEGNUM(USERADDR)] = STE(PADDR(upte), STE_C\|STE_V)` — segment **0x3FF** entry, **paged** (STE bit 3 clear) | `K/mmu.c:136`; PRM Table 2-1 p. 2-5 |
| `upte += PGNUM(USERADDR)` → the entry for page 0x3FE of that segment = VA 0xFFFFE000 | `K/mmu.c:137` |
| `mmusetstb(PADDR(KSTBADDR))` → `%STB = 0x80001000 \| STB_C` | `K/mmu.c:138`, `K/raml.s:169-172`, `K/machine.h:86` |
| allocator caches: 5 STB pages, 10 PTB pages | `K/mmu.c:140-141` |
| `mmuwalk`: `table = &p->mmustb->va[SEGNUM(va)]`; a missing paged STE gets a fresh page table (`ptbinit` zeroes it), `*table = STE(pg->pa, STE_C\|STE_V)` | `K/mmu.c:144-171` |
| `putmmu`: `pa \| PTE_R\|PTE_C\|PTE_U`, then `*entry = (*entry & (0x7F<<4)) \| pa` — preserves bits 10:4 (hardware M plus PRM-reserved bits) | `K/mmu.c:181`, `:198`; PRM Table 2-3 p. 2-7 |
| `ptb[0] = 0x7F<<4`, `ptb[1] = 0` and `ptbuupdate` keep a 7-bit first/last page number in reserved PTE bits of the page table's first two entries; `ptbuclear` memsets the page and returns before using them | `K/mmu.c:77-110` (intent is not printed — O3) |
| `mmuiomap(ioa,npages)`: refuses if not segment-aligned or already mapped, else `stb[SEGNUM(ioa)] = NPSTE(ioa,npages,STE_W\|STE_V)` + `mmuflushpte` | `K/mmu.c:117-127` |
| `mapstack`: `*upte = PTE(p->upage->pa, PTE_W\|PTE_V)`; `%STB = p->mmustb->pa`; `u = (User*)USERADDR` | `K/mmu.c:257-274` |
| `invalidateu`: `*upte = 0` + `mmuflushpte(USERADDR)` | `K/mmu.c:276-281` |
| `flushmmu` falls back to the kernel STB and flushes the cache | `K/mmu.c:240-255` |

Where the tables live: the *kernel* segment table is fixed at
`KSTBADDR = KDATABASE+0x1000 = 0x80001000` (`K/mem.h:80`), inside the first
16 KB below `KTZERO`; per-process segment tables are `Page`s from the `Page`
allocator (physical pages above `PGROUND(end)`, `K/rammain.c:160-163`), and
each process's STB is installed by `mmusetstb` on context switch.

### 1.8 `K/trap.c` — where the C handlers are and what they read

| Fact | Cite |
|---|---|
| `events[16]` names every `cause` value 0…15 | `K/trap.c:12-29` |
| `exceptions[16]` names exception ids 0x0…0xF | `K/trap.c:31-48` |
| `setvector(v)` stores `vector[v->mask]`, ORs the bit into `irqmask`, and sets `IRQADDR->mask0/mask1` (bits 0-7 / 8-15) | `K/trap.c:120-130` |
| `interrupt(ur)` decodes `(status1&0xFF)<<8 \| (status0&0xFF)`, masks by `irqmask`, and dispatches in the fixed order INCON, SONIC, SCSI, SCSIDMA, QUART; **any other enabled bit panics** | `K/trap.c:132-172` |
| `trap(ur)` switches on `ur->cause`; `0x01` = exception, then on `ur->id` (Table 1-26 ids), `default` = reboot/panic | `K/trap.c:188-289` |
| `syscall(ur)`: `u->scallnr = ur->id`; args are `*(Sargs*)(ur->sp+BY2WD)`; result is written to `*(ulong*)(ur->sp+BY2WD)`; dispatch is `systab[u->scallnr]` | `K/trap.c:394-458`; `P/portdat.h:92-95`; `K/trap.c:392` (`../port/systab.h`) |
| syscall 0 is usurped as a breakpoint trap and the PC is wound back 2 | `K/trap.c:418-424` |
| `execregs()` builds the user Ureg at `UREGADDR` | `K/trap.c:469-481`, `K/mem.h:86` |
| `Ureg` is 8 words: `cause,user,id,fault,sp,msp,pc,psw` | `I/ureg.h:1-13` |

**The event frame / `Ureg` relationship is the one place the released sources
do not agree with the printed manual — see O4 before writing the A4 event
model.** In one sentence: `K/raml.s:233-300` writes `cause`, `fault`, `sp`,
`msp` into an 8-word `Ureg` at `ISP` and expects the hardware to have put
`id`, `pc`, `psw` at +8, +24 and +28; the PRM (pp. 1-37, 1-38, 3-29) prints a
16-byte frame with the three saved words at +4, +8, +12 after `ISP -= 16`.

### 1.9 `K/trap.c` entry points that the boot path uses

| Symbol | Reached from | Cite |
|---|---|---|
| `interrupt` | `_vectors+0x28` (level 6) | `K/raml.s:297` |
| `trap` | `_vectors+0x04/08/0C/10/14…24/2C/30/34` | `K/raml.s:288-300` |
| `syscall` | `_vectors+0x00`, via KCALL → VB+0 | `K/raml.s:287` |
| `faulthobbit` | `trap`, for ids 7/8/9 | `K/trap.c:96-115` |
| `notify`/`noted` | `trap` after a note is posted | `K/trap.c:291-390` |

---

## 2. Memory map as the kernel expects it

Sizes and bases are `K/mem.h` unless noted; addresses marked † are computed.

| Range | What | Cite |
|---|---|---|
| 0x00000000 | reset PC, and `PROMBASE`/`UZERO` | PRM p. 1-35; `K/mem.h:44,71` |
| 0x00000000–0x00000FFF | user page 0, never mapped (`UTZERO = UZERO+0x1000`) | `K/mem.h:72` |
| 0x00001000 | user text base (`UTZERO`); 32-byte `Exec` + text | `K/mem.h:72` |
| 0x00001020 | first user instruction after the `Exec` header (`initcode` is linked `-T0x1020`) | `K/mkfile:83`; `K/rammain.c:242` (`ur->pc = UTZERO+0x20`) |
| †0x7FC00000–0x7FFFFFFF | user stack, `USTKSIZE = 4 MB`, growing down from `USTKTOP` | `K/mem.h:73-74`; `K/rammain.c:255` |
| 0x80000000 | `RAMBASE` = `KTEXTBASE` = `KZERO`; boot page `ppage0` and hardware vector table | `K/mem.h:42,58,67`; `K/rammain.c:18`; `K/raml.s:54-57` |
| 0x80000000 | `VBADDR` (`KDATABASE+0`) | `K/mem.h:79` |
| 0x80001000 | `KSTBADDR`: kernel segment table, 1024 × 4 B | `K/mem.h:80`; `K/raml.s:22`; PRM p. 2-4 |
| 0x80002000 | `MACHADDR`: `Mach` struct (`stack[1]` last field) | `K/mem.h:81`; `K/dat.h:76-96` |
| †0x80002F00 | `MACHADDR+SPOFFSET` — SP field of the initial CRET frame | `K/mem.h:83`; `K/raml.s:44` |
| †0x80002FE0 | `MACHADDR+ISPOFFSET` — ISP as set at `raml.s:16` and reloaded at `:52`; `_startup`'s `ENTER R-16` puts the boot CRET frame 16 bytes below it (0x80002FD0) | `K/mem.h:82`; `K/raml.s:16,20,52` |
| 0x80004000 | `KTZERO`: first kernel text; `-T0x80004000` | `K/mem.h:60`; `K/mkfile:52` |
| 0x80004000–`edata` | text+data | `K/raml.s:91` |
| `edata`–`end` | BSS, zeroed by `_virtual` | `K/raml.s:91-97` |
| `PGROUND(end)`… | free physical pages handed to `palloc` (`conf.base0`, `conf.npage0`) | `K/rammain.c:160-166`; `P/alloc.c:105-121` |
| …0x80000000+`ppage0->memsize` | top of usable RAM | `K/rammain.c:142-149` |
| 0xA4400000 | SONIC register block, 1 page, mapped on demand | `K/io.h:208`; `K/devether.c:791-792` |
| 0xB0000000 | `IOBASE`; 4 pages (16 KB) mapped **user**-accessible (`/* IIC hack */`) | `K/mem.h:43`; `K/raml.s:38-39` |
| 0xB0000000 | Incon (`ctl`,`csr`,`data`) | `K/devincon.c:19,34-39` |
| 0xB0000080 | PCF8584 IIC (`data`,`ctl`) | `K/io.h:133-137` |
| 0xB0000100 | Quart DUART, 0x100-byte struct | `K/io.h:73-96` |
| 0xB0003000 | LCD (`ctl`,`data`) | `K/io.h:213-217`; `K/screen.c:120-137` |
| 0xB8000000 | `IOBASE+0x08000000` = NAK space; 4 pages, kernel only | `K/io.h:2`; `K/raml.s:41-42` |
| 0xB8000000 | `IOCTLADDR` (bit 0 `SCSIENABLE`, bit 2 `IOENABLE`) | `K/io.h:4-7` |
| 0xB8000080 | interrupt controller: mask0, mask1, status0, status1 | `K/io.h:12-18` |
| 0xB8000100 / 0xB8000104 / 0xB8000180 | SCSI address / data / DMA ports | `K/io.h:157-163` |
| 0xB8002000 | MK48T02 NVRAM, 2040 bytes at 4-byte stride | `K/io.h:111-116` |
| 0xB8003FE0 | RTC: control,sec,min,hour,wday,mday,mon,year (8 words, fills the page) | `K/io.h:118-128` |
| 0xC0000000 | `VROMBASE`; ROM build text base (`-T0xC0000000`) | `K/mem.h:45,49`; `K/mkfile:62` |
| 0xFFC00000 | `TSTKTOP`, end of the new stack in `sysexec` | `K/mem.h:68` |
| 0xFFFFE000 | `USERADDR`: the per-process `User` page (paged segment 0x3FF) | `K/mem.h:85`; `K/mmu.c:136` |
| †0xFFFFEFC0 | `UREGADDR` = `USERADDR+ISPOFFSET-0x20`: the user `Ureg` | `K/mem.h:86`; `K/rammain.c:239` |

Notes that follow from the numbers and matter to the model:

* The kernel image starts at 0x80004000, so the first 16 KB of RAM
  (0x80000000–0x80003FFF) is **not** kernel text: it holds `ppage0` (page 0),
  the kernel STB (page 1) and `Mach` (page 2).
* `KZERO == RAMBASE`, so for the RAM kernel `KADDR`/`PADDR` are identities
  (`K/mem.h:62-63`); only the ROM build offsets by 0x400000.
* Kernel text+data must fit in the first 4 MB: the only STE `raml.s` installs
  for RAM covers exactly 1024 pages (4 MB, `K/raml.s:33`, PRM Table 2-2). The
  rest of RAM is mapped later by `meminit()` from `ppage0->memsize`
  (`K/rammain.c:136-150`), in 4 MB segments.

---

## 3. Device inventory

Every device below is in every `cpu`/`term`/`bart` config unless the row says
otherwise. The device list is `K/cpu:1-22` (identical device lines in
`K/term:1-23`, `K/termlocal:1-23`, `K/bart:1-23`, `K/rom:1-22`).

### 3.1 Summary table

| Device | Register base(s) | Interrupt | Kernel files | Needs from the model |
|---|---|---|---|---|
| Serial console (Quart ch.0) | `EIAADDR` 0xB0000100 | IRQ 1 (`IRQQUART`) | `deveia.c`, `io.h`, `cpu:47-53` | DUART register file + TX; polled path is enough for the banner |
| Keyboard (serial, EIA port 2) | same Quart, channel 2 | IRQ 1 | `kbd.c`, `deveia.c`, `screen.c:178` | RX byte → `kbdq`, LED/parity/RTS bits obeyed |
| Mouse (serial, EIA port 3) | same Quart, channel 3 | IRQ 1 | `screen.c:179`, `devbit.c:2143`, `P/devcons.c:41` | RX 3-byte packets at 1200 baud |
| Screen / LCD | `LCDADDR` 0xB0003000 | none | `screen.c`, `devbit.c`, `screen.h` | write-only ctl/data framebuffer port |
| Incon (integrated concentrator) | 0xB0000000 | IRQ 5 (`IRQINCON`) | `devincon.c` | ctl/csr/data, "alive" bit, packet FIFO |
| IIC bus + EEPROM/LEDs | 0xB0000080 | none | `deviic.c` | PCF8584 state machine; supplies `eeprom.ea` and `eeprom.clock` |
| RTC + NVRAM | 0xB8003FE0, 0xB8002000 | none | `devrtc.c` | 8 BCD words + 2040-byte NVRAM |
| SCSI (WD33C93A) | 0xB8000100/104/180 | IRQ 10, IRQ 8 | `scsi.c`, `scsibuf.c`, `P/devscsi.c`, `P/devwren.c` | 32 indirect registers, DMA FIFO, bus reset latch |
| Ethernet (DP83932 SONIC) | 0xA4400000 | IRQ 9 (`IRQSONIC`) | `devether.c` | 0x100-byte register block + descriptor DMA |
| FPU | none (software) | vector 13 / slots 2,3 | `fpi.c`, `fpihobbit.c`, `fprt0.s` | unimplemented-instruction vectors; no FP hardware |
| Timers | DUART counter (ch.0 A) | IRQ 1, `CtAvail` | `deveia.c:527-543`, `clock.c` | 25 Hz counter/timer |
| Board IRQ controller | 0xB8000080 | CPU level 6 | `trap.c:120-172` | 16 source bits, mask/status |
| "boot" device (`#B/boot`) | — | — | `P/devboot.c` | only needed by the ROM monitor |

### 3.2 Serial console — `deveia.c` (Quart)

| Fact | Cite |
|---|---|
| `EIAADDR` = `IOACK(Quart,0x0100)` = 0xB0000100 | `K/io.h:96` |
| `Quart` = two `Duart` + bidding/interrupt/BRG registers; each field is a 32-bit word, so register *n* of the comment is at `+4n`; the struct is 0x100 bytes | `K/io.h:32-95` (field comments 0x00…0x2F) |
| Per-channel registers: `mr`, `sr`/`csr`, `cr`, `rxfifo`/`txfifo` (`K/io.h:32-43`) | — |
| Channel A extras: `ipcr`/`acr`, `isr`/`imr`, `ctu`, `ctl` (`K/io.h:45-57`) | — |
| Global: `opr`, `ipr`/`iopcra`, `start`/`iopcrb`, `stop`, `bcr[4]`, `pwrdn`, `pwrup`, `nak`, `ack`, `cir`, `gicr`, `gibcr`/`update`, `grxfifo`/`gtxfifo`, `icr`, `brg`, `setclk[2]` | `K/io.h:59-95` |
| Port map: 0 = `duart[0].a`, 1 = `duart[0].b`, 2 = `duart[1].a`, 3 = `duart[1].b` | `K/deveia.c:501-521` |
| `uartsetup` resets and programs 8N1, parity off, 19200 (`BD19200 = 0xBB`) | `K/deveia.c:401-422` |
| `uartputs` (the console writer) is **polled**: `cr = TxEnable`, spin on `sr & TxRDY`, write `txfifo` | `K/deveia.c:351-372` |
| `eiarawput` also waits for `TxEMT` | `K/deveia.c:600-615` |
| `eiaintr` reads `cir & TypeMask` and `gicr & 3` then services `TxAvail0/1`, `RxAvail`, `CtAvail`, `RxAvailErr`; `quart->update = 0` acknowledges | `K/deveia.c:424-479` |
| `uartenable` sets `oq->puts`/`iq->ptr`, enables TX/RX, ORs `TxRDYx`/`RxRDYx` into `imr` | `K/deveia.c:374-399` |
| `eiasetup` does `quart->ack = 0; quart->icr = 0`, `acr = BRGSet2`, and `setvector(&vector[0])` | `K/deveia.c:485-525` |
| Vector: `{IRQQUART, 0, eiaintr, "eia0"}` | `K/deveia.c:481-483` |
| `eiaspecial(portno,oq,iq,baud)` is how the console/keyboard/mouse bind queues | `K/deveia.c:545-563` |
| Board `IOENABLE` (bit 2) must be set before any I/O register answers; rammain does it explicitly | `K/rammain.c:103-107`; `K/io.h:5` |

**Minimum interface for A4 (banner):** decode 32-bit words in
0xB0000100-0xB00001FF; store writes to `cr/mr/csr/acr/opr/iopcr*/imr`;
return `sr` with `TxRDY` (0x04) and `TxEMT` (0x08) set; on a write to
`duart[0].a.txfifo` emit 8N1 on the console; return 0 for `cir` and
`status0/1` bit 1 (no interrupt needed, since the console writer polls).
`delay()` is driven by `eeprom.clock`, so an un-modelled EEPROM makes every
`delay()`/`mdelay()` a no-op (`K/clock.c:11-19; K/deviic.c:49`) — harmless for
the polled path, but it is why `eiasetup`'s reset delays disappear.

### 3.3 Keyboard — `kbd.c`

| Fact | Cite |
|---|---|
| A **serial** keyboard on EIA port 2 at 600 baud, odd parity | `K/kbd.c:274-283` |
| `eiaspecial(portno,&liteq,&kbdq,600)`; LED writes go out that port's `oq`; `eiasetrts(portno,0)` ("0 turns LED on"), `eiasetparity(portno,'o')`, `eiarawput(portno,Noclick)` | `K/kbd.c:278-282` |
| Raw scancode → ASCII via `keymap`/`skeymap` (128 entries, bit 7 = key-up, 0x80) | `K/kbd.c:99-135`, `:171-268` |
| `kbdq.putc = rawkbdputc` for the kernel console; `kbdcr2nl` when used as the `kbdq` of a stream port | `K/kbd.c:281`; `K/deveia.c:561-562` |
| Chars enter the kernel via `kbdputc` (`P/devcons.c:270-292`) which also echoes to the screen | `P/devcons.c:282` |
| On `CONF=cpu`/`rom` no keyboard is initialised (`screeninit` is a stub); only the UART's own input queue exists | `K/cpu:47-53`, `K/rom:49-59` |

**Minimum interface:** one DUART receive channel (port 2) that delivers a byte
per character, plus honouring `imr`/`cir` `RxAvail` if interrupts are used.
Boot to the first prompt does not need the keyboard.

### 3.4 Screen — `screen.c`, `devbit.c`, `devincon.c`

| Fact | Cite |
|---|---|
| `LCDADDR = IOACK(Lcdisp,0x3000)` = 0xB0003000, fields `ctl`, `data` | `K/io.h:213-217` |
| `screenupdate` writes `ctl` twice (`y>>8`, `(y>>2)&0x3f`) then one 32-bit `data` word per 4 pixels, low byte first | `K/screen.c:118-139` |
| Geometry 768 × 1024, `LCDLD = 1` → 2 bits/pixel, framebuffer is `LCDWORDS` words of kernel memory | `K/screen.c:16-30`, `:186-190` |
| `screenputs` draws text into `gscreen` then `screenupdate` pushes the dirty rectangle | `K/screen.c:235-286` |
| `screeninit` allocates the framebuffer, swizzles the font, and calls `kbdinit(2)` + `eiaspecial(3,0,&mouseq,1200)` | `K/screen.c:168-218` |
| `conf.monitor = 1` marks "has a display" | `K/screen.c:180`; `K/dat.h:15` |
| `#b/bitblt` (`devattach('b')`) exposes screen/mouse/fonts to `libg` | `P/devbit.c:345`, `:169-176` |
| `devincon.c` is **not** the screen: it is the Incon network concentrator (§3.5) | `K/devincon.c:1-19` |

**Minimum interface:** a write-only port where `ctl` selects a scanline/column
and each `data` write stores 4 pixels. No reads, no interrupt. Only `term`,
`termlocal` and `bart` build the screen (`bit b bbmalloc screen kbd`,
`K/term:22`, `K/termlocal:22`, `K/bart:22`); `9cpu` never touches `LCDADDR`.

### 3.5 Incon — `devincon.c`

| Fact | Cite |
|---|---|
| `INCONADDR = IOACK(Device,0x0000)` = 0xB0000000; `Device{ctl,csr,pad[2],data}` → ctl 0x0, csr 0x4, data 0x10 | `K/devincon.c:19,34-39` (the `io.h` version is `#ifdef notdef`, `K/io.h:98-106`) |
| `IRQINCON = 5` | `K/io.h:21` |
| Vector `{IRQINCON,0,inconintr,"incon0"}` installed by `inconreset` | `K/devincon.c:304-308`, `:347` |
| `inconreset` stops the chip and records station-number range from `station` | `K/devincon.c:310-348` |
| `inconpoll` selects a station by writing internal registers through `csr`, then waits ≤250 ms for `csr & 0x80` ("alive") | `K/devincon.c:201-264` |
| Stream I/O: `inconoput`/`inconstopen`/`inconkproc`, `Qinfo inconinfo` | `K/devincon.c:113-128` |
| All `cpu`/`term` configs list it and the boot method `incon "config 1 64 restart dk"` | `K/cpu:13,76`, `K/term:13,50` |

**Minimum interface:** ctl/csr/data with an "alive" bit and a byte FIFO. It is
the *default boot device*; a boot that only needs the console can leave it
"not alive" (`inconrestart` prints `incon[0] not polled` and returns).

### 3.6 IIC bus — `deviic.c` (PCF8584 + PCF8582 EEPROM + PCF8574 LEDs)

| Fact | Cite |
|---|---|
| `IICADDR = IOACK(Iic,0x0080)` = 0xB0000080; `Iic{data,ctl}` → data 0x80, ctl 0x84 | `K/io.h:133-137` |
| Master-only, **no interrupts** (file comment) | `K/deviic.c:1-7` |
| `iicreset`: first write must be the own address (`PCF8584=0x10`), then `ClockReg`, `Ecl8MHz\|Scl100KHz`, then `Eso`; if `Busfree` read the EEPROM | `K/deviic.c:193-229` |
| Status bits: `Busfree 0x01`, `Nak 0x08`, `Buserr 0x10`, `Pin 0x80`; control bits `Ack 0x01`, `Sto 0x02`, `Sta 0x04`, `Esi 0x08`, `OwnAddrReg 0x00`, `IntrVecReg 0x10`, `ClockReg 0x20`, `Eso 0x40` | `K/deviic.c:16-40` |
| `eepromread` reads `sizeof(Eeprom)` bytes from slave `0xA4` into the global `eeprom` | `K/deviic.c:124-191` |
| `Eeprom` = `magic[5] "A600D92010"`, `ea[6]`, `mask`, `clock`, `dsp`, `pcb`, `rev` | `K/io.h:143-152` |
| Comment: this must run **before** Ethernet reset, because `etherreset` copies `eeprom.ea` | `K/deviic.c:216-219`; `K/devether.c:790` |
| `eeprom.clock` is the `delay()` timebase | `K/clock.c:16`; `K/scsi.c:165-167` |
| LED path writes one byte to slave `0x40` | `K/deviic.c:231-248` |

**Minimum interface:** a PCF8584 model that can answer the sequence
`data=own-address, ctl=ClockReg, data=clock, ctl=Eso` and then a byte-wise
EEPROM read, **or** an honest failure (`iic->ctl` without `Busfree`) which
leaves `ctlr.iic = 0` and makes `#2` unattachable (`K/deviic.c:256-261`). What
the model must *not* do is return garbage `ea`/`clock`: `clock` scales every
delay loop, and `ea` becomes the SONIC MAC address.

### 3.7 RTC and NVRAM — `devrtc.c`

| Fact | Cite |
|---|---|
| `RTCADDR = IONAK(RTCdev,0x3FE0)` = 0xB8003FE0; words `control,sec,min,hour,wday,mday,mon,year` (8 × 4 B = fills the last page) | `K/io.h:118-128` |
| `RTCREAD 0x40`, `RTCWRITE 0x80` in `control` | `K/devrtc.c:9-10` |
| `rtctime` reads BCD, masks `sec 0x7F`, `min 0x7F`, `hour 0x3F`, `mday/mon 0x3F`, and maps `year<70 → 2000+` | `K/devrtc.c:166-192` |
| `setrtc` writes BCD | `K/devrtc.c:151-164` |
| `NVRAMADDR = IONAK(Nvram,0x2000)`, `Nvram{val,pad[3]}`, `NVRAMLEN 2040` | `K/io.h:111-116` |
| `#r/rtc` returns seconds since 1970 as a decimal string; `#r/nvram` is byte-addressed over the 4-byte-strided array | `K/devrtc.c:259-296` |
| The kernel's boot environment comes from NVRAM (the ROM monitor reads it) | `B/romboot.c:84-103` |
| No interrupt, no reset/init work (`rtcreset`/`rtcinit` empty) | `K/devrtc.c:194-202` |

**Minimum interface:** 8 BCD words with the `control` read/write latch, and a
2040-byte NVRAM array. `date` (Goal B) is the gate.

### 3.8 SCSI — `scsi.c`, `scsibuf.c` (WD33C93A)

| Fact | Cite |
|---|---|
| `SCSIADDR = IONAK(ulong,0x0100)` = 0xB8000100 (register *index* port), `SCSIDATA = 0xB8000104` (data port), `SCSIPDMA = 0xB8000180` (DMA FIFO) | `K/io.h:157-163` |
| Register numbers 0x00…0x1F: `Rownid 0x00`, `Rcontrol 0x01`, `Rtimeout 0x02`, `Rcdb 0x03`, `Rlun 0x0F`, `Rcmdphase 0x10`, `Rsync 0x11`, `Rtchi/mi/lo 0x12-14`, `Rdestid 0x15`, `Rsrcid 0x16`, `Rstatus 0x17`, `Rcmd 0x18`, `Rdata 0x19`, `Raux 0x1F` | `K/scsi.c:35-52` |
| Access protocol: write the index to `*addr`, then read/write `*data`; `*addr` read returns the auxiliary status | `K/scsi.c:173-229`, `:682-720` |
| `Raux` bits: `Dbr 0x01`, `Cip 0x10`, `Bsy 0x20`, `Lci 0x40`, `Intrpend 0x80` | `K/scsi.c:77-83` |
| Commands used: `Creset 0x00`, `CselectATN 0x06`, `CtransferATN 0x08`, …; single-byte transfer `Csbt 0x80` | `K/scsi.c:85-95` |
| `resetscsi`: installs `IRQSCSI(10)` and `IRQSCSIDMA(8)`, then toggles the **board** SCSI reset via `*IOCTLADDR &= ~SCSIENABLE; delay; |= SCSIENABLE` | `K/scsi.c:926-956`; `K/io.h:4,7` |
| `ctlrreset`: writes `Rownid = Fs16MHz\|Eaf\|CtlrID(7)`, issues `Creset`, waits for `Intrpend`, sets `Rcontrol = BurstDma\|Edi\|Idi\|Hsp`, `Rtimeout = 200*16/80`, `Rsrcid = Er` | `K/scsi.c:829-920` |
| `scsidmaintr` pumps `*SCSIPDMA` while `IRQADDR->status1 & 0x01` | `K/scsi.c:806-827` |
| `#S` device (`devscsi.c`) + `#w` (`devwren.c`, partitions on Wren drives) sit on this adapter | `K/cpu:15-16`; `P/devwren.c:1-30` |
| `scsibuf` only allocates physically contiguous buffers (`PADDR` of a `smalloc` block) and remembers `virt/phys` | `K/scsibuf.c:10-25`; `P/portdat.h:244-249` |
| No DMA engine is implemented in the driver beyond the FIFO loop ("dma" is a TODO in the file header) | `K/scsi.c:1-11` |

**Minimum interface:** the 32-register indirect file, `Intrpend`/`Bsy`/`Cip`,
and a target that answers INQUIRY/READ CAPACITY/READ. `resetscsi` must not hang:
`ctlrreset` spins on `*ctlr->addr & Intrpend` (`K/scsi.c:875-876`), so a model
that never raises `Intrpend` wedges the boot at `chandevreset`.

### 3.9 Ethernet — `devether.c` (DP83932 SONIC)

| Fact | Cite |
|---|---|
| `SONICADDR = (Sonic*)0xA4400000` — a raw pointer, **not** in the IOBASE windows | `K/io.h:208` |
| `etherreset` maps it with `mmuiomap((ulong)SONICADDR,1)` — one STB segment entry, 1 page | `K/devether.c:791-792` |
| `Sonic` struct: `cr,dcr,rcr,tcr,imr,isr,utda,ctda,urda,crda,eobc,urra,rsa,rea,rrp,rwp,cep,cap2/1/0,ce,cdp,cdc,sr,wt0,wt1,rsc,crct,faet,mpt,mdt,dcr2` — 32-bit words, 0x100 bytes | `K/io.h:170-207` |
| Reset: `cr = Rst(0x0080); dcr = Sterm\|Dw32; cr = 0` | `K/devether.c:646-654` |
| Receive resource/descriptor areas (`rra[16+2]`, `rda`, `tda`, `cda`) are kernel **physical** addresses programmed as LS16/MS16 pairs | `K/devether.c:679-758` |
| `cr = Rrra` then `while(cr & Rrra)`, and `cr = Lcam` then `while(cr & Lcam)` — the model must clear those bits | `K/devether.c:701-702`, `:751-752` |
| Enable receive only in `etherup`: `cr = Rxen` | `K/devether.c:769-772` |
| Vector `{IRQSONIC,0,etherintr,"ether0"}`, `IRQSONIC = 9` (status1 bit 1) | `K/devether.c:636-638`; `K/io.h:23` |
| Station address copied from `eeprom.ea` | `K/devether.c:790` |
| `isr` bits handled: `Txdn/Txer` (0x0100/0x0200), `Pktrx/Rde`, `Lcd`, `Hbl`, `Br` | `K/devether.c:567-633` |

**Minimum interface:** registers behave as RAM with `cr` reads returning 0 for
`Rrra`/`Lcam` so the init loops exit, `isr` = 0, and the descriptor memory
left alone. That is enough for boot; Goal B needs descriptor DMA (the buffer
addresses are physical kernel addresses, so the model's bus master must
translate nothing but must write into main memory).

### 3.10 FPU — `fpi.c`, `fpihobbit.c`, `fprt0.s`

| Fact | Cite |
|---|---|
| There is **no FPU**: "floating point status word register (unimplemented)" | `K/machine.h:38-40` |
| FP is a software interpreter linked into the kernel (`OBJ` includes `fprt0.z fpihobbit.z fpi.z`) | `K/mkfile:42-44` |
| `fprt0` is the entry: saves PSW/R32/MSP, `MOVA R32,R16`, `CALL fpi`, then synthesises PSW.C/V/F by executing `ADD3`, `TESTC`, `DIV3 $0xFFFFFFFF,$0x80000000`, `TESTV` | `K/fprt0.s:3-44` |
| `fpi(void*)` decodes a run of unimplemented parcels from `pc`, using `getparcel`, addressing modes (`absolute/stack/indirect/immediate`) and opcodes 17, 25, 26, 40-43, 56-59 | `K/fpihobbit.c:13-85`, `:355-475` |
| Operand kinds are selected from the parcel's mode nibbles: single/double/int, get/put | `K/fpihobbit.c:220-297` |
| Software arithmetic: `fpiround`, `fpiadd/sub/mul/div`, `fpicmp` over a 28-bit-fraction `Internal` | `K/fpi.c:1-293`; `K/fpi.h:26-47` |
| `fprt0` is installed in the *boot page* at 0x74 by the ROM and copied into hardware vector slots 2 and 3 by `raml.s` | `K/roml.s:29,85-87`; `K/raml.s:85-86` |
| A separate `fpi.out` link at `-T0xE0000020` and `fpi.root.c` exist as rules, but nothing in this `mkfile` depends on them | `K/mkfile:91-102` (O6) |

**Minimum interface:** no FP hardware; the model must (a) implement the
unimplemented-instruction and trapped-niladic sequences to `VB+12`/`VB+8`
(PRM p. 1-39/1-40), and (b) support the integer primitives `fprt0` uses
(`MOVA`, `ADD3` destination form, `DIV3`, `TESTC`, `TESTV`, `KRET`) before
Goal B's FP gate can pass.

### 3.11 Timers

| Fact | Cite |
|---|---|
| `HZ = 25`, `MS2HZ = 40`, `TK2MS(t) = t*40` | `K/mem.h:21-25` |
| The system clock is the **DUART channel A counter/timer**: `acr = BRGSet2\|TimerD16`, `ctu/ctl = Crystal/(2*16*HZ)` with `Crystal = 3686400` → 4608 = 0x1200, `imr |= CtrRDY`, `start` | `K/deveia.c:527-543`, `:63-81` |
| `CtAvail` in `eiaintr` reads `duart->stop` and calls `clockintr(ctlrno,ur)` | `K/deveia.c:464-467` |
| `clockintr` bumps `m->ticks`, accounts time, `checkalarms()`, `eiaclock()`, `kproftimer()`, and can `sched()` | `K/clock.c:21-54` |
| The CPU's own `TIMER1`/`TIMER2` registers exist and are readable (`gettimer1` reads and clears TIMER1; `getcpureg` reads TIMER1/2) | `K/machine.h:17-18`; `K/raml.s:156-159`, `:322-396` |
| `CONFIG` timer bits `T1CI/T1X/T1IE/T2CI/T2OFF/T2X/T2IE` are defined | `K/machine.h:30-36` |
| Nothing in the port programs `T1IE/T2IE`; the DUART counter is the only tick source | grep of `K/` + `P/` finds TIMER1/2 only in `raml.s`/`roml.s` |
| Timer vector slots exist at VB+0x2C/+0x30 but `_vectors[11]/[12]` are `$trap` | `K/raml.s:79-82`, `:298-299` (O5) |

**Minimum interface:** a DUART counter that, after `ctu/ctl` are written,
raises `CtAvail` in `cir`/`isr` at 25 Hz. That is the whole kernel clock.

### 3.12 Board interrupt controller

| Fact | Cite |
|---|---|
| `IRQADDR = IONAK(Irq,0x0080)` = 0xB8000080: `mask0, mask1, status0, status1` | `K/io.h:12-18` |
| Source numbers: `IRQQUART 1`, `IRQINCON 5`, `IRQSCSIDMA 8`, `IRQSONIC 9`, `IRQSCSI 10`, `NIRQ 16`; the comments give the status bit (0x0002, 0x0020, 0x0100, 0x0200, 0x0400) | `K/io.h:20-25` |
| `setvector` writes the masks; `interrupt` reads the two status bytes | `K/trap.c:120-138` |
| All board interrupts arrive on **CPU level 6** → `VB+0x28` → `_vectorA` → `_vectors[0x0A] = interrupt` | `K/raml.s:67-71`, `:297`; PRM Table 1-25 p. 1-36 |
| `spllo()` sets `PSW_IPL = 7` (allow 0-6); `splhi()` clears it (only NMI) | `K/raml.s:102-110`; PRM p. 1-36 |
| An enabled-but-unhandled bit panics: `interrupt: #....` | `K/trap.c:170-171` |

**Minimum interface:** 16 sticky source bits in `status0/1`, ANDed with
`mask0/1` for the CPU line, cleared by the device handler. Level must be
**IL=6** so that `PSW.IPL` gating matches PRM p. 1-36.

---

## 4. Build requirements for A3

### 4.1 Toolchain and variables

`K/mkfile` is a Plan 9 `mk` file driven by `/$objtype/mkfile` with

| Variable | Value | Cite |
|---|---|---|
| `$objtype` | `hobbit` | `K/mkfile:5` |
| `$CC`/`$LD`/`$AS`/`$RL`/`$O` | `zc`/`zl`/`za`/`rl`/`z` | `hobbit/mkfile:1-6` (the release's `/hobbit/mkfile`) |
| `CONF` | `cpu` (default) | `K/mkfile:1` |
| `CONFLIST` | `cpu term termlocal bart rom` | `K/mkfile:2` |
| `TYPE` | `ram` (for **all** configs, including `rom`) | `K/mkfile:3` |
| `CFLAGS` | `-w -Dram` | `K/mkfile:7` |
| `LIBRARY` | `libram.a` | `K/mkfile:8` |

### 4.2 What is compiled (resolved for `CONF=cpu`)

`OBJ` (`K/mkfile:14-44`) plus the generated lists:

* port/hobbit objects: `trap, alarm, alloc, chan, clock, dev, fault, latin1,
  taslock, segment, swap, rammain, mmu, net, page, pgrp, print, proc, qlock,
  queue, sysfile, sysproc, stream, fcall, fprt0, fpihobbit, fpi` — the names
  not present in `K/` are taken from `P/` by `P/portmkfile:1-4`; the ones in
  `K/` win (`P/portmkfile:9-10`).
* `$DEV` = `{rc ../port/mkdevlist $CONF}` (`K/mkfile:10`) → `P/mkdevlist:8-17`
  emits, in file order: `devroot devcons devenv devpipe devproc devsrv devmnt
  devdup deviic deveia devrtc devincon devdk devscsi scsi scsibuf devwren
  devether devarp deviproute devip tcpinput tcpoutput tcptimer tcpif stil
  devkprof` (all `.z`) — from `K/cpu:1-22`.
* `$STREAM` → `sturp stip stasync stfcall streboot` (`K/mkfile:11`,
  `P/mkstreamlist:8-17`, `K/cpu:24-30`).
* `$MISC` empty for `cpu`/`term`/`bart`/`rom`; `kfs.root` for `cpulocal` and
  `termlocal` (`K/cpulocal:33`, `K/termlocal:32`).
* `cpu.c` is **generated** by `P/mkdevc` from the config file: it emits
  `devtab[]`, `devchar`, `streaminit()`, the whole `port` section verbatim,
  `conffile` and `kerndate` (`K/mkfile:48-51`; `P/mkdevc:8-58`;
  `P/portmkfile:34-35`).
* `devtab.h` from `P/mkdevh` over the *whole* `CONFLIST` (`P/portmkfile:37-38`).
* `systab.h` from `P/mksystab` over `sys.h` (`P/portmkfile:31-32`).
* `init.h`: `initcode` is assembled and linked `-l -s -o init.out -H2
  -T0x1020 -R4`, then `xd -r -1x` into a C array (`K/mkfile:81-87`).
  `initcode` is the first user program: `KCALL $EXEC` with `R4="/boot"`,
  `R8=argv` (`K/initcode:1-14`; `EXEC=7`, `SYSR1=0` in
  `sys/src/libc/9syscall/sys.h:1,8`).
* `bootcpu.root.c`: `B/mkboot cpu` generates the boot program's `Method[]`
  table and `main()` (`P/portmkfile:75-79`); it is linked as a **user**
  executable against `libboot.a` + `-lauth`, then embedded as a byte array by
  `P/mkroot`.

Read this list as the A3 checklist: 27 local/port objects + 27 device objects
+ 5 stream objects, one generated `cpu.c`, one generated `bootcpu.root.c`.

### 4.3 Link step and what the image must contain

`K/mkfile:50-53`:

```
9cpu: raml.$O boot$CONF.root.$O $LIBRARY $CONF.c
        $CC $CFLAGS '-DKERNDATE='`{date -n} $CONF.c
        $LD -o $target -l -R4 -H1 -T0x80004000 -E0x80004000 \
                raml.$O $CONF.$O boot$CONF.root.$O $LIBRARY -lc
        size 9$CONF
```

So a 1e Hobbit kernel image (`9cpu`) must be:

| Requirement | Value | Cite |
|---|---|---|
| Format | **`-H1` = "boot image"**: 80-byte header, magic `0x01610000`, text at file offset 80, type `FHOBBITB` | `K/mkfile:52`; `sys/src/cmd/zl/obj.c:100-109` (`HEADR = 20+60`, `INITRND` default 4); `sys/src/libmach/executable.c:72-78` and `hobbitboot` (`txtoff = sizeof(struct mipsexec)+4`) |
| Text base / **entry** | 0x80004000 for both | `-T0x80004000 -E0x80004000`, `K/mkfile:52` |
| First text symbol | `_startup`, from `raml.z`, the first object | `K/raml.s:12`; link order in `K/mkfile:52` |
| `-R4` means | `INITRND`, the data-start rounding — **not** an alignment of the image | `sys/src/cmd/zl/obj.c:58-62`, `:106-109` |
| Data | `INITDAT` defaults to 0, and an explicit `-D` is **ignored whenever `INITRND != 0`** (`zl` prints `warning: -D… is ignored because of -R…`), so data follows text, 4-byte rounded; `datsz`+`bsssz` go in the header | `sys/src/cmd/zl/obj.c:100-109`, `:123-125`; `B/romboot.c:524-527` |
| Header vs `tools/p9exec.py` | The kernel image is **not** the 32-byte `Exec` that `p9exec.py` parses (it wants `Z_MAGIC 0x197`). `-H2` produces that `Exec`, and is what `initcode` and the embedded boot program use (`zl`'s default header is `-H2`) | `tools/p9exec.py:17-19,41-47`; `K/mkfile:83`; `P/portmkfile:75-79`; `sys/src/cmd/zl/obj.c:4-5,71-80` |
| BSS | not in the file; zeroed by `_virtual` from `edata` to `end` | `K/raml.s:91-97` |
| Symbols the kernel requires | `edata`, `end` (BSS bounds), `main` | `K/raml.s:91-99` |
| Libraries | `libram.a`, then `-lc` | `K/mkfile:52` |
| Load rule | text→`txtaddr`, data→`dataddr`, zero `bsssz`, set `ppage0->argc/argv`, start at `entry` with PSW=0 | `B/romboot.c:521-553`; `K/roml.s:173-186` |
| Reproducibility | `kerndate` = `date -n` at compile time — pass a fixed value for a reproducible image | `K/mkfile:51`; `P/mkdevc:58` |

The ROM variant (`9rom`, `K/mkfile:60-63`) is a different beast: linked
`-H1 -T0xC0000000 -D0xC0604000 -E0x0`, uses `roml.z` (its own `_startup`
begins `JMP *$(PROMBASE+6)`, `K/roml.s:12-13`) and is flattened by `mkrom`,
which copies `txtsz` bytes from the header's `txtoff` plus `datsz` from
`datoff` and **swaps the two 16-bit halves of every 32-bit word**
(`K/mkrom.c:79-94`) — the same big-endian-parcel order that `tools/p9exec.py`
documents for the model image (`tools/p9exec.py:36-38`). Its `FHOBBIT` case
that re-bases text to offset 32 (`K/mkrom.c:81-90`) applies to a 32-byte
`Exec`, not to the `FHOBBITB` header this link produces
(`sys/src/libmach/executable.c:72-78`). `9rom` is the monitor
(`boot romboot`, `K/rom:73`) that loads `9cpu`; it is **not** needed to boot
`9cpu` on the model (§1.2), and its own copy path has the problems in O7.

### 4.4 What `rom`, `term`, `termlocal`, `bart`, `cpu` are

| Config | Kernel | cpuserver | Display | Boot methods | Notes |
|---|---|---|---|---|---|
| `cpu` | RAM `9cpu` | 1 | no (`screeninit` stub sets `printq` on EIA0) | `il`, `tcp`, `incon` | diskless CPU server; **this is the A4 target** (`K/cpu:34-35,47-53,73-78`) |
| `term` | RAM `9term` | 0 | yes (`screen.c`) + `kbd` | `il`, `tcp`, `incon` | terminal, `bit b bbmalloc screen kbd` (`K/term:22,33-45,47-52`) |
| `termlocal` | RAM `9termlocal` | 0 | yes, no `kbd` in `bit` | + `local` | `misc kfs.root` embeds a local kfs (`K/termlocal:22,31-32,47-53`) |
| `bart` | RAM `9bart` | 1 | yes (`bit` = bbmalloc screen), `islcd = 1` | `il`, `tcp`, `incon` | LCD CPU server (`K/bart:22,34-45,47-52`) |
| `rom` | ROM `9rom` | 1 | no | `romboot` | the monitor that loads `9cpu`; `boot B` device (`K/rom:22,32-73`) |

`cpuserver` is a generated global in the config's `port` section
(`P/mkdevc:55` inserts it into `cpu.c`), and `mkboot` reads the `boot` section
to pick the password prompt: `pword = key` when `boot cpu`, else
`userpasswd` (`B/mkboot:65-77`).

### 4.5 Device probe order (this is a hard ordering constraint)

`chandevreset()` calls `(*devtab[i].reset)()` for every entry in **devchar
order**, which is the order of the `dev` lines (`P/chan.c:40-47`;
`P/mkdevc:18-44`). For `cpu` that is:

```
root cons env pipe proc srv mnt dup iic eia rtc incon dk scsi wren ether arp
iproute ip kprof
```

Consequences that are stated in the sources:

* `iic` (index 8) runs **before** `ether` (index 15): `iicreset` reads the
  EEPROM and comments "Must ensure that this code runs before ether reset"
  (`K/deviic.c:216-219`), and `etherreset` copies `eeprom.ea`
  (`K/devether.c:790`).
* `eiareset` creates the four ports and enables them (`K/deveia.c:772-803`);
  `deveia` is index 9.
* `inconreset` installs IRQ5 and stops the chip (`K/devincon.c:310-348`).
* `devscsi`'s reset is `resetscsi` (`K/scsi.c:931`), which toggles the bus
  reset latch and then spins on `Intrpend`.
* `devether`'s reset maps the SONIC and spins on `cr & Rrra`/`cr & Lcam`.
* `clockinit()` is **not** in this list; it is called directly at
  `K/rammain.c:116` before `chandevreset()`.
* The loop condition is literally `i < devchar[i]` (`P/chan.c:45`) — an idiom
  that works because `devchar` is `"/ce|psMd2trikSwlaPIT"` and is
  NUL-terminated (`P/mkdevc:38-44`).

### 4.6 Reproducing the link on this host

The pieces exist: `tools/plan9-1e/sys/src/cmd/{za,zc,zl}` (vendored) and the
shipped `hobbit/bin/{za,zc,zl}`. A3's link command is exactly `K/mkfile:52`
with `$O=z` and the object order above. `zl`'s entire option set is parsed in
`sys/src/cmd/zl/obj.c:29-63`: `-o`, `-E`, `-H`, `-T`, `-D`, `-R`, and every
other letter is a debug flag (so `-l` only sets `debug['l']`, which suppresses
the `_main` cross-reference at `obj.c:159-165`; it is not a linker mode). The
kernel object must be produced by **`za`/`zl` running on the model** (A2) or by
the shipped binaries.

Not in the release and therefore required from A0/A2/A3 work: `mkextract`,
`mkdevc`, `mkdevh`, `mklist` family, `mkroot`, `mkboot`, `mkrom` and `size`
are Plan 9 `rc`/`awk` scripts and C programs. `P/mkdevc`, `P/mkdevlist`,
`P/mkstreamlist`, `P/mkmisclist`, `P/mkdevh`, `P/mkextract`, `P/mkroot`,
`B/mkboot` are plain `rc`+`awk` and can be re-implemented on the host;
`mkrom.c` (a C program, `K/mkrom.c`) needs `crackhdr` from `libmach` (vendored
at `tools/plan9-1e/sys/src/libmach`). Running the generated `cpu.c` through
`zc` is the part that needs the toolchain, not the model.

---

## 5. Open questions (do not fill these in; each is an experiment)

**O1 — `ENTER R-16` with `MSP` undefined.** `raml.s:20` executes `ENTER R-16`
after setting `ISP` but before any `MSP` value exists. The new CSP value is
determined (`PSW=0` makes the CSP the ISP, PRM p. 1-35; `ENTER` with a stack
offset moves it by the offset, PRM pp. 3-19…3-21, which gives the frame
address 0x80002FD0 and is confirmed by `_virtual`'s `ISP` reload at `:52`).
What is *not* determined is the stack-cache side: the PRM warns that `SP` and
`MSP` are undefined at external reset and that the caches should not be
enabled (they are, at `:14`) until both are assigned, "since the range check
circuitry would not know whether an address should access the on-chip stack
cache or off-chip memory" (PRM p. 1-35 Note). So the *architectural* address is
0x80002FD0; whether the four frame words are written to the cache or to memory
is the implementation's choice. A4 must record which one and keep it, because
`CRET` reads the frame from `ISP+0` (`K/raml.s:49`).

**O2 — the FP vector slot is at 0x74 or 0x84?** `K/raml.s:85-86` and
`K/roml.s:29` use boot-page offset **0x74**; `I/rom.h:36-39` declares
`spare0x0070[4]; ulong memsize; void (*fpi)`, which puts `fpi` at **0x84**.
One of the two is wrong. The kernel reads 0x74, so 0x74 is what A4 must
populate; the header comment is stale. (This is a source conflict, not a
guess: both lines are quoted.)

**O3 — what are page-table bits 10:4?** `mmu.c` preserves `(0x7F<<4)` on every
PTE store (`K/mmu.c:198`) and seeds `ptb[0] = 0x7F<<4` (`:80`) as a first/last
page hint. The PRM calls 10:5 reserved and 4 the modified bit (Table 2-3
p. 2-7). The intent of the hint is not printed.

**O4 — the event frame vs `Ureg` (blocks A4's exception/syscall path).**
Required by `trap.c`/`raml.s`: `Ureg.cause` +0 (written by the stub's `R0`,
`raml.s:231`), `Ureg.fault` +12 (`raml.s:238`), `Ureg.sp` +16 (`:234`),
`Ureg.msp` +20 (`:244`), `Ureg.id` +8 (read at `trap.c:200`, `syscall`,
`trap.c:406`), `Ureg.pc` +24 (`trap.c:402`), `Ureg.psw` +28 (`trap.c:194`,
`raml.s:237`) — i.e. an 8-word frame. Printed by the PRM: three words at
`ISP-12` (id / KCALL src), `ISP-8` (PC), `ISP-4` (PSW), then `ISP -= 16`
(pp. 1-37, 1-38, 3-29), i.e. a 4-word frame with id/PC/PSW at +4/+8/+12; the
repo's model implements exactly that (`bsv/HobbitEvents.bsv:374-386`). The two
cannot both hold for one `ISP`: with a 16-byte frame the kernel's `ur->id` at
+8 reads the saved PC, and `ur->pc` at +24 reads above the frame. A4 must
settle it with one KCALL of a known `src` and a dump of the eight words at
`ISP` (the frame is only 4 words, so the test is cheap), then either fix the
model or adjust the kernel's `Ureg`. Until then, the syscall and exception
paths of A4/A5 are not trustworthy, and A0's `FAULT pc=000012c2` is a
*user-mode exception* whose handler depends on the same layout.

The same test should print `ISP` across the handler: `raml.s:257-258` uses
`ADD $16,%ISP` **and** `ADD3 $4,%ISP`, and `ADD3` writes the accumulator, not
its named destination (PRM p. 3-5; the model agrees, `bsv/HobbitCore.bsv:486`
writes only `spBefore+4`), so the second instruction cannot be what advances
`ISP` by 4. Either the sequence is a leftover or `ISP` is meant to end up 16,
not 20, bytes further on; that difference decides where `CATCH *R4` and any
subsequent `KRET` land.

**O5 — which vector do the CPU timers take?** `raml.s` installs `_vectorB`/
`_vectorC` at VB+0x2C/+0x30 for TIMER1/TIMER2 (`:79-82`) and maps them to
`$trap` (`:298-299`), but PRM Table 1-14 (p. 1-20) and the interrupt sequence
(PRM p. 1-37) only define VB+0x10…+0x40 (NMI + levels 1-6), and the timers
"are asserted at level 1" (PRM p. 1-36). Either the 92010 has extra timer
vectors the table omits, or a timer interrupt actually lands on level 1 and
panics. Nothing in the port programs `T1IE`/`T2IE`, so boot does not depend on
it, but Goal B's timer gate does.

**O6 — dead FP build rules.** `K/mkfile:91-102` builds `fpi.out` at
`-T0xE0000020` and `fpi.root.c`, but no target in this `mkfile` (or in
`P/portmkfile`) depends on `fpi.root.c`. The interpreter that the kernel
actually links is the one in `OBJ` (`K/mkfile:42-44`). Treat the `fpi.root.c`
rules as leftovers; if a later kernel revision loads the interpreter into user
space at 0xE0000020, that is not in this tree.

**O7 — the ROM build cannot place its data where `roml.s` copies it.**
Three sourced facts, which conflict:

1. `9rom` is linked `-T0xC0000000 -D0xC0604000` (`K/mkfile:62`).
2. `zl -H1` sets `INITRND = 4` by default (`sys/src/cmd/zl/obj.c:106-109`) and
   therefore **ignores `-D`**, printing `warning: -D0x… is ignored because of
   -R0x…` (`obj.c:123-125`). Data follows text, 4-byte rounded.
3. `roml.s` maps only 64 pages (256 KB) at segment 0x300 for the ROM
   (`K/roml.s:45-46`) and then copies "ROM → RAM" to
   `KDATABASE+0x4000 = 0xC0604000` until `R4 == edata`
   (`K/roml.s:67-75`; `K/mem.h:50`), i.e. into segment 0x301, which nothing
   maps.

So either the copy loop copies nothing (if the link-time `edata` is below
0xC0604000, the `CMPHI R4,$edata` / `JMPT _vbinit` at `K/roml.s:69-71` exits
immediately) or it faults on an unmapped segment before any vector table is
installed. The experiment that settles it is one `zl` link of `9rom` plus a
symbol dump of `edata`; it is **not** on the A4 path, because the model can
load `9cpu` directly from its Fhdr (§1.2).

**O8 — `eeprom.clock` and `eeprom.ea` are uninitialised without an IIC
model.** `delay()` multiplies by `ROUNDUP(eeprom.clock,2)/2`
(`K/clock.c:16`), so `clock = 0` makes all delays no-ops, and `ea` becomes the
SONIC station address (`K/devether.c:790`). The sources do not say what the
real EEPROM contents are (only the magic and field layout, `K/io.h:143-152`).

**O9 — the DUART/Quart byte map.** `io.h` gives each register as a 32-bit
field of a C struct plus a *register number* in the comment (`0x00`…`0x2F`).
That fixes the addressing convention (register *n* at `EIAADDR+4n`, struct
0x100 bytes), but the chip's actual bit semantics come from the Signetics
68C94 datasheet, which is not in the release. The driver's own bit
definitions (`K/deveia.c:18-81`) are the only printed authority.

**O10 — Incon protocol.** `devincon.c` writes internal register numbers as
`csr` values and says nothing about the wire protocol; the "alive" bit is
assumed (`K/devincon.c:253-263`). Goal B's network gate would need a real
Incon peer or a documented substitute.

---

## 6. How each claim was checked

```sh
# provenance
shasum -a 256 /tmp/p9/plan9-1e.tar.bz2
mkdir -p /tmp/p9inv && cd /tmp/p9inv && tar xjf /tmp/p9/plan9-1e.tar.bz2
diff -rq tools/plan9-1e/sys/src/9/hobbit /tmp/p9inv/plan9-1e/sys/src/9/hobbit

# boot path, in order
nl -ba .../sys/src/9/hobbit/raml.s          # 1-100, 286-300
nl -ba .../sys/src/9/hobbit/mem.h           # 42-86
nl -ba .../sys/src/9/hobbit/machine.h       # 24-36, 68-136
nl -ba .../sys/src/9/hobbit/rammain.c       # 18, 89-122, 136-166, 235-250
nl -ba .../sys/src/9/hobbit/mmu.c           # 77-142, 144-201, 257-281
nl -ba .../sys/src/9/hobbit/trap.c          # 12-48, 120-172, 188-289, 394-481
nl -ba .../sys/src/9/boot/romboot.c         # 32-39, 518-553
nl -ba .../sys/src/9/hobbit/roml.s          # 12-75, 173-186, 322-336
nl -ba .../sys/src/9/port/devboot.c         # 99-120

# devices
grep -n "EIAADDR\|IRQQUART\|SCSIADDR\|SONICADDR\|LCDADDR\|IICADDR\|RTCADDR\|NVRAMADDR\|IRQINCON" \
     .../sys/src/9/hobbit/io.h

# build
nl -ba .../sys/src/9/hobbit/mkfile        # 1-12, 14-44, 48-63, 81-102
nl -ba .../sys/src/9/port/portmkfile      # 1-10, 31-38, 60-79
nl -ba .../sys/src/9/port/mkdevc           # 8-58
nl -ba .../sys/src/9/boot/mkboot           # 10-99
nl -ba .../sys/src/9/hobbit/cpu            # 1-78
nl -ba .../sys/src/9/port/chan.c           # 40-56
```

Deliberately not done: `9cpu` was **not** built (A3 is the build step; this
document fixes its inputs), no device model was written or changed, and no
claim in §5 was turned into a fix. The only artifact is this file.
