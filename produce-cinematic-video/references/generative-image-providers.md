# GPT Image 2 与 Gemini Nano Banana 生图适配

## 使用边界

用图像模型完成参考帧、风格探索、局部修复、扩图或角色/场景设计，再把批准的画面交给视频模型。生图不是最终剪辑；输出仍需进入镜头清单、连续性检查、合成、字幕、声音和 QC。

不要把未授权私密素材、未成年人照片、身份证件、医疗/学校记录、受保密约束的项目画面或未取得权利的声音/肖像上传到远程 API。包含真人尤其未成年人时，优先本地合成；需要远程处理时必须重新取得明确授权并核对提供方当时的未成年人、肖像与数据规则。

## 最小 `.env.local`

只启用实际要用的一家；不要把下面两组同时复制，除非确实需要双提供方。

GPT Image 2：

```dotenv
PCV_OPENAI_IMAGE_ENABLED=true
PCV_OPENAI_IMAGE_MODEL=gpt-image-2
PCV_OPENAI_IMAGE_API_KEY=填入新密钥
```

Gemini Nano Banana：

```dotenv
PCV_GEMINI_IMAGE_ENABLED=true
PCV_GEMINI_IMAGE_ENDPOINT=https://中转地址/v1beta/models/实际模型:generateContent
PCV_GEMINI_IMAGE_MODEL=与端点路径一致的实际模型
PCV_GEMINI_IMAGE_API_KEY=填入新密钥
```

也可在本机终端逐个运行 `configure.py setup-provider openai-image` 或 `configure.py setup-provider gemini-image`。Gemini 向导要求完整的中转 `generateContent` 端点，并从路径自动提取模型；密钥输入隐藏，旧配置自动归档。不要把密钥粘贴到聊天或命令行参数。

`PCV_GEMINI_IMAGE_ENDPOINT` 是完整请求地址而不是根地址。配置后适配器原样调用该 HTTPS URL，不拼接官方域名、不静默回退；路径必须以 `/models/<model>:generateContent` 结尾，且 `<model>` 必须和 `PCV_GEMINI_IMAGE_MODEL` 一致。当前中转按其已验证协议使用 `?key=...`：endpoint 中不得写密钥，适配器只在请求内存中 URL 编码附加 `PCV_GEMINI_IMAGE_API_KEY`，不保存到日志、dry-run 或 provenance。图像输出参数按当前 REST 结构写入 `generationConfig.responseFormat.image`。指向 `/chat/completions` 的地址不能用于此适配器。旧的 `PCV_GEMINI_IMAGE_BASE_URL` 仅为官方兼容路径，不要与 endpoint 混用。

密钥如果曾出现在聊天、截图、日志或版本库中，先到提供方吊销并创建新密钥，再写入用户级 `.env.local`。不要用 `configure.py set` 或命令行参数传密钥。

## 选择提供方

- `openai_images`：调用 Images API 的 `/images/generations` 与 `/images/edits`；适合生成、带遮罩局部编辑和多图编辑。
- `gemini_images`：优先原样调用 `PCV_GEMINI_IMAGE_ENDPOINT` 的 Gemini `generateContent` 中转，以文本和可选参考图生成/编辑图像；适合对话式图像设计与参考图驱动的整体修改。
- Gemini 返回的生成图像按提供方说明带 SynthID。不要把这当作发行所需披露的替代品。

模型、功能、价格和政策会变化。每次实际调用前核对官方文档与控制台，不把内置默认当作永久保证。

## Dry-run

Dry-run 可以在 provider 尚未启用、没有密钥时检查路由、输入哈希和参数；它不会连接网络，也不会创建输出：

```text
python <skill-dir>/scripts/generate_image.py --provider openai_image generate --prompt-file shot.prompt.txt --output shot.png --size 1024x1536 --quality high --dry-run
```

```text
python <skill-dir>/scripts/generate_image.py --provider gemini_image edit --prompt-file edit.prompt.txt --input approved-reference.png --output edited.png --aspect-ratio 9:16 --image-size 2K --dry-run
```

## 实际调用

先在控制台确认当前价格、预算与数据上传范围，再显式添加两个一次性批准标志：

```text
python <skill-dir>/scripts/generate_image.py --provider openai_image generate --prompt-file shot.prompt.txt --output shot.png --size 1024x1536 --quality high --approve-remote-upload --approve-cost
```

OpenAI 遮罩编辑示例：

```text
python <skill-dir>/scripts/generate_image.py --provider openai_image edit --prompt-file repair.prompt.txt --input frame.png --mask mask.png --output repaired.png --approve-remote-upload --approve-cost
```

脚本拒绝覆盖输出和 provenance，错误信息不回显密钥或临时下载地址。每次成功调用会生成 `*.provenance.json`，记录模型、提示词、输入哈希、批准与输出哈希。

兼容中转把生成图放在 Gemini `inlineData`、常见 Base64 包装或候选文本中的 Markdown 临时 HTTPS 图片链接；链接只在内存中立即下载，不写入日志或 provenance。若成功响应没有可提取图像，脚本保存不含密钥、Base64 和临时 URL 的 `*.response.json` 摘要，并停止而不自动重试。

## 为视频设计参考帧

提示词按可验收镜头契约写：

1. 画面用途和镜头编号；
2. 主体身份、数量、姿态、空间关系与不可变化项；
3. 构图、景别、机位、光线、色彩与目标画幅；
4. 下一步视频动作需要的起始状态和可运动空间；
5. 禁止新增角色、畸形肢体、错误文字、标志漂移或水印等可观察偏差。

不要要求模型复刻原图中已有水印。使用无水印且权利状态清楚的源图；对站点水印、版权标识或来源标记的移除必须先确认权利与用途。

## 官方依据

- OpenAI：<https://developers.openai.com/api/docs/guides/image-generation>
- GPT Image 2：<https://developers.openai.com/api/docs/models/gpt-image-2>
- Gemini 图像生成：<https://ai.google.dev/gemini-api/docs/image-generation>
