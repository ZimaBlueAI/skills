# 公众号排版组件库 - 极客终端风

## 设计变量速查表

| 项 | 值 |
|---|---|
| 主色 | `#16A34A` |
| 背景 | `#0B1220` |
| 卡片 | `#111827` |
| 浅字 | `#D1FAE5` |
| 正文 | `#D1D5DB` |

气质：开发者、命令行、开源项目、工具链。适合技术教程、CLI 工具、工程实践。

## 组件 HTML

### 终端封面

```html
<section style="margin:0 auto 24px;padding:22px;border-radius:12px;background:#0B1220;border:1px solid #1F2937;font-family:Consolas,Monaco,monospace;">
  <p style="margin:0 0 12px;font-size:13px;color:#86EFAC;"><span leaf="">$ run article --mode=gzh</span></p>
  <h1 style="margin:0 0 12px;font-size:23px;line-height:1.35;color:#F9FAFB;font-weight:800;"><span leaf="">这里放文章主标题</span></h1>
  <p style="margin:0;font-size:14px;line-height:1.9;color:#D1D5DB;"><span leaf="">用开发者能快速扫描的方式交代目标、输入、输出和限制条件。</span></p>
</section>
```

### 命令式章节

```html
<section style="margin:28px 0 14px;padding:12px 14px;border-radius:10px;background:#111827;border:1px solid #1F2937;font-family:Consolas,Monaco,monospace;">
  <p style="margin:0;font-size:15px;line-height:1.7;color:#86EFAC;font-weight:700;"><span leaf="">[01] 章节标题</span></p>
</section>
```

### 状态输出卡

```html
<section style="margin:18px 0;padding:16px;border-radius:10px;background:#111827;border:1px solid #374151;font-family:Consolas,Monaco,monospace;">
  <p style="margin:0 0 8px;font-size:13px;color:#22C55E;"><span leaf="">STATUS: PASS</span></p>
  <p style="margin:0;font-size:14px;line-height:1.8;color:#D1D5DB;"><span leaf="">这里写关键检查结果、配置差异或工程结论。</span></p>
</section>
```

### Patch Note

```html
<section style="margin:18px 0;padding:16px 18px;border-left:4px solid #22C55E;background:#F0FDF4;">
  <p style="margin:0;font-size:15px;line-height:1.9;color:#14532D;"><span leaf="">这段用于强调修复点、迁移步骤或需要读者立即执行的命令前说明。</span></p>
</section>
```

### Maintainer 签名

```html
<section style="margin:28px 0 0;padding:18px;border-radius:12px;background:#F9FAFB;border:1px solid #E5E7EB;">
  <p style="margin:0;font-size:14px;line-height:1.9;color:#374151;"><span leaf="">我是 {{作者名}}，{{一句话简介}}。</span></p>
  <p style="margin:8px 0 0;font-size:14px;line-height:1.9;color:#16A34A;font-weight:700;"><span leaf="">如果这篇对你有帮助，欢迎点赞、在看、转发。</span></p>
</section>
```

## 完整文章模板骨架

终端封面 → 命令式章节 → 正文段落 → 状态输出卡/通用代码块 → Patch Note → Maintainer 签名。

## 文章类型 -> 组件组合配方表

| 类型 | 核心组合 |
|---|---|
| 开发教程 | 终端封面 + 命令式章节 + 通用代码块 + Patch Note |
| 工具测评 | 终端封面 + 状态输出卡 + 正文段落 + Maintainer 签名 |
| 开源发布 | 终端封面 + 状态输出卡 + Patch Note + Maintainer 签名 |

## Markdown -> 组件映射规则表

| Markdown | 映射 |
|---|---|
| `#` | 终端封面 |
| `##` | 命令式章节 |
| `>` | Patch Note |
| 状态/结果 | 状态输出卡 |
| 末尾署名 | Maintainer 签名 |
