#!/usr/bin/env bash
# viz-charts → editable PPTX chart
# Takes a chart spec JSON (or raw ECharts option) and emits a .pptx
# whose single slide contains a data-bound native chart.
#
# Open the .pptx in PowerPoint and:
#   - Right-click chart → "Edit Data" → opens spreadsheet with your data
#   - Change chart type via Chart Design → real conversion (not redraw)
#   - Recolor series → applies to data, not pixels
#
# Usage:
#   ./export-chart-pptx.sh <spec.json> [-o out.pptx]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <spec.json> [-o out.pptx]" >&2
  echo ""
  echo "Specs in: $SCRIPT_DIR/../specs/"
  exit 2
fi

# Detect ppt-master across current and legacy harness install locations
if [ -n "${PPT_MASTER_HOME:-}" ] && [ -d "$PPT_MASTER_HOME" ]; then
  PPT_MASTER="$PPT_MASTER_HOME"
elif [ -d "$HOME/.codex/skills/ppt-master" ]; then
  PPT_MASTER="$HOME/.codex/skills/ppt-master"
elif [ -d "$HOME/.agents/skills/ppt-master" ]; then
  PPT_MASTER="$HOME/.agents/skills/ppt-master"
elif [ -d "$HOME/.claude/skills/ppt-master" ]; then
  PPT_MASTER="$HOME/.claude/skills/ppt-master"
else
  echo "ERROR: ppt-master not installed. Run one of:"
  echo "  git clone https://github.com/hugohe3/ppt-master ~/.codex/skills/ppt-master   # Codex"
  echo "  git clone https://github.com/hugohe3/ppt-master ~/.agents/skills/ppt-master   # Codex"
  echo "  git clone https://github.com/hugohe3/ppt-master ~/.claude/skills/ppt-master   # Claude Code"
  echo "Then: cd <install-path> && python -m venv .venv && .venv/Scripts/pip install python-pptx"
  exit 1
fi

PYTHON="$PPT_MASTER/.venv/Scripts/python.exe"
[ -f "$PYTHON" ] || PYTHON="$PPT_MASTER/.venv/bin/python"

if [ ! -f "$PYTHON" ]; then
  echo "ERROR: venv not found at $PPT_MASTER/.venv — run python -m venv .venv inside that dir." >&2
  exit 1
fi

SPEC="$1"; shift
OUT=""
while [ $# -gt 0 ]; do
  case "$1" in
    -o|--out) OUT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$OUT" ]; then
  BASE="$(basename "$SPEC" .json)"
  OUT="${BASE}_chart.pptx"
fi

"$PYTHON" "$SCRIPT_DIR/echarts_to_pptx.py" "$SPEC" -o "$OUT"
