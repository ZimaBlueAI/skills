# Seedance 类模型视频生成

## 目录

- [工作流定位](#工作流定位)
- [最小用户配置](#最小-envlocal)
- [输入安全](#输入安全)
- [模式约束](#模式约束)
- [Dry-run](#dry-run)
- [实际生成](#实际生成)
- [动画镜头提示词](#动画镜头提示词)
- [官方依据](#官方依据)

## 工作流定位

当用户明确要求“用 Seedance 类模型生成视频”时，必须先生成真实的模型视频镜头，再用 FFmpeg、NLE、Pillow/OpenCV 或合成软件完成选段、画幅、字幕、配音、音乐、混音和 QC。确定性平移缩放、HTML2Video 或静帧动画可以作为 animatic、故障预览或本地合成层，但不能冒充模型生成镜头。

推荐链路：

```text
批准的无水印参考图 → Seedance 图生视频 → 逐帧验收 → 本地剪辑/字幕/Qwen3-TTS/音乐 → QC
```

## 最小 `.env.local`

中国区 ModelArk/火山方舟默认根地址与当前 Seedance 2.0 模型已内置；通常只添加：

```dotenv
PCV_SEEDANCE_ENABLED=true
PCV_SEEDANCE_MODEL=doubao-seedance-2-0-260128
PCV_SEEDANCE_API_KEY=填入新密钥
```

推荐直接在本机终端运行 `python <skill-dir>/scripts/configure.py setup-provider seedance`，由隐藏输入向导写入这两项；不要把密钥发到聊天中。

控制台给出的模型 ID 不同时修改：

```dotenv
PCV_SEEDANCE_MODEL=控制台中的模型ID
```

只有使用其他地区或 BytePlus 账户时才添加 `PCV_SEEDANCE_BASE_URL`。密钥曾被打印、粘贴或提交过时必须先轮换；不要继续使用旧值。

配置后可运行只读鉴权，不创建生成任务：

`python <skill-dir>/scripts/seedance_video.py --provider seedance_video --auth-check`

## 输入安全

Seedance 2.0 当前不接受直接上传含真实人脸的本地参考图/视频。真人需先走提供方的授权资产库与人脸授权流程，再以 `asset://...` 使用；“用户拥有照片”不等于可以绕过该流程。

脚本据此区分：

- `--content-class animation`：动画、插画、卡通角色；
- `--content-class nonperson`：产品、物件、风景、抽象画面且没有真人脸；
- `--content-class real-person-authorized`：只允许提供方已批准的 `--reference-asset asset://...`，拒绝本地真人图。

未成年人及其他可识别真人影像默认留在本地处理；只有取得明确授权且提供方当前规则允许时，才进入其授权资产流程。动画参考与真人素材分开管理，不以动画上传批准推定真人上传批准。

对知名动画角色、品牌图形或其他受保护素材，在 `--rights-basis` 中记录来源、用途与发行边界。私人用途不自动获得商业发布、广告投放或衍生商品权利。

提供方仍可能依据自身政策拒绝已获用户授权或仅供私人使用的知名角色素材。若结果为版权/敏感内容策略失败：

1. 保存 task 与 result 记录，明确标记为提供方策略拒绝；
2. 不通过删品牌名、同义改写或连续重试来规避审核；
3. 不把失败误报为网络故障，也不把静帧运动冒充模型动画；
4. 改为先用已配置的图像模型设计轮廓、配色、服装和面部均明显不同的原创角色，经用户确认后再生成视频；
5. 新提交仍需重新核对预算和远程上传批准。

这类原创重设计使用 `references/generative-image-providers.md` 的 GPT Image 或 Gemini 适配器。源图只可用作场景意图参考，提示词不得要求复刻角色、标志或片名。

## 模式约束

- 文生视频：只给提示词；
- 首帧图生视频：一个 `--first-frame`；
- 首尾帧：同时给 `--first-frame` 与 `--last-frame`；
- 多模态参考图：一个或多个 `--reference-image`，角色为 `reference_image`；
- 首/尾帧模式与参考图模式互斥；
- Seedance 2.0 常用时长为 4–15 秒，参考图最多 9 张；以当时官方文档和账户模型为准。

需要独立控制对白、音乐和音效的项目通常把 `--generate-audio` 留空，使用已批准的
TTS 与独立声音设计做后期，避免模型音轨与对白争抢。`--watermark` 默认关闭，只控制
提供方新加的 AI 水印；它不会合法或可靠地清除源图已有水印，因此必须使用干净来源图。

## Dry-run

```text
python <skill-dir>/scripts/seedance_video.py --provider seedance_video --prompt-file shot.prompt.txt --first-frame approved-animation.png --content-class animation --rights-basis "user supplied authorized animation reference; approved project scope; no external publication" --ratio adaptive --duration 5 --output shot.mp4 --dry-run
```

Dry-run 不读取密钥、不发起任务、不创建输出，只打印脱敏请求计划、输入哈希与所需批准。

## 实际生成

核对价格、预计次数和上传内容后：

```text
python <skill-dir>/scripts/seedance_video.py --provider seedance_video --prompt-file shot.prompt.txt --first-frame approved-animation.png --content-class animation --rights-basis "user supplied authorized animation reference; approved project scope; no external publication" --ratio adaptive --duration 5 --output shot.mp4 --approve-remote-upload --approve-cost
```

脚本会：

1. `POST /contents/generations/tasks` 创建异步任务；
2. 定时 `GET /contents/generations/tasks/{id}`；
3. 成功后立即下载临时 `video_url`；
4. 保存 task、result 与 provenance，均不含密钥和临时下载 URL；
5. 拒绝覆盖已有文件。

本地图片会以内联 Base64 进入请求，编码后体积约增加三分之一。保留无损母图不动，另做经目视验收的上传副本：动画首帧通常先缩到目标画幅附近（如 1280×720）并导出高质量 JPEG/WEBP；不要为减小请求而破坏线稿、文字、面部或透明边缘。大 PNG 在网络/中转不稳定时可能造成 TLS EOF，但“连接断开”并不能证明服务端一定没有接到创建请求。

任务被中断时，保留 `*.task.json` 中的 task ID；不要重复付费提交。使用恢复模式只查询同一个任务并下载结果，不会再次 `POST`：

```text
python <skill-dir>/scripts/seedance_video.py --provider seedance_video --resume-task-record group-shot.mp4.task.json
```

轮询遇到 TLS、超时、429 或 5xx 时，会有限次数重试同一 task ID；绝不自动重建任务。终端失败会保存 `*.result.json`。若下载暂时中断，task record 保持可恢复，重新运行上面的命令即可。

如果 `POST` 创建阶段在返回 task ID 前发生 TLS/超时，结果属于“是否已创建未知”。不要立刻再次付费提交。先只读查看最近任务：

```text
python <skill-dir>/scripts/seedance_video.py --provider seedance_video --list-recent 10
```

它只显示 task ID、状态、模型和时间等安全字段，不显示 prompt、输入、临时 URL 或密钥。把时间、模型与控制台记录对照；只有确认没有新任务，或用户明确批准另一笔费用后，才能重新 `POST`。发现对应 task ID 时先建立/核对 task record，再使用恢复模式，绝不靠重复提交“试试看”。

## 动画镜头提示词

写时间化、可验收动作，不堆叠“高级、电影感、丝滑”：

```text
保持参考图中全部二维卡通角色的数量、配色、轮廓与服装不变。
0–2秒：角色看向镜头，轻轻眨眼和挥手；动作幅度小，脚底保持接触地面。
2–4秒：彩纸从上方缓慢落下，角色依次露出庆祝表情；不新增人物。
4–5秒：镜头轻微推进后稳定停住，预留上方字幕空间。
保持二维平涂线稿；禁止角色融合、肢体增加、文字变形、标志漂移、突然切镜和源图外水印。
```

一条生成镜头只承担一个叙事动作。先生成短预览并逐帧查角色数量、脸部、手脚、轮廓、文字、闪变和接触，再决定是否进入成片。

### 物理动作提示词铁律（实战教训）

1. **动作动词必须与首帧实际状态一致。** 首帧里剑已出鞘却写"拔剑"，模型会凭空生成
   剑鞘并长出第二个剑柄；首帧无门却写"推门"，会凭空长门。动作描述**禁止引入首帧中
   不存在的物件**；必要时显式否定（"画面中没有剑鞘，只有一个剑柄一个护手"）。
2. **同一核心物理偏差第二次出现时，停止收紧措辞重掷**——那是结构问题不是措辞问题。
   回到首帧重审"提示词假设了什么首帧里没有的东西"，换结构假设后再生成一次。
3. **持物/接触类动作是高危区**（握持、抽拔、插入、递接、开合）：涉及手-物接触点变化的
   动作，静帧抽检容易漏（单帧看着都对，动态里换手/穿模才显形）——此类镜头必须
   **实时看动态**而非只看抽帧，属导演审片必查项。
4. 物理正确性目前仍是生成视频最弱环节：能用"状态 A→状态 B"的姿态变化描述，就不要
   写复杂操作过程；实在需要复杂操作，把它拆成多条各承担一步的镜头。

## 官方依据

- Seedance 2.0 创建任务：<https://docs.byteplus.com/en/docs/modelark/1520757>
- 查询任务：<https://docs.byteplus.com/en/docs/modelark/1521309>
- 官方 API 教程：<https://docs.byteplus.com/api/docs/ModelArk/2298881>
- 真人授权资产：<https://docs.byteplus.com/en/docs/ModelArk/2315856>
