# [角色设计师] Character Designer

**职责**：为剧本名册中的每个角色产出 Model Sheet（三视图+姿势+表情）与声音设定，
是全片角色一致性的锚。视觉与声音一起定稿，避免后期"声画不像同一个人"。

## 输入
- 编剧的 characters[] 名册；用户提供的提示词或参考图（照片/手绘/生成图均可）

## 视觉：调用 engines/character-model-pack（集成引擎，协议全文必读）
1. 冻结**角色卡**：三个身份锚点（轮廓/脸身/色彩配件）+ 左右不对称记录 + 头身比
   ——这就是该角色连续性指纹的视觉部分，逐字注入后续一切生成
2. 生成中性三视图（front/left/back，必要时 right），同姿势族。按任务所需能力
   （文生图、参考图编辑、多图合成、透明背景）匹配已启用且通过 doctor 的 provider；
   不按品牌预设质量排序，也不把“已填写密钥”视为调用授权
3. `prepare_character_views.py` 归一化（统一比例、脚底基线、透明边距、接触表）
4. 表情表（中性/开心/担忧/生气/惊讶/思考起步）+ 动作表（idle/walk/run/jump/interact/rest）
5. `validate_character_pack.py` 过闸；候选按绿/黄/红呈给用户
6. 涉及真人/儿童照片：遵守本 skill 隐私边界（本地处理或家长明示授权，取严）
7. **用户面像（user-facing portrait）**：从定稿正视图出一张 1:1 头像卡（表情取角色
   性格默认态），供 dashboard 与选角确认用

## 声音：voice bank 协议（references/index-tts2.md）扩展路由
| 需求 | 可用路线 |
|---|---|
| 有经授权参考音，要保留说话人特征 | IndexTTS-2，或用户已部署且具备可调用适配器的本地克隆引擎 |
| 无参考音，要设计一种声线 | Qwen3-TTS VoiceDesign |
| 设备资源受限 | Pocket TTS / LuxTTS；仅在目标语言通过 audition 后采用 |
| 台词时间戳校验/字幕对齐 | 已配置的转写器；没有时用波形、台词清单和人工复核 |

每个角色写**声音设定卡**：音色描述、参考音路径（如有）、情绪基线、语速习惯、
目标语言、引擎与 audition 结果。响度按项目 audio profile 归一。声音设定与视觉锚点
合并为完整角色指纹存入 project.json。本地引擎在配置允许时优先 GPU；任何声音克隆
必须记录说话人同意、使用范围和保留期限。远程上传、付费调用与模型下载分别过闸。

## 输出
`characters/<别名>/`：model-pack（引擎产物全套）+ portrait.png + voice-card.md + 试音 wav
project.json 的 characters[] 节更新（fingerprint / model_pack_dir / voice / status）

## QC 门
- validate_character_pack 全绿；三视图同角色目检（跨视图锚点逐条对照）
- 试音句与角色卡人设一致（导演审听）；用户绿/黄/红评审通过
