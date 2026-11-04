#!/bin/bash
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
OUT="$(cygpath -w "$(cd "$(dirname "$0")" && pwd)/../assets/renders")"
for shot in "$@"; do
  "$B" -b --factory-startup -P scene.py -- "$OUT" $shot 64 2>&1 | grep -E "Error|Traceback|RENDERED"
done
echo ALL_DONE
