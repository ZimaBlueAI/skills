# 本地引擎一站式配置（local stack）

目标：用户用最少的命令把本地 AI 引擎接进本 skill。所有键都写进同一个用户配置
`.env.local`（位置见 SKILL.md 配置契约），`configure.py set KEY VALUE` 逐项写入，
`configure.py validate` 一次体检。**先跑 doctor 再干活**是每个引擎的通用规则。

## 目录

- [快速配置清单](#快速配置清单按能力分组)
- [配置一次性走查](#配置一次性走查给用户的模板)

## 快速配置清单（按能力分组）

### 视频生成 — LTX-Video（本地 Docker，回环）
```dotenv
PCV_LTX_VIDEO_ENABLED=true
PCV_LTX_VIDEO_BASE_URL=http://127.0.0.1:7871
```
体检：`python scripts/ltx_video.py doctor`。适用边界与质检红线见 references/ltx-video.md
（单主体简单场景微动可用；真人照片与多角色复杂帧会崩，先目检）。

### 图像生成 — Qwen3-Image / Z-Image（本地 Docker，文生图）
```dotenv
PCV_QWEN3_IMAGE_ENABLED=true
PCV_QWEN3_IMAGE_BASE_URL=http://127.0.0.1:7864
PCV_QWEN3_IMAGE_MODEL=Tongyi-MAI/Z-Image-Turbo
```
契约：`POST /api/generate {prompt,width,height,num_inference_steps,guidance_scale}`、
`GET /health`、`POST /api/load`。**仅文生图**——需要图生图或保身份编辑时，路由到
已配置且声明相应能力的远程图像 provider，见 generative-image-providers.md。

### 3D — 混元3D + Blender（生成资产 → 确定性动画/渲染）
```dotenv
PCV_HUNYUAN3D_ENABLED=true
PCV_HUNYUAN3D_BASE_URL=http://127.0.0.1:8081
PCV_BLENDER=C:/Program Files/Blender Foundation/Blender 4.x/blender.exe
```
路径：混元3D 从概念图生成网格 → Blender 无头渲染（`blender -b scene.blend -P script.py`）
做确定性运镜/物理/转台展示。适用于：可量化机制（教育/产品）、道具/敌人三视图资产、
需要精确相机路径的镜头。生成网格进成片前逐帧目检拓扑与贴图崩坏。

### 语音 — IndexTTS-2（克隆）与 Qwen3-TTS（声音设计）
```dotenv
PCV_INDEX_TTS2_ENABLED=true
PCV_INDEX_TTS2_PYTHON=<venv python>
PCV_INDEX_TTS2_REPO_DIR=<index-tts 检出>
PCV_INDEX_TTS2_MODEL_DIR=<IndexTTS-2 模型目录>
PCV_QWEN3_TTS_ENABLED=true
PCV_QWEN3_TTS_PYTHON=<venv python>
PCV_QWEN3_TTS_VOICE_DESIGN_MODEL=<VoiceDesign 模型目录>
```
选型：有参考音、要"像某个人" → IndexTTS-2（多角色 voice bank 工序见 index-tts2.md）；
无参考音、要"设计一种声线"（VoiceDesign 自然语言描述音色）→ Qwen3-TTS。
Windows 崩溃守护键（HF 缓存/numba）见 index-tts2.md。

### 低配语音 — Pocket TTS 或 LuxTTS

无 GPU 且语言属于 Pocket TTS 当前官方列表时：

```dotenv
PCV_POCKET_TTS_ENABLED=true
PCV_POCKET_TTS_PYTHON=<venv python>
PCV_POCKET_TTS_LANGUAGE=english
```

Pocket 固定 CPU 优先，目前不含中文。低显存/CPU 且需要 48 kHz 克隆候选时：

```dotenv
PCV_LUX_TTS_ENABLED=true
PCV_LUX_TTS_PYTHON=<venv python>
PCV_LUX_TTS_REPO_DIR=<LuxTTS 检出>
PCV_LUX_TTS_MODEL=YatharthS/LuxTTS
```

不要无目的同时启用两组。LuxTTS 上游没有语言矩阵，必须先做语言专项 audition；角色声音批准后不可静默换引擎。安装、doctor、首次显式模型下载和 consent gate 见 `references/lightweight-tts.md`。

### 扩展 provider 的边界

只有在本 skill 中存在真实可调用的适配器、doctor 能验证其能力、且 TUI 已公开对应字段
时，才把扩展 provider 写入用户 `.env.local`。仅预留配置名、安装了上游仓库或拥有 API
key 都不代表本 skill 能执行它。新增图像、语音、转写、音乐或音效 provider 时应同时
补齐：适配器、能力声明、dry-run、上传/费用闸门、错误处理和最小测试。

对于 Suno、Udio、ElevenLabs 等外部服务，本 skill 默认只生成供应商中立的音乐或音效
brief。只有用户明确选择某服务、该服务存在已验证适配器，并批准本次上传与费用后才可
调用；不在说明中引导注册或推荐中转服务。密钥只写入 `.env.local`，不进命令行、日志
或交付物。

### 音乐与音效 — 本地无引擎时输出提示词包
本地未部署音乐模型时，skill 的交付物是**可直接粘贴的提示词包**（不是空手而归）：
- **音乐提示词**：按 generated-music-and-sfx.md 规范生成——含 BPM、
  结构段落（intro/verse/drop 秒数）、配器、情绪弧、参考风格锚点；卡点项目先出节奏
  网格再写提示词。用户指定 Suno 或 Udio 时，可在不改变创作意图的前提下映射到其
  当前字段格式。
- **音效/配音提示词**：逐条音效给出文字描述 + 时长 + 层次（近/中/远）+
  循环性要求；配音给出角色声线描述、情绪指示与断句标注。用户指定 ElevenLabs
  时再输出其当前字段版本。
- 提示词包存 `work/audio-prompts/`，用户生成后把成品文件路径回填 edit_plan。
本地可跑的兜底：Demucs 源分离回填（audio-post.md）、ffmpeg/numpy 合成简单
whoosh/riser/hit/drone。

## 配置一次性走查（给用户的模板）

```text
python scripts/configure.py init
python scripts/configure.py set PCV_FFMPEG <完整版 ffmpeg 路径>
python scripts/configure.py set PCV_FFPROBE <ffprobe 路径>
# 逐引擎 set 上面各组键（只配实际部署了的）
python scripts/configure.py validate
python scripts/ltx_video.py doctor        # 每个已启用引擎各跑一次 doctor
python scripts/index_tts2.py doctor
python scripts/qwen3_tts.py doctor
```
原则：只配置真实存在且有适配器的引擎；`pricing unknown` 表示必须保持 dry-run，
不能视为免费或自动放行；密钥只进 `.env.local`，永不进命令行、日志或成片元数据。
