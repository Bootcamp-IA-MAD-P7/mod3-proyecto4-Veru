import csv

import pytest

pytestmark = pytest.mark.epic2

SPLITS = ("train", "val", "test")


def test_allocate_keeps_every_split_populated(import_script):
    split_dataset = import_script("split_dataset")

    counts = split_dataset.allocate(10, [0.8, 0.1, 0.1])

    assert sum(counts) == 10
    assert all(count > 0 for count in counts)


def test_allocate_sums_to_n_for_small_inputs(import_script):
    split_dataset = import_script("split_dataset")

    for n in range(0, 25):
        counts = split_dataset.allocate(n, [0.8, 0.1, 0.1])
        assert sum(counts) == n


def test_count_boxes_ignores_blank_lines(import_script, tmp_path):
    split_dataset = import_script("split_dataset")
    label = tmp_path / "img.txt"
    label.write_text("0 0.5 0.5 0.2 0.2\n\n0 0.1 0.1 0.1 0.1\n", encoding="utf-8")

    assert split_dataset.count_boxes(label) == 2


def test_count_boxes_missing_file_is_zero(import_script, tmp_path):
    split_dataset = import_script("split_dataset")

    assert split_dataset.count_boxes(tmp_path / "missing.txt") == 0


@pytest.mark.smoke
def test_main_splits_dataset_without_overlap(import_script, tmp_path, monkeypatch):
    split_dataset = import_script("split_dataset")

    images_dir = tmp_path / "images"
    labels_dir = tmp_path / "labels"
    out_dir = tmp_path / "dataset"
    images_dir.mkdir()
    labels_dir.mkdir()

    total = 10
    positives = 7
    for index in range(total):
        stem = f"img_{index:02d}"
        (images_dir / f"{stem}.png").write_bytes(b"fake-image")
        line = "0 0.5 0.5 0.2 0.2\n" if index < positives else ""
        (labels_dir / f"{stem}.txt").write_text(line, encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "split_dataset.py",
            "--images",
            str(images_dir),
            "--labels",
            str(labels_dir),
            "--out",
            str(out_dir),
            "--copy",
        ],
    )
    split_dataset.main()

    assigned = {}
    for split in SPLITS:
        image_files = sorted((out_dir / "images" / split).glob("*.png"))
        label_files = sorted((out_dir / "labels" / split).glob("*.txt"))
        assert len(image_files) == len(label_files)
        for image in image_files:
            assert image.name not in assigned, f"{image.name} duplicated"
            assigned[image.name] = split

    assert len(assigned) == total
    assert len(set(assigned.values())) == len(SPLITS)
    assert all((out_dir / "images" / split).exists() for split in SPLITS)

    with (out_dir / "split.csv").open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == total
    assert {row["split"] for row in rows} == set(SPLITS)

    data_yaml = (out_dir / "data.yaml").read_text(encoding="utf-8")
    assert "nc: 1" in data_yaml
    assert "names: ['proton_logo']" in data_yaml
