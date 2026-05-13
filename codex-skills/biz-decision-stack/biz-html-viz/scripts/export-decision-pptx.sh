#!/usr/bin/env bash
# biz-decision-stack → editable PPTX wrapper
# Wraps make-decision-pptx.mjs (terminal-themed JSON → SVG → ppt-master → PPTX)
#
# Usage:
#   ./export-decision-pptx.sh <spec.json> [--out DIR]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <spec.json> [--out DIR]" >&2
  echo ""
  echo "Spec examples in: $SCRIPT_DIR/../specs/" >&2
  exit 2
fi

# Detect ppt-master across both harness install locations
if [ -n "${PPT_MASTER_HOME:-}" ] && [ -d "$PPT_MASTER_HOME" ]; then
  :
elif [ -d "$HOME/.agents/skills/ppt-master" ]; then
  :
elif [ -d "$HOME/.claude/skills/ppt-master" ]; then
  :
else
  echo "ERROR: ppt-master not installed. Run one of:"
  echo "  git clone https://github.com/hugohe3/ppt-master ~/.agents/skills/ppt-master   # Codex"
  echo "  git clone https://github.com/hugohe3/ppt-master ~/.claude/skills/ppt-master   # Claude Code"
  echo "Then create the venv:"
  echo "  cd <install-path> && python -m venv .venv"
  echo "  .venv/Scripts/pip install python-pptx edge-tts svglib reportlab Pillow numpy"
  exit 1
fi

node "$SCRIPT_DIR/make-decision-pptx.mjs" "$@"
