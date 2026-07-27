#!/usr/bin/env bash
# ZimaBlueAI Agent Skills · 安装器（Claude Code / OpenAI Codex CLI 通用）
#
# 从 dist/<harness>/*.zip 安装。包由 packaging/build.py 从单一源 skills/ 生成，
# 两个 harness 的差别只有安装根目录（.claude/ vs .codex/）与三个 skill 的 description。
#
# 用法：
#   bash packaging/install.sh                          # 自动探测已装的 harness
#   bash packaging/install.sh --harness claude         # 只装 Claude Code
#   bash packaging/install.sh --harness both           # 两个都装
#   bash packaging/install.sh --skill viz-deck         # 只装一个包
#   bash packaging/install.sh --project /path/to/repo  # 装到项目而非 $HOME
#   bash packaging/install.sh --no-agents              # 跳过 subagent
#   bash packaging/install.sh --dry-run                # 只打印，不动手

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST="$ROOT/dist"

HARNESS=""
ONLY_SKILL=""
TARGET="$HOME"
DRY_RUN=0
WANT_AGENTS=1

while [ $# -gt 0 ]; do
  case "$1" in
    --harness)   HARNESS="$2"; shift 2 ;;
    --skill)     ONLY_SKILL="$2"; shift 2 ;;
    --project)   TARGET="$2"; shift 2 ;;
    --no-agents) WANT_AGENTS=0; shift ;;
    --dry-run)   DRY_RUN=1; shift ;;
    -h|--help)   sed -n '1,18p' "$0"; exit 0 ;;
    *) echo "未知参数：$1" >&2; exit 2 ;;
  esac
done

if [ ! -d "$DIST" ]; then
  echo "没有 dist/。先构建：python packaging/build.py" >&2
  exit 1
fi

# —— 没指定就按 $HOME 下已存在的 harness 目录来探测 —— #
if [ -z "$HARNESS" ]; then
  detected=""
  [ -d "$HOME/.claude" ] && detected="claude"
  [ -d "$HOME/.codex" ] && detected="${detected:+$detected }codex"
  if [ -z "$detected" ]; then
    echo "没探测到 ~/.claude 或 ~/.codex。用 --harness claude|codex|both 明确指定。" >&2
    exit 1
  fi
  HARNESS="$detected"
  echo "探测到已安装的 harness：$HARNESS"
elif [ "$HARNESS" = "both" ]; then
  HARNESS="claude codex"
fi

unzip_to() {
  local zip="$1" dest="$2"
  if command -v unzip >/dev/null 2>&1; then
    unzip -o -q "$zip" -d "$dest"
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$zip" "$dest"
  elif command -v python >/dev/null 2>&1; then
    python -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$zip" "$dest"
  else
    echo "ERROR: PATH 上既没有 unzip 也没有 python" >&2
    exit 1
  fi
}

installed=0
for h in $HARNESS; do
  src="$DIST/$h"
  if [ ! -d "$src" ]; then
    echo "  跳过 $h：$src 不存在（跑 python packaging/build.py 生成）" >&2
    continue
  fi
  echo ""
  echo "[$h] → $TARGET/.$h/skills/"
  for zip in "$src"/*.zip; do
    [ -e "$zip" ] || continue
    archive="$(basename "$zip" .zip)"
    if [ -n "$ONLY_SKILL" ] && [ "$archive" != "$ONLY_SKILL" ]; then
      continue
    fi
    echo "  解开 $archive.zip"
    if [ "$DRY_RUN" -eq 0 ]; then
      unzip_to "$zip" "$TARGET"
    fi
    installed=$((installed + 1))
  done

  if [ "$WANT_AGENTS" -eq 0 ] && [ "$DRY_RUN" -eq 0 ]; then
    agents_dir="$TARGET/.$h/agents"
    if [ -d "$agents_dir" ]; then
      archive_dir="$agents_dir/.archive/no-agents-$(date +%Y%m%d-%H%M%S)"
      mkdir -p "$archive_dir"
      for f in "$agents_dir"/0[0-8]-*; do
        [ -e "$f" ] && mv -f "$f" "$archive_dir/"
      done
      echo "  --no-agents：subagent 已移到 $archive_dir"
    fi
  fi
done

if [ "$installed" -eq 0 ]; then
  echo "没有装上任何包。检查 --skill 名字，或先跑 python packaging/build.py" >&2
  exit 1
fi

cat <<'EOF'

装好了。

验证：
  Claude Code   /skills
  Codex CLI     /skills   （subagent 用 /agents）

可选桥接：
  ppt-master（真编辑 PPTX / TTS 旁白，MIT）
    git clone https://github.com/hugohe3/ppt-master ~/.claude/skills/ppt-master
    cd ~/.claude/skills/ppt-master && python -m venv .venv
    .venv/bin/pip install python-pptx edge-tts svglib reportlab Pillow numpy
  huashu-design（动画 / 视频 / 设计哲学）
    见 docs/install-guide.md

技能脚本会同时探测 ~/.codex、~/.agents、~/.claude 三个位置，桥接装在哪个下面都能找到。
EOF
