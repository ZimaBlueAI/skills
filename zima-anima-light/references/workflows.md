# 固定工作流

所有入口共用同一套节点合同，只改变起点与解锁顺序。

## 共用节点

`intake` → `story` → `assets` → `continuity_lock` → `storyboard` → `generate_stills` → `generate_video` → `audio` → `edit` → `qc` → `deliver`

## 入口差异

| 工作流 | 跳过/前置 |
|---|---|
| `from_story` | 从 `story` 写剧本与角色 |
| `from_image` | `intake` 绑定主图，先建 `assets` 再补 `story` |
| `from_music` | `intake` 绑定曲目与段落情绪，分镜按拍点 |
| `from_video` | `intake` 绑定参考视频与抽帧，强制 `continuity_lock` |

## 大节点确认（guided）

用户必须确认：`story`、`assets`、`storyboard`、`generate_video`（代表样片）、`edit`、`deliver`。其余由监工按证据内部签收。

## 一致性

角色 / 道具 / 场景必须有 canonical 素材 ID；分镜与生图请求绑定这些 ID。连续性状态写在 `continuity.json`。
