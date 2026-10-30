import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "train" / "setup_env.py"
WEIGHTS = ROOT / "models" / "yolov8n.pt"
DATA_YAML = ROOT / "data" / "dataset" / "data.yaml"

pytestmark = pytest.mark.epic3


def _load():
    spec = importlib.util.spec_from_file_location("setup_env", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_dataset(tmp_path, counts):
    base = tmp_path / "dataset"
    for split, count in counts.items():
        images_dir = base / "images" / split
        images_dir.mkdir(parents=True)
        for index in range(count):
            (images_dir / f"{split}_{index}.png").write_bytes(b"fake-image")

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
    return config_path, base


def test_validate_dataset_counts_images(tmp_path):
    setup_env = _load()
    config_path, base = _write_dataset(
        tmp_path, {"train": 3, "val": 1, "test": 2}
    )

    result = setup_env.validate_dataset(config_path)

    assert result["base"] == base
    assert result["counts"] == {"train": 3, "val": 1, "test": 2}


def test_validate_dataset_missing_key_raises(tmp_path):
    setup_env = _load()
    config_path, _ = _write_dataset(tmp_path, {"train": 1, "val": 1, "test": 1})
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config.pop("val")
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    with pytest.raises(ValueError, match="Missing key 'val'"):
        setup_env.validate_dataset(config_path)


def test_validate_dataset_class_count_mismatch_raises(tmp_path):
    setup_env = _load()
    config_path, _ = _write_dataset(tmp_path, {"train": 1, "val": 1, "test": 1})
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["nc"] = 2
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    with pytest.raises(ValueError, match="class names"):
        setup_env.validate_dataset(config_path)


def test_validate_dataset_can_skip_file_check(tmp_path):
    setup_env = _load()
    config_path, base = _write_dataset(
        tmp_path, {"train": 1, "val": 1, "test": 1}
    )
    for split in ("train", "val", "test"):
        for image in (base / "images" / split).iterdir():
            image.unlink()

    result = setup_env.validate_dataset(config_path, check_files=False)

    assert result["counts"] == {"train": 0, "val": 0, "test": 0}


def test_validate_dataset_raises_on_empty_split(tmp_path):
    setup_env = _load()
    config_path, _ = _write_dataset(tmp_path, {"train": 1, "val": 1, "test": 1})
    for image in (tmp_path / "dataset" / "images" / "val").iterdir():
        image.unlink()

    with pytest.raises(ValueError, match="No images for split 'val'"):
        setup_env.validate_dataset(config_path)


def test_ensure_weights_uses_existing_file(tmp_path):
    setup_env = _load()
    weights = tmp_path / "yolov8n.pt"
    weights.write_bytes(b"weights")

    path, downloaded = setup_env.ensure_weights(weights)

    assert path == weights
    assert downloaded is False


def test_ensure_weights_without_download_raises(tmp_path):
    setup_env = _load()

    with pytest.raises(FileNotFoundError):
        setup_env.ensure_weights(
            tmp_path / "missing.pt", allow_download=False
        )


def test_repo_data_yaml_is_valid():
    setup_env = _load()

    result = setup_env.validate_dataset(DATA_YAML, check_files=False)

    assert result["config"]["nc"] == 1
    assert result["config"]["names"] == ["proton_logo"]


def test_package_versions_reports_training_stack():
    pytest.importorskip("ultralytics")
    pytest.importorskip("torch")
    setup_env = _load()

    versions = setup_env.package_versions()

    assert versions["ultralytics"]
    assert versions["torch"]
    assert isinstance(versions["cuda"], bool)


@pytest.mark.skipif(not WEIGHTS.is_file(), reason="yolov8n.pt not downloaded")
def test_base_weights_are_present():
    assert WEIGHTS.stat().st_size > 1_000_000
