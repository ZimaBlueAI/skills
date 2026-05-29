# codex-skills · 安装、配置、使用说明

**OpenAI Codex CLI 版** · v3.0 · 2026-05-13

> 与 [`claude-code-skills/skills-install-guide.md`](../claude-code-skills/skills-install-guide.md) 同源同构，仅适配到 Codex CLI 的 `.codex/skills/` + `.codex/agents/` 目录结构。skill 内容一字不差。

---

## 📋 目录

- [01 · skills 是什么](#01--skills-是什么)
- [02 · 前置要求](#02--前置要求)
- [03 · 安装步骤](#03--安装步骤)
- [04 · subagent 触发协议](#04--subagent-触发协议)
- [05 · 项目级 vs 全局](#05--项目级-vs-全局)
- [06 · v2 huashu-design 桥接](#06--v2-huashu-design-桥接)
- [07 · v3 ppt-master 桥接](#07--v3-ppt-master-桥接)
- [08 · 与 Claude Code 共存](#08--与-claude-code-共存)
- [09 · 疑难排查](#09--疑难排查)

---

## 01 · skills 是什么

完全等同于 Claude Code 版。各 skill 互不依赖，可选装。

### biz-decision-stack（约 223 KB zip）

终端风决策链 7 subagents + 1 skill：

| Subagent | 路由模板 | 用途 |
|---|---|---|
| `01-board-advisor` | `board-brief.html` | 投资人 / 董事会简报 |
| `02-ceo-decision` | `ceo-canvas.html` | CEO 决策画布 |
| `03-chief-architect` | `tech-roadmap.html` | 技术路线 |
| `04-product-manager` | `mrd-report.html` / `project-board.html` | MRD 双模 |
| `05-dev-test-lead` | `dev-report.html` | 开发 / QA 汇报 |
| `06-acceptance-retro` | `retro-report.html` | 验收 / 复盘 |
| `07-design-critic` 🆕 v2 | `design-critique.html` | 5 维评审 |
| `00-all-hands-orchestrator` | `index.html` | 全流程编排（7 个串起来） |

**v3 起**：可选 ppt-master 桥接出口 8 个决策 layout 的可编辑 PPTX。

### viz-deck（约 416 KB zip）

讲演风深度报告，**v3 起 5 模产出**：

| 模式 | 触发 | 输出 |
|---|---|---|
| 1 · keynote-report | 阶段汇报 / 架构 / 竞品 | HTML |
| 2 · prototype 🆕 v2 | iOS / Android / macOS / 浏览器原型 | HTML + AppPhone 状态 |
| 3 · slide-deck 🆕 v2 | 演讲幻灯片 | HTML + 快速 PPTX + PDF |
| 4 · motion-stage 🆕 v2 | hero / 解说视频 | HTML + MP4 + GIF + BGM |
| 5 · pptx-deck 🆕 v3 | 给 stakeholder 编辑的 PPT | 真编辑 PPTX + TTS 旁白 |

### viz-charts（约 403 KB zip）

被前两者调用的能力 skill，**v3 起 6 类视觉**：

Mermaid · ECharts · SVG 组件 · 3D KG · Motion · **Native PPTX chart 🆕 v3**

### zima-html-ppt（约 18 KB zip）

ZimaBlueAI 现场讲演 deck：暖纸编辑风单文件 HTML 幻灯片 + 演讲者模式（S 键提词器、逐字稿、计时、议程）。适合内训课件、路演稿、训战材料和上台讲的 HTML PPT。

---

## 02 · 前置要求

| 组件 | 最低版本 | 用途 | 必装？ |
|---|---|---|---|
| OpenAI Codex CLI | 最新版 | 跑 skill 的载体 | ✓ 必装 |
| Node.js | 18.0+ | 离线图表渲染 / KG builders / PPTX bridge driver | viz-charts / v2 / v3 需要 |
| npm | 9.0+ | 装 echarts/mermaid 离线包、huashu runtime | viz-charts / v2 |
| Chromium | — | Mermaid 离线 SVG、MP4 录制、PPTX 导出 | v2 模式（playwright 自动装） |
| ffmpeg | 4.0+ | MP4 编码 / 60fps / GIF / BGM | v2 motion-stage |
| huashu-design | latest | v2 工具链 | v2 prototype/slide/motion |
| **ppt-master** | latest | v3 真编辑 PPTX / TTS | **v3 模式 5 / 决策 PPTX / 数据 chart** |
| **Python 3** | 3.10+ | v3 ppt-master runtime | v3 模式必需 |

---

## 03 · 安装步骤

### 推荐：一键脚本

```bash
# Linux / macOS
bash codex-skills/install.sh

# Windows (PowerShell)
.\codex-skills\install.ps1
```

### 手动：解 zip

**全局**（推荐，所有项目共享）：

```bash
unzip -o codex-skills/biz-decision-stack/biz-decision-stack.zip -d ~/
unzip -o codex-skills/viz-deck/viz-deck.zip -d ~/
unzip -o codex-skills/viz-charts/viz-charts.zip -d ~/
unzip -o codex-skills/zima-html-ppt/zima-html-ppt.zip -d ~/
```

落点：

```
~/.codex/skills/biz-html-viz/
~/.codex/skills/viz-deck/
~/.codex/skills/viz-charts/
~/.codex/skills/zima-html-ppt/
~/.codex/agents/00-..08-*.toml
```

**项目级**（仅在某个项目里启用）：

```bash
unzip -o codex-skills/biz-decision-stack/biz-decision-stack.zip -d /path/to/project/
unzip -o codex-skills/viz-deck/viz-deck.zip -d /path/to/project/
unzip -o codex-skills/viz-charts/viz-charts.zip -d /path/to/project/
unzip -o codex-skills/zima-html-ppt/zima-html-ppt.zip -d /path/to/project/
```

落点：`/path/to/project/.codex/skills/` + `/path/to/project/.codex/agents/`。

### 验证

```
codex> /skills
```

应能看到 `biz-html-viz` · `viz-deck` · `viz-charts` · `zima-html-ppt`。

```
codex> /agents
```

应能看到 8 个 subagent。

---

## 04 · subagent 触发协议

Codex CLI 支持三种触发方式，三个都好用：

### A. 自然语言（隐式）

```
你说："给瑞林这个项目做个董事会简报"
Codex：自动匹配 description → 启动 01-board-advisor
```

### B. 显式 $ 调用

```
codex> $board-advisor 给瑞林做董事会简报
```

### C. 全流程

```
codex> $all-hands-orchestrator 走一遍全流程
```

或自然语言："走一遍全流程"、"all hands"、"end-to-end"。

orchestrator 会按顺序串调：board → CEO → architect → PM(MRD) → PM(Delivery) → dev-test → retro，最后生成 `index.html` 串成一个连贯叙事。**v3 起**：可在最后追加 design-critic 做 5 维评审。

---

## 05 · 项目级 vs 全局

| 维度 | 项目级 | 全局 |
|---|---|---|
| 落点 | `<project>/.codex/skills/` + `<project>/.codex/agents/` | `~/.codex/skills/` + `~/.codex/agents/` |
| 受影响范围 | 仅该项目 | 所有项目 |
| 升级 | 重解 zip 到该项目 | 重解 zip 到 `~/` |
| 推荐场景 | 团队仓库附带 skill 给协作者 | 个人长期使用 |

**Codex 同时识别两层**，项目级优先于全局。

---

## 06 · v2 huashu-design 桥接

解锁动画 / 视频 / 设计哲学 / 5 维评审。

```bash
git clone --depth=1 https://github.com/alchaincyf/huashu-design.git ~/.codex/skills/huashu-design
cd ~/.codex/skills/huashu-design

cat > package.json <<'JSON'
{
  "name": "huashu-design-runtime",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "playwright": "^1.48.0",
    "sharp": "^0.33.5",
    "pptxgenjs": "^3.12.0",
    "pdf-lib": "^1.17.1"
  }
}
JSON
npm install && npx playwright install chromium

ffmpeg -version || echo "请先安装 ffmpeg"
```

> 不要给 huashu 的 `package.json` 加 `"type": "module"`——会破坏它的 CommonJS 脚本（如 `render-video.js`）。

**桥接调用**：所有路径走 `$HOME/.codex/skills/huashu-design/scripts/...`，HTML stage 必须在首次渲染后设 `window.__ready = true`。

**许可证**：huashu-design 个人免费，**商用独立授权**（USD 1,800/年 或 USD 3,500 永久）。

---

## 07 · v3 ppt-master 桥接

解锁：真编辑 PPTX / TTS 旁白 / 母版继承 / 数据绑定 chart。MIT 协议，无商用限制。

```bash
git clone --depth=1 https://github.com/hugohe3/ppt-master.git ~/.codex/skills/ppt-master
cd ~/.codex/skills/ppt-master
python -m venv .venv

# Linux / macOS
.venv/bin/pip install python-pptx edge-tts svglib reportlab Pillow numpy
# Windows
# .venv/Scripts/pip install python-pptx edge-tts svglib reportlab Pillow numpy

# 验证
.venv/bin/python -c "import pptx, edge_tts; print('ok')"
```

可选附加（图像生成、语音克隆）：

```bash
.venv/bin/pip install openai google-genai elevenlabs
```

### v3 调用约定

| Skill | 入口 | 输入 | 输出 |
|---|---|---|---|
| viz-deck 模式 5 | `scripts/export-editable-pptx.sh <spec.json>` | 8-layout JSON | 真编辑 PPTX |
| viz-deck 旁白 | `scripts/embed-narration.sh <build_dir>` | speaker_notes/*.txt | 含 MP3 嵌入的 PPTX |
| biz-decision PPTX | `scripts/export-decision-pptx.sh <spec.json>` | 8-layout 决策 JSON | 终端风可编辑 PPTX |
| viz-charts native chart | `scripts/export-chart-pptx.sh <spec.json>` | ECharts spec | 数据绑定 PPTX |

### 验证脚本

```bash
PPTM="$HOME/.codex/skills/ppt-master"
PY="$PPTM/.venv/bin/python"
[ -f "$PY" ] || PY="$PPTM/.venv/Scripts/python.exe"

test -f "$PY" && \
test -f "$PPTM/skills/ppt-master/scripts/svg_to_pptx.py" && \
"$PY" -c "import pptx, edge_tts" 2>/dev/null && \
echo "OK" || echo "ppt-master MISSING — 见第 7 节安装"
```

### 可编辑性验证

```bash
# 每张 slide 应该有数十个独立 native shape
unzip -p deck.pptx ppt/slides/slide1.xml | grep -c "<p:sp>"

# native chart 才有这一行
unzip -l deck.pptx | grep "ppt/charts/chart"
```

如果 `<p:sp>` 是 0 或 1 → 退化成单图；改用 `--only native` 重生成。

---

## 08 · 与 Claude Code 共存

完全兼容。两个 harness 在同一台机上互不冲突：

| | Claude Code | Codex |
|---|---|---|
| skill 目录 | `~/.claude/skills/<name>/` | `~/.codex/skills/<name>/` |
| subagent 目录 | `~/.claude/agents/<name>.md` | `~/.codex/agents/<name>.toml` |
| 桥接 ppt-master | 装到 `~/.claude/skills/ppt-master/` 或 `~/.codex/skills/ppt-master/`（脚本自动探测） | 同 |
| 桥接 huashu-design | 同上 | 同 |

**ppt-master 桥接脚本** (`make-pptx-deck.mjs` / `make-decision-pptx.mjs` / 几个 `.sh`) 已加入三档探测：

```
$PPT_MASTER_HOME → ~/.codex/skills/ppt-master → ~/.agents/skills/ppt-master → ~/.claude/skills/ppt-master
```

所以**只装一份桥接、两个 harness 都能用**，不需要重复安装。

唯一忌：**别同一个项目同时解两份 zip**（一个 `.claude/`、一个 `.codex/`）——不冲突但没意义，且会让维护混乱。

---

## 09 · 疑难排查

### Codex 看不到 skill

```bash
ls -la ~/.codex/skills/         # 应有 biz-html-viz / viz-deck / viz-charts / zima-html-ppt
ls -la ~/.codex/agents/          # 应有 00-..08-*.toml
```

如目录为空：重跑 `install.sh` / `install.ps1`。

### subagent 触发不到

Codex 的 description 匹配偏严格，**用 `$<agent-name>` 强制触发**测试：

```
codex> $design-critic
```

如果显式调用都失败 → TOML 文件可能损坏，对照 `agents-toml/*.toml` 重置。

### v3 模式失败

Codex 跑 `viz-deck pptx-deck` 报错？最常见原因：

1. ppt-master 没装 → 第 07 节安装
2. ppt-master 装了但 venv 没建 → `python -m venv .venv` + pip install
3. svg_to_pptx.py 报 GBK 编码错 → 这是 Windows 终端的问题，已在 echarts_to_pptx.py 修复；其他脚本已规避

### 桥接探测失败

手动指定：

```bash
export PPT_MASTER_HOME="$HOME/.codex/skills/ppt-master"
~/.codex/skills/viz-deck/scripts/export-editable-pptx.sh my-deck.json
```

如果路径正确仍报错 → 检查 venv 是否在该目录下（`.venv/bin/python` 或 `.venv/Scripts/python.exe`）。

---

**codex-skills v3.0** · 2026-05-13 · 与 claude-code-skills v3.0 同源同构 · Apache 2.0
