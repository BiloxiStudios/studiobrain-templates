"""Tests for the immutability logic in scripts/publish_to_r2.py (SBAI-7183).

Uses a mocked S3 client rather than a live R2/moto endpoint (moto's S3 mock
only intercepts *.amazonaws.com hosts, not R2's custom endpoint) so these
run with zero network access and zero credentials, safe in any PR job.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import publish_to_r2 as pub  # noqa: E402


def _not_found_error():
    return ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject")


class PublishToR2Test(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.local_path = pathlib.Path(self.tmp.name) / "artifact.txt"
        self.local_path.write_bytes(b"hello world")
        self.sha = pub.sha256_file(self.local_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_new_object_is_uploaded(self):
        client = MagicMock()
        client.head_object.side_effect = _not_found_error()

        result = pub.publish_versioned_object(client, "bucket", "plugins/x/1.0.0/artifact.txt", self.local_path)

        self.assertEqual(result, "uploaded")
        client.upload_file.assert_called_once()

    def test_identical_existing_object_is_skipped(self):
        client = MagicMock()
        client.head_object.return_value = {"Metadata": {"sha256": self.sha}}

        result = pub.publish_versioned_object(client, "bucket", "plugins/x/1.0.0/artifact.txt", self.local_path)

        self.assertEqual(result, "skipped-identical")
        client.upload_file.assert_not_called()

    def test_different_existing_object_raises_immutability_violation(self):
        client = MagicMock()
        client.head_object.return_value = {"Metadata": {"sha256": "0" * 64}}

        with self.assertRaises(RuntimeError) as ctx:
            pub.publish_versioned_object(client, "bucket", "plugins/x/1.0.0/artifact.txt", self.local_path)

        self.assertIn("IMMUTABILITY VIOLATION", str(ctx.exception))
        client.upload_file.assert_not_called()


if __name__ == "__main__":
    unittest.main()
