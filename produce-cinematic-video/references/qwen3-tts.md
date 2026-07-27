# Qwen3-TTS 声音设计与本地合成

## 目录

- [能力分工](#能力分工)
- [独立运行环境](#独立运行环境)
- [最小配置](#最小配置)
- [检查](#检查)
- [声音设计](#声音设计)
- [预置音色](#预置音色)
- [声音克隆](#声音克隆)
- [安全与验收](#安全与验收)

## 能力分工

Qwen3-TTS 官方模型按任务拆分，不能用一个 checkpoint 假装覆盖全部能力：

- `VoiceDesign`：从自然语言描述创造新音色与表演；
- `CustomVoice`：使用官方预置 speaker，并用 instruction 控制语气；
- `Base`：从已获同意的参考音频做声音克隆。

`scripts/qwen3_tts.py` 是轻量控制层，`scripts/qwen3_tts_runner.py` 由 Qwen3-TTS 专用 Python 启动。三种任务均采用非覆盖 WAV、离线优先、脱敏 dry-run 和 provenance。声音设计不应以真实人物姓名作为提示；声音克隆必须提供 consent record。

## 独立运行环境

按 [Qwen3-TTS 官方仓库](https://github.com/QwenLM/Qwen3-TTS)建议使用干净的 Python 3.12 环境：

```text
conda create -n qwen3-tts python=3.12 -y
conda activate qwen3-tts
pip install -U qwen-tts
```

不要把 Qwen3-TTS、Torch、FlashAttention 安装进 skill 或 IndexTTS2 环境。确保该专用环境安装的是与本机驱动匹配的 GPU 版 Torch；“机器有 NVIDIA GPU”不等于这个 Python 能看到 CUDA。仅在兼容的 CUDA、dtype 和显存条件下安装/启用 FlashAttention 2；默认 attention 为 `auto`，不要求用户填写。Qwen 的音频加载链路还建议安装系统 SoX，安装方法见 `references/configuration.md`。

模型可从官方 Hugging Face/ModelScope 下载到用户数据目录。生产配置默认 `offline=true`，因此填写本地模型目录，不在合成时静默下载权重。

## 最小配置

只添加实际使用的任务。仅做声音设计时，`.env.local` 只需：

```dotenv
PCV_QWEN3_TTS_ENABLED=true
PCV_QWEN3_TTS_PYTHON=C:/absolute/path/to/qwen3-tts/python.exe
PCV_QWEN3_TTS_VOICE_DESIGN_MODEL=D:/models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

使用官方预置音色时再添加：

```dotenv
PCV_QWEN3_TTS_CUSTOM_VOICE_MODEL=D:/models/Qwen3-TTS-12Hz-1.7B-CustomVoice
```

需要经授权的声音克隆时再添加：

```dotenv
PCV_QWEN3_TTS_BASE_MODEL=D:/models/Qwen3-TTS-12Hz-1.7B-Base
```

内部默认值为 `device=auto`、`dtype=auto`、`attention=auto`、`offline=true`、`language=Auto`。`auto` 是 GPU 优先：依次选择可用的 CUDA、XPU、Apple MPS，最后才使用 CPU；CUDA 自动选择支持的 BF16，否则使用 FP16，MPS 使用 FP16，CPU 使用 FP32。只有排错或经过 smoke test 的固定硬件策略才添加 `PCV_QWEN3_TTS_DEVICE`、`PCV_QWEN3_TTS_DTYPE`、`PCV_QWEN3_TTS_ATTENTION` 或 `PCV_QWEN3_TTS_OFFLINE`，普通用户不必填写。

显式指定 `cuda:0`、`mps` 或 `xpu` 时，适配器会验证该设备是否真的可用；不可用就清晰报错，不会悄悄回落到 CPU。遇到显存不足也不要自动重复一遍长任务：先缩短文本、关闭额外加速、换较小模型，或由用户明确改用 CPU。

## 检查

不加载权重的路径检查：

```text
python <skill-dir>/scripts/qwen3_tts.py doctor
```

再检查专用环境能否导入官方类，仍不加载权重：

```text
python <skill-dir>/scripts/qwen3_tts.py doctor --runtime-import
```

输出中的 `selected_device`、`selected_dtype`、CUDA 设备名及 MPS/XPU 状态就是该专用 Python 的真实选择。只有在确认设备、时间窗口和模型目录后，才用一句非敏感文本做真实 smoke test；正式 provenance 会同时记录请求值与实际设备/dtype。

## 声音设计

声音设计 instruction 按以下顺序写：

`角色功能 → 非身份化音色 → 语言/口音 → 说话对象与距离 → 节奏和停顿 → 情绪弧 → 强调词 → 禁止偏差`

不要只写“温柔、电影感”。可验收示例：

```text
一位温暖、明亮的成年女性讲述者，普通话自然清晰，不模仿任何真实人物。
像在近距离给亲友送上祝福，开头带惊喜，中段放慢并真诚，最后一句轻轻上扬。
语速中等，句间有呼吸，不使用播音腔、幼儿腔、夸张尖声或广告式兴奋。
```

运行：

```text
python <skill-dir>/scripts/qwen3_tts.py design --text-file script.txt --instruction "..." --language Chinese --output voice-design-001.wav --dry-run
```

确认 dry-run 后去掉 `--dry-run`。提示中不写在世艺术家、演员、公众人物或私人个体姓名；把目标拆成可听属性。

## 预置音色

使用 `CustomVoice` 时，先通过官方 demo/API 查询当前模型支持的 speaker，不把旧列表写成永久保证：

```text
python <skill-dir>/scripts/qwen3_tts.py custom --text-file script.txt --speaker Vivian --instruction "克制而开心，结尾有微笑感" --language Chinese --output custom-001.wav --dry-run
```

0.6B 与 1.7B 对 instruction 的支持可能不同，以当前官方模型和运行时返回为准。

## 声音克隆

优先同时提供参考音频及其准确逐字稿：

```text
python <skill-dir>/scripts/qwen3_tts.py clone --text-file script.txt --reference-audio speaker.wav --reference-text-file speaker.txt --consent-record RELEASE-2026-001 --language Chinese --output clone-001.wav --dry-run
```

`--x-vector-only` 可省略参考逐字稿，但官方说明相似度/质量可能下降。不得克隆未成年人、公众人物、未授权个人或敏感对象来表达其未说内容。

## 安全与验收

- `.env.local` 只保留用户真实启用的 Qwen 变量；不需要的模型路径不要列。
- 默认离线；只有显式 `PCV_QWEN3_TTS_OFFLINE=false` 且单次命令加入 `--allow-network` 才允许解析远程模型 ID。
- VoiceDesign 是合成音色，不等于取得某个真实人的人格、身份或授权。
- 验收逐字内容、专名、停顿、年龄感、音色稳定、情绪弧、金属感、重复呼吸、峰值、头尾和与画面的同步。
- 正式输出保留模型、任务类型、instruction、参考校验和、consent record、输出校验和与受众可理解的合成披露。
