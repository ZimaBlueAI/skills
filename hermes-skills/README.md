# Hermes Agent · 动效HTML + 图表/3D知识图谱 + PPTX，频道里对话生成并交付

> 让 Hermes Agent 在 IM 频道里跟用户**对话**，用 ZimaBlueAI 的 `viz-deck` / `viz-charts`
> 生成**自定义风格的动效 HTML（含图表、3D 知识图谱）/ 可编辑 PPTX / MP4**，
> 再把成品作为附件**发回当前会话**。
> **当前投递 adapter = 飞书 / Lark**（优先 lark-cli，回退 REST）；Hermes 的 gateway
> 还支持 Telegram/Discord/Slack/企业微信 等，换通道只需在 `channel_deliver.py` 加 adapter。

---

## 这是什么

ZimaBlueAI 仓库的三个技能只管**生成**，不管**送达**，也没有**频道对话编排**。
本目录补齐这两环，把它们落到 Hermes：

```
用户在频道 @机器人:「做个云度 Q2 的动效汇报发我」
        │
        ▼  Hermes 飞书 gateway adapter 收到消息,绑定到 session
        ▼  触发 viz-channel 技能
   ┌────────────────────────────────────────────┐
   │ 1. 频道里问清需求(≤2 问,给默认)            │
   │ 2. viz-deck 模式1 生成动效 HTML             │
   │    (图表/3D KG 由 viz-charts 提供)         │
   │ 3. channel_send.sh 把 deck.html 发回当前 chat │
   │ 4. 频道回执"已发,下载用浏览器看"            │
   └────────────────────────────────────────────┘
```

Hermes 强项:同一条链路还能做成 **cron / webhook 自动化**(无人值守定时出报告发群),
见 `skills/viz-channel/references/hermes-channel.md`。

## 目录结构

```
hermes-skills/
├── README.md                        ← 你在看
├── USAGE.md                         ← ★ 实战案例库(11 个案例,含 cron/webhook 自动化)
├── install-hermes-skills.sh         ← 一键安装(Linux / WSL / git-bash)
├── install-hermes-skills.ps1        ← 一键安装(Windows PowerShell)
└── skills/
    └── viz-channel/                 ← ★ 频道对话 + 交付编排技能
        ├── SKILL.md                 ← 触发器 + 工作流(clarify→generate→deliver)
        ├── references/
        │   ├── default-style.md     ← ★ 默认视觉风格 ZimaBlue Editorial(暖纸编辑风)
        │   ├── channel-protocol.md  ← 频道对话话术 / 状态机 / 多轮迭代
        │   ├── delivery-matrix.md   ← 形态决策(HTML/PPTX/MP4/chart/3D KG)
        │   └── hermes-channel.md    ← Hermes 侧:chat_id、技能目录、cron/webhook 自动化
        ├── templates/
        │   └── zima-editorial-deck.html  ← 默认 HTML 起步骨架(令牌/组件/图表就绪)
        └── scripts/
            ├── channel_deliver.py   ← 频道投递适配器(当前:飞书/Lark REST,--via auto 优先 lark-cli)
            ├── resolve_chat.py      ← 解析当前频道 chat_id
            ├── channel_send.sh      ← 投递一行入口(Linux)
            └── channel_send.ps1     ← 投递一行入口(Windows)
```

`viz-deck` / `viz-charts` / `biz-html-viz` 的本体**不在这里**——
安装器从本仓库 `../claude-code-skills/*/*.zip` 取(或 `--from-github` 实时拉),
装进 Hermes 的 skills 目录。大技能本体单一可维护、不重复。

## 安装

前提:Hermes 已接好你的频道(飞书 gateway adapter,群里 @机器人 响应);
`hermes doctor` 确认 gateway 在线、skills 目录路径。然后:

```bash
# Linux / WSL / git-bash —— 默认(动效 HTML + 图表 + 3D KG + 频道交付)
bash install-hermes-skills.sh

# skills 目录非默认时显式指定
bash install-hermes-skills.sh --target /your/hermes/skills

# 要 MP4 / 可编辑 PPTX
bash install-hermes-skills.sh --with-bridges
```

```powershell
# Windows
./install-hermes-skills.ps1 -WithBridges
```

装完自检会列出 skills 目录下的 `viz-deck / viz-charts / viz-channel`。

## 用法(在频道里)

@机器人，直接说人话：

| 你说 | 出什么 | 收到的体验 |
|------|--------|-----------|
| 「做个 X 的动效汇报发我」 | 动效 HTML（默认） | 下载→浏览器开，动效+图表+3D 全在 |
| 「做个能改的 X PPT」 | 可编辑 PPTX | 下载→PowerPoint 改 |
| 「做个 X 动画发群里」 | MP4 | 视频消息，点开就播 |
| 「画个 X 的 3D 知识图谱」 | 3D KG（WebGL） | 下载→浏览器转着看 |

机器人会先问清 1-2 个关键点（主题/形态），再生成，再发回你正在聊的这个会话。

> 📖 **完整实战案例（季度汇报 / 可编辑 PPT / 3D 知识图谱 / 发布会动画 / 竞品格局 /
> 群里改稿 + Hermes 的 cron 自动周报 / webhook 触发出图）见 [USAGE.md](USAGE.md)。**

## 凭证 & 权限（飞书 adapter）

- 凭证自动找：`FEISHU_APP_ID/SECRET` 环境变量 → `~/.bodhi/config.yaml` → `~/.lark-cli/config.json`。
  部署机配过 lark-cli（明镜先生那套）就直接复用。
- app 权限需：`im:message`、`im:message:send_as_bot`、`im:resource`（上传文件/视频）。
  报 91402 多半缺 `im:resource`，去飞书开发者后台补上重新发版。
- 换其它频道（企业微信/Slack/Telegram）：在 `channel_deliver.py` 按相同结构加 adapter。

## 与 openclaw-skills 的关系

`openclaw-skills/` 是同一套能力面向 **OpenClaw** 的平行实现。技能本体、脚本、对话协议
与形态决策完全相同，差异只在平台连接细节（chat_id 来源、技能目录、安装器、自动化方式），
分别见各自的 `references/<platform>-channel.md`。

## 默认视觉风格

频道生成的 HTML / PPTX **默认走 ZimaBlue Editorial（暖纸编辑风）**——暖白纸底 + 深青主色
（`#1b5e5a`）+ 金/赭点缀 + 发丝描边卡片 + 顶部 teal→gold→red 三色条 + 大号粗体数字。
专业、简洁、出片即用（参考母版 `D1-破局与进化.html`）。完整设计系统与起步模板见
`skills/viz-channel/references/default-style.md` 与 `templates/zima-editorial-deck.html`。
要换风格直接在频道里说（"用深空风" / "用我们品牌色 #xxxxxx"）。

## 更多

- 🔥 实战案例库（11 个案例,含自动化）→ [USAGE.md](USAGE.md)
- 🎨 默认视觉风格 → `skills/viz-channel/references/default-style.md`
- 形态怎么选 → `skills/viz-channel/references/delivery-matrix.md`
- 频道对话怎么编排 → `skills/viz-channel/references/channel-protocol.md`
- Hermes 平台细节 + cron/webhook → `skills/viz-channel/references/hermes-channel.md`
