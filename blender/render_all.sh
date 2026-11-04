#!/bin/bash
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
OUT="$(cygpath -w "$(cd "$(dirname "$0")" && pwd)/../assets/renders")"
for shot in room_wide room_portrait sofa_34 sofa_front sofa_side; do
  "$B" -b --factory-startup -P scene.py -- "$OUT" $shot ${1:-128} 2>&1 | grep -E "Error|Traceback|RENDERED|HOTSPOTS"
done
echo ALL_DONE
