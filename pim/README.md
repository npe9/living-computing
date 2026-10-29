# ICOT Parallel Inference Machine (1992)

The Parallel Inference Machine was the hardware culmination of Japan's
Fifth Generation Computer Systems project at ICOT. It was not one
machine but five experimental implementations (`PIM/p`, `/m`, `/c`,
`/k`, and `/i`) of a distributed-memory parallel computer for KL1, the
project's concurrent logic-programming kernel language. The first model
for this directory is **PIM/m**: a microprogrammable CISC processing
element compatible with Multi-PSI, connected as a two-dimensional mesh
of as many as 256 processing elements. The other four variants remain
comparative sources until PIM/m is reproduced.

Bluespec implementation: `bsv/` (not started).

See [`plan.md`](plan.md) for the evidence gates and staged model.
The primary-source acquisition manifest is [`docs/README.md`](docs/README.md).

Sources: ICOT, *Proceedings of the International Conference on Fifth
Generation Computer Systems 1992*, especially Kazuo Taki, "Parallel
Inference Machine" and Nakashima et al., "Architecture and
Implementation of PIM/m"; ICOT Technical Report TR-324, *Parallel
Inference Machine Research*; the ICOT FGCS Museum's contemporary PIM
specification and archive. The proceedings and report are project or
project-author publications; each architectural claim must be checked
against the page image before it enters the model.
