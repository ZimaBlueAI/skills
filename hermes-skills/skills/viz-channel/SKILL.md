---
name: viz-channel
description: >-
  在 IM 频道(飞书 / 企业微信 / Slack / Telegram 等)里【对话式】生成动效 HTML 报告 /
  图表 / 3D 知识图谱 / 可编辑 PPTX / MP4,并把成品作为附件发回当前会话。当用户在频道里
  @机器人 说"做个XX的PPT/汇报/可视化/动效报告/图表/知识图谱发给我/发群里",或说"帮我做份
  能改的PPT""做个能直接播的动画"时使用。这是 viz-deck / viz-charts 生成能力 + 频道投递的
  编排层:先在频道里把需求问清,再生成,再用频道适配器(当前实现:飞书/Lark,优先 lark-cli
  回退 REST)把文件发回当前 chat。触发词:做PPT、做汇报、做可视化、动效报告、做图表、
  知识图谱、3D图谱、发给我、发群里、发到飞书、做个能改的PPT、deck、slides。
license: MIT
---

# 频道对话 · 做图做PPT并发回当前会话 (channel delivery · Hermes)

> **一句话**:用户在 IM 频道里说一句需求,你(Hermes Agent)把需求问清 → 调用
> viz-deck / viz-charts 的生成能力做出动效 HTML / 图表 / 3D 知识图谱 / PPTX / MP4
> → 用 `channel_send.sh` 把成品发回**当前这个会话**。生成靠 viz 系技能,送达靠本技能。
>
> **频道适配器**:当前实现 = **飞书 / Lark**(优先复用 lark-cli 令牌,回退 REST)。
> Hermes 的 gateway 还支持 Telegram/Discord/Slack/企业微信 等——要换/加投递通道,
> 在 `scripts/channel_deliver.py` 里加对应 adapter 即可,对话与生成逻辑复用。下文以飞书为例。

本技能**不自己写 HTML/PPTX 的设计细节** —— 那是 `viz-deck` 和 `viz-charts` 的职责。
本技能负责的是**频道里的对话编排 + 形态决策 + 频道交付**这条链路。

---

## 何时触发

用户在飞书频道(单聊或群,群里需 @机器人)里说:
- "做个 X 的汇报 / PPT / deck 发我" / "做份 X 的可视化报告"
- "做个 X 的动效报告" / "做个能直接播的动画发群里"
- "做张 X 的图表" / "画个 X 的知识图谱 / 3D 图谱"
- "做个能改的 PPT" / "要可编辑的 PPTX"

→ 这就是 **频道对话 → 生成 → 交付** 三步连做。

## 依赖的生成技能(必须已安装)

| 你要做的 | 用哪个技能 | 装没装 |
|---------|-----------|-------|
| 动效 HTML 报告 / 幻灯片 / 原型 / MP4 | `viz-deck` | 必装 |
| 图表(柱/线/饼/雷达…)、3D 知识图谱 | `viz-charts` | 必装 |
| 终端风商业决策报告 | `biz-html-viz` | 可选 |

装法见同目录 `install-hermes-skills.sh` / `.ps1`。
没装就先装,别自己硬写——viz 系技能里有完整的设计系统和反 AI-slop 清单。

---

## 工作流(频道里逐步执行)

### 第 0 步 · 确认你在频道里 & 拿到当前 chat_id

频道场景的核心:成品要发回**用户正在跟你说话的这个会话**。
- Hermes 的飞书 gateway adapter 把入站消息绑定到一个 session;当前会话上下文(含 chat_id)
  通常在环境/会话元数据里。
- 自检:`python3 scripts/resolve_chat.py`(打印解析到的 chat_id)。
- 解析不到时,从这条飞书消息的事件上下文里取 `chat_id`(群是 `oc_` 开头),
  交付时用 `--to <chat_id> --to-type chat_id` 显式传。
- 平台与 chat_id 细节见 `references/hermes-channel.md`。

### 第 1 步 · 把需求问清(最多 2 个来回,别啰嗦)

频道是聊天场景,**先回一句确认 + 至多两个关键问题**,问完就动手。
默认值要给足,用户不答就用默认。要问清的:

1. **主题 / 数据**:做什么内容?有没有要用的数据/要点?(没有就用占位并说明是假设)
2. **形态**:默认**动效 HTML**(最轻、效果好、含图表与 3D 图谱)。
   只有用户说"要能改"→ 可编辑 PPTX;说"群里直接播"→ MP4。
   形态决策表见 `references/delivery-matrix.md`。
3. **风格 / 受众**(可选):给老板/客户/技术评审?
   **默认风格 = ZimaBlue Editorial(暖纸编辑风)**,专业简洁、出片即用,**不用问**。
   只有用户明确要别的(深空风 / 终端风 / 指定品牌色)才改。见 `references/default-style.md`。

> 反模式:在频道里甩一长串问卷。问清 = 一条消息内 ≤2 个问题 + 明确的默认。

### 第 2 步 · 生成(交给 viz 系技能)

> **默认风格(必读)**:频道产出的 HTML 与 PPTX **一律走 ZimaBlue Editorial 暖纸编辑风**——
> 暖白纸底(`#f7f4ee`)+ 深青主色(`#1b5e5a`)+ 金/赭点缀 + 发丝描边卡片 + 顶部 teal→gold→red
> 三色条 + 大号 tabular-nums 数字。完整令牌 / 组件 / 图表 / PPTX 主题映射见
> **`references/default-style.md`**。**把这套设计系统作为 design spec 传给 viz-deck / viz-charts**,
> 除非用户点名要别的风格,否则不偏离。(参考母版:`D1-破局与进化.html`)

按第 1 步定的形态,触发对应技能、走对应模式:

- **动效 HTML(默认)** → `viz-deck` 模式1 keynote-report,**以
  `templates/zima-editorial-deck.html` 为骨架**填内容(令牌/组件/Chart.js 默认值已就绪,最稳出片)。
  需要图表 → `viz-charts` 出图,palette 用 default-style 第 6 节(teal/gold/green/red);
  需要 3D 知识图谱 → `viz-charts` 3D KG。产物:`output/<date>-<topic>-deck.html`(单文件全内联)。
- **可编辑 PPTX** → `viz-deck` 模式5 pptx-deck(经 ppt-master,需 venv),
  **用 default-style 第 8 节的「暖纸主题」映射,不要用深空 / 终端主题**。
  产物:`*_pptx_build/exports/*.pptx`(真可编辑,形状可点)。
- **MP4** → `viz-deck` 模式4 motion-stage(经 huashu + ffmpeg),同样套暖纸 palette。
  产物:`*.mp4`(≤30MB / 1920×1080)。
- **单张图表 / 图谱** → 直接 `viz-charts`,palette 走 default-style 第 6 节,产物 .html 或 .png。

生成时**先对照 `references/default-style.md` 第 9 节自检清单**(暖纸底 / 三色条 / 深青主色 /
发丝卡片 / 粗体数字 / 克制动效),别在频道里草草了事。
做完**先自己核对文件真的生成了**(路径存在、大小合理),再进交付。

### 第 3 步 · 发回当前频道

用一行入口 `channel_send.sh`(优先 lark-cli 令牌,回退 REST):

```bash
# 发回当前频道(最常用)
bash scripts/channel_send.sh \
  --file output/2026-05-29-yundu-q2-deck.html \
  --to-current \
  --note "云度 Q2 动效报告已生成 ✦ 下载后用浏览器打开即可看到完整动效与图表"
```

```bash
# 若 --to-current 解析不到 chat_id,用事件里的 chat_id 显式发
bash scripts/channel_send.sh \
  --file output/...deck.html \
  --to oc_xxxxxxxxxxxx --to-type chat_id \
  --note "..."
```

Windows 上把 `bash scripts/channel_send.sh` 换成 `pwsh scripts/channel_send.ps1`(参数相同)。

**附言铁律**:
- 发 **HTML** → 必须提醒"**下载后用浏览器打开**才看得到动效"(飞书内直接点可能看不全)。
- 发 **PPTX** → 提示"可编辑,PowerPoint 里直接改"。
- 发 **MP4** → 不用提醒,飞书原生播放。

### 第 4 步 · 在频道里回执

文件发出后,在频道回一句简短确认:做了什么形态、发了什么文件、怎么看。
**别在文件还没真正发出前就说"已发给你了"**(见反模式)。

---

## 三种交付形态怎么选(默认动效 HTML)

| 用户的话 | 形态 | 模式 | 飞书里的体验 |
|---------|------|------|------------|
| "做个汇报/报告发我"(默认) | 动效 HTML | viz-deck 模式1 | 下载→浏览器开,动效+图表+3D全在 |
| "做个能改的 PPT" | 可编辑 PPTX | viz-deck 模式5 | 下载→PowerPoint 改 |
| "做个能直接播的发群里" | MP4 | viz-deck 模式4 | 视频消息,点开就播 |
| "画张图 / 做个知识图谱" | 图表 / 3D KG | viz-charts | HTML(交互)或 PNG(静态) |

完整决策逻辑(含 chart vs 3D KG、HTML vs PNG、大小/权限边界)见
`references/delivery-matrix.md`。频道对话话术模板见 `references/channel-protocol.md`。

---

## Hermes 特有:可把"对话生成PPT"做成 cron / webhook 自动化

Hermes 有 cron/webhook routine。除了频道里临时对话触发,还可把本流程编排成:
- **cron**:每周一 9:00 自动生成上周业绩动效报告,发到指定群(`--to <chat_id> --to-type chat_id`)。
- **webhook**:外部系统打点 → 触发生成 + 投递。
自动化场景没有"问清需求"这一步,需在 routine 配置里把主题/形态/接收方写死。
细节见 `references/hermes-channel.md`。

---

## 凭证与权限(自动找,一般不用配)

投递脚本按优先级找凭证:命令行 → 环境变量 `FEISHU_APP_ID/SECRET`
→ `~/.bodhi/config.yaml` → `~/.lark-cli/config.json`。
部署机若已配 lark-cli(明镜先生那套),`--via auto` 直接复用,无需另配。

发送方 app 需要权限:`im:message`、`im:message:send_as_bot`、`im:resource`
(上传文件/视频)。报 91402 / permission denied → 多半缺 `im:resource`,
去飞书开发者后台补上重新发版。

---

## 边界 & 反模式

- 文件 > 30MB(飞书文件消息上限):先压缩 / MP4 降码率,或转云文档发链接。
- ❌ 生成完没真跑投递就说"已发给你"——必须真发成功(脚本退出码 0)再回执。
- ❌ HTML 发出不提醒"下载用浏览器打开"——用户在飞书里直接点会以为没动效。
- ❌ 在频道里甩长问卷——最多 2 个关键问题,给足默认。
- ❌ 自己硬写 HTML/PPTX 跳过 viz 系技能——会丢掉设计系统、出 AI slop。
- ❌ 把 app_secret 写死进命令或提交进库。
