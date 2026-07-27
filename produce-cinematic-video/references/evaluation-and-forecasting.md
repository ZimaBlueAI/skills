# 视频评分、同题学习与表现预测

## 目录

- [三层结论](#三层结论)
- [创作评分](#创作评分)
- [同题基准](#同题基准)
- [预测闸门](#预测闸门)
- [指标口径](#指标口径)
- [发布后校准](#发布后校准)

## 三层结论

始终分开：

1. **技术 QC**：文件、编码、响度、黑场、冻结、字幕和播放；
2. **创作评估**：故事、表演、理解、节奏、声画、原创性、信任和平台适配；
3. **表现预测**：基于可比历史数据的区间估计。

技术通过不等于好看；创作高分不保证流量；没有数据时不得伪造预测。

## 创作评分

复制 `assets/evaluation-input.template.json`，每项给：

- `score`：0–10；
- `evidence`：文件、时间码、截图、波形或研究样本；
- `confidence`：low / medium / high；
- `impact`：对理解、情绪、信任或行动的影响；
- `recommended_change`。

默认维度：

1. audience fit；
2. promise clarity；
3. story / argument；
4. proof / factual trust；
5. payoff；
6. visual staging and continuity；
7. sound and speech intelligibility；
8. rhythm and attention；
9. originality and rights safety；
10. packaging / CTA。

只有全部维度有证据时才计算 100 分总分；任何缺项都输出“部分评分”。权重来自项目 brief，不使用跨类型固定权重。

## 同题基准

同题研究卡只比较可比样本：

- 同平台、地区、时期、账号量级和付费/自然流量；
- 同目标、片长、形式和受众；
- 相同指标分母与观察窗口。

比较可观察特征，不推断单一剪辑技巧导致成功。输出目标组与对照组差异、样本量、缺失值、置信度和可能混杂因素。

## 预测闸门

`scripts/evaluate_video.py` 只有同时满足以下条件才输出经验区间：

- 至少 30 条可比历史发布；
- 每个率的分母明确且为正；
- 聚合曝光/观看量达到项目设定阈值；
- 样本包含普通或低表现内容，不只有爆款；
- 平台、时期、投放和受众差异已记录。

不满足时输出 `not_estimable`，并给出需要收集的数据和可验证实验。即使满足，结果也是关联性基线，不是流量、点赞或获客承诺。

## 指标口径

推荐口径：

- `view_rate = views / impressions`；
- `like_rate = likes / views`；
- `completion_rate = completions / views`；
- `click_rate = clicks / impressions`；
- `lead_rate = leads / clicks`；
- `customer_rate = customers / leads`。

如果平台没有 impressions、clicks 或 leads，不要换分母后沿用同一指标名。`获客率`必须明确指 lead、qualified lead 还是 customer。

历史表使用 `assets/performance-history.template.csv`。个人信息只保留聚合数据，不把用户级标识写入项目。

## 发布后校准

1. 预先登记版本差异、主要假设、成功指标和观察窗口；
2. A/B 每次只改变一个主要变量；
3. 回收真实分母、流量来源、投放、时间、受众与版本；
4. 报告点估计与 Wilson 区间，而不是只报百分比；
5. 对预测误差做校准，记录失效条件；
6. 把结论写回研究卡和下一版策划，不覆盖原预测。

预测模型只有在连续多个周期保持校准时才升级为决策输入；否则保持为假设生成器。
