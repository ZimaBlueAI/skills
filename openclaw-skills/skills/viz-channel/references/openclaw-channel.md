# OpenClaw 平台细节 · 频道、chat_id、技能目录

> 本文件只讲 **OpenClaw 这一侧** 怎么拿当前频道、技能装哪、文件怎么发回去。
> 生成与对话逻辑见 SKILL.md / channel-protocol.md / delivery-matrix.md。

---

## 1. OpenClaw 的飞书频道是怎么连的

- OpenClaw 用内置 **飞书 channel 插件**,通过 **WebSocket 长连接** 订阅飞书事件
  (`im.message.receive_v1` 等),无需公网回调地址。
- 用户在飞书 @机器人 发消息 → OpenClaw 收到事件 → 把消息路由进当前 agent 的会话
  → agent(你)读 SKILL.md 干活 → 回复**自动**走 channel 发回该会话。
- 会话绑定:OpenClaw 把 飞书 chat ↔ 一个 `session`(`~/.openclaw/agents/<id>/sessions/`)绑定,
  所以**多轮迭代**(用户说"改一下")天然在同一上下文里。
- 频道命令:`openclaw channels status --probe`(诊断)、
  `openclaw channels logs --channel <id>`(看日志)。

## 2. 拿当前频道 chat_id 的三条路(按优先级)

文本回复 OpenClaw 自动发回当前会话;但**发文件**要我们显式调投递脚本,
所以需要知道当前 `chat_id`。按下面顺序拿:

1. **环境变量(最省事)**:OpenClaw 在频道会话里通常注入当前 chat 上下文。
   先跑 `python3 scripts/resolve_chat.py`,它会检查
   `FEISHU_CHAT_ID / OPENCLAW_CHAT_ID / OPENCLAW_CHANNEL_CHAT_ID / CHAT_ID` 等。
   解析到就用 `channel_send.sh --to-current`。
2. **事件上下文**:解析不到环境变量时,从**触发本次对话的飞书消息事件**里读 `chat_id`
   (群聊是 `oc_` 开头)。用 `--to <chat_id> --to-type chat_id` 显式发。
3. **私聊兜底**:实在拿不到 chat_id,但知道用户 `open_id` → `--to <open_id> --to-type open_id`
   私发给本人(群场景会变成私聊,需向用户说明)。

> 若你的 OpenClaw 版本没注入 chat_id 环境变量,可在 channel 配置 / workspace 的
> AGENTS.md 里加一条:把当前 `chat_id` 写入 `FEISHU_CHAT_ID` 供技能读取。

## 3. 技能装在哪(加载优先级 高→低)

| 优先级 | 路径 | 说明 |
|---|---|---|
| 1 | `<workspace>/skills/` | 每 agent,最高 |
| 2 | `~/.openclaw/skills/` | 跨工作区共享 |
| 3 | OpenClaw 内置 | 最低 |

本桥接默认装到 `~/.openclaw/skills/`(共享),即:
```
~/.openclaw/skills/viz-channel/   ← 本技能
~/.openclaw/skills/viz-deck/              ← 生成(动效HTML/PPTX/MP4)
~/.openclaw/skills/viz-charts/            ← 图表 / 3D KG
~/.openclaw/skills/biz-html-viz/          ← 可选,商业决策报告
```
装法见 `../../install-openclaw-skills.sh`(Linux/WSL)或 `.ps1`(Windows)。

## 4. SKILL.md 触发机制(写 description 的注意)

OpenClaw 只读 frontmatter 的 `name` + `description` 决定要不要触发技能。
`description` 要写**触发条件**(用户会说什么),不是功能介绍——
本技能的 description 已覆盖"做PPT/做汇报/做图表/知识图谱/发给我/发群里"等口语触发词。

## 5. 文件发回去:为什么不用 channel 原生发,而是调脚本

- OpenClaw 的文本回复走 channel 自动回;但跨版本**直接发文件附件**的能力不一,
  且要拿 file_key、走飞书上传 API。
- 因此本桥接用 `scripts/channel_deliver.py`(REST,稳定)统一处理上传+发送,
  `--via auto` 会**优先复用 lark-cli 的令牌**(部署机若配了 lark-cli),取不到再直连 REST。
- 这样无论 OpenClaw 版本如何,文件交付路径都确定、可调试。

## 6. 常见问题

- **Q: 文本能自动回,文件发不出去?**
  A: 多半是 chat_id 没拿到(见第 2 节)或 app 缺 `im:resource` 权限。
- **Q: 群里机器人不理我?**
  A: 群聊要 **@机器人**;且确认 channel 在线 `openclaw channels status --probe`。
- **Q: 多个龙虾/多 Bot 怎么不串台?**
  A: 用 `session.dmScope = per-channel-peer`(速查表),不同频道/用户隔离上下文。
- **Q: 装了 viz-deck 但生成报"huashu/ppt-master not installed"?**
  A: 只有 PPTX(模式3/5)和 MP4(模式4)需要桥接;默认的动效 HTML(模式1)不需要。
     装桥接:`install-openclaw-skills.sh --with-bridges`。
