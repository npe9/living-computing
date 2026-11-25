# Preserved PSI machines, reminiscences, vendor journals, catalogues and listings (2026-11-24, b)

The fourth search of the day, after `web_search_2026-11-24.md`, `web_search2_2026-11-24.md`,
`sweep_2026-11-24.md` and `fixpoint_2026-11-24.md`. It covers the places that `fixpoint`'s §3 lists
as not searched:
- surviving PSI machines (a preserved PSI with its disk would hold a SIMPOS binary);
- reminiscence posts;
- vendor names and journals;
- theses and repositories;
- library catalogues;
- auction and second-hand listings, as a record only;
- patents.

All accesses were on **2026-11-24**. Nobody was contacted, nothing was bought or bid on, no form was
submitted (catalogue searches are GET queries on public interfaces), no terms were accepted, no login
was used and no bot challenge was bypassed. Downloads went into empty scratch directories and were
read with `python3 -I`, `pdftotext`, `pdftoppm` and `tesseract`; nothing downloaded was executed.

How each fact was read:
- **read here**: the raw HTML, JSON or PDF text was parsed here, or the page image was viewed;
- **summary only**: a search engine's summary or a fetch tool's summary was read, not the page.
  The fixpoint record calls this "reported by a delegated search".

> **Verdict.** No SIMPOS or CESP system code, binary, disk image or tape was found. **No source
> mentions disks or media for any surviving PSI.** One surviving PSI is listed (not confirmed: an IPSJ page
> of unknown date): JAIST's, model and working state unstated. The other preserved hardware is PIM/m and PIM/p in the 国立科学博物館's
> store. Two new primary documents were found and are on disk only (§1).

## 1. FOUND

| # | what | where | how read | what it adds |
|---|---|---|---|---|
| F1 | **CESP application source in print.** 前田恭伸, *Environmental risk assessment support system based on multiple domain knowledge*, 筑波大学 doctoral thesis, 甲第1300号, 1994-05-31. Appendix A, "Basic syntax of Common ESP" (A-1 to A-3). Appendix B, "Source code of the RARCOM" (A-4 to A-34): the classes `rarcom`, `waterWorks`, `simModel`, `bridge`, `waterE_WaterW`, `fplant`, `sewage`, `city`, `basin`, `riverSegment`, `compo`, `conduit` and `scenarioMaking` | https://tsukuba.repo.nii.ac.jp/records/20781 (`1.pdf`, 156 pp.; `A1300.pdf`, summary). Found through CiNii Research OpenSearch (`q=Common ESP`), record crid 1910865335688164608 | **read here.** The text layer is a poor OCR. Pages A-5, A-28, A-32 and A-34 (PDF pp. 127, 150, 154, 156) were viewed as images. Calls were listed from the text layer, both `#` and full-width `＃` | Calls into the CESP library, seen on the page images: `:create(#list_index, L)` and `:add_at/3`; `#utility` `:member/3`, `:nth/3` and `:delete/4`; `#symbolizer` `:get_atom_string/3`, `:get_number/3` and `:get_atom/3`; `:class_object/2`; a dialog box's `:activate`, `:read` and `:deactivate`; `:fprintf(Cl, stdout, Fmt, Args)`. In the text layer only: `:get_class_object(#library, BID, Bridge)` (p. A-6). **Checked against the SIMPOS census** (`../required/classes.tsv`, grep): 7 of these 14 keys are in it: `list_index` `create/2` and `add_at/3`, `symbolizer` `get_atom/3`, `get_atom_string/3` and `get_number/3`, `class_object/2` (on several classes), `library` `get_class_object/3`. **Not in it:** the class `utility` (no row; `member/3`, `nth/3`, `delete/4`), `fprintf/4` (no occurrence; with `stdout` it looks like a CESP-on-Unix addition, INFERENCE), and the dialog box class (no dialog class in the census). Its value: CESP kept SIMPOS's `list_index`, `symbolizer` and `library` interfaces; the three absent groups are either CESP additions or SIMPOS classes the 15 census programs never call (not decided). It cites `[AIR91]`, 「CESP言語」 (AIR, 1991). Grade: **USAGE (CESP application code), not system code.** The thesis's RARCOM ran at 筑波大学 社会工学系, the CESP site already listed in `web_search2` rank 4 (KAKEN 07680449) |
| F2 | 溝口文雄 (東京理科大学 理工学部), 「ソフトウェア評論 ESP」, コンピュータソフトウェア 5(1), 1988, pp. 62-68 (received 1987-08-28) | https://www.jstage.jst.go.jp/article/jssst/5/1/5_1_62/_pdf. Found by the J-STAGE search API (`article=ESP`) | **read here**: p. 62 viewed as an image; all 7 pp. OCR'd (tesseract jpn+eng) | **A PSI site:** the PSI had been installed "我々のバイオシステム研究所に設置されて" (p. 62, checked on the page image) for about 1 year 7 months. Which body that institute is was not established; that it belonged to 東京理科大学 is INFERENCE from the author's printed affiliation. It prints ESP class examples: Fig. 1, the class syntax and a keyed-door class; Fig. 2, a temporal-event class whose slot initialiser does `:create(#list, Hist)`; `class adder has nature constraint`. Its SIMPOS usage (OCR only, p. 65-66) is PROSE: the pool's "リストバケット" is used for all-solutions search, and the pool's index type and SIMPOS's window functions are used. It names the graduate students of the PSI evaluation project in its acknowledgements (not copied here) |
| F3 | 中澤修, AIR's CESP lead, is back on an **Oki** byline in 1995: 鈴木寿郎・吉田誠・中澤修, 「分散ソフトウェア構築のための分散オブジェクト指向言語DOL/C++」, OKI テクニカルレビュー No. 167 | https://www.oki.com/global/ja/technologies/otr/1995/n167/ | **read here** (table of contents) | Corroborates the fixpoint INFERENCE that AIR's CESP leads were seconded from Oki. No CESP or SIMPOS content |

Not added to the manifest: Mitsubishi Giho issues fetched to scratch and found to hold no SIMPOS
content (§3), the JSAI 2014 retrospectives (§3) and the OKI 120-year history chapters (§3).

## 2. LEADS for the owner (ranked by likelihood of yielding SIMPOS software)

Nobody was contacted. Each route is an institution's published enquiry channel, as printed on the
page cited; no personal address was inferred or recorded.

| rank | holder | what is there | evidence (how read) | why this rank | published enquiry channel |
|---|---|---|---|---|---|
| 1 | **JAIST 記号処理計算機コレクション** (北陸先端科学技術大学院大学, 情報科学系研究棟1F, 能美市旭台1-1) | "PSI（ICOT）" among the preserved items; "関連するマニュアルや資料" also kept. Some machines were "動態展示も試み"; an ELIS demonstration was held in 2010. **Model, disks and working state of the PSI are not stated.** The library OPAC (§3) holds the five 1985 PSI-I manuals (SIMPOS使用説明書, SIMPOS操作説明書, SIMPOS 1.5版 changes, KL0組込述語説明書 2nd ed., CSP操作説明書), the ICOT Journal and the TR/TM series | IPSJ satellite page `museum.ipsj.or.jp/satellite/hokurikusentandai.html` (raw HTML **read here**); JAIST WebOPAC (**read here**) | The only confirmed surviving PSI, kept with manuals by a collection that tries to keep machines running. A PSI's disk would carry a SIMPOS system. Ask: which model; whether its disk or cartridges survive; whether it boots; the list of "related materials" | 広報・学生獲得推進室 広報係, Tel. 0761-51-1031, kouhou@ml.jaist.ac.jp (printed on the IPSJ page as the 照会先) |
| 2 | **国立科学博物館** (National Museum of Nature and Science), store | "ICOT PIM／ｍ" and "ICOT PIM／ｐ" (also "東京大学 PIE"), status "----": kept in storage, not normally shown; viewing by consultation with the institution | IPSJ 「実物の所在地情報」 table, `museum.ipsj.or.jp/library/shozaichi.html` (rows **read here**); IPSJ page `en/computer/other/0002.html` (summary only) | PIM/m's front end was a PSI-III running SIMPOS, with `pimfep`/`pimscsi` (`../../icot_software_survey.md` rows on the PIM/m front end; `../../fep_services.md`). INFERENCE: if the front-end unit or its disk went with the cabinets, it holds a SIMPOS (PSI-III, 7.x era) system. Nothing found says what came with the cabinets. Ask: whether a front-end processor, console or disk was accessioned with PIM/m or PIM/p | the museum's published route for its 産業技術史資料情報センター (https://sts.kahaku.go.jp/); the IPSJ table says viewing needs consultation with the holding institution |
| 3 | **筑波大学** (社会工学系, the RARCOM thesis's department) | A CESP site 1993-96: KAKEN 07680449 (`web_search2`), and the thesis of F1 with RARCOM's source, which ran under CESP | F1 (**read here**) | CESP (not SIMPOS) media and manuals may survive with the department; the paths printed in the thesis (`/home/ecopolis/...`) show a Unix CESP installation | **not looked up**: use the university's own published enquiry route |
| 4 | **東京理科大学** (理工学部, the author's affiliation in F2) | A PSI installed about 1986 at the author's "バイオシステム研究所", for an expert-system evaluation project. That the institute belonged to TUS is INFERENCE from the affiliation | F2 (**read here**) | A first-generation PSI site. Nothing says the machine survives; TUS's IPSJ satellite museum (なるほど科学体験館) lists only FACOM201, UNIVAC120 and Bendix G-15 (summary only) | **not looked up**: use the university's own published enquiry route |
| 5 | Mitsubishi Electric (IT group) and Oki | unchanged from `fixpoint` §4 | — | No corporate museum of either holds a PSI as far as found (§3) | unchanged |

Unchanged from earlier records, and not re-ranked here: NDL; AIST (the ICOT archive successor);
the CESP universities other than Tsukuba; ASTEM; Argonne and Lawrence Berkeley (pairs of PSI-II,
1990: `../../psi_acquisition.md` §9). For the US sites nothing further was found (§3).

## 3. NOTHING (the place answered; nothing relevant)

Each row gives the place, the queries, the result and the depth read. All rows are dated 2026-11-24.

**Museums and machine registries**

| place | queries | result |
|---|---|---|
| IPSJ 情報処理技術遺産 | all year pages 2008-2019 and 2023-2025, the 機器名別 and 製造者別 indexes (**read here**); regex PSI, ICOT, 推論, PIM, SIMPOS, 第五世代, Prolog, 新世代 | none. The 2020-2022 year pages answer 404 and are not linked from the index |
| IPSJ 分散コンピュータ博物館, all 14 certified sites | every site page (**read here**); regex PSI, ICOT, 推論, Prolog, LISP, 三菱, 沖電気, 記号処理 | only JAIST (LEAD 1). KCG, 東京農工大 (西村コレクション), 東京理科大, 東北大, 統数研, 神戸大, NTT, 日立大みか, 富士通DNA館, 京都産業大 and マイコン博物館: no PSI |
| IPSJ 「実物の所在地情報」 | the whole table (**read here**) | PIM/m, PIM/p and PIE at 国立科学博物館 (LEAD 2); no PSI, Multi-PSI or MELCOM PSI row |
| IPSJ MELCOM PSI page (`en/computer/other/0009.html`) | read (summary only) | does not say where any unit is |
| IPSJ magazine MGN520616 (2011, the 2010 certification ceremony) | text layer **read here** | KT-1 only; no PSI |
| 東京大学 総合研究博物館 | web search | nothing (summary only) |
| 東京理科大学 なるほど科学体験館 | page (summary only) | FACOM201, UNIVAC120, Bendix G-15 |
| 東北大学 分散コンピュータ博物館 | page (summary only) | SENAC-1, supercomputers, TAINS; no PSI |
| Mitsubishi Electric IT history page (`/it/history/`) | read (summary only) | the 1986 MELCOM PSI entry; no museum or preservation statement. Subsidiary mergers: 2014 and 2025 (三菱電機デジタルイノベーション) |
| Oki: 「沖電気120年史」 chapters 4-6 (25 PDFs) | text layer **read here**; regex ICOT, 第五世代, 推論マシン, PSI, 新世代コンピュータ, Prolog, AI言語研究所, ESP, 人工知能 | no PSI, ICOT or ESP; only if800, PENSEE and the 1990 関西総合研究所 |
| Computer History Museum, The National Museum of Computing, Heinz Nixdorf MuseumsForum | web searches | nothing (summary only). CHM's catalogue itself: UNREACHABLE (§4) |
| Argonne, Lawrence Berkeley, NIH (the 1990 PSI-II pairs) | web searches (Argonne PSI-II fate, Overbeek/Lusk, NIH/NCI/LBL) | nothing (summary only) |
| Multi-PSI survivors | web search 「Multi-PSI」「マルチPSI」 保存/現存/博物館 | nothing |
| Private collectors | web searches 「MELCOM PSI」「PSI/UX」 所有/入手/保管/レトロ; vcfed/classiccmp ICOT PSI | nothing (summary only) |

**Reminiscences**

| place | queries | result |
|---|---|---|
| Hatena: blackcomb.hatenablog.com (2019-01-14) | read (summary only) | a former participant learned ESP on SIMPOS; no materials |
| Hatena: yaneurao.hatenadiary.com (2006-08-20) | read (summary only) | the AITEC/ICOT archive DVD (already mirrored: `../../literature_gaps.md` at the DVD rows); KLIC passed to the KLIC association. No PSI or SIMPOS |
| Qiita sym_num (FGCS revisited) | read (summary only) | N-Prolog; no PSI |
| note / Qiita / Zenn / Hatena / X / 5ch | web searches 「SIMPOS」「PSI」 with the site names; 「SIMPOS」 twitter/x.com; 5ch 第五世代 PSI | nothing |
| JSAI 人工知能 29(2), 2014: 橋田浩一 「ICOT終了20周年に寄せて」 (pp. 157-) and 「海外から見た第五世代コンピュータプロジェクト…」 (pp. 149-) | text layers **read here**; regex PSI, SIMPOS, 保存, 寄贈, 博物館, 廃棄, ソースコード, アーカイブ, PIM, ESP | they name PSI, ESP and SIMPOS; nothing on where machines or software went |

**Vendor journals**

| place | queries | result |
|---|---|---|
| 三菱電機技報, issues not held before: 8504, 8601, 9003, 9103, 9107, 9112, 9412, 9509, 9601 (8805 was re-fetched; it is held) | text layers **read here**; regex PSI, SIMPOS, ICOT, 推論マシン, CESP, Common ESP | 9103 and 9107: a PSI/UX product notice (PSI/UXモデル350/400, B2150/B2151; "SIMPOS", "ESP"), already known from Giho 1991-03; 9112: the 1991 index; 9509: a design-review system first built on PSI (an application); 8805: the machine-translation system on MELCOM PSI (held). No code, no archive statement. Kept in scratch only |
| OKI テクニカルレビュー, issues 166-179 (1995-98) | tables of contents **read here**; regex 推論, Prolog, ESP, ICOT, 第五世代, 論理型, 知識処理, オブジェクト指向, KL1, PSI | F3 only. The 1985-94 沖電気研究開発 is not online (NDL only, as before) |
| ETL / AIST reports | web search | none online (NDL only, as `fixpoint` §3) |

**Theses, repositories and articles**

| place | queries | result |
|---|---|---|
| CiNii Research OpenSearch (all) | SIMPOS, Common ESP, CESP, 逐次型推論マシン, PSI ESP, KL0, ESP 論理型 オブジェクト指向; 200 per query, filtered to repository and thesis items | F1, and the EUODHILOS-II paper (IPSJ 13492, 1997, a GNU Emacs re-implementation of the PSI/SIMPOS EUODHILOS; located, not read). The rest is noise |
| CiNii Research dissertations, 1984-2000 | ESP, SIMPOS, CESP, PSI 推論, 逐次型推論, 論理型 オブジェクト指向, KL1 PIM, ICOT | Nakashima 1991 (held); Kyoto 1996 and Waseda 1998 on parallel logic languages (KL1, not SIMPOS). Title and abstract only: F1 was not found this way |
| J-STAGE search API | keyword (SIMPOS, Common ESP, CESP, 逐次型推論マシン, PSI ESP): 0; article (ESP, 推論マシン, PSI); text (SIMPOS: 24, Common ESP); authors 近山隆 (15), 実近憲昭 (2), 横田実, 内田俊一, 服部隆; 中澤修 gives 368 unrelated namesakes | F2. WINCS (JSSST 8(1), 1991) is already held. The rest: PIM surveys, the 2014 retrospectives, unrelated |
**Library catalogues** (public search interfaces, GET only)

| catalogue | queries | result |
|---|---|---|
| **JAIST WebOPAC** (`opacsrv02.jaist.ac.jp/webopac/ctlsrh.do`) | SIMPOS (3); ESP 説明書; 逐次型推論マシン (2); PSI 説明書 (2); 新世代コンピュータ技術開発機構 (18); Common ESP; CESP; MELCOM PSI; KL0; 無償公開ソフトウェア; PIMOS; 小型化PSI; SEMACS; Pmacs; MP1002; MP3001; MP3003; MP1005; MP7002; ESP説明書; SIMPOS使用操作説明書 | **read here.** Only the five 1985 manuals, the ICOT Journal, the TR/TM series, FGCS and LPC proceedings, and 「第五世代コンピュータ研究開発の終わりにあたって」 (1995). **Negative control:** `MP3001` returns 0 although JAIST holds MP3001-1, so MP numbers are not indexed. An MP-number miss anywhere is not evidence |
| **Kyoto KULINE** (`kuline.kulib.kyoto-u.ac.jp`, amode=2) | SIMPOS (19, all "simposio"); ESP 説明書; 新世代コンピュータ技術開発機構 (11); ICOT journal; 逐次型推論マシン; Common ESP (1, noise); MELCOM PSI; 無償公開ソフトウェア; PSI 説明書; 人工知能 and 推論マシン (positive controls: 1,879 and 5); ESP説明書; MELCOM; KL0組込述語説明書; MP1002; MP3003; SIMPOS使用説明書 | **read here.** Zero-hit pages were confirmed by the page's own `no-hit` marker. Held: ICOTジャーナル, 「第五世代コンピュータ研究開発の終わりにあたって」, FGCS proceedings, and PIM theses (島田, 長沼, 平田). No SIMPOS, ESP or PSI manual |
| **Keio and Waseda** (Primo `primaws/rest/pub/pnxs`) | SIMPOS; ESP 説明書; 逐次型推論マシン; 新世代コンピュータ技術開発機構; Common ESP; CESP; MELCOM PSI; ICOTジャーナル; 無償公開ソフトウェア; PSI 説明書; MP1002; MP3001; MP3003; KL0組込述語説明書 | **read here.** Keio: ICOT TR and TM series (1982-1995), LPC proceedings, FGCS'84. Waseda: AI白書, FGCS'84. No manual |
| **神奈川県立図書館 / 川崎図書館** (WINJ, `klnet.pref.kanagawa.jp/winj/opac`) | SIMPOS (4, noise); ESP 説明書; 逐次型推論マシン; PSI 説明書; 新世代コンピュータ技術開発機構 (34, all 4 pages read); Common ESP (noise); CESP (noise); MELCOM PSI; ICOTジャーナル (18, both pages read); 無償公開ソフトウェア; 推論マシン; AI言語研究所; MP1002; MP3003; MP3001; ICOT (86, pages 1-4 of 9 read) | **read here.** ICOTジャーナル 通巻21-37 (1990-03 to 1995-03; 要問合せ), ICOT研究速報 and ICOT研究論文 series, the FGCS results book. No manual, no 無償公開ソフトウェア総覧 |
| CiNii Books, ICOTジャーナル (NCID AN10155113) | holdings JSON (**read here**) | the seven holders: 筑波大 図書館情報学図書館, 東大 柏図書館, 電通大, 京大 情報学研究科, JAIST, 群馬高専, 神奈川県立川崎図書館 |

**Listings** (record only)

| place | queries | result |
|---|---|---|
| Yahoo!オークション closed listings (the last 120 days only, as the page states) | MELCOM PSI, SIMPOS, ICOT, 推論マシン, 第五世代コンピュータ, MELCOM 説明書 PSI, ESP Prolog | **read here**; every returned title was grepped. Zero matches for all but ICOT (handbags, "ikot") and 第五世代コンピュータ (three books: 『第五世代コンピュータ入門』, POPCOM 1984-02, 元岡・喜連川 『第五世代コンピュータ』). No hardware, media or manual |
| メルカリ | web search on the site | nothing (summary only) |
| eBay | web search | nothing (summary only); the site itself: UNREACHABLE |

**Patents**

| place | queries | result |
|---|---|---|
| Google Patents (`xhr/query`) | SIMPOS; 逐次型推論マシン; "ESP" "KL0"; KL0 with Mitsubishi; 推論マシン with Oki and with Mitsubishi before 1995; Prolog, ユニフィケーション and 論理型言語 with Mitsubishi before 1996; 論理型言語 and Prolog with Oki before 1996; ICOT as assignee (English name: 0) | **read here, top 10 of each list only** (Mitsubishi Prolog 65, 論理型言語 113; Oki 論理型言語 27, Prolog 5). Two Mitsubishi logic-language patents were read (summary only): KR920002853B1 (priority JP 1987, a predicate database shared by Prolog tasks) and JPS63282847A (Prolog tasks linked with FORTRAN on a process-control computer). Both are MELCOM process-control Prolog, not the PSI, and neither prints code or interfaces. Further ICOT-assignee queries were refused (HTTP 503) |

## 4. UNREACHABLE (and why)

| place | why |
|---|---|
| 東京大学 OPAC (`opac.dl.itc.u-tokyo.ac.jp`) | HTTP 202 with an empty body (a JavaScript gate) |
| 東京工業大学 / 東京科学大学 (`topics.libra.titech.ac.jp`) | Cloudflare "Just a moment" challenge (HTTP 403) |
| IRDB (`irdb.nii.ac.jp/search`) | HTTP 403 "Server Error!". CiNii Research, which indexes IRDB's records, was used instead |
| Computer History Museum catalogue (`/collections/catalog?s=`) | a script-rendered shell: four queries returned the same 442-character page with no records |
| 国立科学博物館 未来技術遺産 registry (`sts.kahaku.go.jp/research/shiryo/`) | script-rendered (a POST API); only web searches were run against it. They found no ICOT, PSI or AI-machine registration. Not a negative |
| 国立科学博物館 技術の系統化調査報告 | the old PDF URLs redirect to an index (`/research/taikei/`). The report titles in its computing list (I) cover mainframes, office computers and PCs, with none on AI machines. The PDFs were not opened |
| 日本の古本屋 search | HTTP 202, empty (a JavaScript gate) |
| eBay search | HTTP 403 |
| aucfan (closed-auction history) | "緊急メンテナンス" (HTTP 503) |
| Google Patents, further queries | HTTP 503 after about 15 queries |
| J-PlatPat | a JavaScript application; not tried |
| JAIST 創立20周年記念誌 (2010, dspace 10119/9588) | fetched, but it has no text layer, so not read |

## 5. Still not searched (no negative claimed)

- Mercari's own search (only a web search was run), and Yahoo!オークション beyond its 120-day window.
- Oki's 沖電気研究開発 1985-94 (NDL only) and the ETL reports (NDL only).
- The 1992-96 CESP university sites other than Tsukuba, in their own repositories.
- J-STAGE by author beyond the six names above.
- KAKEN final-report PDFs: the project pages were covered by `web_search2`, but no report PDF
  was looked for in this search.

## 6. Files

- **Added, on disk only** (gitignored; rows in `../../nonlocal/lit/SOURCES.tsv` and `SHA256SUMS`,
  addendum in `../../nonlocal/LIT_MANIFEST.md`):
  - `lit/theses/tsukuba_20781_maeda1994_1.pdf` and `..._A1300.pdf` (F1);
  - `lit/journals/jstage-jssst_5_1_62_mizoguchi_esp.pdf` (F2).
  They are in the worktree this search ran in and must be copied to the main checkout's directories
  of the same name.
- **Edited:** `../../psi_acquisition.md` (§15 and the who-to-ask list), `fixpoint_2026-11-24.md` §3.
