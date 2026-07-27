# 可恢复的视频生产工作流

## 目录

- [目标](#目标)
- [默认流程](#默认流程)
- [工位与算子契约](#工位与算子契约)
- [状态与闸门](#状态与闸门)
- [返工与学习闭环](#返工与学习闭环)
- [工程版本与节点重做](#工程版本与节点重做)
- [看板要求](#看板要求)

## 目标

把视频生产视为可暂停、可恢复、可审计的有向图，而不是一串聊天消息。采用 ZimaBlueAI 定义的 Pipeline → Operator → Artifact 分层、文件化检查点、上下文隔离和导演工位表达；不把影视判断机械化。第三方产品或项目只在实际互操作需要时中性引用，不构成本方法的来源声明、合作或背书。

每个阶段必须留下：

- 结构化输入、输出路径和稳定 ID；
- 执行状态、依赖、审批闸门与返工原因；
- 人工判断、自动检查和模型推断的边界；
- 来源、权利、模型、成本、版本与验收证据；
- 下一阶段真正需要的摘要，而不是整个历史上下文。

## 默认流程

```text
00 需求/权利/预算
  → 01 同题研究与样本卡
  → 02 创作策划与原创性闸门
  → 03 剧本/论点/证据图
  → 04 角色/场景/道具/声音设计圣经
  → 05 分镜与 animatic
  → 06 拍摄/素材获取/生成
  → 07 画面剪辑与 picture lock
  → 08 音源分离/清理/转写
  → 09 可见说话人、口型活动与对白定位
  → 10 对白/音乐/音效/环境混音
  → 11 调色/字幕/母版
  → 12 技术 QC + 导演审片 + 权利检查
  → 13 创意评分 + 发布前诊断 + 有条件预测
  → 14 发布/A-B/真实指标回收
  → 15 校准、复盘与下一版
```

允许并行的只有真正独立的工作。例如角色、场景和道具可在剧本锁定后并行；画面剪辑与最终混音不可假装完全独立。所有并行分支在合流前必须验证版本和上游指纹。

## 工位与算子契约

一个 operator 至少记录：

```json
{
  "id": "audio.separate.uvr5.v1",
  "station": "audio_post",
  "depends_on": ["picture.lock.v3"],
  "inputs": [{"asset_id": "source-01", "path": "source.mp4"}],
  "outputs": [{"asset_id": "stem-dialogue-01", "path": "stems/dialogue.wav"}],
  "status": "review",
  "gate": "human_audio_review",
  "evidence": ["stems/dialogue.wav.provenance.json"],
  "invalidates": ["mix.v2"],
  "note": "人声/非人声分离；残留与伪影需试听"
}
```

约束：

- 输入只读，输出写新版本；拒绝隐式覆盖。
- 同一资产只有一个稳定 `asset_id`，别用多个名称伪装成多个素材。
- operator 只声明实际能力。UVR5 的 vocals/accompaniment 不等于任意乐器和噪声的完美分离。
- 自动结果进入 `review`，不能直接跳成 `approved`。
- 执行日志保存摘要与证据路径，不保存密钥、完整私有提示或未脱敏请求。

## 状态与闸门

通用状态：

- `planned`：已定义但未具备输入；
- `ready`：依赖齐全，可执行；
- `running`：正在执行；
- `review`：已产出，等待人工或独立检查；
- `approved`：已签收；
- `rework`：有明确返工说明；
- `blocked`：缺少授权、配置、权利、预算或关键输入；
- `stale`：上游变更使结果失效。

硬闸门：

1. 私有媒体远程上传；
2. 付费生成与预算变化；
3. 声音克隆及未成年人/可识别个人同意；
4. 纪录片、产品证明和事实重建；
5. picture lock 后的结构变化；
6. 对外发布。

每个闸门记录批准人、范围、时间、预算上限与会失效的条件。

## 返工与学习闭环

使用 generate → evaluate → filter → refine，但影视评价始终保留人工审片：

1. 生成或剪出候选；
2. 自动检查文件、同步、响度、黑场、缺帧和数据完整性；
3. 人工检查故事、表演、真实性、连续性、声音与权利；
4. 过滤未达标候选，保留拒绝原因；
5. 每轮只改变一个结构变量；
6. 三次重复核心偏差后换媒介、模型或前提；
7. 发布后只用真实同口径数据校准假设。

完成的子任务写入文件并压缩为面向下一阶段的摘要。不要让完整研究网页、逐帧日志或模型原始输出永久占据主上下文。

## 工程版本与节点重做

工程 manifest 与历史快照必须在同一项目目录，默认结构：

```text
project/
  project.json
  dashboard.html
  history/
    index.json
    versions/
      <version-id>.project.json
```

使用 `scripts/workflow_control.py`，任何修改都先保存当前 manifest；版本文件用独占创建且永不覆盖。常用命令：

```text
# 查看实时状态
python <skill-dir>/scripts/workflow_control.py status project.json

# 更新节点；先预演，核对后追加 --confirm
python <skill-dir>/scripts/workflow_control.py transition project.json --stage sound_mix --status review --note "v3 混音待审"

# 重做某节点；自动把全部下游标成 stale
python <skill-dir>/scripts/workflow_control.py redo project.json --stage storyboard --reason "角色运动方向错误"

# 列出/恢复历史；恢复前仍会保存当前状态
python <skill-dir>/scripts/workflow_control.py versions project.json
python <skill-dir>/scripts/workflow_control.py restore project.json --version <id> --reason "回到导演签收版"
```

`transition`、`redo`、`restore` 默认只输出计划；只有显式 `--confirm` 才写入。重做不是删除旧产物：旧 manifest 和媒体版本继续保留，新的节点产物使用新版本号，用户可在 dashboard 的历史选择器查看快照并复制恢复预演命令。

## 看板要求

看板应同时显示：

- 全流程图、当前节点、依赖、闸门和返工回路；
- 工位状态与更新时间；
- 输入、生成物、采用/拒绝状态和溯源；
- 音频 stems、混音、口型/同步报告；
- 技术 QC、创意审片与营销预测的独立状态；
- 成本、变更、真实指标和预测置信度。

SVG 流程节点可点击/键盘聚焦，并定位到节点状态、依赖、输出和重做入口；历史选择器只切换已保存版本说明，不在浏览器里静默写工程。状态改变后重新运行 `scripts/pipeline_dashboard.py`；本地 `file://` 看板默认不自动刷新，避免重置音视频播放。无人盯守的进度屏可显式使用 `--refresh <秒>`，正常审片使用手动刷新。
