# mp4-export: 图表 → 视频的工具链桥接

> viz-charts 自身不实现录屏。本文件说明如何把 motion stage HTML 喂给 `huashu-design` skill 的视频导出脚本。

## 前置条件

`~/.claude/skills/huashu-design/` 已安装，且：

```bash
cd ~/.claude/skills/huashu-design
npm install                          # playwright + sharp + pptxgenjs + pdf-lib
npx playwright install chromium
which ffmpeg                         # 需要 ffmpeg 在 PATH
```

如果缺，向用户报告并停止，**不要 silently fallback** —— motion 模式没工具链就不该出片。

## 一图一片（最简）

```bash
node ~/.claude/skills/huashu-design/scripts/render-video.js \
  ./output/trend-motion.html \
  --duration=6 \
  --width=1920 --height=1080
```

参数（huashu CLI 风格：位置参数 + `--key=value`）：

| 参数 | 默认 | 说明 |
|---|---|---|
| 位置参数 1 | — | 必填。motion stage HTML 路径；输出自动同名 `.mp4` 落在同目录 |
| `--duration=N` | 30 | 录制秒数 |
| `--width=W` / `--height=H` | 1920/1080 | 录制画布 |
| `--trim=N` | 自动 | 录制开头要 trim 的秒数（覆盖 `__ready` 自动检测） |
| `--fontwait=N` | 1.5 | 没有 `__ready` 信号时的字体兜底等待 |
| `--readytimeout=N` | 8 | 等待 `window.__ready=true` 超时秒数 |
| `--keep-chrome` | off | 默认 CSS 会隐藏 `.no-record/.progress/.replay` 元素，加 flag 保留 |

**重要**：motion stage HTML 必须在首次渲染后设 `window.__ready = true`，huashu 用这个标记作录制 t=0 起点，否则前 1-2 秒会黑帧。`templates/motion/motion-stage-template.html` 已内置；自己写 stage 必须加：

```js
document.fonts.ready.then(() => {
  requestAnimationFrame(() => { window.__ready = true; });
});
```

## 三件套导出（25fps + 60fps + GIF）

```bash
bash ~/.claude/skills/huashu-design/scripts/convert-formats.sh ./output/trend-motion.mp4
```

产物：

- `trend-motion.mp4`（保留 25fps 原片）
- `trend-motion-60fps.mp4`（minterpolate 插帧到 60fps）
- `trend-motion.gif`（palettegen+paletteuse，<2MB）

## 加 BGM（可选）

```bash
# 选一首 huashu-design 自带的场景化 BGM
bash ~/.claude/skills/huashu-design/scripts/add-music.sh \
  ./output/trend-motion-60fps.mp4 \
  ~/.claude/skills/huashu-design/assets/bgm-tech.mp3 \
  ./output/trend-motion-final.mp4
```

可选 BGM（位于 `~/.claude/skills/huashu-design/assets/`）：

- `bgm-tech.mp3` — 科技数据风
- `bgm-educational.mp3` / `bgm-educational-alt.mp3` — 解说讲解
- `bgm-tutorial.mp3` / `bgm-tutorial-alt.mp3` — 步骤教学
- `bgm-ad.mp3` — 短广告 / hook

不要给信息密集型决策图表加歌剧式 BGM。BGM 默认音量 0.18（ffmpeg `volume` 滤镜）。

## 批量导出

`output/` 下所有 `*-motion.html` 一键出片：

```bash
for f in ./output/*-motion.html; do
  name="${f%.html}"
  node ~/.claude/skills/huashu-design/scripts/render-video.js \
    --input "$f" --output "${name}.mp4"
done
```

## 失败排查

| 症状 | 原因 | 修复 |
|---|---|---|
| 录出来全黑 | chart 还没渲染就开始录 | 加 `--wait-selector ".chart-loaded"` 并在 chart 完成 `setOption` 后给容器加该 class |
| 文字模糊 | device-scale=1 + 1080p 投影到 4K | 加 `--device-scale 2` |
| 帧丢失 / 卡顿 | CPU 不够 | 降 `--fps 25`，后续插帧到 60；不要原生录 60fps |
| MP4 体积爆炸 | bitrate 默认太高 | 在 render-video.js 命令后接 `ffmpeg -i ... -crf 23 ...` 再压一次 |
| 60fps 文件比 25fps 还小 | 这是正常的 —— minterpolate 重用关键帧 | 不用担心 |
| GIF > 5MB | palette 没生效 | 检查 ffmpeg 版本 ≥ 4.0 |

## 嵌入到 viz-deck 报告

最终视频通常**不内嵌进 keynote HTML**（体积爆炸），而是：

1. 上传到 CDN / 项目 release / 飞书云盘
2. 在 deck 模板里放占位封面图（取视频第一帧 + play overlay）
3. 链接到外部 MP4

例：

```html
<a href="https://cdn.example.com/trend-motion-60fps.mp4" class="motion-link" data-poster="./trend-motion-poster.png">
  <span class="play-icon">▶</span>
  <span class="motion-meta">6s · 60fps · 12 MB</span>
</a>
```

提取首帧做封面：

```bash
ffmpeg -i trend-motion-60fps.mp4 -vframes 1 -q:v 2 trend-motion-poster.png
```
