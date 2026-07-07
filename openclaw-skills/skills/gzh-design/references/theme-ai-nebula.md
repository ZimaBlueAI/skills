# 公众号排版组件库 - AI 星云风

## 设计变量速查表

| 项 | 值 |
|---|---|
| 主色 | `#7C3AED` |
| 辅色 | `#06B6D4` |
| 浅底 | `#F5F3FF` |
| 深字 | `#1E1B4B` |
| 正文 | `#475569` |

气质：AI、智能体、模型、自动化。使用紫和青作强调，避免过度霓虹。

## 组件 HTML

### 星云封面

```html
<section style="margin:0 auto 24px;padding:28px 22px;border-radius:18px;background:linear-gradient(135deg,#F5F3FF,#ECFEFF);border:1px solid #DDD6FE;">
  <p style="margin:0 0 12px;font-size:13px;color:#7C3AED;font-weight:800;"><span leaf="">AI NEBULA</span></p>
  <h1 style="margin:0 0 14px;font-size:24px;line-height:1.35;color:#1E1B4B;font-weight:900;"><span leaf="">这里放文章主标题</span></h1>
  <p style="margin:0;font-size:15px;line-height:1.9;color:#475569;"><span leaf="">用一句话交代模型、智能体或自动化工作流带来的真实变化。</span></p>
</section>
```

### 推理章节

```html
<section style="margin:28px 0 14px;">
  <p style="margin:0 0 6px;font-size:12px;color:#06B6D4;font-weight:800;"><span leaf="">CHAIN 01</span></p>
  <h2 style="margin:0;font-size:20px;line-height:1.45;color:#1E1B4B;font-weight:900;"><span leaf="">章节标题</span></h2>
</section>
```

### Agent 能力卡

```html
<section style="margin:18px 0;padding:18px;border-radius:14px;background:#FFFFFF;border:1px solid #E9D5FF;box-shadow:0 8px 22px rgba(124,58,237,.08);">
  <p style="margin:0 0 8px;font-size:13px;color:#7C3AED;font-weight:800;"><span leaf="">Agent 能力</span></p>
  <p style="margin:0;font-size:15px;line-height:1.9;color:#334155;"><span leaf="">这里写能力边界、输入输出、成功条件和人工介入点。</span></p>
</section>
```

### 模型判断块

```html
<section style="margin:18px 0;padding:16px 18px;border-radius:14px;background:#F5F3FF;border:1px solid #DDD6FE;">
  <p style="margin:0;font-size:15px;line-height:1.9;color:#4C1D95;"><span leaf="">关键判断：不要只看模型参数，要看任务链路、评测样本和实际失败模式。</span></p>
</section>
```

### 自动化收束

```html
<section style="margin:28px 0 0;padding:20px;border-radius:16px;background:linear-gradient(135deg,#7C3AED,#06B6D4);">
  <p style="margin:0;font-size:16px;line-height:1.9;color:#FFFFFF;font-weight:800;"><span leaf="">下一步，把这个流程拆成可评测、可回滚、可人工接管的自动化节点。</span></p>
</section>
```

## 完整文章模板骨架

星云封面 → 引言 → 推理章节 → 正文段落 → Agent 能力卡/模型判断块 → 通用代码块或图片 → 自动化收束 → 作者签名区。

## 文章类型 -> 组件组合配方表

| 类型 | 核心组合 |
|---|---|
| AI 产品测评 | 星云封面 + Agent 能力卡 + 模型判断块 |
| 智能体方案 | 星云封面 + 推理章节 + Agent 能力卡 + 自动化收束 |
| 模型观察 | 星云封面 + 推理章节 + 模型判断块 |

## Markdown -> 组件映射规则表

| Markdown | 映射 |
|---|---|
| `#` | 星云封面 |
| `##` | 推理章节 |
| `>` | 模型判断块 |
| 能力/边界 | Agent 能力卡 |
| 结尾行动 | 自动化收束 |
