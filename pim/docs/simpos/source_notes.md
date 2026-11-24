<!-- The working notes of the 2026-11-23 SIMPOS-only search (a delegated
agent), kept as written: page numbers are PDF page indices of the
scans, not printed folios. "Opened" pages were read; "located" pages
were found by a class/method pattern only. Summary and status:
../psi_acquisition.md section 9. class_census.tsv and trtm_table.tsv in
this directory are that search's outputs. -->

# SIMPOS search notes (2026-11-23) -- page numbers are PDF page indices (p-NN of the render), not printed folios

## Source text of SIMPOS printed in reports (OCR'd at 200 dpi, tesseract eng+jpn; read by eye on the cited pages)
- TR-046 pp26-28: ESP source of class default_translation_table (coordinator key bindings: kill/lull/arouse/status/visit/memorize/broadcast/remember/system menu/whiteboard) and class system_menu (p27).
- TR-061 p13: same default_translation_table listing (Coordinator).
- TM-100 pp4-17: SIMPOS supervisor in ESP: class object (p4), class process with full attribute list (context, priority, sub_priority, mask_count, suspend_reason(s), status dormant/suspended/ready, parent/children, invocation_stack, resources, world, user, interpreter_instance, process_clock) and :create/:create_core (p7-8); as_program (:goal/:assign/:resign/:invoke) p11; parrot example p10; interrupt_process p12; channel p15; bounded_channel p17.
- TR-056 (Supervisor concepts): stream/semaphore/event ESP p13; global environments, library and directory class slots (:root(#directory,R)) p20-22.
- TR-059 (File system concepts): buffer/file marker method interfaces p10-12; as_permanent_object :store/:restore ESP code p22.
- TR-524 (Distributed file system) pp37-38 Appendix A "Class Definitions": binary_file (nature remote_binary_file, binary_file_accessor, local_binary_file, p_binary_file, logical_file, with_retrieval), local_binary_file, logical_file/logical_object, binary_file_accessor, file_accessor -- real ESP method bodies (:g_call/:l_call/:r_call/:x_call ROAM protocol, p21).
- TR-283 (ROAM) pp6-12,19: remote object access mechanism, GOIDs, export/import tables per process, test class p19.
- TM-065 pp12-16: class file (p12), binary_file (p13), bare_window, with_border, with_label, as_label, window_with_border_and_label (p15-16) -- ESP class skeletons with before/after demons.
- TM-125 pp14-25: SIMPOS window system method reference (text/graphic output :draw_line/:draw_rectangle/:draw_string/:get_point_value, markers ...) p16-17.
- TM-115 (PSI Font Editor Implementation Notes, 119pp): class-by-class method documentation of an ESP application built on SIMPOS windows/menus; not SIMPOS itself.
- TM-112: font editor user guide.
- TM-785 p3: Librarian install-from-floppy procedure ("ライブラリアンを生成", Execute, Command>, "FDD mount ok? Input unit No.", error "Package ... already exists / Cannot load package_template", Error handling menu: Erase existing package and continue / Inspect / Return to librarian top level).
- TM-786: "オンラインSIMPOS照会書" operations guide (an online query/inquiry form application) -- not SIMPOS internals.
- TM-025 pp172-195: GP-PRO graphics library source in DEC-10 Prolog (pre-PSI), not SIMPOS.
- ESP manuals (IFS manuals/esp, TeX): overview-e.tex describes the 4-volume SIMPOS manual set (Overview, Operations, Programming, Japanese document edition); program-e.tex has Package/librarian sections (lines 5250-5660: package, package environment, Package##Class, librarian externally declares classes, catalogs) and macro banks saved by the librarian (7270). No class library reference.
- TM-388 ESP Guide, TR-044 ESP Reference manual, TM-364/TM-134/TM-146: ESP language with examples (standard_io_window etc.), not SIMPOS internals.

## Usage-derived interface: IFS SIMPOS application sources (held)
- tools/census.py over extract/ifs_simpos (19 archives, 1351 .ESP files): 1879 classes defined in apps, ~300 external (system) classes referenced with method names; output pages/simpos_class_census.tsv.

## Library holdings (CiNii Books, opened)
- JAIST library (北陸先端科学技術大学院大学 附属図書館), call no. C42.4, barcodes 2950400-2950404:
  BN13167194 SIMPOS使用説明書 1985.4 "MP3001-1"; BN13167514 SIMPOS操作説明書 1985.4 "MP3002-1";
  BN13167467 SIMPOS(1.5版)機能追加・変更点の説明資料 1985.9 "SIM-I-U-GEN021";
  BN13167310 KL0組込述語説明書 (逐次型推論マシンPSI説明書) 1985.4 2版 "MP7002-1";
  BN13167682 コンソール・プロセッサ(CSP)操作説明書 1985.4 "MP7003-1".

## Media
- ICOT museum VIDEO/PSI: 7 wmv segments incl. simpos.wmv (SIMPOS structure diagram, real screen footage of system menu: debugger, editor, file_manipulator, librarian, spooler, font_editor).
- Giho 1991-03 (9103) p107: MELCOM PSI/UX product page (models 350 B2150 / 400 B2151; SIMPOS and UNIX run concurrently on X window).

## Additions
- Librarian batch command files in IFS apps (.COM, 55 files): vocabulary command("lib:FILE.COM"), fxds([files]) (compile/catalogue list), make_environment(Env,[simpos]), save_environment, make_package(Pkg,Env), save_package, use_package, load, refute; gog-esp/login.com = SIMPOS login file (items_list system menu: debugger, pmacs, file_manipulator, librarian, shell, spooler_manipulator, pattern_editor; superuser##file_backup). Pathnames ">sys>user>cgs>source>..." and logical "pb:file.esp".
- SIMPOS versions stated in IFS READMEs: 3.0, 3.2, 4.0, 5.0, 5.1, 6.2 (OKI PSI-II), 7.0, 7.1, "7 or 8" (PSI-II), "A22" (PSI-III); CiNii: 1.5 (1985.9). Giho 63(7) 1989: SIMPOS II "B00版" released for PSI-II.
- WINCS (Computer Software 8(1) 1991): ESP window-control development tool, contains code listings and screenshots (montage checked). TM-079: handwritten slides with SIMPOS structure tree (programming system / OS: window, file, network / supervisor: process, memory, stream / kernel).
- Leads: NIH grant Z01-CT000237-01 (grantome): ICOT installed 2 PSI-II at NIH Oct 1990, pairs at Argonne and LBL. ICOT Journal No.30 (1991) "The Struggle to Installing PSIs at Argonne".
- Overlap: giho-9103 sha 79a99f19... also in search2 manifest.

## Corrections / page provenance (all = PDF page index of the render; "opened" = read by eye in OCR text)
- Opened: TR-046 p28; TR-061 p13; TR-524 p21,p37,p38; TM-100 p6,p8,p11,p13,p18; TR-056 p13, p21, p22 (index 22 = printed folio 20); TR-059 p12 (= folio 10), p22, p30; TM-125 p17 (= folio 16); TM-065 p16; TR-283 p8; TM-115 p4,p36,p64,p100; TM-785 p3,p8; TM-229 p5,p6; TM-181 p4 (screenshot reads "SIMPOS version 2.19"); TM-786 p3,p6; TM-025 p177; TR-353 p4; TR-057 p10; TR-087 p9,p11; TR-086 p9; TR-055 p7,p14; TM-134 p66; TM-388 p102.
- Located by class/method regex only (not read): TM-100 p4,7,9,10,12,14,15,17; TM-065 p7,12,13,15; TM-125 p16; TR-056 p19-20; TR-059 p20-21; TR-283 p6-7,9-12,19; TM-061 p6-9 (class file).
- Boot: concept only. TR-056 p21 / TM-100 p6,p13: class boot_process (inherits process, overrides :create/:activate; runs boot program inheriting as_boot_program; created by hardware at bootstrap). TR-059 p30: device handlers instantiated during boot-up. TR-087 p11 / TR-086 p9 / TM-100 p18: an IPL written in ESP; modules separately compiled, partially linked and stored on flexible disks (cites Ueda et al. 1984); IPL operational May 1984. No boot-image or disk format described.
- Librarian / templates: TR-057 p10 and TR-087 p9: each class has a class source file, a class template file and a class object file on secondary storage; a template is built from one source file and holds everything but inheritance analysis. TM-229 p6, TM-181 p4, TM-143 p3: librarian generates and manages executable code from ESP source (Japanese overview). No document describes the .ptf (package template file) byte format.
- Overview-only (OCR code score ~0, not read in full): TR-055, TR-057 (except p10), TM-009, TM-126, TM-143, TM-161 (PSI port of a general assembler; class work p15-16), TM-181, TM-229, TM-401 (network system overview), TM-079 (handwritten slides with SIMPOS structure tree), TR-353 (Chikayama 1988, OS development with OO language: ESP/SIMPOS prose, no listings seen in OCR).
- Version ties: disc/README "SIMPOS 6.2 OKI-PSI-II"; kappa2/INSTALL "PSI-II, SIMPOS Version 7 or 8" and "PSI-III and SIMPOS A22".
- NIH lead correction: grant Z01-CT000237-01 text: "The Institute for New Generation Computer Technology installed two of the PSI-II logic programming computers in October 1990. Similar pairs of machines have been installed at Argonne National Laboratory and lawrence Berkeley National Laboratory." The host being NIH (DCRT) is INFERRED from the Z01 grant id, not stated.
