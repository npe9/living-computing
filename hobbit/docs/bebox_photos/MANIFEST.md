# Photographs of Hobbit BeBox boards: acquisition manifest

Collected 2026-11-24 as evidence for `../bebox_hardware.md` (tag [P]). The
images are held on disk in this directory but kept **out of git**
(`.gitignore`): none of their sources shows redistribution terms, and the
repository is public. `sh fetch.sh` downloads whatever is missing and checks
every file against `SHA256SUMS` (`sh fetch.sh --check` only checks). The
checksums were confirmed by a fresh re-fetch.

| File | Source | What it shows, as used in the dossier |
|---|---|---|
| `shibata_motherboards.jpeg` | Fumihiko Shibata, *BeBox GuideBook*, photo 5, as posted to the Haiku forum (2020-10-08) | Early Be motherboards together |
| `shibata_rev1.jpeg` | same, photo 6 | Rev 1: wire-wrapped, one Hobbit at 25 MHz, one serial port (caption) |
| `shibata_rev2.jpeg` | same, photo 7 | Rev 2: PCB, "Be Motherboard revision 2", I/O on daughter cards (caption) |
| `shibata_rev4.jpeg` | same, photo 8 | Rev 4: "Be Machine board revision 4", socketed CPUs and DSPs; caption also describes Rev 3 |
| `strickland_5841494811_b.jpg` | Colin M. Strickland, Flickr album "Original BeBox", 2011-06-17, S/N 9308000017 | CPU1/CPU2 `BL-ATT92010-CN 9309A`; DSP1-3 `DSP3210 F12 072 9309S` |
| `strickland_5841550383_b.jpg` | same | "COMBO I/O" U400 (windowed ceramic QFP); AM29F010-120PC flash; Motorola MCS3201FN beside the FDC header |
| `strickland_5841616027_b.jpg` | same | Eight 30-pin SIMM sockets (3-chip parity SIMMs); socketed DIP-32 flash with green stickers; glue logic |
| `strickland_5841616289_b.jpg` | same | Case front: Be badge, Turbo and Reset buttons |
| `strickland_5842009852_b.jpg` | same | Serial label, "Rev. A", S/N 9308000017 |
| `strickland_5842090860_b.jpg` | same | External Rayovac 844 4.5 V clock battery |

URLs:

- Haiku forum thread: <https://discuss.haiku-os.org/t/original-bebox-introduction-at-agenda-96/9512/8>;
  images under `https://discuss.haiku-os.org/uploads/default/original/2X/` (paths in `fetch.sh`).
  Larger copies were once at `lorezan.free.fr/BeBoxHobbit/`, which now returns HTTP 500;
  its Wayback captures are HTML, not images.
- Flickr: `https://live.staticflickr.com/<server>/<id>_<secret>_b.jpg` (paths in `fetch.sh`).
  The image host refuses curl's default user agent, so `fetch.sh` sends a browser one.

Nothing downloaded was executed.
