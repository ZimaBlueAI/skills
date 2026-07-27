# 转场语法

转场是标点符号，不是装饰。**转场越花哨，越暴露业余。**

## 语法表

| 类型 | 语义 | 何时用 | 实现 |
|---|---|---|---|
| cut 硬切 | 逗号 | 默认，≥85% 的剪辑点 | 直接拼接 |
| dissolve 叠化 | 时间流逝 / 空间远移 | 仅此两义，用在别处即错 | ffmpeg xfade=fade |
| dip_to_black 黑场 | 句号，章节结束 | 章节间；开头黑场渐入=庄重 | xfade=fadeblack |
| white_flash 白闪 | 冲击 / 闪回 / 记忆 | 情绪爆点、回忆切入 | xfade=fadewhite |
| whip 甩镜 | 能量延续 | 快节奏段落间，动势相接 | xfade=slideleft + motion blur，或素材本身甩摄 |
| mask_wipe 遮挡转场 | 空间穿越 | 前景物扫过画面时切 | 素材遮挡点对切 |
| match_cut 匹配剪辑 | **概念连接（隐喻）** | 形状/动作/声音相似的两物相接 | 选材阶段发现，剪辑点对齐 |
| gl_transition | 风格化包装 | 品牌片/科技感包装段 | GL-Transitions shader 库 |
| generative 生成式 | 时空跳跃 / 变形 / 穿越 | 见下方决策树 | Seedance 首尾帧 |

**硬规则（写入 edit_plan schema）：非 cut 转场必须填 `reason` 字段，写明它表达了什么硬切表达不了的东西。写不出来，改硬切。** 这条是审美的下限保险。

match_cut 是最高级的转场，因为它在做隐喻（骨头抛起接卫星）。每片能有一个好 match cut，胜过十个 shader 特效。

## 生成式转场决策树

```
两镜头需要衔接
├─ 有画面内在联系（动作/形状/声音相似）？
│    └─ 是 → match_cut，不花一分钱
├─ 只是节奏衔接？
│    └─ 是 → cut 或 whip
├─ 语义是章节/时间跳跃？
│    └─ 是 → dip_to_black 或 dissolve
├─ 两镜头完全无关且必须表达"穿越/变形/时空跳跃"的叙事含义？
│    └─ 是 → generative（Seedance 首尾帧），进 gap_list 报预算
└─ 只是想"炫一下"？
     └─ 禁止。回到 cut。
```

生成式转场的准入条件是**叙事含义**，不是"两个镜头接不上"。接不上通常是选材问题，先回 shot_manifest 换镜头。

## 各结构的转场配比参考

- trailer-6：cut 90%，高潮前一处 dip/silence，落版前可一处 white_flash
- 卡点混剪：cut + whip 为主，drop 处硬切最强镜头（不要在 drop 上叠转场，转场会吃掉冲击力）
- 起承转合："转"的位置是全片唯一值得用 dissolve/match_cut/generative 的地方
- listicle：条目间统一用同一种转场（编号卡或同款 whip），一致性即专业感

## 审美检查清单

- [ ] cut 占比 ≥ 85%（listicle 可放宽）
- [ ] 每个非 cut 转场的 reason 经得起追问
- [ ] dissolve 只出现在时间/空间语义处
- [ ] drop 切点上没有叠加转场特效
- [ ] generative 转场每处都有叙事含义且已计入成本
