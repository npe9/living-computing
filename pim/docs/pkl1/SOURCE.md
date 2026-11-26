# pkl1 samples (ICOT Free Software)

Four sample programs of ICOT's "portable KL1" (pkl1), the alpha of
KLIC (README of the archive: "KL1 to C compiler system: KLIC (alpha
version)", July 9, 1993), copied byte for byte from the archive's
`samples/` directory:

| File | SHA-256 |
|---|---|
| `fact.kl1` | `1a7b7e1769ac20e8a493a3e83d5f7599063796c759e8218842f53c3fe9cd7a4b` |
| `nrev.kl1` | `61ffb49d4196b35b02c5d9d5191f30c8eaf051d02a6e35fdd03533484a02dc7b` |
| `qsort.kl1` | `9bd5478d9790b9a4ad62db5f93dfa769bb10dac30790f5bc3ce5a47bbf06cc74` |
| `kkqueen.kl1` | `d4dff43bcc7cd90144ded534275335e9b704ab8a52309f7c41ca9d7f3962908c` |
| `COPYRIGHT` | `9cfaad774b86a47e3201d63f7bf43e2aae87dae5b05d98cdad9080a6b1c992a5` |

Source: `pkl1.tar.Z` (`docs/nonlocal/MANIFEST.md`: from
`https://www.airc.aist.go.jp/aitec-icot/ICOT/ifs/symbolic-proc/unix/pkl1.tar.Z`,
130,871 bytes, SHA-256
`70f5944926da8c5b57eca9e0cd5780213a343f8a03b9166fbd5b8e5cf74c2298`).

Terms: "TERMS AND CONDITIONS FOR USE OF "ICOT FREE SOFTWARE"", the
archive's `COPYRIGHT`, kept here whole. Its section 2 allows free use,
modification, copying and distribution, provided that section 3 ("NO
WARRANTY") always appears on, or is attached to, the Program. The
`COPYRIGHT` file beside the samples is that attachment, and each
sample's header points to it.

Use (R8, `docs/pimos_roadmap.md`): `ref/pimm/longrun_ipl.py` serves
the four as files of the SIMPOS home directory, and again as
`NAME_r8.kl1` with the edits of `PKL1_ADAPT` (OURS: a `:- public` line,
the `top` module dropped). Those edits are made at run time. The files
here are not changed.

`klic_oracle/` holds how the answers were checked against KLIC 2.002
(OURS): the build recipe, our two source edits as a diff, the entry
modules and their output.
