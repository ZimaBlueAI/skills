# IndexTTS2 情感声音克隆

## 目录

- [能力边界](#能力边界)
- [独立运行环境](#独立运行环境)
- [用户配置](#用户配置)
- [检查](#检查)
- [生成](#生成)
- [情感控制](#情感控制)
- [模型布局兼容](#模型布局兼容)
- [多角色配音与合体祝福（voice bank）](#多角色配音与合体祝福voice-bank)
- [同意披露与验收](#同意披露与验收)

## 能力边界

`scripts/index_tts2.py` 是控制层，使用 skill 所在的普通 Python；`scripts/index_tts2_runner.py` 由用户配置的 IndexTTS2 专用 Python 启动。这样 torch、CUDA/MPS 和模型依赖不会污染 Codex 或视频工具环境。

适配器支持：

- 单一说话者参考音频的零样本声音克隆；
- 独立的情感参考音频；
- 8 维情感向量，固定顺序为 `happy, angry, sad, afraid, disgusted, melancholic, surprised, calm`；
- 从台词本身推断情感，或使用独立的自然语言情感描述；
- Windows CUDA/CPU、macOS MPS/CPU，以及官方构造器公开的 XPU 设备；
- 离线模式、官方新版 `hf_cache` 与既有旧式辅助模型目录；
- 非覆盖式 WAV 输出和自动 provenance sidecar。

不宣称未由当前官方推理接口启用的精确时长控制。对嘴、广播交付和最终时长仍需在 NLE/DAW 中实测、剪辑或做获批的轻微时长适配。

## 独立运行环境

不要把 IndexTTS2 的大型依赖安装进 skill 目录。按 [IndexTTS 官方仓库](https://github.com/index-tts/index-tts)当前说明使用 `git-lfs` 与 `uv` 创建项目级 `.venv`：

```text
git clone https://github.com/index-tts/index-tts.git
cd index-tts
git lfs pull
uv sync --all-extras
```

Windows 上如果 DeepSpeed、flash-attn 或 Triton 不兼容，先用不含对应 extra 的官方基础环境，并让配置中的加速项保持 `false`。只有运行过官方 GPU 检查和一条短样本后再逐项启用 FP16、CUDA kernel、DeepSpeed、accel 或 torch compile。

专用 Python 一般位于：

- Windows：`<index-tts>\.venv\Scripts\python.exe`
- macOS/Linux：`<index-tts>/.venv/bin/python`

代码和模型的许可彼此独立，也可能变化。使用、分发或商用前读取当前官方仓库 `LICENSE` 与模型许可；skill 不包含官方源码、权重或它们的许可授权。

运行 `python <skill-dir>/scripts/configure.py paths` 可查看本系统推荐的 `runtimes_dir` 与 `models_dir`。新安装可把官方仓库放在 `runtimes_dir/index-tts`，把权重放在 `models_dir/IndexTTS-2`；已有模型无需移动，直接在用户配置写绝对路径即可。

## 用户配置

先运行 `scripts/configure.py init`，然后只把必填项加入用户级 `.env.local`：

```dotenv
PCV_INDEX_TTS2_ENABLED=true
PCV_INDEX_TTS2_MODEL=IndexTTS-2
PCV_INDEX_TTS2_PYTHON=/absolute/path/to/index-tts/.venv/bin/python
PCV_INDEX_TTS2_REPO_DIR=/absolute/path/to/index-tts
PCV_INDEX_TTS2_MODEL_DIR=/absolute/path/to/IndexTTS-2_models
```

可选的运行时兼容键（仅在需要时添加）：

```dotenv
# 显式指定 HF 辅助模型缓存目录。不设置时自动探测：
# <model_dir>/hf_cache → <repo_dir>/checkpoints/hf_cache，并以绝对路径注入
# HF_HUB_CACHE，规避部分 IndexTTS2 检出版本里 cwd 相对缓存路径的问题。
PCV_INDEX_TTS2_HF_CACHE_DIR=/absolute/path/to/hf_cache
# Windows 上 numba/LLVM 崩溃（LLVM ERROR: Symbol not found: __svml_cosf8_ha）时
# 设为 generic 强制使用可移植 CPU 特征；适配器会同时停用 SVML，
# 并为每次隔离运行使用全新 Numba 缓存，避免复用含旧 SVML 符号的对象。
PCV_INDEX_TTS2_NUMBA_CPU_NAME=generic
```

适配器还会向专用运行时自动注入 `INDEXTTS_MODEL_DIR=<model_dir>`（部分社区检出版本用它定位本地 w2v-bert 等辅助模型），并在 `offline: true` 时注入 `HF_HUB_OFFLINE=1` 与 `TRANSFORMERS_OFFLINE=1`。

`model`、设备、离线策略、FP16、CUDA kernel、DeepSpeed、accel、torch compile 和情感默认值已有内部安全默认，不要全部抄进用户文件。Windows 路径推荐使用 `/`，例如 `C:/Tools/index-tts/.venv/Scripts/python.exe`；无需 JSON 双反斜杠。

默认 `device=auto` 是 GPU 优先：依次选择可用的 CUDA、XPU、Apple MPS，最后才使用 CPU。`doctor --runtime-import` 会显示实际选择和设备名。只有需要固定多卡编号或排错时才加 `PCV_INDEX_TTS2_DEVICE=cuda:0`、`mps`、`xpu` 或 `cpu`；显式设备不可用时适配器会报错，不会静默回落。FP16、CUDA kernel、DeepSpeed、accel 与 torch compile 仍保持保守默认，只有当前官方环境和短样本实测通过后才逐项加入；CPU 不允许启用 FP16。

默认 `offline: true`，防止生成时意外下载或上传。若模型辅助文件不完整，先由用户在受控安装步骤中补齐，不要让生产任务静默联网。只有用户把 `offline` 显式改成 `false` 且在单次命令加入 `--allow-network` 时，控制层才允许官方运行时获取缺失的辅助模型；这仍不授权上传参考音频。

## 检查

结构检查不加载权重：

```text
python <skill-dir>/scripts/index_tts2.py doctor
```

再检查专用运行时能否导入官方类，仍不加载权重：

```text
python <skill-dir>/scripts/index_tts2.py doctor --runtime-import
```

输出中的 `selected_device`、CUDA 设备名及 MPS/XPU 状态来自 IndexTTS2 专用 Python。最后用已获同意的短参考音频和一句非敏感文本做真实 smoke test。真实测试会加载模型，可能占用大量显存/内存；显存不足时先降低可选加速、缩短文本或换小模型，只有用户明确决定后才改用 CPU，不自动把一次长任务重跑两遍。

## 生成

优先把长文本放在 UTF-8 文件中，避免出现在 shell 历史或进程参数：

```text
python <skill-dir>/scripts/index_tts2.py synthesize --text-file script.txt --speaker-reference speaker.wav --output take-001.wav --consent-record RELEASE-2026-001 --dry-run
```

确认 dry-run 的模型、设备、输入和新输出路径后，去掉 `--dry-run` 执行。适配器拒绝覆盖现有 WAV 或 sidecar，并生成 `take-001.wav.provenance.json`，记录同意编号、输入和输出校验和、模型、参数、合成披露以及情感模式。

## 情感控制

四种显式情感方式互斥；不提供时沿用说话者参考音频的情感：

- `--emotion-reference emotion.wav`：用另一条音频提供情感风格；
- `--emotion-vector "0,0,0.8,0,0,0,0,0"`：8 维显式向量；
- `--emotion-text "克制地焦虑，努力不惊动别人"`：独立文字描述；
- `--use-script-emotion`：从要合成的台词推断。

`--emotion-alpha 0..1` 控制影响强度。文本情感默认 `0.6`，是起始点而不是质量保证；每个角色和场景都要盲听 A/B。`--random` 会增加随机性，也可能降低声音克隆相似度，默认关闭。

每次只改变一个变量；先锁定清晰度、读音和角色身份，再调情感。情感强度不能替代表演方向、标点、停顿、分句和呼吸设计。

## 模型布局兼容

适配器接受模型文件直接位于 `model_dir`，或位于 `model_dir/checkpoints`。主文件至少包含 `config.yaml`、`gpt.pth`、`s2mel.pth`、`bpe.model`、`wav2vec2bert_stats.pt`、`feat1.pt` 和 `feat2.pt`。

辅助模型可使用：

- 官方新版 `model_dir/hf_cache` 平铺布局；
- 既有 `w2v-bert-2.0`、`MaskGCT`、`campplus`、`bigvgan_v2_22khz_80band_256x` 目录布局；
- `runtime.aux_paths` 显式映射。

文本情感还需要 `qwen0.6bemo4-merge`。`doctor` 只检查结构与导入；只有真实 smoke test 能证明权重、torch、GPU/MPS 和音频链路完整。

## 多角色配音与合体祝福（voice bank）

把片中多个角色的台词换成另一种语言（配音），或让多个克隆声线共同说一段祝福/口号时，按 voice bank 约定组织项目：

```
<project>/work/tts/
├── refs/               # 每个角色一个参考音（角色名.wav）
│   ├── role_a.wav
│   └── role_b.wav
├── dub/                # 合成输出（一句一个 wav + provenance sidecar）
├── voice-roles.json    # 角色表：assets/voice-roles.template.json 复制而来
└── consent-record.md   # 本次克隆的用途、来源、披露说明（--consent-record 指向它）
```

工序：

1. **提参考音**：用词级 ASR（或人工听）在源素材里为每个角色找 1.5–10 秒的单人干净语句，`ffmpeg -ss <in> -to <out> -ar 24000 -ac 1` 抽成 `refs/<role>.wav`。同一片段既当音色参考也当情感参考，最贴近原角色状态。
2. **填角色表**：`voice-roles.json` 里给每个角色记 `ref`、台词列表（每句含 `text`、时间线落点 `at_s`、可选 `emotion_text`）。
3. **逐句合成**：每句调用一次 `synthesize`，`--speaker-reference refs/<role>.wav`，输出到 `dub/`。跨语言克隆（如英文参考音合成中文台词）是支持的。
4. **合体祝福 / 齐声**：同一句文本用每个角色各合成一遍，混音时同一时刻叠放（各路先 `loudnorm`，合唱层每路降 5–6 dB 再叠）。
5. **上时间线**：每句配音先 `loudnorm=I=-18:TP=-1.5:LRA=7` 统一响度（克隆输出会继承参考音的响度，逐条差异可达 15 dB），再 `adelay` 落位；原声在配音窗内压至 20–30%；音乐用 sidechaincompress 以配音总线为 key。**注意 FFmpeg 滤镜图标签只能消费一次：配音总线要 `asplit` 成 duck key 与终混两路，否则第二处引用会静默变成无声。**

时长对位：IndexTTS2 不承诺精确时长，先合成再量长度，必要时微调台词字数或允许 J/L cut 溢出镜头边界，禁止靠变速拉伸超过 ±10%。

## 同意披露与验收

生成命令强制要求 `--consent-record`，但这个字段不能代替真实授权。记录说话者、允许用途、地域、期限、语言、角色、撤回流程和是否允许广告/再训练；不要克隆公众人物、未成年人、未授权个人或敏感对象去表达其未说内容。

验收至少包括：

1. 台词逐字正确，专名、数字、语气和限定词无误；
2. 音色相似但没有不自然的吞字、金属感、重复呼吸或情感漂移；
3. 情感与剧情、人物弧线、镜头距离和空间一致；
4. WAV 头尾、峰值、底噪、点击声、采样率和时长可用；
5. 与画面同步后再次检查，不以单独听感代替成片验收；
6. 观众可理解的合成披露、字幕、provenance 和撤回记录齐全。
