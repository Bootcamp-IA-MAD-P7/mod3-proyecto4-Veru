import hashlib

import pytest

pytestmark = pytest.mark.epic2


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\xff\xd8\xff\xe0rest", ".jpg"),
        (b"\x89PNG\r\n\x1a\nrest", ".png"),
        (b"GIF87arest", ".gif"),
        (b"GIF89arest", ".gif"),
        (b"RIFF\x00\x00\x00\x00WEBPrest", ".webp"),
        (b"RIFF\x00\x00\x00\x00WAVErest", None),
        (b"not-an-image", None),
    ],
)
def test_detect_ext(import_script, data, expected):
    collect_images = import_script("collect_images")

    assert collect_images.detect_ext(data) == expected


def test_sha256_matches_hashlib(import_script):
    collect_images = import_script("collect_images")
    data = b"proton"

    assert collect_images.sha256(data) == hashlib.sha256(data).hexdigest()


def test_next_index_ignores_other_prefixes_and_names(import_script, tmp_path):
    collect_images = import_script("collect_images")
    (tmp_path / "proton_001.png").write_bytes(b"")
    (tmp_path / "proton_010.jpg").write_bytes(b"")
    (tmp_path / "proton_abc.png").write_bytes(b"")
    (tmp_path / "other_099.png").write_bytes(b"")

    assert collect_images.next_index(tmp_path, "proton") == 11


def test_next_index_starts_at_one_for_empty_dir(import_script, tmp_path):
    collect_images = import_script("collect_images")

    assert collect_images.next_index(tmp_path, "proton") == 1


def test_metadata_roundtrip(import_script, tmp_path):
    collect_images = import_script("collect_images")
    path = tmp_path / "metadata.csv"
    rows = [
        {
            "file": "proton_001.png",
            "source": "test",
            "url": "https://example.com/logo.png",
            "license": "CC0",
            "notes": "",
            "sha256": "abc",
        }
    ]

    collect_images.save_metadata(path, rows)
    loaded, hashes = collect_images.load_metadata(path)

    assert loaded == rows
    assert hashes == {"abc"}
