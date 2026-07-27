# NOTICE · web-shader-extractor

本 skill **原样移植**自上游开源仓库，未修改任何 `SKILL.md` / `references/` / `scripts/` / `templates/` 内容（逐字节复制）。

| 项 | 值 |
|---|---|
| 上游仓库 | https://github.com/lixiaolin94/skills |
| 子路径 | `web-shader-extractor/` |
| 原作者 | [@lixiaolin94](https://github.com/lixiaolin94) |
| 鸣谢 | [@HeyHuazi](https://github.com/HeyHuazi) — 2D Canvas 抠取报告与移植策略 |
| License | MIT |
| 移植日期 | 2026-06-29 |

## 本仓库新增的内容（非上游）

以下文件是本仓库为方便使用而**额外添加**的，不属于上游 skill 本体：

- `NOTICE.md`（本文件）
- `web-shader-extractor-README.md`（中文使用说明）
- `demo-webgl-fragment.html` / `demo-canvas2d-flow.html` / `demo-three-reconstruct.html`（自包含样例复现，演示该 skill 抠取产物的形态）

> 升级上游版本时：重新 `git clone https://github.com/lixiaolin94/skills`，用 `web-shader-extractor/` 覆盖
> SKILL.md / references / scripts / templates 即可，本文件与 demo 不受影响。

MIT License 全文见上游仓库根 README（上游声明 `## License: MIT`，仓库根未单独放 LICENSE 文件）。
