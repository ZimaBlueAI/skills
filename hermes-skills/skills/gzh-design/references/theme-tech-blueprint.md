# 公众号排版组件库 - 科技蓝图

## 设计变量速查表

| 项 | 值 |
|---|---|
| 主色 | `#2563EB` |
| 浅底 | `#EFF6FF` |
| 深字 | `#0F172A` |
| 正文 | `#334155` |
| 强调 | `#38BDF8` |

气质：理性、清晰、系统化。适合科技趋势、研发方案、SaaS 解读、行业报告。

## 组件 HTML

### 封面蓝图卡

```html
<section style="margin:0 auto 24px;padding:28px 22px;border-radius:16px;background:linear-gradient(135deg,#EFF6FF,#FFFFFF);border:1px solid #DBEAFE;box-shadow:0 10px 28px rgba(37,99,235,.10);">
  <p style="margin:0 0 12px;font-size:13px;letter-spacing:0;color:#2563EB;font-weight:700;"><span leaf="">TECH BLUEPRINT</span></p>
  <h1 style="margin:0 0 14px;font-size:24px;line-height:1.35;color:#0F172A;font-weight:800;"><span leaf="">这里放文章主标题</span></h1>
  <p style="margin:0;font-size:15px;line-height:1.9;color:#334155;"><span leaf="">用一句话说明这篇文章解决什么技术问题，或者给出怎样的趋势判断。</span></p>
</section>
```

### 章节标题

```html
<section style="margin:28px 0 14px;padding:0 0 0 12px;border-left:4px solid #2563EB;">
  <p style="margin:0 0 4px;font-size:12px;color:#60A5FA;font-weight:700;"><span leaf="">01 / MODULE</span></p>
  <h2 style="margin:0;font-size:20px;line-height:1.45;color:#0F172A;font-weight:800;"><span leaf="">章节标题</span></h2>
</section>
```

### 指标模块卡

```html
<section style="margin:18px 0;padding:18px;border-radius:12px;background:#F8FAFC;border:1px solid #E2E8F0;">
  <p style="margin:0 0 8px;font-size:13px;color:#2563EB;font-weight:700;"><span leaf="">关键指标</span></p>
  <p style="margin:0;font-size:28px;line-height:1.2;color:#0F172A;font-weight:800;"><span leaf="">73%</span></p>
  <p style="margin:8px 0 0;font-size:14px;line-height:1.8;color:#475569;"><span leaf="">指标解释写在这里，突出变化、影响和下一步动作。</span></p>
</section>
```

### 系统提示块

```html
<section style="margin:18px 0;padding:16px 18px;border-radius:12px;background:#EFF6FF;border:1px solid #BFDBFE;">
  <p style="margin:0;font-size:15px;line-height:1.9;color:#1E3A8A;"><span leaf="">把关键结论写成清晰的系统提示，适合放架构判断、风险提醒或决策建议。</span></p>
</section>
```

### 收束行动卡

```html
<section style="margin:28px 0 0;padding:20px;border-radius:14px;background:#0F172A;">
  <p style="margin:0 0 8px;font-size:13px;color:#93C5FD;font-weight:700;"><span leaf="">NEXT STEP</span></p>
  <p style="margin:0;font-size:16px;line-height:1.9;color:#FFFFFF;font-weight:700;"><span leaf="">接下来可以从一个小模块开始验证，而不是一次性重构整个系统。</span></p>
</section>
```

## 完整文章模板骨架

封面蓝图卡 → 开头引言/目录 → 章节标题 → 正文段落 → 指标模块卡/系统提示块 → 通用图片或代码块 → 结尾行动卡 → 作者签名区。

## 文章类型 -> 组件组合配方表

| 类型 | 核心组合 |
|---|---|
| 科技趋势 | 封面蓝图卡 + 章节标题 + 指标模块卡 + 系统提示块 |
| 研发方案 | 封面蓝图卡 + 章节标题 + 通用代码块 + 系统提示块 |
| 行业报告 | 封面蓝图卡 + 指标模块卡 + 正文段落 + 收束行动卡 |

## Markdown -> 组件映射规则表

| Markdown | 映射 |
|---|---|
| `#` | 封面蓝图卡 |
| `##` | 章节标题 |
| `>` | 系统提示块 |
| 数据/百分比 | 指标模块卡 |
| 结尾 CTA | 收束行动卡 |
