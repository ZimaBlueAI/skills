# zima-design audit 动词示范（anti-slop 引擎） — 对 `demo-before-ai-slop.html` 的审计报告

> 这是 zima-design（anti-slop 引擎）**audit 动词**的输出示范：对反面教材页面跑 slop-test 通用子集，逐关卡给出 PASS / FAIL 与证据。
> 重设计结论：FAIL 数量过多，修补不如重做 → 走 **redesign 动词**，产出 `demo-after-redesign-hum.html`。

## 审计对象

- 页面：`demo-before-ai-slop.html`（虚构产品 Curio 的落地页）
- 审计基准：`references/slop-test.md` 通用子集 + `references/anti-patterns.md`
- 结论：**24 项抽查，17 FAIL** → 判定为典型 AI-slop，建议整页重设计

## 逐关卡结果（节选）

| # | 关卡 | 结果 | 证据 |
|---|------|------|------|
| 1 | 禁居中 hero 堆叠（badge → 居中 H1 → 两行副标 → 实心+幽灵双 CTA） | ❌ FAIL | `.hero` 整段就是该模板，`text-align: center` |
| 2 | 禁 H1 上方 badge-pill | ❌ FAIL | `✨ 全新 AI 驱动 · 现已上线` |
| 3 | 禁紫→蓝对角渐变默认底 | ❌ FAIL | `linear-gradient(135deg, #667eea, #764ba2)`（教科书级 AI 配色） |
| 4 | 标题禁斜体 | ❌ FAIL | `.hero h1`、`h2`、`.footer-statement` 均 `font-style: italic` |
| 5 | 色值经由令牌（`:root` 变量）而非散落 hex | ❌ FAIL | 全页 0 个 CSS 变量，14+ 处内联 hex |
| 6 | 禁三等宽卡片行（图标+标题+两行灰字 ×3） | ❌ FAIL | `.cards` 精确命中，且用 emoji 当图标 |
| 7 | 禁 emoji 代替图标 | ❌ FAIL | 🚀 🧠 🔥 |
| 8 | 禁卡片顶部/左侧 accent 条 | ❌ FAIL | `border-top: 4px solid #667eea` |
| 9 | 禁全大写灰 eyebrow 当壁纸（每节一个） | ❌ FAIL | 4 个 section 全部相同 `.eyebrow` |
| 10 | 诚实文案：禁编造用户量/提升率 | ❌ FAIL | `50,000+ 团队`、`+47% 留存`、`4.9/5` 均无出处 |
| 11 | 诚实文案：禁虚构证言（尤其「姓名 · 指标」统一署名语法） | ❌ FAIL | 三张证言卡全部虚构，署名清一色 `姓名 · 指标` |
| 12 | 禁空话动词（革命性/解锁/赋能/超充/生态/旅程） | ❌ FAIL | hero 副标一句话命中 6 个 |
| 13 | 禁巨型宣言 footer + `auto 1fr 1fr 1fr` 元信息网格 | ❌ FAIL | `.footer-statement` + `.footer-grid` 精确命中 |
| 14 | 渐变禁三连（背景+标题+按钮不同时上渐变） | ❌ FAIL | hero 背景渐变 + `.stat-num` 文字渐变 |
| 15 | 响应式：320px 无横向滚动、内容不硬挤 | ❌ FAIL | 三卡网格无断点；用 `overflow-x: hidden` 把溢出藏起来（应为治理后 `clip`） |
| 16 | `prefers-reduced-motion` 降级 | ❌ FAIL | 无任何处理 |
| 17 | 结构多样性：hero 之后的「尾巴」不得是 features→证言×3→宣言 footer 模板连招 | ❌ FAIL | 完整命中模板尾巴 |
| 18 | 字体经由令牌声明 | ⚠️ PASS* | 用了系统栈（勉强过，但 Inter 兜底也是 slop 惯用相） |
| 19 | 焦点可见（`:focus-visible`） | ❌ FAIL | 按钮无焦点样式 |
| 20 | 语义结构（main/header/footer/heading 层级） | ⚠️ PASS* | 有 h1→h2→h3，但无 `<main>` |
| 21 | 对比度（正文 ≥ 4.5:1） | ✅ PASS | `#333`/`#fff` 达标（唯一像样的地方） |
| 22 | 一处出格时刻（off-grid / 非对称） | ❌ FAIL | 全页居中等宽块堆叠，零非对称 |
| 23 | 一处「人为设计的例外」 | ❌ FAIL | 无 |
| 24 | 动效克制且有归属（非全员 fade-in / 非零动效裸奔） | ❌ FAIL | 零交互反馈，所有可交互元素无状态响应 |

## 重设计要点（→ `demo-after-redesign-hum.html`）

1. **选题路由**：每日好奇心 app → 命中 Hum 主题 brief 关键词（daily / habit / streak / learning / playful）；宏结构选 **Narrative Workflow**（产品确实是"每天一条 → 收进书架 → 连击"的顺序叙事）。
2. **令牌化**：全部色值/字体/圆角/间距收进 `:root`，正文墨色用 `color-mix` 调透明度，不新增 hex。
3. **hero 去居中**：文左图右分栏，产品卡自己演示自己（今天这条知识直接放在 hero 里），外加 1.5° 倾斜作为 designed exception。
4. **三等卡 → 编号叙事**：`1.0 → 2.0 → 3.0` 各占一条 accent 带（梨黄/天青/珊瑚各守其面），放大编号溢出边缘作为 off-grid 时刻。
5. **文案诚实化**：删除全部编造指标与证言；连击数标注「示例数据」；「关于我们」改为可核实的实话（三个人、只靠订阅）。
6. **动效有归属**：按钮 push 系统（按下即反馈）、计数器 tick-up、梨黄圆点角色时刻 + CTA 星爆，全部带 `prefers-reduced-motion` 降级。
7. **响应式治理**：`overflow-x: clip`、`minmax(0, 1fr)` 网格轨、720px 单列断点、320px 无横滚。
8. **紧凑单行 footer** 替代宣言 footer。

---
*本报告是 demo 示范产物；实际 audit 会跑完整 57 关卡并按 genre 加载对应分卷。*
