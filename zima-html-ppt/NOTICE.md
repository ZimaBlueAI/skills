# NOTICE · zima-html-ppt

zima-html-ppt 的**视觉系统（ZimaBlue Editorial）、演讲者模式引擎、起步模板、构建 shell 与
`deck.json` 文档契约均为 ZimaBlueAI 原创**，提炼自实战母版 `D1-破局与进化.html` /
`D2-三场战役.html` / `D3-训练方案.html`。

v2 新增的**工程治理层方法论**借鉴自下列开源项目。我们没有移植其代码或资产，
借的是工作流骨架与闸门思路；在此完整署名。

## 方法论溯源

| 我们的东西 | 借鉴自 | 版本/commit | 原作者 | 许可 | 借鉴日期 |
|---|---|---|---|---|---|
| 方案先行工作流（意图卡 / `1a·2b·3c` 三方向选择卡 / source-grounded `deck-plan.md` / 视觉所有者 / 内容→能力映射表） | [joeseesun/qiaomu-bento-ppt](https://github.com/joeseesun/qiaomu-bento-ppt) `references/workflow.md` | `55c63c8`（2026-07-27） | 向阳乔木 | MIT | 2026-07-27 |
| 闸门阶梯（Route / Structure / Identity / Shell / Quality / Browser / Rollback）与 `missing evidence` 证据纪律 | 同上 `SKILL.md` "Gate Ladder" | 同上 | 同上 | MIT | 2026-07-27 |
| 文档内嵌事实源 + 反解重编辑（`#bento-doc` → 我们的 `#zima-doc`）、身份保持（`docId` → `deckId`）、默认不覆盖源文件的回滚边界 | 同上 `scripts/bento_deck.py` | 同上 | 同上 | MIT | 2026-07-27 |
| 输出契约（plan + JSON + 产物 + 报告 + 交付说明）与路由 trigger eval 的组织方式 | 同上 `SKILL.md` / `evals/trigger_cases.json` | 同上 | 同上 | MIT | 2026-07-27 |

**没有借的**：上游内置的 `nyblnet/bento` 官方 shell（600KB）、`bento/slides` 文档格式、
upstream 锁定与同步机制、Skill IR 导出。本技能不依赖 bento，也不产出 `.bento.html`。

`scripts/zima_deck.py`、`scripts/trigger_eval.py`、`evals/run_fixtures.py`、
`templates/zima-ppt-shell.html`、`references/deck-json.md` 全部为本仓库自行编写，
仅在结构组织上参考上游，未复制其源码。

## 姊妹层

- 反 AI slop 硬闸蒸馏自 [nutlope/hallmark](https://github.com/nutlope/hallmark)（MIT），
  已收编为本仓库 `zima-design` 的 anti-slop 引擎，署名详见 `zima-design/NOTICE.md`。
- 口味档位与选材/文案细则见 `zima-design` 的 taste 引擎。

## 升级借鉴来源

上游是独立仓库，与本技能无代码耦合，直接读它的最新 `SKILL.md` / `references/` 即可：

```bash
git clone --depth 1 https://github.com/joeseesun/qiaomu-bento-ppt
```

看到值得吸收的新纪律时，改的是本技能的 `references/gates.md` 与 `references/workflow.md`，
并回来更新本文件的版本列。
