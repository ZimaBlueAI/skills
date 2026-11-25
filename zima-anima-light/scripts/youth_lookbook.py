"""Youth lookbook — 40 style packs + 21 masters = 61 design agents.

Research basis (youth-safe, no real-person likeness / no horror):
- CN youth short-video prefs: humor, humanities, hotspot, daily, anime/game (青研中心)
- Edu film crafts: live drama, doc, animation, found-footage; whiteboard / cut-out / stop-motion
- Teen animation: clean cel, webtoon, guofeng, ink, clay, family 3D, toy miniature
- Soft Studio rule: prompts describe light/shape/motion only; never real celebrity or adult themes
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
PACKS_DIR = SKILL / "styles" / "packs"
MASTERS_PATH = SKILL / "masters" / "catalog.json"
LOOKBOOK_PATH = SKILL / "styles" / "lookbook_61.json"
AGENTS_DIR = SKILL / "agents" / "design"

YOUTH_AVOID_BASE = [
    "horror",
    "gore",
    "realistic celebrity likeness",
    "adult romance",
    "weapon fetish",
    "dark occult",
]

# --- 40 style packs ---------------------------------------------------------

STYLES: list[dict[str, Any]] = [
    # Campus / daily
    {
        "id": "warm_school",
        "title": "暖色校园",
        "category": "campus",
        "medium": ["live", "short", "anime"],
        "prompt_prefix": "warm soft daylight, clean school environment, friendly teen characters, readable faces, simple backgrounds, cohesive warm color grade",
        "prompt_zh": "暖色软日光，干净校园环境，青少年面孔清晰可读，背景简洁，统一暖调",
        "preview": "午后教室窗边，同学讨论手绘海报",
        "signature": ["暖日光", "脸清楚", "背景干净"],
        "agent": "你是暖色校园短片设计代理：每镜写清谁在做什么、光从哪边来；禁止抽象情绪堆砌。",
    },
    {
        "id": "campus_golden_hour",
        "title": "操场黄金时刻",
        "category": "campus",
        "medium": ["live", "short", "film"],
        "prompt_prefix": "golden-hour school field, long soft shadows, teens after class, warm rim light, clear silhouettes against sky",
        "prompt_zh": "放学后操场黄金时刻，长软阴影，暖轮廓光，人物剪影贴着天空可读",
        "preview": "夕阳下跑道尽头，两人并肩走远",
        "signature": ["金时轮廓光", "剪影可读", "放学节奏"],
        "agent": "你盯「放学后」的时间压力：镜头要看见太阳位置与人物走向，不堆伤感词。",
    },
    {
        "id": "club_room_cozy",
        "title": "社团室暖窝",
        "category": "campus",
        "medium": ["live", "anime", "short"],
        "prompt_prefix": "cozy clubroom clutter that stays readable, desk lamps, posters on wall, teens collaborating, soft practical lights",
        "prompt_zh": "社团室杂物仍可读，台灯与墙上海报，青少年协作，柔和实用光",
        "preview": "社团室长桌，几人围着拼手工模型",
        "signature": ["实用光", "杂物可读", "协作构图"],
        "agent": "设计代理强调道具功能：每个杂物要服务剧情，不让背景变成噪声。",
    },
    {
        "id": "library_quiet_light",
        "title": "图书馆静光",
        "category": "campus",
        "medium": ["live", "short", "doc"],
        "prompt_prefix": "quiet library daylight through tall windows, soft dust motes, focused teen studying, calm cool-warm mix, low noise",
        "prompt_zh": "图书馆高窗日光，细尘浮动，专注阅读的青少年，冷暖安静混光",
        "preview": "书架过道尽头，一人翻开笔记本",
        "signature": ["高窗光", "安静景深", "专注动作"],
        "agent": "用动作代替旁白：翻页、标注、抬头对视，保持声场克制。",
    },
    {
        "id": "sports_field_kinetic",
        "title": "运动场动能",
        "category": "campus",
        "medium": ["live", "short", "anime"],
        "prompt_prefix": "kinetic sports field, clear action beats, readable body mechanics, bright daylight, youth athletes, no injury close-ups",
        "prompt_zh": "运动场动能镜头，动作节拍清楚，肢体力学可读，明亮日光，青年运动员，无受伤特写",
        "preview": "三分线外起跳投篮的定格瞬间",
        "signature": ["动作节拍", "肢体可读", "明亮外光"],
        "agent": "运动片设计代理：一镜一主动作；慢动作只服务读懂，不炫技血腥。",
    },
    {
        "id": "festival_lantern_soft",
        "title": "节庆灯笼柔光",
        "category": "campus",
        "medium": ["live", "anime", "short"],
        "prompt_prefix": "soft festival lantern light, warm paper glow, family-friendly crowd, teens holding lanterns, gentle bokeh, no stampede",
        "prompt_zh": "节庆灯笼柔光，纸灯暖晕，合家欢人群，青少年提灯，轻柔虚化，无拥挤踩踏",
        "preview": "校园灯会小径，纸灯照亮笑脸",
        "signature": ["纸灯暖晕", "人群有序", "节日亲和"],
        "agent": "节庆戏只写灯色与人物目标，避免喧闹失控与迷信恐吓。",
    },
    {
        "id": "travel_diary_handheld",
        "title": "旅行手账手持",
        "category": "daily",
        "medium": ["live", "short", "vlog"],
        "prompt_prefix": "youth travel diary look, gentle handheld framing, scenic but simple backgrounds, clear faces, notebook and map props",
        "prompt_zh": "青年旅行手账感，轻手持构图，风景背景简洁，面孔清楚，笔记本与地图道具",
        "preview": "车站前摊开地图，手指点到下一站",
        "signature": ["轻手持", "地图道具", "旅途目标"],
        "agent": "每场写清『下一站去哪』；手持晃动有节制，保证脸可读。",
    },
    {
        "id": "family_kitchen_warm",
        "title": "家庭厨房暖调",
        "category": "daily",
        "medium": ["live", "short", "film"],
        "prompt_prefix": "warm family kitchen, practical overhead light, teens helping cook, steam and chopping readable, cozy domestic color",
        "prompt_zh": "家庭厨房暖调，顶灯实用光，青少年帮忙做饭，蒸汽与切菜动作可读",
        "preview": "灶台前递一碗汤，窗外傍晚",
        "signature": ["厨房实用光", "家务动作", "亲情节制"],
        "agent": "家庭戏靠动作传递关系：递碗、并肩切菜，不煽情旁白。",
    },
    # City / lyric night (safe)
    {
        "id": "night_city_glow",
        "title": "夜城灯带",
        "category": "city",
        "medium": ["live", "anime", "short"],
        "prompt_prefix": "safe night city glow, distant light ribbons, teens on overpass sharing earphones, soft neon reflections, no crime tone",
        "prompt_zh": "安全夜城灯带，远处灯带，天桥上分享耳机的同学，柔和霓虹反光，无犯罪气质",
        "preview": "天桥上看远处灯带，同学分享耳机",
        "signature": ["远灯带", "柔霓虹", "同伴并排"],
        "agent": "夜戏保持安全氛围：灯色服务情绪，不写危险街区与暴力暗示。",
    },
    {
        "id": "rainy_window_lyric",
        "title": "雨窗抒情",
        "category": "lyric",
        "medium": ["live", "anime", "film"],
        "prompt_prefix": "rainy window lyric mood, droplets on glass, soft interior warm light, teen looking out, gentle seasonal turn",
        "prompt_zh": "雨窗抒情，玻璃水珠，室内暖光，青少年望向窗外，细小时令转折",
        "preview": "教室窗上雨痕，一人擦雾看见操场",
        "signature": ["雨珠层", "内外光差", "细小转折"],
        "agent": "抒情不等于空洞：转折必须落到一个可见动作（擦雾、推窗、收伞）。",
    },
    # Education / knowledge
    {
        "id": "whiteboard_explainer",
        "title": "白板讲解",
        "category": "edu",
        "medium": ["edu", "short", "mg"],
        "prompt_prefix": "whiteboard explainer animation, clean marker lines appearing in order, clear diagrams, friendly teen-friendly narration space, bright flat light",
        "prompt_zh": "白板讲解动画，马克笔线条按序出现，图表清楚，留旁白空间，明亮平光",
        "preview": "白板上画出水循环箭头，旁白停半拍",
        "signature": ["按序出现", "图表清楚", "旁白气口"],
        "agent": "科普设计代理：一屏一结论；图形先于术语；禁恐吓式『不学就会怎样』。",
    },
    {
        "id": "flat_infographic_mg",
        "title": "扁平信息图MG",
        "category": "edu",
        "medium": ["mg", "edu", "short"],
        "prompt_prefix": "flat infographic motion graphics, bold simple shapes, limited palette, kinetic type, teen STEM explainers, no clutter",
        "prompt_zh": "扁平信息图动态图形，大胆简单形状，有限配色，动态字效，青少年 STEM 讲解，不堆杂",
        "preview": "三个色块弹出对应三个实验步骤",
        "signature": ["有限色", "形状先行", "步骤弹出"],
        "agent": "MG 代理强制『步骤可视化』：数字、箭头、对照，一眼能复述。",
    },
    {
        "id": "science_lab_curious",
        "title": "科学实验室好奇",
        "category": "edu",
        "medium": ["live", "edu", "anime"],
        "prompt_prefix": "curious science lab for teens, bright safe lighting, clear glassware, supervised experiment gestures, wonder without hazard close-ups",
        "prompt_zh": "青少年科学实验室，明亮安全光，器皿清楚，有监护的实验手势，好奇感，无危险特写",
        "preview": "护目镜下观察烧杯颜色变化",
        "signature": ["安全光", "器皿可读", "好奇手势"],
        "agent": "实验戏必须出现护具与步骤；禁止危险操作示范。",
    },
    {
        "id": "map_journey_geo",
        "title": "地图旅程地理",
        "category": "edu",
        "medium": ["mg", "edu", "anime"],
        "prompt_prefix": "animated map journey geography style, path drawing across terrain, landmark icons, clear scale cues, exploratory teen tone",
        "prompt_zh": "动画地图旅程地理风，路线在地形上画出，地标图标，比例尺清楚，探索型青少年语气",
        "preview": "地图上的虚线从海岸连到山区小镇",
        "signature": ["路线绘制", "地标图标", "比例尺"],
        "agent": "地理代理每镜交代『从哪到哪、为什么走这条路』。",
    },
    {
        "id": "safety_edu_friendly",
        "title": "安全教育友好风",
        "category": "edu",
        "medium": ["edu", "anime", "short"],
        "prompt_prefix": "friendly safety education animation, calm colors, clear do-and-dont panels, empowering teens, no trauma imagery",
        "prompt_zh": "友好安全教育动画，冷静配色，正误对照分格，赋能青少年，无创伤画面",
        "preview": "过马路三步对照图：停看走",
        "signature": ["正误对照", "冷静色", "赋能语气"],
        "agent": "安全片禁止恐吓；用正确示范 + 简短错误对照。",
    },
    {
        "id": "nature_field_notes",
        "title": "自然田野笔记",
        "category": "edu",
        "medium": ["live", "doc", "short"],
        "prompt_prefix": "nature field-notes documentary look, sketchbook overlays, soft outdoor light, teen observer, respectful wildlife distance",
        "prompt_zh": "自然田野笔记纪录片感，速写本叠加，柔和外光，青少年观察者，与野生动物保持尊重距离",
        "preview": "草甸上摊开速写本，画下一只停在远处的鸟",
        "signature": ["速写叠加", "观察距离", "外光柔和"],
        "agent": "自然代理强调尊重距离与不打扰；禁止惊扰动物镜头。",
    },
    # Animation / craft
    {
        "id": "paper_cut_day",
        "title": "日间剪纸",
        "category": "craft",
        "medium": ["anime", "stopmotion", "short"],
        "prompt_prefix": "daylight paper-cut layers, crisp silhouettes, soft window light, handmade craft texture, family-friendly",
        "prompt_zh": "日间剪纸分层，剪影利落，窗边柔光，手作纸质感，合家欢",
        "preview": "窗台上的剪纸小人向太阳举手",
        "signature": ["分层剪影", "手作纸感", "窗光"],
        "agent": "剪纸代理：每层颜色不超过三色；动作靠层移，不靠复杂表情。",
    },
    {
        "id": "ink_adventure",
        "title": "墨色冒险",
        "category": "craft",
        "medium": ["anime", "film", "short"],
        "prompt_prefix": "stylized ink-and-wash adventure look, clear silhouettes, gentle motion, family-friendly fantasy, generous negative space",
        "prompt_zh": "水墨风格化冒险，剪影清楚，动作轻柔，合家欢奇幻，大量留白",
        "preview": "少年持地图站在山径，远处小镇灯火",
        "signature": ["墨色留白", "剪影路程", "轻奇幻"],
        "agent": "墨色冒险代理：奇幻服务路程目标，不堆妖魔鬼怪恐吓。",
    },
    {
        "id": "toy_storyboard",
        "title": "玩具分镜桌面",
        "category": "craft",
        "medium": ["stopmotion", "3d", "edu"],
        "prompt_prefix": "desktop toy storyboard miniature, soft tabletop lighting, readable props, gentle explanation vibe",
        "prompt_zh": "桌面玩具分镜微缩，柔和桌灯光，道具可读，温和讲解感",
        "preview": "桌面微缩街道，玩具巴士转弯",
        "signature": ["桌面微缩", "道具可读", "讲解光"],
        "agent": "微缩代理先列道具清单，再写机位；适合科普与产品说明向。",
    },
    {
        "id": "clay_stop_motion",
        "title": "黏土定格",
        "category": "craft",
        "medium": ["stopmotion", "short", "comedy"],
        "prompt_prefix": "clay stop-motion youth comedy, fingerprint texture kept, bright miniature sets, rounded characters, gentle slapstick",
        "prompt_zh": "青少年黏土定格喜剧，保留指纹质感，明亮微缩布景，圆润角色，温和闹剧",
        "preview": "黏土小人把书包抛过桌子接到另一边",
        "signature": ["指纹质感", "圆润角色", "温和闹剧"],
        "agent": "定格代理写清逐帧位移；喜剧靠道具失误，不靠伤害玩笑。",
    },
    {
        "id": "watercolor_storybook",
        "title": "水彩绘本",
        "category": "craft",
        "medium": ["anime", "film", "short"],
        "prompt_prefix": "watercolor storybook animation, soft paper grain, gentle washes, pencil underlines, tender youth tales",
        "prompt_zh": "水彩绘本动画，纸纹柔和，淡彩晕染，铅笔淡线，温柔青少年故事",
        "preview": "淡彩街道，铅笔勾出骑车少年",
        "signature": ["纸纹淡彩", "铅笔淡线", "温柔叙事"],
        "agent": "绘本代理控制色层：天空一色、地面一色、人物一点强调色。",
    },
    {
        "id": "guofeng_gongbi",
        "title": "国风工笔插画",
        "category": "craft",
        "medium": ["anime", "short", "film"],
        "prompt_prefix": "Chinese gongbi illustration style for youth, fine clean lines, soft mineral colors, silk texture hint, respectful traditional motifs",
        "prompt_zh": "青少年向国风工笔插画，细净线描，柔和石色，绢纹暗示，传统纹样尊重表达",
        "preview": "工笔庭院，少年整理书箱准备远行",
        "signature": ["细净线", "石色柔和", "纹样克制"],
        "agent": "国风代理禁用封建迷信恐吓与刻板丑化；纹样服务场景，不堆满。",
    },
    {
        "id": "cel_clean_anime",
        "title": "干净赛璐璐动画",
        "category": "craft",
        "medium": ["anime", "short"],
        "prompt_prefix": "clean cel-shaded youth anime look, crisp outlines, flat fills, readable expressions, school-life friendly, original characters only",
        "prompt_zh": "干净赛璐璐青年动画，利落描边，平涂填色，表情可读，校园友好，仅原创角色",
        "preview": "走廊转身挥手，表情清楚不挤脸",
        "signature": ["利落描边", "平涂", "表情可读"],
        "agent": "动画代理禁止模仿受保护角色与商标；表情优先于特效。",
    },
    {
        "id": "webtoon_soft",
        "title": "柔和条漫风",
        "category": "craft",
        "medium": ["anime", "short"],
        "prompt_prefix": "soft webtoon youth style, slender friendly proportions, gentle gradients, vertical-panel friendly framing, school romance kept wholesome",
        "prompt_zh": "柔和条漫青年风，亲和修长比例，轻渐变，适合竖分格构图，校园情感保持清爽",
        "preview": "竖构图楼梯口对视，留白给气泡",
        "signature": ["竖分格", "轻渐变", "清爽情感"],
        "agent": "条漫代理：情感戏停在『关心/鼓励』，不写成人亲密。",
    },
    {
        "id": "pixel_retro_game",
        "title": "复古像素游戏",
        "category": "craft",
        "medium": ["game", "short", "mg"],
        "prompt_prefix": "retro pixel-art game look for teens, limited palette, readable 16-bit characters, cheerful adventure, no horror sprites",
        "prompt_zh": "青少年复古像素游戏风，有限色板，16-bit 角色可读，明快冒险，无恐怖精灵",
        "preview": "像素小镇入口，角色举起地图道具",
        "signature": ["有限色板", "像素可读", "明快冒险"],
        "agent": "像素代理关卡目标一句话写清；禁止恐怖跳杀与赌博机。",
    },
    {
        "id": "scrapbook_collage",
        "title": "手账拼贴",
        "category": "craft",
        "medium": ["short", "mv", "vlog"],
        "prompt_prefix": "scrapbook collage youth aesthetic, torn paper edges, washi tape, polaroid frames, diary captions, craft paper texture",
        "prompt_zh": "手账拼贴青年美学，撕边纸、胶带、拍立得框、日记标题，牛皮纸质感",
        "preview": "拍立得与车票贴在手账页，箭头指向『今天』",
        "signature": ["撕边纸", "拍立得框", "日记标题"],
        "agent": "拼贴代理适合回忆杀与 MV；每页一个主题，不堆贴纸。",
    },
    {
        "id": "family_3d_round",
        "title": "合家欢圆润3D",
        "category": "craft",
        "medium": ["3d", "film", "short"],
        "prompt_prefix": "family-friendly rounded 3D animation, soft subsurface skin, big readable eyes, bright inviting sets, gentle comedy timing",
        "prompt_zh": "合家欢圆润3D动画，柔和次表面皮肤，大而可读的眼睛，明亮友好场景，温和喜剧节拍",
        "preview": "圆润角色推开彩色房门探头",
        "signature": ["圆润比例", "友好布景", "温和节拍"],
        "agent": "3D 合家欢代理：造型亲和，动作夸张但不惊吓幼儿观众。",
    },
    {
        "id": "toy_plastic_3d",
        "title": "玩具塑料3D",
        "category": "craft",
        "medium": ["3d", "stopmotion", "short"],
        "prompt_prefix": "matte toy-plastic 3D look, rounded joints, bright solid colors, miniature set lighting, playful product-story vibe",
        "prompt_zh": "哑光玩具塑料3D，圆关节，明亮纯色，微缩布光，玩味产品故事感",
        "preview": "塑料小车驶过积木桥",
        "signature": ["哑光塑料", "纯色块", "微缩布光"],
        "agent": "玩具3D代理适合品牌友好短片；避免真实商标外观。",
    },
    # Genre looks
    {
        "id": "soft_fantasy_silhouette",
        "title": "轻奇幻剪影",
        "category": "genre",
        "medium": ["anime", "film", "short"],
        "prompt_prefix": "soft fantasy silhouette adventure, readable outlines, gentle magic glow, youth quest goals, no dark occult symbols",
        "prompt_zh": "轻奇幻剪影冒险，轮廓可读，温和魔法光晕，青年任务目标，无黑暗邪典符号",
        "preview": "山脊剪影，杖尖一点柔光指示方向",
        "signature": ["轮廓优先", "柔魔法光", "任务目标"],
        "agent": "奇幻代理魔法只服务『指路/守护/解谜』，禁止诅咒恐吓。",
    },
    {
        "id": "soft_scifi_campus",
        "title": "软科幻校园",
        "category": "genre",
        "medium": ["anime", "live", "short"],
        "prompt_prefix": "soft sci-fi school campus, friendly gadgets, clean near-future design, hopeful teen inventors, no dystopia dread",
        "prompt_zh": "软科幻校园，友好小装置，干净近未来设计，乐观青少年发明者，无反乌托邦压抑",
        "preview": "走廊里悬浮课本轻轻跟在学生身后",
        "signature": ["友好装置", "近未来干净", "乐观发明"],
        "agent": "软科幻代理科技服务学习与互助，不写监视压迫世界。",
    },
    {
        "id": "mystery_club_clean",
        "title": "清爽社团谜题",
        "category": "genre",
        "medium": ["live", "anime", "short"],
        "prompt_prefix": "clean mystery club for teens, clue boards, flashlight pools, puzzle-solving joy, no gore or stalking menace",
        "prompt_zh": "青少年清爽社团谜题，线索板、手电光斑、解谜乐趣，无血腥与跟踪恐吓",
        "preview": "活动室白板上贴着三张线索便签",
        "signature": ["线索板", "光斑分区", "解谜乐趣"],
        "agent": "谜题代理线索必须可验证；结局给合理解释，禁止超自然恐吓收尾。",
    },
    {
        "id": "music_stage_glow",
        "title": "音乐舞台光",
        "category": "genre",
        "medium": ["live", "mv", "short"],
        "prompt_prefix": "youth music stage glow, colored spot lights, band performance energy, clear faces under light, concert joy without haze overload",
        "prompt_zh": "青少年音乐舞台光，彩色追光，乐队表演能量，灯下脸清楚，演唱会欢快不过度烟雾",
        "preview": "主唱侧脸被蓝光切出，鼓手在后景",
        "signature": ["追光分区", "脸清楚", "表演能量"],
        "agent": "舞台代理先定主光色；歌词情绪用表演动作落地。",
    },
    {
        "id": "dance_mirror_practice",
        "title": "镜前舞蹈练习",
        "category": "genre",
        "medium": ["live", "short", "mv"],
        "prompt_prefix": "dance practice mirror room, clean reflections, countable choreography beats, athletic teens, bright studio light",
        "prompt_zh": "舞蹈练习镜房，反射干净，编舞节拍可数，运动型青少年，明亮练功房光",
        "preview": "镜前数拍，四人同步举手",
        "signature": ["镜面可读", "节拍可数", "练功房光"],
        "agent": "舞蹈代理分镜按八拍写；镜子里动作与实体一致。",
    },
    {
        "id": "comedy_slapstick_clean",
        "title": "干净闹剧喜剧",
        "category": "genre",
        "medium": ["live", "anime", "short"],
        "prompt_prefix": "clean slapstick youth comedy, prop mishaps, wide readable staging, bright timing, no humiliation bullying",
        "prompt_zh": "干净闹剧青年喜剧，道具失误，宽景可读调度，明亮节拍，无羞辱欺凌",
        "preview": "端托盘转弯差点撞上，托盘稳稳接住",
        "signature": ["道具失误", "宽景调度", "无欺凌"],
        "agent": "喜剧代理笑点来自情境与道具，不拿外貌/成绩羞辱角色。",
    },
    # Format / delivery
    {
        "id": "vertical_short_punch",
        "title": "竖屏短视频节拍",
        "category": "format",
        "medium": ["short", "vlog", "mg"],
        "prompt_prefix": "vertical short-video framing 9:16, punchy opening hook in first second, big readable faces, bold captions space, teen platform safe",
        "prompt_zh": "竖屏 9:16，首秒钩子，大脸可读，大字幕留白，青少年平台安全",
        "preview": "竖构图特写举手，下方留字幕条",
        "signature": ["9:16", "首秒钩子", "字幕留白"],
        "agent": "竖屏代理：3秒内交代『看什么』；禁用软色情构图。",
    },
    {
        "id": "horizontal_film_short",
        "title": "横幅电影短片",
        "category": "format",
        "medium": ["film", "short", "live"],
        "prompt_prefix": "horizontal film-short framing 16:9, deliberate camera moves, motivated lighting, youth drama with clear goals, restrained grade",
        "prompt_zh": "横幅 16:9 电影短片构图，有动机的运镜与布光，青年戏剧目标清楚，调色克制",
        "preview": "横移跟拍走廊对话，光随门框变化",
        "signature": ["16:9", "动机运镜", "克制调色"],
        "agent": "电影短片代理每场一句目标；禁用空洞『高级感』形容词。",
    },
    {
        "id": "mv_lyric_montage",
        "title": "歌词蒙太奇MV",
        "category": "format",
        "medium": ["mv", "short", "anime"],
        "prompt_prefix": "lyric montage music-video style for teens, beat-synced cuts, motif recurring props, wholesome imagery, clear emotional arc",
        "prompt_zh": "青少年歌词蒙太奇 MV，踩点剪辑，母题道具反复出现，健康意象，情绪弧线清楚",
        "preview": "同一枚徽章在合唱段落三次特写",
        "signature": ["踩点", "母题道具", "健康意象"],
        "agent": "MV 代理先标副歌高光镜；母题道具至少回响三次。",
    },
    {
        "id": "vlog_day_in_life",
        "title": "一日生活Vlog",
        "category": "format",
        "medium": ["vlog", "short", "live"],
        "prompt_prefix": "day-in-life youth vlog, friendly talking-head, B-roll of routine, natural daylight, authentic but tidy spaces",
        "prompt_zh": "青少年一日生活 Vlog，亲和口播，日常空镜，自然光，真实但整洁空间",
        "preview": "书桌口播切到食堂排队空镜",
        "signature": ["口播+空镜", "自然光", "整洁真实"],
        "agent": "Vlog 代理保护隐私：不暴露住址门牌与同学未授权面孔特写策略要提醒。",
    },
    {
        "id": "silent_gesture_comedy",
        "title": "无声手势喜剧",
        "category": "format",
        "medium": ["short", "anime", "live"],
        "prompt_prefix": "silent gesture comedy for youth, mime-clear body language, prop timing, no dialogue needed, bright staging",
        "prompt_zh": "青少年无声手势喜剧，肢体如默剧般清楚，道具节拍，无需对白，明亮调度",
        "preview": "两人抢同一把伞，最后一起撑开",
        "signature": ["默剧肢体", "道具节拍", "无对白"],
        "agent": "无声喜剧代理：每个笑点用三拍（准备-失误-解决）。",
    },
    {
        "id": "shadow_puppet_folk",
        "title": "皮影民俗轻演绎",
        "category": "craft",
        "medium": ["stopmotion", "anime", "edu"],
        "prompt_prefix": "youth-friendly shadow-puppet folk style, translucent colored figures, warm backlight screen, gentle folk tale, no scary spirits",
        "prompt_zh": "青少年友好皮影风，半透明彩色影人，暖背光幕，温和民间故事，无恐怖精灵",
        "preview": "影幕上马儿小跑，暖黄背光",
        "signature": ["背光幕", "半透明影人", "温和民俗"],
        "agent": "皮影代理故事选励志/互助型民间片段，避开厉鬼题材。",
    },
]

# --- 9 new masters (added to existing 12 → 21) ------------------------------

NEW_MASTERS: dict[str, list[dict[str, Any]]] = {
    "director": [
        {
            "id": "zhixing",
            "name": "知行",
            "reading": "zhī xíng",
            "title": "科普讲解导演",
            "tagline": "一屏一结论 · 图形先于术语",
            "intro": "知行把知识短片拆成可复述的步骤。适合白板、MG、实验安全示范。提示词先写图形运动，再写术语。",
            "signature": ["一屏一结论", "图形先行", "安全示范"],
            "fit": "科普、STEM、安全教育、课堂导入",
            "unfit": "纯情绪片、恐吓式说教",
            "hue": 175,
            "cover": "covers/zhixing.svg",
            "agent": "你是科普讲解导演代理：每镜必须能让观众复述一个结论；禁用恐吓话术。",
            "prompt_compile": "Lead with diagram motion and labeled steps; keep faces optional; youth-safe lab cues.",
        },
        {
            "id": "yuechang",
            "name": "跃场",
            "reading": "yuè chǎng",
            "title": "运动热血导演",
            "tagline": "动作节拍 · 胜负可读",
            "intro": "跃场专攻球场、跑道、舞台竞技的青年向热血：一镜一主动作，慢动作只为读懂。",
            "signature": ["一镜一动作", "胜负节拍", "无伤害特写"],
            "fit": "体育短片、社团比赛、训练蒙太奇",
            "unfit": "暴力斗殴、伤害炫耀",
            "hue": 12,
            "cover": "covers/yuechang.svg",
            "agent": "运动导演代理：写出准备-爆发-结果三拍；禁止受伤美学。",
            "prompt_compile": "Readable body mechanics, bright field light, celebrate effort not injury.",
        },
        {
            "id": "xiantai",
            "name": "弦台",
            "reading": "xián tái",
            "title": "音乐舞台导演",
            "tagline": "追光分区 · 歌词落地",
            "intro": "弦台让表演短片和 MV 有舞台语法：主光色、副歌高光镜、母题道具回响。",
            "signature": ["主光色", "副歌高光", "母题回响"],
            "fit": "校园音乐会、MV、才艺短片",
            "unfit": "夜店成人向、烟雾淹没面孔",
            "hue": 280,
            "cover": "covers/xiantai.svg",
            "agent": "舞台导演代理：先定主光色与副歌镜，再铺过门空镜。",
            "prompt_compile": "Colored spotlights with readable faces, beat-aware staging, wholesome concert joy.",
        },
        {
            "id": "mishe",
            "name": "谜社",
            "reading": "mí shè",
            "title": "清爽谜题导演",
            "tagline": "线索可验证 · 结局讲理",
            "intro": "谜社做青年社团解谜：线索板、手电分区、合理收束，拒绝血腥与跟踪恐吓。",
            "signature": ["线索板", "可验证", "非恐吓"],
            "fit": "社团推理、寻宝、解谜游戏短片",
            "unfit": "恐怖片、犯罪猎奇",
            "hue": 230,
            "cover": "covers/mishe.svg",
            "agent": "谜题导演代理：每条线索要能在结局回收；禁止超自然恐吓收尾。",
            "prompt_compile": "Clue boards, flashlight pools, puzzle joy, no gore or stalking menace.",
        },
        {
            "id": "xiaodian",
            "name": "笑点",
            "reading": "xiào diǎn",
            "title": "青年喜剧导演",
            "tagline": "道具失误 · 不羞辱",
            "intro": "笑点坚持干净闹剧：笑从情境与道具来，不拿外貌、成绩、家境羞辱角色。",
            "signature": ["道具喜剧", "宽景调度", "零羞辱"],
            "fit": "校园喜剧、无声手势短片、轻小品",
            "unfit": "嘲讽弱者、身体羞辱玩笑",
            "hue": 42,
            "cover": "covers/xiaodian.svg",
            "agent": "喜剧导演代理：三拍结构准备-失误-解决；禁用欺凌笑点。",
            "prompt_compile": "Prop mishaps, wide readable staging, bright timing, no bullying humor.",
        },
        {
            "id": "yanzhou",
            "name": "砚舟",
            "reading": "yàn zhōu",
            "title": "国风短片导演",
            "tagline": "线与留白 · 纹样克制",
            "intro": "砚舟把国风落在线描、石色与留白，适合工笔、水墨、皮影轻演绎，拒绝迷信恐吓。",
            "signature": ["线描留白", "石色克制", "非迷信"],
            "fit": "国风短片、节气故事、民俗友好演绎",
            "unfit": "恐怖志怪恐吓、刻板丑化",
            "hue": 355,
            "cover": "covers/yanzhou.svg",
            "agent": "国风导演代理：纹样服务场景；奇幻走守护与解谜，不走厉鬼。",
            "prompt_compile": "Fine lines, soft mineral colors, generous negative space, respectful motifs.",
        },
        {
            "id": "shuya",
            "name": "竖芽",
            "reading": "shù yá",
            "title": "竖屏短视频导演",
            "tagline": "首秒钩子 · 字幕留白",
            "intro": "竖芽专治 9:16：首秒说清看点，大脸与字幕共存，平台安全优先。",
            "signature": ["9:16钩子", "大脸可读", "平台安全"],
            "fit": "竖屏科普、挑战、日更短视频",
            "unfit": "软色情构图、引战标题党",
            "hue": 320,
            "cover": "covers/shuya.svg",
            "agent": "竖屏导演代理：3秒内交代看点；构图避开软色情与引战。",
            "prompt_compile": "9:16 punchy hook, big readable faces, caption space, platform-safe teens.",
        },
        {
            "id": "jishiqing",
            "name": "纪实青",
            "reading": "jì shí qīng",
            "title": "青年纪录片导演",
            "tagline": "观察距离 · 真实整洁",
            "intro": "纪实青用观察式镜头拍青少年生活与自然田野：尊重距离、隐私提醒、不消费苦难。",
            "signature": ["观察距离", "隐私提醒", "不消费苦难"],
            "fit": "校园纪实、自然笔记、人物小传",
            "unfit": "窥私、苦难展演",
            "hue": 155,
            "cover": "covers/jishiqing.svg",
            "agent": "纪录片导演代理：先问知情同意；苦难不拿来猎奇。",
            "prompt_compile": "Observational framing, natural light, respectful distance, tidy authentic spaces.",
        },
        {
            "id": "yuandeng",
            "name": "圆灯",
            "reading": "yuán dēng",
            "title": "合家欢动画导演",
            "tagline": "圆润亲和 · 惊吓归零",
            "intro": "圆灯负责合家欢 3D/黏土/玩具向：造型圆润、喜剧温和，低龄观众也可共看。",
            "signature": ["圆润造型", "温和喜剧", "低龄可看"],
            "fit": "合家欢动画、玩具故事、亲子共看短片",
            "unfit": "惊吓跳杀、黑暗畸变",
            "hue": 55,
            "cover": "covers/yuandeng.svg",
            "agent": "合家欢导演代理：动作可夸张，情绪惊吓必须归零。",
            "prompt_compile": "Rounded friendly 3D or clay forms, bright sets, gentle comedy timing.",
        },
    ],
}


def _style_pack(row: dict[str, Any]) -> dict[str, Any]:
    avoid = list(dict.fromkeys([*(row.get("avoid") or []), *YOUTH_AVOID_BASE]))
    return {
        "id": row["id"],
        "title": row["title"],
        "category": row.get("category") or "general",
        "medium": row.get("medium") or [],
        "prompt_prefix": row["prompt_prefix"],
        "prompt_zh": row.get("prompt_zh") or "",
        "avoid": avoid,
        "preview": row.get("preview") or "",
        "signature": row.get("signature") or [],
        "agent": row.get("agent") or "",
        "audience": "youth",
    }


def _master_agent_card(m: dict[str, Any], role: str) -> dict[str, Any]:
    return {
        "id": m["id"],
        "kind": "master",
        "role": role,
        "name": m["name"],
        "title": m["title"],
        "tagline": m.get("tagline") or "",
        "category": "master",
        "medium": ["film", "short", "anime"],
        "prompt_prefix": m.get("prompt_compile") or "",
        "prompt_zh": m.get("intro") or "",
        "signature": m.get("signature") or [],
        "fit": m.get("fit") or "",
        "unfit": m.get("unfit") or "",
        "agent": m.get("agent") or m.get("intro") or "",
        "audience": "youth",
        "hue": m.get("hue"),
    }


def build_lookbook(existing_masters: dict[str, Any] | None = None) -> dict[str, Any]:
    existing = existing_masters or json.loads(MASTERS_PATH.read_text(encoding="utf-8"))
    styles = [_style_pack(s) for s in STYLES]
    master_cards: list[dict[str, Any]] = []
    for role in ("director", "supervisor", "producer"):
        for m in existing.get(role) or []:
            # prefer enriched agent text from NEW if same id later overwritten
            card = _master_agent_card(m, role)
            if not card["agent"]:
                card["agent"] = f"你是{m.get('name')}（{m.get('title')}）设计代理：{m.get('intro') or m.get('tagline') or ''}"
            if not card["prompt_prefix"]:
                card["prompt_prefix"] = ", ".join(m.get("signature") or []) or m.get("tagline") or m.get("name")
            master_cards.append(card)
    # ensure new directors present in cards even before catalog merge
    existing_ids = {c["id"] for c in master_cards}
    for m in NEW_MASTERS["director"]:
        if m["id"] not in existing_ids:
            master_cards.append(_master_agent_card(m, "director"))

    items = [{**s, "kind": "style"} for s in styles] + master_cards
    return {
        "schema": "zima-anima-light/youth-lookbook/1",
        "title": "青少年向风格与大师设计代理 Lookbook",
        "audience": "youth",
        "count": len(items),
        "style_count": len(styles),
        "master_count": len(master_cards),
        "research_notes": [
            "未成年人短视频偏好：幽默、人文知识、热点、日常、动漫游戏（中国青少年研究中心相关报告）",
            "教育影像类型：剧情实拍、纪录片、动画、资料再剪；白板/剪纸/定格等可操作技法",
            "青少年动画媒介：赛璐璐、条漫、国风工笔/水墨、黏土定格、合家欢3D、玩具微缩",
            "安全红线：无恐怖猎奇、无成人向、无真实名人肖像、提示词不写真实大师姓名",
        ],
        "items": items,
    }


def merge_masters_catalog() -> dict[str, Any]:
    raw = json.loads(MASTERS_PATH.read_text(encoding="utf-8"))
    dirs = list(raw.get("director") or [])
    have = {m.get("id") for m in dirs}
    for m in NEW_MASTERS["director"]:
        if m["id"] in have:
            # update agent fields in place
            for i, old in enumerate(dirs):
                if old.get("id") == m["id"]:
                    dirs[i] = {**old, **{k: v for k, v in m.items() if k != "agent"}}
                    dirs[i]["agent"] = m.get("agent")
                    break
        else:
            dirs.append({k: v for k, v in m.items()})
            have.add(m["id"])
    raw["director"] = dirs
    # attach agent text to all masters if missing
    for role in ("director", "supervisor", "producer"):
        for m in raw.get(role) or []:
            if not m.get("agent"):
                m["agent"] = (
                    f"你是{m.get('name')}（{m.get('title')}）设计代理。"
                    f"{m.get('intro') or ''}"
                    f" 签名：{'；'.join(m.get('signature') or [])}。"
                    f" 适用：{m.get('fit') or '—'}。不适用：{m.get('unfit') or '—'}。"
                )
            if not m.get("prompt_compile"):
                m["prompt_compile"] = ", ".join(m.get("signature") or []) or m.get("tagline") or ""
    return raw


def sync(*, write_packs: bool = True, write_agents: bool = True) -> dict[str, Any]:
    masters = merge_masters_catalog()
    MASTERS_PATH.write_text(json.dumps(masters, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lookbook = build_lookbook(masters)
    if lookbook["count"] != 61:
        raise RuntimeError(f"lookbook count must be 61, got {lookbook['count']}")

    LOOKBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOOKBOOK_PATH.write_text(json.dumps(lookbook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if write_packs:
        PACKS_DIR.mkdir(parents=True, exist_ok=True)
        keep_ids = {s["id"] for s in STYLES}
        for path in PACKS_DIR.glob("*.json"):
            if path.stem not in keep_ids:
                # archive-friendly: leave unknown packs; Soft Studio loads all packs
                pass
        for s in STYLES:
            pack = _style_pack(s)
            (PACKS_DIR / f"{s['id']}.json").write_text(
                json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
            )

    if write_agents:
        AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        index_lines = [
            "# 青少年向设计 Agent 名册（61）",
            "",
            "本目录由 `scripts/youth_lookbook.py` 同步。每位条目都是**原创 persona / 风格代理**：",
            "提示词只写光、形、材质、动作、机位；禁止真实名人姓名与成人/恐怖题材。",
            "",
            f"- 风格包：{lookbook['style_count']}",
            f"- 大师：{lookbook['master_count']}",
            f"- 合计：{lookbook['count']}",
            "",
            "## 条目",
            "",
        ]
        for item in lookbook["items"]:
            kind = item.get("kind")
            title = item.get("title") or item.get("name")
            index_lines.append(
                f"- **{item['id']}**（{kind}）{item.get('name') or ''} · {title} — {item.get('tagline') or item.get('preview') or ''}"
            )
            agent_path = AGENTS_DIR / f"{item['id']}.md"
            body = "\n".join([
                f"# {item.get('name') or item['id']} · {title}",
                "",
                f"- 类型：{kind}",
                f"- 分类：{item.get('category')}",
                f"- 媒介：{', '.join(item.get('medium') or [])}",
                f"- 签名：{'；'.join(item.get('signature') or [])}",
                "",
                "## 设计 Agent 系统提示",
                "",
                item.get("agent") or "",
                "",
                "## 提示词前缀（EN）",
                "",
                "```",
                item.get("prompt_prefix") or "",
                "```",
                "",
                "## 提示词要点（ZH）",
                "",
                item.get("prompt_zh") or "",
                "",
                "## 避开",
                "",
                ", ".join(item.get("avoid") or YOUTH_AVOID_BASE),
                "",
            ])
            agent_path.write_text(body, encoding="utf-8")
        (AGENTS_DIR / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "count": lookbook["count"],
        "style_count": lookbook["style_count"],
        "master_count": lookbook["master_count"],
        "lookbook": str(LOOKBOOK_PATH),
        "packs_dir": str(PACKS_DIR),
        "agents_dir": str(AGENTS_DIR),
    }


def load_lookbook() -> dict[str, Any]:
    if LOOKBOOK_PATH.is_file():
        return json.loads(LOOKBOOK_PATH.read_text(encoding="utf-8"))
    return build_lookbook()


def main() -> int:
    result = sync()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
