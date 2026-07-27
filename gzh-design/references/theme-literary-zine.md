# 公众号排版组件库 - 文艺杂志风

## 设计变量速查表

| 项 | 值 |
|---|---|
| 主色 | `#B45309` |
| 纸色 | `#FFFBEB` |
| 深字 | `#292524` |
| 正文 | `#57534E` |
| 辅色 | `#A16207` |

气质：文艺、杂志、书影音、人物随笔、文化观察。强调纸感、刊头和留白。

## 组件 HTML

### 杂志刊头

```html
<section style="margin:0 auto 24px;padding:28px 22px;border-radius:4px;background:#FFFBEB;border:1px solid #FDE68A;">
  <p style="margin:0 0 10px;font-size:13px;color:#B45309;font-weight:700;"><span leaf="">LITERARY ZINE</span></p>
  <h1 style="margin:0 0 14px;font-size:25px;line-height:1.35;color:#292524;font-weight:800;"><span leaf="">这里放文章主标题</span></h1>
  <p style="margin:0;font-size:15px;line-height:2;color:#57534E;"><span leaf="">像杂志导语一样写一段柔和但有判断的引入。</span></p>
</section>
```

### 栏目章节

```html
<section style="margin:30px 0 14px;border-top:1px solid #E7E5E4;padding-top:14px;">
  <p style="margin:0 0 4px;font-size:12px;color:#B45309;font-weight:700;"><span leaf="">Essay 01</span></p>
  <h2 style="margin:0;font-size:21px;line-height:1.45;color:#292524;font-weight:800;"><span leaf="">章节标题</span></h2>
</section>
```

### 书页引文

```html
<section style="margin:18px 0;padding:18px 20px;background:#FFFFFF;border-left:4px solid #D97706;box-shadow:0 8px 20px rgba(180,83,9,.08);">
  <p style="margin:0;font-size:16px;line-height:2;color:#44403C;font-weight:600;"><span leaf="">这里放一句有质感的引文、观点或人物原话。</span></p>
</section>
```

### 片段札记

```html
<section style="margin:18px 0;padding:16px 18px;border-radius:10px;background:#FEF3C7;">
  <p style="margin:0;font-size:15px;line-height:2;color:#57534E;"><span leaf="">这一块适合放观察、片段、场景描写或不适合压成结论的细节。</span></p>
</section>
```

### 余韵收束

```html
<section style="margin:30px 0 0;padding:20px 0;border-top:1px solid #E7E5E4;border-bottom:1px solid #E7E5E4;">
  <p style="margin:0;font-size:15px;line-height:2;color:#57534E;"><span leaf="">我是 {{作者名}}，{{一句话简介}}。愿这篇文章留下一个可以慢慢回味的问题。</span></p>
</section>
```

## 完整文章模板骨架

杂志刊头 → 开头引文 → 栏目章节 → 正文段落 → 书页引文/片段札记 → 余韵收束。

## 文章类型 -> 组件组合配方表

| 类型 | 核心组合 |
|---|---|
| 文化观察 | 杂志刊头 + 栏目章节 + 书页引文 |
| 生活随笔 | 杂志刊头 + 片段札记 + 余韵收束 |
| 人物故事 | 杂志刊头 + 书页引文 + 正文段落 |

## Markdown -> 组件映射规则表

| Markdown | 映射 |
|---|---|
| `#` | 杂志刊头 |
| `##` | 栏目章节 |
| `>` | 书页引文 |
| 场景片段 | 片段札记 |
| 结尾 | 余韵收束 |
