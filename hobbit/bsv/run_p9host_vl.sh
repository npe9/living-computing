#!/bin/sh
# run_p9host.sh on Verilator: the same arguments, environment, outputs
# and comparison, with step 2 on sim_p9host_vl (build_p9host_vl.sh)
# instead of Bluesim's sim_p9host.
#
#   ./run_p9host_vl.sh TREE BINARY [ARG ...]
#
# The core's output (p9work/core.log) is byte-identical to Bluesim's,
# cyc included, on every run checked (docs/bluespec_architecture.md,
# "Simulators"); the simulator is roughly an order of magnitude faster.
set -eu
P9HOST_SIM=verilator
export P9HOST_SIM
exec "$(dirname "$0")/run_p9host.sh" "$@"
