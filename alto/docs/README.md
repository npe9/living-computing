# Xerox Alto documentation inventory

| source | status and role |
|---|---|
| Siewiorek, Bell, and Newell, *Computer Structures: Principles and Examples* (1982), ch. 33, printed p. 549 | book source; personal-computer structure, graphics, I/O, and Ethernet context |
| *Alto Hardware Manual* (Xerox PARC, May 1979; Bitsavers) | **cited by section throughout `bsv/`, not yet held**; acquire with checksum and convert citations to printed pages |
| Alto microcode listings (source with assembled octal) | not present; the intended primary oracle for the PROM images |
| Ethernet documentation (3 Mb/s interface) | covered by the Hardware Manual §7 as cited in `bsv/Ethernet.bsv`; separate documents not present |
| ContrAlto emulator (Living Computers Museum) | **not a source**; two design choices in `bsv/` cite it and are listed as gaps in `../README.md` |

The model in `bsv/` (imported 2026-11-24) was written from the Hardware Manual before that manual was added here. Add checksummed
Xerox primary documents and original software or diagnostics with printed-page
citations; do not infer Alto behavior from later emulators.
