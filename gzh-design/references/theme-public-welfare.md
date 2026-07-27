# 公众号排版组件库 - 公益倡议风

## 设计变量速查表

| 项 | 值 |
|---|---|
| 主色 | `#0F766E` |
| 浅底 | `#F0FDFA` |
| 深字 | `#134E4A` |
| 正文 | `#475569` |
| 暖色 | `#F59E0B` |

气质：可信、温暖、行动导向。适合公益倡议、志愿者招募、ESG、公共议题。

## 组件 HTML

### 倡议封面

```html
<section style="margin:0 auto 24px;padding:26px 22px;border-radius:16px;background:#F0FDFA;border:1px solid #99F6E4;">
  <p style="margin:0 0 10px;font-size:13px;color:#0F766E;font-weight:900;"><span leaf="">PUBLIC GOOD</span></p>
  <h1 style="margin:0 0 14px;font-size:24px;line-height:1.35;color:#134E4A;font-weight:900;"><span leaf="">这里放公益倡议标题</span></h1>
  <p style="margin:0;font-size:15px;line-height:1.95;color:#475569;"><span leaf="">用真诚、具体的话说明这个议题和每个人有什么关系。</span></p>
</section>
```

### 行动章节

```html
<section style="margin:28px 0 14px;padding:0 0 0 12px;border-left:4px solid #0F766E;">
  <p style="margin:0 0 4px;font-size:12px;color:#14B8A6;font-weight:900;"><span leaf="">ACTION 01</span></p>
  <h2 style="margin:0;font-size:20px;line-height:1.45;color:#134E4A;font-weight:900;"><span leaf="">章节标题</span></h2>
</section>
```

### 事实说明卡

```html
<section style="margin:18px 0;padding:18px;border-radius:14px;background:#FFFFFF;border:1px solid #CCFBF1;">
  <p style="margin:0 0 8px;font-size:13px;color:#0F766E;font-weight:900;"><span leaf="">事实说明</span></p>
  <p style="margin:0;font-size:15px;line-height:1.95;color:#334155;"><span leaf="">这里放可核查事实、数据来源、服务对象或问题现状。</span></p>
</section>
```

### 温暖引言

```html
<section style="margin:18px 0;padding:16px 18px;border-radius:14px;background:#FFFBEB;border:1px solid #FDE68A;">
  <p style="margin:0;font-size:15px;line-height:1.95;color:#92400E;"><span leaf="">一句温暖但不煽情的话，帮助读者理解行动背后的真实处境。</span></p>
</section>
```

### 参与方式

```html
<section style="margin:28px 0 0;padding:20px;border-radius:16px;background:#134E4A;">
  <p style="margin:0 0 8px;font-size:13px;color:#99F6E4;font-weight:900;"><span leaf="">参与方式</span></p>
  <p style="margin:0;font-size:16px;line-height:1.9;color:#FFFFFF;font-weight:800;"><span leaf="">转发给需要的人、报名志愿者、捐出闲置物资，任选一种就能开始。</span></p>
</section>
```

## 完整文章模板骨架

倡议封面 → 温暖引言 → 行动章节 → 正文段落 → 事实说明卡 → 参与方式 → 作者/机构签名区。

## 文章类型 -> 组件组合配方表

| 类型 | 核心组合 |
|---|---|
| 公益倡议 | 倡议封面 + 温暖引言 + 参与方式 |
| 志愿者招募 | 倡议封面 + 行动章节 + 事实说明卡 + 参与方式 |
| ESG 报告 | 倡议封面 + 行动章节 + 事实说明卡 |

## Markdown -> 组件映射规则表

| Markdown | 映射 |
|---|---|
| `#` | 倡议封面 |
| `##` | 行动章节 |
| `>` | 温暖引言 |
| 数据/事实 | 事实说明卡 |
| 报名/捐赠/转发 | 参与方式 |
