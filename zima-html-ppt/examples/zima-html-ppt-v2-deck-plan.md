# 做完的 deck 改不动，等于没做完 · deck-plan

> zima-html-ppt v2 升级复盘。本 plan 是 `references/workflow.md` 的实例，
> 也是这份技能自带的示范：**先过方案，再做幻灯片。**

## 1. 意图卡

| 项 | 结论 |
|---|---|
| 受众 | ZimaBlueAI 内部工程与设计同学。已知这套技能能出片，不知道 v2 改了什么、为什么值得改工作方式 |
| 场景 | 内部技术分享 / 训战复盘，投影 + 讲 |
| 时长 | 23 分钟 → 主线 14 页（每页 45–90 秒，`data-min` 之和 = 23） |
| 交付 | 单文件 `.html` + `deck.json`（这份 deck 自己也要能被 extract 改稿） |
| 离线边界 | 只有第 11 页有 Chart.js 图表，走 CDN。断网现场这一页会空，其余 13 页不受影响 |
| 证据 | 全部数字来自本次改动的代码与测试输出，见每页 `source`；无估算、无 `[N/A]` |

## 2. 方向

- 选定：**`1a` 说服型** —— 一个冲突、一条变化、一句结论。
- 理由：受众不是不知道怎么做 deck，是不觉得"做完还能改"值钱。要先把痛点摆到台面上。
- 放弃的方向与代价：`3c` 训战型会变成 API 讲解课，听众记住语法但记不住为什么改。

## 3. 一句话结论

> 脚本过了不等于验收过了，但没有脚本，连"过没过"都无从谈起。

## 4. 叙事弧

冲突（v1 能出片，出片之后就死了）→ 借力（借纪律不借壳）→ 变化（事实源 + 闸门 + 证据纪律）
→ 代价（闸门自己也会骗人，浏览器那关得人来）→ 结论。

## 5. 逐页计划

| # | min | 版式 | 这页的任务 | 核心信息 | 视觉所有者 | 用什么块 | 逐字稿要点 | 来源 |
|---|-----|------|-----------|---------|-----------|---------|-----------|------|
| 01 | 2 | cover | 立命题 | 四个数字砸出改动量级 | 标题 | metrics | cue + say + data + bridge | 本次改动统计 |
| 02 | 2 | full | 摆冲突 | v1 出片之后就死了 | 卡片 | cards | cue + say + do + bridge | v1 技能目录 |
| 03 | 1 | full | 交代来源 | 借纪律不借壳 | 引言 | quote + list | say + do + bridge | NOTICE.md |
| 04 | 2 | split | 亮机制 | HTML 里内嵌 deck.json | 代码块 | term + text ‖ list + pills | cue + data + do + bridge | zima_deck.py |
| 05 | 2 | full | 展开闸门 | 七道闸门，最后一道是人 | 列表 | list | cue + say + data + bridge | gates.md |
| 06 | 2 | full | 落到具体 | 结构闸门 38 项硬拦截 | 表格 | table | cue + say + data + do + bridge | 代码计数 |
| 07 | 2 | compare | 给选择 | 两条路线各有场合 | 卡片 | cards ‖ cards + table | cue + say + do + bridge | workflow.md |
| 08 | 1 | full | 讲纪律 | missing evidence | 引言 | quote + text + pills | cue + say + do + bridge | gates.md |
| 09 | 2 | full | 兑现纪律 | 复核查出三个真缺陷 | 卡片 | cards | cue + say + data + do + bridge | 浏览器复核 |
| 10 | 2 | split | 挖最狠的一个 | 条形从来没显示过 | 代码块 | term ‖ bars + list | cue + say + data + do + bridge | starter.html diff |
| 11 | 2 | split | 说覆盖 | 31 项回归守住边界 | 图表 | chart ‖ list | cue + say + data + do + bridge | evals 输出 |
| 12 | 1 | full | 给方法 | 视觉所有者 | 引言 | quote + list | say + do + bridge | workflow.md |
| 13 | 1 | full | 说交付 | 五件套输出契约 | 列表 | list | cue + say + bridge | gates.md |
| 14 | 1 | closing | 收束 | 一句话带走 | 标题 | bigline + quote + term | say + do | — |
| 合计 | **23** | | | | 用到 11/12 种块（`html` 逃生口刻意不用） | | | |

> `‖` 左右两侧分别是 `blocks` 与 `right` 两栏。

> **视觉所有者**逐页只指定一个：标题说完的结论，正文不再复述；图表说完的量级，
> 逐字稿只补"为什么是这个量级"。

## 6. 素材清单

| 素材 | 形态 | 来源 | 状态 |
|---|---|---|---|
| 38 项 error / 14 项 warning | 数字 | `grep -c 'add_error(' scripts/zima_deck.py` | 已核 |
| 31 项回归（15 + 16） | 数字 | `evals/run_fixtures.py` / `scripts/trigger_eval.py` 输出 | 已核 |
| 12 块型 / 5 版式 / 4 子命令 / 7 闸门 / 8 条 shell 签名 | 数字 | 代码常量 | 已核 |
| 1024 行脚本 | 数字 | `wc -l scripts/zima_deck.py` | 已核（未上台，deck 里没用到这个数） |
| 三个渲染缺陷 | 描述 + 数值 | 浏览器实测（fills 0×0 → 332×11 / 239×11；横滚 25px → 0） | 已核 |
| 上游 commit `55c63c8` | 标识 | qiaomu-bento-ppt git log | 已核 |

## 7. 动效时刻

- 全场保留 2 个"数字砸下来"的时刻：第 1 页封面四个 metric 滚动；第 10 页两根条形，
  上面一根停在 0（修复前的 0px），下面一根填满（修复后的 11px）。
  这根条形正是本次修好的那个组件——**动效本身就是论据**，空的那根不是没动画，是没盒子。
- 其余动效只做入场。无循环、无辉光、无粒子。

## 8. 风险与 missing evidence

- 演讲者窗口（S 键）在 headless 环境验不了 —— `window.open` 被拦。数据链路已核，
  窗口观感待人工确认：`missing evidence: presenter window check`。
- 断网现场第 5、11 页图表会空白：`missing evidence: offline rendering (Chart.js CDN)`。
- 未在实际投影分辨率上看过：`missing evidence: projector resolution check`。
