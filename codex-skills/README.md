# codex-skills · ZimaBlueAI 三件套（OpenAI Codex CLI 版）

> 这是 `claude-code-skills/` 的 **Codex CLI 对等版本**。三个 skill 的内容（SKILL.md、references、templates、scripts、specs）和 Claude Code 版**完全相同**——只是装到 Codex 期望的位置，且 8 个 subagent 改用 TOML 格式。
>
> 想了解项目全貌、设计哲学、桥接关系，请读仓库根 `README.md` / `README_en.md`。这里只讲 Codex 安装与差异。

---

## TL;DR

```bash
# Linux / macOS
git clone --depth=1 https://github.com/ZimaBlueAI/skills.git
cd skills/codex-skills
bash install.sh

# Windows (PowerShell)
git clone --depth=1 https://github.com/ZimaBlueAI/skills.git
cd skills\codex-skills
.\install.ps1
```

装完在 Codex CLI 里 `/skills`，应能看到：

- `biz-html-viz` — 决策链 8 模板 + 决策 PPTX
- `viz-deck` — 五模产出（keynote / prototype / slide / motion / pptx-deck）
- `viz-charts` — 6 类视觉表达 + 原生 PPTX 图表

8 个 subagent 通过 `$<name>` 或自然语言触发：`$all-hands-orchestrator`、`$board-advisor`、`$ceo-decision`、`$chief-architect`、`$product-manager`、`$dev-test-lead`、`$acceptance-retro`、`$design-critic`。

---

## Codex CLI 与 Claude Code 的映射

整套设计在两个 harness 上**共享同一份 SKILL.md 和同一份 scripts**——这是有意的。每一项差异都列在下面：

| 维度 | Claude Code | OpenAI Codex CLI | 差异类型 |
|---|---|---|---|
| 用户 skill 目录 | `~/.claude/skills/<name>/` | `~/.agents/skills/<name>/` | **路径不同**（内容完全相同） |
| SKILL.md frontmatter | `name:` + `description:` + 可选 `license:` | `name:` + `description:` | **完全兼容**（Codex 会忽略未知字段） |
| 项目级 skill 目录 | `.claude/skills/<name>/` | `.agents/skills/<name>/` | **路径不同** |
| Subagent 文件 | `~/.claude/agents/<name>.md`（YAML frontmatter） | `~/.codex/agents/<name>.toml`（TOML） | **格式不同 → 已预转好** |
| Subagent 字段 | `name` / `description` / `tools` | `name` / `description` / `developer_instructions` / 可选 `model`/`sandbox_mode` | TOML 化时自动适配 |
| 触发 | 自然语言 + 隐式 SKILL.md 加载 | 自然语言 + 隐式加载 + 显式 `$skill-name` + `/skills` | 行为等价 |
| 桥接（ppt-master / huashu-design） | 安装到 `~/.claude/skills/<bridge>` | 安装到 `~/.agents/skills/<bridge>` | 脚本**双路径自动探测**（无需配置） |

凡 SKILL.md 中含 `~/.claude/skills/` 的字面描述（少数地方），Codex 也能识别——脚本本身（make-pptx-deck.mjs / make-decision-pptx.mjs / 几个 .sh）已加入 `$PPT_MASTER_HOME` → `~/.agents/skills/ppt-master` → `~/.claude/skills/ppt-master` 的探测链，所以同一份脚本两个 harness 都能用。

---

## 三个 zip 的内容

每个 zip 都按 Codex 的 install 布局组织：

```
biz-decision-stack.zip
├── .agents/skills/biz-html-viz/      # SKILL.md + references + templates + scripts + specs
└── .codex/agents/00-..07-*.toml      # 8 TOML subagents（v0.3 终端风评审为第 7 个）

viz-deck.zip
└── .agents/skills/viz-deck/          # 5 模 + 11 references + 7 templates + 6 scripts

viz-charts.zip
└── .agents/skills/viz-charts/        # 6 类视觉 + 3D KG builders + native PPTX chart script
```

解压到 `$HOME/` 即落到位。`install.sh` / `install.ps1` 就是封装了这步。

---

## 安装细节

### 手动安装（不想用 install 脚本）

```bash
unzip -o biz-decision-stack/biz-decision-stack.zip -d ~/
unzip -o viz-deck/viz-deck.zip -d ~/
unzip -o viz-charts/viz-charts.zip -d ~/
```

### 项目级安装（只在某项目里启用）

把 zip 解到项目根（与 `.git` 同级）：

```bash
unzip -o codex-skills/biz-decision-stack/biz-decision-stack.zip -d /path/to/your-project/
unzip -o codex-skills/viz-deck/viz-deck.zip -d /path/to/your-project/
unzip -o codex-skills/viz-charts/viz-charts.zip -d /path/to/your-project/
```

Codex 会同时识别项目级 `.agents/skills/` 和用户级 `~/.agents/skills/`。

### 验证

```
> /skills
```

应能看到 `biz-html-viz`、`viz-deck`、`viz-charts`。

```
> /agents
```

应能看到 8 个 subagent。

---

## 可选 · 装桥接解锁 v2 / v3 高级能力

两个软桥接都不装也行——v1 能力（HTML 报告 / 静态图表 / 决策链）完全可用。

### v3 · ppt-master（推荐先装这个）

解锁：viz-deck 模式 5 真编辑 PPTX、biz-decision 决策 PPTX、viz-charts 数据绑定 chart、TTS 旁白。

```bash
git clone --depth=1 https://github.com/hugohe3/ppt-master.git ~/.agents/skills/ppt-master
cd ~/.agents/skills/ppt-master
python -m venv .venv

# Linux/macOS
.venv/bin/pip install python-pptx edge-tts svglib reportlab Pillow numpy
# Windows
# .venv/Scripts/pip install python-pptx edge-tts svglib reportlab Pillow numpy
```

### v2 · huashu-design

解锁：HTML→MP4/60fps/GIF/PPTX 导出、20 设计哲学、5 维评审。

```bash
git clone --depth=1 https://github.com/alchaincyf/huashu-design.git ~/.agents/skills/huashu-design
cd ~/.agents/skills/huashu-design

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

---

## 完整使用手册

详细的 skill 触发关键词、命令行、依赖矩阵、桥接调用约定，请读：

- [`INSTALL.md`](./INSTALL.md) — Codex 版完整安装与配置手册（mirror of `claude-code-skills/skills-install-guide.md`）
- 仓库根 [`README.md`](../README.md) / [`README_en.md`](../README_en.md) — 整体说明

---

## 三个 zip 的关系图

```
┌──────────────────────────┐     ┌────────────────────────────┐
│ huashu-design (v0.2)     │     │ ppt-master (v0.3)          │
│ - MP4 / 60fps / GIF      │     │ - python-pptx              │
│ - HTML→PPTX (text only)  │     │ - SVG→DrawingML (clickable)│
│ - 20 design philosophies │     │ - master/template inherit  │
│ - 5-dim critique std     │     │ - TTS narration embed      │
│ - iOS/Android frames     │     │ - native data-bound charts │
└────────────┬─────────────┘     └──────────────┬─────────────┘
             │                                  │
   ┌─────────┼──────────────┐    ┌──────────────┼─────────────┐
   ▼         ▼              ▼    ▼              ▼             ▼
┌─────────┐ ┌──────────────┐ ┌──────────────────┐
│viz-     │ │   viz-deck   │ │ biz-decision-    │
│ charts  │ │ (modes 2-4 + │ │     stack        │
│ (motion │ │   mode 5)    │ │ (critique + pptx)│
│  + pptx)│ │              │ │                  │
└─────────┘ └──────────────┘ └──────────────────┘
```

`huashu-design` / `ppt-master` 都是软依赖；两个都在 `~/.agents/skills/` 下安装即可，三个 skill 会自动桥接。

---

## 反向兼容：同时装 Claude Code + Codex

完全支持。在同一台机上：

- Claude Code 跑 `~/.claude/skills/` 下的同名 skill 们
- Codex 跑 `~/.agents/skills/` 下的同名 skill 们
- 两个 harness 共享同一份 `ppt-master` 和 `huashu-design`（只装一份，脚本会自动检测）

唯一要注意的：**别同时把两份 zip 都解压到同一个项目根**——只会冲突，没有好处。一个项目选一个 harness。

---

## 许可证

Apache License 2.0 · Copyright © 2026 ZimaBlueAI · 详见仓库根 [`LICENSE`](../LICENSE)。

软桥接保留各自上游许可证：
- [`hugohe3/ppt-master`](https://github.com/hugohe3/ppt-master) — MIT
- [`alchaincyf/huashu-design`](https://github.com/alchaincyf/huashu-design) — 个人免费 / 商用独立授权

---

<sub>Made by ZimaBlueAI · 2026 </sub>
