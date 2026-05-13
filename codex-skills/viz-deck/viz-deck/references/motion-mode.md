# motion-mode: 动画 + MP4/GIF 视频导出协议

> v2 新增。viz-deck 的第 4 种产出模式——HTML 动画一气呵成的视频，导出 MP4 + GIF 三件套，可加 BGM。

## 何时启用

| 用户说什么 | 启用 |
|---|:---:|
| "导出 MP4"、"做成视频"、"60fps 视频" | ✅ |
| "做个动画 demo"、"动效演示" | ✅ |
| "做个 hero video"、"产品宣传片" | ✅ |
| "做个解说视频"、"配音动画"、"voiceover" | ✅ → 走 narration 子模式（见下） |
| "做个 GIF" | ✅ |
| "做个幻灯片然后录视频" | ❌ → 那是 slide-mode 的 autoplay 录屏 |

## 与 motion-chart（viz-charts 的 motion 能力）的区别

| 维度 | viz-charts · motion-chart | viz-deck · motion-mode |
|---|---|---|
| 焦点 | 单个图表的动效 | 完整叙事 / 多 stage 连贯运动 |
| 时长 | 2-12s | 6-60s（带解说可到 5 分钟） |
| 结构 | 一 stage 一图表 | 一 stage 多元素 + 多镜头切换 |
| 输出 | trend-motion.mp4 | hero-video.mp4 + 可选 BGM/narration |

如果只是想做"图表动起来"——用 viz-charts。如果是"产品概念视频"——用 viz-deck motion-mode。

## 工作流

### 1. 选模板

`templates/motion-stage.html` 是基础 stage 模板，含 huashu 的 Stage/Sprite/Easing 引擎：

```html
<!doctype html>
<html data-motion-stage data-record-seconds="8">
<head>
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
  <div id="root" class="stage" style="width:1920px;height:1080px;"></div>
  <script type="text/babel" data-presets="react">
    // 引入 huashu 的 animations 引擎
    // <Stage> 包装画布
    // <Sprite> 包装可动元素（提供 useTime / useSprite / interpolate / Easing）
    function HeroVideo() {
      return (
        <Stage duration={8}>
          <Sprite from={0} to={3}>
            {(t) => <Title opacity={interpolate(t, [0, 0.5], [0, 1])} />}
          </Sprite>
          <Sprite from={2} to={6}>
            {(t) => <ProductShot scale={interpolate(t, [0, 1], [0.8, 1.2], Easing.cubicOut)} />}
          </Sprite>
          <Sprite from={5} to={8}>
            {(t) => <CTA y={interpolate(t, [0, 1], [200, 0], Easing.cubicOut)} />}
          </Sprite>
        </Stage>
      );
    }
    ReactDOM.createRoot(document.getElementById('root')).render(<HeroVideo />);
  </script>
</body>
</html>
```

**铁律**：整片是**一个连续的运动叙事**。**禁 PowerPoint 切换**（fade-out → black → fade-in 下一页）——那是 slide-mode 的事。motion-mode 里画面元素必须连续运动。

### 2. 时长 / 帧率

| 类型 | 时长 | 帧率 |
|---|---|---|
| Hero loop（无音 GIF） | 4-8s | 25fps → 60fps 插帧 → GIF 12fps |
| 产品视频 | 15-30s | 25fps → 60fps 插帧 |
| 概念解说视频 | 1-5 min | 25fps → 60fps 插帧 + voiceover |
| 路演开场 | 8-12s | 25fps → 60fps 插帧 + BGM |

不要超过 5 分钟——长视频的注意力曲线会断。如果内容多，分段。

### 3. 录制：调用 huashu render-video.js

```bash
HUASHU="$HOME/.claude/skills/huashu-design"

# 单镜头 —— huashu CLI 用 --key=value 语法，输出文件名 = 输入文件名 + .mp4
node "$HUASHU/scripts/render-video.js" ./output/hero.html \
  --duration=8 --width=1920 --height=1080

# 三件套（25fps + 60fps + GIF）
bash "$HUASHU/scripts/convert-formats.sh" ./output/hero.mp4
# 产物：hero.mp4 / hero-60fps.mp4 / hero.gif

# 或直接用 viz-deck 的 wrapper（自动二步走）
bash ~/.claude/skills/viz-deck/scripts/export-mp4.sh ./output/hero.html 8
```

**重要**：录制要求 stage HTML 在首次渲染完成后设置 `window.__ready = true`——huashu 的 render-video.js 会用这个信号作为录制 t=0 起点，否则前 1-2 秒会录到黑帧。`templates/motion-stage.html` 已内置这个信号；自己写 stage 时务必加上：

```js
document.fonts.ready.then(() => {
  requestAnimationFrame(() => { window.__ready = true; });
});
```

### 4. 加 BGM（可选）

huashu 自带 6 首场景化 BGM：

| 文件 | 场景 |
|---|---|
| `bgm-tech.mp3` | 科技数据风 |
| `bgm-educational.mp3` | 解说讲解 |
| `bgm-educational-alt.mp3` | 同上备选 |
| `bgm-tutorial.mp3` | 步骤教学 |
| `bgm-tutorial-alt.mp3` | 同上备选 |
| `bgm-ad.mp3` | 短广告 / hook |

```bash
bash "$HUASHU/scripts/add-music.sh" \
  ./output/hero-60fps.mp4 \
  "$HUASHU/assets/bgm-tech.mp3" \
  ./output/hero-final.mp4
```

BGM 默认音量 0.18，自动 fade-in/out。

### 5. 解说子模式（voiceover / narration）

如果用户要"带解说的动画"、"5 分钟讲清楚 XX"、"科普视频"——走解说子模式。

需要：

- 豆包 TTS 凭据（`.env`：`DOUBAO_TTS_API_KEY` + `DOUBAO_TTS_VOICE_ID`，详见 `~/.claude/skills/huashu-design/.env.example`）
- 解说脚本（markdown）
- ducking 混音规则（解说说话时 BGM 自动降低 -12dB）

```bash
HUASHU="$HOME/.claude/skills/huashu-design"

# 1) 生成 TTS 音频 + 实测时长
node "$HUASHU/scripts/tts-doubao.mjs" \
  --input ./input/narration.md \
  --output-dir ./output/audio/

# 2) 基于实测时长生成 timeline.json
# 3) NarrationStage 自动驱动画面
# 4) 整体 pipeline 一键过
node "$HUASHU/scripts/narrate-pipeline.mjs" \
  --script ./input/narration.md \
  --visual ./output/hero.html \
  --output-dir ./output/narration/
```

产物：

- `narration.html` — HTML 实时播放（含 NarrationStage）
- `narration.mp4` — 发布用 MP4（带 ducking 混音）
- `narration-subtitles.srt` — 字幕

**铁律**：解说时长 → 画面运动节奏对齐。**禁止**给 30s 解说配 90s 画面（观众会走神）。

## 字幕与音量

| 项 | 标准 |
|---|---|
| BGM 默认音量 | 0.18 |
| Voiceover 音量 | 1.0 |
| Ducking 阈值 | 解说说话时 BGM 自动 -12dB |
| 字幕字号 | 1080p 视频 32-40px |
| 字幕底色 | rgba(0,0,0,0.6) 半透明黑条 |
| 字幕对比度 | WCAG AAA（≥ 7:1） |

## 反模式

- ❌ 在 motion-mode 里塞 slide 切换（PowerPoint 模式）
- ❌ 一镜超过 5 分钟无任何变化
- ❌ 用 emoji 当主视觉
- ❌ BGM 音量 > 0.3（盖过解说）
- ❌ 解说速率 > 350 字/分钟（汉语）/ > 200 wpm（英语）
- ❌ 录制画布 ≠ 1920×1080（除非明确做 9:16 短视频，要在 stage 上声明）
- ❌ 不跑 ffmpeg 看一眼输出就交付——首/末帧、音画同步、文件大小都要 sanity check
