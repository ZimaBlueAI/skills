# USAGE · OpenClaw × viz-channel 实战案例库

> 在 IM 频道(下文以**飞书**为例)@机器人 说一句话,机器人**问清 → 生成 → 发回当前会话**。
> 下面每个案例都给齐:**你说的话 · 机器人对话 · 它在后台跑什么 · 你在飞书收到什么 · 酷炫点**。
> 生成靠 `viz-deck` / `viz-charts`,送达靠 `viz-channel`。默认产出**动效 HTML**。

图例:🧑 你 ｜ 🤖 机器人 ｜ `$` 机器人后台执行 ｜ 📦 你收到的东西

> 🎨 **默认视觉风格 = ZimaBlue Editorial(暖纸编辑风)**:暖白纸底 + 深青主色 + 金/赭点缀 +
> 发丝卡片 + 顶部三色条 + 大号粗体数字,专业简洁、出片即用(下面所有案例都是这个风格)。
> 要换风格直接说一句"用深空风"或"用品牌色 #xxxxxx"。详见
> `skills/viz-channel/references/default-style.md`。

---

## 0 · 30 秒快速上手

```
🧑 @小龙虾 做一份云度科技 Q2 业绩的动效汇报,做完发我
🤖 收到 ✦ 我来做一份「云度科技 Q2 业绩」的动效 HTML 报告。两点确认:
   1）有要用的数据吗?没有我先用占位结构,你看了再补。
   2）默认出动效 HTML(下载用浏览器看);要能在 PPT 里改 / 群里直接播,说一声。
🧑 用这些数:营收 3.2 亿(+38%)、毛利率 61%、新增客户 240、NRR 128%
🤖 好,按动效 HTML,深空风,稍等 ~40s。
```
机器人后台:
```
$ # viz-deck 模式1 keynote-report,数字滚动 + ECharts 柱/折线,深空青金配色
$ #   → 生成 output/2026-05-29-yundu-q2-deck.html
$ bash scripts/channel_send.sh \
    --file output/2026-05-29-yundu-q2-deck.html --to-current \
    --note "云度 Q2 动效报告已生成 ✦ 下载后用浏览器打开即可看到完整动效与图表"
```
```
🤖 已发 ✦「云度科技 Q2 业绩」动效报告(deck.html)。下载用浏览器打开,
   KPI 会滚动、图表会生长。要可编辑 PPT 或加页直接说。
📦 飞书文件消息:2026-05-29-yundu-q2-deck.html(约 180KB)
```

---

## 案例库

### 案例 1 · 季度业绩动效汇报(给老板看)
- 🧑「做个 Q2 业绩动效报告发我」
- 形态:**动效 HTML**(viz-deck 模式1)。KPI 数字滚动入场、柱状/折线图依次生长、
  深空青金高管风、滚动叙事。
- 📦 `*-deck.html`,下载浏览器开,动效全在。
- ✦ 酷炫点:数字 count-up、图表 draw-in、章节视差。**零桥接依赖,最快**。

### 案例 2 · 一句话出董事会**可编辑** PPT
- 🧑「做个能在 PPT 里改的董事会汇报」→ 触发可编辑 PPTX。
- `$ bash scripts/channel_send.sh --file out/board_pptx_build/exports/board.pptx --to-current --note "可编辑 PPT,PowerPoint 里直接改"`
- 形态:viz-deck 模式5 pptx-deck(经 ppt-master,需 `--with-bridges`)。
  真 DrawingML、形状可点、母版统一、可加动画。
- 📦 `*.pptx`,PowerPoint 打开逐个形状可编辑。
- ✦ 酷炫点:不是"图片塞进 PPT",是**真可编辑**。验证 `unzip -p x.pptx ppt/slides/slide1.xml | grep -c '<p:sp>'` > 1。

### 案例 3 · 产品生态 **3D 知识图谱**(酷炫担当)
- 🧑「把我们产品 + 合作伙伴 + 客户的关系画成 3D 知识图谱发我」
- 形态:viz-charts 3D KG(WebGL,可旋转/缩放/点击节点高亮)。**必发 HTML**(PNG 丢交互)。
- `$ bash scripts/channel_send.sh --file output/yundu-ecosystem-3dkg.html --to-current --note "3D 知识图谱,下载用浏览器打开,可拖动旋转"`
- 📦 `*-3dkg.html`,浏览器里拖动旋转、滚轮缩放、点节点看关系。
- ✦ 酷炫点:三维力导向布局 + 发光节点 + 关系连线动画。汇报现场最抓眼。

### 案例 4 · 发布会 Hero 动画(**发群直接播**)
- 🧑「做个新品发布的开场动画,发产品群,群里能直接看」
- 形态:viz-deck 模式4 motion-stage → 导出 **MP4**(需 `--with-bridges` + ffmpeg)。
  1920×1080、≤8s、自带场景化 BGM + 自动 fade。
- `$ bash scripts/channel_send.sh --file output/launch-hero.mp4 --to-current`
- 📦 飞书**视频消息**,点开就播,无需下载、无需提醒。
- ✦ 酷炫点:60fps 插帧、运动叙事一镜到底(非 PPT 翻页)。

### 案例 5 · 竞品格局一图流(**实时联网调研**)
- 🧑「做个国内 RPA 赛道的竞品格局分析,发我」
- 形态:viz-deck keynote-report + research-playbook(联网查竞品)→ 象限图/对比矩阵/时间线。
- 📦 `*-landscape-deck.html`,含竞品定位四象限 + 能力雷达 + 融资时间线。
- ✦ 酷炫点:**先联网调研再可视化**,数据有出处;象限图节点动效。

### 案例 6 · 数据贴群:30 秒出一张专业图
- 🧑「把这组月度留存画成折线图,发群里」+ 贴一段数据
- 形态:viz-charts 单图。要贴群直接看 → 出 **PNG**(图片消息,群里显缩略图);
  要可交互 → 出 HTML。
- `$ bash scripts/channel_send.sh --file output/retention.png --to oc_xxx --to-type chat_id`
- 📦 图片消息,群成员秒看。
- ✦ 酷炫点:专业配色 + 数据标注 + 趋势高亮,比 Excel 截图高级一个量级。**最高频实用**。

### 案例 7 · 技术架构 deep-dive(技术评审)
- 🧑「给架构评审做一份微服务拆分方案的技术汇报」
- 形态:viz-deck 学术/技术模板(action-title 句式 + 架构图 + 取舍表 + 时序),信息密度高。
- 📦 `*-arch-deck.html`,每页标题即结论,适合工程评审。
- ✦ 酷炫点:action-titles + 引用脚注 + bento-grid 架构分区。

### 案例 8 · 群里多人改稿(多轮迭代)
```
🧑 @小龙虾 上面那份报告,第 3 页的柱状图换成饼图,再加一页"风险与对策"
🤖 好,改第 3 页为饼图 + 增"风险与对策"页,重做后发这个会话。
$ # 复用同一主题/数据/风格,只改增量,重新生成并覆盖式再发
$ bash scripts/channel_send.sh --file output/2026-05-29-yundu-q2-deck.html --to-current \
    --note "已更新:第3页改饼图、新增风险与对策页"
📦 新版 deck.html
```
- ✦ 酷炫点:**记住本会话已定的主题/形态/风格**,不重新问需求。OpenClaw session 绑定该 chat。

### 案例 9 · 自定义品牌风格
- 🧑「用我们品牌色 #0E7C66 和思源黑体,做个 ESG 报告动效页」
- 形态:viz-deck + 指定设计令牌(品牌主色/字体/留白节奏)。可让它先给 3 个差异化设计方向再选。
- 📦 带品牌识别的 `*-esg-deck.html`。
- ✦ 酷炫点:从 20 种设计哲学(Pentagram 信息建筑 / Kenya Hara 留白 / Field.io 运动诗学…)
  里挑方向,**自定义风格而非千篇一律的模板感**。

---

## 进阶用法

### 群聊里怎么收
- 群里必须 **@机器人**。成品默认发回**本群**(`oc_` 开头 chat_id),群成员都能下载。
- 敏感内容:机器人会先问"发群里还是私发给你?"。私发就发提问人 `open_id`。

### 形态随时切换(同主题复用)
```
动效 HTML ──"要能改"──▶ 可编辑 PPTX(模式5)
动效 HTML ──"群里直接播"──▶ MP4(模式4)
动效 HTML ──"只要那张图"──▶ 抽出图表单发(viz-charts)
```
直接在频道说一句,机器人复用同一数据换模式重生成、再发一次。

### 一次出多形态
- 🧑「同一份内容,给我动效 HTML 看,再出个可编辑 PPT 给客户」
- 机器人先发 HTML,再发 PPTX,两条消息,各带对应附言。

---

## 触发词速查(机器人听得懂的话)

| 你想要 | 这样说 | 出什么 |
|--------|--------|--------|
| 动效报告 | 做个 X 的汇报 / 动效报告 / 可视化 / deck 发我 | 动效 HTML |
| 可编辑 PPT | 做个能改的 X PPT / 要可编辑 PPTX | PPTX |
| 群里能播的动画 | 做个 X 动画发群里 / 能直接播的 | MP4 |
| 一张图 | 把这组数据画成柱状/折线/饼图发群 | 图表(PNG/HTML) |
| 3D 图谱 | 画个 X 的 3D 知识图谱 / 关系网络 | 3D KG(HTML) |
| 改稿 | 第 N 页换成…/ 加一页…/ 换个配色 | 同主题重生成再发 |

---

## 排错速查

| 现象 | 多半原因 | 怎么办 |
|------|---------|--------|
| 文本能回,文件发不出 | chat_id 没拿到 / 缺 `im:resource` | `python3 scripts/resolve_chat.py` 自检;补权限重发版 |
| 报 91402 / permission denied | app 缺 `im:resource` | 飞书开发者后台补权限 |
| 收到 HTML 看不到动效 | 在飞书里直接点开了 | **下载到电脑用浏览器打开** |
| 生成报 "huashu/ppt-master not installed" | 没装桥接 | `install-openclaw-skills.sh --with-bridges`(动效 HTML 不需要) |
| 文件 > 30MB 发失败 | 超飞书上限 | 压缩 / MP4 降码率 / 转云文档链接 |
| 群里机器人不理 | 没 @ / channel 掉线 | @机器人;`openclaw channels status --probe` |

更细的对话编排见 `skills/viz-channel/references/channel-protocol.md`,
形态决策见 `delivery-matrix.md`,OpenClaw 平台细节见 `openclaw-channel.md`。
