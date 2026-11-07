# Computer History Museum scans, fetched 2026-11-07

Downloaded from the CHM text archive,
`https://archive.computerhistory.org/resources/text/IBM/Stretch/pdfs/<box-folder>/<catalog>.pdf`.
None of these is mirrored on bitsavers. CHM catalog pages do not link
the PDFs: they were found by probing that URL pattern against catalog
numbers. Most are from the Kolsky papers (CHM accession X3021.2005).

**Only 102634375 has been read in the ink so far.** Every other title
below is the CHM catalog record's, not this project's reading. Rule 4
applies: cite a page only after reading it.

| catalog | box-folder | pp | catalog title / content | why it matters |
|---|---|---|---|---|
| **102634375** | 09-05 | 3 | **T. C. Chen, "The Multiplier Register on the 7030", memo to Dept. 271, 7 Sep 1961. READ.** | $MR and STM exist on K-2 and later only, not on X-1 (LASL), the 7950 or K-1 (LRL). $MR's exponent is $R.48-59 ($L.112-123), and its fraction and sign are the last 52 bits of the E-box D register. LMR = LFT's code 10010; *+ = 01110; STM = 11110. LFT, *+, M+, M+MG and D/ take two look-ahead levels on K-1, and one on improved machines with the operand in core. Times: LFT 2.8-4.4 µs on K-1; LMR 0.9-1.2 µs on K-2; *+ 6.5 µs on K-1, 3.9-4.5 µs on K-2. VFL side effects on $MR (p.2 item 8). Bears directly on MCP's STM probes (p.117 line 7, p.122 line 7). |
| 102634064 | 05-09 | 5 | Kolsky, "Simplified timing rules for SIGMA" | timing oracle candidate |
| 102632583 | 06-19 | 34 | Dirac/Bahnsen, "Proposal for a Sigma lookahead system", Dec 1957 | look-ahead design |
| 102632589 | 06-19 | 3 | look-ahead address register and forwarding | look-ahead design |
| 102632591 | 06-19 | 33 | Bloch, Sigma simulation | timing simulation |
| 102634322 | 15-26 | 86 | Cocke/Kolsky, "Stretch virtual memory concept and timing simulation program", with an SM-2 simulator appendix | may be a longer edition of TR00.03000.703 (42 pp) in docs/ |
| 102635106 | 09-06 | 17 | simulator result report | timing |
| 102635128 | 09-06 | 13 | simulator result report | timing |
| 102634001 | 03-07 | 2 | timing chart | timing |
| 102634092 | 05-10 | 3 | timing chart | timing |
| 102635057 | 06-04 | 6 | Bloch et al., "Timing in Sigma" | timing |
| 102634095 | 05-10 | 2 | data-flow schematic | E-box structure |
| 102632537 | 06-16 | 1 | VFL hardware flow | VFL unit |
| 102632307 | 06-24 | 36 | Brooks, RC-213, "Execute operations: a fourth mode" | EX / EXIC design |
| 102632361 | 06-10 | 15 | high-speed disk definition | the 353 |
| 102632367 | 06-10 | 18 | Exchange maintenance console controls | the Exchange |
| 102633953 | 03-03 | 104 | STRAP-1 manual, LASL 1959 | assembler history |
| 102634364 | 09-05 | 4 | SEVA | |
| 102634372 | 09-05 | 3 | index arithmetic bulletin | |
| 102634373 | 09-05 | 6 | progressive indexing bulletin | |

**Also at CHM but catalog-only, so it needs a request** (docs/archival_inventory.md
"CHM"): the Lowell Wood (LRL) collection, X2462.2002. It holds the VFL
diagnostic JB AV1C, the timing programs KA AT1 RAWSPEED, KA BT1 MEMTIM
and JA AT1 BASICTIM, the PAU diagnostics KC AF2/AF2B, and the SAU
diagnostic KC AV2B (records 102698893, -896 and -897). It also holds
diagnostic reference manuals, CE manuals of instruction and installation
manuals (102698889-91). Also catalog-only: the FIC "Stretch Manual of
Operation - Preliminary", May 1958, 317 pp (102633186).

The owner's untracked `docs/102634360 (1).pdf` is CHM 102634360,
from box-folder 09-05 (same byte count, 690,934).

## The full sweep, 2026-11-07: 484 of 1,039 records are online

The first fetch above probed 37 records. A second pass probed every
Stretch-related record in the catalog range 102632000-102637000 (1,039
records). It tried each catalog number in the box-folders of its
already-found neighbours, ±3 folders. **484 are online.**
`online_index.tsv` lists every one: catalog number, box-folder, size,
date and the catalog title. Any of them can be fetched from

    https://archive.computerhistory.org/resources/text/IBM/Stretch/pdfs/<box-folder>/<catalog>.pdf

A MISS means "not at a neighbour's folder". It does not mean "not
online", so the 555 misses are not proof of absence.

**102 more are now in this directory**, chosen for the replication. They
are listed by theme below. The rest of the 484 are mostly marketing,
committee minutes, 1955-57 design studies the machine moved beyond, and
press material. Titles are the CHM catalog's unless a line says
"read". Rule 4 still applies.

**Read so far, and what each settles:**

- **102634363, "7030 Publications List", 7 Jul 1961, 1 p. Read in the
  ink.** IBM's "complete summary of all literature that has been
  published for the IBM 7030 computer as of July 1, 1961". Against this
  repo's holdings:
  - **Held, some from this sweep:**
    - the Reference Manual (held as the later 22-6530-2);
    - C22-6531-1, the 704-9-90 package;
    - C22-6578 Programming Examples;
    - J22-6559 MCP Users Guide;
    - C28-6129 STRAP-II Reference Manual;
    - X28-6131 Programming System Reference Card;
    - **J22-6532, the "IBM 7030 Systems Program Package" bulletin =
      102634122**;
    - **J28-6127, the FORTRAN bulletin = 102634362**;
    - J28-6126 Minimum Configuration = 102634359 (form number in its
      text layer). It lists MCP's minimum machine: 32K words of core,
      the 1401 off line, a 7612/7302 disk for system and object
      programs, the 7152 console, the 7503 reader, and four 729 IV
      tapes (Spool Output, Alternate Spool Output, Spool Read, and
      Spool Write/Scan).
    - X22-6798-0 STRAP program sheet = 102633946 (the form number is
      printed on it);
    - X22-6533 Reference Card and A22-6552 Physical Planning Manual,
      already in `docs/` (from bitsavers).
  - **Still not held:**
    - D22-6513 General Information Manual (102634357 is a 1960
      edition, probably the same);
    - **J28-6128 SMAC Bulletin** (102634361 is only its errata sheet);
    - the "Specifications Notebook (for Programs)", from Dept. 271,
      "available on a limited basis";
    - the card stock A26425 and A36259.
- **102634122, J22-6532, read from its text layer.** IBM's own list of
  the 7030 systems programs:
  - STRAP I and the 7030 Simulator, on the 704, 709 and 7090;
  - **a 704 Simulator and a 709 Simulator that ran ON the 7030**, so
    that old programs could run "with a minimum of reprogramming";
  - MCP;
  - STRAP II;
  - "a set of processors that operate on languages at several levels".
  The two simulators are IBM environment pieces this repo had not listed.
- **102634362, J28-6127, read from its text layer.** 7030 FORTRAN "must
  be used in conjunction with the Master Control Program", and its
  object programs run under MCP, which does their I/O.
- **102633932, read from its text layer.** It is the STRAP-1
  specification and a "Primitive Supervisor": a binary loader with
  origin, flow, branch and dump cards, an interrupt table and debugging
  macros. That is the pre-MCP environment.
- **102632618** is catalogued "Computer memos, 1960-61", but its first
  pages are the **Revised Manual, Harvest System, 13 Nov 1957**: stream
  indexing and the streaming mode of the 7950. That is outside the 7030
  scope; it is kept as a citation.

### Software: programming systems, STRAP, MCP, FORTRAN

| catalog | box-folder | pp | date | catalog title |
|---|---|---|---|---|
| 102634363 | 09-05 | 1 | 1961-07-07 | 7030 publications list |
| 102634122 | 05-10 | 3 | Circa 1965 | IBM 7030 systems program package |
| 102634362 | 09-05 | 2 | 1961 | The IBM Fortran system |
| 102634361 | 09-05 | 2 | Circa 1965 | SMAC language processor errata sheet |
| 102633932 | 03-01 | 66 | Circa 1959-06-01 | Stretch programming systems specifications manual |
| 102633930 | 03-01 | 1 | 1959-06-04 | New edition of the completely revised Stretch programming systems specifications manual |
| 102633931 | 03-01 | 1 | 1959-06-19 | Correction of June 1 edition of the Stretch programming systems specifications manual |
| 102633933 | 03-01 | 39 | 1957-07-01 | Revisions to the Stretch programming systems specifications manual |
| 102633935 | 03-01 | 25 | 1957-07-29 | Stretch coding assumptions |
| 102633938 | 03-01 | 1 | 1959-03-13 | Address arithmetic in STRAP-1 |
| 102633939 | 03-01 | 20 | 1960-12 | IBM 7030 Data Processing System : Master Control Program user's guide |
| 102633941 | 03-02 | 23 | 1960-07-05 | Program preparation for Stretch |
| 102633942 | 03-02 | 1 | Circa 1959 | Strap control card |
| 102633944 | 03-02 | 7 | 1960-03-10 | Documentation of instruction set |
| 102633946 | 03-02 | 1 | Circa 1959 | IBM STRAP program sheet |
| 102633954 | 03-03 | 1 | 1959-11-10 | Note about floating point zeros in Stretch (addenda to the STRAP-1 write-up) |
| 102633955 | 03-03 | 3 | 1960-01-07 | Appendix D of the STRAP 1 manual |
| 102633956 | 03-03 | 5 | Circa 1960 | Appendix F of the STRAP 1 manual |
| 102633958 | 03-03 | 4 | 1960-05-10 | STRAP-1 pseudo operations |
| 102633957 | 03-03 | 6 | 1960-05-03 | Stretch math subroutine conventions |
| 102633965 | 03-05 | 105 | Circa 1959 | Stretch 7030 programming examples : matrix, cosine, log, exp |
| 102632570 | 06-17 | 32 | 1959-06-05 | Specifications for a debugging console-defining routine |
| 102632571 | 06-17 | 5 | 1959-06-16 | Examples illustrating the use of CONDEF |
| 102635069 | 06-04 | 4 | 1960 | Appendix A |
| 102633945 | 03-02 | 1 | 102633945 | Annotated partial program listing |
| 102634359 | 09-05 | 2 | 1961 | IBM 7030 minimum configuration |
| 102634357 | 09-05 | 26 | 1960 | IBM general information manual : 7030 data processing system |

### Training material (1959-60 Stretch schools)

| catalog | box-folder | pp | date | catalog title |
|---|---|---|---|---|
| 102633940 | 03-02 | 22 | 1959-05-04 | Introduction to the Stretch system : a talk by F.P. Brooks, Jr. |
| 102633947 | 03-02 | 2 | 1960-10 | Life history of a problem solved on the 7030 |
| 102633948 | 03-02 | 4 | 1960-10 | Major units in the 7030 |
| 102633950 | 03-02 | 2 | 1960-10 | List of important registers in the 7030 |
| 102633951 | 03-02 | 3 | 1960-10 | Summary of 7030 instruction execution |
| 102633952 | 03-02 | 3 | 1960-11 | Hints towards good 7030 programming |
| 102634098 | 05-10 | 7 | 1959-02-16 | Notes taken at "Stretch school" |
| 102634100 | 05-10 | 3 | 1959-02-16 | Lecture notes |
| 102634120 | 05-10 | 2 | Circa 1965 | Brief summary of IBM 7030 data processing system |
| 102634121 | 05-10 | 1 | Circa 1965 | Instruction formats |
| 102634123 | 05-10 | 2 | Circa 1965 | Detailed instruction breakdown |

### Console, Exchange, I/O, the disk

| catalog | box-folder | pp | date | catalog title |
|---|---|---|---|---|
| 102634101 | 05-10 | 8 | 1959-02-25 | Console program |
| 102634111 | 05-10 | 1 | 1959-06-30 | Revisions in console |
| 102634112 | 05-10 | 2 | 1959-07-02 | Exchange channel addressing |
| 102634113 | 05-10 | 1 | 1959-10-02 | Stretch preliminary Manual of operation, revised Chapters 2, 4, and Appendix, dated 8/15/59 : acknowledgement of receipt |
| 102632355 | 06-10 | 30 | 1957-01-21 | Exchange machine definition |
| 102632356 | 06-10 | 3 | 1957-02-04 | Increasing simultaneous operation in the Exchange |
| 102632358 | 06-10 | 5 | 1957-06-18 | Switching between the Exchange and the input-output units |
| 102632360 | 06-10 | 5 | 1957-06-21 | General performance characteristics of the Basic Exchange |
| 102632512 | 06-16 | 3 | 1958-01-27 | Exchange |
| 102632522 | 06-16 | 4 | 1958-09-25 | Present state of 729 tape control in the 7000 System |
| 102632526 | 06-16 | 4 | 1958-10-06 | Binary serial disk file and error correction |
| 102632531 | 06-16 | 1 | 1958-10-23 | Modifications of the Exchange |
| 102632532 | 06-16 | 2 | 1958-10-01 | Disk characteristics |
| 102632538 | 06-16 | 4 | 1958-11-05 | Character and control codes |
| 102632541 | 06-16 | 5 | 1958-11-17 | High-speed disks |
| 102632543 | 06-17 | 3 | 1959-01-09 | Control codes for the 7030 system |
| 102632544 | 06-17 | 1 | 1959-01-27 | Resetting of odd-even parity and high-low density triggers in 729 tape |
| 102632545 | 06-17 | 1 | 1959-01-28 | Capacity of the Basic Exchange |
| 102632556 | 06-17 | 5 | 1959-05-26 | Attachment of 1401 (space) to 7030 (Stretch) |
| 102632558 | 06-17 | 11 | 1959-05-07 | Binary serial files |
| 102632564 | 06-17 | 2 | 1959-06-09 | High speed parallel disk file operation |
| 102632565 | 06-17 | 2 | 1959-06-09 | Use of spare memory for control word locations |
| 102632567 | 06-17 | 1 | 1959-06-09 | Present definition of the Low Speed Exchange |
| 102632568 | 06-17 | 2 | 1959-06-03 | Serial binary ADF file and million character file |
| 102632569 | 06-17 | 5 | 1959-07-02 | Binary serial disk proposal |
| 102632614 | 06-21 | 4 | 1959-07-10 | Stretch disk file etc. : meeting or contact report |
| 102632566 | 06-17 | 1 | 1959-06-09 | 7030 system card reader |
| 102632563 | 06-17 | 2 | 1959-05-28 | Unit check operation |
| 102632519 | 06-16 | 1 | 1958-06-11 | Elimination of RELEASE |
| 102632520 | 06-16 | 2 | 1958-06-13 | RELEASE instruction and EOS mode |
| 102632521 | 06-16 | 2 | 1958-06-16 | RELEASE instruction |
| 102632505 | 06-16 | 6 | 1958-08-22 | Actuation of indictors and consequent effect on machine operations |
| 102634057 | 05-09 | 2 | 1959-03-26 | Input/output units for 7030 system |
| 102632592 | 06-19 | 4 | 1958-12-20 | Attachment of 729 tapes to project 7000 system |

### Arithmetic and instruction set

| catalog | box-folder | pp | date | catalog title |
|---|---|---|---|---|
| 102632562 | 06-17 | 1 | 1959-05-22 | No operation control instruction |
| 102632559 | 06-17 | 1 | 1959-05-11 | Meeting of May 6, 1959, on true zero handling |
| 102632560 | 06-17 | 2 | 1959-05-11 | True zero handling |
| 102632587 | 06-19 | 30 | 1958-03-25 | Floating point instruction set |
| 102634374 | 09-05 | 7 | 1961-08-28 | Floating-point arithmetic |
| 102634376 | 09-05 | 8 | 1961-09-12 | Design of floating point arithmetic |
| 102635058 | 06-04 | 10 | 1959-03-27 | VFL integer instructions |
| 102632344 | 06-09 | 1 | 1956-09-20 | Adding one to memory |
| 102632346 | 06-09 | 2 | 1956-09-21 | Storing part words in memory without destroying the remainder |
| 102632348 | 06-09 | 2 | 1956-09-27 | Floating point definition |

### Timing and simulation

| catalog | box-folder | pp | date | catalog title |
|---|---|---|---|---|
| 102633975 | 03-07 | 4 | Circa 1955 | Stretch timing simulation program SIM-2 |
| 102635101 | 09-06 | 14 | 1958-02-06 | First report on results of Sigma timing simulator program |
| 102635105 | 09-06 | 3 | 1958-03-05 | Distribution of operation classes in sample programs used in Sigma timing simulator |
| 102635110 | 09-06 | 2 | 1958-04-18 | Sigma performance -- a list of some "5 percent effects" |
| 102635114 | 09-06 | 9 | 1958-05-19 | Branching on arithmetic results in Sigma |
| 102635115 | 09-06 | 1 | 1958-05-20 | Memory cycle times and their effect on Sigma performance |
| 102635123 | 09-06 | 11 | 1958-08-29 | Effect on Sigma performance of the half-microsecond instruction memory |
| 102635131 | 09-06 | 12 | 1958-11-20 | Sigma performance compared to other computers |
| 102635134 | 09-06 | 4 | 1959-03-10 | Percentage effects of certain component variations on Sigma internal computing speed |
| 102635135 | 09-06 | 9 | 1959-04-21 | Stretch performance |

### Multiprogramming (MCP's design ancestry)

| catalog | box-folder | pp | date | catalog title |
|---|---|---|---|---|
| 102635071 | 06-05 | 2 | 1957-05-21 | Computer operation - multi-program control |
| 102635078 | 06-05 | 8 | 1958-01-02 | Multiprogram control - signals from the operator to the supervisory program |
| 102635079 | 06-05 | 2 | 1958-05-08 | Multiprogram control - CPU attention switching |
| 102635081 | 06-05 | 3 | 1958-09-30 | Some conventions for the unshared subroutines capable of operating in the supervised mode |
| 102635087 | 06-05 | 3 | 1960-04-29 | Multiprogram scheduling |
| 102635088 | 06-05 | 2 | 1960-05-12 | Multiprogramming Stretch : feasibility considerations |
| 102635077 | 06-05 | 3 | 1957-12-17 | Automatic protection and relocation scheme |

### Other

| catalog | box-folder | pp | date | catalog title |
|---|---|---|---|---|
| 102632618 | 06-22 | 136 | 1964-01-10 | Computer memos, 1960-61 |
| 102634173 | 05-14 | 14 | 1960-10-27 | Meeting on Stretch and Super Stretch plans, Poughkeepsie |
| 102634174 | 05-14 | 9 | 1960-10-20 | Meeting with Livermore at research center |
