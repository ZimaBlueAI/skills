# NOTICE · gzh-design

本 skill **原样移植**自上游开源仓库，未修改任何 `SKILL.md` / `references/` / `scripts/` / `assets/` 内容（逐字节复制）。

| 项 | 值 |
|---|---|
| 上游仓库 | https://github.com/isjiamu/gzh-design-skill |
| 上游 commit | `67c079e`（2026-07-07，甲木 × 摸鱼小李 联名首发） |
| 原作者 | [@isjiamu](https://github.com/isjiamu)（甲木） × [「摸鱼小李」](https://mp.weixin.qq.com/s/EMahAzgfAbRQrYukWE7_IQ) 联名共建 |
| License | AGPL-3.0（全文见本目录 `LICENSE`，随上游一并复制） |
| 移植日期 | 2026-07-07 |

## 移植范围

移植 skill 本体全部 20 文件：`SKILL.md` + `LICENSE` + 11 篇 `references/`（主题索引 / 6 套主题组件库 + 通用增量库 + 主题生成器 + 格式归一化 + 回归用例）+ 4 个 `scripts/`（双关卡校验 / docx 提取 / 预览包装）+ 3 个 `assets/`（预览模板 / 样例文章 / 主题预览示例）。

**未移植**（非 skill 运行所需）：上游 `archive/`（v1 旧版主题与图库归档）、`docs/`（效果展示长图库）、`.github/`、`CONTRIBUTING.md`、上游 README。

## 本仓库新增的内容（非上游）

- `NOTICE.md`（本文件）
- `gzh-design-README.md`（中文使用说明）

> 升级上游版本时：重新 `git clone https://github.com/isjiamu/gzh-design-skill`，用其
> `SKILL.md` / `references/` / `scripts/` / `assets/` / `LICENSE` 覆盖本目录同名内容即可，本文件与使用说明不受影响。
> 覆盖后跑一遍 `PYTHONIOENCODING=utf-8 python scripts/component_lint.py .` 确认 ERROR×0。
