# 闸门阶梯 · 输出契约 · 证据纪律

> 一句话：**过了闸门才能说"做完了"，没过的项要按名字写进交付说明。**
> 闸门由 `scripts/zima_deck.py` 与 `scripts/trigger_eval.py` 执行，报告落到 `reports/*.json`。

---

## 1. 七道闸门

| 闸门 | 谁来判 | 判什么 | 不过怎么办 |
|---|---|---|---|
| **Route（路由）** | `scripts/trigger_eval.py` | 这活该不该进本技能 | 让给 `biz-html-viz` / `viz-deck` / `viz-charts`，别硬做 |
| **Structure（结构）** | `zima_deck.py validate` | 缺 `min`、缺逐字稿、未知块型、图表数据非数字、表格列数不齐、占位符残留 | **零 error 才能 build**，`--force` 只在用户明确要求时用 |
| **Identity（身份）** | `zima_deck.py build` | 新建只铸一次 `deckId`；改稿必须与 `--identity-source` 一致 | 不一致直接拒绝构建，先查是不是拿错了原文件 |
| **Shell（外壳）** | build 后自动跑 | 暖纸底色、顶部三色条、`togglePresenter`、`S` 键绑定、`reduced-motion`、品牌签名、计时条 | 说明 shell 被改坏了，回退到 `templates/zima-ppt-shell.html` |
| **Quality（质量）** | `validate` 的 warnings | 名词式标题、逐字稿过短或缺 say/data、一页 >2 种强调色、有数据无来源、页数超区间 | warning 不阻断构建，但**每条都要么改掉、要么在交付说明里解释** |
| **Browser（浏览器）** | 人 | `references/workflow.md` 第 7 节六条 | 没做就写 `missing evidence: browser visual review` |
| **Rollback（回滚边界）** | `zima_deck.py build` | 默认写新文件，源 `.html` 与源资料原封不动 | 要覆盖必须显式 `--overwrite`，并在交付说明里点名 |

跑法：

```bash
python scripts/trigger_eval.py  --report reports/trigger-eval.json    # Route
python evals/run_fixtures.py    --report reports/fixture-eval.json    # 闸门自身的回归
python scripts/zima_deck.py validate deck.json --report reports/deck-validation.json
python scripts/zima_deck.py validate output/xxx.html                  # 含手写 deck
```

---

## 2. 证据纪律 · missing evidence

报告里 `missingEvidence` 默认就带着 `browser visual review`——**这是故意的**。
只有你真的打开浏览器逐条看过，才能在交付说明里划掉它。

下面这些一律按 `missing evidence` 写，不许含糊成"已验证"：

- 没在浏览器里打开过 → `missing evidence: browser visual review`
- 没试过演讲者模式 → `missing evidence: presenter window check`
- 没在断网环境验过 → `missing evidence: offline rendering (Chart.js CDN)`
- 没在实际投影分辨率上看过 → `missing evidence: projector resolution check`
- 数字来自用户口述、没有可查来源 → 页面标 `[估]`，说明里写 `unverified figures`

反面例子（禁止）：「已完成并验证，可直接上台」——脚本证明不了这句话。

---

## 3. 输出契约

一次交付至少给出这五样，缺一样就说明缺在哪：

1. **`deck-plan.md`** —— 受众、目标、叙事弧、逐页结构（含视觉所有者）、素材来源、风险。
2. **`deck.json`** —— 文档源（脚本路线必给；手写路线注明"无，改稿需人重读 HTML"）。
3. **`{YYYY-MM-DD}-{slug}-deck.html`** —— 单文件产物，双击可开、可投影、可演讲者模式。
4. **`reports/deck-validation.json`** —— errors / warnings / gates / stats 全量报告。
5. **交付说明** —— 文件路径、页数与总配额、离线边界、已验证项、仍属 `missing evidence` 的项。

---

## 4. 权限与边界

- **允许**：读用户给的资料与技能自带模板；在输出目录写 plan / JSON / 报告 / 新 deck；跑本地 Python 校验；开本地浏览器复核。
- **需用户明确授权**：覆盖已有 deck（`--overwrite`）、重铸已有身份（`--overwrite-identity`）、带 error 强行产出（`--force`）、把图表资源改成外链、改动 `templates/zima-ppt-shell.html`。
- **禁止**：把 token / cookie / 账号写进 deck 或报告；未经要求就发布、部署或推送；编造数字充当真值。
