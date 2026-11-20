# PIMOS boot binaries: `.kbn` and `.sav`

Source note for running PIMOS on the Bluespec model. The corpus contains
the bootable PIMOS images in `docs/nonlocal/pimosobj.tar.Z`. This note
records what the format is, from the PIMOS unloader source and from the
bytes themselves, so a loader can be written against evidence rather
than guesswork.

## The boot artifacts

| File | Size | Role |
|---|---|---|
| `pimm_ipl.kbn` | 92,160 B | IPL code, loaded first from CSP; only enough to load PIMOS |
| `pimm_kernel360E.sav` | 408,482 B | kernel module set |
| `pimm_library360E.sav` | 1,316,520 B | library module set |
| `pimm_shell360E.sav`, `pimm_server360E.sav`, `pimm_utility360E.sav`, `pimm_macro360E.sav`, `pimm_bios360E.sav`, `pimm_debugger360E.sav` | | remaining system modules |
| `pimm_patch_*.sav` | | patch modules, loaded last |
| `pimos.ipl` | 1,678 B | list of `.sav` files to load, in order |
| `pimm_ipl.sym`, `pimm_ipl.ldb` | | symbol tables (tagged text) |

`pimos.ipl` is a tagged KL1 list of module paths. Decoding the tag pairs
gives `dsys:cs:PIMOS.DIR>pimm/kernel360E.sav`, and the rest of the
sequence likewise.

The PIMOS manual (`e-sysman.tex` §IPL Setup) states the contract:
`*.kbn` is loaded from CSP and is "only the code required to IPL
PIMOS"; that code then loads the modules listed in `pimos.ipl`. From
version 3.0 the files are produced by the PIMOS unloader.

## `.kbn`: a raw heap image

`pimm_ipl.kbn` is **not** a stream of instructions. It is a memory
image. 0xe0-prefixed 32-bit words are unbound-variable cells (tag
`0xe0`, pointer in the low bits), and `0x00000000` is free memory.
Disassembling every word as an instruction is meaningless; the code is
embedded in the heap as tagged cells.

The first words are `0xe0000000`, `0x0000477c`, `0xe0001e81`,
`0xe0001e25`, then zeros. That is a UREF, a small value, two more UREFs,
then free space — a heap, not code.

The load address and entry point are not stated in the `.kbn` itself.
The boot contract is in `pimos/src/bios/boot/bios.kl1`: `go/4` is the
top-level predicate; it initializes SCSI, merges the loaded modules,
calls `predicate_to_code(module#init,go,0,PIMOS_TOP)` and executes
`PIMOS_TOP` at priority 4050.

## `.sav`: unloader module files

The format is defined by `pimos/src/library/unloader/encoder.kl1` (and
`unlver.kl1`, `termencoder.kl1`). The stream is 16-bit big-endian words.

### File header

```
[MagicNum, N, 0xFFFF, (comment length L1,L2, comment words...) , modules...]
```

`MagicNum` from `unlver.kl1`:

| Value | Meaning |
|---|---|
| `0x5502` | module |
| `0x5602` | package |
| `0x5702` | comment (used by the `.sav` files here) |
| `0x5802` | commented package |
| `0x5902` | term encoding |

The kernel `.sav` starts `5702 002a ffff 0000 0020`: comment marker,
42 modules, separator, comment length 32, then 32 tagged comment words.

### Module

```
[L1, L2, GCSize, GC-area, pred-table, code, 0xFFFF]
```

`L1:L2` is the module length; `GCSize` is the number of GC-area
elements. The kernel's first module is `0000 0cea 0004`: length 3306,
4 GC elements.

### Term tags observed in the `.sav`

The 1992 encoder writes atoms with tag `0x0000`; the 1994 `.sav` files
use `0x8000`/`0x8001`/`0x8002` for atoms. The observed encodings:

| Tag | Meaning | Payload |
|---|---|---|
| `0x8000`–`0x8002` | atom | AtomID, length, then one tagged char word (`0x23xx`) per character |
| `0x0100\|v` | small integer | value |
| `0x0200\|v` | small negative integer | value |
| `0x0300` | large integer | hi, lo |
| `0x00TT`, `TT` > 0 | tagged 32-bit object (floats use `TT` = `0x30`) | V1, V2 |
| `0x0600\|size` | string | L1, L2, then one tagged char word per character |
| `0x0700` | vector | L1, L2, then elements |
| `0x0800` | list | L1, L2, then elements |
| `0x1900` | module | atom names |

The kernel's first module GC area decodes to the atoms
`exception/table` and `matsuo`, the integer 2555905, and a vector of
eight elements whose fifth is a 55-character string.

### Predicate table

Starts with `0x1000`, then `HashSize`, `EntryNo`. Entries are
variable-length hash slots; the observed entries carry an atom name
(`0x8003`… tags), an arity, and a 32-bit code offset (`Loc1`, `Loc2`).
The hash-table structure is not fully transcribed here; the code
section is what a loader needs first.

### Code section

The code is a sequence of KL1-B words. The general form is a triple:

```
[0x0023, VAL1, VAL2]      ; value = (VAL1 << 16) | VAL2
```

`VAL1`'s top byte is the opcode from `inst_tab.kl1`; the low 24 bits are
the operand fields. Examples from the kernel tail:

| Words | Value | Instruction |
|---|---|---|
| `0023 bd03 0d00` | `0xbd030d00` | `get_bound_value r3, r13` |
| `0023 1401 1400` | `0x14011400` | `set_value 1, r20` |
| `0023 1402 1500` | `0x14021500` | `set_value 2, r21` |
| `0023 1304 0c00` | `0x13040c00` | `set_variable 4, r12` |

Atom operands are a special case: `encode_code_1` writes
`0x2300|Reg` (set_atom), `0x2340|Reg` (put_atom), `0x2380|Reg`
(wait_atom), `0x23C0|Reg` (get_atom), `0x2323` (write_atom), `0x23B3`
(read_atom), each followed by the atom name.

The kernel's first module has its code from word 333 to 3343 (the
module ends at 3343). Disassembling the tail with the table in
`kl1_encoding.md` gives, for example:

```
write_marked_value r10
write_marked_value r6
write_variable r8
write_value r15
get_bound_value r3, r13
set_value 1, r20
set_value 2, r21
```

Thirteen opcodes appear in the object set that are commented out in
the 1992 `inst_tab.kl1`: `put_vector_0`..`put_vector_6` (`0x38`-`0x3e`)
and `wait_vector_1`..`wait_vector_6` (`0xa9`-`0xae`). The 1994 binaries
use these per-length quick forms; that is a real version difference,
not a decode error. A code area also holds two kinds of non-instruction
tagged word: predicate heads (tag `0x24`) and float constants (tag
`0x30`). Counts and sources are in `pimos_boot_requirements.md`.

## What a loader needs

1. Parse the `.sav` header and modules.
2. Decode the GC area (atoms, vectors, lists, strings, integers) into
   the model's memory image.
3. Decode the pred table into `(predicate, arity, code offset)`.
4. Decode the code section into 40-bit tagged words.
5. Load the `.kbn` heap image at its base address and set the entry
   point per `bios.kl1` (`go/4`).

The `.kbn` base address and the exact heap-image layout are the
remaining unknowns; the `.sav` format is documented above and by
`encoder.kl1`.

## The SCSI device PIMOS expects

The boot path reads the `.sav` modules over SCSI. The code distinguishes
two things: the boot file service and the disk driver.

**Boot file service.** `bios/boot/scsi_conf.kl1` gives the PE's own SCSI
address, default `{0,0,0,6}`: cluster 0, processor 0, SCSI port 0, unit
6. `bios/boot/bios.kl1` gives the FEP target: `Cluster=0, Processor=0,
Unit=7, Send_LUN=0, Receive_LUN=1`. So on real hardware the modules come
from the CSP/FEP file service at unit 7, LUN 0 (send) and LUN 1
(receive), not from a raw disk the PE block-reads.

**Disk driver.** `bios/scsi/scsi_common.kl1` parses INQUIRY by the
standard format: byte 0 is the Device Code, byte 1 bit 7 is RMB, byte 4
is the additional length. It checks the device type only, not a vendor
or product string. `bios/boot/scsi_man.kl1` maps
`scsi#direct_access` to `direct_access`, so the expected device is a
**direct-access (DASD) block device, device code 0**. `bios/scsi/DAM.kl1`
is the direct-access method: INQUIRY, TEST UNIT READY, READ(6) (21-bit
block address), WRITE(6), MODE SENSE/SELECT, READ CAPACITY (0x25), and
the rest of the SCSI-1 command set. `SAM.kl1` is the sequential (tape)
path and is not used for boot.

The block size is not hardcoded: `read_capacity` (0x25) is the command
that reports it, so the shim chooses it (512 or 1024) and reports it
there.

**VM interface.** Under `virtual_machine_interface: yes` (the
pseudo-PIM configuration closest to the Bluesim model), the disk is a
`scsi_simulator` whose ports come from the `vm:scsi_where` environment
variable, default `[{0,0,0,6}]`. The model's device shim therefore
implements the simulator's command interface, not a physical SCSI bus.

### What a device shim needs

- The command/response interface of `scsi_simulator`: CDB in, data and
  status out.
- A block device (SD card or SDRAM image) holding `pimos.ipl` and the
  `.sav` modules.
- INQUIRY returning device code 0 (direct access), and READ CAPACITY
  returning the chosen block size and block count.
- READ(6)/WRITE(6) block transfers.

A full SCSI bus (arbitration, phases, bus-free) is not needed: the PE's
driver issues CDBs to a unit and waits for the response.
