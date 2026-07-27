#!/usr/bin/env bash
# viz-deck → editable PPTX bridge wrapper
# Wraps make-pptx-deck.mjs (JSON → SVG → ppt-master → PPTX)
#
# Usage:
#   ./export-editable-pptx.sh spec.json [--theme deep-space|terminal|deck-light] [--anim ANIM] [--trans TRANS]
#
# Required: ppt-master .venv with python-pptx + edge-tts + svglib + reportlab + Pillow + numpy
#   Searched in: $PPT_MASTER_HOME, ~/.codex/skills/ppt-master, ~/.agents/skills/ppt-master, ~/.claude/skills/ppt-master
# Output: <spec-dir>/<spec-name>_pptx_build/exports/<spec-name>.pptx

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <spec.json> [--theme T] [--anim A] [--trans T] [--out DIR]" >&2
  exit 2
fi

# Detect ppt-master across current and legacy harness install locations
if [ -n "${PPT_MASTER_HOME:-}" ] && [ -d "$PPT_MASTER_HOME" ]; then
  :  # honored via env
elif [ -d "$HOME/.codex/skills/ppt-master" ]; then
  :
elif [ -d "$HOME/.agents/skills/ppt-master" ]; then
  :
elif [ -d "$HOME/.claude/skills/ppt-master" ]; then
  :
else
  echo "ERROR: ppt-master not installed. Install via:" >&2
  echo "  git clone https://github.com/hugohe3/ppt-master ~/.codex/skills/ppt-master   # Codex" >&2
  echo "  git clone https://github.com/hugohe3/ppt-master ~/.agents/skills/ppt-master   # Codex" >&2
  echo "  git clone https://github.com/hugohe3/ppt-master ~/.claude/skills/ppt-master   # Claude Code" >&2
  exit 1
fi

node "$SCRIPT_DIR/make-pptx-deck.mjs" "$@"
