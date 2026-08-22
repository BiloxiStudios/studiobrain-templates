"""Unit tests for catalog-index R2 ETag / read-back witness (SBAI-7611)."""
from __future__ import annotations

import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import publish_catalog_index_to_r2 as pub  # noqa: E402


class FakeBody:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


class FakeS3:
    def __init__(self, etag: str = '"abc123"', body: bytes = b'{"ok":true}') -> None:
        self.etag = etag
        self.body = body
        self.puts: list[tuple[str, str]] = []

    def put_object(self, **kwargs):
        self.puts.append((kwargs["Bucket"], kwargs["Key"]))
        return {}

    def head_object(self, **kwargs):
        return {"ETag": self.etag, "ContentLength": len(self.body)}

    def get_object(self, **kwargs):
        return {"Body": FakeBody(self.body), "ETag": self.etag}


class WitnessTests(unittest.TestCase):
    def test_witness_s3_ok(self) -> None:
        body = b'{"ok":true}'
        client = FakeS3(body=body)
        etag = pub.witness_s3(client, "sb-content", "catalog/catalog-index.json", body)
        self.assertEqual(etag, "abc123")

    def test_witness_s3_missing_etag(self) -> None:
        body = b'{"ok":true}'
        client = FakeS3(etag="", body=body)
        with self.assertRaises(RuntimeError) as ctx:
            pub.witness_s3(client, "sb-content", "catalog/catalog-index.json", body)
        self.assertIn("missing ETag", str(ctx.exception))

    def test_witness_s3_body_mismatch(self) -> None:
        client = FakeS3(body=b'{"other":1}')
        with self.assertRaises(RuntimeError) as ctx:
            pub.witness_s3(client, "sb-content", "catalog/catalog-index.json", b'{"ok":true}')
        self.assertIn("read-back mismatch", str(ctx.exception))

    def test_witness_cdn_ok(self) -> None:
        body = b'{"ok":true}'
        headers = {"ETag": '"cdn-etag"'}
        resp = mock.MagicMock()
        resp.headers = headers
        resp.read.return_value = body
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False
        with mock.patch("publish_catalog_index_to_r2.urllib.request.urlopen", return_value=resp):
            etag = pub.witness_cdn("https://pub.example", "catalog/catalog-index.json", body)
        self.assertEqual(etag, "cdn-etag")

    def test_publish_runs_s3_witness(self) -> None:
        body = b'{"generated":true}'
        client = FakeS3(body=body)
        with mock.patch.object(pub, "make_client", return_value=client):
            with mock.patch.object(pathlib.Path, "is_file", return_value=True):
                with mock.patch.object(pathlib.Path, "read_bytes", return_value=body):
                    rc = pub.publish(
                        pathlib.Path("catalog-index.json"),
                        "catalog/catalog-index.json",
                        "sb-content",
                        "acct",
                        "ak",
                        "sk",
                    )
        self.assertEqual(rc, 0)
        self.assertEqual(client.puts, [("sb-content", "catalog/catalog-index.json")])


if __name__ == "__main__":
    unittest.main()
