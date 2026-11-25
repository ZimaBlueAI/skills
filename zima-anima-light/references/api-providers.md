# API 提供方（Light）

首期默认云端路由；本地/开源模型列入目录但不默认启用。

## 生图

| 优先 | Provider key | 说明 |
|---|---|---|
| 1 | `seedream` | Seedream 4.5 / v5 Lite，中文与性价比 |
| 2 | `qwen_image` | Qwen-Image / Z-Image Turbo，图文编辑与草图 |
| 3 | `baidu_image` | 百度 AI 作画等（适配后启用） |

## 视频

| 优先 | Provider key | 说明 |
|---|---|---|
| 1 | `seedance` | Seedance 1.x/2.x 多模态叙事 |
| 2 | `wan` | 通义万相 Wan 系列 |
| 3 | `minimax_h3_api` | 仅 API，不启本地 Comfy |

## 音乐

`haimian`（海绵）、`skymusic` / `mureka`（天工）、`netease_tianyin`、`ace_step_api`

## 语音

`qwen3_tts`、`cosyvoice`、`minimax_speech`、`index_tts_api`（远程）

配置键见 `assets/.env.local.example`。真实调用前检查密钥、预算与青少年上传策略。
