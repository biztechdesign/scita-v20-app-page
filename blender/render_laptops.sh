#!/bin/bash
# Curled-paper demo laptops for the hero Live Preview strip.
cd "$(dirname "$0")"
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
OUT="$(cygpath -w "$(pwd)/../assets/renders")"
T="$(pwd)/../assets/shots"
run() { "$B" -b --factory-startup -P paper_laptop.py -- "$OUT" "$1" "$(cygpath -w "$T/$1_tex.png")" "$2" ${3:-48} ${4:-1400} 2>&1 | grep -E "Error|Traceback|RENDERED"; }
[ "$1" = "sides" ] || run grocery 0
run webtoprint 26 48 2000
run furniture -26 48 2000
echo ALL_DONE
