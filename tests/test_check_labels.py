import pytest

pytestmark = pytest.mark.epic2


def _write(tmp_path, text):
    path = tmp_path / "label.txt"
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_valid_label(import_script, tmp_path):
    check_labels = import_script("check_labels")
    path = _write(tmp_path, "0 0.5 0.5 0.2 0.2\n")

    boxes, problems = check_labels.parse_label(path, class_count=1)

    assert boxes == 1
    assert problems == []


def test_parse_empty_label_is_background(import_script, tmp_path):
    check_labels = import_script("check_labels")
    path = _write(tmp_path, "\n")

    boxes, problems = check_labels.parse_label(path, class_count=1)

    assert boxes == 0
    assert problems == []


def test_parse_reports_wrong_field_count(import_script, tmp_path):
    check_labels = import_script("check_labels")
    path = _write(tmp_path, "0 0.5 0.5 0.2\n")

    boxes, problems = check_labels.parse_label(path, class_count=1)

    assert boxes == 0
    assert any("expected 5 fields" in problem for problem in problems)


def test_parse_reports_out_of_range_and_invalid_size(import_script, tmp_path):
    check_labels = import_script("check_labels")
    path = _write(tmp_path, "1 1.2 0.5 0 0.2\n")

    _, problems = check_labels.parse_label(path, class_count=1)

    assert any("out of range" in problem for problem in problems)
    assert any("outside [0,1]" in problem for problem in problems)
    assert any("non-positive size" in problem for problem in problems)


def test_parse_reports_non_numeric(import_script, tmp_path):
    check_labels = import_script("check_labels")
    path = _write(tmp_path, "0 abc 0.5 0.2 0.2\n")

    _, problems = check_labels.parse_label(path, class_count=1)

    assert any("non-numeric" in problem for problem in problems)


def test_main_fill_empty_creates_background_labels(
    import_script, tmp_path, monkeypatch
):
    check_labels = import_script("check_labels")
    images_dir = tmp_path / "images"
    labels_dir = tmp_path / "labels"
    images_dir.mkdir()

    (images_dir / "logo.png").write_bytes(b"fake-image")

    monkeypatch.setattr(
        "sys.argv",
        [
            "check_labels.py",
            "--images",
            str(images_dir),
            "--labels",
            str(labels_dir),
            "--fill-empty",
        ],
    )
    check_labels.main()

    assert (labels_dir / "logo.txt").exists()
    assert (labels_dir / "logo.txt").read_text(encoding="utf-8") == ""


def test_main_fails_on_invalid_label(import_script, tmp_path, monkeypatch):
    check_labels = import_script("check_labels")
    images_dir = tmp_path / "images"
    labels_dir = tmp_path / "labels"
    images_dir.mkdir()
    labels_dir.mkdir()

    (images_dir / "logo.png").write_bytes(b"fake-image")
    (labels_dir / "logo.txt").write_text("0 0.5 0.5 0.2\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "check_labels.py",
            "--images",
            str(images_dir),
            "--labels",
            str(labels_dir),
        ],
    )

    with pytest.raises(SystemExit):
        check_labels.main()
