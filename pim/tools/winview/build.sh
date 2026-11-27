#!/bin/sh
# Build the window viewer (winview.c, OURS) with SDL2: tools/winview/build.sh [OUT]
# (default OUT: the build directory's winview, $WINVIEW_BUILD or
# pim/bsv/build-win/winview/winview).  Needs pkg-config and sdl2
# (Homebrew sdl2 2.32.10 was used, 2026-11-26).
set -eu
cd "$(dirname "$0")"
OUT=${1:-${WINVIEW_BUILD:-../../bsv/build-win/winview}/winview}
mkdir -p "$(dirname "$OUT")"
command -v pkg-config >/dev/null 2>&1 || { echo "winview build: pkg-config not found" >&2; exit 1; }
pkg-config --exists sdl2 || { echo "winview build: sdl2 not found by pkg-config" >&2; exit 1; }
# shellcheck disable=SC2046
cc -O2 -Wall -o "$OUT" winview.c $(pkg-config --cflags --libs sdl2)
echo "winview build: $OUT (SDL2 $(pkg-config --modversion sdl2))"
