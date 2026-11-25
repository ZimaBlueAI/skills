---
name: zima-anima-light
description: Open-source non-professional animation studio distilled from zima-anima/PCV. Youth Lookbook 61 (40 style packs + 21 masters/design agents), Soft Studio (look/story/materials/review/cut timeline), infinite canvas, material history, director/supervisor/producer agents, API-first Seedream/Seedance. Install into WorkBuddy, Doubao Work, TRAE, Qoder, DeepSeek Harness, Kimi Work, CodeBuddy, MiniMax Code, Coze, Bailian and similar Work agents. 开源非专业动画工作室轻量版：青少年向61风格与大师、选片与剪辑台、好用易用，可接入各类 Work Agent。
metadata:
  version: "0.2.0"
  audience: youth_and_creators
  edition: light
  lookbook: "61"
---

# Zima Anima Light

从 **zima-anima / produce-cinematic-video** 提炼的**开源非专业版**动画工作室：保留「工作流 + 素材历史 + 一致性 + Agent 监看」骨架，去掉 GPU 农场与院线片场复杂度。

交互对齐消费级创作工具的节奏（即梦 AI、Seko、PixVerse、Pika、Morphic、OiiOii、小云雀 AI 等）：**选入口 → 画布上推进 → 预览 → 确认费用 → 出片**，而不是先填一堆工程表单。

本包自包含 `agents / prompts / mcp / scripts / studio / styles / masters`，可单独装进各类 Work Agent，不必同装完整 zima-anima。

## 固定入口

| 入口 | ID |
|---|---|
| 从故事剧本开始 | `from_story` |
| 从图片开始 | `from_image` |
| 从音乐开始 | `from_music` |
| 从视频开始 | `from_video` |

## Soft Studio 模式

| 模式 | 作用 |
|---|---|
| 创作 | 风格与大师（Lookbook）、故事协作、流程画布 |
| 素材 | 素材堆叠 / 版本历史 |
| 选片 | 审片台：通过 / 不通过 / 待定 / 存档 |
| 剪辑 | 时间线：选片入库、拉伸缩放、剪开、复制粘贴、调速、加减镜头 |
| 助手 | Agent 说明 |

## 青少年向 Lookbook（61）

权威册：`styles/lookbook_61.json`（**40 风格包 + 21 大师 = 61**）。

| 部分 | 路径 | 说明 |
|---|---|---|
| 风格包 | `styles/packs/*.json` | EN/ZH 提示词前缀、签名、避开项、设计 Agent 系统提示 |
| 大师 | `/api/masters` | 导演、艺术总监、摄影灯光运镜、剪辑大师、监制的阵容与配图 |
| 风格示例 | `studio/style-covers/<id>.webp` | 按风格包 ID 对应的示例画面 |
| 设计 Agent | `agents/design/<id>.md` | 每条 Lookbook 的可加载系统提示 |
| 同步脚本 | `scripts/youth_lookbook.py` | 重生成 packs / masters / agents |

分类：`campus` `daily` `city` `lyric` `edu` `craft` `genre` `format`。安全红线见 [references/youth-safety.md](references/youth-safety.md) 与 [references/youth-lookbook.md](references/youth-lookbook.md)。

提示词规则：只写光、形、材质、动作、机位；**禁止真实名人姓名**与成人/恐怖题材。

## 运行

```text
python -B <skill>/scripts/light_cli.py doctor
python -B <skill>/scripts/light_cli.py lookbook
python -B <skill>/scripts/light_cli.py lookbook --sync
python -B <skill>/scripts/light_cli.py init <project> --workflow from_story --title "我的短片"
python -B <skill>/scripts/light_cli.py serve <project>
python -B <skill>/scripts/light_cli.py import-legacy <full-zima-project>
```

工作室常用 API：`/api/styles` `/api/lookbook` `/api/masters` `/api/review` `/api/timeline` `/api/story`。

## 与完整版关系

| | Light | 完整 zima-anima |
|---|---|---|
| 对象 | 青少年 / 创作者 / Work Agent | 专业片场 |
| 算力 | 云 API 为主 | 本地/LAN GPU + API |
| 画布 | 无限画布工作流 + 素材历史 | 制片工程图 + 分镜工作台全家桶 |
| 风格 | Lookbook 61（青年向） | 多部门大师名册 + 组阁 |
| 升级 | 需要院线级控制时再装完整版 | — |

## Agent

- `agents/director.md` 导演（默认可切换 Lookbook 大师）
- `agents/supervisor.md` 固定工作流监工。通过 `/api/work-queue` 跟踪队列与调整顺序，逐项确认付费任务。
- `agents/producer.md` 监制
- `agents/design/` Lookbook 设计 Agent 名册（61）
- 宿主系统提示可叠加 `prompts/system-youth-studio.md`

## 多 Harness

WorkBuddy、豆包 Work、TRAE、Qoder、DeepSeek Harness、QoderWork、Kimi Work、百度搭子、CodeBuddy、ZCode、MiniMax Code、Coze、阿里云百炼、Claude Code、Codex CLI 等见 `installer/targets.toml` 与 [references/multi-harness.md](references/multi-harness.md)。

```text
python -B <skill>/scripts/light_cli.py install --target qoder          # dry-run
python -B <skill>/scripts/light_cli.py install --target claude --apply
python -B <skill>/scripts/light_cli.py install --target workbuddy --apply
```

## API

Seedream / Qwen-Image、Seedance / Wan、海绵·天工等音乐、通义 TTS 等：见 [references/api-providers.md](references/api-providers.md) 与 `assets/.env.local.example`。
