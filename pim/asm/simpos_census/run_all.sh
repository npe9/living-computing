#!/bin/sh
# As run on 2026-11-23 (docs/simpos/README.md). The paths are that session's
# scratch space: the IFS SIMPOS applications extracted, each archive into
# its own empty directory, from docs/nonlocal/ifs/ (IFS_MANIFEST.md). To
# rerun, extract them again and set B and E.
# Re-run the whole scan.  Inputs are read-only; outputs go to $B.
B=/private/tmp/claude-501/-Users-npe-src-living-computing-pim/01b03f2f-1efc-495c-9771-b09885a1fa2f/scratchpad/simposspec/B
E=/private/tmp/claude-501/-Users-npe-src-living-computing-pim/01b03f2f-1efc-495c-9771-b09885a1fa2f/scratchpad/simpos2/extract/ifs_simpos
cd /tmp
python3 -I $B/bin/espscan.py $B cal-esp=$E/cal-esp chal=$E/chal cil=$E/cil disc=$E/disc euod=$E/euod fuzclust=$E/fuzclust gog-esp=$E/gog-esp icotext=$E/icotext kappa2=$E/kappa2+$E/kappa2d1+$E/kappa2d2+$E/kappa2d3 knov=$E/knov kwic-esp=$E/kwic-esp-002 papyrus=$B/x/papyrus_src sum=$E/sum txtstrct=$E/txtstrct utter=$E/utter
python3 -I $B/bin/comscan.py $B/com.json cal-esp=$E/cal-esp chal=$E/chal cil=$E/cil disc=$E/disc euod=$E/euod fuzclust=$E/fuzclust gog-esp=$E/gog-esp icotext=$E/icotext kappa2=$E/kappa2+$E/kappa2d1+$E/kappa2d2+$E/kappa2d3 knov=$E/knov kwic-esp=$E/kwic-esp-002 papyrus=$B/x/papyrus_src sum=$E/sum txtstrct=$E/txtstrct utter=$E/utter
python3 -I $B/bin/report.py $B /private/tmp/claude-501/-Users-npe-src-living-computing-pim/01b03f2f-1efc-495c-9771-b09885a1fa2f/scratchpad/inside/x/esptex+/private/tmp/claude-501/-Users-npe-src-living-computing-pim/01b03f2f-1efc-495c-9771-b09885a1fa2f/scratchpad/inside/x/esptexj /Users/npe/src/living-computing/pim/docs/simpos/class_census.tsv /private/tmp/claude-501/-Users-npe-src-living-computing-pim/01b03f2f-1efc-495c-9771-b09885a1fa2f/scratchpad/simpos2/ocr
