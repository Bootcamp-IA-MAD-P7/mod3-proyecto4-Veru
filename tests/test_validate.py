import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "train" / "validate.py"

pytestmark = pytest.mark.epic3


def _load():
    spec = importlib.util.spec_from_file_location("validate_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_dataset(tmp_path):
    base = tmp_path / "dataset"
    for split in ("train", "val", "test"):
        images_dir = base / "images" / split
        images_dir.mkdir(parents=True)
        (images_dir / f"{split}_0.png").write_bytes(b"fake-image")

    config = {
        "path": str(base),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": 1,
        "names": ["proton_logo"],
    }
    config_path = tmp_path / "data.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return config_path


def test_find_weights_returns_existing_file(tmp_path):
    validate = _load()
    weights = tmp_path / "best.pt"
    weights.write_bytes(b"weights")

    assert validate.find_weights(weights) == weights


def test_find_weights_missing_raises(tmp_path):
    validate = _load()

    with pytest.raises(FileNotFoundError):
        validate.find_weights(tmp_path / "missing.pt")


def test_copy_weights_creates_target(tmp_path):
    validate = _load()
    source = tmp_path / "runs" / "best.pt"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"weights")
    target = tmp_path / "models" / "best.pt"

    result = validate.copy_weights(source, target)

    assert result == target
    assert target.read_bytes() == b"weights"


def test_copy_weights_missing_source_raises(tmp_path):
    validate = _load()

    with pytest.raises(FileNotFoundError):
        validate.copy_weights(tmp_path / "missing.pt", tmp_path / "best.pt")


def test_build_val_kwargs_uses_test_split_defaults():
    validate = _load()
    args = validate.parse_args([])

    kwargs = validate.build_val_kwargs(args)

    assert kwargs["data"] == "data/dataset/data.yaml"
    assert kwargs["split"] == "test"
    assert kwargs["imgsz"] == 640
    assert kwargs["device"] == "cpu"
    assert Path(kwargs["project"]) == (ROOT / "runs" / "train").resolve()
    assert kwargs["name"] == "test"
    assert kwargs["exist_ok"] is True


class _Box:
    mp = 0.912345
    mr = 0.823456
    map50 = 0.834567
    map = 0.501234


class _Results:
    box = _Box()
    speed = {"inference": 12.3456}


def test_format_metrics_rounds_values():
    validate = _load()

    metrics = validate.format_metrics(_Results())

    assert metrics == {
        "precision": 0.9123,
        "recall": 0.8235,
        "mAP50": 0.8346,
        "mAP50-95": 0.5012,
        "inference_ms": 12.35,
    }


def test_main_dry_run_does_not_copy(tmp_path, capsys):
    validate = _load()
    data_yaml = _write_dataset(tmp_path)
    weights = tmp_path / "best.pt"
    weights.write_bytes(b"weights")
    target = tmp_path / "models" / "best.pt"

    result = validate.main(
        [
            "--data",
            str(data_yaml),
            "--weights",
            str(weights),
            "--target",
            str(target),
            "--dry-run",
        ]
    )

    output = capsys.readouterr().out
    assert result is None
    assert "Dry run, not validating." in output
    assert "split: test" in output
    assert not target.exists()


def test_main_missing_weights_raises(tmp_path):
    validate = _load()
    data_yaml = _write_dataset(tmp_path)

    with pytest.raises(FileNotFoundError):
        validate.main(
            [
                "--data",
                str(data_yaml),
                "--weights",
                str(tmp_path / "missing.pt"),
                "--dry-run",
            ]
        )
