#!/usr/bin/env python3
"""Render richer scenario showcase HTML files for gzh-design.

Outputs:
  assets/demo-html/showcase/*_一键复制_*.html
  assets/demo-html/showcase/clean/*_正文片段_*.html

The copy target remains a clean <section> fragment. Icons are inline text
symbols inside styled spans so they survive paste into WeChat better than SVG.
"""

from __future__ import annotations

import html
from pathlib import Path


def leaf(text: str, style: str | None = None) -> str:
    escaped = html.escape(text, quote=False)
    if style:
        return f'<span leaf="" style="{style}">{escaped}</span>'
    return f'<span leaf="">{escaped}</span>'


def p(text: str, color: str = "#475569", size: int = 15, weight: int = 400, margin: str = "0 0 12px", line: str = "1.9") -> str:
    return f'<p style="margin:{margin};font-size:{size}px;line-height:{line};color:{color};font-weight:{weight};">{leaf(text)}</p>'


def badge(text: str, bg: str, color: str) -> str:
    return (
        f'<span style="display:inline-block;padding:4px 9px;border-radius:999px;background:{bg};'
        f'color:{color};font-size:12px;font-weight:800;margin:0 6px 8px 0;">{leaf(text)}</span>'
    )


def icon_card(icon: str, title: str, body: str, accent: str, bg: str = "#FFFFFF") -> str:
    return (
        f'<section style="margin:10px 0;padding:15px 16px;border-radius:14px;background:{bg};border:1px solid #E5E7EB;">'
        f'<p style="margin:0 0 8px;font-size:14px;line-height:1.7;color:{accent};font-weight:900;">'
        f'<span style="display:inline-block;width:24px;height:24px;line-height:24px;text-align:center;border-radius:8px;background:{accent};color:#FFFFFF;margin-right:8px;">{leaf(icon)}</span>'
        f'{leaf(title)}</p>'
        f'{p(body, "#475569", 14, 400, "0", "1.85")}'
        f'</section>'
    )


def metric(label: str, value: str, note: str, accent: str) -> str:
    return (
        f'<section style="flex:1;min-width:0;margin:0 6px 12px;padding:14px;border-radius:14px;background:#FFFFFF;border:1px solid #E5E7EB;">'
        f'{p(label, accent, 12, 900, "0 0 6px", "1.5")}'
        f'{p(value, "#0F172A", 26, 900, "0 0 6px", "1.1")}'
        f'{p(note, "#64748B", 13, 400, "0", "1.6")}'
        f'</section>'
    )


def timeline(items: list[tuple[str, str, str]], accent: str) -> str:
    parts = ['<section style="margin:18px 0;">']
    for step, title, desc in items:
        parts.append(
            f'<section style="display:flex;gap:12px;margin:0 0 12px;">'
            f'<span style="flex-shrink:0;width:34px;height:34px;line-height:34px;text-align:center;border-radius:999px;background:{accent};color:#FFFFFF;font-size:13px;font-weight:900;">{leaf(step)}</span>'
            f'<section style="flex:1;padding:0 0 12px;border-bottom:1px solid #E5E7EB;">'
            f'{p(title, "#0F172A", 15, 900, "0 0 4px", "1.6")}'
            f'{p(desc, "#475569", 14, 400, "0", "1.8")}'
            f'</section></section>'
        )
    parts.append("</section>")
    return "\n".join(parts)


def quote(text: str, accent: str, bg: str) -> str:
    return (
        f'<section style="margin:18px 0;padding:18px 18px;border-radius:16px;background:{bg};border-left:5px solid {accent};">'
        f'{p(text, "#1F2937", 16, 800, "0", "1.9")}'
        f'</section>'
    )


def cta(title: str, desc: str, accent: str) -> str:
    return (
        f'<section style="margin:26px 0 0;padding:20px;border-radius:18px;background:#0F172A;">'
        f'{p(title, "#FFFFFF", 17, 900, "0 0 8px", "1.7")}'
        f'{p(desc, "#CBD5E1", 14, 400, "0", "1.8")}'
        f'<p style="margin:14px 0 0;font-size:14px;line-height:1.7;color:#FFFFFF;font-weight:900;">'
        f'<span style="display:inline-block;padding:8px 13px;border-radius:999px;background:{accent};color:#FFFFFF;">{leaf("立即行动")}</span></p>'
        f'</section>'
    )


def wrap(root: Path, title: str, content: str) -> str:
    tpl = (root / "assets" / "preview-template.html").read_text(encoding="utf-8")
    return tpl.replace("{{TITLE}}", title).replace("<!--GZH_CONTENT-->", content.strip())


def article_shell(label: str, title: str, subtitle: str, accent: str, pale: str, body: str) -> list[str]:
    return [
        f'<section style="max-width:677px;margin:0 auto;padding:0 12px;font-family:-apple-system,BlinkMacSystemFont,'
        f"'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;\">",
        f'<section style="margin:0 0 24px;padding:28px 22px;border-radius:20px;background:{pale};border:1px solid #E5E7EB;">'
        f'{badge(label, "#FFFFFF", accent)}'
        f'<h1 style="margin:4px 0 14px;font-size:25px;line-height:1.35;color:#0F172A;font-weight:900;">{leaf(title)}</h1>'
        f'{p(subtitle, body, 15, 500, "0", "1.9")}'
        f'</section>',
    ]


def finish(parts: list[str]) -> str:
    parts.append(
        '<section style="margin:28px 0 0;padding:18px;border-radius:14px;background:#F9FAFB;border:1px solid #E5E7EB;">'
        + p("我是 {{作者名}}，{{一句话简介}}。如果这篇文章对你有帮助，欢迎点赞、在看、转发。", "#475569", 14, 400, "0", "1.9")
        + "</section></section>\n"
    )
    return "\n".join(parts)


def scenarios() -> list[tuple[str, str, str]]:
    data: list[tuple[str, str, str]] = []

    accent = "#7C3AED"
    parts = article_shell("AI INSIGHT", "一个 Agent 工作流，如何从想法走到上线", "适合 AI 产品解读、智能体方案、自动化案例复盘。", accent, "#F5F3FF", "#475569")
    parts += [
        quote("判断一个 Agent 是否可用，不看它能写多少字，而看它能不能稳定完成一条真实任务链。", accent, "#F5F3FF"),
        icon_card("A", "任务拆解", "把需求拆成输入、检索、执行、验证和人工确认五个节点。", accent),
        icon_card("M", "模型边界", "所有缺失事实都标为待确认，避免为了完整而自动脑补。", accent, "#FAF5FF"),
        timeline([("01", "先跑单场景", "选择一个低风险流程连续跑两周。"), ("02", "建立评测表", "记录遗漏、误判、返工时间。"), ("03", "扩大到跨团队", "只在稳定后接入更多数据源。")], accent),
        cta("从一个可评测流程开始", "先让 Agent 替你整理信息，再决定是否让它推动动作。", accent),
    ]
    data.append(("01-ai-agent-showcase", "AI Agent 场景模板", finish(parts)))

    accent = "#0EA5E9"
    parts = article_shell("PRODUCT", "FlowPilot 2.0 发布：让会议自动变成行动", "适合新品发布、版本更新、功能宣发和增长活动。", accent, "#F0F9FF", "#475569")
    parts += [
        '<section style="display:flex;gap:0;margin:18px -6px 8px;">' + metric("节省整理时间", "42%", "会议纪要自动生成", accent) + metric("行动项追踪", "3x", "负责人更清晰", accent) + "</section>",
        icon_card("✓", "自动摘要", "会议结束后生成主题、决定、风险和待办。", accent),
        icon_card("→", "行动分配", "负责人、截止时间、依赖关系自动进入看板。", accent, "#F0F9FF"),
        quote("过去大家都觉得有人会跟进；现在每个行动项都有状态。", accent, "#E0F2FE"),
        cta("创建第一个会议空间", "跑完第一场会，就能看到摘要和行动项自动生成。", accent),
    ]
    data.append(("02-product-launch-showcase", "产品宣发场景模板", finish(parts)))

    accent = "#F97316"
    parts = article_shell("COURSE", "7 天内容训练营：把选题变成稳定栏目", "适合课程招募、训练营、社群活动和知识付费说明。", accent, "#FFF7ED", "#4B5563")
    parts += [
        quote("你缺的不是更多灵感，而是一套能重复产出好选题的流程。", accent, "#FFEDD5"),
        timeline([("D1", "定位读者问题", "明确谁会因为这篇内容停下来。"), ("D3", "建立栏目结构", "把选题分成固定栏目和临时热点。"), ("D7", "完成发布复盘", "用数据和评论反推下一轮内容。")], accent),
        icon_card("＋", "适合人群", "个人号作者、企业内容运营、知识型博主。", accent),
        cta("报名加入下一期", "保留一个真实账号作为训练对象，7 天做出可持续栏目。", accent),
    ]
    data.append(("03-course-camp-showcase", "课程训练营场景模板", finish(parts)))

    accent = "#B45309"
    parts = article_shell("EDITORIAL", "一间城市小书店的周末活动邀请", "适合活动邀请、品牌故事、文化空间、生活方式内容。", accent, "#FFFBEB", "#57534E")
    parts += [
        quote("这个周末，我们想把一小时留给纸页、咖啡和一段慢下来的谈话。", accent, "#FEF3C7"),
        icon_card("时", "时间", "周六 15:00-17:00，提前 10 分钟入场。", accent),
        icon_card("地", "地点", "梧桐街 18 号二楼，小书店后厅。", accent, "#FFFBEB"),
        icon_card("票", "名额", "现场 24 席，报名成功后保留座位。", accent),
        cta("预约一个座位", "带一本最近读过的书，也可以只带一个问题来。", accent),
    ]
    data.append(("04-event-invite-showcase", "活动邀请场景模板", finish(parts)))

    accent = "#2563EB"
    parts = article_shell("CASE STUDY", "一个客服工单系统的 30 天改造复盘", "适合客户案例、项目复盘、解决方案白皮书和行业报告。", accent, "#EFF6FF", "#475569")
    parts += [
        '<section style="display:flex;gap:0;margin:18px -6px 8px;">' + metric("响应时间", "-36%", "平均首响下降", accent) + metric("重复问题", "-51%", "知识库命中提升", accent) + "</section>",
        timeline([("前", "问题分散", "客服、研发、销售各自维护问题记录。"), ("中", "统一标签", "把工单按原因、客户层级和紧急程度分类。"), ("后", "闭环复盘", "每周把 Top 10 问题沉淀为知识库。")], accent),
        quote("系统改造的关键不是多一个看板，而是让问题有统一入口和统一出口。", accent, "#DBEAFE"),
        cta("复制这套复盘框架", "从一个高频问题开始，先让闭环跑起来。", accent),
    ]
    data.append(("05-case-study-showcase", "案例复盘场景模板", finish(parts)))

    accent = "#0F766E"
    parts = article_shell("PUBLIC GOOD", "旧电脑再发光：社区数字支持行动", "适合公益倡议、志愿者招募、ESG、社区行动。", accent, "#F0FDFA", "#475569")
    parts += [
        quote("一台闲置电脑，可能是另一个孩子打开世界的第一扇窗。", accent, "#CCFBF1"),
        icon_card("1", "捐赠设备", "仍可开机的旧电脑、显示器和键盘都可以登记。", accent),
        icon_card("2", "报名志愿者", "参与设备检测、系统安装或数字培训。", accent, "#F0FDFA"),
        icon_card("3", "转发给需要的人", "让真正需要支持的家庭和社区空间看到信息。", accent),
        cta("选择一种方式参与", "公益可以从一台旧电脑、一个周末下午开始。", accent),
    ]
    data.append(("06-public-action-showcase", "公益行动场景模板", finish(parts)))

    accent = "#64748B"
    parts = article_shell("WEEKLY DIGEST", "本周值得关注的 5 个变化", "适合周报、资讯合集、行业观察、团队内刊。", accent, "#F8FAFC", "#475569")
    parts += [
        icon_card("01", "产品", "多家工具开始把 AI 功能从对话框迁移到具体工作流。", accent),
        icon_card("02", "市场", "企业采购更关注可验证收益，而不是单点演示效果。", accent, "#F8FAFC"),
        icon_card("03", "组织", "内容、产品和研发的边界正在被自动化流程重新划分。", accent),
        quote("真正值得关注的不是新概念，而是它进入日常工作后的摩擦。", accent, "#E2E8F0"),
        cta("把这 5 个变化转给团队", "下周例会可以直接围绕这些问题讨论。", accent),
    ]
    data.append(("07-weekly-digest-showcase", "周报内刊场景模板", finish(parts)))

    return data


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "assets" / "demo-html" / "showcase"
    clean_dir = out_dir / "clean"
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_dir.mkdir(parents=True, exist_ok=True)
    for stem, title, content in scenarios():
        clean = clean_dir / f"{stem}_正文片段.html"
        page = out_dir / f"{stem}_一键复制.html"
        clean.write_text(content, encoding="utf-8")
        page.write_text(wrap(root, title, content), encoding="utf-8")
        print(page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
