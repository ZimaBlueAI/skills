# Hermes Agent 平台细节 · 频道、chat_id、技能目录、自动化

> 本文件只讲 **Hermes Agent 这一侧** 怎么拿当前频道、技能装哪、文件怎么发回去、
> 以及怎么把"对话生成PPT"做成 cron/webhook 自动化。
> 生成与对话逻辑见 SKILL.md / channel-protocol.md / delivery-matrix.md。

---

## 1. Hermes 的飞书是怎么连的

- Hermes Agent 自带多平台 gateway adapter(Telegram/Discord/Slack/WhatsApp/Signal/
  Weixin/WeCom/**Feishu**)。飞书入站消息经 gateway 归一化成统一 envelope,
  绑定到一个 **session**(Hermes 有 session search / memory provider)。
- 用户在飞书发消息 → gateway 收到 → 路由进 agent loop → agent(你)读 SKILL.md 干活
  → 文本回复经 gateway 发回该会话。
- Hermes 的安装/运维:`hermes install` / `hermes setup` / `hermes doctor` / `hermes logs`。
  排查频道用 `hermes doctor`(检查 gateway 连接、凭证、session)。

## 2. 拿当前频道 chat_id 的三条路(按优先级)

文本回复 gateway 自动发回当前会话;但**发文件**要显式调投递脚本,需要当前 `chat_id`:

1. **环境变量 / session 元数据(最省事)**:Hermes 把入站会话上下文绑定到 session;
   当前 chat 通常可从环境变量读到。先跑 `python3 scripts/resolve_chat.py`,
   它检查 `FEISHU_CHAT_ID / HERMES_CHAT_ID / HERMES_CHANNEL_CHAT_ID / CHAT_ID` 等。
   解析到就用 `channel_send.sh --to-current`。
2. **事件上下文**:解析不到环境变量时,从**触发本次对话的飞书消息事件**里读 `chat_id`
   (群聊是 `oc_` 开头)。用 `--to <chat_id> --to-type chat_id` 显式发。
3. **私聊兜底**:拿不到 chat_id 但知道用户 `open_id` → `--to <open_id> --to-type open_id`。

> 若你的 Hermes 版本没把 chat_id 注入环境变量,可在 gateway 适配层 / agent 启动脚本里
> 把当前 `chat_id` 导出为 `HERMES_CHAT_ID` 供技能读取;或始终走第 2 条(事件上下文)。

## 3. 技能装在哪

Hermes 有内置/可选技能 + Skills Hub。本桥接把技能装进 Hermes 的 skills 目录,
默认 `~/.hermes/skills/`(若你的部署不同,用安装器 `--target <你的skills目录>` 指定,
或先 `hermes doctor` / 看 Hermes 配置确认 skills 加载路径):

```
<hermes skills 目录>/viz-channel/   ← 本技能
<hermes skills 目录>/viz-deck/              ← 生成(动效HTML/PPTX/MP4)
<hermes skills 目录>/viz-charts/            ← 图表 / 3D KG
<hermes skills 目录>/biz-html-viz/          ← 可选,商业决策报告
```
装法见 `../../install-hermes-skills.sh`(Linux/WSL)或 `.ps1`(Windows)。
SKILL.md 同样是 frontmatter(`name`+`description` 作触发器)+ 正文(操作手册)。

## 4. 文件发回去:为什么不用 gateway 原生发,而是调脚本

- gateway 的文本回复自动回;但**跨 adapter 统一发文件附件**的能力不一,
  且飞书发文件要先上传拿 file_key。
- 因此本桥接用 `scripts/channel_deliver.py`(REST,稳定)统一处理上传+发送,
  `--via auto` 会**优先复用 lark-cli 的令牌**(部署机若配了 lark-cli),取不到再直连 REST。
- 这样无论 Hermes 版本如何,文件交付路径都确定、可调试。

## 5. 把"对话生成PPT"做成 cron / webhook 自动化(Hermes 强项)

Hermes 的 cron/webhook routine 可以无人值守地跑生成+投递。和频道对话的区别:
**没有"问清需求"这步**,所有参数在 routine 配置里写死。

**cron 示例(每周一 9:00 自动出上周业绩动效报告发到运营群):**
```
触发: cron "0 9 * * 1"
步骤:
  1. (按固定数据源/模板) viz-deck 模式1 生成 output/weekly-deck.html
  2. bash scripts/channel_send.sh \
       --file output/weekly-deck.html \
       --to oc_<运营群chat_id> --to-type chat_id \
       --note "上周业绩动效周报 ✦ 下载用浏览器打开"
```

**webhook 示例(外部系统打点 → 出图发群):**
```
触发: webhook POST /routines/deck-on-event  (带 payload: topic, chat_id)
步骤:
  1. viz-charts 按 payload 数据出图 output/event-chart.html
  2. bash scripts/channel_send.sh --file output/event-chart.html \
       --to <payload.chat_id> --to-type chat_id --note "..."
```

自动化里把接收方 chat_id 固定写好,不要依赖 `--to-current`(无交互上下文)。

## 6. 常见问题

- **Q: 文本能自动回,文件发不出去?**
  A: 多半 chat_id 没拿到(见第 2 节)或 app 缺 `im:resource` 权限。
- **Q: 群里机器人不理我?** A: 群聊要 **@机器人**;`hermes doctor` 看 gateway 是否在线。
- **Q: 多用户会话串台?** A: 确认 Hermes 的 session 按 chat/user 维度隔离(memory scope)。
- **Q: 装了 viz-deck 但生成报"huashu/ppt-master not installed"?**
  A: 只有 PPTX(模式3/5)和 MP4(模式4)需要桥接;默认动效 HTML(模式1)不需要。
     装桥接:`install-hermes-skills.sh --with-bridges`。
