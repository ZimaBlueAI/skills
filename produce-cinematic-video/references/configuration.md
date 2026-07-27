# 安装后配置

## 目录

- [配置位置](#配置位置)
- [初始化](#初始化)
- [依赖安装](#依赖安装)
- [配置优先级](#配置优先级)
- [工具配置](#工具配置)
- [提供方配置](#提供方配置)
- [密钥与隐私](#密钥与隐私)
- [预算与发布策略](#预算与发布策略)
- [交付 profile](#交付-profile)
- [验证和排错](#验证和排错)

## 配置位置

默认把 skill 安装到当前用户目录，Windows、macOS、Linux 都使用同一个逻辑位置：

- 用户级安装：`~/.codex/skills/produce-cinematic-video`
- 项目级安装（需要项目隔离或锁定版本时）：`<project>/.codex/skills/produce-cinematic-video`

`~` 表示当前用户主目录；在 Windows PowerShell 中对应 `$HOME`。运行配置与 skill 本体分离，升级或替换 skill 时不会覆盖个人设置：

- Windows：`%APPDATA%\produce-cinematic-video\.env.local`
- macOS：`~/Library/Application Support/produce-cinematic-video/.env.local`
- Linux：`${XDG_CONFIG_HOME:-~/.config}/produce-cinematic-video/.env.local`
- macOS 显式设置 `XDG_CONFIG_HOME` 时也会优先使用它
- 自定义：设置 `CINEMATIC_VIDEO_ENV_FILE` 为完整文件路径
- 兼容迁移：旧 `CINEMATIC_VIDEO_CONFIG` 仍可指向 `.env.local` 或旧 `config.json`

不要把用户配置或密钥打包回 skill。

大型模型、独立运行时和可重建缓存不要放进 skill 或 Windows 漫游配置目录。建议用户数据根目录：

- Windows：`%LOCALAPPDATA%\produce-cinematic-video`
- macOS：`~/Library/Application Support/produce-cinematic-video`
- Linux：`${XDG_DATA_HOME:-~/.local/share}/produce-cinematic-video`
- 自定义：`CINEMATIC_VIDEO_DATA_HOME`

查看 skill、配置、模型和 runtime 的实际路径：

`python <skill-dir>/scripts/configure.py paths`

不想手工编辑 dotenv 时，直接打开跨平台终端向导：

`python <skill-dir>/scripts/configure.py tui`

向导不依赖 curses/Textual，在 Windows PowerShell、macOS Terminal 与 Linux 终端均可用；它只显示核心工具、用户实际选择启用的模型和验证入口。密钥使用隐藏输入，不进入命令行历史。

## 初始化

Windows PowerShell 安装到用户目录后运行：

`python "$HOME\.codex\skills\produce-cinematic-video\scripts\configure.py" init`

macOS 或 Linux 安装到用户目录后运行：

`python3 "$HOME/.codex/skills/produce-cinematic-video/scripts/configure.py" init`

项目级安装或其他位置可运行：

`python <skill-dir>/scripts/configure.py init`

该命令从 `assets/.env.local.example` 创建用户配置。已有配置时默认拒绝覆盖；只有用户明确运行 `init --replace` 时才把旧文件归档为带时间戳的备份并写入新模板。

初始文件只含 FFmpeg 与 FFprobe。ImageMagick、远程 provider、IndexTTS2、Qwen3-TTS、交付覆盖项和调优参数都在实际需要时再添加；内部安全默认无需抄进用户文件。

从旧版迁移：

`python <skill-dir>/scripts/configure.py migrate`

迁移命令把旧 `config.json` 移动为带时间戳的归档，并生成 `.env.local`。它不会复制疑似明文密钥或旧凭据引用；先在提供方轮换已暴露密钥，再把新值填入 `.env.local`。

查看实际路径：

`python <skill-dir>/scripts/configure.py path`

显示脱敏配置（密钥只显示是否已设置）：

`python <skill-dir>/scripts/configure.py show`

预览精简后的配置键（不写文件、不显示密钥）：

`python <skill-dir>/scripts/configure.py compact`

确认列表后运行 `compact --confirm`。命令会先把当前 `.env.local` 归档，再只保留核心工具、已启用 provider、本地运行时及非默认安全策略；已存在规范字段时，也会归档并移除旧 `PCV_OPENAI_IMAGE2_*` 别名。不会静默丢弃未知字段。

安全更新一个非密钥值并自动归档上一版：

`python <skill-dir>/scripts/configure.py set PCV_FFMPEG /absolute/path/to/ffmpeg`

`set` 拒绝通过命令行写密钥，避免进入 shell 历史；密钥请私下编辑 `.env.local` 或由秘密管理器导出。

验证：

`python <skill-dir>/scripts/configure.py validate`

远程 provider 建议逐个使用本地交互向导配置，密钥由终端隐藏输入，不进入命令行历史、聊天或脚本日志：

```text
python <skill-dir>/scripts/configure.py setup-provider seedance
python <skill-dir>/scripts/configure.py setup-provider openai-image
python <skill-dir>/scripts/configure.py setup-provider gemini-image
```

一次只运行当前需要的一条。向导写入上述用户级 `.env.local`，自动归档上一版，并只显示 `<set; redacted>`。不要通过管道、重定向或远程聊天窗口输入密钥。

## 依赖安装

依赖分三层，不要把所有包混装到一个 Python：

1. **核心：** Python 3.10+、完整 FFmpeg、FFprobe；库存、contact sheet、转码和媒体 QC 依赖它们。
2. **按任务可选：** ImageMagick、Pillow、OpenCV、PySceneDetect、jsonschema，以及本地 TTS 音频链路建议使用的 SoX；静帧处理、视觉分析、镜头检测、完整 schema 校验或 Qwen/Index 音频处理时再安装。
3. **独立模型运行时：** IndexTTS2、Qwen3-TTS、Pocket TTS、LuxTTS、GPT-SoVITS/UVR5 及其 torch/CUDA/MPS 依赖，优先复用各自项目环境；不要为了其中一个模型改坏普通视频工作环境。详见 `references/index-tts2.md`、`references/qwen3-tts.md`、`references/lightweight-tts.md` 与 `references/audio-separation-and-sync.md`。
4. **可选研究桌面工具：** OmniGet 可由用户单独安装，用于合法样本的采集、字幕/Whisper、片段和时间戳笔记。它当前没有本 skill 可依赖的稳定外部 CLI/API，因此不增加 `PCV_OMNIGET_*` 配置；把用户明确导出的目录交给 `scripts/research_ingest.py`。详见 `references/creative-research-and-planning.md`。

常见系统安装入口：

- Windows：从 [FFmpeg 官方下载页](https://ffmpeg.org/download.html)选择完整 Windows build；从 [ImageMagick 官方下载页](https://imagemagick.org/download/)安装，并配置命令行 PATH；本地 TTS 需要时可运行 `winget install --id ChrisBagwell.SoX --exact`。不要使用 Playwright、浏览器或其他软件附带的精简 FFmpeg。
- macOS：已安装 Homebrew 时可运行 `brew install ffmpeg imagemagick sox`；Apple Silicon 和 Intel 都应在终端重新打开后检查实际路径。
- Debian/Ubuntu：可运行 `sudo apt install ffmpeg imagemagick sox libsox-fmt-all`；其他发行版使用其受信任的软件仓库。

可选 Python 包使用 skill 的清单安装到普通视频工作环境，不要装进 IndexTTS2 环境：

```text
python -m pip install -r <skill-dir>/requirements-optional.txt
```

Pillow 与 OpenCV 的平台差异以各自[官方安装说明](https://pillow.readthedocs.io/en/stable/installation/basic-installation.html)和[官方 Python 指南](https://docs.opencv.org/4.x/da/df6/tutorial_py_table_of_contents_setup.html)为准。

安装后先运行只读诊断：

```text
python <skill-dir>/scripts/environment_doctor.py
```

按任务收紧检查：

```text
python <skill-dir>/scripts/environment_doctor.py --require-imagemagick --require-vision --require-av-sync --require-scenedetect --require-schema --require-sox
```

诊断不会安装、下载或修改系统。缺少可选项只报告 `OPTIONAL`；被任务要求的项目缺失时返回失败。

使用自定义路径测试：

`python <skill-dir>/scripts/configure.py --config <path> validate`

## 配置优先级

按以下顺序解析：

1. 当前命令的显式参数；
2. 进程环境变量与 `CINEMATIC_VIDEO_ENV_FILE`；
3. 用户 `.env.local`；
4. skill 内安全默认值。

项目 manifest 可以收紧预算、披露或交付标准，但不要静默放宽用户级安全策略。项目要求与用户策略冲突时，采用更严格者并报告。

## 工具配置

以下 `.env.local` 变量映射可执行文件：

- `PCV_FFMPEG`：完整 FFmpeg，用于抽帧、分析、转码和 QC；
- `PCV_FFPROBE`：通常随完整 FFmpeg 安装；
- `PCV_IMAGEMAGICK`：可选 `magick` CLI，用于静帧合成、格式转换、标注和批处理；
- `PCV_PYTHON`：普通视频脚本环境；所有本地模型另用各自专用 Python；
- `PCV_SCENEDETECT`：可选镜头检测；
- `PCV_TRANSCRIBER`：可选带时间码转写；
- `PCV_NLE`：可选 Premiere、Resolve、Final Cut、Avid、Remotion 或其他编辑入口。

可写命令名（从 PATH 解析）或绝对路径。不要使用只有截图功能的精简 FFmpeg；运行 QC 前确认包含 ffprobe 以及 blackdetect、freezedetect、silencedetect、ebur128、scale 和 tile 等所需功能。

脚本从配置读取 ffmpeg/ffprobe，不修改系统 PATH。

Python 3.10+ 可运行全部标准库路径。Pillow 的 import 名为 `PIL`，OpenCV 的 import 名为 `cv2`；它们是视觉工作流可选项，当前 contact sheet 脚本直接使用 FFmpeg 的 `scale` 与 `tile`，不以 Pillow/OpenCV 作为隐式依赖。可选安装 `jsonschema` 以启用完整 JSON Schema 校验；未安装时仍执行时间线、预算、事实、权利与批准等语义检查，并明确标记 schema 检查未运行。

## 提供方配置

用户文件只添加真正启用的 provider。专用适配器已在 skill 内保存安全默认地址、adapter 与 capability，通常只需要启用开关和新密钥。

GPT Image 2 最小配置：

```dotenv
PCV_OPENAI_IMAGE_ENABLED=true
PCV_OPENAI_IMAGE_MODEL=gpt-image-2
PCV_OPENAI_IMAGE_API_KEY=填入新密钥
```

Gemini Nano Banana 最小配置：

```dotenv
PCV_GEMINI_IMAGE_ENABLED=true
PCV_GEMINI_IMAGE_ENDPOINT=https://中转地址/v1beta/models/实际模型:generateContent
PCV_GEMINI_IMAGE_MODEL=与端点路径一致的实际模型
PCV_GEMINI_IMAGE_API_KEY=填入新密钥
```

Seedance 中国区最小配置：

```dotenv
PCV_SEEDANCE_ENABLED=true
PCV_SEEDANCE_MODEL=doubao-seedance-2-0-260128
PCV_SEEDANCE_API_KEY=填入新密钥
```

对已启用 provider 显式保存模型 ID，便于检查和复现。Gemini 中转统一使用完整的 `PCV_GEMINI_IMAGE_ENDPOINT`，由向导从端点路径提取模型；其他 provider 只有地区根地址与内置默认不同才添加 `*_BASE_URL`。具体命令、输入限制和上传闸门见 `references/generative-image-providers.md` 与 `references/seedance-video.md`。

`PCV_AUDIO_*` **不是**本地 Qwen3-TTS 或 IndexTTS2 的前置配置。它只服务于用户自己接入的通用远程音频 API/tool；未使用该通道时不要写 `PCV_AUDIO_ENABLED`、adapter、model、base URL 或 API key，避免与本地 TTS 混淆。

旧项目或自定义 tool/MCP 仍可使用 `PCV_IMAGE_*`、`PCV_VIDEO_*`、`PCV_AUDIO_*` 三组通用变量构建内部能力注册表：

- `*_ENABLED`：是否允许选择；
- `*_ADAPTER`：环境中实际可调用的 tool、CLI 或 API 适配器标识；
- `*_TOOL_NAME`：若由 agent tool/MCP 提供，写真实名称；
- `*_BASE_URL` 与 `*_MODEL`：需要时填写；
- `*_CAPABILITIES`：逗号分隔的明确能力；
- `*_REMOTE_UPLOAD`、`*_REGION`：数据边界；
- `*_UNIT_COST`、`*_PRICING_CHECKED_AT`：估算与核对日期；
- `PCV_IMAGE_API_KEY`、`PCV_VIDEO_API_KEY`、`PCV_AUDIO_API_KEY`：通用 slot 的可选凭据，读取后只作为当前进程环境变量，不写入内部配置、日志或 provenance。

常用 capability：

- `text_to_image`、`image_edit`、`inpaint`、`outpaint`；
- `text_to_video`、`image_to_video`、`first_last_frame`、`video_extend`；
- `reference_identity`、`synchronized_audio`；
- `tts`、`voice_clone`、`emotion_control`、`voice_design`、`sound_effects`、`music`。
- `source_separation`、`dereverb`、`audio_mix`、`av_sync`。

不要把同一生态或相似 API 当成能力保证。任务前读取当前官方文档，确认输入互斥、参考图、时长、分辨率、音频、内容政策、数据保留和价格。

专用 `generate_image.py` 与 `seedance_video.py` 仅依赖 Python 标准库；不要求用户额外安装 OpenAI、Google 或火山 SDK。Dry-run 可在未启用、未填密钥时验证路由。真实调用仍必须启用 provider，并显式确认远程上传和成本。

如果当前 agent 环境没有与其他 `adapter` 对应的工具或客户端，报告缺失并停在计划阶段；不要臆造调用。

本地 IndexTTS2 使用 `index_tts2_local` adapter。用户只需配置启用开关、`PCV_INDEX_TTS2_PYTHON`、`PCV_INDEX_TTS2_REPO_DIR` 与 `PCV_INDEX_TTS2_MODEL_DIR`；模板默认禁用、离线且 GPU 优先自动选设备。先运行 `scripts/index_tts2.py doctor --runtime-import` 确认实际 CUDA/XPU/MPS/CPU，再使用已获同意的短音频做真实 smoke test。具体字段、Windows/macOS 路径和情感参数见 `references/index-tts2.md`。

本地 Qwen3-TTS 使用 `qwen3_tts_local` adapter。只做声音设计时仅添加 `PCV_QWEN3_TTS_ENABLED`、`PCV_QWEN3_TTS_PYTHON` 与 `PCV_QWEN3_TTS_VOICE_DESIGN_MODEL`；CustomVoice 或克隆需要时再分别添加对应模型目录。默认设备同样 GPU 优先，能力由已配置的模型自动派生，不要求用户维护 capability 或设备列表。详见 `references/qwen3-tts.md`。

低配设备本地 TTS 有两个独立 slot：

```dotenv
# CPU 优先；只填写实际启用的一组。当前不支持中文。
PCV_POCKET_TTS_ENABLED=true
PCV_POCKET_TTS_PYTHON=<runtime-python>
PCV_POCKET_TTS_LANGUAGE=english

# 或：低显存 / CPU 48 kHz 克隆候选
PCV_LUX_TTS_ENABLED=true
PCV_LUX_TTS_PYTHON=<runtime-python>
PCV_LUX_TTS_REPO_DIR=<LuxTTS-repository>
PCV_LUX_TTS_MODEL=YatharthS/LuxTTS
```

不要同时照抄两组；按语言、设备和已批准的角色声音启用一个。Pocket 固定 CPU 优先并阻止中文；LuxTTS 的 `device=auto` 走 CUDA → Apple MPS → CPU，但语言必须先 audition。两者默认离线，首次模型下载需要命令同时带 `--no-offline --allow-network`，reference voice 仍只允许本地文件。详见 `references/lightweight-tts.md`。

本地 GPT-SoVITS 的 UVR5 用于人声/伴奏分离、去混响与去回声。一般只需配置一次安装目录：

```text
python <skill-dir>/scripts/configure.py setup-local gpt-sovits --repo-dir <GPT-SoVITS目录>
python <skill-dir>/scripts/configure.py validate --capability source_separation
python <skill-dir>/scripts/gpt_sovits_uvr5.py doctor --runtime-import
```

向导只写 `PCV_GPT_SOVITS_ENABLED` 和 `PCV_GPT_SOVITS_REPO_DIR`。它会优先复用 `<repo>/runtime/python`，并由该运行时的 Torch 自动选择 CUDA；只有非标准安装或排错时才添加 `PCV_GPT_SOVITS_PYTHON` / `PCV_GPT_SOVITS_DEVICE`。不要把 GPT-SoVITS 的锁定依赖安装进普通视频脚本环境。

## 密钥与隐私

`.env.local` 本身是仅供当前用户读取的秘密文件，不是可分享的普通配置。也可以完全不在文件中写密钥，而是在 shell、CI secret 或密码管理器中导出同名 `PCV_*_API_KEY`；进程环境变量优先。配置验证只检查是否存在，不打印值。

创建后应确保：文件位于用户配置目录而非项目目录；macOS/Linux 权限为 `0600`；项目 `.gitignore` 包含 `.env*`；备份、截图、日志、聊天和报错中不出现真实值。

禁止：

- 在 SKILL.md、manifest、edit plan、prompt、provenance、日志或终端摘要中写明文密钥；
- 把未授权私密素材上传到远程提供方；
- 在错误消息中回显 Authorization header、signed URL 或完整请求；
- 为“方便”把密钥复制进项目仓库。

若密钥曾写进 `*_ENV` 字段、被 `show`/验证输出、粘贴到聊天、提交到版本库或进入日志，立即停止远程调用；先在提供方吊销并轮换，再清理本地配置。仅从文件中删除旧值不能使已暴露凭据重新安全。

## 预算与发布策略

`policy` 定义：

- 默认币种和项目生成软预算；
- 超预算是否必须重新批准；
- 远程上传、人物/声音克隆、合成纪录内容的默认许可；
- 是否保留生成 provenance；
- 是否必须在外部发布前再次确认。

价格会变化。`pricing` 只用于预估；调用前核对并把估算、批准和实际成本写入 gap。没有价格信息时不能把成本填成 0。

任何外部发布或发送都需要用户明确授权，即使 `require_publish_approval` 被错误关闭；skill 的硬闸门优先。

## 交付 profile

`delivery_profiles` 保存可复用技术目标：

- raster、aspect、fps policy；
- video codec、profile、pixel format、color space；
- audio codec、sample rate、channels、integrated loudness 与 true peak；
- captions、metadata、naming 和 QC 容差。

模板提供 review、web-horizontal、web-vertical、mezzanine 示例。它们不是官方平台保证。复制成项目 profile 前，根据合同和当前平台官方规格调整。

若 `fps` 为 `source`，保留主要摄影帧率；混合帧率时在 ingest 决定 conform 策略。不要只为“更顺”把 24/25 fps 叙事母版随意转成 30/60 fps。

## 验证和排错

`configure.py validate` 检查：

- JSON 和配置版本；
- 必需 section 和字段类型；
- 工具是否可解析；
- enabled provider 的 adapter、capability、模型/工具和秘密环境变量；
- 配置中是否疑似出现明文秘密；
- delivery profile 的基本一致性。

常见问题：

| 症状 | 处理 |
|---|---|
| 找不到 `.env.local` | 运行 `path`，检查 `CINEMATIC_VIDEO_ENV_FILE`，再执行 `init` |
| 仍在使用 `config.json` | 运行 `configure.py migrate`，轮换任何曾被打印的密钥 |
| 找不到 ffprobe | 安装完整 FFmpeg，或在 `tools.ffprobe` 填绝对路径 |
| FFmpeg 缺滤镜 | 替换精简 build；不要把未运行检查标成通过 |
| 本机有 GPU 但 TTS 选到 CPU | 用对应专用 Python 运行 `doctor --runtime-import`；安装与驱动匹配的 GPU 版 Torch，而不是只改设备字符串 |
| TTS 显存不足 | 缩短文本/分段、关闭未经测试的加速项或换较小模型；用户明确决定后才固定 CPU |
| 电脑没有可用 GPU | 支持的欧洲语言优先 Pocket TTS；需要 48 kHz 克隆可试听 LuxTTS CPU；中文继续用 Qwen3/Index 的可用运行环境或远程授权方案 |
| Pocket TTS 收到中文 | 不绕过语言闸门；改走 Qwen3-TTS 或 IndexTTS2 |
| LuxTTS 语言效果未知 | 先生成短 audition，做人工听辨与 ASR 回验；没有批准记录不进正式时间线 |
| provider disabled | 配置 `enabled`、adapter、model/tool、capabilities 和环境变量 |
| 能力不匹配 | 换已声明 capability 的 slot，或改用本地/确定性方案 |
| 预算未知 | 核对当前价格，写估算和批准后再调用 |
| schema 失败 | 不绕过；修 config、manifest 或 edit plan，并保留报告 |

配置只解决“如何调用”和“允许调用什么”，不替代用户对创意、事实、权利和发布的授权。
