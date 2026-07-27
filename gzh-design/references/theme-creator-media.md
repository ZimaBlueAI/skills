# 公众号排版组件库 - 自媒体栏目风

## 设计变量速查表

| 项 | 值 |
|---|---|
| 主色 | `#F97316` |
| 浅底 | `#FFF7ED` |
| 深字 | `#1F2937` |
| 正文 | `#4B5563` |
| 强调 | `#FB923C` |

气质：栏目化、强标题、易转发。适合个人号、热点复盘、内容运营、知识号。

## 组件 HTML

### 栏目封面

```html
<section style="margin:0 auto 24px;padding:24px 20px;border-radius:14px;background:#FFF7ED;border:1px solid #FED7AA;">
  <p style="margin:0 0 10px;font-size:13px;color:#F97316;font-weight:900;"><span leaf="">今日栏目</span></p>
  <h1 style="margin:0 0 12px;font-size:24px;line-height:1.35;color:#1F2937;font-weight:900;"><span leaf="">这里放文章主标题</span></h1>
  <p style="margin:0;font-size:15px;line-height:1.9;color:#4B5563;"><span leaf="">用一句钩子说明为什么读者现在就要看这篇。</span></p>
</section>
```

### 爆点章节

```html
<section style="margin:28px 0 14px;padding:10px 14px;border-radius:999px;background:#F97316;">
  <h2 style="margin:0;font-size:18px;line-height:1.5;color:#FFFFFF;font-weight:900;"><span leaf="">01 章节标题</span></h2>
</section>
```

### 要点卡

```html
<section style="margin:18px 0;padding:16px 18px;border-radius:14px;background:#FFFFFF;border:1px solid #FED7AA;box-shadow:0 8px 18px rgba(249,115,22,.10);">
  <p style="margin:0 0 8px;font-size:13px;color:#F97316;font-weight:900;"><span leaf="">重点来了</span></p>
  <p style="margin:0;font-size:15px;line-height:1.9;color:#374151;"><span leaf="">这里写读者最该带走的结论，适合做转发截图里的核心句。</span></p>
</section>
```

### 互动提问

```html
<section style="margin:18px 0;padding:16px 18px;border-radius:14px;background:#FFF7ED;">
  <p style="margin:0;font-size:15px;line-height:1.9;color:#9A3412;font-weight:700;"><span leaf="">你更认同哪一种做法？欢迎在评论区留下你的判断。</span></p>
</section>
```

### 三连 CTA

```html
<section style="margin:28px 0 0;padding:18px;border-radius:14px;background:#1F2937;">
  <p style="margin:0;font-size:15px;line-height:1.9;color:#FFFFFF;"><span leaf="">我是 {{作者名}}，{{一句话简介}}。如果有收获，欢迎点赞、在看、转发。</span></p>
</section>
```

## 完整文章模板骨架

栏目封面 → 目录/导读 → 爆点章节 → 正文段落 → 要点卡/互动提问 → 三连 CTA。

## 文章类型 -> 组件组合配方表

| 类型 | 核心组合 |
|---|---|
| 热点复盘 | 栏目封面 + 爆点章节 + 要点卡 |
| 知识号教程 | 栏目封面 + 爆点章节 + 要点卡 + 互动提问 |
| 观点合集 | 栏目封面 + 要点卡 + 三连 CTA |

## Markdown -> 组件映射规则表

| Markdown | 映射 |
|---|---|
| `#` | 栏目封面 |
| `##` | 爆点章节 |
| `>` | 要点卡 |
| 提问句 | 互动提问 |
| 末尾 CTA | 三连 CTA |
