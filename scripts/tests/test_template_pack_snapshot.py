"""Official pack publication, exercised with immutable Git fixtures and an in-memory object store."""
import hashlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import build_catalog_index as builder
import publish_catalog_index_to_r2 as publisher
import template_pack_snapshot as packs


class StoreError(Exception):
    def __init__(self, code):
        self.response = {"ResponseMetadata": {"HTTPStatusCode": code}}


class Store:
    def __init__(self):
        self.objects = {}
        self.before_pointer = None
        self.fail_read = False

    def put_object(self, *, Key, Body, **options):
        if Key == packs.POINTER and self.before_pointer:
            before, self.before_pointer = self.before_pointer, None
            before()
        existing = self.objects.get(Key)
        if options.get("IfNoneMatch") == "*" and existing is not None:
            raise StoreError(412)
        if "IfMatch" in options and options["IfMatch"] != (existing or (None,))[0]:
            raise StoreError(412)
        etag = '"' + hashlib.sha256(Body).hexdigest() + '"'
        self.objects[Key] = etag, Body
        return {"ETag": etag}

    def get_object(self, *, Key, **_):
        if Key not in self.objects:
            raise StoreError(404)
        etag, value = self.objects[Key]
        if self.fail_read and Key != packs.POINTER:
            value = b"incomplete"
        return {"ETag": etag, "Body": io.BytesIO(value)}

    def current(self):
        return json.loads(self.objects[packs.POINTER][1])


class OfficialPackSnapshotTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.root = pathlib.Path(work.name)
        self.git("init", "-q")
        self.git("config", "user.email", "fixtures@example.test")
        self.git("config", "user.name", "Fixture")
        self.index = [{"id": "kitchen", "path": f"{packs.PACKS}/kitchen"}, {"id": "starter"}]
        self.manifest = {
            "id": "kitchen", "name": "Kitchen", "version": "1.0.0",
            "templates": ["../../Standard/RECIPE_TEMPLATE.md"], "rulesets": ["RECIPE"],
            "layouts": ["../../Layouts/recipe.json"], "presets": ["PORTRAIT"],
        }
        self.base_path = f"{packs.PACKS}/kitchen/pack.json"
        self.put(packs.INDEX, self.index)
        self.put(self.base_path, self.manifest)
        self.put(f"{packs.PACKS}/starter/pack.json", {"id": "starter", "name": "Starter", "version": "1.0.0",
                                                     "is_meta_pack": True, "includes": ["kitchen"]})
        self.put("templates/Standard/RECIPE_TEMPLATE.md", b"original\r\n")
        self.put("rules/RECIPE.md", b"published rule\n")
        self.put("templates/Layouts/recipe.json", b'{"field":"title"}')
        self.put("presets/PORTRAIT.preset.json", b'{"id":"PORTRAIT"}')
        self.put(f"{packs.PACKS}/kitchen/rules/kitchen.md", b"pack-local rule")
        self.put(f"{packs.PACKS}/kitchen/examples/unlisted.md", b"not an opted-in example")
        self.revision = self.commit()
        self.store = Store()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root).decode().strip()

    def put(self, path, data):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data if isinstance(data, bytes) else json.dumps(data).encode())

    def commit(self):
        self.git("add", "templates", "rules", "presets")
        self.git("commit", "-qm", "source changes")
        return self.git("rev-parse", "HEAD")

    def publish(self, revision, generation):
        return packs.stage_and_promote(self.store, "fixture", packs.build(self.root, revision), revision, generation)

    def test_same_revision_preserves_exact_source_and_declared_and_discovered_members(self):
        self.put("templates/Standard/RECIPE_TEMPLATE.md", b"uncommitted change")
        expected = packs.build(self.root, self.revision)
        out = self.root / "snapshot.json"
        with mock.patch.object(builder, "ROOT", self.root):
            self.assertEqual(builder.main(["--pack-revision", self.revision, "--out", str(out)]), 0)
        self.assertEqual(out.read_bytes(), expected)
        record = json.loads(expected)
        self.assertEqual(record["revision"], self.revision)
        self.assertEqual(record["index"], self.index)
        self.assertEqual(record["files"]["templates/Standard/RECIPE_TEMPLATE.md"], "original\r\n")
        self.assertIn("presets/PORTRAIT.preset.json", record["files"])
        self.assertIn(f"{packs.PACKS}/kitchen/rules/kitchen.md", record["files"])
        self.assertNotIn(f"{packs.PACKS}/kitchen/examples/unlisted.md", record["files"])
        self.assertEqual(record["files"][self.base_path], json.dumps(self.manifest))

    def test_failed_build_preserves_previous_output_and_pointer(self):
        out = self.root / "snapshot.json"
        packs.write_snapshot(self.root, self.revision, out)
        original = out.read_bytes()
        self.publish(self.revision, 1)
        before = self.store.current()
        (self.root / "rules/RECIPE.md").unlink()
        changed = self.commit()
        with self.assertRaisesRegex(ValueError, "rules/RECIPE.md"):
            packs.write_snapshot(self.root, changed, out)
        self.assertEqual(out.read_bytes(), original)
        with mock.patch.object(publisher, "ROOT", self.root), mock.patch.object(publisher, "make_client") as client:
            with self.assertRaisesRegex(ValueError, "rules/RECIPE.md"):
                publisher.main(["--file", str(out), "--pack-revision", changed, "--pack-generation", "2"])
            client.assert_not_called()
        self.assertEqual(self.store.current(), before)

    def test_missing_included_pack_and_noncontent_file_are_rejected(self):
        self.put(packs.INDEX, self.index[1:])
        with self.assertRaisesRegex(ValueError, "included packs missing"):
            packs.build(self.root, self.commit())
        self.put(packs.INDEX, self.index)
        self.manifest["templates"] = ["../../../README.md"]
        self.put(self.base_path, self.manifest)
        with self.assertRaisesRegex(ValueError, "invalid templates member"):
            packs.build(self.root, self.commit())

    def test_publish_cli_refuses_modified_artifact_before_client_creation(self):
        out = self.root / "snapshot.json"
        packs.write_snapshot(self.root, self.revision, out)
        as_json = json.loads(out.read_bytes())
        as_json["files"]["rules/RECIPE.md"] = "not from the requested source"
        out.write_bytes(packs.encode(as_json))
        with mock.patch.object(publisher, "ROOT", self.root), mock.patch.object(publisher, "make_client") as client:
            with self.assertRaisesRegex(ValueError, "differs from the expected Git source"):
                publisher.main(["--file", str(out), "--pack-revision", self.revision, "--pack-generation", "1"])
            client.assert_not_called()

    def test_interrupted_readback_leaves_previous_complete_revision_selected(self):
        self.assertEqual(self.publish(self.revision, 1), "published")
        before = self.store.current()
        self.put("rules/RECIPE.md", b"updated rule")
        new = self.commit()
        self.store.fail_read = True
        with self.assertRaisesRegex(ValueError, "did not match"):
            self.publish(new, 2)
        self.assertEqual(self.store.current(), before)
        self.store.fail_read = False
        self.assertEqual(self.publish(new, 2), "published")
        self.assertEqual(self.publish(new, 2), "unchanged")
        current = self.store.current()
        self.assertEqual((current["revision"], current["generation"]), (new, 2))
        body = self.store.objects[f"{packs.PUBLIC_PREFIX}/snapshots/{current['sha256']}.json"][1]
        self.assertEqual(json.loads(body)["files"]["rules/RECIPE.md"], "updated rule")
        self.assertIn(f"{packs.PUBLIC_PREFIX}/snapshots/{before['sha256']}.json", self.store.objects)

    def test_competing_publish_and_replay_cannot_restore_older_snapshot(self):
        self.publish(self.revision, 1)
        self.put("rules/RECIPE.md", b"third version")
        newer = self.commit()
        self.store.before_pointer = lambda: self.publish(newer, 3)
        self.assertEqual(self.publish(self.revision, 2), "superseded")
        self.assertEqual(self.store.current()["revision"], newer)
        self.assertEqual(self.publish(self.revision, 1), "superseded")
        with self.assertRaisesRegex(ValueError, "already identifies another"):
            self.publish(self.revision, 3)
        self.assertEqual(self.store.current()["generation"], 3)


if __name__ == "__main__":
    unittest.main()
