# 主题索引与选择决策表

本表是主题信息的单一来源。工作流第 1 步据此展示选项，第 2 步按“组件库文件”读取主题库，下划线标记按“正文下划线 CSS”取值。

每个主题的英文标识 = “组件库文件”去掉 `theme-` 前缀与 `.md` 后缀。产物命名使用 `{主题中文名}({标识}).html`。

## 已注册主题

| 主题 | 主色 | 适用场景 | 组件库文件 | 正文下划线 CSS |
|------|------|---------|-----------|---------------|
| 摸鱼绿 | `#059669` emerald | 教程、测评、清单、工具盘点（卡片丰富、信息密度高，默认推荐） | `references/theme-moyu-green.md` | `border-bottom:2px solid #A7F3D0;font-weight:600;` |
| 红白色系 | `#DC2626` 正红 | 深度分析、观点、力量感话题（经典编辑风，编号章节+引言卡+签名区，红色克制点睛） | `references/theme-red-white.md` | `border-bottom:2px solid #FECACA;font-weight:600;` |
| 石墨极简风 | `#52525B` 石墨灰 | 设计、科技评论、专业观点、高端品牌（极简克制、留白理性、全灰阶） | `references/theme-graphite-minimal.md` | `border-bottom:2px solid #52525B;font-weight:600;` |
| 留白禅意风 | `#4A5D52` 墨绿 | 禅意冥想、极简生活、深度随笔、艺术留白（呼吸感最强） | `references/theme-zen-whitespace.md` | `border-bottom:1.5px solid #B5C8BC;font-weight:500;` |
| 摸鱼票据风 | `#059669` emerald | 测评、工具对比、创意评测（票据/门票视觉隐喻，星级评分+编号+硬阴影卡片） | `references/theme-moyu-ticket.md` | `border-bottom:2px solid #A7F3D0;font-weight:600;` |
| 橄榄手记 | `#1e1f23` 墨黑（配橙 `#ed7b2f`） | 内刊手记、深度评测、案例复盘、系统性说明文档（编辑部内刊质感，分节形式多样，信息密度偏高） | `references/theme-olive-journal.md` | `border-bottom:2px solid #ed7b2f;font-weight:600;` |
| 科技蓝图 | `#2563EB` 蓝 | 科技趋势、SaaS、研发方案、产品技术解读、行业报告（理性蓝图、模块卡、指标条） | `references/theme-tech-blueprint.md` | `border-bottom:2px solid #BFDBFE;font-weight:600;` |
| 极客终端风 | `#16A34A` 绿 | 开发者教程、开源项目、工具链、命令行、系统架构（终端感、等宽字体、状态标签） | `references/theme-geek-terminal.md` | `border-bottom:2px solid #86EFAC;font-weight:700;` |
| AI 星云风 | `#7C3AED` 紫 | AI 产品、模型评测、智能体、自动化工作流、AIGC 案例（深浅紫+电光蓝，适度未来感） | `references/theme-ai-nebula.md` | `border-bottom:2px solid #DDD6FE;font-weight:600;` |
| 文艺杂志风 | `#B45309` 琥珀 | 书影音、生活方式、人物随笔、文化观察、品牌故事（杂志刊头、引文、温柔纸感） | `references/theme-literary-zine.md` | `border-bottom:2px solid #FDE68A;font-weight:500;` |
| 自媒体栏目风 | `#F97316` 橙 | 个人号栏目、热点复盘、内容运营、知识号、观点合集（强标题、栏目条、互动 CTA） | `references/theme-creator-media.md` | `border-bottom:2px solid #FED7AA;font-weight:700;` |
| 产品宣发风 | `#0EA5E9` 天蓝 | 新品发布、功能推广、活动页文案、增长案例、版本更新（卖点卡、对比表、CTA 收束） | `references/theme-product-launch.md` | `border-bottom:2px solid #BAE6FD;font-weight:700;` |
| 公益倡议风 | `#0F766E` 青绿 | 公益倡议、志愿者招募、ESG、公共议题、社区行动（可信、温暖、行动导向） | `references/theme-public-welfare.md` | `border-bottom:2px solid #99F6E4;font-weight:600;` |

## 选择建议

- 用户选择制：用户没指定主题时，把 2-4 个最匹配主题给用户选；最贴合题材的主题标“推荐”。
- 全自动模式：用户明说“直接排/一键/不用问”时自动选题材最契合主题，并在交付时说明理由。
- 同一篇文章只用一套主题，不混搭。

## 下划线色值的权威性

正文关键词下划线一律用上表“正文下划线 CSS”列。组件库里的浅色变体只是局部组件样式，不作为正文关键词标记的权威来源。

## 新主题登记流程

1. 写入 `references/theme-{英文标识}.md`。
2. 在上表登记一行。
3. 跑 `python3 scripts/component_lint.py .` 确认 0 ERROR。

> 用户想要全新风格时，走 `references/theme-generator.md`：按偏好/参考图生成区块库预览，确认后转标准主题库并登记。
