---
name: viz-deck
description: Generate keynote-grade HTML deliverables — five output modes (keynote-report, hi-fi prototype, slide deck, motion-stage video, editable-pptx) sharing one deep-space cyan/blue/gold design language. v2 bridges to huashu-design for HTML→MP4/GIF/PPTX export; v3 adds a second bridge to hugohe3/ppt-master for true native DrawingML PPTX with clickable shapes, master slides, real animations, and per-slide TTS narration. Includes 20 design philosophies (Pentagram / Field.io / Kenya Hara / Sagmeister etc.) and a 5-dimension expert critique (philosophy alignment / visual hierarchy / craft quality / functionality / originality, each 0-10 with radar). Use for stage reports, architecture deep-dives, competitive landscapes (live web research), iOS/Android/macOS hi-fi prototypes, presentation slide decks, hero/explainer motion videos, and editable native PPTX with narration + animations. NOT for engineering scan-reads or printable sign-off documents — those use biz-html-viz. Trigger on "讲演 / 演示报告 / keynote / 阶段报告 / 架构深研 / 竞品对比 / 高保真原型 / hi-fi prototype / iOS 原型 / 幻灯片 / 演讲 PPT / 动画 demo / hero video / 导出 MP4 / 导出 PPTX / 可编辑 PPT / native PPTX / 母版 / 旁白 / TTS narration / 5 维评审 / 设计风格 / 20 哲学".
license: MIT
---

# viz-deck: 讲演级可视化 · 五模产出

为客户演示、投资人路演、团队 keynote、客户原型评审、对外宣传视频、可编辑 PPT 交付提供**五种产出**，共享一套视觉语言。v2 通过 huashu-design 获得 HTML→MP4/PPTX 导出、20 哲学、5 维评审；**v3 新增 ppt-master 桥接**，获得真正可编辑的 native DrawingML PPTX（每个元素可点、母版可继承、TTS 旁白可嵌入）。

## 五种产出模式

| 模式 | 触发关键词 | 主模板 | 委派的桥接能力 |
|---|---|---|---|
| **1 · keynote-report** | 讲演 / 阶段报告 / 路演 / 走读 / 架构深研 / 竞品 | `stage-report.html` / `architecture-deep.html` / `competitive-landscape.html` | — |
| **2 · prototype**（高保真原型） | 做原型 / hi-fi / iOS 原型 / App mockup / 可点击 demo | `prototype-shell.html` | huashu：设备外壳 `*_frame.jsx` · Playwright 验证 |
| **3 · slide-deck**（演讲幻灯片，HTML→快速 PPTX） | 做幻灯片 / 做 PPT / 演讲稿 / TED 风 | `slide-deck.html` | huashu：`export_deck_pptx.mjs` · `export_deck_pdf.mjs` |
| **4 · motion-stage**（动画 + MP4） | 导出 MP4 / 60fps / 动效 demo / hero video / 解说视频 / voiceover | `motion-stage.html` | huashu：`render-video.js` · `convert-formats.sh` · `add-music.sh` · `narrate-pipeline.mjs` |
| **5 · pptx-deck**（**v3** · 真正可编辑 native PPTX） | 真正可编辑 PPT / native PPTX / 母版 / 旁白 / TTS / Powerpoint 里直接改 | `templates/pptx-deck-spec.example.json`（JSON spec） | **ppt-master**：`svg_to_pptx.py`（DrawingML） + `notes_to_audio.py`（TTS） + `register_template.py`（母版） |

> v1 / v2 用户：原 4 个模式**完全保持不变**。v3 只是在并列位置**新增**模式 5，独立 JSON 输入，独立产出可编辑 PPTX，对其他模式零影响。

### 模式 3 vs 模式 5 选哪个？

| 维度 | 模式 3 · slide-deck | 模式 5 · pptx-deck |
|---|---|---|
| 输入 | HTML（已写好的 `slide-deck.html`） | JSON spec（结构化字段） |
| 输出 PPTX 每个元素能点击 | 部分（text frame 可改，背景是 image） | **是**（每个矩形、圆、文字框、KPI 都是独立 `<p:sp>`） |
| 母版可继承 | 否（每页独立） | **是**（可 `register_template.py` 导入公司模板） |
| OOXML 原生动画/转场 | 否 | **是**（`--anim fade\|fly\|zoom`、`--trans push\|wipe` 等） |
| 旁白音频嵌入 | 否（PPT 内嵌不行） | **是**（edge-tts / ElevenLabs / MiniMax / Qwen / CosyVoice） |
| 输出 MP4 | 走模式 4 | **PowerPoint 自带**（File → Export → Create a Video，自动同步旁白+动画） |
| 适用场景 | 演讲者自己讲，幻灯片是辅助 | 交付给客户/同事，对方要在 PowerPoint 里改 |

## 与 biz-html-viz 的边界

| 维度 | biz-html-viz | viz-deck |
|---|---|---|
| 受众 | 工程师 / CEO / 董事会 | 客户 / 投资人 / 全员 keynote |
| 场景 | 5 分钟扫读、决策签字、打印归档 | 60-90 分钟走读、视觉记忆、对外宣传 |
| 风格 | 黑底 + 酸黄强调 + 等宽 + 零动效 | 深空蓝紫青 + Inter + 微动效 |
| 信息密度 | 极高 | 中等，叙事节奏优先 |
| v2 能力 | + 5 维评审用于设计 QA | + 4 模产出 + 20 哲学 + 5 维评审 + MP4/PPTX 导出 |

**同一项目可两个 skill 各出一份**：决策版用 biz-html-viz 打印归档，讲演版用 viz-deck 上台展示。

## 工作流程

### Step 1 — 强制读 design-system-deck

`references/design-system-deck.md` 定义了所有模板共享的 CSS 变量、组件库、动画规则、视觉禁令。**未读直接写 = 视觉不一致**。

### Step 2 — 识别用户意图，选模式

按上表关键词判断走哪个模式。**含混不清时主动确认**（"这是要 60 分钟讲演稿还是分页 PPT 还是动画视频？"），不要默认。

### Step 3 — （仅 v2）询问哲学方向（可选）

如果用户的输入暗示视觉品味偏好（例如"日系"、"严肃"、"硅谷风"、"奢华"、"科幻感"），或主动说"用 XX 风格"，先读 `references/design-philosophies.md`，从 20 哲学里选定 1 个写进生成参数。**没说就用 viz-deck 默认深空风**——不要为了用而用。

### Step 4 — 按模式执行

#### 模式 1（keynote-report）

| 子类型 | 模板 |
|---|---|
| 阶段汇报 / 项目状态 / Roadmap / 对外里程碑 | `stage-report.html` |
| 系统架构 / 治理模型 / 技术纵深 / ADR | `architecture-deep.html` |
| 竞品对比 / 技术雷达 / 市场格局 | `competitive-landscape.html` |

**Competitive-Landscape 必须先调研**——读 `references/research-playbook.md`，严禁仅凭训练数据写竞品对比。

#### 模式 2（prototype）

读 `references/prototype-mode.md` → 复制 `templates/prototype-shell.html` → 选设备外壳（iOS / Android / macOS / browser）→ 填 AppPhone 状态 → 真实素材（Wikimedia / Met / Unsplash）→ Playwright 点击测试。

#### 模式 3（slide-deck）

读 `references/slide-mode.md` → 复制 `templates/slide-deck.html` → 章节 3-5 / 总页 12-25 / 单页 ≤ 60 字 → 写 Speaker Notes → 用 `scripts/export-pptx.sh` 出可编辑 PPTX。

#### 模式 4（motion-stage）

读 `references/motion-mode.md` → 复制 `templates/motion-stage.html` → 8s 内完成完整运动叙事 → 用 `scripts/export-mp4.sh` 出 25fps+60fps+GIF 三件套 → 可选 BGM/voiceover。

#### 模式 5（pptx-deck · v3 真正可编辑 PPTX）

读 `references/pptx-master-bridge.md` → 复制 `templates/pptx-deck-spec.example.json` → 改字段（每页 layout + 数据）→ 跑 `scripts/export-editable-pptx.sh deck.json --theme deep-space --anim fade --trans fade`。

支持 8 个布局：`title-cover`、`agenda`、`section-divider`、`title-bullets`、`two-column`、`kpi-grid`、`pullquote`、`closing`。

主题 3 选 1：`deep-space`（viz-deck 默认）、`terminal`（给 biz-decision-stack 用）、`deck-light`（公司模板友好）。

要旁白？加 `--with-notes` 让脚本写 `speaker_notes/`，再跑 `scripts/embed-narration.sh ./<build_dir> --voice zh-CN-XiaoxiaoNeural` → 生成 `*_narrated.pptx`。在 PowerPoint 里走 File → Export → Create a Video 出 MP4，画面+动画+旁白自动对齐。

要继承公司模板？读 `references/master-templates.md`，跑 `register_template.py` 提取后再生成。

**与模式 3 的边界**：模式 3 是 HTML 优先（演讲者自己讲），模式 5 是交付给别人在 PowerPoint 里改。两者不互相替代。

### Step 5 — 填充内容

复制选定模板 → 替换所有 `{{占位符}}` → 输出到用户指定目录或 `output/`。

文件名格式：

- 模式 1：`{YYYY-MM-DD}-{type}-{slug}-deck.html`
- 模式 2：`{YYYY-MM-DD}-{slug}-prototype.html`
- 模式 3：`{YYYY-MM-DD}-{slug}-slides.html`（+ `.pptx` / `.pdf`）
- 模式 4：`{YYYY-MM-DD}-{slug}-motion.html`（+ `.mp4` / `-60fps.mp4` / `.gif`）
- 模式 5：`{YYYY-MM-DD}-{slug}-deck.json` → `{slug}_pptx_build/exports/{slug}.pptx`（+ `{slug}_narrated.pptx`）

### Step 6 — 一致性检查

| 模式 | 必查 |
|---|---|
| 1 | 每章 eyebrow + kicker-num + h2 + lead；reveal 覆盖；prefers-reduced-motion 降级；竞品引用 data-source |
| 2 | 设备外壳就位；AppPhone 状态切换；真实素材；Playwright 全按钮可点 |
| 3 | 章节 3-5；总页 12-25；字号 ≥ 20px；Speaker Notes 实写；PPTX 导出后真实文本框 |
| 4 | 录制画布 1920×1080；时长 ≤ 12s（无解说）；first-frame 不空；末帧 hold 0.5s |
| 5 | PPTX 用 unzip 检查 `ppt/slides/slide1.xml` 含多个 `<p:sp>`；PowerPoint 里 Tab 能逐个 shape 遍历；旁白模式下每页都有对应 mp3 |

### Step 7 —（v2 可选）5 维评审

读 `references/critique-5dim.md` → 对照 5 维给分 → 写 scores.json → 跑 `scripts/review-5dim.mjs` 生成评审 HTML（含雷达图）：

```bash
node scripts/review-5dim.mjs --input scores.json --output critique.html
```

**触发场景**：用户问"好不好看"、"再优化"、"做对了吗"、"评一下"。

## 桥接到 huashu-design（v2 模式 2/3/4 必要）

模式 2-4 都依赖 `~/.claude/skills/huashu-design/`。检测：

```bash
HUASHU="$HOME/.claude/skills/huashu-design"
test -f "$HUASHU/scripts/render-video.js" || echo "huashu-design not installed"
```

如果未安装，**告诉用户**（不要 silent fallback）：

```bash
git clone --depth=1 https://github.com/alchaincyf/huashu-design.git ~/.claude/skills/huashu-design
cd ~/.claude/skills/huashu-design && npm install && npx playwright install chromium
```

详细桥接协议见 `references/huashu-bridge.md`。

## 桥接到 ppt-master（v3 模式 5 必要）

模式 5 依赖 `~/.claude/skills/ppt-master/`。检测：

```bash
PPTM="$HOME/.claude/skills/ppt-master"
test -f "$PPTM/.venv/Scripts/python.exe" -o -f "$PPTM/.venv/bin/python" || echo "ppt-master not installed"
```

如果未安装，**告诉用户**（不要 silent fallback）：

```bash
git clone --depth=1 https://github.com/hugohe3/ppt-master.git ~/.claude/skills/ppt-master
cd ~/.claude/skills/ppt-master && python -m venv .venv
.venv/Scripts/pip install python-pptx edge-tts svglib reportlab Pillow numpy
```

详细桥接协议见 `references/pptx-master-bridge.md`、`references/editable-pptx.md`、`references/master-templates.md`、`references/narration-pptx.md`。

## 内容质量规则

- **每章 lead 一句话定调**——讲演节奏感来源
- **主视觉一份报告只一个**——orbit / canvas / SVG knowledge graph 选一种
- **章节数控制 5-8 章**（模式 1）/ 总页 12-25（模式 3）——少了没分量，多了观众累
- **每章 250-600 字**（模式 1）——讲演不是论文
- **所有数字用真值**——估值标 `[ESTIMATED]`，缺失标 `[N/A]`，**严禁编造**
- **竞品评价用对方的话**——不要用本项目术语去框对方

## 文件结构

```
viz-deck/
├── SKILL.md                          这份
├── references/
│   ├── design-system-deck.md         视觉规范（必读）
│   ├── research-playbook.md          竞品调研三档协议
│   ├── huashu-bridge.md              v2 · 桥接 huashu-design 的协议
│   ├── design-philosophies.md        v2 · 20 哲学的 viz-deck 适配
│   ├── critique-5dim.md              v2 · 5 维评审协议
│   ├── prototype-mode.md             v2 · 高保真原型协议
│   ├── slide-mode.md                 v2 · 幻灯片 + PPTX 导出协议
│   ├── motion-mode.md                v2 · 动画 + MP4 导出协议
│   ├── pptx-master-bridge.md         v3 · 桥接 ppt-master 的协议
│   ├── editable-pptx.md              v3 · PPTX 里哪些能点哪些不能
│   ├── master-templates.md           v3 · 母版/模板继承工作流
│   └── narration-pptx.md             v3 · TTS 旁白 + MP4 导出
├── templates/
│   ├── stage-report.html             阶段报告（v1）
│   ├── architecture-deep.html        架构深研（v1）
│   ├── competitive-landscape.html    竞品对比（v1）
│   ├── prototype-shell.html          v2 · 高保真原型骨架
│   ├── slide-deck.html               v2 · 幻灯片骨架
│   ├── motion-stage.html             v2 · 动画 stage 骨架
│   └── pptx-deck-spec.example.json   v3 · 可编辑 PPTX 的 JSON spec 范例
└── scripts/
    ├── export-mp4.sh                 v2 · MP4 / 60fps / GIF 导出
    ├── export-pptx.sh                v2 · HTML→快速 PPTX
    ├── review-5dim.mjs               v2 · 5 维评审 HTML 生成器
    ├── make-pptx-deck.mjs            v3 · JSON→SVG→ppt-master 编排
    ├── export-editable-pptx.sh       v3 · 模式 5 入口
    └── embed-narration.sh            v3 · TTS 旁白嵌入 + 重建 PPTX
```

## 反模式

- ❌ 跳过 design-system-deck.md 直接写
- ❌ 4 个模式视觉风格漂移
- ❌ Competitive 模板没做 web_search 就写
- ❌ 章节缺 eyebrow / kicker-num / lead 任一（模式 1）
- ❌ 一份报告塞两种主视觉
- ❌ 用 biz-html-viz 的黑黄配色（那是另一个 skill）
- ❌ 未提供 prefers-reduced-motion 降级
- ❌ 留下未替换的 `{{占位符}}`
- ❌ 模式 2 不带设备外壳就交付
- ❌ 模式 3 字号 < 20px（投影看不清）
- ❌ 模式 4 录制画布 ≠ 1920×1080 或 一镜超过 12s 无变化
- ❌ 5 维评审任意一项给 10 分（10 留给真"惊艳"产出）
- ❌ 把 huashu 的资源**复制**进 viz-deck（违反桥接协议）
- ❌ 同一份 deck 混合 2 个哲学（哲学一致性必扣分）
