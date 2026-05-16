# doc-to-deck: 长文 → 幻灯片转换协议

> v2.1 新增。灵感来自 odin-slides（长 Word 转结构化 PPT）和 colloquium（Markdown native 幻灯片）。把已写好的长报告/论文/方案文档自动拆解成 viz-deck 模式 5 的 pptx-deck-spec JSON，再走 ppt-master 桥接出 native PPTX。

## 何时使用

| 用户场景 | 触发 |
|---|:---:|
| 写完一份 30 页报告，要给 board 讲 30 分钟 | ✅ |
| 已有 Markdown 笔记，想直接讲课 | ✅ |
| 客户给了一份 .docx，要做对应 PPT | ✅（需 pandoc 预处理） |
| 翻译 / 复刻别人的 PPT | ❌ 不是本路径，走 gpt-image2-ppt-skills 思路 |
| 从零无文档生成 | ❌ 不是本路径，走 SKILL.md 主流程 |

## 输入格式

### 原生支持：Markdown

```bash
node ~/.claude/skills/viz-deck/scripts/doc-to-spec.mjs \
  --input report.md \
  --output deck.json \
  --theme deep-space \
  --max-slides 25 \
  --target-min 30
```

### .docx / .pdf：先 pandoc 预处理

```bash
# DOCX → MD
pandoc report.docx -o report.md --wrap=none

# PDF → MD（需要 pdftotext，brew/apt install poppler）
pandoc report.pdf -o report.md --wrap=none

# 然后跑 doc-to-spec
node ~/.claude/skills/viz-deck/scripts/doc-to-spec.mjs --input report.md --output deck.json
```

### 长文风格建议

为了最大化转换质量，源 Markdown 推荐结构：

```markdown
# 文档标题（doc title — 自动用作 cover）

可选导语段落（自动用作 cover subtitle）

## 章节 1 标题

段落（自动用作章节 lead）

- bullet
- bullet
- bullet

### 子标题（自动用作 bullet slide eyebrow）

> 引用（自动转 pullquote slide）

| 指标 | 数值 | 说明 |
|---|---|---|
| ARR | $12M | +47% |

## 章节 2 标题
...
```

## 解析规则

| Markdown 元素 | 转换为 |
|---|---|
| 第一级章节标题（H1 或 H2，取多者） | `section-divider` 页 |
| 子标题（H3） | 内页 eyebrow + title |
| 段落 | 内页 `lead` 字段 |
| 无序/有序列表（≤6 项） | `title-bullets` 页 |
| 无序/有序列表（>6 项） | 自动拆分多页 |
| 引用块 `>` | `pullquote` 页 |
| 表格（2-3 列, ≤6 行） | `kpi-grid` 页 |
| 表格（更大） | `two-column` 对比页 |

## 章节预算

```
预算 = max-slides - 3（cover + agenda + closing）
每章 = 预算 / 章节数
```

例如 `--max-slides 25 --target-min 30` + 5 章 → 每章 ~4 页内容 + cover/agenda/closing = 共 ~23 页。

## 后续工作流

```bash
# 1. Doc → spec
node ~/.claude/skills/viz-deck/scripts/doc-to-spec.mjs \
  --input report.md --output deck.json

# 2. 人工 review deck.json — 改 cover author/date、补 KPI 单位、调 pullquote 归属
$EDITOR deck.json

# 3. Spec → native PPTX
~/.claude/skills/viz-deck/scripts/export-editable-pptx.sh deck.json \
  --theme deep-space --anim fade --trans push

# 4. （可选）加旁白
~/.claude/skills/viz-deck/scripts/embed-narration.sh ./deck_pptx_build \
  --voice zh-CN-XiaoxiaoNeural
```

## 反模式

- ❌ 输入是产品文档（README / API 文档）→ 这是技术参考，不是讲稿，先重写大纲
- ❌ 没有任何标题的纯散文 → 没法识别章节，先用 LLM 加 ## 标题
- ❌ 表格全是文字（非数据）→ 会被错误识别为 kpi-grid，改成 bullet list 更准
- ❌ `--max-slides 50` → 超过 25 页观众会累，先压缩文档不要让脚本压缩
- ❌ 转换完直接生成 PPTX 而不 review JSON → 一定要人工抽查 cover/closing 页

## 与 colloquium 的差异

| 维度 | colloquium | viz-deck doc-to-spec |
|---|---|---|
| 输入 | Markdown | Markdown / DOCX / PDF（pandoc） |
| 输出 | Marp/Reveal HTML | pptx-deck-spec JSON → native PPTX |
| 受众 | 学者笔记直转课件 | 报告 → 客户/Board 演讲 |
| 视觉控制 | CSS 主题 | viz-deck 8 layout × 3 theme |
| 后续 | 直接讲 | 还能加旁白、转 MP4、5 维评审 |

## 与 odin-slides 的差异

| 维度 | odin-slides | viz-deck doc-to-spec |
|---|---|---|
| 输入 | DOCX（重 Word 用户） | Markdown 优先（.docx 经 pandoc） |
| 输出 | python-pptx 直出 | spec JSON（可中间编辑）→ native PPTX |
| 重写规则 | LLM 自动重写章节 | 保守解析 + 人工 review |
| 风格 | 内置咨询模板 | 接 viz-deck 20 哲学 |
