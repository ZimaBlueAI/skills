# Zima Anima Light

面向青少年创作者的本地影视工作台。从一句想法或一场剧本出发，选择视觉风格，准备角色和镜头，在浏览器里审片、剪辑并导出成片。

## 本地启动

使用 Python 3.11 或更高版本，在本目录运行以下命令。示例把作品保存在仓库旁边的独立工程目录。

```sh
python -B scripts/light_cli.py init ../../light-projects/my-short --workflow from_story --title "我的第一部短片"
python -B scripts/light_cli.py serve ../../light-projects/my-short --port 8766
```

浏览器打开 [本地工作台](http://127.0.0.1:8766/)。再次打开已有作品时，只需运行第二条命令。

- **剧本与风格**：按场次阅读、划词批注，比较 40 套带示例图的风格包。
- **生成作品**：用自然语言描述镜头，选择运镜、表演、对白和音乐提示。云生成需要配置相应供应商凭据；付费解析和生成分别确认。详见[接口说明](references/api-providers.md)和[环境配置示例](assets/.env.local.example)。
- **审片与剪辑**：双屏预览时间线与原素材，支持修剪、变速、音量调整、撤销和重做。导出 MP4 时需要在系统 PATH 中提供 FFmpeg 和 FFprobe。

在 Cursor 等 Agent 宿主中使用时，以本目录的 [SKILL.md](SKILL.md) 为技能入口。运行核心离线测试：

```sh
python -B scripts/test_light_core.py
```

许可和署名见[仓库 LICENSE](../LICENSE) 与 [NOTICE.md](NOTICE.md)。
