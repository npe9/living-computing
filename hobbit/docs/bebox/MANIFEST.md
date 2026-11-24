# Hobbit BeBox: surviving software and documents (held on disk, not in git)

Everything below was fetched on 2026-11-24 from the "BeOS Hobbit Prototype
Release" directory of fsck.technology's software archive,
<https://fsck.technology/software/Be/BeOS%20Install%20Media/BeOS%20Hobbit%20Prototype%20Release/>
(an h5ai listing; the files there are dated 2019-11-08). It is Be Inc.'s
proprietary software and a draft hardware manual marked "CONFIDENTIAL : Be
Labs, Inc."; the archive states no licence or redistribution terms, and the
repository is public, so **none of it is committed**. `fetch.sh` fetches it
again into `hobbit/build/bebox/` (gitignored by `hobbit/.gitignore`'s
`build/`) and checks every file against `SHA256SUMS` (194 files).
Provenance and what each file holds are in [`../bebox_hobbit.md`](../bebox_hobbit.md).

Each archive has its own directory. The contents are untrusted data: no
binary from them is run on the host (they are Hobbit code; the only thing
that executes them is the reference model), and every Python that reads
them runs with `python3 -I` (`tools/befs1.py`, `tools/beboot.py`).

| local path under `build/bebox/` | bytes | what it is |
|---|---:|---|
| `hdd-Hobbit-9308000044/Hobbit-9308000044.img` | 170,233,856 | SCSI disk of BeBox serial 9308000044; volume `be3`; `/system/kernel` 177,976 B, built **Mar 1 1994** |
| `hdd-hobbit-9308000058/hobbit-9308000058.img` | 170,233,856 | SCSI disk of serial 9308000058; volume `be`; kernel 197,868 B, built **Nov 23 1994** |
| `hdd-hobbit-930800009/hobbit-930800009.img` | 127,233,024 | SCSI disk; volume `pixels`; same kernel as 0058 (identical SHA-256) |
| `fsdump-be3/be3.tgz` | 41,103,360 | tar of the `be3` volume's files (774 entries) |
| `fsdump-pixels/pixels.tgz` | 27,985,920 | tar of the `pixels` volume's files (610 entries) |
| `floppy-installer/installer.img` | 1,474,560 | installer boot floppy: `/system/kernel` (the Nov 1994 kernel, stripped: 158,444 B), servers, `/Installer` |
| `floppy-1of7/1of7.img` … `floppy-7of7/7of7.img` | 7 × 1,474,560 | install set: each holds `/info` and one `archive.Z00` piece (compress'd tar, split by `chop`) |
| `floppy-update/update.img` | 1,474,560 | Be's update of 28 Nov 1994: `/info`, `archive.Z00` (phone prompts, `storage_server`) |
| `docscans/letter.jpg`, `intro1.jpg`, `intro2.jpg` | 2,885,733 | cover letter (Paula Butler & Ctein to Dan Dahle, Be Labs, 16 Sep 1993) and introduction |
| `docscans/chapter1/` … `chapter9/`, `appendix/` | 176 files, 135,603,692 | "Be machine hardware documentation", interim drafts of 15/16 Sep 1993: 1 Slots, 2 I/O, 3 Joysticks, 4-6, 7 Floppy, 8 Printer, 9 SCSI, Appendix A Memory Map (page scans, JPEG) |

| `datasheets/NCR_53C94_53C95_53C96_Data_Sheet_Feb90.pdf` | 3,002,374 | NCR 53C94/95/96 data sheet, Feb 1990, from bitsavers `components/ncr_symbios/scsi/53C94/` (not from fsck.technology): `tools/beboot.py`'s 53C94 model cites its Table 8 (p. 18) and p. 33 |

Total about 714 MB.

What does **not** exist publicly (as of 2026-11-24, see `../bebox_hobbit.md`,
"Searches"): any dump of the Hobbit BeBox boot ROM (flash), or of the
DSP3210 code in ROM. The kernel is therefore booted the way the ROM would:
loaded from the disk's `/system/kernel` ELF file.

Kernels extracted for analysis (build products, `build/bebox/kernels/`,
made by `python3 -I tools/befs1.py IMAGE --get /system/kernel OUT`):

| file | SHA-256 |
|---|---|
| `Hobbit-9308000044.kernel` (Mar 1994) | `1c91a68995d6bb6e0fed7dc36d0141d83deb0b6bd258c5dfb76112c8b7f57aaf` |
| `hobbit-9308000058.kernel` = `hobbit-930800009.kernel` (Nov 1994) | `450716b22c33ed105684cdbe660b73e1843f2308b66fa76f2a153be112167b0b` |
| `installer.kernel` (Nov 1994, stripped) | `30a1b0cfeb1e78f3a01913ac9785a38cf7376c3a783497d1d57a649289264d97` |
