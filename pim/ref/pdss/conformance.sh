#!/bin/sh
# PDSS conformance runner: compile and run every program of PDSS's own
# test/ directory and the example programs on one PDSS build, and
# compare the normalised transcripts with a golden directory
# (PDSS_GOLDEN, default golden/; README.md "Record sizes" says which).
#
#   ./conformance.sh ROOT [fast|slow|all] [--record]
#
# ROOT is a PDSS tree with a built emulator/pdss and reassembled
# libraries (modern.sh's build-<target>/).  Each job is one Micro PIMOS session: compile(File) (PDSS's
# KL1 compiler, then its assembler, loader and saver), then the job's
# goals, then halt.  PDSS_WORLD makes the "World is" directory a path
# of the same length wherever the tree is (the string is in the heap,
# so its length changes GC timing; sysdep.c honours it), and
# it is printed as <world>.
# The transcript is normalised (the banner line, and the msec of stat/1
# and of the GC report are host-dependent and removed), the emulator's
# exit status is appended,
# and so are the sha256 sums of the .asm the compiler wrote and the
# .sav the saver wrote.  It is compared byte for byte with
# <golden>/<job>.out.  --record writes the golden files instead:
# golden/ was recorded from the retired reference port, golden32/ from
# build-native (README.md); neither is re-recorded to make a change pass.
#
# The job list is jobs.txt: "name|file|goal. goal. ..." per line; a
# leading "slow " marks jobs run only in slow/all mode.  PDSS_RUN
# prefixes the emulator command (e.g. "arch -x86_64").
# PDSS_JOBS (an extended regular expression) runs only the matching jobs;
# PDSS_ARGS is put before the emulator's other arguments (e.g. -h250000,
# a heap size, to move the GC schedule).
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$1; MODE=${2:-fast}; REC=$3
[ -x "$ROOT/emulator/pdss" ] || { echo "conformance: no $ROOT/emulator/pdss"; exit 2; }
ROOT=$(cd "$ROOT" && pwd)
G=${PDSS_GOLDEN:-$HERE/golden}; W="$ROOT/conf"
rm -rf "$W"; mkdir -p "$W" "$G"
cp "$ROOT"/test/*.kl1 "$ROOT"/sample/*.kl1 "$W/"
cp "$ROOT"/emulator/sample.kl1 "$W/emu_sample.kl1"
# Micro PIMOS reads ~/.PDSSsave and friends; keep the user's home out.
mkdir -p "$W/home"; HOME="$W/home"; export HOME
# The world directory, seen through a symlink whose path has the same
# length on every host: /tmp/pdssw.XXXXXXXX/t/emulator (30 characters).
L=$(mktemp -d /tmp/pdssw.XXXXXXXX) || exit 2
trap 'rm -rf "$L"' 0 1 2 15
ln -s "$ROOT" "$L/t"
PDSS_WORLD="$L/t/emulator"; export PDSS_WORLD
T=timeout; command -v timeout >/dev/null 2>&1 || T=
RUN=${PDSS_RUN:-}
SHA="shasum -a 256"; command -v shasum >/dev/null 2>&1 || SHA=sha256sum
pass=0; fail=0; failed=
norm() {
  sed -e '1{/^\*\*\*\*\* PDSS-KL1/d;}' -e "s|$PDSS_WORLD|<world>|g" \
      -e 's/ reductions in [0-9]* msec/ reductions in N msec/' \
      -e 's/^GC Time: [0-9]* msec/GC Time: N msec/' \
      -e 's/[[:space:]]*$//'
}
while IFS= read -r line; do
  case "$line" in ''|'#'*) continue ;; esac
  slow=0
  case "$line" in 'slow '*) slow=1; line=${line#slow } ;; esac
  [ "$MODE" = fast ] && [ $slow = 1 ] && continue
  [ "$MODE" = slow ] && [ $slow = 0 ] && continue
  name=${line%%|*}; rest=${line#*|}; file=${rest%%|*}; goals=${rest#*|}
  if [ -n "${PDSS_JOBS:-}" ]; then
    echo "$name" | grep -Eq "^(${PDSS_JOBS})\$" || continue
  fi
  case "$name" in
    c_*)
      # The KL1 compiler alone (emulator/KL1CMP, as pdsscmp runs it) on
      # one of the distribution's own KL1 sources: goals is its path.
      file=$name
      rm -f "$W/$file.asm" "$W/$file.sav"
      printf "no.\n3.\n'../%s.kl1'.\n'../conf/%s.asm'.\n" "$goals" "$file" > "$W/$name.in"
      args="${PDSS_ARGS:+$PDSS_ARGS }KL1CMP +t" ;;
    *)
      rm -f "$W/$file.asm" "$W/$file.sav"
      printf "compile('../conf/%s').\n%s\nhalt.\n" "$file" "$goals" > "$W/$name.in"
      args=${PDSS_ARGS:-} ;;
  esac
  (cd "$ROOT/emulator" && ${T:+$T 600} $RUN ./pdss $args < "$W/$name.in" > "$W/$name.raw" 2>&1; echo "exit $?" >> "$W/$name.raw")
  {
    norm < "$W/$name.raw"
    for x in asm sav; do
      if [ -f "$W/$file.$x" ]; then echo "$x $($SHA < "$W/$file.$x" | cut -c1-64)"; else echo "$x none"; fi
    done
  } > "$W/$name.got"
  if [ "$REC" = --record ]; then
    cp "$W/$name.got" "$G/$name.out"; pass=$((pass+1))
  elif [ -f "$G/$name.out" ] && cmp -s "$G/$name.out" "$W/$name.got"; then
    pass=$((pass+1))
  else
    fail=$((fail+1)); failed="$failed $name"
    [ -f "$G/$name.out" ] && diff "$G/$name.out" "$W/$name.got" | head -${PDSS_DIFFLINES:-6} | sed "s/^/  $name: /"
  fi
done < "$HERE/jobs.txt"
# The libraries the build reassembled from their .asm (pdssasm): the
# save-file bytes, which are big-endian by construction (saveload.c).
if [ "$MODE" != slow ]; then
  (LC_ALL=C; export LC_ALL; cd "$ROOT" && for f in runtime/*.sav mpimos/*.sav compiler/*.sav; do
     echo "$f $($SHA < $f | cut -c1-64)"; done) > "$W/libsav.got"
  if [ "$REC" = --record ]; then cp "$W/libsav.got" "$G/libsav.out"; pass=$((pass+1))
  elif cmp -s "$W/libsav.got" "$G/libsav.out"; then pass=$((pass+1))
  else fail=$((fail+1)); failed="$failed libsav"
       diff "$G/libsav.out" "$W/libsav.got" | head -6 | sed 's/^/  libsav: /'; fi
fi
if [ $fail = 0 ]; then
  echo "conformance($MODE): PASS ($pass jobs${REC:+ recorded})"
else
  echo "conformance($MODE): FAIL ($fail of $((pass+fail)):$failed)"; exit 1
fi
