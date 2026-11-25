# 一致性与连续性

1. 每个角色/道具/场景一个 `asset_id`，canonical 文件哈希写入 `materials/<id>/current.json`。
2. 替换素材只追加版本，旧文件进入 `materials/<id>/history/`。
3. 分镜与生图必须引用 approved 版本；文本重生人物默认拒绝。
4. `continuity.json` 记录每镜首末状态：位置、朝向、手持道具、光线方向。
5. 运镜与空间调整改 `stage_plan`，不直接改 canonical 形象。
