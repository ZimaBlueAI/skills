# design-philosophies: 20 设计哲学 × viz-deck 场景适配

> v2 新增。本文件不重复哲学定义——20 个流派的提示词 DNA / 代表作 / 哲学内核**全部在** `~/.claude/skills/huashu-design/references/design-styles.md`。本文件做的是**适配工作**：把 huashu 的 20 哲学映射到 viz-deck 的 4 个产出模式（keynote-report / prototype / slide-deck / motion-stage）。

## 5 流派 × 20 风格速查

| 流派 | 风格编号 | 风格名 |
|---|---|---|
| 信息建筑派 | 01-04 | Pentagram / Stamen / Information Architects / Fathom |
| 运动诗学派 | 05-08 | Locomotive / Active Theory / Field.io / Resn |
| 极简主义派 | 09-12 | Experimental Jetset / Müller-Brockmann / Build / Sagmeister & Walsh |
| 实验先锋派 | 13-16 | Zach Lieberman / Raven Kwok / Ash Thorp / Territory Studio |
| 东方哲学派 | 17-20 | Takram / Kenya Hara / Irma Boom / Neo Shen |

完整描述、提示词 DNA、代表作、搜索关键词——见 huashu 文件，**不要在 viz-deck 里复述**。

## viz-deck 模式 × 风格推荐表

每个产出模式适合的哲学不同，避免"哲学不合体"。

### keynote-report（默认讲演级报告）

| 哲学 | 适配度 | 适用场景 |
|---|:---:|---|
| 04 Fathom | ★★★ | 投资人简报、研究型路演（数据密度大） |
| 10 Müller-Brockmann | ★★★ | 严肃技术评审、政府/学术汇报 |
| 11 Build | ★★★ | 高端品牌发布、奢侈品级路演 |
| 17 Takram | ★★★ | 设计驱动的创新提案、研究型公司 |
| 18 Kenya Hara | ★★☆ | 日系审美客户、东方市场 |
| 05 Locomotive | ★★☆ | 创意机构 / 科技品牌阶段汇报（有视差需求） |
| 06 Active Theory | ★☆☆ | 仅当主视觉是 3D KG 时（避免炫技） |

**默认基线 = viz-deck 原本的"深空蓝紫青"** ≈ 介于 06 Active Theory 与 17 Takram 之间。如果不指定，沿用默认。

### prototype（HTML 高保真原型）

| 哲学 | 适配度 | 适用场景 |
|---|:---:|---|
| 03 Information Architects | ★★★ | 内容型应用（资讯/写作/阅读） |
| 17 Takram | ★★★ | 概念原型、未来产品 demo |
| 11 Build | ★★★ | B2B SaaS、企业 dashboard |
| 18 Kenya Hara | ★★★ | 极简消费品（电商、内容订阅） |
| 16 Territory Studio | ★★☆ | 科幻题材、游戏内 UI、HUD 原型 |
| 02 Stamen | ★★☆ | 地图 / 数据可视化型应用 |

### slide-deck（演讲幻灯片）

| 哲学 | 适配度 | 适用场景 |
|---|:---:|---|
| 01 Pentagram | ★★★ | 严肃学术 / 政府 / 标准发布 |
| 04 Fathom | ★★★ | 数据汇报、研究分享 |
| 10 Müller-Brockmann | ★★★ | 设计课件、版式标准课 |
| 11 Build | ★★★ | 品牌发布、产品上市 keynote |
| 12 Sagmeister & Walsh | ★★☆ | 创意行业分享、TED 风格 |
| 17 Takram | ★★★ | 设计驱动 keynote |
| 18 Kenya Hara | ★★★ | 日系发布会、东方品牌 |

### motion-stage（动画 + MP4 导出）

| 哲学 | 适配度 | 适用场景 |
|---|:---:|---|
| 05 Locomotive | ★★★ | 滚动叙事视频、产品 hero |
| 06 Active Theory | ★★★ | 3D / WebGL 录屏（粒子流） |
| 07 Field.io | ★★★ | 生成艺术 / 算法动画 |
| 13 Zach Lieberman | ★★☆ | 代码诗学的实时生成动画 |
| 15 Ash Thorp | ★★☆ | 概念视频、电影级镜头 |
| 16 Territory Studio | ★★★ | FUI / 虚构 UI 录屏 |
| 20 Neo Shen | ★★☆ | 水墨/光晕氛围视频 |

## 风格选择流程（设计方向顾问模式）

需求模糊时，触发**设计方向顾问**模式（参考 huashu 的 fallback 协议）：

1. **询问**（向用户）：
   - 受众是谁？（投资人 / 客户 / 全员 / 学术）
   - 行业/品牌已有视觉？（uploads 一张参考图 或 一个 brand URL）
   - 偏好情绪？（严肃克制 / 高级安静 / 创意张扬 / 未来科幻 / 东方诗意）

2. **从 5 流派×20 哲学里选 3 个**（要差异化，不能同流派 3 选）：
   - 推荐 1 个"安全选择"（默认基线 或 最适配流派的 TOP 1）
   - 推荐 1 个"对照选择"（不同流派，制造差异）
   - 推荐 1 个"野卡选择"（实验先锋派 或 东方哲学派）

3. **每个推荐输出**：
   - 风格名 + 流派
   - 一句话哲学
   - 提示词 DNA（引用 huashu 的，**不复制内容**，链接到 huashu 文件的对应章节）
   - 一句话："为什么适合本项目"

4. **并行生成 3 个视觉 demo**：每个风格出一份缩略 HTML（占位数据即可），让用户选

5. 用户选完，进入主流程

## 与原 viz-deck 视觉基线的关系

原 viz-deck 的"深空 #030711 + 青 #42e8ff + 金 #ffd987 + Inter"是**默认风格**，对应**6 Active Theory 的简化版**。

启用 v2 后：

- 用户未指定 → 沿用原默认（视觉无变化，向后兼容）
- 用户指定哲学编号（如 "用 18 风格" / "Kenya Hara 风" / "Pentagram 那种"）→ 加载对应 CSS 变量覆盖
- 用户上传参考图 / 提供 brand URL → 触发顾问模式，从 20 选 3 推荐

## 不要做的事

- ❌ 在 viz-deck 文件里完整复述 20 哲学的细节——引用 huashu 即可
- ❌ 同一份 deck 混合 2 个流派（破坏哲学一致性，5 维评审第 1 项必扣分）
- ❌ 用 "in the style of Pentagram" 这种短语——必须用具体设计特征描述
- ❌ 推荐时给出 3 个同流派选择——失去对照价值

## 与 5 维评审的联动

每次完成 deck 后，调用 `references/critique-5dim.md` 给出 5 维评分，其中**第 1 项哲学一致性**就是检验"你是否真的按所选哲学执行"。打分 < 7 = 需要修复。

## v2.1 · Show-Don't-Tell 三变体预览

> 灵感来自 frontend-slides（17.5k Star）的 "show, don't tell" — 用户口头描述风格通常说不清，看到 3 张缩略图却能一眼分辨。

### 何时触发

| 用户输入特征 | 触发预览 |
|---|:---:|
| 完全没说视觉风格（"做个 keynote"） | ✅ 跑 shotgun |
| 风格描述含混（"高级一点"、"专业一点"、"好看点"） | ✅ 跑 shotgun |
| 明确指定哲学（"用 Kenya Hara 风" / "用 18"）| ❌ 直接用 |
| 上传参考图 / brand URL | ❌ 进顾问模式（仍可生成 3 变体但优先匹配参考） |

### 默认对照三联（contrast triples）

按场景选不同三联，**强制跨流派**：

| 场景关键词 | 安全选 | 对照选 | 野卡选 |
|---|---|---|---|
| 投资人 / 路演 / 严肃发布 | **01 Pentagram**（信息建筑） | **11 Build**（极简） | **17 Takram**（东方实验） |
| 产品发布 / 品牌 / 创意机构 | **04 Fathom**（信息建筑·数据型） | **12 Sagmeister**（实验先锋） | **18 Kenya Hara**（东方极简） |
| 技术深研 / 工程师演讲 | **10 Müller-Brockmann**（瑞士网格） | **07 Field.io**（运动诗学·算法） | **16 Territory**（实验·FUI） |
| 学术 / 政府 / 研究 | **01 Pentagram** | **03 Information Architects** | **18 Kenya Hara** |
| 默认（无关键词） | **viz-deck baseline**（深空青金） | **18 Kenya Hara**（东方极简） | **07 Field.io**（算法运动） |

### Shotgun 工作流

跑 `scripts/preview-shotgun.mjs`：

```bash
node ~/.claude/skills/viz-deck/scripts/preview-shotgun.mjs \
  --topic "AI Agent 全景报告" \
  --scene "投资人路演" \
  --output ./previews/
# 产出：./previews/preview-board.html（3 张 hero 缩略图横向并列 + Pick 按钮）
```

输出的 `preview-board.html` 让用户点击 "Pick this direction" → 把所选哲学编号写入下一步的 deck 生成参数。

**不要并行生成完整 deck**——只生成 hero 缩略图（1 页封面 + 1 页章节内页），节省 token，专注于视觉决策。
