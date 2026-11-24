# PARC Diablo disk images — held locally, not in git

| file | source | used by |
|---|---|---|
| `diags.dsk` | Bitsavers, `bits/Xerox/Alto/disk_images/chm/diags.zip` (Computer History Museum Alto file release) | `tests/run_smoke.sh` |

Fetch with `sh tools/fetch-disks.sh disks` (also fetches `bcpl.zip`
and `games.zip`), then `cd disks && shasum -a 256 -c SHA256SUMS`.
