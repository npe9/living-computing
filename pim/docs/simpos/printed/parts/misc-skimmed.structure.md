# Other held reports skimmed by F4 (tesseract eng+jpn at 200 dpi into A/work/<id>/ocr unless noted)

## TR-714 「AIワークステーションPSI/UXのアーキテクチャ」(益田嘉直 他, Nov 1991), 9 pp; p4 read by eye (35% view of 200 dpi render).
- PSI/UX = inference board (PSI-III-class CPU from the PIM/m element processor, VLSI) + UNIX workstation (MC68030/68040); SIMPOS runs on the inference part and is shown as a "SIMPOS screen" X window on UNIX; windows, mouse and keyboard inside it handled by SIMPOS (p4).
- Fig. 2 「SIMPOSの内部構造」 (p4): PSI-II: application / PS / I/O subsystem (B) / kernel = process, memory, I/O (A). PSI/UX: same, but (A) SIMPOS kernel I/O handlers and (B) part of the I/O subsystem replaced by "UNIXの機能でエミュレート". Fixed disk, window, network sockets all under UNIX; PS and applications keep object-code compatibility. Communication via shared interface memory (128 KB on VME) with control info + interrupt. REIMPLEMENTABLE insight: the I/O handler layer is the porting seam.
## TM-444 「小型化PSIにおける論理型言語KL0の処理系実装方式」(中島克人, Jan 1988), 36 pp (OCR only)
- PSI-II firmware: "System Area" also used as GC work area; **SIMPOS process control blocks (PCB) are placed in the System Area, which is extended when a process is created** (p35 OCR). Firmware supports ESP method call and slot access, exception-based fast trace, mark-compaction GC, bind_hook, on_backtrack, remote cuts, SIMPOS process switching (p35 OCR).
## TR-142 Evaluation of PSI Micro-Interpreter (1985), 6 pp: firmware includes 1.5 Kw garbage collector and 2.0 Kw "SIMPOS support functions" (p3 OCR).
## TM-661 PSI-II instruction-set evaluation (1989): static/dynamic instruction frequencies of SIMPOS 3.2 / 4.2 compiled code (p7-9 OCR); versions named.
## TM-104 if-then-else in KL0 (1985): benchmark includes "SIMPOS process interrupt control part" (p2 OCR).
## TM-128 知識情報処理用ワークステーションの研究開発 (内田俊一, 1985): SIMPOS overview, window screenshot (OCR); no listing.
## TM-055 Unique Features of ESP (1984), TM-075 ESP (1984), TM-053 OO parser in ESP: language examples (door/with_a_lock); no SIMPOS classes beyond mention.
## TR-237, TR-265, TR-483, TM-696, TM-306: mention SIMPOS/ESP as host of Multi-PSI tools or PIMOS front end (FEP on SIMPOS written in ESP, TM-696 p5 OCR); no SIMPOS internals.
## No SIMPOS content found (OCR): TR-005, TR-013, TR-014, TR-045, TR-052, TR-075, TR-079, TR-112, TR-219, TR-236, TR-274, TR-439, TR-469, TR-563, TR-585, TR-715, TM-001, TM-005, TM-224 (Japanese; OCR found no "SIMPOS" -- not eyed, may be OCR failure), TM-299, TM-392, TM-426, TM-734, TM-859, TM-1203, TM-1254. Not processed: TM-305 (81 pp Multi-PSI benchmarks), TM-399 (115 pp workshop), TM-161 (assembler port; prior notes: class work p15-16).
