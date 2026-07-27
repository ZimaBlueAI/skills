# LTX-Video 本地图生视频服务

`scripts/ltx_video.py` 对接一个本地 LTX-Video HTTP 服务（Lightricks/ltx-video 的 Docker 封装，
契约：`GET /health`、`POST /generate`（multipart）、`GET /tasks/{id}`、`GET /tasks/{id}/result`）。
回环地址可降低素材外传风险，但不替代肖像、声音或未成年人监护人授权。敏感影像只有
在项目用途、访问权限和保留期限已明确时才走本地适配器；未经单独批准不得改走远程
provider。

## 用户配置

```dotenv
PCV_LTX_VIDEO_ENABLED=true
PCV_LTX_VIDEO_BASE_URL=http://127.0.0.1:7871
# 可选：单任务等待上限（默认 900s）
PCV_LTX_VIDEO_TIMEOUT_S=900
```

非回环地址必须是 HTTPS，否则适配器拒绝启动。

## 用法

```text
python <skill-dir>/scripts/ltx_video.py doctor
python <skill-dir>/scripts/ltx_video.py generate \
  --prompt "<英文动作描述，写运动不写风格空话>" \
  --image first_frame.jpg --width 512 --height 768 \
  --num-frames 97 --frame-rate 25 --output out.mp4
```

约束（客户端强制）：宽高被 32 整除；`num_frames % 8 == 1`（81/97/121…）。
输出不覆盖已有文件，自动写 provenance sidecar（含 prompt/seed/task_id/披露标记）。

## 质检红线（实测教训）

真人照片直接图生视频时 LTX 会发生**身份漂移**——脸会变成另一个人，还可能凭空加人、
把道具变形（头灯→红眼）。凡涉及真实人物（尤其儿童）的镜头，逐帧目检身份保真是硬闸；
不合格就不进成片。两条替代路径：
1. **宝丽来合成**：真照片压白框卡片，叠在（模糊+压暗的）动画场景背景上做缓移入场——零 API 成本，身份 100% 保真；
2. **先卡通化再生视频**：先用生图模型把人物转绘成动画角色关键帧（卡通域对漂移不敏感），再喂 LTX 首帧生视频。
