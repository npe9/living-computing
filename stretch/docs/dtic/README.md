# DTIC reports with real 7030 programs, fetched 2026-11-07

US government technical reports, 1964-68, from the Defense Technical
Information Center, fetched from archive.org
(`https://archive.org/details/DTIC_<id>`). Each one documents a program
that ran on a real 7030 under MCP: at MITRE (Bedford, MA) or at the
Naval Weapons Laboratory, Dahlgren. Several print their **job decks
and listings**. Together they are the only first-hand examples this
repo holds of how users actually submitted work to MCP.

They are scans with poor OCR. Rule 4 applies: read the page image
before citing anything.

| id | pp | what | what it shows (from the OCR; to be read in the ink) |
|---|---|---|---|
| AD0642331 | 78 | Sullivan, "XPSTC, a FORTRAN dynamic storage allocator", MITRE ESD-TR-66-94, Oct 1966 | The 7030 FORTRAN IV calling sequence at STRAP level. MCP is the monitor. The target is "IBM 7030 (improved version with $MR)". Cites MITRE's "7030 Facility Manual", Aug 1965, which is not found. |
| AD0658446 | 40 | Beilin, "MERGE", MITRE ESD-TR-67-371, Aug 1967 | A 7030 tape merge, with IOD/REEL card usage, an IOD table and control-word layouts |
| AD0685715 | 134 | "Numerical solution of electromagnetic scattering problems" (IMSCAT), 1968 | FORTRAN listings under `T SUBTYPE,FORTRAN,LMAP,LSTRAP` cards, and **a STRAP II routine under `SUBTYPE,STRAP`**, around printed pp.84-85 (OCR page markers): PUNREL, ENTER, `B,$MCP` / `,$AREOJ` |
| AD0646577 | 57 | CHITRAN, a 7030 chi-square program, NWL Dahlgren, 1967 | **A complete deck head**, around printed pp.45-46 (OCR page markers): class-B IOD and REEL cards (`IOD,DISK,...`), `SUBTYPE,FORTRAN,LMAP,DBIN`, then the source |
| AD0663887 | 67 | BI-CHI, NWL Dahlgren, 1967 | the same kind of deck |
| AD0665291 | 52 | Kolmogorov test, NWL Dahlgren, 1968 | the same kind of deck |
| AD0642369 | 31 | helicopter armament suppression model, 1966 | listing in Appendix E |
| AD0642495 | 80 | incomplete beta function, 1966 | STRAP / "absolute machine language" coding, described in prose; no listing found in the OCR |
| AD0601171 | 68 | FORSIM IV, MITRE, 1964 | cites G. A. Fagan, "The STAPP System", MITRE TM-67, which is not found |

**Why they matter here.** Step E4 of `docs/programming_environment.md`
(a first job) needs real card decks. These are real decks, so the job
can be one IBM's users ran rather than one this project invented. The
FORTRAN sources are also test input for a found or reconstructed
FORTRAN IV (E7). Found by a delegated search; the archive.org records
were re-checked by hand.
