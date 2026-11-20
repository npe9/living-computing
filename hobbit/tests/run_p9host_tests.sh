#!/bin/sh
# A2 on the Bluespec core (docs/plan9_boot_plan.md): the shipped 1st
# Edition Plan 9 toolchain runs on the model, checked retirement by
# retirement against the reference run of the same binary.
#
# Each step is bsv/run_p9host.sh: tools/p9run.py records the program on
# sem/hobbit_sem.py, bsv/P9HostTb.bsv replays the kernel's side on the
# core, tools/p9trace_cmp.py compares every retirement record (all fields
# but cyc), and the files the model wrote are compared with the reference
# run's.  On top of that this script checks the two things the gate
# names:
#
#   * the object the shipped za writes *on the core* for libc's main9.s is
#     byte-identical to the member of the shipped hobbit/lib/libc.a;
#   * the shipped zl links, on the core, an object za made on the core,
#     and the linked program runs on the core and prints its line.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
hobbit=$(cd "$here/.." && pwd)
rel=$hobbit/tools/plan9-1e
run=$hobbit/bsv/run_p9host.sh
work=$hobbit/bsv/p9work
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

step() {
  # step NAME TREE BINARY [ARG...]: run, show the summary, fail loudly.
  name=$1; shift
  if ! "$run" "$@" > "$tmp/$name.out" 2>&1; then
    cat "$tmp/$name.out"
    echo "run_p9host_tests: $name FAILED" >&2
    exit 1
  fi
  grep '^MATCH\|^P9HOST EXIT\|^P9HOST console\|^P9HOST file' "$tmp/$name.out" |
      sed "s/^/$name: /"
  # Reads of addresses in no segment.  The comparison cannot see them (a
  # spurious read changes no record), and 2,399 of them on za were how a
  # too-eager operand fetch was found (docs/conformance_1to1.md 1c).  The
  # runs here make 5 to 83; a hundred is the alarm.
  n=$(sed -n 's/^P9HOST EXIT.* \([0-9][0-9]*\) reads outside the segments$/\1/p' "$tmp/$name.out")
  if [ -z "$n" ] || [ "$n" -gt 100 ]; then
    echo "run_p9host_tests: $name made ${n:-?} reads outside the segments (limit 100)" >&2
    exit 1
  fi
}

# echo: its _main and main do not share a 1 Kbyte window (demand fill),
# and it reads its arguments from the exec frame.
mkdir "$tmp/empty"
step echo "$tmp/empty" echo hello world
export P9HOST_KEEP_SIM=1          # the testbench does not depend on the program

# cat of a file longer than its 8,192-byte buffer.
mkdir "$tmp/cat"
cp "$rel/sys/src/9/hobbit/trap.c" "$tmp/cat/"
step cat "$tmp/cat" cat trap.c

# za on libc's main9.s; the object against the shipped archive's member.
mkdir "$tmp/za"
cp "$rel/sys/src/libc/hobbit/main9.s" "$tmp/za/"
step za-main9 "$tmp/za" za main9.s
python3 -c '
import sys
sys.path.insert(0, sys.argv[1])
import build_zl_inferno
member = build_zl_inferno.read_members(sys.argv[2])["main9.z"]
made = open(sys.argv[3], "rb").read()
if made != member:
    sys.exit("run_p9host_tests: main9.z written on the core differs from libc.a main9.z")
print("za-main9: main9.z written on the core, %d bytes, identical to the shipped libc.a member" % len(made))
' "$hobbit/tools" "$rel/hobbit/lib/libc.a" "$work/out/main9.z"

# za, then zl, then the program: all three on the core.
mkdir -p "$tmp/link/hobbit/lib"
cp "$rel/hobbit/lib/libc.a" "$tmp/link/hobbit/lib/"
cp "$here/p9/hello.s" "$tmp/link/"
step za-hello "$tmp/link" za hello.s
cp "$work/out/hello.z" "$tmp/link/"
step zl-hello "$tmp/link" zl -o hello hello.z -lc
cp "$work/out/hello" "$tmp/hello"
# main returns, so _main passes exits() libc's `_exits` function (the
# `_exits<>` quirk, docs/plan9_boot_plan.md): the status is not empty and
# the reference runner exits 1, which run_p9host.sh does not treat as a
# failure of the comparison.
step hello "$tmp/empty" "$tmp/hello"
if [ "$(cat "$work/out/console")" != "hello 1e" ]; then
  echo "run_p9host_tests: the linked program did not print its line" >&2
  exit 1
fi
echo "hello: the program za and zl built on the core printed: $(cat "$work/out/console")"
