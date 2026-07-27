# 3D Knowledge Graph · Builder Guide

构建可交互 3D 知识图谱的完整流程。

## 三种入口

| viewer 模板 | 数据来源 | builder | 典型用途 |
|---|---|---|---|
| `templates/kg3d/code-graph.html` | git 代码仓库 | `builders/code-kg.mjs` | 项目代码结构总览、模块依赖审计 |
| `templates/kg3d/doc-graph.html` | markdown 文档目录 | `builders/doc-kg.mjs` | 项目知识图谱、概念地图 |
| `templates/kg3d/data-graph.html` | 任意 JSON | （手填或自定义） | 业务实体关系、组织结构 |

## 统一数据契约

三个 viewer 消费**完全相同**的 JSON 结构：

```json
{
  "nodes": [
    {
      "id":    "唯一标识（字符串）",
      "name":  "显示名（鼠标悬浮显示）",
      "group": "分组名（决定颜色）",
      "size":  4,
      "desc":  "可选 · 详情面板显示"
    }
  ],
  "links": [
    {
      "source": "源节点 id",
      "target": "目标节点 id",
      "type":   "可选 · 关系类型（详情显示）",
      "value":  1
    }
  ],
  "meta": {
    "title":    "图谱标题",
    "subtitle": "副标题",
    "stats": { "nodes": 0, "edges": 0, "groups": 0 }
  }
}
```

### 字段约束

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `nodes[].id` | string | ✓ | 全局唯一，建议含命名空间前缀（`file:`、`concept:`） |
| `nodes[].name` | string | ✓ | 用户看到的名字 |
| `nodes[].group` | string | 推荐 | 决定颜色，控制 ≤ 8 类（超过会循环复用配色） |
| `nodes[].size` | number | 推荐 | 2-24 范围，建议用 log 缩放避免极差悬殊 |
| `nodes[].desc` | string | - | markdown 不渲染，纯文本 |
| `links[].source/target` | string | ✓ | 必须匹配某个 node.id |
| `links[].type` | string | - | 边类型标签（"imports", "mentions"…） |
| `links[].value` | number | - | 边权重，影响渲染粗细 |

## Builder 1: 代码 KG

### 用法

```bash
node .claude/skills/viz-charts/builders/code-kg.mjs \
  --repo ./my-project \
  --output ./code-kg.json \
  --group-by dir
```

### 选项

| 选项 | 默认 | 说明 |
|---|---|---|
| `--repo` / `-r` | `.` | 仓库根目录 |
| `--output` / `-o` | `code-kg.json` | 输出 JSON |
| `--group-by` | `dir` | `language` \| `dir` \| `depth` \| `node` |
| `--max-files` | 800 | 防爆炸上限 |
| `--exclude` | （内置 12 项） | 额外排除目录，逗号分隔 |

### 支持语言

| 语言 | 扩展名 | 解析方式 |
|---|---|---|
| JS / TS | `.js .jsx .ts .tsx .mjs .cjs` | `import` 语句 + `require()` 调用 |
| Go | `.go` | `import "..."` 含多行块 |
| Python | `.py .pyx` | `from ... import ...` 相对 import |
| Rust | `.rs` | `use ...` 路径 |

### 解析限制

- **只解析仓库内**的相对 import；外部包跳过
- 不区分类型 import / 值 import
- 不做语义级解析（不依赖 AST），可能漏掉间接调用
- Python `from . import x` 这种隐式 init 边可能漏

如果需要更精确的图（含函数级、调用图），后续可改用 tree-sitter 重写——本工具的目标是 **5 秒出图**，不是 99% 准确。

### group 策略选择

- `dir`：按一级目录分组（src/api/、src/db/...）—— 适合**架构概览**
- `language`：按语言分组（go, ts, py...）—— 适合**多语言项目**
- `depth`：按目录深度分组（L0, L1, L2...）—— 适合**层级清晰的 monorepo**

## Builder 2: 文档 KG

### 用法

```bash
node .claude/skills/viz-charts/builders/doc-kg.mjs \
  --input ./docs \
  --output ./doc-kg.json \
  --min-mentions 2
```

### 选项

| 选项 | 默认 | 说明 |
|---|---|---|
| `--input` / `-i` | `.` | 文档目录或单个 .md |
| `--output` / `-o` | `doc-kg.json` | 输出 JSON |
| `--min-mentions` | 2 | 术语至少出现 N 次才纳入 concept |
| `--top-terms` | 40 | 自动抽取的高频术语上限 |
| `--max-files` | 200 | 文件数上限 |
| `--include-pdf` | false | 是否扫 PDF（需 `npm i pdf-parse`） |

### 抽取逻辑

每个 .md 文件产生：

1. **1 个 file 节点**：取 H1 作为 name，否则取文件名
2. **N 个 section 节点**：H2 标题（H3+ 不入图，避免噪声）
3. **M 个 concept 节点**：来自三个源
   - **markdown 加粗**（`**term**`）—— 显式概念
   - **行内代码**（含大写 / 含 `.` / 含 `::` 的 `` `code` ``）—— 标识符术语
   - **高频短语**（≥ `--min-mentions` 次）—— 文本挖掘补漏

### 边类型

| type | 含义 |
|---|---|
| `parent-of` | file → 它的 section |
| `links-to` | file → 它通过 `[](xxx.md)` 链接到的 file |
| `mentioned-in` | concept → 提及它的 file |

### group 划分

固定三组：`document` / `section` / `concept`。

## Builder 3: 自定义数据

如果你的数据不来自代码或文档（如客户关系、订单流、组织结构），直接构造 JSON 喂 `data-graph.html` viewer。

### 最小例子

```json
{
  "nodes": [
    { "id": "ceo",  "name": "CEO",        "group": "exec",     "size": 12 },
    { "id": "cto",  "name": "CTO",        "group": "exec",     "size": 10 },
    { "id": "lead", "name": "Eng Lead",   "group": "manager",  "size": 6  },
    { "id": "ic1",  "name": "Engineer A", "group": "ic",       "size": 4  }
  ],
  "links": [
    { "source": "ceo", "target": "cto",  "type": "manages" },
    { "source": "cto", "target": "lead", "type": "manages" },
    { "source": "lead","target": "ic1",  "type": "manages" }
  ],
  "meta": {
    "title": "组织架构",
    "subtitle": "Q2 2026",
    "stats": { "nodes": 4, "edges": 3, "groups": 3 }
  }
}
```

## 渲染流程

1. 选 viewer 模板（code-graph / doc-graph / data-graph）
2. 用 `cat`、`sed` 或脚本替换：
   - `{{TITLE}}`
   - `{{SUBTITLE}}`
   - `{{REPORT_TYPE}}` （比如 `CODE KG`）
   - `{{THEME}}` （`terminal` 或 `deck`）
   - `{{KG_DATA_JSON}}` （整个 JSON 文件内容）
3. 用浏览器打开

### 一键渲染脚本

```bash
#!/bin/bash
TPL=".claude/skills/viz-charts/templates/kg3d/code-graph.html"
DATA="code-kg.json"
OUT="code-kg.html"

python3 -c "
import json, sys
viewer = open('$TPL').read()
data   = json.dumps(json.load(open('$DATA')), ensure_ascii=False, indent=2)
out = (viewer
  .replace('{{TITLE}}', '我的项目')
  .replace('{{SUBTITLE}}', '代码结构 KG')
  .replace('{{REPORT_TYPE}}', 'CODE KG')
  .replace('{{KG_DATA_JSON}}', data)
  .replace('{{THEME}}', 'terminal'))
open('$OUT', 'w').write(out)
print('rendered:', '$OUT')
"
```

## 性能预估

| 节点数 | 边数 | 渲染体验 |
|---|---|---|
| < 200 | < 500 | 流畅，桌面/手机均可 |
| 200-1000 | 500-3000 | 桌面流畅，手机略卡 |
| 1000-5000 | 3000-15000 | 仅桌面，需 GPU |
| > 5000 | > 15000 | 不建议 — 拆图，或换专业工具（Gephi、neo4j） |

## 反模式

- ❌ 把代码 KG 和文档 KG 合在一个 viewer 里（语义混乱）
- ❌ group 超过 8 类（颜色循环复用，无法区分）
- ❌ 节点 size 极差超过 10 倍（小节点看不见、大节点遮挡）
- ❌ 边 type 用了但 viewer 不展示（白做 —— 当前 viewer 在详情面板展示 type）
- ❌ 用 3D KG 替代静态架构图（< 30 节点用 Mermaid 反而更清晰）
- ❌ 公司机密代码生成的 KG 上传到公网（注意 desc 字段不要包含敏感信息）
