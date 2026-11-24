# Alto II control PROMs — held locally, not in git

The model's microcode, constant and ACS PROM contents are compiled in
from `rom/rom_arrays.h` (read by `sim/host.c`). They are bit images of
Xerox's Alto II control PROMs, and no redistribution terms for them are
recorded here, so — following the `pim/docs/nonlocal/` pattern — the
file is held on disk and only its checksum is in git (`SHA256SUMS`).

| file | role | provenance as recorded at import |
|---|---|---|
| `rom_arrays.h` | `UROM0`/`UROM1` (2 × 1K microcode words, 32-bit), `CROM` (256 × 16 constant PROM), `ACSROM` (256 × 4 ACS PROM) | "decoded from the public dumps used by ContrAlto / palo" (alto-bluespec README, commit e47186b). The upstream dump files and the decoding are **not yet recorded**: an open item. |

To obtain it today: copy `rom/rom_arrays.h` from the alto-bluespec
repository (unchanged since its first commit, e47186b) and check it with
`shasum -a 256 -c SHA256SUMS`. The `.hex` files in that repository's
`rom/` are not read by the model and were not imported.
