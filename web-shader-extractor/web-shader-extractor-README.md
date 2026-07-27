# web-shader-extractor · 网页 Shader 动效抠取与本地复现

**从真实网页里把 WebGL / WebGPU / Canvas 着色器动效"抠"出来，本地证据匹配复现，再工程化为可编辑项目。** · 移植自 [lixiaolin94/skills](https://github.com/lixiaolin94/skills)（MIT）

> 这不是「DOM/CSS 克隆」工具，也不是「生成漂亮动效」工具。它是**逆向侦察 + 证据复现**工具：
> 锁定渲染面 → 抓 shader/资源/渲染图/时序/输入证据 → 建立证据匹配的本地基线 → 工程化。

---

## 01 · 何时用 / 何时不用

### ✅ 用它当

- 给定一个**网页 URL**，想抠出它的 WebGL / WebGPU / Canvas2D / OffscreenCanvas / shader / 动画 canvas 效果。
- 想把某个**动态背景 / 产品 shader / 交互式 WebGL 场景 / Canvas 视觉**在本地复现并替换数据。
- 想先建立**证据匹配的基线**（不靠肉眼凑色），再转成可编辑工程。
- 想调查目标渲染面绑定的 shader / 渲染图 / 时序 / 资源 / 输入事实。

### ❌ 不要用它当

- 普通 DOM/CSS 页面克隆、静态截图、整站复制。
- 与渲染面无关的 JS 反混淆、产品 UI 重设计。
- **只想要好看的动效**——那是生成需求，不是抠取需求（用 huashu-design / viz-deck 的 motion 模式）。

---

## 02 · 触发词

> 「把这个网页的着色器效果抠出来 / 复现这个 WebGL 背景 / 这个 canvas 动画怎么做的 / 本地 replay 这个 shader / 移植这个动态背景 / extract this WebGL effect / reproduce this shader / port this canvas animation」

带 **URL** + **shader/canvas 目标** 时触发；纯 DOM/CSS 不触发。

---

## 03 · 工作流（Recon Kernel 状态机）

```text
INTAKE → CAPABILITY_SNAPSHOT → QUICK_SCOUT → SURFACE_ATTRIBUTION
  → TARGET_LOCK_GATE → TRACE_ROUTE_SELECT → SOURCE_TRACE
  → CAPTURE_MINIMUM_TRUTH → REPLAY_READY_GATE → RAW_REPLAY
  → BASELINE_RUN → BASELINE_VERIFY → PROJECTIZE → PROJECT_VERIFY → PACKAGE
```

六条铁律（来自 `SKILL.md` Core Rules）：

1. **目标绑定优先于框架绑定** — 全局检测到 Three.js 只是假设，必须绑定到目标渲染面才成立。
2. **证据优先于实现** — 源码/运行时对象/帧捕获/source map 胜过肉眼凑。
3. **基线优先于工程化** — 永不为「清理/简化」覆盖已验证基线。
4. **诚实标签** — 关键事实标 `SOURCE` / `PARTIAL` / `GUESS`，未标默认当 `GUESS`。
5. **不做补偿调参** — 不靠改亮度/时间/颜色/噪声掩盖管线缺口。
6. **Gate 工件是状态守卫** — 缺关键证据 = 状态没推进。

---

## 04 · 文件结构

```
web-shader-extractor/
├── SKILL.md                       # 路由索引（不是完整手册）
├── references/                    # 13 篇按状态加载的参考
│   ├── operating-contract.md      # 标签/事实/完成态总契约
│   ├── recon-kernel.md            # 协议/自治/状态流
│   ├── surface-discovery.md       # 视觉归因
│   ├── target-lock.md             # 锁定标准 + Three.js 绑定
│   ├── evidence-policy.md         # 证据标签/账本/未知分类
│   ├── tool-capability-matrix.md  # 工具能力选择
│   ├── capture-backends.md        # WebGL/WebGPU/Canvas2D 捕获
│   ├── source-analysis.md         # source map/bundle 切片
│   ├── replay-policy.md           # 复现就绪/路线/基线/栈选择
│   ├── qa-failure-policy.md       # QA/失败路由/严重度
│   ├── three-shader-reconstruction.md  # Three.js 注入 / TSL 重建
│   ├── unicorn-studio.md          # Unicorn Studio 平台适配
│   └── shaders-com.md             # shaders.com / TSL 适配
├── scripts/
│   ├── fetch-rendered-dom.mjs     # 可选：Playwright 已就绪时的清单助手
│   └── scan-bundle.sh             # 可选：目标绑定的 bundle 切片扫描
└── templates/                     # 当 schema 用，不是自由笔记
    ├── scout-card.json
    ├── replay-manifest.json       # schemaVersion 3：source/runtime/renderGraph/...
    ├── run-state.json
    ├── qa-report.md
    ├── known-gaps.md
    └── extraction-report.md
```

---

## 05 · 能力清单（Capability Profile）

skill 进入任务前先记录可用能力档案：

```text
navigate, runtime-eval, preload-script, network-metadata, network-body,
source-map, canvas-screenshot, interaction, frame-capture-webgl,
frame-capture-webgpu, local-run, multi-frame-compare
```

工具是「可替换能力」不是「前置依赖」。`scripts/` 里的两个脚本只是**假设证据助手**，
单独不能满足 Surface Attribution / Target Lock / Replay Ready / QA 任何一个 gate。

---

## 06 · Demo（自包含样例复现）

仓库里附了 3 个**自包含 demo HTML**，双击即可看，演示「该 skill 抠取/复现出来的产物长什么样」——
每个 demo 顶部嵌了一个 `extraction-report` 风格的 manifest 面板（source / backend / replay route / fidelity tier / truth 标签），
对齐 `templates/replay-manifest.json` 与 `templates/extraction-report.md` 的真实 schema：

| Demo | 覆盖 backend | 内容 |
|---|---|---|
| `demo-webgl-fragment.html` | WebGL 片元 shader | 流动渐变/噪声场动态背景（最典型的 shader 动效） |
| `demo-canvas2d-flow.html` | Canvas2D | 粒子流场（鸣谢 @HeyHuazi 的 2D Canvas 抠取路线） |
| `demo-three-reconstruct.html` | Three.js shader 重建 | TSL/onBeforeCompile 风格的着色器重建 |
| `demo-logo-fold-generative.html` | Three.js 自定义 ShaderMaterial | **生灭折叠用例**：项目 logo 矢量化(`logo-vector.svg`, vtracer) → 网格折翼，每块走「生成→生长→收缩→消失」生命周期 3D 折叠，中心对称自转 + 3 层无限递归 |

> 前 3 个 demo 是**生成的样例**，说明抠取产物形态；第 4 个是一个**完整生成用例**——
> 把项目 logo 矢量化后做成离散折翼的生灭折叠 3D 动效（自包含，矢量源以 data URI 内联）。
> 真正的抠取要给定 URL 走 Recon Kernel 状态机。

---

## 07 · 安装

```bash
# 项目级：放进项目根 .claude/skills/
cp -r claude-code-skills/web-shader-extractor .claude/skills/

# 或全局：
cp -r claude-code-skills/web-shader-extractor ~/.claude/skills/

# 验证
claude /skills    # 列表应出现 web-shader-extractor
```

**可选依赖**（仅高阶捕获/脚本助手需要）：

- Playwright（`fetch-rendered-dom.mjs` 用）：`npm i -D playwright && npx playwright install chromium`
- 完整帧捕获需要支持 `frame-capture-webgl/webgpu` 的浏览器调试能力。

无依赖也能用——skill 会按 `tool-capability-matrix.md` 在能力缺失时降级路由。

---

## 08 · 边界与许可

- **MIT License**，原样移植自 [lixiaolin94/skills](https://github.com/lixiaolin94/skills)，详见 `NOTICE.md`。
- 抠取他人网页内容时请遵守目标站点的版权与使用条款；本 skill 内置 `permissionBoundary`（public / user-authorized / external-blocked）字段提示权限边界。
- 与本仓库其它 skill 的分工：**抠取/复现** 用本 skill；**生成漂亮动效/视频** 用 huashu-design / viz-deck motion 模式。
