# Prompt templates for character production

These templates are model-agnostic. Attach the original character image and, when relevant, the approved style card. Use image editing/reference modes when available. Replace bracketed fields and remove instructions that do not apply.

Translate a named animation reference into observable traits such as line weight, shape language, palette, texture, depth, and background treatment. Do not ask for an exact copy or imply official affiliation.

## Contents

- [Canonical front view](#1-canonical-front-view)
- [Style transfer without identity drift](#2-style-transfer-without-identity-drift)
- [Neutral turnaround](#3-neutral-turnaround--三视图或四视图)
- [Six-expression sheet](#4-six-expression-sheet)
- [Story-led action sheet](#5-story-led-action-sheet)
- [Repair one failed view](#6-repair-one-failed-view)
- [Visual acceptance prompt](#7-visual-acceptance-prompt-for-a-reviewing-model)

## 1. Canonical front view

```text
任务：把附件中的孩子原创角色整理成一张可继续制作动画的“标准正面图”。

角色不能丢的三个地方：
1. [轮廓锚点]
2. [脸/身体锚点]
3. [颜色/材质/配件锚点]

只整理画面，不重新发明角色。保留孩子故意画得奇怪、夸张或不对称的地方。
画面：单个角色，全身，正面，中性自然站姿/坐姿，双脚或身体底部完整可见，手臂不遮挡身体关键结构。
风格语言：[线条]；[形状]；[色彩]；[材质]；[明暗与空间]。
背景：透明；若不支持透明，用均匀纯色背景。四周留出安全边距。
不要文字、边框、网格、投影、第二个角色、额外道具或自动补出的装饰。
```

## 2. Style transfer without identity drift

```text
任务：把“角色原稿”迁移到“共同风格卡”的绘制语言中。

只能改变：线条粗细与手感、上色材料、色块边缘、明暗方式、画面质感。
不能改变：物种、年龄感、头身比、身体结构、三个身份锚点、左右不对称、服装结构和配件位置。

角色原稿的三个身份锚点：
- [锚点 1]
- [锚点 2]
- [锚点 3]

共同风格卡拆解：
- 线条：[例如深色铅笔感、粗细有变化]
- 形状：[例如圆角几何、轮廓简洁]
- 色彩：[例如低饱和主色 + 一个高亮点色]
- 材质：[例如纸张颗粒、平涂水粉]
- 空间：[例如少量体积感、不做写实光影]

输出一张全身正面候选图，透明背景，四周留白。不要偷偷“美化”或补全未经作者同意的细节。
```

## 3. Neutral turnaround / 三视图或四视图

```text
基于附件中已经通过作者确认的标准正面图，制作同一个角色的角色转面设定。

视图：[正面、左侧、背面；如果需要再加右侧]。
所有视图必须使用同一个中性姿势家族、同一头身比、同一身体高度、同一脚底线、同一镜头高度和同一绘制风格。

每个视图都必须保留：
- [轮廓锚点]
- [脸/身体锚点]
- [颜色/材质/配件锚点]
- [左侧专属细节]
- [右侧专属细节]

侧面和背面只补充空间结构，不重新设计角色。不要把坐姿改成跑姿，不要增减四肢、耳朵、尾巴、口袋或装饰。
角色之间不要重叠；每格完整全身；背景透明或均匀纯色；不要文字、箭头、阴影或场景。
```

When a model struggles with a four-view sheet, generate one missing view at a time from the canonical front plus the last approved adjacent view. Normalize views deterministically afterward.

## 4. Six-expression sheet

```text
为附件中的同一个角色制作 2×3 表情表：平静、开心、担心、生气/坚定、惊讶、思考。

保持相同头部角度、脸部比例、耳朵/角/头发轮廓、眼睛颜色、面部花纹、线条、材质和光线。
主要通过眉眼、嘴形、脸颊张力和很小的头部动作表达，不改变年龄、物种或脸型。
每格只出现一个完整头像或半身像；不重叠；格间留出宽边距；背景透明或统一纯色。
不要文字标签、表情符号、边框和额外道具。
```

## 5. Story-led action sheet

```text
为附件中的同一个角色制作 [2×3 / 3×3] 动作表。

故事真正需要的动作：
1. [待机/倾听]
2. [走路]
3. [跑步]
4. [跳起或受惊]
5. [角色标志性互动]
6. [休息/思考]

每格保持三个身份锚点、固定比例、服装、花纹、左右细节和绘制风格。动作可以改变姿态，但不能改变角色身份。
每格单个完整角色，四周有切片余量，彼此不重叠。必要道具与角色保持清晰间隔；非必要道具单独成格。
背景透明；若不支持透明，使用均匀亮绿色或与角色完全不同的纯色。不要文字、编号、格线、复杂阴影或场景。
```

## 6. Repair one failed view

```text
只修复附件中的 [左侧/背面/某动作]，不要重画整套。

问题：[例如左耳花纹跑到右耳；身体变高；尾巴少一节]。
以已通过的 [正面图/相邻视图] 为身份依据。
必须恢复：[相关身份锚点和不对称说明]。
保持原来的姿势、画布、脚底线、比例、线条和材质。只改列出的问题，其他部分不动。
输出单个完整角色，透明背景，无文字。
```

## 7. Visual acceptance prompt for a reviewing model

Use this only as a second opinion; the author still decides.

```text
比较这些视图是否是同一个角色。逐项检查，不重新生成图片：
1. 轮廓和头身比；
2. 三个身份锚点；
3. 四肢、耳朵、角、尾巴数量；
4. 颜色、花纹、衣服与配件；
5. 左右不对称是否放在正确一侧；
6. 是否属于同一中性姿势家族；
7. 脚底线和视觉高度；
8. 是否有裁切、邻格碎片或背景残留。

只输出“通过 / 需修改 / 无法判断”，并列出可以直接动手修的具体差异。不要评价孩子画得好不好。
```
