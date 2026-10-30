import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "train" / "train.py"

pytestmark = pytest.mark.epic3


def _load():
    spec = importlib.util.spec_from_file_location("train_script", SCRIPT)
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


def test_default_epochs_follow_spec():
    train = _load()

    assert train.MIN_EPOCHS <= train.DEFAULT_EPOCHS <= train.MAX_EPOCHS


def test_build_train_kwargs_uses_spec_defaults():
    train = _load()
    args = train.parse_args([])

    kwargs = train.build_train_kwargs(args)

    assert kwargs["data"] == "data/dataset/data.yaml"
    assert kwargs["epochs"] == train.DEFAULT_EPOCHS
    assert kwargs["imgsz"] == 640
    assert kwargs["device"] == "cpu"
    assert kwargs["workers"] == 0
    assert Path(kwargs["project"]) == (ROOT / "runs" / "train").resolve()
    assert kwargs["name"] == "proton"
    assert kwargs["val"] is True
    assert kwargs["save"] is True


def test_build_train_kwargs_allows_no_plots():
    train = _load()
    args = train.parse_args(["--no-plots", "--epochs", "55", "--batch", "4"])

    kwargs = train.build_train_kwargs(args)

    assert kwargs["plots"] is False
    assert kwargs["epochs"] == 55
    assert kwargs["batch"] == 4


def test_main_rejects_zero_epochs():
    train = _load()

    with pytest.raises(SystemExit):
        train.main(["--epochs", "0", "--dry-run"])


def test_main_dry_run_validates_without_training(tmp_path, capsys):
    train = _load()
    data_yaml = _write_dataset(tmp_path)
    weights = tmp_path / "yolov8n.pt"
    weights.write_bytes(b"weights")

    result = train.main(
        [
            "--data",
            str(data_yaml),
            "--weights",
            str(weights),
            "--dry-run",
        ]
    )

    output = capsys.readouterr().out
    assert result is None
    assert "Dry run, not starting training." in output
    assert "epochs: 60" in output
    assert "imgsz: 640" in output
