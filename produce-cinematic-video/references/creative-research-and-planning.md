# 同题研究与创作策划

## 目录

- [研究契约](#研究契约)
- [OmniGet 采集与入库](#omniget-采集与入库)
- [样本设计](#样本设计)
- [拆解方法](#拆解方法)
- [原创策划](#原创策划)
- [交付物](#交付物)

## 研究契约

先确定主题、受众、平台、地区、时段、片长、内容形式、业务目标和不可触碰边界。研究的用途是学习可解释的创作机制，不是下载、重剪或模仿受保护素材。

只使用用户提供、公开可访问且允许研究的页面或平台接口。每条样本记录 URL、标题、作者/频道、发布日期、访问日期、片长、平台、可见指标、权利备注和数据缺口。平台数据和政策易变，正式使用前重新核对官方来源。

## OmniGet 采集与入库

当用户需要在 Windows、macOS 或 Linux 上收集同主题公开样本时，可把 [OmniGet](https://github.com/tonhowtf/omniget) 作为可选的桌面采集、整理与学习工具。它能管理 yt-dlp/FFmpeg 下载、字幕、Whisper、片段、时间戳笔记和本地播放，但当前官方形态是桌面应用，没有供本 skill 承诺的稳定外部 CLI/API。因此：

- 用户在 OmniGet 中完成 URL 预览、账号登录和有权访问内容的导出；
- 不自动读取 clipboard、cookies、浏览器登录态、OmniGet 数据库或私有课程；
- 不绕过 DRM、付费墙、地区限制、登录限制或平台条款；
- 只把用户明确选定的导出目录交给 PCV 做只读理解；
- OmniGet 或 yt-dlp “技术上能下载”不代表拥有改编、再发布或训练权。

将选中的视频、音频、字幕、缩略图与 `.info.json` 放在一个项目研究目录，然后先预览：

```text
python <skill-dir>/scripts/research_ingest.py --input-dir <authorized-export> --output research/source-manifest.json --collection-title "<topic>" --rights-basis research-only --dry-run
```

确认后去掉 `--dry-run`。脚本不下载、不移动、不改写源文件；它生成 checksum、FFprobe 技术信息，配对字幕/元数据，只保留 canonical page URL，拒绝带 token/signature 的 URL，并把权利基础标为用户声明且仍需核验。若同一目录中的素材权利不同，用 `--source-map` JSON 按相对路径覆盖 `source_url`、`rights_basis`、`rights_note`。

入库后按需运行：

1. `media_inventory.py`：编码、时长、声道、画幅和文件健康；
2. `shot_detect.py`：镜头结构与节奏分布；
3. `contact_sheet.py`：视觉构图、角色、字幕与色彩；
4. 转写/字幕：论点、叙事 beat、钩子和声音结构；
5. `moment_ground.py`：只对已获准的本地媒体定位关键语义事件；
6. reference card：把可见事实、推断和可迁移机制分开。

研究材料进入项目 `research/`，不进入成片 `assets/source/`。真正引用、截取或改编前再做逐条权利审批；`research-only` 永远不自动升级为可复用素材。

## 样本设计

至少区分：

- 3–5 个主题/受众高度相近的高表现样本；
- 3–5 个同期、同平台的普通或低表现对照；
- 1–3 个跨品类但机制可借鉴的远邻样本；
- 用户自己的历史内容，若可获得且口径一致。

不要只研究“爆款”。播放量会被账号体量、投放、发布时间、分发和幸存者偏差影响。没有可比对照时，输出创作假设，不输出因果结论。

## 拆解方法

为每条样本写 reference card：

1. 首帧对象与第一句承诺；
2. 冲突、问题或好奇缺口出现时间；
3. 首次 payoff 和主 payoff；
4. beat 顺序、信息密度、情绪曲线和留白；
5. 镜头长度分布、运动、景别、字幕和视觉证据；
6. 人声/音乐/音效/静默的结构；
7. 标题、封面、CTA 和评论触发；
8. 负面反馈、误解、跳出点和信任风险；
9. 可迁移机制与不可复制的表面元素；
10. 证据强度与置信度。

用 `assets/creative-research.template.json` 保存。观察和推断分开写；找不到的数据填 `null`，不要编造。

## 原创策划

从样本中提取“机制”，再重新组合为原创方案：

- 受众张力：观众当前状态 → 想得到的变化；
- 创作命题：理解、感受、相信、行动；
- 独特视角：人物、事实、世界观、过程或形式上的不可替代性；
- 叙事发动机：问题、任务、关系、证据或变化；
- 声画钩子：首帧、首句、首个声音事件；
- payoff 设计：何时、以什么证据兑现；
- 情绪弧：建立、蓄力、转折、释放、余韵；
- 平台包装：标题、封面、字幕、CTA，但不改变事实；
- 风险：权利、隐私、未成年人、品牌、误导和合成披露。

至少给出三种方向，但最终必须选择一个主方向。每个方向说明适用受众、核心机制、成本、风险和放弃原因。避免把多个互相冲突的方向硬拼成一个方案。

## 交付物

策划阶段应产生：

- `research/reference-cards.json`：样本与证据；
- `planning/creative-brief.md`：受众、命题、承诺、证明、payoff、行动；
- `planning/originality-map.md`：借鉴机制、原创变化、禁用元素；
- `planning/beat-sheet.csv`：时间、信息、情绪、声音和镜头职责；
- `planning/script.md`：剧本/旁白/采访问题/事实引用；
- `planning/experiment-plan.json`：标题、封面、开场或 CTA 的单变量 A/B 假设；
- `planning/approval.json`：用户选择、预算与风险确认。

研究未完成不妨碍草拟方案，但必须标记证据空缺。付费生成、私有媒体上传或对外发布仍需独立批准。
