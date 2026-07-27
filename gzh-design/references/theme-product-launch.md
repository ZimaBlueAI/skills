# 公众号排版组件库 - 产品宣发风

## 设计变量速查表

| 项 | 值 |
|---|---|
| 主色 | `#0EA5E9` |
| 深色 | `#0F172A` |
| 浅底 | `#F0F9FF` |
| 正文 | `#475569` |
| 强调 | `#FACC15` |

气质：产品发布、功能卖点、转化导向。适合新品、版本更新、活动推广、增长案例。

## 组件 HTML

### 发布封面

```html
<section style="margin:0 auto 24px;padding:28px 22px;border-radius:18px;background:linear-gradient(135deg,#0EA5E9,#2563EB);">
  <p style="margin:0 0 12px;font-size:13px;color:#BAE6FD;font-weight:900;"><span leaf="">PRODUCT LAUNCH</span></p>
  <h1 style="margin:0 0 14px;font-size:25px;line-height:1.35;color:#FFFFFF;font-weight:900;"><span leaf="">这里放产品发布标题</span></h1>
  <p style="margin:0;font-size:15px;line-height:1.9;color:#E0F2FE;"><span leaf="">用一句话说清新功能给用户带来的直接收益。</span></p>
</section>
```

### 卖点章节

```html
<section style="margin:28px 0 14px;">
  <p style="margin:0 0 6px;font-size:12px;color:#0EA5E9;font-weight:900;"><span leaf="">FEATURE 01</span></p>
  <h2 style="margin:0;font-size:21px;line-height:1.45;color:#0F172A;font-weight:900;"><span leaf="">章节标题</span></h2>
</section>
```

### 功能卖点卡

```html
<section style="margin:18px 0;padding:18px;border-radius:14px;background:#F0F9FF;border:1px solid #BAE6FD;">
  <p style="margin:0 0 8px;font-size:13px;color:#0284C7;font-weight:900;"><span leaf="">核心卖点</span></p>
  <p style="margin:0;font-size:16px;line-height:1.85;color:#0F172A;font-weight:800;"><span leaf="">把复杂流程压缩成一个可感知的用户收益。</span></p>
  <p style="margin:8px 0 0;font-size:14px;line-height:1.8;color:#475569;"><span leaf="">这里补充适用人群、场景或前后对比。</span></p>
</section>
```

### 对比结论

```html
<section style="margin:18px 0;padding:16px 18px;border-radius:12px;background:#FFFFFF;border:1px solid #E2E8F0;">
  <p style="margin:0;font-size:15px;line-height:1.9;color:#334155;"><span leaf="">过去：流程长、协作慢、反馈散。现在：一次配置，自动收敛结果。</span></p>
</section>
```

### 行动按钮卡

```html
<section style="margin:28px 0 0;padding:20px;border-radius:16px;background:#0F172A;">
  <p style="margin:0 0 8px;font-size:13px;color:#FACC15;font-weight:900;"><span leaf="">立即行动</span></p>
  <p style="margin:0;font-size:16px;line-height:1.9;color:#FFFFFF;font-weight:800;"><span leaf="">现在就把第一个场景接入，看看它能替你省下多少重复操作。</span></p>
</section>
```

## 完整文章模板骨架

发布封面 → 卖点章节 → 功能卖点卡 → 对比结论 → 通用图片/截图 → 行动按钮卡 → 作者签名区。

## 文章类型 -> 组件组合配方表

| 类型 | 核心组合 |
|---|---|
| 新品发布 | 发布封面 + 功能卖点卡 + 行动按钮卡 |
| 版本更新 | 发布封面 + 卖点章节 + 对比结论 |
| 活动推广 | 发布封面 + 功能卖点卡 + 行动按钮卡 |

## Markdown -> 组件映射规则表

| Markdown | 映射 |
|---|---|
| `#` | 发布封面 |
| `##` | 卖点章节 |
| `>` | 对比结论 |
| 功能/收益 | 功能卖点卡 |
| CTA | 行动按钮卡 |
