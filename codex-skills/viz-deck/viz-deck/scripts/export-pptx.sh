#!/usr/bin/env bash
# viz-deck · HTML → editable PPTX export wrapper
# Bridges to ~/.claude/skills/huashu-design/scripts/export_deck_pptx.mjs
#
# Usage:
#   ./export-pptx.sh INPUT.html OUTPUT.pptx [WIDTH] [HEIGHT]
#
# Output contains real text frames (editable in PowerPoint/Keynote),
# not flattened images. .speaker-notes content lands in the PPT notes pane.
set -euo pipefail

HUASHU="${HUASHU:-$HOME/.claude/skills/huashu-design}"

if [[ ! -f "$HUASHU/scripts/export_deck_pptx.mjs" ]]; then
  echo "[viz-deck] huashu-design not installed at $HUASHU" >&2
  echo "  Install:" >&2
  echo "    git clone --depth=1 https://github.com/alchaincyf/huashu-design.git $HUASHU" >&2
  echo "    cd $HUASHU && npm install" >&2
  exit 1
fi

INPUT="${1:-}"
OUTPUT="${2:-}"
WIDTH="${3:-1920}"
HEIGHT="${4:-1080}"

if [[ -z "$INPUT" || -z "$OUTPUT" ]]; then
  echo "Usage: $0 INPUT.html OUTPUT.pptx [WIDTH] [HEIGHT]" >&2
  exit 2
fi

if [[ ! -f "$INPUT" ]]; then
  echo "[viz-deck] input not found: $INPUT" >&2
  exit 3
fi

echo "[viz-deck] Exporting $INPUT → $OUTPUT (${WIDTH}x${HEIGHT})"
node "$HUASHU/scripts/export_deck_pptx.mjs" \
  --input  "$INPUT" \
  --output "$OUTPUT" \
  --width "$WIDTH" \
  --height "$HEIGHT"

echo "[viz-deck] Done. Open $OUTPUT and verify text frames are editable."
