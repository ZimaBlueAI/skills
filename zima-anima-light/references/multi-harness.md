# 多 Harness 安装

本 skill 通过仓库 `packaging/build.py` 打 ZIP，并通过 `installer/targets.toml` 指向各宿主目录。

## 已声明宿主

WorkBuddy、豆包 Work、TRAE (Work)、Qoder、DeepSeek Harness、QoderWork、Kimi Work、百度搭子、CodeBuddy、ZCode、MiniMax Code、Coze（扣子）、阿里云百炼；以及 Claude Code / Codex。

## 安装

```powershell
rtk python packaging/build.py --only zima-anima-light
rtk python zima-anima-light/scripts/light_cli.py lookbook
rtk python zima-anima-light/scripts/light_cli.py install --target qoder
rtk python zima-anima-light/scripts/light_cli.py install --target claude --apply
rtk python zima-anima-light/scripts/light_cli.py install --target codex --apply
```

无原生 skills 目录的宿主（WorkBuddy、部分 Work 产品）：复制到 `~/.zima-anima-light/host-bundles/<name>/` 并按生成的导入说明操作。

## MCP

`mcp/manifest.json` 描述只读项目状态与工作流提示工具；各宿主按自家 MCP 配置导入，脚本不改写用户 MCP 文件。
