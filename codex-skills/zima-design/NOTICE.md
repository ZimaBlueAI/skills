# NOTICE · zima-design

zima-design 是 ZimaBlueAI 的自有设计合奏引擎：**SKILL.md 路由协议、多样性协议、验收栈、demos 为原创**；三个内置引擎收编自下列开源项目（均为宽松许可，逐字节保留本体以便跟进上游升级）。我们不冒认引擎本体的原创权，在此完整署名。

## 内置引擎溯源

| 引擎目录 | 上游仓库 | 版本/commit | 原作者 | 许可 | 移植日期 |
|----------|----------|-------------|--------|------|----------|
| `engines/anti-slop/` | [nutlope/hallmark](https://github.com/nutlope/hallmark) | `aeb42fb`（2026-06-04，v1.1.0） | @nutlope (Hassan El Mghari) · Powered by Together AI | MIT（`LICENSES/LICENSE-hallmark`） | 2026-07-16 |
| `engines/motion/` | [emilkowalski/skills](https://github.com/emilkowalski/skills) | `6bf2443`（2026-07-15） | @emilkowalski (Emil Kowalski，sonner/vaul 作者) | MIT（`LICENSES/LICENSE-emil-skills`） | 2026-07-16 |
| `engines/database/` | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | `f8ac5e1`（2026-07-14） | Next Level Builder | MIT（`LICENSES/LICENSE-ui-ux-pro-max`） | 2026-07-16 |

**移植范围**：
- anti-slop：上游 `skills/hallmark/` 全量（SKILL.md + references/，106 文件）；未移植上游 docs/site/package.json
- motion：上游 `skills/` 全量 6 个技能（emil-design-eng / apple-design / animation-vocabulary / review-animations / improve-animations / find-animation-opportunities，10 文件）；未移植上游 README
- database：上游 `.claude/skills/` 全量 7 个技能（ui-ux-pro-max / ui-styling / design / design-system / brand / banner-design / slides，229 文件，含 CSV 数据库与 Python 检索脚本）；未移植上游 cli/src/docs/screenshots

## 外部联动（不落库，仅探测路径）

- [pbakaus/impeccable](https://github.com/pbakaus/impeccable)（Apache-2.0）——有自己的 npx 安装/更新通道，保持独立安装
- [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design)——同上
- 本仓库 `taste-engine/`

## ZimaBlueAI 原创部分

- `SKILL.md`（合奏路由协议 / 三条铁律 / 路由表 / 五轴多样性协议 / 设计签名台账 / 验收栈）
- `demos/`（反面教材 → 审计报告 → 重设计三件套）
- `NOTICE.md`（本文件）、`zima-design-README.md`
- Codex CLI 打包与安装接线

## 升级上游

各引擎目录零改动，直接整目录覆盖即可：

```bash
git clone --depth 1 https://github.com/nutlope/hallmark              # skills/hallmark/ → engines/anti-slop/
git clone --depth 1 https://github.com/emilkowalski/skills           # skills/*        → engines/motion/
git clone --depth 1 https://github.com/nextlevelbuilder/ui-ux-pro-max-skill  # .claude/skills/* → engines/database/
```

覆盖后不要动 `SKILL.md`（顶层）/ `NOTICE.md` / `demos/` / `LICENSES/`。
