# USAGE · Hermes × viz-channel 实战案例库

> 在 IM 频道(下文以**飞书**为例)@机器人 说一句话,Hermes**问清 → 生成 → 发回当前会话**。
> 每个案例都给齐:**你说的话 · 机器人对话 · 后台执行 · 你收到什么 · 酷炫点**。
> 生成靠 `viz-deck` / `viz-charts`,送达靠 `viz-channel`。默认产出**动效 HTML**。
> **Hermes 独有**:同一条链路还能做成 **cron / webhook 自动化**(见末尾案例 10–11)。

图例:🧑 你 ｜ 🤖 机器人 ｜ `$` 后台执行 ｜ 📦 你收到的东西

> 🎨 **默认视觉风格 = ZimaBlue Editorial(暖纸编辑风)**:暖白纸底 + 深青主色 + 金/赭点缀 +
> 发丝卡片 + 顶部三色条 + 大号粗体数字,专业简洁、出片即用(下面所有案例都是这个风格)。
> 要换风格直接说一句"用深空风"或"用品牌色 #xxxxxx"。详见
> `skills/viz-channel/references/default-style.md`。

---

## 0 · 30 秒快速上手

```
🧑 @hermes 做一份云度科技 Q2 业绩的动效汇报,做完发我
🤖 收到 ✦ 我来做一份「云度科技 Q2 业绩」的动效 HTML 报告。两点确认:
   1）有要用的数据吗?没有我先用占位结构,你看了再补。
   2）默认动效 HTML(下载用浏览器看);要能在 PPT 改 / 群里直接播,说一声。
🧑 营收 3.2 亿(+38%)、毛利率 61%、新增客户 240、NRR 128%
🤖 好,动效 HTML,深空风,稍等 ~40s。
```
```
$ # viz-deck 模式1:数字滚动 + ECharts 柱/折线 + 深空青金配色 → output/2026-05-29-yundu-q2-deck.html
$ bash scripts/channel_send.sh \
    --file output/2026-05-29-yundu-q2-deck.html --to-current \
    --note "云度 Q2 动效报告已生成 ✦ 下载后用浏览器打开即可看到完整动效与图表"
```
```
🤖 已发 ✦「云度科技 Q2 业绩」动效报告。下载用浏览器打开,KPI 滚动、图表生长。
📦 飞书文件消息:2026-05-29-yundu-q2-deck.html(约 180KB)
```

---

## 案例库(频道对话触发)

### 案例 1 · 季度业绩动效汇报(给老板看)
- 🧑「做个 Q2 业绩动效报告发我」→ **动效 HTML**(viz-deck 模式1)。
- KPI 数字滚动、柱/折线图依次生长、深空青金高管风、滚动叙事。
- ✦ 零桥接依赖,最快;数字 count-up + 图表 draw-in。

### 案例 2 · 一句话出董事会**可编辑** PPT
- 🧑「做个能在 PPT 里改的董事会汇报」→ viz-deck 模式5(ppt-master,需 `--with-bridges`)。
- `$ bash scripts/channel_send.sh --file out/board_pptx_build/exports/board.pptx --to-current --note "可编辑 PPT,PowerPoint 里直接改"`
- 📦 `*.pptx`,形状可点、母版统一、真 DrawingML。
- ✦ 不是图片塞 PPT,是真可编辑。

### 案例 3 · 产品生态 **3D 知识图谱**(酷炫担当)
- 🧑「把产品 + 伙伴 + 客户关系画成 3D 知识图谱」→ viz-charts 3D KG(WebGL,可旋转/缩放/点击)。
- `$ bash scripts/channel_send.sh --file output/yundu-ecosystem-3dkg.html --to-current --note "3D 知识图谱,浏览器打开可拖动旋转"`
- 📦 `*-3dkg.html`,拖动旋转、滚轮缩放、点节点高亮。
- ✦ 三维力导向 + 发光节点 + 关系连线动画,汇报现场最抓眼。

### 案例 4 · 发布会 Hero 动画(**发群直接播**)
- 🧑「做个新品发布开场动画,发产品群」→ viz-deck 模式4 → **MP4**(需 `--with-bridges` + ffmpeg)。
- `$ bash scripts/channel_send.sh --file output/launch-hero.mp4 --to oc_xxx --to-type chat_id`
- 📦 飞书**视频消息**,点开就播。
- ✦ 60fps 插帧 + 场景化 BGM,运动叙事一镜到底。

### 案例 5 · 竞品格局一图流(**实时联网调研**)
- 🧑「做个国内 RPA 赛道竞品格局分析」→ viz-deck + research-playbook(联网查)。
- 📦 `*-landscape-deck.html`:竞品四象限 + 能力雷达 + 融资时间线。
- ✦ 先调研再可视化,数据有出处。

### 案例 6 · 数据贴群:30 秒一张专业图
- 🧑「把这组月度留存画成折线图发群」→ viz-charts 单图,贴群出 **PNG**。
- `$ bash scripts/channel_send.sh --file output/retention.png --to oc_xxx --to-type chat_id`
- 📦 图片消息,群成员秒看。
- ✦ 专业配色 + 数据标注,比 Excel 截图高级一档。最高频实用。

### 案例 7 · 技术架构 deep-dive
- 🧑「给架构评审做微服务拆分方案技术汇报」→ viz-deck 技术模板(action-title + 架构图 + 取舍表)。
- 📦 `*-arch-deck.html`,每页标题即结论。
- ✦ bento-grid 架构分区 + 引用脚注。

### 案例 8 · 群里多人改稿(多轮迭代)
```
🧑 @hermes 上面那份报告第 3 页柱状图换饼图,再加一页"风险与对策"
🤖 好,改第 3 页 + 增"风险与对策"页,重做后发本会话。
$ bash scripts/channel_send.sh --file output/2026-05-29-yundu-q2-deck.html --to-current \
    --note "已更新:第3页改饼图、新增风险与对策页"
```
- ✦ Hermes session 记住本会话主题/形态/风格,不重新问。

### 案例 9 · 自定义品牌风格
- 🧑「用品牌色 #0E7C66 和思源黑体做个 ESG 报告动效页」→ viz-deck + 设计令牌,可先给 3 个方向选。
- ✦ 20 种设计哲学(Pentagram / Kenya Hara / Field.io…)挑方向,自定义风格不千篇一律。

---

## 🤖 案例 10–11 · Hermes 自动化(无人值守)

Hermes 有 cron/webhook routine。把"生成 + 投递"编排成自动任务,**不需要对话问需求**——
主题/形态/接收方在 routine 配置里写死,接收方用固定 `chat_id`(不要用 `--to-current`,无交互上下文)。

### 案例 10 · 每周一早 9 点自动出上周周报,发运营群(cron)
```
触发: cron "0 9 * * 1"
步骤:
  1. (按固定数据源/模板) viz-deck 模式1 → output/weekly-deck.html
  2. bash scripts/channel_send.sh \
       --file output/weekly-deck.html \
       --to oc_<运营群chat_id> --to-type chat_id \
       --note "上周业绩动效周报 ✦ 下载用浏览器打开"
```
- ✦ 周一上班群里已躺着一份动效周报,零人工。

### 案例 11 · 线上事件触发自动出图发群(webhook)
```
触发: webhook POST /routines/deck-on-event   payload: { topic, data, chat_id }
步骤:
  1. viz-charts 按 payload.data 出图 → output/event-chart.html
  2. bash scripts/channel_send.sh --file output/event-chart.html \
       --to <payload.chat_id> --to-type chat_id --note "..."
```
- ✦ 监控告警 / 成交播报 / 数据更新 → 自动出可视化推群。
- 配置细节见 `skills/viz-channel/references/hermes-channel.md` 第 5 节。

---

### 案例 12 · 公众号文章排版(gzh-channel,先确认再排)
- 🧑(发来一篇长文或 .docx)「排成公众号发我」
- 机器人:整理成 Markdown 结构稿 → 发一张 **interactive 卡片**(标题/章节/字数摘要 +
  Markdown 全文代码块,长稿则附 `.md` 文件)→ 你回「确认」或说改哪里
- 🧑「确认」→ 问一句主题(默认推荐摸鱼绿,可换红白/石墨极简/留白禅意/摸鱼票据/橄榄手记)
- 📦 两个文件:`*_预览.html`(浏览器打开 → 点右上角「**一键复制**」→ 编辑器粘贴,
  样式不丢)+ 干净正文 HTML(兜底)。
- ✦ 关键点:**排版前必过草稿确认卡片**;排版由 `gzh-design` 完成(样式全内联 +
  `<span leaf>` 包裹 + 校验 ERROR×0),粘贴到公众号编辑器不掉格式。

---

## 进阶用法

- **群聊**:必须 @机器人;成品发回本群(`oc_` chat_id)。敏感内容机器人先问"群发还是私发"。
- **形态切换**(同主题复用):说"要能改"→PPTX;"群里播"→MP4;"只要那张图"→单图。
- **一次多形态**:「给我动效 HTML 看,再出个可编辑 PPT 给客户」→ 两条消息分别发。

## 触发词速查

| 你想要 | 这样说 | 出什么 |
|--------|--------|--------|
| 动效报告 | 做个 X 的汇报 / 动效报告 / 可视化 / deck 发我 | 动效 HTML |
| 可编辑 PPT | 做个能改的 X PPT | PPTX |
| 群里能播 | 做个 X 动画发群里 | MP4 |
| 一张图 | 把数据画成柱/折线/饼图发群 | 图表(PNG/HTML) |
| 3D 图谱 | 画个 X 的 3D 知识图谱 | 3D KG(HTML) |
| 公众号排版 | (发来文章)排成公众号 / 公众号排版 / 微信排版 | 草稿卡片确认 → 预览 HTML(一键复制) |
| 改稿 | 第 N 页换成… / 加一页… | 同主题重生成再发 |

## 排错速查

| 现象 | 多半原因 | 怎么办 |
|------|---------|--------|
| 文本能回,文件发不出 | chat_id 没拿到 / 缺 `im:resource` | `python3 scripts/resolve_chat.py` 自检;补权限 |
| 报 91402 | app 缺 `im:resource` | 飞书开发者后台补权限重发版 |
| HTML 看不到动效 | 在飞书里直接点开 | **下载用浏览器打开** |
| "huashu/ppt-master not installed" | 没装桥接 | `install-hermes-skills.sh --with-bridges` |
| 文件 > 30MB | 超飞书上限 | 压缩 / 降码率 / 转链接 |
| 群里不理 / gateway 掉线 | 没 @ / 连接断 | @机器人;`hermes doctor` |

对话编排见 `skills/viz-channel/references/channel-protocol.md`,形态决策见 `delivery-matrix.md`,
Hermes 平台细节 + 自动化见 `hermes-channel.md`。
