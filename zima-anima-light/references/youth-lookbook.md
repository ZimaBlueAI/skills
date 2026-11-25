# 青少年向 Lookbook（61）

## 构成

| 数量 | 类型 | 来源 |
|---:|---|---|
| 40 | 风格包 | `styles/packs/*.json` |
| 21 | 大师（导演 13 + 监工 4 + 监制 4） | `masters/catalog.json` |
| **61** | 设计 Agent | `agents/design/` + `styles/lookbook_61.json` |

同步：

```text
python -B scripts/youth_lookbook.py
# 或
python -B scripts/light_cli.py lookbook --sync
```

## 风格分类

| category | 用途 |
|---|---|
| campus | 校园日常光与空间 |
| daily | 家庭 / 旅行手账 |
| city | 安全夜城等城市气质 |
| lyric | 雨窗等细小转折 |
| edu | 白板 / MG / 实验 / 地理 / 安全教育 |
| craft | 剪纸、水墨、黏土、赛璐璐、条漫、3D 玩具等工艺 |
| genre | 轻奇幻、软科幻、谜题、舞台、舞蹈、喜剧 |
| format | 竖屏、横幅短片、MV、Vlog、无声喜剧、皮影 |

## 新增导演（相对 v0.1）

知行（科普）· 跃场（运动）· 弦台（舞台）· 谜社（清爽谜题）· 笑点（喜剧）· 砚舟（国风）· 竖芽（竖屏）· 纪实青（纪录）· 圆灯（合家欢动画）

## 提示词编译

1. 只用可见/可听事实：光、形、材质、动作、机位、节拍。
2. 每条风格包带 `prompt_prefix`（EN）与 `prompt_zh`。
3. 全局避开：horror / gore / realistic celebrity likeness / adult romance / dark occult。
4. 禁止在生成提示里写真实大师或明星姓名；师承只用于思考，不进 prompt。

## Soft Studio

创作页「风格与大师」按分类筛选风格包；选中后展示当前设计 Agent 系统提示。API：`GET /api/lookbook`、`GET /api/styles`。

## 调研摘要（选型依据）

- 未成年人短视频偏好偏幽默、人文知识、热点、日常、动漫游戏。
- 教育影像常用实拍、纪录、白板讲解、剪纸/定格等可操作技法。
- 青少年向动画媒介覆盖赛璐璐、条漫、国风、黏土、合家欢 3D、玩具微缩。
