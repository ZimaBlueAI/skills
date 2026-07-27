# 低配设备 TTS：Pocket TTS 与 LuxTTS

## 目录

- [定位与路由](#定位与路由)
- [独立安装](#独立安装)
- [配置与 doctor](#配置与-doctor)
- [安全合成](#安全合成)
- [版本与能力边界](#版本与能力边界)

## 定位与路由

这两个 provider 是本地低资源补充，不替代中文情感配音主路径。

| 任务 | 首选 |
|---|---|
| 中文、自由音色设计、明确情绪导演 | Qwen3-TTS VoiceDesign |
| 中文、经授权的声音克隆与情感参考 | IndexTTS2 或 Qwen3-TTS Base |
| 无可用 GPU，英语/法语/德语/葡萄牙语/意大利语/西班牙语 | Pocket TTS |
| 低显存或 CPU、需要 48 kHz 克隆候选 | LuxTTS，先做语言专项试听 |

Pocket TTS 当前官方语言列表不含中文。适配器检测到中文字符会停止，而不是生成不可用的替代音频。LuxTTS 上游没有发布语言矩阵；任何语言都必须先生成 audition，做人工听辨和 ASR 回验，再批准进入正式剪辑。已批准某一角色声音后，不因机器变慢而自动换 provider；先生成 A/B，重新确认角色连续性。

## 独立安装

不要把两者安装进普通视频脚本、Qwen3-TTS 或 IndexTTS2 环境。

### Pocket TTS

官方要求 Python 3.10–3.14、PyTorch 2.5+，不需要 GPU 版 PyTorch：

```text
python -m venv <runtime-dir>/pocket-tts
<runtime-python> -m pip install --upgrade pip
<runtime-python> -m pip install pocket-tts
```

Pocket TTS 是 CPU 优先路径，默认限制为 2 个 CPU 线程。当前官方 API 暴露 `quantize` 时可在命令中使用 `--quantize`；先通过 doctor 检查安装版本是否真的支持，不能只凭文档假设。

最小 `.env.local`：

```dotenv
PCV_POCKET_TTS_ENABLED=true
PCV_POCKET_TTS_PYTHON=<runtime-python>
PCV_POCKET_TTS_LANGUAGE=english
```

如果是源码 editable 安装，才添加 `PCV_POCKET_TTS_REPO_DIR`。通常不需要设备、线程、离线或量化字段。

### LuxTTS

官方当前安装方式是检出仓库并安装其锁定依赖：

```text
git clone https://github.com/ysharma3501/LuxTTS.git
cd LuxTTS
python -m venv .venv
<runtime-python> -m pip install --upgrade pip
<runtime-python> -m pip install -r requirements.txt
```

最小 `.env.local`：

```dotenv
PCV_LUX_TTS_ENABLED=true
PCV_LUX_TTS_PYTHON=<runtime-python>
PCV_LUX_TTS_REPO_DIR=<LuxTTS-repository>
PCV_LUX_TTS_MODEL=YatharthS/LuxTTS
```

`device=auto` 按 CUDA → Apple MPS → CPU 路由；CPU 默认 2 线程。上游 README 同时展示 MPS 用法和仍待发布的 MPS roadmap 项，因此必须以本机 `doctor --runtime-import` 和真实 audition 为准，不承诺未测试的 MPS 可用性。若模型已放在本地，把 `PCV_LUX_TTS_MODEL` 改为其目录。

## 配置与 doctor

也可用跨平台 TUI，仅会询问启用 provider 必需的值：

```text
python <skill-dir>/scripts/configure.py tui
```

检查 Pocket：

```text
python <skill-dir>/scripts/lightweight_tts.py --engine pocket doctor --runtime-import
```

检查 LuxTTS：

```text
python <skill-dir>/scripts/lightweight_tts.py --engine lux doctor --runtime-import
```

Doctor 只导入包和检查方法签名，不加载权重、不合成、不联网。Pocket 报告固定为 CPU；LuxTTS 报告其专用 Python 实际看到的 CUDA/MPS/CPU，不能用宿主系统的 GPU 信息代替。

## 安全合成

两条路径都只接受本地 reference file，拒绝 URL 与 `hf://` 说话人引用，拒绝覆盖已有输出，并要求非空 `--consent-record`。Pocket 接受本地 WAV、MP3 或已导出的 safetensors voice state；LuxTTS 接受 WAV/MP3，参考音频至少 3 秒。

Pocket 示例：

```text
python <skill-dir>/scripts/lightweight_tts.py --engine pocket synthesize --text-file script.txt --speaker-reference approved-speaker.wav --consent-record releases/speaker-consent.md --output takes/pocket-take-01.wav
```

LuxTTS audition：

```text
python <skill-dir>/scripts/lightweight_tts.py --engine lux synthesize --text-file audition.txt --language English --speaker-reference approved-speaker.wav --consent-record releases/speaker-consent.md --output takes/lux-audition-01.wav
```

默认离线。首次拉取公开模型权重必须同时打开两道闸门：

```text
... synthesize --no-offline --allow-network ...
```

这只授权该次模型下载；reference voice 仍是本地路径，不上传到远程推理服务。缓存完成后恢复默认离线调用。

每次成功生成都写不可覆盖的 `.provenance.json`，包含文本哈希、reference 哈希、consent record、模型/包版本、实际设备、参数、输出哈希和披露说明，不保存正文。正式 take 还要：

1. 用 10–20 秒 audition 检查音色、口音、专名、数字和情绪；
2. 用 ASR 回验台词并人工核对，错读则重做，不用音乐遮盖；
3. LuxTTS 记录“语言专项试听已批准”，因为上游没有语言矩阵；
4. 与画面逐句对齐，再做 EQ、去齿音、动态和空间；
5. 不克隆未成年人、公众人物或任何未明确授权者来表达其未说内容。

## 版本与能力边界

- Pocket TTS 官方仓库：<https://github.com/kyutai-labs/pocket-tts>
- Pocket TTS Python API：<https://kyutai-labs.github.io/pocket-tts/API%20Reference/python-api/>
- LuxTTS 官方仓库：<https://github.com/ysharma3501/LuxTTS>

上游模型、voice catalog、语言、许可证与参数会变化。发布前重新核对当前官方说明和所用 voice/model 的许可证；本 reference 只定义安全调用和项目验收流程。
