#!/usr/bin/env bash
# viz-deck narration embedder
# 1) Generates per-slide MP3 narration from speaker_notes/*.txt using edge-tts
# 2) Re-runs ppt-master svg_to_pptx.py with --narration-audio-dir + --use-narration-timings
# Result: PPTX with embedded audio that plays automatically on slide entry
#
# Usage:
#   ./embed-narration.sh <project_dir> [--voice zh-CN-XiaoxiaoNeural] [--provider edge|elevenlabs|minimax|qwen|cosyvoice]

set -euo pipefail

PROJECT_DIR="${1:-}"
shift || true

if [ -z "$PROJECT_DIR" ] || [ ! -d "$PROJECT_DIR" ]; then
  echo "Usage: $0 <project_dir> [--voice VOICE] [--provider edge|elevenlabs|...]" >&2
  exit 2
fi

# ppt-master detection: $PPT_MASTER_HOME → ~/.agents/skills/ppt-master (Codex) → ~/.claude/skills/ppt-master (Claude Code)
if [ -n "${PPT_MASTER_HOME:-}" ] && [ -d "$PPT_MASTER_HOME" ]; then
  PPT_MASTER="$PPT_MASTER_HOME"
elif [ -d "$HOME/.agents/skills/ppt-master" ]; then
  PPT_MASTER="$HOME/.agents/skills/ppt-master"
elif [ -d "$HOME/.claude/skills/ppt-master" ]; then
  PPT_MASTER="$HOME/.claude/skills/ppt-master"
else
  echo "ERROR: ppt-master not installed. Looked in: \$PPT_MASTER_HOME, ~/.agents/skills/ppt-master, ~/.claude/skills/ppt-master" >&2
  exit 1
fi

PYTHON="$PPT_MASTER/.venv/Scripts/python.exe"
[ -f "$PYTHON" ] || PYTHON="$PPT_MASTER/.venv/bin/python"

NOTES_DIR="$PROJECT_DIR/speaker_notes"
AUDIO_DIR="$PROJECT_DIR/narration_audio"

if [ ! -d "$NOTES_DIR" ]; then
  echo "ERROR: no speaker_notes/ in $PROJECT_DIR. Re-run make-pptx-deck.mjs with --with-notes" >&2
  exit 1
fi

mkdir -p "$AUDIO_DIR"

echo "[narration] generating per-slide audio via ppt-master notes_to_audio.py …"
"$PYTHON" "$PPT_MASTER/skills/ppt-master/scripts/notes_to_audio.py" "$PROJECT_DIR" \
  -o "$AUDIO_DIR" "$@"

echo "[narration] rebuilding PPTX with embedded audio …"
PROJECT_NAME="$(basename "$PROJECT_DIR")"
OUT_PPTX="$PROJECT_DIR/exports/${PROJECT_NAME%_pptx_build}_narrated.pptx"
mkdir -p "$(dirname "$OUT_PPTX")"

"$PYTHON" "$PPT_MASTER/skills/ppt-master/scripts/svg_to_pptx.py" "$PROJECT_DIR" \
  -o "$OUT_PPTX" \
  --narration-audio-dir "$AUDIO_DIR" \
  --use-narration-timings

echo "[narration] ✓ narrated PPTX: $OUT_PPTX"
echo "[narration] To export MP4 with synced narration: open in PowerPoint → File → Export → Create a Video"
