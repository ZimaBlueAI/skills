#!/usr/bin/env python3
"""Offline tests for Zima Anima Light core."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import legacy_import
import masters_catalog
import material_store
import project_model
import edit_timeline
import review_desk
import story_collab
import youth_lookbook
from providers import work_queue
from workflow_defs import WORKFLOWS, build_nodes


class LightCoreTests(unittest.TestCase):
    def test_retime_trim_mix_and_persistent_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)
            a=edit_timeline.add_clip(project,path="intro.mp4",kind="video",source_duration=8)["clip"]["id"]
            b=edit_timeline.add_clip(project,path="next.png",kind="image")["clip"]["id"]
            edit_timeline.add_clip(project,path="theme.wav",kind="audio",track="A1",start=2,source_duration=5)
            tl=edit_timeline.set_speed(project,a,2)["timeline"]
            self.assertEqual([c["start"] for c in tl["clips"]],[0,4,2])
            tl=edit_timeline.trim_clip(project,a,in_point=1,out_point=5)["timeline"]
            self.assertEqual(tl["clips"][1]["start"],2)
            edit_timeline.mix_clip(project,a,.4,True)
            edit_timeline.set_playhead(project,1)
            tl=edit_timeline.restore_edit(project,"undo")["timeline"]
            self.assertNotIn("muted",tl["clips"][0])
            self.assertTrue(tl["can_redo"])
            self.assertTrue(edit_timeline.restore_edit(project,"redo")["timeline"]["clips"][0]["muted"])
            self.assertEqual(edit_timeline.move_clip(project,b,index=0)["timeline"]["clips"][0]["id"],b)

    def test_direction_notes_follow_scene_and_respect_user_choices(self):
        from providers.creative_context import direction_notes, scene_id
        doc={"continuity":{"notebook":{"S01":{"人物与服装":"蓝袖口"},"S02":{"动作与道具":"合起本子"}}}}
        self.assertEqual(scene_id("沿用 S01 的风格，这次是S02场"),"S02")
        notes=direction_notes("video",{"camera":"目光接力"},doc,"拍S01场")
        self.assertEqual(notes["本场场记"],{"人物与服装":"蓝袖口"})
        self.assertIn("视线",notes["镜头怎么走"])
        self.assertIn("物理",notes["镜头连续性"])

    def test_queue_skips_unapproved_and_continues_after_uncertain_submission(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            jobs = [work_queue.enqueue(project, title, {"route":"test","payload":{"title":title}})
                    for title in ("旁白","S02 雨窗","S03 分镜图")]
            for job in jobs[1:]:
                self.assertTrue(work_queue.action(project, job, "approve"))
            self.assertIn("已提前", work_queue.intent(project,"让 S03 分镜图插队"))
            responses = [TimeoutError(), {"asset":"/media/generated/sample.webp"}]
            with patch("providers.creative_chat.execute_plan",side_effect=responses) as submit:
                self.assertTrue(work_queue.run_once(project))
                self.assertTrue(work_queue.run_once(project))
                self.assertFalse(work_queue.run_once(project))
                self.assertEqual([call.args[1]["payload"]["title"] for call in submit.call_args_list],
                                 ["S03 分镜图","S02 雨窗"])
            states = {row["id"]:row["state"] for row in work_queue.listing(project)}
            self.assertEqual([states[i] for i in jobs],["waiting","done","blocked"])

    def test_workflows_build(self):
        for wf in WORKFLOWS:
            nodes = build_nodes(wf)
            self.assertEqual(nodes[0]["id"], "look")
            self.assertEqual(nodes[0]["status"], "ready")
            self.assertTrue(any(n["id"] == "intake" for n in nodes))

    def test_init_and_approve(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = project_model.init_project(root, title="测试片", workflow="from_story")
            self.assertEqual(doc["schema"], "zima-anima-light/project/1")
            self.assertTrue((root / "project.json").is_file())
            self.assertEqual(doc["nodes"][0]["id"], "look")
            node = project_model.approve_node(doc, "look", "ok")
            self.assertEqual(node["status"], "approved")
            project_model.save_project(root, doc)
            again = project_model.load_project(root)
            self.assertEqual(again["nodes"][0]["status"], "approved")
            self.assertEqual(again["nodes"][1]["status"], "ready")

    def test_material_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_model.init_project(root, title="材", workflow="from_image")
            material_store.ensure_material(root, "CH-A", "character", "阿青", media_kind="image", stage="assets")
            f1 = root / "exports" / "a.png"
            f2 = root / "exports" / "b.png"
            f1.parent.mkdir(exist_ok=True)
            f1.write_bytes(b"png-one")
            f2.write_bytes(b"png-two")
            v1 = material_store.add_version(root, "CH-A", f1, note="first")
            v2 = material_store.add_version(root, "CH-A", f2, note="second")
            self.assertEqual(v1["version"], 1)
            self.assertEqual(v2["version"], 2)
            self.assertTrue(v2["history"])
            versions = material_store.list_versions(root, "CH-A")
            self.assertEqual(versions[-1]["version"], 2)
            restored = material_store.restore_version(root, "CH-A", 1)
            self.assertEqual(restored["version"], 3)
            layout = material_store.layout_positions(
                project_model.load_project(root)["nodes"],
                material_store.list_materials(root),
            )
            self.assertIn("CH-A", layout["materials"])
            listed = material_store.list_materials(root)
            self.assertIn("CH-A", listed)

    def test_pick_preview_prefers_master_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "C_HERO"
            root.mkdir()
            (root / "noise-detail.png").write_bytes(b"a")
            (root / "nested").mkdir()
            (root / "nested" / "other.png").write_bytes(b"b")
            (root / "master-portrait-imagegen.png").write_bytes(b"c")
            picked = legacy_import.pick_preview_file(root, media_kind="image")
            self.assertIsNotNone(picked)
            self.assertEqual(picked.name, "master-portrait-imagegen.png")

    def test_review_desk_decide(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_model.init_project(root, title="审", workflow="from_image")
            material_store.ensure_material(root, "IMG-1", "still", "静帧", media_kind="image", stage="generate_stills")
            f1 = root / "exports" / "a.png"
            f1.parent.mkdir(exist_ok=True)
            f1.write_bytes(b"png-review-one")
            material_store.add_version(root, "IMG-1", f1, note="candidate")
            snap = review_desk.snapshot(root, refresh=True)
            self.assertEqual(len(snap["items"]), 1)
            item = snap["items"][0]
            result = review_desk.decide(
                root,
                item_id=item["id"],
                decision="approved",
                comment="表情清楚",
                sha256=item["sha256"],
            )
            self.assertEqual(result["event"]["decision"], "approved")
            self.assertEqual(result["counts"]["approved"], 1)
            record = material_store.get_material(root, "IMG-1")
            self.assertTrue(record.get("approved"))

    def test_edit_timeline_ops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_model.init_project(root, title="剪", workflow="from_image")
            material_store.ensure_material(root, "SHOT-A", "still", "镜头A", media_kind="image", stage="generate_stills")
            material_store.ensure_material(root, "SHOT-B", "still", "镜头B", media_kind="image", stage="generate_stills")
            fa = root / "exports" / "a.png"
            fb = root / "exports" / "b.png"
            fa.parent.mkdir(exist_ok=True)
            fa.write_bytes(b"png-a")
            fb.write_bytes(b"png-b")
            material_store.add_version(root, "SHOT-A", fa, note="a")
            material_store.add_version(root, "SHOT-B", fb, note="b")
            a = edit_timeline.add_clip(root, asset_id="SHOT-A")
            self.assertEqual(a["clip_count"], 1)
            b = edit_timeline.add_clip(root, asset_id="SHOT-B", after_id=a["clip"]["id"])
            self.assertEqual(b["clip_count"], 2)
            clip_a = a["clip"]
            mid = float(clip_a["start"]) + float(clip_a["duration"]) / 2
            split = edit_timeline.split_clip(root, clip_a["id"], mid)
            self.assertEqual(split["clip_count"], 3)
            left_id = split["left"]["id"]
            edit_timeline.copy_clip(root, left_id)
            paste = edit_timeline.paste_clip(root, after_id=left_id)
            self.assertEqual(paste["clip_count"], 4)
            sped = edit_timeline.set_speed(root, paste["clip"]["id"], 2.0)
            self.assertAlmostEqual(sped["clip"]["speed"], 2.0)
            stretched = edit_timeline.stretch_clip(root, paste["clip"]["id"], 4.0)
            self.assertAlmostEqual(stretched["clip"]["duration"], 4.0)
            before = paste["clip_count"]
            edit_timeline.remove_clip(root, paste["clip"]["id"])
            snap = edit_timeline.snapshot(root)
            self.assertEqual(snap["clip_count"], before - 1)

    def test_masters_catalog_covers(self):
        payload = masters_catalog.catalog_payload()
        self.assertGreaterEqual(len(payload["all"]), 21)
        qinghe = next(m for m in payload["all"] if m["id"] == "qinghe")
        self.assertTrue(qinghe.get("intro"))
        self.assertTrue(qinghe.get("cover_url", "").startswith("/masters/"))
        cover = (masters_catalog.MASTERS_DIR / qinghe["cover"])
        self.assertTrue(cover.is_file())
        self.assertIn("青禾", cover.read_text(encoding="utf-8"))
        self.assertTrue(any(m["id"] == "zhixing" for m in payload["all"]))

    def test_youth_lookbook_61(self):
        result = youth_lookbook.sync(write_packs=True, write_agents=False)
        self.assertEqual(result["count"], 61)
        self.assertEqual(result["style_count"], 40)
        self.assertEqual(result["master_count"], 21)
        lookbook = youth_lookbook.load_lookbook()
        self.assertEqual(lookbook["count"], 61)
        packs = list((youth_lookbook.PACKS_DIR).glob("*.json"))
        self.assertGreaterEqual(len(packs), 40)
        warm = json.loads((youth_lookbook.PACKS_DIR / "warm_school.json").read_text(encoding="utf-8"))
        self.assertIn("agent", warm)
        self.assertTrue(warm.get("prompt_zh"))

    def test_story_collab_iterate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_model.init_project(root, title="剧", workflow="from_story")
            story_collab.write_story(
                root,
                "# 第一场\n阿青推开教室门。\n\n# 第二场\n雨停了，两人并肩回家。\n",
                note="seed",
            )
            story_collab.add_annotation(
                root,
                kind="edit",
                body="动作再具体",
                quote="阿青推开教室门。",
                suggestion="阿青用肩膀顶开教室门，书包带滑到肘弯。",
                author="青禾",
            )
            story_collab.add_comment(root, body="第二场缺一句对白。", author="守衡")
            draft = story_collab.build_iteration_draft(root, author="青禾", note="消化反馈")
            self.assertTrue(draft["text"])
            self.assertEqual(len(draft["based_on_feedback"]), 2)
            applied = story_collab.apply_draft(root, accept_feedback=True, author="青禾")
            self.assertGreaterEqual(applied["version"], 2)
            snap = story_collab.snapshot(root)
            self.assertIsNone(snap["draft"])
            self.assertTrue(any(a.get("status") == "accepted" for a in snap["annotations"]))
            self.assertIn("肩膀", snap["text"])

    def test_layout_stacks_same_kind(self):
        nodes = [{"id": "assets"}, {"id": "storyboard"}]
        materials = {
            "C1": {"kind": "character", "stage": "assets"},
            "C2": {"kind": "character", "stage": "assets"},
            "L1": {"kind": "scene", "stage": "assets"},
        }
        layout = material_store.layout_positions(nodes, materials)
        self.assertEqual(layout["materials"]["C1"]["x"], layout["materials"]["C2"]["x"])
        self.assertNotEqual(layout["materials"]["C1"]["x"], layout["materials"]["L1"]["x"])
        self.assertTrue(layout["materials"]["C1"].get("stacked"))
        expanded = material_store.layout_positions(nodes, materials, expanded={"assets::character"})
        self.assertNotEqual(expanded["materials"]["C1"]["x"], expanded["materials"]["C2"]["x"])
        self.assertEqual(layout["stacks"]["assets::character"]["count"], 2)


if __name__ == "__main__":
    unittest.main()
