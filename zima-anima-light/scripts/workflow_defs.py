"""Fixed youth workflows."""
from __future__ import annotations

from typing import Any

WORKFLOWS = ("from_story", "from_image", "from_music", "from_video")

SHARED_NODES = (
    ("look", "风格与大师", True),
    ("intake", "开工素材", True),
    ("story", "故事剧本", True),
    ("assets", "角色场景道具", True),
    ("continuity_lock", "一致性锁定", False),
    ("storyboard", "分镜", True),
    ("generate_stills", "关键帧生图", False),
    ("generate_video", "代表样片", True),
    ("audio", "配音配乐", False),
    ("edit", "剪辑成片", True),
    ("qc", "质检", False),
    ("deliver", "交付", True),
)

ENTRY_FOCUS = {
    "from_story": "look",
    "from_image": "look",
    "from_music": "look",
    "from_video": "look",
}


def build_nodes(workflow: str) -> list[dict[str, Any]]:
    if workflow not in WORKFLOWS:
        raise ValueError(f"Unknown workflow: {workflow}")
    focus = ENTRY_FOCUS[workflow]
    nodes = []
    for node_id, title, gate in SHARED_NODES:
        status = "ready" if node_id == focus else "locked"
        nodes.append({
            "id": node_id,
            "title": title,
            "gate": gate,
            "status": status,
            "evidence": [],
            "notes": "",
        })
    return nodes


def ensure_look_node(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Prepend style/master node for older projects."""
    if any(n.get("id") == "look" for n in nodes):
        return nodes
    look = {
        "id": "look",
        "title": "风格与大师",
        "gate": True,
        "status": "ready",
        "evidence": [],
        "notes": "选择工作台风格与导演、艺术总监、摄影灯光运镜、剪辑和监制阵容",
    }
    # Keep prior progress: if later nodes already moved, mark look approved.
    if any(n.get("status") in {"ready", "in_progress", "approved"} and n.get("id") != "intake"
           for n in nodes):
        if any(n.get("status") == "approved" for n in nodes):
            look["status"] = "approved"
    return [look, *nodes]


def unlock_after(nodes: list[dict[str, Any]], node_id: str) -> None:
    order = [n["id"] for n in nodes]
    if node_id not in order:
        return
    idx = order.index(node_id)
    if idx + 1 < len(nodes) and nodes[idx + 1]["status"] == "locked":
        nodes[idx + 1]["status"] = "ready"
