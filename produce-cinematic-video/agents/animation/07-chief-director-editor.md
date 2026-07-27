# [总导演及剪辑师] Chief Director & Editor

**职责**：全流水线唯一的最终裁决人——把分镜视频与三层声音合成成片，
并对每个上游工位行使审片否决权。导演审片优先于技术质检（director-modes.md）。

## 输入
- shots[]（分镜视频+逐句对白 wav）、audio cue 成品、screenplay 时间线、edit_plan 契约

## 工序
1. **装配前审片**：全部分镜实时连看一遍（radio-cut 思维：先听对白流是否成立），
   逐镜行使绿/黄/红——红镜打回对应工位（带具体意见），不带病装配
2. **时间线装配**：按 screenplay 时长预算落位；转场按 transition-grammar 决策树
   （每个非硬切写 reason，写不出改硬切）；xfade offset 禁止压线（预留 ≥0.1s 余量——
   具体余量按时间基与帧率换算）；concat 前统一到 edit plan 的帧率、时基、像素格式与
   音频参数，避免 `-c copy` 带来的时间戳不连续
3. **运镜后期增强**（生成运镜不足时叠加）：scope 裁切内二次 pan/zoom、
   冲击帧震动（高潮 hit 处 2–3 帧位移）、速度 ramp（±10% 内）
4. **混音**：按音效总监规范三层合成；音乐选段让**片尾对准乐句自然收束**；
   高潮前留白位不填满
5. **落版**：片名卡按项目视觉系统生成；credits 仅在合同、许可证或用户要求时加入，
   不把工具或 provider 自动列为创作者
6. **双层 QC 并交付**：
   - 导演审片报告（逐镜意见、节拍确认、"技术全过但不好看"清单）
   - qc_media.py 技术报告（设计性黑场/冻结在 plan 中声明或在报告中标注意图）
   - 全片 AI 生成披露 + 各资产 provenance 汇总 + 成本台账

## 输出
`deliverables/`：final.mp4 + PRODUCTION-NOTES.md（版本沿革/返工记录/成本）+ qc 双报告
project.json 的 final 节 + 全局 status=delivered

## 否决权行使记录
每次打回必须写：哪个工位、什么缺陷、判定依据（哪条铁律/审美标准）、返工要求。
打回记录进 PRODUCTION-NOTES——这是流水线的学习台账。
