# How ICOT / FGCS did databases, and what that means for a reconstructed PIM/m

Research survey, compiled 2026-11-20. Research only: nothing here changes the
model. Every substantive claim carries its source and one of three marks:

- **READ** -- I opened the document (or unpacked the archive) and saw the
  statement. "READ (OCR)" means a scanned ICOT TR/TM that I ran through
  tesseract myself; OCR text is noisy, so numbers quoted from OCR were checked
  against the page image only where I say "image-checked".
- **ABSTRACT** -- from a catalogue entry, a title in the TR/TM list, or an
  abstract page; the body was not read.
- **SECONDARY** -- a later retrospective or home page.

Web-search result summaries were used only to find URLs, never as evidence.

Quotations from the FGCS'92 proceedings are taken from the text layer of the
held scans, which is itself OCR; I silently corrected obvious OCR slips
inside quotations ("K11" for KL1, "1(QL" for KQL, stray spaces). The one
Kappa-P number quoted from there ("at least three times") was checked
against the page image.

Archive roots used below:

- `MUSEUM` = `https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum`
- `IFS` = `https://www.airc.aist.go.jp/aitec-icot/ICOT/ifs`
- FGCS'92 proceedings: the two volumes already held in this directory
  (`FGCS92_Volume_1.pdf`, `FGCS92_Volume_2.pdf`); page numbers are printed
  page numbers.

## 0. The answer in fifteen minutes

1. **Three generations, three different ideas.** Initial stage (1982-85): a
   hardware relational database *machine*, Delta, as a back end to PSI
   workstations over a LAN. Intermediate stage (1985-88): "knowledge base
   machines" that extended relations to hold Prolog terms and retrieved by
   unification (RBU, the unification engine, Mu-X with a multiport page
   memory), plus software systems on PSI/SIMPOS (Kappa-I/II, PHI, CRL).
   Final stage (1989-94): no database hardware at all. The database is a
   KL1 *program*, Kappa-P, running on the same PIM as its applications,
   under PIMOS, with the DOOD language Quixote above it.
2. **The database stack on PIM was: PIMOS -> Kappa-P -> (Quixote) ->
   applications.** Kappa-P is a nested-relational (NF2) DBMS written in KL1:
   one "element DBMS" per cluster/node, some of them "server DBMSs" holding a
   replicated global map, "interface processes" created per application,
   two-phase commit between element DBMSs, B-tree indexes on disk, T-tree
   indexes in memory, a buffer manager, a recovery log. (READ: Kawamura et
   al., FGCS'92 pp. 248-256; READ: the released source.)
3. **Kappa-P's source survives and is small enough to study**: IFS package
   13, `kappa-p.tar.Z`, 1,897,310 bytes, 510 files, 344 `.kl1` files,
   151,683 lines of KL1, plus 7 ESP files for the front end. Its own README
   names the machines: "PIMOS 3.4 on Pseudo M-PSI / PIMOS 3.4 on Pseudo
   PIM-M / PIMOS 3.45 on PIM-M or PIM-P", disk "SIMPOS File: 14 mega bytes".
   (READ: archive unpacked and inspected.)
4. **Storage on PIM had three interchangeable back ends**, chosen by a
   prefix on the file name (READ: `src/flm/io.kl1` in the archive):
   - `fep:` (and the default with no prefix) -- pages go through a PIMOS
     *string_io* device to an ESP class on the PSI front end, which keeps
     them in an ordinary SIMPOS binary file. Eight operations in total.
   - `scsi:` -- raw blocks on a SCSI disk attached to a PIM cluster, through
     PIMOS's `scsi_request` / `direct_access` device, with Kappa-P doing its
     own extent allocation from a static table.
   - `pimos:` -- the PIMOS internal file system (`request(pimos_file, ...)`).
5. **Most relevant fact for a PIM/m + PIMOS reconstruction**: the default
   back end needs *no disk on the PIM at all* -- only a front-end string_io
   endpoint that implements eight page-file operations (161 lines of ESP in
   the original). The SCSI back end needs exactly three SCSI commands:
   `read_capacity`, `read`, `write` (that is what Kappa-P itself sends; the
   PIMOS SCSI BIOS underneath sends its own commands when it configures and
   opens the unit). The third back end depends on a PIMOS file-system
   request, `pimos_file`, whose server is not in the released PIMOS source
   (section 6.4).
6. **No measured Kappa-P-on-PIM performance was found.** The FGCS'92 paper
   gives none; the only quantitative statements are "at least three times"
   (main-memory vs secondary-storage relations) and, for the later KLIC
   port, "almost half that of an experimental [relational] DBMS" on the
   Wisconsin benchmark. No source read names the PIM model on which any
   Kappa-P measurement was taken.
7. **Quixote as released does not call Kappa-P.** FGCS'92 text says Quixote
   is "implemented on top of" Kappa-P; the IFS Quixote Ver.III source
   contains no call to Kappa-P's interface process, and its persistence
   manager defaults to `null` (section 4.2). This is a contradiction between
   the papers and the surviving code, recorded in section 8.

## 1. Table of systems

| System | Years | Host | Language | Data model | Surviving artefacts |
|---|---|---|---|---|---|
| Delta | 1982-85 | dedicated hardware (4 RDBEs, hierarchical memory), back end to PSI over LAN | firmware + control software on 16-bit CPUs | relational, attribute-wise storage | papers only: TR-074, TR-089, TR-053, TR-063, TR-064, TM-121, FGCS'84 pp. 419, 427 (all downloadable) |
| RBU / unification engine | 1985-88 | proposed hardware, simulated | -- | "relational knowledge base": relations of terms | papers only: TR-141, TR-158, TR-240, TR-284, TR-311 |
| Mu-X | 1985-89 | 8 x MC68020 + multiport page memory, at Toshiba, on PSI-Net | dedicated management software | term relational model | papers only: TR-384, TR-422, TM-830 |
| PHI | 1985-91 | PSI / SIMPOS, distributed | ESP | deductive (Datalog with negation) over relational | papers only: TR-716, TR-280, TM-174, TM-292. Not in the IFS catalogue. |
| Kappa-I | 1985-87 | PSI-I / SIMPOS | ESP (60 thousand lines) | nested relational | papers only |
| Kappa-II | 1987-89 | PSI-II / SIMPOS | ESP (180 thousand lines) | nested relational + term type | **source**: IFS 12, four archives, 25.9 MB compressed |
| CRL / DO-1 | 1988-89 | PSI, on Kappa-II | ESP | deductive language for nested relations | papers only (TR-334) |
| Kappa-P | 1989-94 | PIM / Multi-PSI / pseudo-PIM, PIMOS 3.4-3.45 | KL1 (+ a little ESP on the FEP) | nested relational + term type | **source**: IFS 13, 1.9 MB compressed, Japanese manual |
| Quixote | 1990-95 | server on PIM/PIMOS in KL1; client on UNIX | KL1, ESP, C, Emacs Lisp | deductive object-oriented (DOOD) | **source**: IFS 11 (PIMOS), 79 (KLIC), 80 (micro-Quixote, C) |
| Kappa (KLIC) | 1994-99 | UNIX + KLIC | KL1 + C | nested relational | **source**: IFS 87, with English manual |
| Helios | 1993-95 | UNIX | C | heterogeneous distributed agents wrapping DBs and solvers | **source**: IFS 89 |
| PIMOS pool / Distributed Pool | 1988-95 | PIMOS; D-Pool also KLIC | KL1 | keyed in-memory tables | **source**: in PIMOS (IFS 4); D-Pool IFS 86 |

Dates: Kappa-I/II/P and PHI from Yokota and Yasukawa, FGCS'92 appendix
(READ); Delta from TR-074 (READ, OCR); Mu-X from TR-384/TR-422 (READ, OCR).

## 2. Scope 1 -- database machines of the initial and intermediate stages

### 2.1 Delta (1982-85)

Source: N. Miyazaki, T. Kakuta, S. Shibayama, H. Yokota, K. Murakami, "An
Overview of Relational Database Machine Delta", ICOT TR-074, August 1984,
`MUSEUM/TRTM/TR/TRpdf/tr0074.pdf`. READ (OCR; the 128 MB figure
image-checked).

- Purpose, quoted: "First, Delta will be used to study the construction of
  knowledge base machines. For a logic programming environment, the
  relational database machine is considered to be the first step toward
  knowledge base machines. Second, the machine will be used as a software
  development tool, along with PSIs, for the intermediate stage".
- Architecture: five functional units -- Interface Processor (IP), Control
  Processor (CP), Relational Database Engines (RDBE), Hierarchical Memory
  (HM), Maintenance Processor (MP) -- "a loosely-coupled,
  functionally-distributed multiprocessor".
- RDBE: "a relational database engine (RDBE) based on a pipelined merge-sort
  algorithm"; all relational operations are done on sorted streams. "Delta
  has four RDBEs, which can be used in parallel." The engine core is "an
  IN-module, a sorter, and a merger"; the sorter "consists of 12 sorting
  cells used in pipelined fashion"; capacity "either 64 K Bytes or 4 K
  (2**12) items", repeated under CPU control for larger inputs.
- Hierarchical memory: a semiconductor "database memory unit (DMU)" over
  moving-head disks. "The size of this DMU is 128 MB, and the total capacity
  of the MHDs is about 20 GB." The DMU is split into a buffer (work) area
  and a disk-cache area with "the write-after strategy"; battery back-up;
  "A Shadow-page mechanism ... and logs are also supported in HM to be used
  for transaction roll-back and data recovery."
- Storage schema: attribute-based ("it splits a relation into a collection
  of attributes and separately stores individual attributes", each value
  with a tuple identifier), with a two-level index.
- Interfaces: HM to other units "a kind of I/O interface with maximum
  transfer rate of about 3 MB per second"; control over "the IEEE488
  standard bus, which connects units other than HM to each other"
  (image-checked).
- Status at the time of writing: "Part of its hardware, along with 5 GB of
  storage, was installed at ICOT in April 1984 ... we expect Delta to be
  fully operational by March 1985."

**How PSI/SIMPOS talked to it** (same source): "Delta acts as a database
server to a number of PSIs ... in a local network (LAN)"; "A faster direct
interface is also available for experimentation with PSI." Requests are in
a relational-algebra "Delta access language" using attribute numbers;
"requests expressed in user-level query languages are compiled into the
Delta access language by the host". Because Delta "will have to serve
several dozen high performance PSIs ... some high-level functions are not
implemented in Delta; some of them will be incorporated in PSI's software"
(views, security, predefined requests, least-fixed-point operations are
listed as not supported). I did not find a description of the SIMPOS-side
software that did this (section 9).

**Performance.** H. Sakai, K. Iwata, M. Abe, S. Shibayama, H. Itoh,
"Development of Delta as a First Step to a Knowledge Base Machine", ICOT
TM-121, July 1985, `MUSEUM/TRTM/TM/TMpdf/tm0121.pdf`. READ (OCR, not
image-checked): the sorter's time is given as a formula in the transfer
period T, "currently 3 Mbyte/sec", with the example "4096 tuples of 16
bytes are sorted in 43 milliseconds"; HM "Access Time 8 msec (Typ.)",
"Transfer Rate (to RDBE) 3 Mbyte/sec". The memo says only primitive
operations had been measured at that date. TR-295 / TM-300 (F. Itoh et al.,
"Design, Implementation, and Evaluation of a Relational Database Engine for
Variable Length Records", 1987) is not a Delta evaluation: its abstract
(READ, OCR) describes a later engine, again built round "a pipeline two-way
merge sorter", that handles variable-length records and reads "directly
from disk"; body not read. I found no whole-machine Delta benchmark.

**Verdict by ICOT itself.** S. Shibayama et al., "Overview of Knowledge Base
Mechanism", ICOT TR-422, October 1988 (= FGCS'88 pp. 197ff),
`MUSEUM/TRTM/TR/TRpdf/tr0422.pdf`, READ (OCR): "Though Delta was
operational, it was recognized that the strict relational model adopted in
Delta was not sufficient for the basis of the further knowledge base
machine research ... The modification of Delta's software was considered to
be difficult because of the large amount of software." Yokota and Yasukawa,
FGCS'92 p. 110 footnote 15, READ: "At the initial stage of the FGCS project,
there were other projects for databases and knowledge-based: Delta and
Kaiser, however these were used for targets other than databases and
knowledge-bases." (I found nothing further on "Kaiser".)

### 2.2 The knowledge base machine line: RBU, the unification engine, Mu-X

- **Relational knowledge base and RBU.** Y. Morita, H. Yokota, K. Nishida,
  H. Itoh, "Retrieval-By-Unification Operation on a Relational Knowledge
  Base Model", ICOT TR-158, February 1986,
  `MUSEUM/TRTM/TR/TRpdf/tr0158.pdf`. READ (OCR, abstract and introduction):
  "knowledge is represented by term relations. Terms in the term relations
  are retrieved with operation called RBUs (i.e., unification-join and
  unification-restriction)"; done naively, "all possible pairs of tuples
  ... should be checked", so the paper orders terms to prune pairs and
  proposes "the unification engine (UE), that is, hardware dedicated to the
  RBU operations". The model itself is TR-141 (H. Yokota et al., "A Model
  and an Architecture for a Relational Knowledge Base", 1985) -- ABSTRACT.
- **Unification engine evaluation.** Y. Morita et al., "Performance
  Evaluation of a Unification Engine for a Knowledge Base Machine", ICOT
  TR-240, 1987. READ (OCR, abstract): a pipeline unifier fed by two input
  streams; two pipeline methods compared *by simulator*; "The MAM method
  which applies the most general unifier at the end of a unification is
  proven to outperform the SAM method."
- **MPPM machine, simulated.** H. Monoi et al., "Parallel Control Technique
  and Performance of an MPPM Knowledge Base Machine", ICOT TR-284, 1987.
  READ (OCR, abstract): "performance evaluations by simulation for the
  knowledge base machine (KBM) using the multiport page-memory (MPPM) and
  unification engine (UE)".
- **Superimposed code words** (indexing terms for RBU): TR-259, TR-293
  (M. Wada et al., 1987), TR-347 (A. Nakase et al., 1988), TR-383
  (Y. Morita et al., "An Indexing Scheme for Terms Using Structural
  Superimposed Code Words", 1988), TR-401 (H. Yokota et al., "Term Indexing
  for Retrieval by Unification", 1988). All ABSTRACT (titles from the TR
  list); none read.
- **Mu-X, the machine actually built.** H. Sakai, S. Shibayama, A. Nakase,
  H. Monoi, Y. Morita, H. Itoh, "The Design and Implementation of a
  Knowledge Base Machine Mu-X", ICOT TR-384, May 1988; and TR-422 above.
  READ (OCR; the hardware table image-checked). Hardware table (TR-422
  Table 1): "PE count 8; PE processor MC68020 at 12.5MHz; Local memory
  2MB/PE; Shared memory 2MB; Multiport page-memory 8 ports, 64MB with
  512-byte pages, 5MB/sec/port transfer speed", disk "47MB, formatted" per
  PE. TR-384: "a software-oriented multiprocessor system with hybrid shared
  memory systems"; the data model is "the term relational model ... adopted
  so as to hold a term as an attribute value"; "The logical interface to a
  host machine PSI is also represented in term structure". Connection:
  "Mu-X is connected to the PSI-Net. Mu-X is located at the Toshiba Research
  and Development Center in Kawasaki ... connected to ICOT's local PSI-Net
  via gateways". Note that Mu-X as built is a software database machine: the
  dedicated unification engine stayed in simulation in everything I read.
  TR-422 gives a preliminary timing table (a query at 1/2/4/8 PEs, e.g.
  "197ms | 110ms | 68ms | 49ms" for query 1) -- READ (OCR, not
  image-checked; treat the digits as unverified).
- A KL1-based variant: TR-292 / TM-384, "Knowledge Base Machine Based on
  Parallel Kernel Language" (Takewaki / Itoh, 1987) and TR-214, "A Deductive
  Database System Written in Guarded Horn Clauses" (Mitomo et al., 1986) --
  ABSTRACT. These are the earliest database-in-GHC titles I saw and the
  conceptual ancestor of doing the database in KL1.

### 2.3 PHI (distributed deductive database on PSI)

Source: H. Haniuda, Y. Abiru, N. Miyazaki, "PHI: A Deductive Database
System", ICOT TR-716, December 1991, `MUSEUM/TRTM/TR/TRpdf/tr0716.pdf`.
READ (OCR). "PHI is an experimental distributed deductive database system
... implemented on Personal Sequential Inference Machines (PSI) ... The
design of PHI started in 1985 and it has been operational since 1988."
Two layers: a Knowledge Management Layer that extracts rules and compiles
goal + rules to extended relational algebra, and a Database Management
Layer, "essentially a relational database management system with some
extensions for the iterative processing". "The query language of PHI is
Prolog without function symbols, that is Datalog with negation", evaluated
bottom-up; optimisation by Horn-clause transformation (HCT/P partial
evaluation, HCT/S substitution, HCT/R restrictors, "a generalization of
magic sets"). Applications reach it through "an embedded interface in
Extended Self-contained Prolog (ESP)". Distributed query processing in PHI
is TR-280 and TM-292 (Japanese) -- ABSTRACT. Yokota and Yasukawa (FGCS'92
appendix, READ) add that Oki Electric cooperated and that the follow-on
was called DO-phi.

## 3. Scope 2 -- Kappa

### 3.1 Kappa-I and Kappa-II (PSI / SIMPOS)

Source: K. Yokota and H. Yasukawa, "Towards an Integrated Knowledge-Base
Management System: Overview of R&D on Databases and Knowledge-Bases in the
FGCS Project", FGCS'92 vol. 1 pp. 89-112, appendix a. READ.

- Kappa = "knowledge application oriented advanced database management
  system". The project "begun in September, 1985". First targets: "a
  database with electronic dictionaries including concept taxonomy for
  natural language processing systems and a database for mathematical
  knowledge for a proof checking system called CAP-LA"; "each dictionary has
  a few hundred thousands entries, each of which has a complex data
  structure. We considered that the normal relational model could not cope
  with such data and decided to adopt a nested relational model", plus "a
  new type term for handling mathematical knowledge".
- Kappa-I: "consisting of 60 thousands lines in ESP, was completed in the
  spring of 1987".
- Kappa-II: started April 1987; adds "a main memory database facility,
  extended relational algebra, user-definable command facility, and
  user-friendly window interface. The system, consisting of 180 thousand
  lines in ESP, works 10 times more efficiently in PSI-II machines than
  Kappa-I does in PSI-I. The project was over in March, 1989 and the system
  was widely released ... mainly for genetic information processing."
- The FGCS'88 paper is K. Yokota, M. Kawamura, A. Kanaegami, "Overview of
  the Knowledge Base Management System (KAPPA)", FGCS'88 vol. 1 p. 252,
  `MUSEUM/FGCS/FGCS88en-proc1/88eIRT-4.pdf` (1.8 MB, HTTP 200) --
  ABSTRACT, not read.

### 3.2 Kappa-P (PIM / PIMOS)

Primary sources:

- [K92] M. Kawamura, H. Sato, K. Naganuma, K. Yokota, "Parallel Database
  Management System: Kappa-P", FGCS'92 vol. 1 pp. 248-256. READ in full.
- [YY92] Yokota and Yasukawa, as above, section 3. READ.
- [SRC] IFS package 13, `IFS/kbms-clp/pimos/kappa-p.tar.Z`. READ (unpacked;
  SHA-256 `8a0d53c9fc8a80c6fc9fe30e494730e0110346e98fe3f27805432a62cb525c34`).
- [TM1266] M. Kawamura, "Parallel Database Management System: Kappa-P" (in
  Japanese), ICOT TM-1266, May 1993. READ (OCR, Japanese; skimmed).
- [K94] M. Kawamura and T. Kawamura, "Parallel Database Management System:
  Kappa", FGCS'94 pp. 100-105, `MUSEUM/FGCS94/PS/kappa.ps.gz`. READ in full
  (PostScript converted to text). ICOT TR-897 (November 1994, the ILPS'94
  workshop version, READ by OCR) is a shorter variant of the same paper; its
  conclusion does not contain the Wisconsin-benchmark sentence quoted below.

**Data model.** Nested relations in which "a set constructor is used only as
an abbreviation for a set of normal relations": `{r[l1=a, l2={b1,...,bn}]}`
means `{r[l1=a,l2=b1], ..., r[l1=a,l2=bn]}`. "The reason why we take such
semantics is to retain the first order semantics for efficient processing
and to remain compatible with widely used relational model." Consequence:
a row-nest of `{r[l1=a,l2={b,c}], r[l1=a,l2={c,d}]}` gives
`{r[l1=a,l2={b,c,d}]}` (as in Verso), not a set of sets (as in DASDBS and
AIM-P). Because representation is then not unique, "each nested relation
has a sequence of attributes to be nested". Query evaluation needs two
extensions to unification, "residue goals" and "binding as constraint"
[K92 section 4]. Data types beyond atoms: *term* ("the equality must be
based on unification or matching"), and separate one-byte and two-byte
character types -- "The character code of the PIM machine is based on
2-byte code, but the code wastes secondary memory space" [K92]; "It
contributes to the compression of huge amounts of data such as genetic
sequence data" [YY92].

**Architecture.** "Kappa-P is constructed of a collection of element DBMSs
located in clusters." Three roles [K92 section 3, Figure 1; YY92 section
3.3]:

- *Interface process* (I/F process): "dynamically created by a user
  program, mediates between a user program and (server or local) DBMSs by
  streams". In the source this is `ifp:create(Command_level, Log_switch,
  ^IFP, ^Status)` ([SRC] `doc/kappaP.doc`, and Figure 3 of [K92]:
  `ifp:create(pc, off, IFP, Status0)`).
- *Server DBMS*: holds "the global map of relations"; "Server DBMSs manage
  not only global map but also ordinary relations." The map is the only
  replicated relation, "replicated with a voting protocol"; [K94] names it
  "the weighted voting protocol". The sample start-up file sets
  `voting_num({1,1}). % {Read,Write}`.
- *Local DBMS*: "can be considered as a single nested relational DBMS,
  corresponding to Kappa-II, where users' data is stored".

Each element DBMS in the source is a stack of modules. The directory names
in [SRC] `src/` (my reading of the names and file headers, not a statement
from a paper): `ifp` interface process, `srv`/`svm` server and server
manager, `trp` transaction (with `trp_coord`, `trp_subtran`, `trp_recove`),
`dbm` database manager with `dbm_lock`, `tbm`/`tbp` table manager and table
processing, `rec`/`rcm`/`rcp` record layer (with `rcp_commit`), `ixp`
index, `mixp`/`mrp`/`imu` the main-memory counterparts, `bfm` buffer
manager (`bfm_swap`, `bfm_durab`), `flm` file manager, `clm` command log,
`ilp` the extended relational algebra (join, project, union, hash, sort,
nest, ...), `set` set operations on tuple identifiers, `luu` load/unload,
`mop` manipulator (operator console), `emu` Kappa-II emulation.

**Placement and parallelism** [K92 sections 5, 7, 8].

- Between clusters: *distribution* (whole relations placed on different
  element DBMSs), *horizontal partition* ("logically one relation, but
  consists of some sub-relations"), *replication* ("Only the global map ...
  is replicated ... in the current implementation"). "A database designer
  should be responsible for distribution of relations."
- Within a cluster: "Kappa-P uses parallel processing on a shared memory
  only, but doesn't use parallel operations for secondary memory in element
  DBMSs, in the current implementation." Queries become process networks:
  "The nodes become processes, and arcs become streams through which tuples
  are sent ... it is very important to control the number of tuples, and to
  drive the streams on demand with double buffering." Sets of tuple
  identifiers are "partitioned according to the range of tuple identifiers".
- Application code inside the DBMS: "a tuple filter [is] taken as the
  argument of a read operation. The read operation invocates the filter in
  the same cluster in which a relation exists."
- In the source, placement is by the KL1 pragma `@node(Node)` (17
  occurrences in [SRC]; `@priority` 6); the start-up file binds each LDBMS
  to a node: `ldbms("LDBMS000") :- node(0), ...`,
  `ldbms("LDBMS001") :- node(001), ...`.

**Query languages** [K92 section 7]: "primitive commands" (record-identifier
level; `search_index`, `search_data`, `read_record`, `add_record`, ... in
[SRC] `doc/kappaP.doc`) and "KQL, a query language based on extended
relational algebra", "syntactically similar to KL1", compiled by the
interface process into per-DBMS sub-queries: "Each sub-sequence is
translated into KL1 program with procedures calling intermediate
operations." Results come back as a demand-driven "tuple stream which
does not have cursors as SQL". A compatibility layer exists because "The
PIM machine is used via PSI machines acting as front-end processors ...
Kappa-P provides a program interface compatible to Kappa-II's primitive
commands" (the `emu` directory).

**Indexing.** Disk indexes are B-trees ([K94]: "getting B-tree components
from strings"; [SRC] `src/ixp/{node,leaf,page,...}.kl1`). Main-memory
("temporary") relations use T-trees: "Index structure of temporary
relations is T-tree[5], which is more sufficient in main memory than
B-tree", with leaf nodes deliberately *not* chained so that a range scan is
two parallel descents ("The number of comparison is 2H") instead of a
sequential walk [K92 section 8]. Indexes may hold derived values: "The
value in the entry can be the result of string operations such as substring
and concatenation of the original values, or a result extracted by a user's
program" [YY92] -- built for motif search over sequences.

**Transactions, concurrency, recovery.**

- "The query is processed as a distributed transaction among relevant
  element DBMSs, and is finished under the control of two phase commitment
  protocol." [K92]
- Locking is at table level and declared up front: [K94] "The specified
  nested relations are locked exclusively or not exclusively"; [SRC]
  `doc/kappaP.doc`: `begin_transaction(Table_info_list, LDBMS_info_list,
  ^Status)` with `Lock_mode ::= exclusive | read_only`, plus
  `end_transaction` and `roll_back`.
- Recovery: each LDBMS has a recovery log file and a command log. [SRC]
  `src/mop/startup.`: `recovery_file(">sys>kappaP>LG000")`,
  `command_log_table('CLM_Table')`; `src/dbi/database.init`:
  `log([{375,4}])`; modules `svm_recove.kl1`, `trp_recove.kl1`,
  `bfm_durab.kl1`. I did not read the recovery algorithm itself.
- "Quasi main memory" relations: "a pair of a secondary memory relation and
  a temporary relation ... Operations except for update operations can be
  executed by the temporary relation ... synchronization is achieved by two
  phase commitment protocol" [K92 section 8].

**Storage layout** ([SRC]; this is the part no paper describes).

- Page size 4096 bytes (`page_size(4096).` in `database.init`; the SCSI
  macro file has `file_info#page_size => 4096`).
- Each LDBMS owns five areas, each one file: control area, index area,
  record area, overflow area, recovery log. Sample (`src/mop/startup.`):
  `control_area_file(">sys>kappaP>CA000")`,
  `index_area_file(">sys>kappaP>IA000")`,
  `record_area_file(">sys>kappaP>RA000")`,
  `overflow_area_file(">sys>kappaP>OA000")`,
  `recovery_file(">sys>kappaP>LG000")`. Sample sizes in pages
  (`database.init`): `control(500), index(1000), record(1000),
  overflow(100)`.
- Buffer manager parameters: `bfm_max_buffer(100)`,
  `bfm_lru_table_info(64,33)`, `bfm_lru_priority(2)`.
- "a nested tuple is compressed without decomposition and stored on the
  same page, in principle ... For a huge tuple, such as a genetic sequence,
  contiguous pages are used"; an "address translation table between an ntid
  and a logical page (lp), and between a logical page and a physical page
  (pp)" [YY92 section 3.2].

**The three storage back ends** ([SRC] `src/flm/`). `io.kl1` dispatches on a
prefix of the file name: `"fep"` -> `kappa_file_io_simpos`, `"scsi"` ->
`kappa_file_io_scsi`, `"pimos"` -> `kappa_file_io_pimos`, and anything else
-> `kappa_file_io_simpos`. All three present the same stream interface to
the layers above: `read(LPN, ^Str, ^Stat)`, `write(LPN, Str, ^Stat)`,
`sync`, `get_size`, `expand`, `expand_and_fill`, `get_page_size`,
`set_page_size`, `close`.

1. *Front-end (SIMPOS) file* -- `io_simpos.kl1` (dated 1990-12, the oldest)
   plus `io.esp` on the PSI. KL1 side: `shoen:raise(pimos_tag#task,
   general_request, GRD), GRD = [string_io(StrIo)]`, then
   `StrIo = [create(string#"kappaP##kappa_file_io", StrIo2)]`, then messages
   `io(N, ToFep, FromFep)` with N = 1 open, 2 close, 3 write, 4 read, 5
   sync, 7 expand, 8 expand-and-fill (6 is get-size on the ESP side). ESP
   side: `class kappa_file_io has nature pimfep##as_pimos_string_io_device`,
   backed by a SIMPOS `#binary_file`, default page size 4096. This is the
   configuration the README's "Disk: SIMPOS File: 14 mega bytes" refers to.
2. *Raw SCSI disk on the PIM* -- `io_scsi.kl1` ("Interface program for SCSI
   Dummy FILE system", 1992-04; last entry "'93.6.23 for pimp debug").
   It obtains the device with
   `GRD = [request(scsi_request, _Cancel, normal(SCSIRequest))]`,
   `SCSIRequest = [direct_access({Cluster,Processor,SCSI_PORT}, Unit, LUN,
   Stat)]`, then issues only `read_capacity(0,0,0,Capacity)`,
   `read(Block, Length, Buffer, Status)` and
   `write(Block, Length, Buffer, Status)`, each retried up to ten times.
   Block address = `((StartPage+LPN)*PageSize)/DiskBlkSize`. There is no
   file system: `file_info_scsi.kl1` maps a file name of the form
   `..<area><PE#>` (areas `CA`, `IA`, `RA`, `OA`, `LG`; three-digit PE
   number) to a `{StartPage, FileSize, PageSize}` extent using a static
   table, overridable through the task environment variable
   `kappa:scsi_file_info`. `sync`, `expand` and `set_page_size` are no-ops
   here. A comment records the development machine's disks:
   "`icpsi589 {{0,0,0},2,0} Capacity: 1312343 bkl 512 byte/block`", i.e.
   about 672 MB per unit (my arithmetic), "164042 page"; the commented-out
   table spreads LDBMSs for PE numbers 0..59 over SCSI descriptors
   `{32,0,0}`, `{34,0,0}`, `{36,0,0}`, `{38,0,0}`. I cannot tell from the
   file which PIM model `icpsi589` fronted.
3. *PIMOS internal file system* -- `io_pimos.kl1`:
   `request(pimos_file, _, normal(ToUser))`,
   `ToUser = [create(LVN, FileNo, 511, _), open(LVN, FileNo,
   normal([file_size(...) | FileProc]))]`, i.e. files named by logical
   volume number and file number. `file_info_pimos.kl1` derives them from
   the configured name: for a name ending `...<V>>CA000` the character
   before `>` is the logical volume (interned as a one-character atom,
   `'0'`..`'9'`, `'a'`..`'m'`, `'A'`..`'M'`), and
   `FileNum := (LDBMS*5) + Area` with areas CA=0, IA=1, RA=2, OA=3, LG=4.
   So Kappa-P used this file system as numbered flat files per volume, not
   through path names. [K92] says of this: "The system uses the
   PIMOS file system, a part of which is designed for Kappa-P. The file
   system provides efficient access to large files, mirrored disks, and the
   sync mechanism for each file."

**Which disks.** [K92]: "PIM-p is a hybrid MIMD multi-processor machine ...
Disks can be connected to each cluster directly." [TM1266] (Japanese, OCR):
clusters of about ten PEs on a shared bus, several hundred megabytes of
shared memory per cluster, a disk attachable to each cluster. The SCSI
descriptor is `{Cluster, Processor, SCSI_PORT}` plus unit and LUN ([SRC],
and the PIMOS protocol file `scsi.prt`: `scsi_descriptor =
vector([node,pe,port])`).

**Measured performance -- what exists.**

- [K92]: none. Only "Compared both systems on the same machine, Kappa-P
  works with almost the same efficiency as Kappa-II. Kappa-P is expected to
  work on PIM more efficiently than Kappa-II". "The same machine" is not
  named; given the README it is presumably a PSI running pseudo-parallel
  PIMOS, but that is my inference.
- [YY92]: "In Kappa-P, data in a main memory database are processed at
  least three times more efficiently than in a secondary storage database."
  (p. 97, image-checked.) No machine named.
- [K94], for the KLIC port, not PIM: Figure 5 plots a non-indexed
  restriction over a relation of "10,000 tuples" against buffer size "on a
  sequential version of KLIC" (execution time axis 0-10 s, suspended goals
  0-20000); and "The performance of Kappa for the Wisconsin benchmark
  program is almost half that of an experimental DBMS based on the
  relational model on the same machine".
- The FGCS'92 demonstration text
  (`MUSEUM/FGCS92Demo/TEXTE/demo075-080.txt`, READ) describes the demo as
  PIR, PDB and ProSite "stored in Kappa-P" with the "motif search program
  ... invoked from the GUI [running] in parallel as a filter in each local
  DBMS", but gives no timings.

### 3.3 Kappa on KLIC (1994-99)

[K94] READ; IFS 87 `IFS/kbms-clp/klic/kappa/kappa.tgz` READ (unpacked).
"Kappa is based on Kappa-P, modified to be suitable for parallel and/or
distributed environments on conventional machines with KLIC". Differences
stated: "To reduce the code size of the system, Kappa provides primitive
commands only" (no KQL); one-byte characters; tuple and B-tree string
packing moved to C generic objects -- "These operations are implemented
sequentially in Kappa-P written in KL1 also, because too much parallel
coding decreases performance." Storage collapses to one module,
`src/flm/io_klic.kl1`. The archive has an English manual
(`Kappa/doc/man_e/`, LaTeX) that is the best English description of the
shared design, and a sample application `irpr` ("A personnel management
system"). README environment: "Sun SparcStation 10 running SunOS 4.1.3;
SparcCenter 2000 running SunOS 5.3", disk "29 mega bytes". Copyright lines
run to 1999 (JIPDEC/AITEC).

## 4. Scope 3 -- deductive and knowledge-base layers

### 4.1 CRL, DO-1

[YY92] appendix b, READ: "CRL (complex record language) [Yokota 1988] ... a
logic programming language newly designed for treating nested relations ...
The project started in the summer of 1988 and the system, called DO-1, was
completed in November, 1989. The system works on Kappa-II. The query
processing strategy is based on methods of generalized magic sets and
semi-naive evaluation." The paper is K. Yokota, "Deductive Approach for
Nested Relations", ICOT TR-334, January 1988 -- ABSTRACT. [K92] says the
language "is further extended in QUIXOTE".

### 4.2 Quixote

- Design: H. Yasukawa, H. Tsuda, K. Yokota, "Objects, Properties, and
  Modules in QUIXOTE", FGCS'92 vol. 1 pp. 257-268 -- held locally, not read
  beyond its title for this survey (ABSTRACT). [YY92] READ: Quixote merges
  two proposals, "Juan, as an extension of CRL, and QUINT, as an extension
  of CIL"; "The QUIXOTE project was started in August, 1990. The first
  version of QUIXOTE was released to restricted users in December, 1991,
  and the second version ... at the end of March, 1992. Both versions are
  written in KL1 and work on parallel inference machines."
- Features (IFS 11 abstract page and the archive README, READ): "Object
  identity defined over extended terms (object terms); Constraints in terms
  of subsumption relation among object terms; Property inheritance among
  objects; Modularized and hierarchical knowledge bases defined by modules
  and rule inheritance between them; Queries having additional assertions
  to knowledge bases, and answers with assumed constraints."
- Released system (IFS 11, `quixote.tar.gz`, Ver.III of 1 June 1993, READ):
  "(1) Quixote client on UNIX with C, X-Window(X11R5), and GNU-Emacs, and
  (2) Quixote server on PIM/PIMOS with KL1. Both UNIX workstation (such as
  SS2) and PIM/PSI are required to run this version". Server components:
  QC constraint handler, QD data manager, QE interpreter, QS/pm persistence
  manager.
- **Kappa + Quixote integration, as claimed and as shipped.** Claimed:
  [YY92] "a parallel database management system, Kappa-P, has been
  implemented on parallel inference machines" as the engine under Quixote;
  the FGCS'92 demo text says Kappa-P "has charge of the database engine of
  this system". Shipped (READ in the archive): the persistence manager
  `src/QS/pm/pm.kl1` takes a host that is "simpos | kappa | null |
  {unix,HostNameString}"; `src/tools/qxt_init.kl1` line 236 selects
  `HostName = null`, with the `simpos`, `kappa` and `{unix,"ss151"}` lines
  commented out. The `kappa` path is an ESP class on the front end
  (`pm_kapIF.esp`, class `qf_PM_kappaIF`) whose commented includes point at
  `>sys>kappa>KP_HLCMACRO.INC` and `KP_ADDOPE.INC` -- file names that occur
  in the Kappa-II archive (`kappa2/init/KP_ADDOPE.INC`). A search of the
  Quixote source for `ifp:` (Kappa-P's entry point) finds nothing. So the
  surviving Quixote stores knowledge bases as files via the front end or
  UNIX, optionally through Kappa-II on SIMPOS; I found no code path from
  Quixote into Kappa-P.
- Later reports (ABSTRACT, titles only): TR-845 "Specific Features of
  Deductive Object-Oriented Database Language QUIXOTE" (1993), TR-889
  "Query Processing for Partial Information Databases in QUIXOTE" (1994),
  TM-1142, TM-1272, TM-1275, TM-1307 (micro-Quixote).

### 4.3 Helios and final-stage knowledge-base management

IFS 89 abstract page, READ (catalogue level, so ABSTRACT for the system):
"Helios is a system to support the construction of heterogeneous
distributed cooperative problem-solving systems by establishing message
passing between various problem solvers such as databases, constraint
solvers, etc." Agents are wrapped by a "capsule" (language CAPL) and placed
in an "environment" (language ENVL); one listed use is "constructing
VLDB/VLKB by combining existing databases/knowledge bases". UNIX, C, 0.9 MB
of source. The FGCS'94 Helios paper (`MUSEUM/FGCS94/PS/helios.ps.gz`) and
the FGCS'94 overview by Yokota (`.../PS/knowledge-base.ps.gz`) were
downloaded and converted but only searched, not read: ABSTRACT. The
FGCS'94 Quixote paper's architecture figure lists a "Persistence Manager:
interface to external DBs" with "Kappa (DB)" and "PIMOS and KLIC systems"
(seen by text search only).

## 5. Scope 4 -- how applications used databases on PIM

- **Molecular biology (the driving application).** H. Tanaka, "Integrated
  System for Protein Information Processing", FGCS'92 vol. 1 pp. 321-328,
  READ (sections 1, 4): "we are building an integrated protein knowledge
  base ... which consists of a knowledge representation language (KRL)
  QUIXOTE and a DBMS Kappa-P." Table 1 lists the public databases loaded or
  targeted (PIR 30.0, 33,989 entries; Swiss-Prot 18.0, 20,772 entries; PDB,
  688 entries, 153 Mbytes; ProSite 7.0, 508 entries; REBASE) -- OCR of a
  table, digits not image-checked. Usage pattern: "the user defined
  commands, for example, DP or BLAST, are thrown to every local DBMS, and
  they play a role of filter from local databases to their server"; "We
  have developed a character-pair based index system, especially for motif
  search ... implemented as application commands, while indexes are held in
  each local DBMS." GenBank is the motivating example in [K92] ("the length
  of sequence data ranges from a few characters to 200,000 characters").
  The Kappa-II data archives in IFS 12 hold exactly this kind of content:
  `kappa2d1.tar.Z` contains one file, `kvif/data/pir_gen01.luu` (PIR in
  Kappa load/unload form; READ, archive listed).
- **Quixote knowledge bases.** IFS 83 "Protein Motif Knowledge-Base and
  Retriever Based on QUIXOTE" (`IFS/exper-apps/pimos/qxt_motif.tar.Z`,
  READ: 12 files -- `prosite.qxt`, `prosite.dat`, `prosite.lis`,
  `qxt_init.kl1`, docs): ProSite release 9.0 motifs "represented in a
  hierarchical and multiple inheritance scheme". Machine PIM, PIMOS, KL1.
  It is data for Quixote, not a Kappa-P client.
- **Legal reasoning.** [YY92] lists "a legal reasoning system, TRIAL" as a
  DOOD application on Quixote. HELIC-II (IFS 54, "Machine: PIM, Multi-PSI;
  Language: KL1; 1.7 MB") is described on its catalogue page as a
  rule-based engine "based on the parallel theorem prover MGTP" plus a
  case-based engine; the page does not mention Kappa or Quixote, and a text
  search of the FGCS'94 HELIC-II paper for "kappa", "quixote" and
  "database" found no hits. So HELIC-II appears to keep its statutes and
  cases as KL1 data, not in a DBMS (ABSTRACT; I did not unpack the source).
  Legal databases built *in Quixote* are TR-866, TR-883, TM-1305, TM-1319
  (ABSTRACT).
- **Natural-language dictionaries and mathematical knowledge.** These were
  Kappa-I/II's original clients on PSI ([YY92] appendix, READ; [K92]
  introduction). I found no source showing a dictionary application running
  against Kappa-P on PIM.
- **MGTP.** Not a database client in anything read. Its link to the topic
  is the in-memory side: the Distributed Pool test directory ships
  `mgtp_bench.kl1`, an MGTP-style benchmark for keyed tables (READ, file
  listing only).

## 6. Scope 5 -- what PIMOS itself provided

Sources: the PIMOS release already held here (`nonlocal/pimos.tar.Z`,
`nonlocal/pimosman.tar.Z`, i.e. IFS 4), READ by unpacking in a scratch
directory; and T. Mori, M. Sato, T. Chikayama, F. Itoh, T. Sato, T. Kato,
"The Design of the PIMOS File System", FGCS'92 vol. 1 pp. 278-285, READ
(abstract, sections 1-3 and the logging section).

### 6.1 Files through the front end

The manual (`Eman/e-ioctrl.tex`, "Files and Directories") describes files
obtained from the general request device via a "file request device":
modes read/write/append, character I/O, some directory operations. These
are front-end (SIMPOS, later UNIX) files reached through the FEP. The
source has the corresponding server and BIOS modules
(`src/server/fep/file/`, `src/bios/fep_module/file_dvc.kl1`).

### 6.2 String I/O devices

`Eman/e-strio.tex`, "How to create a string I/O device on FEP": "String I/O
devices provide an interface for manipulating under PIMOS devices that are
defined by the user on an FEP using ESP"; the ESP class must inherit
`pimfep##as_pimos_string_io_device`. This is the mechanism Kappa-P's
default storage back end and Quixote's persistence manager both use.

### 6.3 SCSI from KL1

The released source contains a SCSI server (`src/server/scsi/
scsiRserver.kl1`, `scsiRfil.kl1`), BIOS drivers (`src/bios/scsi/DAM.kl1`,
`DAMC.kl1`, `SAM.kl1`, `scsi_processor.kl1`, `scsi_handler.kl1`), a
simulated disk (`src/vm/scsi_disk.kl1`) and the protocol definition
`protocol/scsi.prt`. The protocol (READ) offers `direct_access`,
`processor`, `sequential_access`, `get_info`, `configuration`; the
direct-access command set is `send_diagnostic`,
`receive_diagnostic_results`, `format_unit`, `read`, `write`,
`mode_select`, `mode_sense`, `reassign_blocks`, `start_stop_unit`,
`prevent_allow_medium_removal`, `read_capacity`, `write_and_verify`, plus
the common `inquiry` and `test_unit_ready`. `src/kernel/init/rsc_init.kl1`
registers `module#scsi_request_server, "SCSI Server"` under
`:- case(scsi)`, marked "Machine dependent part". (`pimos_binaries.md` in
this directory already records what the BIOS direct-access method sends on
the wire.) The system manual's boot
transcript includes "PE00(00) @ DC> SCSI UNITS FOUND". So raw-disk access
from user KL1, exactly as Kappa-P's `io_scsi.kl1` uses it, is in the
release.

### 6.4 The PIMOS internal file system -- described in print, not found in the release

The FGCS'92 paper describes a real on-PIM file system: multiple servers
("A processor with disks can run a server, but the processor is not
dedicated to it"), distributed block caching with Unix semantics, separate
caching schemes for data files and directories, "Logging the modifications
of directories and other essential information", "Multiple log areas",
"Buddy division of blocks", "Hierarchically organized free block maps",
and "logical volumes, each of which corresponds to one file system of
Unix". "The file system has been implemented on PIM." Kappa-P's
`io_pimos.kl1` is its client (`request(pimos_file, ...)`, files addressed
by logical volume number and file number).

What the released PIMOS source (`pimos.tar.Z`) shows, READ:

- No file contains any of `pimos_file`, `logical_volume`, `log_generation`,
  `block_generation`, `buddy`, `free_block_map`, `cylinder_group`.
- The list of servers started at boot is in
  `src/kernel/init/rsc_init.kl1`: `scsi_request_server` ("SCSI Server",
  only under `:- switch(fep_interface). :- case(scsi).`), then `fep_server`,
  `atom_server`, `module_server`, `user_server`, `pipe_server`,
  `profiling_server`, `user_server_manager` (`telnet_server` commented
  out), followed by `system_defined_servers:modules(Tail)`. That last hook,
  in `src/kernel/init/sysdef.kl1`, is `modules(List) :- true | List = [].`
  -- empty. No file-system server is registered.
- `src/server/` has directories `atom`, `fep`, `login`, `module`, `pipe`,
  `profiler`, `scsi`, `telnet`, `user` and nothing else.
- What *is* there from the file-system effort is its test scaffolding:
  `src/vm/DKS.kl1` ("PIMOS disk simulator ... a physical volume simulation
  process which receives and executes simulated i/o"), `DKSF.kl1`
  ("disk_simulator file": save and restore a simulated disk),
  `scsi_disk.kl1` (module `scsi_disk_simulator`) and `sim.kl1` (module
  `scsi_simulator`), dated February-December 1992.

The object archive (`pimosobj.tar.Z`, 34 files, 20 `.sav`) I could not
search meaningfully: a byte search for `pimos_file` in 8-bit and 16-bit
forms finds nothing, but so does the same search for names any PIMOS
must contain (`string_io`, `keyed_set`), and for `scsi_request`, so atom names
are not stored in a form that search sees. Whether the binary PIMOS
contains the file-system server is therefore **not established**; the
source release does not. TM-1254 (T. Mori, "Directory management of the
PIMOS file system", 1993, Japanese) is a further description -- ABSTRACT.

A version note: `src/kernel/init/version.kl1` in the release returns
`string#"3.600"` (other files carry "V3.0" and "V3.50" strings), while
Kappa-P asks for PIMOS 3.4 / 3.45. Whether Kappa-P compiles unchanged
against the released PIMOS is untested.

### 6.5 Pools: the in-memory keyed store

`Eman/e-util.tex`, section "Pool", READ: "PIMOS has a mechanism (pool) that
can generally store any KL1 data." Unkeyed: bag, stack, queue, sorted bag.
Keyed: keyed bag, keyed set, keyed sorted bag, keyed sorted set, and the
multiply keyed bag. "These pools are manipulated by activating a process
... and then using message communication intermediated by streams". Source:
`src/utility/pool/` (`pool.kl1`, `k_bag.kl1`, `k_set.kl1`, `ks_set.kl1`,
...). Kappa-P leans on them heavily: in [SRC] I counted 63 uses of
`pool:keyed_set`, 27 of `pool:keyed_bag`, 5 of `pool:multiply_keyed_bag`,
4 each of `pool:queue` and `pool:keyed_sorted_set`. [YY92] notes that
Kappa itself can store "list, bag, and pool" values and "supports the same
interface to such data types as in SIMPOS or PIMOS".

The pool is a single process. IFS 86, Distributed Pool
(`IFS/symbolic-proc/klic-apps/d-pool/dpool_pimos.tgz`, 226,194 bytes, READ:
83 files, 22 `.kl1`, 10,947 lines) exists because of that: "The original
pool provided by PIMOS operating system of PIMs did not run in parallel.
All the data is managed by a single process ... The distributed pool
distributes the original pool to each node, and maintains the coherence
among copies". Its `doc/` holds evaluation plots named
`dpool-pimm-int.eps`, `dpool-pimm-list.eps`, `dpool-pimm-acc.eps`,
`eval_caching_*_pimm.eps` -- by their names, measurements on PIM/m (I did
not render them).

### 6.6 Strings and vectors

Kappa-P's page I/O is done on KL1 strings: pages are 16-bit-element strings
in memory, converted with `change_element_size(Str, 8, Str8)` before a SCSI
write and back to 16 after a read; it uses `new_string`,
`builtin#substring`, `builtin#copy_string_elements`, `string_element`,
`set_vector_element`, `vector_element` ([SRC] `src/flm/io_scsi.kl1`,
`file_info_scsi.kl1`). Persistence in PIMOS is therefore only what files
and SCSI give: there is no persistent heap.

### 6.7 Other PIMOS services Kappa-P calls

Named requests through the general request device, counted over all of
[SRC]: `request(scsi_request` 3, `request(kappa_mop` 2, `request(pimos_file`
1. `kappa_mop` is Kappa-P's own: the manipulator registers itself as a
server and the tools connect to it, so PIMOS's facility for user-defined
servers (`register`, `connection`) is needed too. Other general-request
messages, counted by a pattern that only catches variables named `GR...`
and is therefore a lower bound: `timer` 15, `file` 10, `getenv` 9,
`string_io` 4, `connection` 4, `execute` 3, `register` 2, `suicide` 2,
`user` 1; one `window`. The `file` requests are front-end files: the six
tools and `dbi/dbimng.kl1` read their parameter files that way, so the
front end must serve ordinary files as well as the string_io page device.
Also `atom_table` (29 uses) and `module_table` (4). Installation needs a
PIMOS user `kappaP` and group `kappa`, and runs the operator console as
`super_pimos` ([SRC] `INSTALL`).

## 7. Scope 5 (continued) -- the IFS catalogue, database-related entries

Catalogue page: `MUSEUM/IFS/abst/ifs-catalogue.html` (100 numbered
entries), READ. Per-package pages: `MUSEUM/IFS/abst/NNN.html`, READ.
"Catalogue size" is what the page prints; "actual bytes" is the HTTP
Content-Length or the downloaded size on 2026-11-20. Directory listings
under `IFS/` return 404; only file URLs resolve.

| No. | Name | Machine / environment | Language | Catalogue "Source Code" | Archive(s) under `IFS/` | Actual bytes | Source included? |
|---|---|---|---|---|---|---|---|
| 11 | Knowledge Representation Language: QUIXOTE | Multi-PSI / PIMOS | ESP, KL1 | 3 MB | `kbms-clp/pimos/quixote.tar.gz` | 1,447,226 | Yes (unpacked: 493 files; 129 `.kl1`, 83,939 lines; 6,763 lines ESP; C and Emacs Lisp client; Japanese docs) |
| 12 | Nested Relational DBMS: Kappa-II | PSI / SIMPOS | ESP | 12 MB, "Documents: None" | `kbms-clp/simpos/kappa2.tar.Z`, `kappa2d1.tar.Z`, `kappa2d2.tar.Z`, `kappa2d3.tar.Z` | 5,710,659; 5,332,175; 4,857,043; 9,995,265 | Yes (`kappa2.tar.Z` listed, not kept: 882 entries, 602 `.ESP` + 49 `.esp`). `d1` is data: one PIR load file. `d2`, `d3` not opened. |
| 13 | Parallel DBMS: Kappa-P | PIM / PIMOS 3.45 | KL1 | 6 MB, Japanese manual | `kbms-clp/pimos/kappa-p.tar.Z` | 1,897,310 | Yes (510 files, 6,799,428 bytes unpacked; 344 `.kl1`, 151,683 lines; 7 `.esp`; 120 `.com` build scripts; 8 Japanese `.doc`) |
| 79 | QUIXOTE, KLIC version | UNIX / KLIC | KL1, C, Emacs Lisp | 6 MB | `kbms-clp/klic/bigqxt/{qxtall,qxtdoc,qxtclient,qxtserver}.tgz` (+ `README`, `INSTALL`) | `qxtall.tgz` 605,445 (others not checked) | Not opened |
| 80 | micro-QUIXOTE | UNIX, MS-DOS | C | 199 KB | `kbms-clp/unix/m-qxt.tgz` | 104,599 | Not opened |
| 86 | Distributed Pool | PIM / UNIX; PIMOS / KLIC | KL1 | 0.2 MB | `symbolic-proc/klic-apps/d-pool/{dpool_klic,dpool_pimos}.tgz` | PIMOS version 226,194 | Yes |
| 87 | Parallel DBMS: Kappa (KLIC version) | UNIX / KLIC | KL1, C | 6 MB, manual English and Japanese | `kbms-clp/klic/kappa/kappa.tgz` (+ `README`) | 764,969 | Yes (381 files; 204 `.kl1`, 84,121 lines; 32 `.c`, 15,385 lines; 28 `.tex`) |
| 89 | Helios | UNIX | C | 0.9 MB | `kbms-clp/unix/helios/helios.tgz` (+ `README`) | 3,699,824 | Not opened |
| 83 | Protein Motif Knowledge-Base and Retriever Based on QUIXOTE | PIM / PIMOS | KL1 | 280 KB | `exper-apps/pimos/qxt_motif.tar.Z` | 771,707 | Yes (data + `qxt_init.kl1`) |
| 96 | Knowledge Base of Biological Reactions | UNIX, Motif, micro-QUIXOTE | C, g++, QUIXOTE | 0.4 MB | `exper-apps/unix/pathway/pathway.tgz` | not checked | Not opened |
| 54 | HELIC-II | PIM, Multi-PSI / PIMOS | KL1 | 1.7 MB | `exper-apps/pimos/helic2.tar.Z` | 775,279 | Not opened |
| 100 | new HELIC-II | PIM / UNIX; PIMOS / UNIX, KLIC | KL1 | 20 MB | `exper-apps/klic/helic2/{cui,drs,gui}/*.tgz` | not checked | Not opened |
| 4 | PIMOS | PIM, Multi-PSI | KL1 | 5.5 MB | `symbolic-proc/pim-psi/{pimos,pimosobj,pimosman}.tar.Z`, `pimosman.ps.Z` | 2,932,865; 2,631,847; 592,865; 866,355 | Yes (held locally) |

Not in the catalogue under any name I could match: Delta, Mu-X, PHI,
Kappa-I, CRL/DO-1.

Catalogue slips worth knowing: the Kappa-II page's overview sentence reads
"Kappa-P is a database management system ..."; the catalogue link text
gives `m-qxt.tgz` as "[1,046K]" and `qxtall.tgz` as "[700K]" against
actual 104,599 and 605,445 bytes; package 11 is listed as "Machine:
Multi-PSI" while its own README says "PIM/PIMOS".

## 8. Contradictions between sources

1. **Quixote "on top of Kappa-P"** (papers, demo text) versus the released
   Quixote source, which has no Kappa-P client and defaults persistence to
   `null` (section 4.2).
2. **Kappa-P start date**: "started in February, 1989" ([YY92] appendix)
   versus "Kappa-P(1988-1994)" on the Kappa home page
   (`MUSEUM/SOFTWARE/KAPPA/hist-E.html`, SECONDARY). [K92] says "initiated
   at the beginning of the final stage".
3. **Kappa-II end date** agrees (March 1989 / "1987-1989"), but the home
   page calls Kappa-P "a translation of Kappa-II in KL1", whereas [K92]
   says it is "based on Kappa-II from a logical point of view, and its
   configuration and query processing have been extended".
4. **Which machine**: the IFS page says "Machine: PIM, Environment: PIMOS
   3.45"; the archive README adds pseudo Multi-PSI and pseudo PIM-M under
   PIMOS 3.4 and names "PIM-M or PIM-P"; [K92] argues from PIM-p's
   cluster architecture only.
5. **Parallel disk access**: a design goal in [K92] section 2 ("The system
   should provide parallel disk access") but section 8 says the current
   implementation "doesn't use parallel operations for secondary memory in
   element DBMSs".
6. **Date of TR-158**: the TR list gives 86.02 and the cover reads
   "February, 1986"; the inner title page reads "February, 1985" in my OCR
   (not image-checked).
7. **Mirrored disks and per-file sync** are attributed to the PIMOS file
   system in [K92]; the SCSI back end in the released Kappa-P makes `sync`
   a no-op and has no mirroring. Not strictly a contradiction (different
   back ends), but the durable path the paper describes is the one whose
   OS half is missing from the release.

## 9. Could not find

- **Any measured Kappa-P result on a named PIM model** (speed-up versus
  PEs or clusters, transactions per second, load times). Looked in: [K92],
  [YY92], [TM1266], [K94], the FGCS'92 demo text, the Kappa home pages
  (`hist-E`, `outline-E`, `dist-E`, `ref-E`, `ifs-E`). Web query tried:
  "Kappa-P parallel nested relational DBMS PIM/m OR PIM/p measured
  performance speedup horizontally partitioned relation motif search ICOT".
  Possibly relevant and not usable here: TM-1246 (Tsubakino et al.,
  "Parallel DBMS Kappa-P", March 1993, Japanese, two-column scan; my OCR of
  it was too poor to read, and a scan of the OCR text for seconds, ratios
  and PIM model names found nothing -- that is weak evidence of absence).
  Not opened:
  TM-1041 (Kappa retrieval and set-based record handling, 1991), reference
  [4] of [K92] (KL1 Programming Workshop '91, Japanese), and K. Taki (ed.),
  "Parallel Processing of Fifth Generation Computers", bit special volume,
  Kyoritsu 1993, section 3.8 (cited on the Kappa references page).
- **The SIMPOS-side software for Delta** (a driver, a library, or a manual
  for using Delta from ESP). Found only the machine-side description in
  TR-074. Candidates not read: FGCS'84 "Query Processing Flow on RDBM
  Delta's Functionally-Distributed Architecture" (p. 427), TR-026, TM-085
  ("Delta Demonstration at ICOT Open House", 1984). Web query tried: "ICOT
  relational database machine Delta evaluation performance PSI SIMPOS
  interface Kaiser Delta criticism Wisconsin benchmark" -- nothing on the
  interface or on "Kaiser".
- **Whole-system Delta benchmark numbers.** Only primitive RDBE/HM figures
  in TM-121. TR-295 / TM-300 turned out to be about a later engine.
  Unread candidates: TR-089 ("The Design and Implementation of Relational
  Database Machine Delta", 1984), TM-085.
- **A hardware unification engine.** Everything read evaluates it by
  simulation. Not established either way.
- **PHI source code, or any PHI entry in IFS.** Checked the catalogue's 100
  titles.
- **The PIMOS internal file system source** (`pimos_file`), see 6.4.
  Absent from the released source tree; the object archive could not be
  searched by name.
- **A natural-language dictionary or HELIC-II client of Kappa-P.** Not seen
  in any paper read; HELIC-II source not unpacked.
- **A second mirror.** Search results show a copy of the archive under
  `www.ueda.info.waseda.ac.jp/AITEC_ICOT_ARCHIVES/`; my one HEAD request
  for `kappa-p.tar.Z` there returned no status line, so its availability is
  unconfirmed.
- **An index page for the FGCS'94 proceedings** on the AIST mirror: the
  guessed name returned HTTP 500; individual paper pages (`kappa2.html`,
  `knowledge-base.html`) and the `PS/*.ps.gz` files do resolve.

## 10. What survives and where to get it

Source code (all HTTP 200 on 2026-11-20, file URLs under `IFS/`): see the
table in section 7. For this project the three that matter are
`kbms-clp/pimos/kappa-p.tar.Z`, `symbolic-proc/klic-apps/d-pool/
dpool_pimos.tgz` and `kbms-clp/klic/kappa/kappa.tgz` (for its English
manual).

Proceedings:

- FGCS'84: index `MUSEUM/FGCS/FGCS84en-proc/FGCS84en-proc.html`; Delta
  papers `84eANGC2-3.pdf` (RDBE, p. 419) and `84eANGC2-4.pdf` (query flow,
  p. 427); overview `84eR&D-2.pdf` (PIM and KBM, p. 18).
- FGCS'88: indexes `MUSEUM/FGCS/FGCS88en-proc{1,2,3}/FGCS88en-proc{1,2,3}
  .html`; `88eR&D-3.pdf` (Itoh et al., "Knowledge Base System in Logic
  Programming Paradigm", p. 37), `88eIRT-1.pdf` (Knowledge Base Mechanism,
  p. 197), `88eIRT-4.pdf` (KAPPA, p. 252), `88ePARA2-1.pdf` (unification-
  based query language for relational knowledge bases, p. 896).
- FGCS'92: both volumes held here; database papers at vol. 1 pp. 89-112,
  248-256, 257-268, 278-285, 321-328. Demo text:
  `MUSEUM/FGCS92Demo/TEXTE/demo075-080.txt`.
- FGCS'94: `MUSEUM/FGCS94/PS/{kappa,knowledge-base,quixote,helios,helic2}
  .ps.gz` (convert with Ghostscript; `quixote.ps` needs a Japanese font
  for `txtwrite` but converts through `ps2pdf`).

ICOT technical reports and memoranda: lists at
`MUSEUM/TRTM/TR/TRlist.html` and `MUSEUM/TRTM/TM/TMlist.html`; PDFs at
`MUSEUM/TRTM/TR/TRpdf/trNNNN.pdf` and `MUSEUM/TRTM/TM/TMpdf/tmNNNN.pdf`
(four digits). All are page scans without a text layer. Numbers by topic
(titles from the lists; R = read here by OCR):

- Delta: TM-002, TM-008, TR-012, TR-053, TR-063, TR-064, TR-074 (R),
  TR-089, TR-091, TM-085, TM-121 (R, part), TM-130, TR-157, TR-182,
  TR-295, TM-300.
- Relational knowledge base, RBU, unification engine, MPPM: TR-141,
  TR-149, TR-156, TR-158 (R, part), TM-178, TM-179, TM-185, TR-240 (R,
  abstract), TR-255, TR-261, TR-284 (R, abstract), TR-294, TR-311, TR-380,
  TR-381.
- Superimposed code words / term indexing: TR-259, TR-293, TR-347, TR-383,
  TR-401.
- Mu-X and KBM overviews: TR-191, TR-234, TR-292, TR-384 (R, part),
  TR-422 (R, part), TR-425, TR-435, TM-384, TM-471, TM-760, TM-830.
- PHI and deductive databases: TR-123, TR-183, TR-214, TR-280, TR-377,
  TR-407, TR-538, TR-716 (R, part), TM-174, TM-292, TM-500.
- Kappa: TM-674, TM-1041, TM-1246, TM-1266 (R, skimmed), TR-334 (CRL),
  TR-519, TR-897 (R).
- Quixote and applications: TR-601, TR-811, TR-845, TR-850, TR-866,
  TR-883, TR-889, TM-1080, TM-1113, TM-1142, TM-1272, TM-1275, TM-1279,
  TM-1305, TM-1307, TM-1316, TM-1319.
- File systems: TR-059 (SIMPOS file system), TR-524 (SIMPOS distributed
  file system), TM-1254 (PIMOS file system directory management).

## 11. Implications for a reconstructed PIM/m + PIMOS that wants to run a real ICOT application

Everything in this section is my assessment from the sources above; none
of it has been tried.

What the database software needs, in order of feasibility:

1. **PIMOS pools (already inside PIMOS).** Needs: nothing beyond a working
   PIMOS; one PE suffices. Pure KL1 in `src/utility/pool/`. This is the
   "database" most ICOT KL1 applications actually used, and a prerequisite
   for everything below (Kappa-P alone makes about a hundred pool calls).
   A natural first database-flavoured regression target.

2. **Distributed Pool (IFS 86, PIMOS version).** Needs: multi-node PIMOS
   with working inter-node goal distribution (`@node`), no I/O beyond the
   console. 10,947 lines of KL1, ships its own benchmarks (`dp_bench*.kl1`,
   `p_bench*.kl1`, `mgtp_bench*.kl1`) and, by file name, PIM/m reference
   plots to compare against. Small, self-checking, PIM/m-specific: the best
   early multi-PE target in this area.

3. **Kappa-P with the front-end file back end, one element DBMS.** Needs:
   - The PIMOS KL1 compiler running (the release is source only; build is
     `take("KL1comp.com")` from the PIMOS shell) or an equivalent
     cross-compilation path, including the `pimos` macro package and the
     Kappa macro modules (23 `.mac` files).
   - PIMOS services: `shoen:raise(pimos_tag#task, general_request, ...)`
     with `string_io`, `timer`, `file` (front-end files, for the start-up
     and `database.init` parameter files), `getenv`, `user`/group data,
     user-defined server registration and connection (Kappa-P registers
     `kappa_mop`), `atom_table`, `module_table`, pools; a registered user
     `kappaP` and group `kappa`; a `super_pimos` shell for the manipulator.
   - A front-end endpoint for the string_io device named
     `kappaP##kappa_file_io` implementing eight operations on a paged
     binary file (open/create, close, write page, read page, sync, get
     size, expand, expand-and-fill; 16-bit-element strings; default page
     4096). In the original that is 161 lines of ESP on SIMPOS; in a
     simulator it is a small host-side shim. No PSI/SIMPOS emulation is
     required for this, only fidelity to the string_io wire protocol,
     which the PIMOS manual documents (`e-strio.tex`) and the PIMOS source
     implements (`src/server/fep/string_io/`,
     `src/bios/fep_module/strioRdvc.kl1`).
   - Storage: the README says 14 MB of front-end file space; the sample
     `database.init` allocates 2,600 pages (about 10.6 MB) for the first
     LDBMS plus its log.
   - PEs: [K92] says "The smallest configuration of Kappa-P is almost the
     same as Kappa-II", and the sample start-up puts the server tables and
     one LDBMS on `node(0)`; the README lists "Pseudo PIM-M" as a supported
     host. So a single node is a documented configuration.
   - Memory: not stated anywhere I read for the minimum case. The papers
     speak of "hundreds of mega bytes" per cluster as the *opportunity*
     for main-memory relations, not as a requirement.
   - Risk: PIMOS version drift (Kappa-P wants 3.4/3.45; the released PIMOS
     reports 3.600), and 151,683 lines of KL1 is a large first application.
   - Payoff: the six programs in `src/tools/` (`create_table`,
     `add_record`, `read_record`, `read_index`, `search_record`,
     `delete_table`) are ready-made smoke tests, and the Kappa-II PIR load
     file in IFS 12 (`pir_gen01.luu`) is authentic period data in Kappa's
     own unload format (whether Kappa-P's `luu` loader reads Kappa-II
     unload files unchanged is unverified).

4. **Kappa-P with the raw SCSI back end.** Needs, beyond item 3: the PIMOS
   SCSI server path (`scsi_request` -> `direct_access({node,pe,port}, unit,
   lun, ...)`) and a simulated SCSI direct-access device. Kappa-P's own
   messages are `read_capacity`, `read` and `write`; what the PIMOS BIOS
   sends beneath them (inquiry, test-unit-ready and so on) is whatever
   `src/bios/scsi/DAM.kl1` does and was not examined here. Blocks are 512
   bytes in Kappa-P's own notes; the code takes the size from
   `read_capacity`. PIMOS also ships its own disk and SCSI simulators in
   KL1 (`src/vm/`), which are a period-authentic reference for device
   behaviour. The
   extent table comes from the task environment variable
   `kappa:scsi_file_info` or a compiled-in macro, so no file system is
   needed. This is the configuration that actually exercises PIM-attached
   disks, and it ties directly into the SCSI BIOS work in the PIMOS source
   (`src/bios/scsi/`). Per-LDBMS disk use in the developers' commented
   table is 53,600 pages (about 220 MB) for the largest entry and 3,600
   pages (about 15 MB) for the smallest; any size works because the table
   is configuration.

5. **Kappa-P across several nodes (server DBMSs + local DBMSs, horizontal
   partition, two-phase commit, voting).** Needs: item 3 or 4 on a
   multi-node PIMOS, one storage endpoint or SCSI unit per element DBMS.
   This is the configuration the FGCS'92 paper is about, and the first one
   where PIM/m's real PE count matters. No reference numbers exist to
   compare against (section 9), so the check would be behavioural, not
   quantitative.

6. **Quixote Ver.III server on PIMOS.** Needs: the KL1 server (83,939
   lines) plus a UNIX-side client speaking its protocol, or a stub for it;
   persistence can be left at the shipped default `null`. It does not need
   Kappa-P. Sample knowledge bases come with it (`sample/cider.qxt`,
   `sumo.qxt`) and with IFS 83 (ProSite motifs). More moving parts than
   Kappa-P (two machines in the original) and less tied to PIM hardware.

7. **Kappa-P on the PIMOS internal file system (`pimos:` back end).** Not
   feasible from the released source: the file-system server it calls is
   described in FGCS'92 and TM-1254, but the release registers no such
   server and its extension hook is empty (section 6.4). Unless the server
   turns out to be inside the binary `.sav` modules (not established), it
   would have to be rewritten from the paper, which is new software, not a
   replica.

8. **Kappa-II, PHI, CRL/DO-1.** Out of reach for a PIM/m reconstruction:
   they are ESP programs for PSI/SIMPOS, and SIMPOS is not available.
   Delta and Mu-X are hardware with no surviving software.

Smallest honest milestone that would deserve the phrase "runs a real ICOT
database": item 3 -- Kappa-P's manipulator starting one LDBMS on one node,
`database_initialize:initialize(...)` creating the five area files through
the string_io shim, and `tools/create_table` + `add_record` +
`read_record` round-tripping a nested tuple, with the page file on the
host inspectable afterwards.

## 12. Sources

Read (in whole or in the parts stated above):

- M. Kawamura, H. Sato, K. Naganuma, K. Yokota, "Parallel Database
  Management System: Kappa-P", Proc. FGCS'92, vol. 1, pp. 248-256.
- K. Yokota, H. Yasukawa, "Towards an Integrated Knowledge-Base Management
  System: Overview of R&D on Databases and Knowledge-Bases in the FGCS
  Project", Proc. FGCS'92, vol. 1, pp. 89-112.
- T. Mori, M. Sato, T. Chikayama, F. Itoh, T. Sato, T. Kato, "The Design of
  the PIMOS File System", Proc. FGCS'92, vol. 1, pp. 278-285.
- H. Tanaka, "Integrated System for Protein Information Processing", Proc.
  FGCS'92, vol. 1, pp. 321-328.
- M. Kawamura, T. Kawamura, "Parallel Database Management System: Kappa",
  Proc. FGCS'94, pp. 100-105, `MUSEUM/FGCS94/PS/kappa.ps.gz`; also ICOT
  TR-897, "Implementation of Parallel Database Management System on KLIC",
  November 1994, `MUSEUM/TRTM/TR/TRpdf/tr0897.pdf`.
- N. Miyazaki et al., "An Overview of Relational Database Machine Delta",
  ICOT TR-074, 1984, `.../TRpdf/tr0074.pdf`.
- H. Sakai et al., "Development of Delta as a First Step to a Knowledge
  Base Machine", ICOT TM-121, 1985, `.../TMpdf/tm0121.pdf`.
- H. Sakai et al., "The Design and Implementation of a Knowledge Base
  Machine Mu-X", ICOT TR-384, 1988, `.../TRpdf/tr0384.pdf`.
- S. Shibayama et al., "Overview of Knowledge Base Mechanism", ICOT TR-422,
  1988, `.../TRpdf/tr0422.pdf`.
- Y. Morita et al., "Retrieval-By-Unification Operation on a Relational
  Knowledge Base Model", ICOT TR-158, 1986; Y. Morita et al., TR-240, 1987;
  H. Monoi et al., TR-284, 1987 (abstracts and introductions).
- H. Haniuda, Y. Abiru, N. Miyazaki, "PHI: A Deductive Database System",
  ICOT TR-716, 1991, `.../TRpdf/tr0716.pdf`.
- M. Kawamura, "Parallel Database Management System: Kappa-P" (Japanese),
  ICOT TM-1266, 1993, `.../TMpdf/tm1266.pdf`.
- FGCS'92 demonstration text, `MUSEUM/FGCS92Demo/TEXTE/demo075-080.txt`.
- IFS catalogue and package pages 4, 11, 12, 13, 54, 79, 80, 83, 86, 87,
  89, 96, 100 under `MUSEUM/IFS/abst/`.
- Kappa home pages, `MUSEUM/SOFTWARE/KAPPA/{outline,hist,dist,ref,ifs}-E
  .html`.
- Archives unpacked: `kappa-p.tar.Z`, `kappa.tgz` (KLIC), `quixote.tar.gz`,
  `dpool_pimos.tgz`, `qxt_motif.tar.Z`; archives listed without keeping:
  `kappa2.tar.Z`, `kappa2d1.tar.Z`; held PIMOS archives `pimos.tar.Z`,
  `pimosman.tar.Z`.
- ICOT TR and TM title lists, `MUSEUM/TRTM/TR/TRlist.html`,
  `MUSEUM/TRTM/TM/TMlist.html`.

Cited from titles or catalogue entries only (not read): every TR/TM number
in section 10 not marked R; FGCS'84 pp. 18, 419, 427; FGCS'88 pp. 37, 197,
252, 896; FGCS'92 pp. 257-268 (Quixote); FGCS'94 Quixote, Helios, HELIC-II
and knowledge-base overview papers (text-searched only).
