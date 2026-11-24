# Readers' notes of the 2026-11-24 subsystem dive

These are the working notes of the ten readers, delegated agents that each covered one kind of held
source. `window.md`, `librarian.md` and `shell.md` were written from them. The notes are kept as the
readers wrote them. Each grades its own claims (PRINTED, PRINTED-INTERFACE, USAGE, PROSE, SCREENSHOT,
INFERENCE) and ends with the pages it read and its open questions. Each `.tsv` holds one fact per row,
with these columns: subsystem, class, kind, member, arity (receiver counted), natures_or_slots, meaning,
grade, citation, version_or_year. `../tools/coverage.py` reads them.

| notes | source covered |
|---|---|
| `trtm_window` | TM-125, TM-126 (every page by eye), TR-046, TR-055, TR-057, TR-061, TM-065, TM-153, TM-225; WINCS (Computer Software 8(1), 1991) |
| `tm115` | TM-115 and TM-112, the font editor (SIMPOS 1.00, 1985) |
| `trtm_progsys` | TM-181, TM-143, TM-229, TM-134, TM-388, TM-364, TM-146, TR-057, TR-087, TR-285, TM-079, TM-634, TM-639 |
| `trtm_manuals` | TM-785, TM-786 (SIMPOS 5.0, 1989: install dialogues), TM-404 (not SIMPOS), TM-401, TM-430 |
| `ipsj` | the 161 held IPSJ items, the journals and the theses: a triage table, then notes on about 30 relevant items |
| `newipsj` | IPSJ 118569, 122601 and 22404, fetched on 2026-11-24, read by eye; with corrections to `../web_search_2026-11-24.md` |
| `ifs_window` | the 19 IFS SIMPOS archives, window side: 334 window classes, creation options, menus, events, key codes |
| `ifs_libshell` | the IFS archives, Librarian and shell side: login files, READMEs, `as_program`, cil's copy of the Librarian; the ESP manuals |
| `ptf` | the 11 held `.ptf` and 10 papyrus `.pak` files: natures, demons, constants recovered by running `../../../../psi/kl0.py` with SIMPOS sends stubbed |
| `video` | the ICOT museum PSI video, all seven segments, read frame by frame |

## Paths in the notes

- Paths such as `work/<reader>/...` and `/private/tmp/...` are the readers' scratch directory, which is
  not kept. Their TR/TM page transcriptions were copied to `../listings/` under the same file names.
- IFS citations are relative to each archive's root, e.g. `cil/src/ds_bep.esp:3123`.
- Papyrus's inner `source.tar` was read from an extraction; its paths start `papyrus_src/`.

## Corrections the notes make to other files

These were not edited in place, because those files belong to earlier passes.

- `../../printed/listings/TM-181_p04_screenshot.esp` and `../../source_notes.md`: TM-181's screens
  read "SIMPOS Version 2.10", not 2.19. The lead checked this on a 300 dpi crop of TM-181 p3.
- `../../printed/listings/TM-785_p03.txt`: the erase confirmation menu is titled `Really?`, with
  items `ERASE` / `STOP`. See `../listings/TM-785_p03.txt`.
- `../../printed/listings/TM-785_p40.esp`: the atoms are single-quoted on the page.
- `../../printed/listings/TM-153_p28_screenshot.esp`: the create call has `[size(...)...]`, not `{`.
- `../../printed/STRUCTURE.md` §11: TM-401 p10-11 describes the file manipulator's functions in
  prose. It does not print menu strings.
- `../../source_notes.md:39`: the system menu in the video has `pmacs` and `edips`, not `editor`.
- `../../required/NOTES.md`: cil's `library_utility` is in package `spec_ds`, not `spec_ms` (see
  `../finds.md` §1). Several `as_program` rows in `../../required/requirements.tsv` are internals of
  cal-esp's debugger (`../finds.md` §3).
- `../web_search_2026-11-24.md` items 118569, 122601 and 22404: see `newipsj.md`. In particular:
  - Fig. 2 of 118569 lists CESP's classes, not SIMPOS's.
  - The `key#cr` row of 122601 is the newline pair.
  - Pmacs may be 81 classes, not 93.
