#!/usr/bin/env bash
# viz-deck · MP4/GIF export wrapper
# Bridges to ~/.claude/skills/huashu-design/scripts/render-video.js
#
# Usage:
#   ./export-mp4.sh INPUT.html OUTPUT.mp4 [DURATION_SECONDS] [WIDTH] [HEIGHT]
#
# Examples:
#   ./export-mp4.sh ./out/hero.html ./out/hero.mp4 8
#   ./export-mp4.sh ./out/motion.html ./out/motion.mp4 12 1920 1080
#
# After MP4 is produced, automatically runs convert-formats.sh to emit:
#   - <name>.mp4         (25 fps base)
#   - <name>-60fps.mp4   (minterpolate to 60 fps)
#   - <name>.gif         (palette-optimized)
set -euo pipefail

HUASHU="${HUASHU:-$HOME/.claude/skills/huashu-design}"

if [[ ! -f "$HUASHU/scripts/render-video.js" ]]; then
  echo "[viz-deck] huashu-design not installed at $HUASHU" >&2
  echo "  Install:" >&2
  echo "    git clone --depth=1 https://github.com/alchaincyf/huashu-design.git $HUASHU" >&2
  echo "    cd $HUASHU && npm install && npx playwright install chromium" >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "[viz-deck] ffmpeg not in PATH — required for convert-formats.sh" >&2
  exit 1
fi

INPUT="${1:-}"
DURATION="${2:-8}"
WIDTH="${3:-1920}"
HEIGHT="${4:-1080}"

if [[ -z "$INPUT" ]]; then
  echo "Usage: $0 INPUT.html [DURATION] [WIDTH] [HEIGHT]" >&2
  echo "  Output: <INPUT>.mp4 next to the input (huashu render-video.js convention)" >&2
  exit 2
fi

if [[ ! -f "$INPUT" ]]; then
  echo "[viz-deck] input not found: $INPUT" >&2
  exit 3
fi

OUTPUT="${INPUT%.html}.mp4"
echo "[viz-deck] Recording $INPUT → $OUTPUT (${DURATION}s @ ${WIDTH}x${HEIGHT})"
node "$HUASHU/scripts/render-video.js" "$INPUT" \
  "--duration=$DURATION" \
  "--width=$WIDTH" \
  "--height=$HEIGHT"

if [[ ! -f "$OUTPUT" ]]; then
  echo "[viz-deck] render-video.js failed to produce $OUTPUT" >&2
  exit 4
fi

echo "[viz-deck] Converting to 60fps + GIF…"
bash "$HUASHU/scripts/convert-formats.sh" "$OUTPUT"

echo "[viz-deck] Done. Artifacts next to $OUTPUT:"
NAME="${OUTPUT%.mp4}"
ls -la "${NAME}.mp4" "${NAME}-60fps.mp4" "${NAME}.gif" 2>/dev/null || true
