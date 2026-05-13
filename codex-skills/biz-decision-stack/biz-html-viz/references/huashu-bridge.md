# huashu-bridge: biz-html-viz 与 huashu-design 的有限桥接

> v2 新增。biz-html-viz 的核心定位（决策报告、零动效、终端风）**不应该**依赖 huashu-design。本文件只描述**两个有限桥接点**：5 维评审的评分标准引用、以及 board-brief 的可选 PDF 导出。

## 桥接哲学：默认不依赖

biz-html-viz 与 viz-deck 不同——viz-deck 拥抱多模产出（含 MP4/PPTX），biz-html-viz 是**单一形态**（终端风 HTML，零动效，打印归档）。所以：

- ❌ 不引入 motion / 动画 / MP4 导出
- ❌ 不引入 20 哲学切换（终端风**就是**唯一哲学）
- ❌ 不引入设备外壳 / prototype 模式
- ✅ 引入 5 维评审标准（concept，不引资源）
- ✅ 引入可选 PDF 导出（仅当用户要"打印归档" PDF 时）

## 桥接点 1: 5 维评审标准（必装）

`references/critique-5dim.md` 引用了 huashu 的 `critique-guide.md` 评分标准。

桥接调用：**仅读取**（read-only），不执行 huashu 脚本。

```bash
HUASHU="$HOME/.claude/skills/huashu-design"
test -f "$HUASHU/references/critique-guide.md" && \
  echo "huashu critique standard available" || \
  echo "huashu not installed — using offline mirror in critique-5dim.md"
```

如果 huashu 未安装也 OK——critique-5dim.md 里已经把 5 维评分标准的核心条款复述了一遍（终端风适配版）。不会 hard fail。

## 桥接点 2: HTML → PDF（可选）

仅当用户明确说"把这份 board-brief 转成 PDF"时启用。**不要自动**——biz-html-viz 的 7 份模板已经内置 `@media print` 规则，用户 Ctrl+P 就能出 PDF，比脚本可靠。

只有以下情况调用 huashu 的 PDF 脚本：

1. 用户要"批量"导出 7 份 PDF（orchestrator 全流程）
2. 用户要"高质量、可选页眉/页脚"的 PDF
3. 用户要把 index.html 出成多页 PDF 而非长滚动

```bash
HUASHU="$HOME/.claude/skills/huashu-design"
node "$HUASHU/scripts/export_deck_pdf.mjs" \
  --input  ./output/index.html \
  --output ./output/all-hands-bundle.pdf \
  --landscape false \
  --width 1280 --height 1810   # A4 portrait pixel-ish
```

横版（landscape）默认 OFF——决策报告以纵版 A4 为主。

## 不做的事

- ❌ 不引入 huashu 的 BGM、设备外壳、动画引擎、TTS 工具链——决策报告不该有这些
- ❌ 不在 board-brief 模板里调用 huashu render-video.js——零动效原则
- ❌ 不把 huashu 的 design-styles.md 列为 biz-html-viz 的设计选项——终端风是单一哲学
- ❌ 不要让 design-critic subagent 越权调用 viz-deck（评决策报告必须用终端风评审模板）

## 许可证

huashu-design 个人使用免费，商用需独立授权。本桥接只读取标准文档 + 可选调用 PDF 脚本，**未引入任何 huashu 商用受限资产**（BGM、设计 token、生成画面等）。
