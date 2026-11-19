"""Check the reference bindings between the stock candidate recipes."""

from pathlib import Path
import unittest

import yaml


CANVAS_DIR = Path(__file__).resolve().parents[2] / "templates" / "Canvas"


def load_canvas(stage):
    return yaml.safe_load((CANVAS_DIR / f"reference-{stage}.canvas.yaml").read_text(encoding="utf-8"))


class ReferenceCanvasTests(unittest.TestCase):
    def test_character_traits_reach_each_image_candidate(self):
        for stage in ("headshot", "turnaround", "story-sheet"):
            with self.subTest(stage=stage):
                canvas = load_canvas(stage)
                inputs = canvas["steps"][0]["in"]
                slots = canvas["slots"]
                self.assertEqual(slots[inputs["character"]]["ref"], "entity.character[0].name")
                self.assertEqual(slots[inputs["eye_colour"]]["ref"], "entity.character[0].eye_color.name")
                self.assertEqual(slots[inputs["hairstyle"]], {"modality": "text"})
                self.assertEqual(slots[inputs["traits"]], {"modality": "text", "optional": True})

    def test_review_handoffs_require_explicit_asset_selections(self):
        stages = (
            ("headshot", (), "headshot_candidate", "image"),
            ("turnaround", ("approved_headshot",), "turnaround_candidate", "image"),
            (
                "story-sheet",
                ("approved_headshot", "approved_turnaround", "location_artwork", "brand_artwork"),
                "story_sheet_candidate",
                "image",
            ),
            ("frame-video", ("approved_frame",), "video_candidate", "video"),
        )
        for stage, selected, candidate, modality in stages:
            with self.subTest(stage=stage):
                canvas = load_canvas(stage)
                slots = canvas["slots"]
                step, = canvas["steps"]
                self.assertEqual(step["out"], {modality: candidate})
                self.assertEqual(
                    {name: slot["out"] for name, slot in slots.items() if "out" in slot},
                    {candidate: f"slot.{candidate}"},
                )
                self.assertEqual(
                    tuple(name for name, slot in slots.items() if slot == {"modality": "image"}),
                    selected,
                )
                for name in selected:
                    inputs = step["in"].get("references", [step["in"].get("image")])
                    self.assertIn(name, inputs)

    def test_story_sheet_uses_distinct_location_and_brand_context(self):
        canvas = load_canvas("story-sheet")
        inputs = canvas["steps"][0]["in"]
        slots = canvas["slots"]
        self.assertEqual(slots[inputs["location"]]["ref"], "entity.location[0].name")
        self.assertEqual(slots[inputs["brand"]]["ref"], "entity.brand[0].name")
        self.assertEqual(
            inputs["references"],
            ["approved_headshot", "approved_turnaround", "location_artwork", "brand_artwork"],
        )
