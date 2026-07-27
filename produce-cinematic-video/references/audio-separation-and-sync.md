# 音源分离、混音与声画同步

## 目录

- [能力边界](#能力边界)
- [GPT-SoVITS UVR5](#gpt-sovits-uvr5)
- [分离流程](#分离流程)
- [音量与动态](#音量与动态)
- [口型与对白定位](#口型与对白定位)
- [验收](#验收)

## 能力边界

分离模型输出是估计值，不是原始多轨。人声残留、音乐空洞、瞬态损伤、相位和混响伪影都要试听。保留原音、模型、权重、参数、输出和拒绝原因。

常见目标分开处理：

- vocals / accompaniment：主唱或说话声与其余声音；
- dialogue / background：对白与音乐、环境和效果；
- dereverb / de-echo：减少混响或延迟；
- music stems：鼓、贝斯、其他、歌声；
- noise reduction：稳态噪声、风噪、爆音或电流声。

一个模型不保证同时做好所有目标。没有相应权重时不要把“非人声”标成“纯音乐”或“完整音效”。

## GPT-SoVITS UVR5

本地适配器读取用户 `.env.local`：

```dotenv
PCV_GPT_SOVITS_ENABLED=true
PCV_GPT_SOVITS_REPO_DIR=/absolute/path/to/GPT-SoVITS
```

Windows 整合包会自动优先使用 `<repo>/runtime/python.exe`；其他安装使用当前 Python。只有无法自动发现时才添加 `PCV_GPT_SOVITS_PYTHON`。不要把模型权重复制进 skill。

配置向导：

```text
python <skill-dir>/scripts/configure.py setup-local gpt-sovits
python <skill-dir>/scripts/gpt_sovits_uvr5.py doctor --runtime-import
```

设备默认为 `auto`：CUDA 可用时用 CUDA，否则 CPU。半精度只在 CUDA 上启用。`doctor` 必须报告实际设备，不能仅凭主机装有显卡宣称 GPU 已启用。

当前适配器可使用安装中已有的 UVR5 `.pth`、RoFormer `.ckpt` 和 onnx dereverb 权重。多乐器 stems 只有在权重本身声明对应 target instruments 时才成立；否则使用单独安装的 Demucs 或补充兼容 RoFormer 权重。

## 分离流程

1. 从视频无损提取 48 kHz 工作音频，保留源时间轴。
2. 先对 10–30 秒代表段做模型 A/B，不直接跑全片。
3. 按目标选择 vocals、accompaniment、dereverb 或 instrument 模型。
4. 输出到新目录，写 provenance；禁止覆盖源文件。
5. 试听齿音、瞬态、尾音、混响、音乐中心声像和残留。
6. 需要时串联两次处理，但每次都保留中间版本。
7. 将采用 stem 从同一时间起点导出，叠加后验证时长、相位和同步。

示例：

```text
python <skill-dir>/scripts/gpt_sovits_uvr5.py separate input.wav \
  --model HP2_all_vocals --output-dir work/stems
```

## 音量与动态

混音先平衡，再母带化。用 dB 自动化而不是固定百分比：

- dialogue：可懂度、语气和距离优先；
- ambience：建立空间，跨剪辑连续；
- effects：关键动作清楚但不抢对白；
- music：支持结构，在对白频段和动态上让位。

使用 `scripts/mix_stems.py` 为各 stem 设置 gain，并可对音乐/环境启用对白 side-chain ducking。默认值只是审听起点，不是交付标准。完成后重新测 integrated loudness、LRA、true peak、相位和小扬声器折叠。

## 口型与对白定位

准确定位分四层：

1. 镜头/人物层：用画面理解或人工标注确认可见说话人、遮挡、侧脸和切换；
2. 活动层：用 OpenCV 估计下半脸/嘴部运动曲线；
3. 音频层：提取人声能量、VAD 和 ASR 字词时间码；
4. 对齐层：在限制搜索窗内比较嘴部活动与语音包络，再由 forced alignment 和逐句审片确认。

`scripts/av_sync_align.py` 输出全局偏移、候选口型窗口、相关度和置信度。它不能仅凭嘴部运动可靠识别具体音素；低置信度、动画夸张口型、遮挡、无声张嘴、画外音和快速切镜必须人工处理。

若使用远程多模态模型理解画面，先取得私有媒体上传授权；优先发送低分辨率 contact sheet 和必要时间段，而不是整片。模型只负责候选说话人与事件定位，最终同步由本地信号、字词时间码和实时播放确认。

## 验收

- 原音与每个 stem 都可追溯、可单独播放；
- stems 从同一起点导出，叠加不漂移；
- 人声没有水下、金属、门限抽吸和断尾；
- 可见发音起始、爆破音、闭唇音和句尾落点可信；
- 对白与音乐的自动化能解释，重要台词不被遮蔽；
- 响度和 true peak 符合当前 delivery profile；
- 仅把人工实时审听过的版本标为 `approved`。
