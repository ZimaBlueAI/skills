# 产品定位

## 我们是什么

**Zima Anima Light** = 开源、非专业、好用的动画短片工作室 skill。  
内核来自 zima-anima / PCV 的工作流、素材版本、一致性与 Agent 监看；形态贴近消费级创作 App，并可装进各类 Work Agent。

## 体验对标（只学交互节奏，不抄品牌与资产）

| 产品 | 可借鉴点 |
|---|---|
| 即梦 AI | 文/图/视频入口清晰、预览优先 |
| Seko / PixVerse / Pika | 短视频生成路径短、参数少 |
| Morphic / OiiOii / 小云雀 | 画布或会话式创作、降低片场感 |

本仓库不嵌入上述产品的商标、素材或私有协议实现；仅作为易用性参考。

## 非目标

- 不是院线级 Production Graph 替代品（那是完整 zima-anima）。
- 不是本地 Comfy / H3 GPU 农场发行版。
- 不是单一封闭 SaaS；优先 API 可插拔 + skill 可分发。

## Work Agent 用法

宿主加载本目录 `SKILL.md` 后：

1. 用 `light_cli.py init` 建项目；
2. `serve` 打开无限画布；
3. Agent 读 `agents/*.md` 与 MCP `light_*` 工具推进节点。
