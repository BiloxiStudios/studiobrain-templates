"""Verify the catalog validator accepts the Core editorial document contract."""

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import validate  # noqa: E402


class CanvasEditorValidationTest(unittest.TestCase):
    def fixture(self, kind):
        path = validate.FIXTURES_DIR / f"valid_canvas_{kind}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def errors(self, document):
        return validate._validate_instance(document, "canvas.json", "test canvas")

    def test_storyboard_selection_must_be_a_nonblank_existing_shot_id(self):
        for selection in (None, 42, "", " \t"):
            with self.subTest(selection=selection):
                document = self.fixture("storyboard")
                document["storyboard"]["video_input_shot_id"] = selection
                self.assertIn("/storyboard/video_input_shot_id", "\n".join(self.errors(document)))

        document = self.fixture("storyboard")
        document["storyboard"]["video_input_shot_id"] = "absent"
        self.assertIn("video input must reference a saved shot", "\n".join(self.errors(document)))

    def test_storyboard_shot_ids_must_be_unique_and_nonblank(self):
        for shot_id in ("wide", " \t"):
            with self.subTest(shot_id=shot_id):
                document = self.fixture("storyboard")
                document["storyboard"]["shots"][1]["id"] = shot_id
                self.assertIn("/storyboard/shots/1/id", "\n".join(self.errors(document)))

    def test_saved_draft_shot_is_valid_as_video_input(self):
        document = self.fixture("storyboard")
        document["storyboard"]["local_editor_data"] = {"color": "green"}
        shot = document["storyboard"]["shots"][0]
        del shot["approved_media"]
        shot["extra"] = True
        document["storyboard"]["video_input_shot_id"] = shot["id"]
        self.assertEqual([], self.errors(document))

        document["storyboard"] = {"shots": []}
        document["entity_types"] = []
        self.assertEqual([], self.errors(document))

    def test_episode_ids_are_unique_across_sequences_and_clip_occurrences(self):
        for sequence_id, clip_id in (("opening", "extra"), ("later", "intro"), ("intro", "extra"), ("later", "opening")):
            with self.subTest(sequence_id=sequence_id, clip_id=clip_id):
                document = self.fixture("episode")
                document["episode"]["sequences"].append({
                    "id": sequence_id,
                    "name": "Later",
                    "clips": [{"id": clip_id, "asset_id": "different-video"}],
                })
                self.assertIn("duplicate episode item ID", "\n".join(self.errors(document)))

    def test_episode_reuses_assets_with_distinct_occurrence_ids(self):
        document = self.fixture("episode")
        document["episode"]["sequences"].append({
            "id": "end",
            "name": "End",
            "clips": [{"id": "outro", "asset_id": "platform-clip"}],
            "extra": {"notes": "editor-owned"},
        })
        self.assertEqual([], self.errors(document))

        document["episode"]["sequences"] = []
        self.assertEqual([], self.errors(document))

    def test_episode_shape_follows_core_editor(self):
        for document_changes in ({"name": " \t"}, {"kind": "workflow"}):
            with self.subTest(document_changes=document_changes):
                document = self.fixture("episode")
                document.update(document_changes)
                self.assertTrue(self.errors(document))

        document = self.fixture("episode")
        del document["name"]
        self.assertTrue(self.errors(document))

        for field, value in (("id", " \t"), ("name", " \t")):
            with self.subTest(field=field):
                document = self.fixture("episode")
                document["episode"]["sequences"][0][field] = value
                self.assertTrue(self.errors(document))

        for field, value in (("id", " \t"), ("asset_id", "path/to/video"), ("asset_id", "a" * 161), ("asset_id", "x\n")):
            with self.subTest(field=field, value=value):
                document = self.fixture("episode")
                document["episode"]["sequences"][0]["clips"][0][field] = value
                self.assertTrue(self.errors(document))

        for field, value in (("canvas_id", "Uppercase"), ("shot_id", " \t")):
            with self.subTest(field=field):
                document = self.fixture("episode")
                document["episode"]["sequences"][0]["clips"][0]["source"][field] = value
                self.assertTrue(self.errors(document))

    def test_ordinary_workflow_alias_still_validates(self):
        document = {
            "id": "ordinary-graph",
            "kind": "workflow",
            "entity_types": ["character"],
            "slots": {},
            "steps": [{"id": "generate", "provides": "image-generation"}],
        }
        self.assertEqual([], self.errors(document))
