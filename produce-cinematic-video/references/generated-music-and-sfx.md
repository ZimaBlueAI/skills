# 为画面生成音乐与音效

## 目录

- [先写 cue 而不是先写风格词](#先写-cue-而不是先写风格词)
- [音乐提示词语法](#音乐提示词语法)
- [音效提示词语法](#音效提示词语法)
- [剧情情绪与转场](#剧情情绪与转场)
- [Suno](#suno)
- [Udio](#udio)
- [ElevenLabs](#elevenlabs)
- [专业示例](#专业示例)
- [生成迭代与成片验收](#生成迭代与成片验收)
- [权利品牌与披露](#权利品牌与披露)

## 先写 cue 而不是先写风格词

复制 `assets/audio-generation-brief.template.md`。在打开生成平台前先回答：

1. 这条声音在故事里做什么，而不只是“什么情绪”？
2. 观众进入 cue 时知道什么，离开时应该新知道/感到什么？
3. 哪些画面事件需要硬同步，哪些只需趋势一致？
4. 进入和退出怎样连接相邻场景？
5. 哪些对白、旁白、同期声、笑点或产品信息必须留空间？
6. 需要完整曲、短 sting、loop、无鼓版、underscore、分轨还是多个长度？

先标相对时间而不是依赖生成器理解项目时间码。至少写 `00:00` 进入、情绪转折、关键 hit、退出四点，并给前后各留可剪 handles。大多数音乐生成器不能逐帧保证命中；精确同步由分段生成、候选选择、NLE/DAW 编辑和必要的获批时长适配完成。

## 音乐提示词语法

按以下顺序写，越靠前越重要：

`戏剧功能 → 情绪弧 → 结构/时长 → 脉冲/速度 → 乐器与音域 → 主题动机 → 同步图 → 转场 → 对白空间 → 结尾 → 排除项`

可复制母版：

```text
Instrumental [form/use] for [scene and audience]. Story job: [function].
Begin [entry emotion/texture], turn toward [new state] when [picture event],
and end [resolved/unresolved/button/tail] for [next transition].
[approximate duration], sections: [A/B/C with approximate spans].
[tempo range/meter/groove], [instrument families/register], [motif behavior],
[harmonic tension and production/acoustic space].
Keep [frequency/register/density] open for [dialogue/VO/production sound].
Sync accents: [relative event map]. Provide [tail/loop/sting/alternate] editability.
Avoid [emotion the story must not imply], [cliches], [instruments/genre traits],
vocals, abrupt ending, and over-compressed trailer mastering.
```

提示词写“可听属性”，不要只堆类型标签。用 `restrained low strings with sparse two-note pulse` 比“感人电影配乐”更可控；用 `tension rises through harmonic narrowing, not louder drums` 比“越来越紧张”更清楚。

不要模仿在世艺术家、受保护角色主题或可识别歌曲。把参考拆成速度、拍号、音色、和声密度、演奏法、录音年代、空间和动态等通用属性。

## 音效提示词语法

一条请求优先描述一个主事件；复杂事件拆成层，再在 DAW 合成：

`声源 → 动作 → 材料/质量 → 速度/力度 → 空间 → 听点/麦克风距离 → 时间包络 → 同步点 → 尾音/loop → 变体 → 排除项`

可复制母版：

```text
[Source] performs [action] against/through [material], with [mass, speed, force].
Heard from [listener/camera perspective] in [space and reflections].
Envelope: [anticipation], [onset/impact], [resonance/mechanism], [decay/tail].
Primary sync at [relative time/event]; total useful length [duration] plus [tail].
[Dry/wet], [close/distant], [realistic/stylized], [variation or seamless loop need].
No music, speech, crowd, reverb baked beyond [amount], clipping, exaggerated whoosh,
unmotivated sub hit, or extra impacts.
```

物理可信度来自接触、质量、材料、机构和空间，不来自“cinematic”一词。为机械动作分别考虑预备、驱动、接触、共振、停止；为 Foley 考虑身体重量、表面与距离；为转场考虑是否有真实声源动机。

## 剧情情绪与转场

情绪不能只写一个形容词，要写变化：

- **进入状态：** 角色/观众目前的确定性、能量和亲密度；
- **触发事件：** 哪个镜头、台词、动作或事实改变意义；
- **转折方式：** 音色替换、和声收窄、节奏抽空、动机变形、空间变远，而不一定升音量；
- **退出状态：** 解决、悬置、释然、警觉、行动欲或品牌记忆；
- **禁忌含义：** 纪录片不要用音乐替事实定罪；教育片不要让胜利音乐掩盖结果的不确定性；广告不要用伪造人群/产品声制造不存在的证明。

转场先选叙事逻辑：

- J-cut/pre-lap：下一场声音提前建立期待或因果；
- L-cut/tail：上一场情绪/空间延续，形成余味或反讽；
- hard button：喜剧、动作或明确章节结束，必须有画面理由；
- riser/drop：只在能量结构需要时使用，不作每次转场默认；
- match texture：用相似的机械、风、频谱或节奏把两个地点连接；
- silence：为真相、反应或危险留空间，要设计进入与退出。

## Suno

Suno 可用于从音乐概念生成完整候选。用户明确选择该服务时：

1. 背景配乐优先选择 Instrumental/无歌词路径；有歌词时把歌词内容、段落和音乐 style 分开写。
2. 在 style/prompt 中先写戏剧功能与情绪弧，再写类型、速度、乐器和制作；不要把剧情说明埋在一串标签末尾。
3. 若当前界面提供 exclude/advanced 字段，把“人声、过密鼓、突然收尾、某种乐器”等负约束放在那里；没有时写在主提示词末尾。
4. 先生成结构清楚、可剪的 30–90 秒候选，再用当前可用的 extend/editor/remix 能力补段；不要一开始要求一首长曲同时精确命中十几个点。
5. 为同一 cue 生成 full、underscore/no-drums、sting/ending 三个功能版本，并记录生成 ID。

Suno 版提示词示例：

```text
Instrumental restrained documentary underscore. A careful investigation moves
from curiosity to verified clarity, never accusation. 62–68 BPM, sparse felt
piano, muted low strings, soft tape texture, no percussion until the evidence
diagram appears around the middle; then add one quiet two-note pulse. Leave the
1–4 kHz range and rhythmic space open for calm narration. End with a clean,
modest resolved button plus two seconds of room-like tail. No vocals, no horror
drones, no heroic triumph, no trailer booms, no abrupt ending.
```

## Udio

Udio 的主提示词同样先描述音乐身份和故事功能；若当前界面提供 manual tags、instrumental、lyrics、extend、remix 或 section 编辑，再把信息放入对应控件：

1. 主提示词保留人能读懂的戏剧弧；manual/tag 区只放平台接受的类型、情绪、乐器、年代和制作标签。
2. Instrumental cue 不要用假歌词承载镜头指令；把段落变化写成 `intro / development / turn / button` 与近似长度。
3. 需要转场时，分别生成“上一场尾段”和“下一场开段”，在 NLE/DAW 做调性、节拍、空间和尾音匹配；不要假设一次生成能精确对齐成片时间码。
4. Remix 用于保留已批准的动机/音色并只改变密度或结尾；每轮只改变一个结构变量。

Udio 版提示词示例：

```text
Instrumental neo-classical electronic underscore for an animated inventor's
failed test becoming a better idea. 96 BPM in 6/8, playful prepared piano,
small wood blocks, warm analog plucks, light bass clarinet. Intro is precise
and optimistic; at the failed launch, remove the pulse for one dry comic beat;
re-enter with the same three-note motif inverted and more curious, not bigger.
Finish with a short upward mechanical cadence that can pre-lap into the next
workshop scene. Clear middle register for dialogue. No vocals, ukulele,
whistling, epic brass, audience laughter, or stock comedy boings.
```

## ElevenLabs

ElevenLabs 的 Sound Effects 和 Music 分开处理。

### Sound Effects

把 UI/API 中的文本描述用于声学事件，把时长、loop、prompt influence 等当前可用参数留给控件或适配器，不要把数字埋在散文里后又假设会严格执行。

- 对同步音效写清 onset、主体、尾音和镜头/听者距离；
- 需要 loop 时描述稳定状态和无明显一次性事件，并使用界面/API 的 loop 选项（若当前提供）；
- 同一动作生成 3–5 个微差变体，避免复制粘贴造成机械重复；
- 复杂转场分别生成 source layer、air/motion layer、impact/body、tail，再按画面组合。

示例：

```text
A heavy laboratory safety door unlocks and slides open on a steel rail: two
quiet relay clicks, a short electric motor start, dense metal carriage movement,
one firm end-stop contact, then a natural industrial-room decay. Camera/listener
is two meters away, slightly off-axis. Realistic mass and mechanism, controlled
dynamics, clean isolated effect with one second of tail. No alarm, voice, music,
sci-fi laser, giant sub boom, extra impacts, or long cinematic whoosh.
```

### Music

若当前账户/地区提供 Eleven Music，用与通用音乐模板相同的 story job、段落、动机和 sync map；若界面提供 composition plan/sections，把每段的功能与近似长度分开填写。先要求可剪结构和干净结尾，再追求华丽音色。需要 SFX 与音乐共同转场时，避免两边同时占满低频和瞬态。

## 专业示例

### 纪录片事实揭示

- 画面：采访 → 档案文件特写 → 数据图；
- 功能：从问题转为可核验答案，不诱导定罪；
- 音乐：低密度、无恐怖低音、图表出现时才增加脉冲；
- 转场：文件翻页真实声做 match texture，音乐通过 L-cut 留尾；
- 音效：纸张、桌面、房间底单独生成/录制，不把“戏剧纸声”伪装成同期证据。

### 15 秒产品短片

- `00:00–00:03`：一个清楚的材质/功能 hook，不先放 logo sting；
- `00:03–00:10`：节奏与三次真实操作对应，但为旁白留中频；
- `00:10–00:13`：抽空一层，让可验证结果成为峰值；
- `00:13–00:15`：短品牌 button，尾音不遮 CTA；
- 生成 full、VO-safe、no-drums 和 2 秒 button 四版，平台裁切时重排而不是硬砍。

### 动画追逐转入安静发现

音乐不要只做线性加速。在发现前先减少打击乐和低频、保留角色动机，画面停下时让空间/呼吸进入，再以同一动机的慢速变体承接发现。转场音效用环境和材质匹配，不自动叠 riser、whoosh、hit 三件套。

## 生成迭代与成片验收

1. 每个平台先做 2–4 个结构差异明确的候选，不做十个同质“抽卡”。
2. 盲听时只看 story job、转折可读性、对白空间、编辑点和违禁含义；选中后才比较音色细节。
3. 记录 provider、界面/模型、prompt、设置、生成 ID、条款核对日期、成本与候选决定。
4. 把批准段落剪进画面后再验收；脱离画面的“好听”不能证明对故事有效。
5. 生成器的响度和结尾不可靠。编辑、交叉淡化、相位/单声道检查、EQ、ducking、响度与 true peak 在 DAW/NLE 后期完成。
6. 检查循环接缝、重复纹理、假空间、突然人声、额外事件、过度低频、编码伪影和版权相似性。
7. 为竖版、横版、预告、短 cutdown 重写 cue 结构；不要只裁掉母版头尾。

## 权利品牌与披露

平台模型、可用功能、导出、商用权限、训练/保留政策和地区限制会变化。每次正式使用前查看 [Suno Help](https://help.suno.com/)、[Udio Help Center](https://help.udio.com/) 与 [ElevenLabs Documentation](https://elevenlabs.io/docs/overview/capabilities/sound-effects) 的当前说明和条款，并在 provenance 记录核对日期；配置中的旧说明不能代替当前条款。

不上传无权使用的 rough cut、演员声音或客户素材。生成音效不能伪装成纪录片同期证据、真实人群反应或产品性能证明。需要披露时，以观众能理解的方式标记生成/合成声音；品牌项目同时检查 sonic logo、竞品相似性、平台 Content ID 和跨地区权利。
