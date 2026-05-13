# huashu-bridge: viz-deck 与 huashu-design 的桥接协议

> v2 新增。viz-deck 不重新发明轮子——把高保真原型、幻灯片导出、MP4 录制、20 设计哲学、5 维评审这些能力都委托给已经成熟的 `huashu-design` skill，本文件说明**桥接点**与**职责边界**。

## 为什么要桥接而不是复制

`huashu-design` 是花叔（alchaincyf）独立维护的成熟 skill：

- 20 设计哲学和 5 维评审是它的版本控制资产（v2.1 / v1.0）
- 视频导出工具链（render-video.js / convert-formats.sh / add-music.sh）依赖 Playwright + ffmpeg + 6 首场景化 BGM
- html2pptx / export_deck_pptx.mjs 已实现"DOM → 真实 PPTX 文本框"的能力

复制这些到 viz-deck 等于：
1. 版本漂移（huashu 升级了，viz-deck 没跟）
2. 资源浪费（BGM 文件 ~5MB × 6 首 + sharp 二进制都会进我们的 zip）
3. 法律风险（huashu 商用授权独立）

桥接策略：**视为可选依赖**——viz-deck 检测到 huashu-design 存在则启用 v2 模式，否则降级到 v1（仅 keynote 静态报告）。

## 桥接点清单

| viz-deck 能力 | 委托对象 | 路径 |
|---|---|---|
| 20 设计哲学风格库 | huashu 的 `design-styles.md` | `~/.claude/skills/huashu-design/references/design-styles.md` |
| 5 维专家评审标准 | huashu 的 `critique-guide.md` | `~/.claude/skills/huashu-design/references/critique-guide.md` |
| HTML → MP4 视频录制 | huashu 的 `render-video.js` | `~/.claude/skills/huashu-design/scripts/render-video.js` |
| 25fps→60fps + GIF 三件套 | huashu 的 `convert-formats.sh` | `~/.claude/skills/huashu-design/scripts/convert-formats.sh` |
| BGM 配乐 | huashu 的 `bgm-*.mp3` + `add-music.sh` | `~/.claude/skills/huashu-design/assets/` |
| HTML → 可编辑 PPTX | huashu 的 `html2pptx.js` / `export_deck_pptx.mjs` | `~/.claude/skills/huashu-design/scripts/` |
| HTML → 多页 PDF（横版 keynote） | huashu 的 `export_deck_pdf.mjs` | `~/.claude/skills/huashu-design/scripts/` |
| 设备外壳（iPhone/Android/macOS/browser） | huashu 的 `*_frame.jsx` | `~/.claude/skills/huashu-design/assets/` |
| 动画引擎（Stage/Sprite/Easing） | huashu 的 `animations.jsx` | `~/.claude/skills/huashu-design/assets/` |
| 解说视频（TTS + timeline + ducking） | huashu 的 `narrate-pipeline.mjs` | `~/.claude/skills/huashu-design/scripts/` |

## 检测 huashu-design 是否就位

每次 viz-deck 进入 v2 模式前，做一次轻量探测：

```bash
HUASHU=~/.claude/skills/huashu-design
test -f "$HUASHU/SKILL.md" && \
test -f "$HUASHU/scripts/render-video.js" && \
test -f "$HUASHU/references/design-styles.md" && \
echo "OK" || echo "MISSING"
```

如果 `MISSING`：

1. **不要 silently fallback**——告诉用户 v2 模式需要 huashu-design
2. 给出一行安装命令：

   ```bash
   git clone --depth=1 https://github.com/alchaincyf/huashu-design.git ~/.claude/skills/huashu-design
   cd ~/.claude/skills/huashu-design && npm install && npx playwright install chromium
   ```

3. 询问是否仍要继续 v1 模式（仅 keynote 静态报告，不出 MP4/PPTX）

## 调用契约：永远用绝对路径

所有桥接调用必须用 **`~` 展开后的绝对路径**，不要假设当前工作目录：

```bash
# ✅ 好
HUASHU="$HOME/.claude/skills/huashu-design"
node "$HUASHU/scripts/render-video.js" --input output/x.html --output output/x.mp4

# ❌ 坏：用户工作目录可能不在 ~/.claude
node ../huashu-design/scripts/render-video.js ...
```

## 不要做的事

- ❌ 把 huashu 的 BGM / chromium 二进制 / 哲学库**复制**进 viz-deck.zip
- ❌ 修改 huashu-design 目录下的任何文件（那是它的版本控制资产）
- ❌ 把桥接做成 git submodule（用户安装体验会很差）
- ❌ 在 viz-deck SKILL.md 里重复阐述 20 哲学的内容——引用即可

## 许可证

huashu-design 个人使用免费，**商用需独立授权**（USD 1,800/年 或 USD 3,500 永久）。如果终端用户是商业项目，提醒他们：viz-deck 是 MIT，但 v2 模式调用的 huashu-design 商用合规由用户自行负责。

联系：alchaincyf@gmail.com
