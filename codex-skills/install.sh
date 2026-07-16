#!/usr/bin/env bash
# codex-skills · one-shot installer
#
# Drops the six skills into $HOME/.codex/skills/ and the 9 subagents into $HOME/.codex/agents/.
# Idempotent — re-running upgrades in place.
#
# Usage:
#   bash install.sh                    # install all six + agents
#   bash install.sh --skill viz-deck   # install just one skill (no agents)
#   bash install.sh --no-agents        # all skills, but skip the TOML agents
#   bash install.sh --dry-run          # show what would be done

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=0
WANT_AGENTS=1
ONLY_SKILL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --skill)     ONLY_SKILL="$2"; shift 2 ;;
    --no-agents) WANT_AGENTS=0; shift ;;
    --dry-run)   DRY_RUN=1; shift ;;
    -h|--help)
      sed -n '1,15p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

run() {
  if [ "$DRY_RUN" -eq 1 ]; then echo "DRY: $*"; else "$@"; fi
}

extract() {
  local zip="$1" dest="$2"
  if [ ! -f "$zip" ]; then
    echo "  warn: $zip not found, skipping" >&2
    return
  fi
  echo "  unzip $(basename "$zip") -> $dest"
  if [ "$DRY_RUN" -eq 0 ]; then
    if command -v unzip >/dev/null 2>&1; then
      unzip -o -q "$zip" -d "$dest"
    elif command -v python3 >/dev/null 2>&1; then
      python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$zip" "$dest"
    elif command -v python >/dev/null 2>&1; then
      python -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$zip" "$dest"
    else
      echo "ERROR: neither unzip nor python found on PATH" >&2
      exit 1
    fi
  fi
}

echo "[codex-skills] target: \$HOME/.codex/skills/ + \$HOME/.codex/agents/"
run mkdir -p "$HOME/.codex/skills" "$HOME/.codex/agents"

install_skill() {
  local repo_dir="$1" name="$2"
  local zip="$SCRIPT_DIR/$repo_dir/${repo_dir}.zip"
  extract "$zip" "$HOME"
  echo "  [ok] $name"
}

if [ -z "$ONLY_SKILL" ] || [ "$ONLY_SKILL" = "biz-decision-stack" ]; then
  install_skill "biz-decision-stack" "biz-html-viz + 8 subagents"
elif [ "$WANT_AGENTS" -eq 0 ]; then
  echo "  (skipping biz-decision-stack since --skill set elsewhere)"
fi

if [ -z "$ONLY_SKILL" ] || [ "$ONLY_SKILL" = "viz-deck" ]; then
  install_skill "viz-deck" "viz-deck"
fi

if [ -z "$ONLY_SKILL" ] || [ "$ONLY_SKILL" = "viz-charts" ]; then
  install_skill "viz-charts" "viz-charts"
fi

if [ -z "$ONLY_SKILL" ] || [ "$ONLY_SKILL" = "zima-html-ppt" ]; then
  install_skill "zima-html-ppt" "zima-html-ppt"
fi

if [ -z "$ONLY_SKILL" ] || [ "$ONLY_SKILL" = "gzh-design" ]; then
  install_skill "gzh-design" "gzh-design"
fi

if [ -z "$ONLY_SKILL" ] || [ "$ONLY_SKILL" = "zima-design" ]; then
  install_skill "zima-design" "zima-design"
fi

if [ "$WANT_AGENTS" -eq 0 ]; then
  echo "[codex-skills] --no-agents passed, archiving freshly-extracted agents ..."
  if [ "$DRY_RUN" -eq 0 ]; then
    archive="$HOME/.codex/agents/.archive/no-agents-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$archive"
    for f in "$HOME/.codex/agents/"0[0-8]-*.toml; do
      [ -f "$f" ] && mv -f "$f" "$archive/"
    done
  fi
fi

echo ""
echo "[codex-skills] installed at:"
echo "  $HOME/.codex/skills/ (skill bodies)"
if [ "$WANT_AGENTS" -eq 1 ]; then
  echo "  $HOME/.codex/agents/ (9 TOML subagents)"
fi
echo ""
echo "Next steps:"
echo "  1) In Codex CLI run /skills to confirm the five skills appear"
echo "  2) (Optional) Install ppt-master to unlock v3 editable-PPTX:"
echo "       git clone https://github.com/hugohe3/ppt-master ~/.codex/skills/ppt-master"
echo "       cd ~/.codex/skills/ppt-master && python -m venv .venv"
echo "       .venv/bin/pip install python-pptx edge-tts svglib reportlab Pillow numpy"
echo "  3) (Optional) Install huashu-design to unlock v2 motion/video/PPTX:"
echo "       git clone https://github.com/alchaincyf/huashu-design ~/.codex/skills/huashu-design"
echo "       (see INSTALL.md for the package.json + ffmpeg setup)"
