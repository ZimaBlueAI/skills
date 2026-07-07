#!/usr/bin/env bash
# OpenClaw · ZimaBlueAI 动效HTML+PPTX+频道对话交付 一键安装
# =========================================================
# 把生成能力(viz-deck / viz-charts [/ biz-html-viz])+ 频道对话交付技能
# (viz-channel)装进 OpenClaw 的 skills 目录,配齐依赖。
#
# 生成能力本体从【本仓库 claude-code-skills/】的 zip 取(默认),或 --from-github 实时拉。
# 频道交付技能(viz-channel)来自本目录 skills/。
#
# 用法:
#   bash install-openclaw-skills.sh                       # 默认装到 ~/.openclaw/skills
#   bash install-openclaw-skills.sh --target ~/.openclaw/skills
#   bash install-openclaw-skills.sh --with-bridges        # 连 huashu + ppt-master(出 MP4 / 可编辑 PPTX)
#   bash install-openclaw-skills.sh --with-biz            # 额外装 biz-html-viz(商业决策报告)
#   bash install-openclaw-skills.sh --minimal             # 只装动效 HTML 所需(viz-deck+viz-charts+频道技能)
#   bash install-openclaw-skills.sh --from-github         # 生成技能从 GitHub 拉而非本仓库 zip

set -u
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; RESET='\033[0m'

# ─── 参数 ───
TARGET="$HOME/.openclaw/skills"
WITH_BRIDGES=0
WITH_BIZ=0
MINIMAL=0
FROM_GITHUB=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target) TARGET="$2"; shift 2 ;;
        --with-bridges) WITH_BRIDGES=1; shift ;;
        --with-biz) WITH_BIZ=1; shift ;;
        --minimal) MINIMAL=1; shift ;;
        --from-github) FROM_GITHUB=1; shift ;;
        -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 本仓库根(claude-code-skills 在它下面)
REPO_ROOT="$(cd "$HERE/.." && pwd)"
LOCAL_CCS="$REPO_ROOT/claude-code-skills"
GH_REPO="https://github.com/ZimaBlueAI/skills.git"
TMP="${TMPDIR:-/tmp}/openclaw-zima-install-$$"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BLUE}  OpenClaw · 动效HTML + PPTX + 频道对话交付${RESET}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo
echo "目标目录: $TARGET"
echo "生成技能来源: $([ $FROM_GITHUB -eq 1 ] && echo 'GitHub 实时拉' || echo "本仓库 $LOCAL_CCS")"
echo "桥接(huashu+ppt-master): $([ $WITH_BRIDGES -eq 1 ] && echo 安装 || echo 跳过)"
echo "biz-html-viz: $([ $WITH_BIZ -eq 1 ] && echo 安装 || echo 跳过)"
echo "最小模式: $([ $MINIMAL -eq 1 ] && echo '是(仅动效HTML)' || echo 否)"
echo

# ─── [1] 基础环境 ───
echo -e "${BLUE}[1/5] 基础环境${RESET}"
MISSING=0
for tool in git node npm python3; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${RESET} $tool ($($tool --version 2>&1 | head -1))"
    else
        echo -e "  ${RED}✗${RESET} $tool"; MISSING=1
    fi
done
[ $MISSING -eq 1 ] && { echo -e "${RED}缺基础工具${RESET}  Ubuntu: sudo apt install git nodejs npm python3 python3-pip"; exit 1; }
if [ $MINIMAL -eq 0 ]; then
    command -v ffmpeg >/dev/null 2>&1 \
        && echo -e "  ${GREEN}✓${RESET} ffmpeg" \
        || echo -e "  ${YELLOW}⚠${RESET} ffmpeg 未装(只有 HTML→MP4 才需要)"
fi
echo

# ─── [2] 取得生成技能的 zip ───
echo -e "${BLUE}[2/5] 准备生成技能 (viz-deck / viz-charts$([ $WITH_BIZ -eq 1 ] && echo ' / biz-html-viz'))${RESET}"
mkdir -p "$TARGET"
EXTRACT="$TMP/extracted"
mkdir -p "$EXTRACT"

if [ $FROM_GITHUB -eq 1 ]; then
    echo -e "  ${YELLOW}→${RESET} clone $GH_REPO ..."
    git clone --depth 1 "$GH_REPO" "$TMP/repo" 2>/dev/null \
        && CCS="$TMP/repo/claude-code-skills" \
        || { echo -e "  ${RED}✗${RESET} clone 失败"; exit 1; }
else
    CCS="$LOCAL_CCS"
    [ -d "$CCS" ] || { echo -e "  ${RED}✗${RESET} 找不到 $CCS"; exit 1; }
fi

# 重装时不硬删旧版,移到 .zima-replaced/ 存档(遵守"只移动不删除")
ARCHIVE="$TARGET/.zima-replaced"
archive_existing() {  # <目标路径>
    local p="$1"
    if [ -e "$p" ]; then
        mkdir -p "$ARCHIVE"
        mv "$p" "$ARCHIVE/$(basename "$p").$(date +%Y%m%d%H%M%S).$$" 2>/dev/null || true
    fi
}

install_skill() {  # <zip路径> <技能名>
    local zip="$1" name="$2"
    if [ -f "$zip" ]; then
        unzip -o -q "$zip" -d "$EXTRACT"
        if [ -d "$EXTRACT/.claude/skills/$name" ]; then
            archive_existing "$TARGET/$name"
            cp -r "$EXTRACT/.claude/skills/$name" "$TARGET/$name"
            echo -e "  ${GREEN}✓${RESET} $name"
        else
            echo -e "  ${YELLOW}⚠${RESET} zip 内没找到 .claude/skills/$name"
        fi
    else
        echo -e "  ${YELLOW}⚠${RESET} 找不到 $zip"
    fi
}

install_skill "$CCS/viz-deck/viz-deck.zip" "viz-deck"
install_skill "$CCS/viz-charts/viz-charts.zip" "viz-charts"
# gzh-design(公众号排版)是纯文件夹,无 zip,直接拷
if [ -d "$CCS/gzh-design" ]; then
    archive_existing "$TARGET/gzh-design"
    cp -r "$CCS/gzh-design" "$TARGET/gzh-design"
    echo -e "  ${GREEN}✓${RESET} gzh-design (公众号排版)"
else
    echo -e "  ${YELLOW}⚠${RESET} 找不到 $CCS/gzh-design(公众号排版跳过)"
fi
if [ $WITH_BIZ -eq 1 ]; then
    install_skill "$CCS/biz-decision-stack/biz-decision-stack.zip" "biz-html-viz"
    if [ -d "$EXTRACT/.claude/agents" ]; then
        AG="$(dirname "$TARGET")/agents"; mkdir -p "$AG"
        cp -r "$EXTRACT/.claude/agents/." "$AG/" 2>/dev/null
        echo -e "  ${GREEN}✓${RESET} biz subagents → $AG (OpenClaw 子代理可选支持)"
    fi
fi
echo

# ─── [3] 安装频道交付技能 ───
echo -e "${BLUE}[3/5] 频道交付技能 viz-channel + gzh-channel${RESET}"
for CH in viz-channel gzh-channel; do
    if [ -d "$HERE/skills/$CH" ]; then
        archive_existing "$TARGET/$CH"
        cp -r "$HERE/skills/$CH" "$TARGET/$CH"
        chmod +x "$TARGET/$CH/scripts/"*.sh 2>/dev/null || true
        echo -e "  ${GREEN}✓${RESET} $CH → $TARGET/$CH"
    else
        echo -e "  ${RED}✗${RESET} 找不到 $HERE/skills/$CH"; exit 1
    fi
done
echo

# ─── [4] 依赖 ───
echo -e "${BLUE}[4/5] 依赖${RESET}"
# 频道投递(飞书adapter): requests + pyyaml
pip3 install --quiet requests pyyaml 2>/dev/null \
    && echo -e "  ${GREEN}✓${RESET} python: requests + pyyaml" \
    || echo -e "  ${YELLOW}⚠${RESET} pip 装 requests/pyyaml 失败(投递需要)"

# viz-charts 离线渲染(可选)
if [ $MINIMAL -eq 0 ] && [ -d "$TARGET/viz-charts/renderers/node" ]; then
    echo -e "  ${YELLOW}→${RESET} viz-charts 离线渲染 npm install ..."
    (cd "$TARGET/viz-charts/renderers/node" && npm install --silent 2>/dev/null) \
        && echo -e "  ${GREEN}✓${RESET} viz-charts 离线渲染就绪" \
        || echo -e "  ${YELLOW}⚠${RESET} 失败(inline CDN 模式仍可用)"
fi

# 桥接
if [ $WITH_BRIDGES -eq 1 ]; then
    HUASHU="$TARGET/huashu-design"
    if [ ! -d "$HUASHU" ]; then
        echo -e "  ${YELLOW}→${RESET} clone huashu-design ..."
        git clone --depth=1 https://github.com/alchaincyf/huashu-design.git "$HUASHU" 2>/dev/null && {
            cat > "$HUASHU/package.json" <<'JSON'
{ "name":"huashu-design-runtime","version":"1.0.0","private":true,
  "dependencies":{"playwright":"^1.48.0","sharp":"^0.33.5","pptxgenjs":"^3.12.0","pdf-lib":"^1.17.1"} }
JSON
            (cd "$HUASHU" && npm install --silent 2>/dev/null && npx playwright install chromium 2>/dev/null) \
                && echo -e "  ${GREEN}✓${RESET} huashu-design" \
                || echo -e "  ${YELLOW}⚠${RESET} huashu npm/playwright 部分失败"
        }
    else echo -e "  ${GREEN}✓${RESET} huashu-design 已存在"; fi

    PPTM="$TARGET/ppt-master"
    if [ ! -d "$PPTM" ]; then
        echo -e "  ${YELLOW}→${RESET} clone ppt-master ..."
        git clone --depth=1 https://github.com/hugohe3/ppt-master.git "$PPTM" 2>/dev/null && {
            (cd "$PPTM" && python3 -m venv .venv && \
             .venv/bin/pip install --quiet python-pptx edge-tts svglib reportlab Pillow numpy 2>/dev/null) \
                && echo -e "  ${GREEN}✓${RESET} ppt-master" \
                || echo -e "  ${YELLOW}⚠${RESET} ppt-master venv 部分失败"
        }
    else echo -e "  ${GREEN}✓${RESET} ppt-master 已存在"; fi
else
    echo -e "  ${YELLOW}⊝${RESET} 桥接跳过(动效 HTML 不需要;要 MP4/可编辑PPTX 加 --with-bridges)"
fi
echo

# ─── [5] 清理 + 自检 ───
# 不硬删,把临时解压目录移到存档(遵守"只移动不删除")
[ -d "$TMP" ] && { mkdir -p "$ARCHIVE"; mv "$TMP" "$ARCHIVE/_install-tmp.$$" 2>/dev/null || true; }
echo -e "${BLUE}[5/5] 自检${RESET}"
for s in viz-deck viz-charts viz-channel gzh-design gzh-channel; do
    [ -f "$TARGET/$s/SKILL.md" ] || [ -d "$TARGET/$s" ] \
        && echo -e "  ${GREEN}✓${RESET} $TARGET/$s" \
        || echo -e "  ${RED}✗${RESET} $TARGET/$s 缺失"
done
python3 "$TARGET/viz-channel/scripts/channel_deliver.py" --help >/dev/null 2>&1 \
    && echo -e "  ${GREEN}✓${RESET} channel_deliver.py 可运行" \
    || echo -e "  ${YELLOW}⚠${RESET} channel_deliver.py 自检失败(检查 requests)"
python3 "$TARGET/gzh-channel/scripts/gzh_card_send.py" --help >/dev/null 2>&1 \
    && echo -e "  ${GREEN}✓${RESET} gzh_card_send.py 可运行" \
    || echo -e "  ${YELLOW}⚠${RESET} gzh_card_send.py 自检失败(检查 requests)"
echo
echo -e "${BLUE}━━━ 完成 ━━━${RESET}"
echo "在你的频道(如飞书)@机器人 试一句:"
echo "  「做一份云度科技 Q2 业绩的动效 HTML 汇报,做完发我」"
echo
echo "OpenClaw 会:读 viz-channel → 频道里问清需求 → viz-deck 模式1 生成动效HTML"
echo "          → channel_send.sh 发回当前会话。"
echo "细节见: $TARGET/viz-channel/references/openclaw-channel.md"
