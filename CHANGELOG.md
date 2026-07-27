# Changelog

All notable changes to **ZimaBlueAI Agent Skills** are documented here.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
and the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

---

## [Unreleased]

### Added — `produce-cinematic-video`：ZimaBlueAI 可恢复影视生产技能

- 将同题研究、策划、剧本、角色/场景/道具设计、分镜、生成式视频、专业剪辑、声音后期、
  技术 QC、创意评分、营销诊断和发布复盘组织为可暂停、可重做、可恢复的工程图。
- 提供 7 张动画专业工位协议卡、离线 SVG 流程看板、项目历史版本、节点重做与结构化
  `project.json` 契约；单 Agent 和具备子任务能力的宿主共享同一产物协议。
- 接入安全闸门明确的图像/视频适配器、本地 GPU 优先的 Qwen3-TTS 与 IndexTTS2、
  低配 Pocket TTS/LuxTTS，以及 GPT-SoVITS UVR5 音源分离、混音和口型/对白定位工具。
- 用户配置统一为跨平台用户目录中的 `.env.local`；TUI 只询问实际启用能力所需字段，
  密钥隐藏输入，大模型与隔离运行时不进入 skill 或漫游配置目录。
- Codex 与 Claude Code 两个安装包均由同一份 99 文件 UTF-8 源生成，逐文件哈希一致；
  包内只含 `.env.local.example`，不含用户配置、模型、媒体、缓存或凭据。

### Security — `produce-cinematic-video` 发布净化

- 移除私人项目名称、内部绝对路径、个人角色示例及其图片；修复一份非 UTF-8 元数据文件。
- 顶层加入 Apache-2.0 `LICENSE` 与 ZimaBlueAI `NOTICE`；第三方名称仅用于说明可选互操作，
  不表示赞助、背书、合作或参与本 skill 创作。
- 远程上传、付费调用、声音克隆和外部发布分别设独立批准闸门；“已填写 API key”
  不再被视为调用授权，未知价格也不再被视为免费。
- 移除固定供应商优劣排序、历史价格、版权安全保证和平台流量操纵话术；改为能力匹配、
  当前条款核对、权利记录和一方数据驱动的可审计决策。

### Changed — 双 harness 目录合并为单一源（skill 直接放仓库根）

`claude-code-skills/` 与 `codex-skills/` 两套目录合并——8 个 skill 直接落在仓库根，
由 `packaging/build.py` 生成两个 harness 的安装包（判定规则：根下带顶层 `SKILL.md`
的目录就是一个 skill）。合并前做了全量比对，结论是：
**两侧本就同源**，差异只有可自动生成的适配（Codex 侧的短 description、脚本里的
ppt-master 路径探测），没有需要人工取舍的功能分叉。

合并同时暴露并解决了四个真问题：

- **三个 skill 的源码只存在于 zip 里** —— `biz-html-viz` / `viz-deck` / `viz-charts`
  在 claude 侧只有 `.zip`，仓库里没有铺开的 `SKILL.md`：读不到、diff 不了、review 不了。
  唯一可读的源反而在 codex 侧。现在全部铺开在仓库根。
- **两处已经悄悄分叉** —— `gzh-design` 的两个主题文件（引用框 `solid` vs `dashed`）与
  `produce-cinematic-video` 的 `SKILL.md` + 旧 `config.example.json`（现为内部
  `assets/config.defaults.json`），都是改动只落了一侧。
  按较新的 codex 侧收敛。
- **skill 列表不对称** —— `web-shader-extractor` 只在 claude 侧。
- **`cinematic_config.py` 硬编码 `.codex/`** —— 装在 Claude Code 下会指错自己的安装位置；
  改为按 `.codex` → `.agents` → `.claude` 顺序探测。同类的 ppt-master 探测本就三路径全覆盖，
  合并后 claude 侧顺带补齐（过去缺 `.codex/`）。

新增：

- `packaging/build.py` —— `--verify` 可与旧 zip 逐字节核对，`--check` 只验源不产出。
- `packaging/harness.toml` —— harness 差异的唯一声明处：安装根目录 + 三个 Codex description 变体。
- `packaging/install.sh` / `install.ps1` —— 双 harness 通用安装器（原来只有 Codex 版），
  支持 `--harness claude|codex|both`、`--skill`、`--project`、`--dry-run`。
- `packaging/agents/{claude-md,codex-toml}/` —— 9 个 subagent 的两种序列化格式并列存放。
- `dist/claude/` + `dist/codex/` —— 16 个包（8 skill × 2 harness）。
- `docs/` —— 安装手册从两个 harness 目录里挪出来集中放置。

旧目录已归档到 `_trash/legacy-harness-dirs-20260727/`，未硬删。

### Removed — 频道交付层（OpenClaw / Hermes）

`openclaw-skills/` 与 `hermes-skills/`（`viz-channel` / `gzh-channel`）下线。
理由：这两个 harness 可以直接安装本仓库的 Claude / Codex 包，再维护一层薄桥接属于重复。
v0.5 的实现保留在 git 历史里。同时 `taste-engine/` 独立目录移除——它已在 v0.7
整目录收编为 `zima-design` 的 taste 引擎（见 `zima-design/NOTICE.md`）。

### Added — `zima-html-ppt` v2：工程治理层（借鉴 qiaomu-bento-ppt 的纪律，不引入 bento）

原本这个技能只有「拷模板填内容 + 设计规范」，做完的 deck 想改一版只能让人重读 HTML。
参考 [joeseesun/qiaomu-bento-ppt](https://github.com/joeseesun/qiaomu-bento-ppt)（MIT，向阳乔木）
的工作流骨架与闸门思路，把它升级成**有事实源、有机器闸门、有证据纪律**的交付链路。
只借方法论，没有移植其内置的 `nyblnet/bento` shell——视觉与演讲者模式仍是 ZimaBlue Editorial 自有。
署名见 `zima-html-ppt/NOTICE.md`。

- **`deck.json` 文档契约 v1.0**（`references/deck-json.md`）：5 种版式 × 12 种内容块 × 5 类逐字稿标签。
  产物末尾内嵌 `<script id="zima-doc">` 存原始 JSON，`extract(build(x)) == x` 有回归用例保证——
  **改稿从"重读 HTML"变成"改 JSON 再 build"**。
- **`scripts/zima_deck.py`**（locate / build / extract / validate，纯标准库、不联网）：
  结构校验 18 项 error + 11 项 warning；图表配置编译成纯 JSON（禁 function formatter）；
  `--legacy` 可把手写 deck 兜底反解成 JSON。
- **七道闸门**（`references/gates.md`）：Route / Structure / Identity / Shell / Quality / Browser /
  Rollback。身份闸门用 `deckId` 锚定，改稿 `--identity-source` 对不上直接拒绝构建；
  回滚边界默认写新文件，源文件不动。
- **`missing evidence` 证据纪律**：报告默认携带 `browser visual review`，人没真在浏览器里看过
  就不许写「已验证」。
- **方案先行**（`references/workflow.md` + `templates/deck-plan-template.md`）：意图卡 →
  `1a` 说服 / `2b` 决策 / `3c` 训战三方向选择卡 → 逐页计划表（含**视觉所有者**：一条信息只由
  标题/图表/卡片/正文/逐字稿其中一层负责，屏幕上的字和嘴里念的话不许是同一句）。
- **`evals/`**：`run_fixtures.py`（15 项，好稿放行 + 坏稿逐类拦截 + 反解一致）、
  `trigger_cases.json` + `scripts/trigger_eval.py`（16 项路由边界，含让给
  biz-html-viz / viz-deck / viz-charts 的用例）。
- **`templates/zima-ppt-shell.html`**：build 用的数据驱动 shell（图表规格由 JSON 装载）。
- **`examples/`**：一份完整走过全链路的示范交付——`deck-plan.md`（含视觉所有者列与三项
  missing evidence）+ `deck.json` + 14 页产物 + 闸门报告。题材就是这次升级本身，
  **每个数字都可回溯到代码计数或测试输出**；用到 11/12 种块型（`html` 逃生口刻意不用），
  结构闸门零 error、质量闸门零 warning。

### Fixed — `zima-html-ppt` 母版三个真实渲染缺陷（浏览器复核查出）

按新写的浏览器验收清单实跑，查出的都是 starter 模板（以及沿用它的 D1/D2/D3 母版）里的老问题：

- **对比条从来没显示过**：`.fill` 是 `<i>`，默认 `display:inline`，宽高不生效，整根条形是 0×0。
  补 `display:block`，并把这条加进 shell 闸门签名，防止再漏。
- **页脚右侧文字被右下角固定的 `.nav` 压住**：`.footer` 补 `padding-right:200px`，窄屏还原为纵向排列。
- **桌面端仍能横拖 25px**：待入场幻灯片带 `translateX(36px)`，只锁 `body{overflow:hidden}` 收不住，
  改为 `html,body`。

## [0.7.0] — 2026-07-16

### Added — `zima-design`（自有设计合奏引擎，三引擎收编 + 原创路由协议）

**设计合奏引擎**——一次好的设计交付需要三种互补智能：结构与主题的多样性、动效与手感、
数据化的选型依据；没有单一体系同时做好三件事，zima-design 把它们编排成合奏。
落位 `claude-code-zima-design/`，同步 `.claude/skills/`，镜像 `codex-zima-design/`
并接线 `build-packages.ps1` 产出 `zima-design.zip`（354 文件）。

- **原创 SKILL.md 路由协议**：三条铁律（多样性优先 / 诚实 / 验收前置）+ 任务路由表
  （落地页 / 产品 UI / 去 AI 味 / 动效专项 / 方向未定 / 交付评审 → 各自的主导与辅助引擎）+
  **五轴多样性协议**（宏结构 × 主题 × 动效人格 × 卡片物理 × 密度节奏，连续交付不得重复组合，
  选择以 `zima-design signature` 注释盖章进交付物，形成台账）+ 四级交付验收栈。
- **engines/anti-slop/**（源自 [nutlope/hallmark](https://github.com/nutlope/hallmark)，MIT，
  commit `aeb42fb` v1.1.0，逐字节收编 106 文件）：21 种页面宏结构轮换、20 具名主题 +
  custom OKLCH 分支、**57 条 slop-test 验收关卡**、`audit` / `redesign` / `study` 动词、
  组件 cookbook（页脚 N1–N9 / 侧栏 S1–S5 / 引用统计 T1–T4）。
- **engines/motion/**（源自 [emilkowalski/skills](https://github.com/emilkowalski/skills)，MIT，
  commit `6bf2443`，逐字节收编 6 技能 10 文件）：动画决策框架（频率门 → 目的 → 缓动 → 时长，
  键盘触发零动画 / UI 动效 <300ms / 禁 ease-in / 禁 scale(0) 入场）、弹簧物理与手势
  （velocity 甩尾 / 边界阻尼 / 打断续动）、性能铁律（只动 transform/opacity）、
  Apple 设计十七则、动效评审十条标准、动效词汇表。
- **engines/database/**（源自 [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)，
  MIT，commit `f8ac5e1`，逐字节收编 7 技能 229 文件）：**84 风格 / 192 配色 / 74 字体搭配 /
  192 产品类型 / 98 UX 准则 / 25 图表类型 / 22 技术栈**的本地 CSV 数据库 + Python 检索脚本
  （零第三方依赖），10 优先级规则分类（可访问性 CRITICAL → 图表 LOW）。
- **外部联动**（不落库，探测到即征用）：impeccable（工程动词 + register 分流）、
  huashu-design（3 方向并行 demo + 5 维评审）、taste-engine（口味档位）。
- **demos/ 两组示范**：闭环三件套（虚构产品 Curio）——`demo-before-ai-slop.html`（故意堆
  12 处 slop 特征，逐处 `[SLOP-N]` 注释）→ `demo-audit-report.md`（audit 动词示范：24 项
  抽查 17 FAIL，逐关卡证据）→ `demo-after-redesign-hum.html`（redesign 动词示范）；
  **多风格样片画廊**——`demo-style-cobalt-devtool.html`（Cobalt × dev-tool：代码即 hero、
  可用的 ⌘K 命令面板、一条石墨暗带）、`demo-style-lumen-night.html`（Lumen·Night ×
  marquee-hero：手工灯丝仪器 + 引线标注、蓝图网格、正弦包络读数条、小写/大写双声部）、
  `demo-style-carnival-bento.html`（Carnival·Studio-Night × loud bento：青/梅双色对撞、
  硬偏移阴影、半调网点、跑马灯）。四张页面四套「设计签名」，五轴零重叠——多样性协议的
  实物证明；头部均带 signature + pre-emit critique 双盖章，320px 无横滚与
  reduced-motion 降级全数实测通过（无头浏览器验证）。
- `NOTICE.md`（三引擎溯源：仓库 / commit / 原作者 / 许可 / 移植范围 / 升级方式，
  原创与收编边界明示）+ `LICENSES/`（三份上游 MIT 全文）+ `zima-design-README.md`（中文使用说明）。

### Changed — 全线生成类 skills 内联「反 AI slop 硬闸」（zima-design 联动）

`viz-deck` / `viz-charts` / `biz-html-viz`（biz-decision-stack）/ `zima-html-ppt` /
`viz-channel`（OpenClaw + Hermes 两份）的 SKILL.md 统一追加「反 AI slop 硬闸 · zima-design 联动」
章节——蒸馏 anti-slop 引擎六大纪律为交付前硬闸：

1. 交付前六轴自评（P/H/E/S/R/V 各 1–5 分，任一 < 3 返工，分数注释盖章产物头部）；
2. 诚实文案（禁编造 "+47% conversion" 式指标 / testimonial / logo 墙）；
3. 令牌锁定（色值与字体只引 `:root` 令牌，禁内联 hex / OKLCH / 裸字体名）；
4. 禁手绘假 chrome（假浏览器栏 / 假手机壳 / 假代码窗）；
5. 响应式硬底线（320/375/414/768px 无横滚 · `overflow-x: clip` · `minmax(0,1fr)` ·
   可点击文本不折两行）；
6. 标题禁斜体（display 一律 roman，强调走字重 / 强调色 / 下划线）。

外加**结构多样性**要求（连续同类交付物轮换版式骨架）与 zima-design 桥接（装有 zima-design 时
交付前跑 `engines/anti-slop/references/slop-test.md` universal 子集）。`taste-engine` 同步升级：
`anti-slop-preflight.md` 收编六大纪律为硬闸段，SKILL.md 新增「zima-design bridge」章节
（轻量预检 ↔ 全量设计合奏的分工与升级路径）。claude 侧（`~/.claude/skills` 实装 +
`claude-code-skills/*.zip`）与 codex 侧（`codex-skills/`）双侧同步并重打包；
顺手把实装侧落后的 `viz-charts`（缺 SVG-KG 七类）与 `zima-html-ppt`（缺 taste 档位节）
刷新到仓库最新。

### Added — `gzh-design`（移植自 [isjiamu/gzh-design-skill](https://github.com/isjiamu/gzh-design-skill)，AGPL-3.0）

**微信公众号文章排版** skill——Markdown / Word(.docx) / PDF / 纯文本 → 可直接粘贴进公众号
编辑器、粘贴后样式不丢失的 HTML。**逐字节原样移植**上游 skill 本体 20 文件（`SKILL.md` +
`LICENSE` + 11 references + 4 scripts + 3 assets，上游 commit `67c079e`，甲木 × 摸鱼小李联名），
未移植上游 `archive/` 旧版归档与 `docs/` 展示图库。落位 `claude-code-gzh-design/`
并同步进 `.claude/skills/`。

- 6 套内置主题（摸鱼绿 / 红白 / 石墨极简 / 留白禅意 / 摸鱼票据 / 橄榄手记）+ **主题生成器**
  （一句话或参考图 → 新组件库落地本地复用）。
- 智能排版：章节自动编号（末章 ∞）、每段 1–3 处关键词下划线、引言卡 + 目录提炼、签名占位、
  中文全角标点；样式全内联 + `<span leaf="">` 包裹规避公众号过滤。
- **双关卡校验**：`component_lint.py`（组件库源头）+ `validate_gzh_html.py`（最终产物）；
  移植后已本地跑通（ERROR×0）。`wrap_preview.py` 产出带「复制到公众号」按钮的预览页。
- `NOTICE.md` — 来源 / 上游 commit / License / 移植范围 / 升级方式；`gzh-design-README.md` — 中文使用说明。
- 与本仓库分工：**公众号图文排版**用本 skill；网页 / 落地页 / PPT 仍走 huashu-design / viz-deck / biz-html-viz。

### Added — `gzh-channel`（OpenClaw / Hermes 频道层 · 公众号排版对话交付）

把 gzh-design 接进 **飞书 IM 频道**的编排技能，落位 `openclaw-skills/skills/gzh-channel/`
与 `hermes-skills/skills/gzh-channel/`（平行镜像，仅平台称呼不同）：

- **工作流**：收稿（文本/md/docx/PDF）→ 归一化 Markdown 草稿 → **飞书 interactive 卡片
  （结构摘要 + 全文代码块）发回用户确认** → 确认后调 gzh-design 排版（校验 ERROR×0）→
  发回 `_预览.html`（带「复制到公众号」按钮）+ 干净正文 HTML → 用户本地浏览器打开一键复制粘贴。
- `scripts/gzh_card_send.py` — 自包含飞书发送器（与 viz-channel 凭证/令牌/chat 解析同源）：
  `--draft` 发确认卡片（4 反引号围栏防文内代码块冲突；>6000 字符自动改「大纲卡片 + .md 附件」；
  interactive 失败自动回退带代码围栏的文本消息）、`--file` 发产物、`--text` 发文本；
  `gzh_send.sh` / `.ps1` 一行入口。
- `references/gzh-card-protocol.md` — 卡片 JSON 协议 / 长稿策略 / 频道话术 / 排错速查。
- 4 个安装器（openclaw/hermes × sh/ps1）默认一并安装 `gzh-design`（纯文件夹直拷）+
  `gzh-channel`，自检覆盖 `gzh_card_send.py`；两侧 README / USAGE 补登用法与案例
  （OpenClaw 案例 10 / Hermes 案例 12）。

### Added — `web-shader-extractor`（移植自 [lixiaolin94/skills](https://github.com/lixiaolin94/skills)，MIT）

网页 **WebGL / WebGPU / Canvas 着色器动效抠取与本地证据匹配复现** skill，**逐字节原样移植**
上游 22 文件（`SKILL.md` + 13 references + 2 scripts + 6 templates），未改动上游内容。
落位 `claude-code-web-shader-extractor/` 并同步进 `.claude/skills/`。

- `NOTICE.md` — 来源/作者（@lixiaolin94，2D Canvas 路线鸣谢 @HeyHuazi）/License/升级方式。
- `web-shader-extractor-README.md` — 中文使用说明（何时用/触发词/Recon Kernel 状态机/能力清单/边界）。
- 3 个**自包含样例复现 demo**（按 `templates/replay-manifest.json` schemaVersion 3 +
  `extraction-report.md` 组装 HUD 面板，演示抠取产物形态）：
  - `demo-webgl-fragment.html` — WebGL 片元 shader（domain-warped fBM 极光场，零依赖）
  - `demo-canvas2d-flow.html` — Canvas2D 粒子流场（BEHAVIOR_REBUILD 路线，零依赖）
  - `demo-three-reconstruct.html` — Three.js 自定义 ShaderMaterial 重建（顶点位移 + 菲涅尔 + 虹彩）
- 1 个**完整生成用例** `demo-logo-fold-generative.html` + 矢量源 `logo-vector.svg`：
  项目 logo 经 `vtracer` 矢量化 → 网格折翼，每块走「生成→生长→收缩→消失」生命周期 3D 折叠
  （绕铰链刚性翻折 + 解析法线，凸/凹各异），**中心对称自转** + 3 层无限递归。Three.js，矢量源 data URI 内联自包含。
- 与本仓库分工：**抠取/复现**用本 skill；**生成动效/视频**用 huashu-design / viz-deck motion 模式。

## [0.6.0] — 2026-06-18

**Taste 升级 + 现场讲演 deck。** 新增 `taste-engine` 口味层（三档 dial + 反 slop 预检 +
选材/文案规则）；`viz-charts` 扩到七类视觉，补两种可交互纯 SVG 知识图谱（环形 Context
Graph + Circos 弦图）；`zima-html-ppt` 现场讲演 deck（暖纸编辑风 + 演讲者模式）正式纳入，
默认 Taste 档位 `1/1/1`。

### Added — `taste-engine` (shared taste layer) + interactive SVG knowledge graphs

A cross-cutting **taste layer** that elevates any HTML/PPT deliverable's color, layout,
motion, material and copy — applied as tokens and constraints, not a renderer or dependency.

- `taste-engine/SKILL.md` — the layer: three dials (`DESIGN_VARIANCE` / `MOTION_INTENSITY`
  / `VISUAL_DENSITY`) set on `<html>` and read by CSS + JS, per-deliverable default dials
  (report `0/0/1` · deck `1/1/1` · keynote `2/2/1`), workflow, and worked demos.
- `references/taste-dials.md` — dial → token/behavior mapping + copy-paste CSS/JS recipe
  (density spacing/scale/columns, variance rhythm/grid, motion gating with progressive
  enhancement + `prefers-reduced-motion`).
- `references/anti-slop-preflight.md` — the pre-ship kill-list (color ≤ 2 accents, hairline
  craft, tabular numerals, no lorem/emoji-as-icon/fabricated numbers, conclusion-titles,
  no "不是 X 而是 Y" / jargon).
- `references/material-and-copy.md` — sourcing (real assets, `[估]`/`[N/A]` honesty) and
  wording rules.
- `demo/taste-demo.html` — dark-cinematic web report with live dials, scroll motion, charts,
  and **three knowledge-graph forms**: 3D force-directed, **interactive SVG 环形 Context
  Graph** (drag · wheel-zoom · background-pan · click-BFS · search · ring↔force · filters),
  and **Circos 弦图** (ideogram + outer histogram track + inner ribbons, hover-highlight).
- `demo/zima-ppt-demo.html` — warm-paper editorial deck (tri-color bar, hairline cards,
  per-slide timer, **speaker mode**), export-ready as input for MP4 / editable-PPTX pipelines.

### Changed — `viz-charts` gains two interactive SVG KG forms (now 七类视觉表达)

- New `references/svg-kg-guide.md`: the shared `{categories, entities, relationships}` data
  model plus both pure-SVG forms — **环形 Context Graph** (per-category rings, Bézier
  cross-links, full drag/zoom/pan/BFS/search/filter, ring↔force) and **Circos 弦图**
  (segmented ideogram + weight track + chord ribbons, hover-highlight). No WebGL, no chart
  lib; vector-scalable, embeddable in report main flow, printable. SKILL table + step added.
- 3D WebGL KG when nodes are many and spatial; SVG ring/Circos when embedding, interacting,
  exporting or printing.

### Changed — `zima-html-ppt` documents its Taste dial default (`1/1/1`)

- SKILL.md adds a 风格档位 · Taste section: the deck's house dial is `variance=1 · motion=1
  · density=1`, with the three guardrails (≤ 2 accent colors, entrance-only motion with
  reduced-motion downgrade, conclusion-titles + true numbers).

### Added — `zima-html-ppt` skill (ZimaBlueAI 现场讲演 deck)

A new generation skill capturing the **ZimaBlue Editorial (暖纸编辑风)** presentation
style and its signature **Speaker Mode**, distilled from the production decks
`D1-破局与进化` / `D2-三场战役` / `D3-训练方案`.

- `references/design-system.md` — full visual spec: warm-paper tokens, type scale,
  signature elements (top tri-color bar, hairline cards, tabular-nums numerals),
  component recipes, Chart.js tuning, restrained motion, anti-AI-slop rules.
- `references/speaker-mode.md` — the presenter engine: `.notes` speaker-script
  convention with a 5-tag taxonomy (cue / say / do / data / bridge, read-aloud lines
  auto-highlighted orange via `:has()`), per-slide `data-min` time budgeting, the
  keyboard map, and the postMessage-synced presenter window architecture.
- `templates/zima-ppt-starter.html` — one fork-ready single file with the whole
  engine baked in: deck/slide scaffold, top tri-color bar, progress + timer bars,
  on-screen hint badge (`按 F 全屏 · 按 S 演讲者模式 · ← → 翻页`), `✦ ZimaBlueAI`
  brand-mark, count-up numerals, Chart.js defaults, and the S-key presenter window.
- Replicated into all four ecosystems: `claude-code-skills/`, `codex-skills/`,
  `openclaw-skills/skills/`, `hermes-skills/skills/`. Cross-linked from
  `viz-channel/references/default-style.md` so the channel workflow can reach
  speaker mode when a deck needs to be presented live.

### Planned

- viz-charts narrative chart explainer (TTS-narrated chart video)
- Channel adapters beyond Feishu/Lark (WeCom / Slack / Telegram) in `viz-channel`
- Cross-harness consistency test suite
- Skill registry index (`skills.json`)

---

## [0.5.0] — 2026-05-29

### Added — channel delivery layer for OpenClaw & Hermes (`viz-channel`)

The three skills only ever **generated** artifacts. This release adds a
**conversational orchestration + channel-delivery** layer so the same
generation power works *inside an IM channel*: a user @-mentions the bot in
Feishu (or any gateway channel), and the agent **clarifies the request →
generates via viz-deck/viz-charts → sends the finished file back to the same
chat**. Feishu was the user's example; the transport is framed as a
pluggable adapter.

#### New top-level directories — `openclaw-skills/` & `hermes-skills/`

- Each ships the new **`viz-channel`** skill (frontmatter trigger + body =
  `clarify → generate → deliver` workflow), a one-command installer
  (`.sh` + `.ps1`), and a **`USAGE.md` case library** (OpenClaw: 9 cases;
  Hermes: 11, incl. 2 automation cases).
- **Thin-bridge packaging**: the heavy generators (`viz-deck` / `viz-charts`
  / optional `biz-html-viz`) are **not duplicated** — the installer vendors
  them from `claude-code-skills/*.zip` (or `--from-github`) into the target
  platform's skills dir. Single source of truth, no four-way drift.
- Installers **never hard-delete**: a re-install moves any existing skill to
  `.zima-replaced/` rather than removing it.

#### `viz-channel` skill

- **`SKILL.md`** — channel-agnostic trigger (做PPT / 做汇报 / 做图表 /
  知识图谱 / 发给我 / 发群里 …); default deliverable = **animated HTML**,
  with PPTX (editable) / MP4 (in-chat playback) / chart / 3D KG on demand.
- **`references/`**
  - `default-style.md` — **default visual system: ZimaBlue Editorial** (warm
    paper bg, deep-teal primary, gold/terracotta accents, hairline cards,
    teal→gold→red top rule, bold tabular-nums metrics; Chart.js palette +
    PPTX warm-paper theme mapping; modeled on `D1-破局与进化.html`). Applied
    by default to all channel HTML/PPTX; overridable per request.
  - `channel-protocol.md` — conversation state machine, ≤2-question clarify
    rule, multi-turn iteration, group-vs-DM, human-readable failure handling
  - `delivery-matrix.md` — form decision table (HTML / PPTX / MP4 / chart /
    3D KG), HTML-vs-PNG rules, Feishu size/permission limits, pre-send checklist
  - `openclaw-channel.md` / `hermes-channel.md` — platform specifics:
    chat_id resolution, skills load paths, why delivery shells out to a
    script; Hermes adds cron/webhook automation recipes
- **`scripts/`**
  - `channel_deliver.py` — the current channel adapter (**Feishu/Lark**):
    upload + send via open.feishu.cn REST; `--via auto` prefers a lark-cli
    token (reuses an existing `~/.lark-cli` config) and falls back to REST;
    `--to-current` resolves the active chat from injected env vars; ffprobe
    duration probing for nicer MP4 video messages
  - `channel_send.sh` / `.ps1` — one-line delivery entrypoint (wraps
    `channel_deliver.py --via auto`)
  - `resolve_chat.py` — prints/validates the current channel chat_id
- **`templates/zima-editorial-deck.html`** — ready-to-fill HTML skeleton in
  the default ZimaBlue Editorial style (tokens, components, Chart.js defaults
  pre-wired) so default channel HTML looks polished out of the box

#### Platform notes

- **OpenClaw**: native Feishu channel over WebSocket long-connection; skills
  load from `<workspace>/skills/` → `~/.openclaw/skills/`.
- **Hermes**: Feishu gateway adapter binds inbound messages to a session;
  the same generate→deliver chain can run unattended as a **cron or webhook
  routine** (e.g. auto weekly deck to a group, event-triggered chart push).

### Docs

- Top-level `README.md` / `README_en.md`: new "channel delivery layer"
  section, refreshed harness/badge framing, repo-structure block now lists
  the shipped `openclaw-skills/` & `hermes-skills/`, roadmap updated.

---

## [0.4.0] — 2026-05-16

### Added — 26-skill landscape cross-pollination (取长补短)

After a systematic review of the open-source Agent-Skill PPT landscape (26
projects ≈ 70k+ aggregate stars), this release imports the highest-value
patterns from peer skills into the three ZimaBlueAI skills. **All v0.3
workflows remain unchanged**; every upgrade is additive.

#### `claude-code-skills/viz-deck` — six v4 enhancements

- **Speaker Mode** (inspired by `lewislulu/html-ppt-skill` — 3.8k★)
  - New `templates/speaker-window.html`: independent draggable presenter
    window with 4 magnetic cards (current preview / next preview /
    teleprompter / timer)
  - `templates/slide-deck.html` rewired: press **S** to pop the window;
    BroadcastChannel `viz-deck-presenter` keeps both windows in sync;
    `?present=true` URL flag auto-opens
  - Timer has elapsed / countdown modes, >90% warn, >100% over-time alert
  - Three layout presets: GRID / PROMPTER / DUO
- **Show-Don't-Tell 3-variant preview** (inspired by `zarazhangrui/frontend-slides` — 17.5k★)
  - New `scripts/preview-shotgun.mjs`: takes a topic + scene preset and
    renders 3 contrasting hero mockups side-by-side
  - 5 scene presets (`investor-pitch`, `product-launch`, `tech-deepdive`,
    `academic`, `default`); each picks a cross-school triple from the
    20-philosophy library
  - New `templates/preview-board.example.html`: sample output
  - `references/design-philosophies.md` extended with the contrast-triple
    table and trigger rules
- **Doc → Deck converter** (inspired by `leonid20000/odin-slides` — 147★ + `natolambert/colloquium` — 190★)
  - New `scripts/doc-to-spec.mjs`: parses Markdown (and DOCX/PDF via pandoc
    pre-flight) and emits a valid `pptx-deck-spec.json` ready for
    `make-pptx-deck.mjs`
  - Heading-level histogram picks the chapter boundary intelligently
  - Tables → kpi-grid; bullet runs → title-bullets; quote blocks → pullquote
  - New `references/doc-to-deck.md` documenting input formats, conversion
    rules, and the difference from odin-slides / colloquium
- **Academic Talk template** (inspired by `Gabberflast/academic-pptx-skill` — 387★)
  - New `templates/academic-talk.html`: long-scroll keynote with action
    titles (verb-driven), numbered citations, exhibit headers, anticipated
    Q&A section, and a proper references bibliography
  - Newsreader serif typography for academic gravitas
  - New `references/academic-mode.md`: action-title rule, citation
    discipline, exhibit caption guidelines, limitations checklist
- **Bento Grid layout** (inspired by `hubeiqiao/apple-bento-grid` — 171★)
  - New `templates/bento-layout.html`: 12-col responsive bento with
    1×1 / 2×1 / 3×1 / 4×1 / 1×2 / 2×2 spans + hero accent halos
  - `make-pptx-deck.mjs` adds `bento-grid` as the 9th native PPTX layout
    (greedy row-packing, 3-col layout, accent variants `accent` / `accent2` /
    `gold`)
  - `templates/pptx-deck-spec.example.json` extended with a sample bento slide
- **Reflective Loop** (inspired by `icip-cas/PPTAgent` — 4.4k★)
  - New `scripts/reflect-and-redo.mjs`: per-page 5-dim critique pass; D2/D3/D4
    scored objectively from the JSON spec; D1/D5 flagged as neutral
    pending human/LLM review
  - HTML report includes deck mean, dimension means, per-slide score table
    (flagged rows red), and explicit issue list
  - Optional `--redo-prompts redo.txt` emits human-readable redo proposals
    per flagged slide
  - `references/critique-5dim.md` extended with the reflective-loop protocol
    and threshold rules

#### `claude-code-skills/biz-decision-stack` — Template Router subagent

- **Template Router** (inspired by `seulee26/mckinsey-pptx` — 426★)
  - New `.claude/agents/08-template-router.md`: 9th subagent in the
    biz-decision-stack
  - Routes ambiguous user input ("做个 deck 给老板"、"做个汇报") to one of 8
    templates by scoring against a 5-dimension rubric (audience fit ×3 /
    decision type ×3 / temporal fit ×2 / density ×1 / trigger keywords ×1)
  - Outputs a ROUTING DECISION block + writes a one-paragraph justification
    into the generated HTML's header comment block — every choice is
    defended, not silent
  - Routes to user pick when top-1 and top-2 scores are within 3 points
- **New reference**: `references/template-routing-rubric.md` — full scoring
  rubric, threshold table, dual-candidate handling

#### Repository-wide

- `.work/repack-v3.py` updated to include the new 9th subagent
  (`08-template-router.md`) in `biz-decision-stack.zip`
- `.work/build-codex.py` updated symmetrically — the 9 subagents are now
  converted to TOML and packaged into `codex-skills/biz-decision-stack.zip`
- All three skills' `SKILL.md` `description` fields extended with the new
  v4 trigger keywords (Speaker Mode, Doc→Deck, academic talk, bento, etc.)
  so the harness's keyword router can find them

### Compatibility

- v0.3 workflows are **fully preserved**. Every v4 addition is additive:
  - viz-deck: still 5 modes, all original templates/scripts intact
  - biz-html-viz: still 8 templates (the new template-router *picks* among
    them, doesn't replace any)
  - viz-charts: not touched in v0.4 (no PPT-landscape peer outperforms it)
- Speaker Mode requires same-origin context (both `slide-deck.html` and
  `speaker-window.html` served from the same path)
- Doc-to-spec for `.docx` / `.pdf` requires pandoc on PATH

### Known constraints

- Reflective Loop's D1 (philosophy alignment) and D5 (originality) cannot
  be scored from JSON alone — the script flags them as neutral 7.0 and
  delegates the actual judgement to an LLM review of the rendered output
- Speaker Mode pop-up requires browser pop-up permissions for the deck
  origin; the hint banner explains this when blocked
- The `preview-shotgun.mjs` philosophy registry is a representative subset
  (11 of the 20 huashu philosophies); the remaining 9 can still be invoked
  by explicit slug

---

## [0.3.0] — 2026-05-13

### Added — ppt-master soft bridge (true native DrawingML PPTX)

This release adds a **second soft bridge** to
[`hugohe3/ppt-master`](https://github.com/hugohe3/ppt-master) — a
python-pptx + SVG-to-DrawingML pipeline that produces editable `.pptx`
files where **every visual element is an independently clickable native
shape**, not a flattened image. All three skills now expose a PPTX export
path on top of their existing HTML / motion deliverables.

#### `claude-code-skills/viz-deck` — new **mode 5 · pptx-deck**

Was 4 modes (keynote-report / prototype / slide-deck / motion-stage), now 5.

- `scripts/make-pptx-deck.mjs` — JSON deck spec → per-slide SVG (deep-space /
  terminal / deck-light themes) → ppt-master assembles `.pptx`
- `scripts/export-editable-pptx.sh` — entry point wrapper
- `scripts/embed-narration.sh` — TTS (edge-tts / ElevenLabs / MiniMax / Qwen /
  CosyVoice) writes per-slide MP3, then rebuilds `.pptx` with embedded audio
  and slide timings synced to narration length. PowerPoint File→Export→Video
  produces a `.mp4` with narration + animations.
- `templates/pptx-deck-spec.example.json` — 9-slide canonical spec with 8
  layouts (`title-cover`, `agenda`, `section-divider`, `title-bullets`,
  `two-column`, `kpi-grid`, `pullquote`, `closing`)
- `references/pptx-master-bridge.md`, `editable-pptx.md`, `master-templates.md`,
  `narration-pptx.md` — bridge protocol, what's-editable matrix, corporate
  template import via `register_template.py`, TTS provider catalog
- **3 sample PPTX** shipped (each paired with reusable `.spec.json`):
  - `editable-deck-sample.pptx` — Q3 board update, deep-space theme (9 slides, native DrawingML)
  - `product-launch-deck-sample.pptx` — Mingjing public launch, deck-light theme (10 slides)
  - `all-layouts-showcase-sample.pptx` — one slide per layout, layout reference deck (8 slides)
- `samples/SAMPLES.md` — catalog with verification commands and reuse instructions

#### `claude-code-skills/biz-decision-stack` — terminal-themed editable PPTX

- `scripts/make-decision-pptx.mjs` + `scripts/export-decision-pptx.sh` —
  JSON spec → per-slide SVG (locked terminal theme: black + acid-yellow +
  JetBrains Mono) → ppt-master `.pptx`. 8 decision-specific layouts:
  `verdict-cover`, `kpi-roster`, `decision-matrix`, `roadmap-phases`,
  `risks-grid`, `retro-3col`, `action-list`, `summary-stack`
- `specs/board-brief.example.json`, `specs/retro-report.example.json` —
  canonical spec starters mirroring the existing HTML templates
- `references/pptx-master-bridge.md` — narrow bridge protocol (zero motion,
  no narration, no animations — preserves the "decision IS the document"
  philosophy)
- **4 sample PPTX** shipped (each paired with reusable `.spec.json`):
  - `decision-board-brief-sample.pptx` — Q3 board brief, GO verdict (5 slides)
  - `decision-retro-report-sample.pptx` — Q2 retrospective with worked/didn't/change (4 slides)
  - `decision-tech-roadmap-sample.pptx` — 4-quarter tech roadmap with phases, risks, actions (5 slides)
  - `decision-sprint-dev-sample.pptx` — Weekly sprint dev report with KPIs + retro + actions (4 slides)
- `samples/SAMPLES.md` — catalog with verification commands and reuse instructions

#### `claude-code-skills/viz-charts` — native PPTX charts

- `scripts/echarts_to_pptx.py` + `scripts/export-chart-pptx.sh` — chart spec
  (or raw ECharts option) → `.pptx` with a real `<c:chart>` object. Opening in
  PowerPoint exposes "Edit Data" which launches a spreadsheet panel. Supports
  8 chart types (`column`, `bar`, `line`, `area`, `pie`, `doughnut`, `scatter`,
  `radar`) with stacked variants for the first 4
- `specs/revenue-by-quarter.example.json`, `specs/market-share-pie.example.json`,
  `specs/trend-line.example.json` — canonical chart spec starters
- `references/pptx-charts.md` — bridge protocol + when-to-use vs SVG inline,
  ECharts→python-pptx type mapping, composability with viz-deck mode 5
- Three themes (`deep-space`, `terminal`, `deck-light`) with matched series
  palettes
- **4 sample PPTX** shipped (each paired with reusable `.spec.json`):
  - `native-chart-sample.pptx` — quarterly revenue, column chart, deep-space (3 series × 4 quarters)
  - `chart-trend-line-sample.pptx` — 12-month workspaces trend, line chart, deep-space (actual vs plan)
  - `chart-market-share-doughnut-sample.pptx` — vendor market share, doughnut, deck-light (6 categories)
  - `chart-critique-radar-sample.pptx` — v3 release self-critique, radar, terminal (5 axes × 3 series)
- `samples/SAMPLES.md` — catalog with composability tip (mixing chart PPTX into deck PPTX via PowerPoint's "Reuse Slides")

#### `codex-skills/` — dual-harness launch (NEW top-level directory)

- All three skills (biz-decision-stack, viz-deck, viz-charts) now ship a
  second flavor tailored to **OpenAI Codex CLI**'s `.codex/skills/` and
  `.codex/agents/` conventions. **Skill content (SKILL.md, references,
  templates, scripts, specs) is byte-for-byte identical** to the Claude
  Code version; only the install path and subagent serialization differ.
- 8 subagents converted from Claude Code's markdown frontmatter → Codex's
  TOML format (`name`, `description`, `developer_instructions`)
- `codex-skills/install.sh` + `codex-skills/install.ps1` — one-shot
  installer that extracts the three zips to `$HOME/.codex/skills/` and
  TOML agents to `$HOME/.codex/agents/`
- `codex-skills/README.md` — explains the harness mapping
- `codex-skills/INSTALL.md` — Codex-flavored install / config / use guide
  (mirror of `claude-code-skills/skills-install-guide.md`)
- `codex-skills/agents-toml/` — pre-converted TOML subagents (reference copies)
- `.work/build-codex.py` — reproducible Codex-flavor builder

#### Bridge script portability (Claude Code + Codex shared scripts)

The four ppt-master bridge scripts now detect their backing install via a
three-tier search — same script runs on either harness:

```
$PPT_MASTER_HOME → ~/.codex/skills/ppt-master → ~/.claude/skills/ppt-master
```

Patched files: `make-pptx-deck.mjs`, `make-decision-pptx.mjs`,
`export-editable-pptx.sh`, `export-decision-pptx.sh`, `export-chart-pptx.sh`,
`embed-narration.sh`. No fork: a single bridge install serves both harnesses.

#### Repository-wide

- `README.md`, `README_en.md`, `skills-install-guide.md` (Claude) +
  `codex-skills/INSTALL.md` updated with §13 ppt-master bridge protocol
- All three skills' SKILL.md updated to expose the new mode/capability
- `.work/repack-v3.py` — reproducible Claude-flavor zip repacker (Python,
  no `zip` CLI dependency)
- `.work/build-codex.py` — reproducible Codex-flavor builder

### Compatibility

- v0.2 workflows are **fully preserved**. Mode 5 in viz-deck is purely
  additive; modes 1-4 untouched. biz-decision-stack HTML templates and
  viz-charts HTML/SVG rendering are unchanged.
- `ppt-master` is a **soft dependency** alongside `huashu-design`. Installing
  it unlocks the new editable-PPTX paths; without it, v0.2 workflows continue
  to work exactly as before.

### Known constraints

- ppt-master native bridge requires: Python 3.10+ with a venv at
  `~/.claude/skills/ppt-master/.venv/`, packages `python-pptx`, `edge-tts`,
  `svglib`, `reportlab`, `Pillow`, `numpy`
- Custom fonts: PowerPoint substitutes if the viewer's machine lacks the font.
  Stick to system fonts (Inter, JetBrains Mono) or use PowerPoint's font
  embedding before distribution
- SVG filters (drop-shadow, blur) approximate only — use PowerPoint's native
  shape effects after import for high fidelity
- ppt-master is MIT-licensed; this is a runtime soft bridge, not a fork —
  attribution lives in NOTICE and README

---

## [0.2.0] — 2026-05-11

### Added — v2 capability expansion + huashu-design soft bridge

This release reshapes `viz-deck` from a single-mode keynote skill into a
**four-mode delivery toolkit**, integrates a published 20-philosophy library
and a 5-dimension critique standard, and exposes a screen-recording / PPTX
export toolchain via a soft bridge to
[`alchaincyf/huashu-design`](https://github.com/alchaincyf/huashu-design).
All v0.1 capabilities remain backwards-compatible.

#### `claude-code-skills/viz-deck` — main upgrade target (35 KB → 65 KB)

- **4 production modes** (was 1):
  1. `keynote-report` — original v1 mode (stage / architecture-deep / competitive-landscape)
  2. `prototype` — hi-fi HTML prototypes with iOS / Android / macOS / browser device frames + AppPhone state manager
  3. `slide-deck` — keyboard-navigated HTML slides with speaker notes, overview, autoplay; exportable to **editable PPTX** (real text frames, not flattened images) and landscape PDF
  4. `motion-stage` — HTML animation stages with `window.__ready` recording signal; exports MP4 at 25 fps base + 60 fps interpolated + palette-optimized GIF + optional BGM (six scene-typed tracks via huashu)
- New starter templates: `prototype-shell.html`, `slide-deck.html`, `motion-stage.html`
- New scripts: `export-mp4.sh`, `export-pptx.sh`, `review-5dim.mjs`
- New references: `huashu-bridge.md`, `design-philosophies.md`, `critique-5dim.md`, `prototype-mode.md`, `slide-mode.md`, `motion-mode.md`
- `SKILL.md` rewritten to expose mode routing, philosophy picker, and critique trigger
- `samples/motion-stage-sample.html` + `.mp4` + `design-critique-sample.html` shipped as reference outputs

#### `claude-code-skills/biz-decision-stack` (57 KB → 62 KB)

- **7th subagent**: `07-design-critic.md` for 5-dimension critique of any decision report
- **8th template**: `design-critique.html` — terminal-style critique HTML with embedded ECharts radar + Keep / Fix (critical / important / polish) / Quick-Wins
- New references: `critique-5dim.md` (terminal-styled critique protocol), `huashu-bridge.md` (limited bridge — critique standard only; motion / BGM / device frames deliberately excluded to honor the zero-motion principle)
- Orchestrator `00-all-hands-orchestrator.md` adds an optional Phase 6 — offers to run a critique pass after the 6-role chain
- `samples/design-critique-sample.html` shipped as reference output

#### `claude-code-skills/viz-charts` (150 KB → 153 KB)

- **5th capability layer**: motion charts — frame-step reveal, temporal sweep, graph orbit
- New references: `motion-charts.md`, `mp4-export.md`
- New theme presets: `themes/motion.js` — animation duration / easing / fps consistency across stages
- New template: `templates/motion/motion-stage-template.html`
- `SKILL.md` updated to 5 capability layers + Step 5 (Motion → MP4) workflow
- `samples/trend-motion-sample.html` + `.mp4` shipped as reference outputs

#### Repository-wide

- `README.md` rewritten to delivery-grade open-source documentation, replacing v0.1 conversational tone
- `README_en.md` added — English-language landing page
- `claude-code-skills/skills-install-guide.md` upgraded to v2.0 with two new sections: §11 v2 capability cheatsheet and §12 huashu-design bridge protocol
- Every skill now ships a `samples/` directory with real rendered deliverables

### Compatibility

- v0.1 workflows are **fully preserved**. Users not adopting v2 modes need no changes.
- `huashu-design` is a **soft dependency** — installing it unlocks v2 advanced modes; without it, the v1 keynote-report / decision chain / static charts continue to work unchanged.

### Known constraints

- v2 motion / PPTX export modes require: Node 18+, Chromium (via Playwright), and ffmpeg on PATH
- huashu-design itself is free for personal use; **commercial deployments must obtain a separate license** from its author

---

## [0.1.0] — 2026-05-10

### Added — Initial public release

First open-source release under Apache License 2.0. Three skills shipped for
the **Claude Code** harness.

#### `claude-code-skills/biz-decision-stack` (57 KB)

- 6 subagents covering board → CEO → architect → MRD/PM → dev-test → retro
- 1 shared HTML rendering skill (`biz-html-viz`) with 7 terminal-style templates:
  `board-brief`, `ceo-canvas`, `tech-roadmap`, `mrd-report`, `project-board`,
  `dev-report`, `retro-report`, plus an `index` aggregator
- `00-all-hands-orchestrator` for one-shot full-chain generation
- Design system: black `#0a0a0a` + acid-yellow `#d4ff00`, JetBrains Mono,
  zero animation, print-ready

#### `claude-code-skills/viz-deck` (35 KB)

- 3 keynote-grade HTML templates: `stage-report`, `architecture-deep`,
  `competitive-landscape`
- Design system: deep-space `#030711` + cyan/blue/gold, Inter, scoped
  micro-animations with `prefers-reduced-motion` fallback
- Tier 1/2/3 adaptive competitive research playbook (web_search + web_fetch)

#### `claude-code-skills/viz-charts` (150 KB)

- Mermaid (11 diagram types), ECharts (25+ chart types), self-rolled SVG
  components (KPI, sparkline, gauge, progress bar, tag cloud)
- 3D knowledge graph viewer (3d-force-graph + three.js) with two builders:
  - `code-kg.mjs` — extracts file/import graph from JS/TS/Go/Python/Rust repos
  - `doc-kg.mjs` — extracts concept/section graph from markdown
- Dual render modes: inline live (CDN with jsdelivr→unpkg fallback) and offline SVG
- Dual themes: `terminal` (for biz-decision-stack) and `deck` (for viz-deck)

### Documentation

- Repository-wide `README.md` with bilingual project intro and roadmap
- `LICENSE` (Apache 2.0) and `NOTICE` (ZimaBlueAI copyright + trademark + third-party)
- `CONTRIBUTING.md` with PR conventions, DCO sign-off requirement, skill quality bar
- `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1)
- `claude-code-skills/skills-install-guide.md` — end-to-end install/config/usage

---

[Unreleased]: https://github.com/ZimaBlueAI/skills/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/ZimaBlueAI/skills/compare/v0.6.0...v0.7.0
[0.4.0]: https://github.com/ZimaBlueAI/skills/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ZimaBlueAI/skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ZimaBlueAI/skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ZimaBlueAI/skills/releases/tag/v0.1.0
