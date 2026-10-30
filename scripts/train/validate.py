import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import setup_env

DEFAULT_WEIGHTS = "runs/train/proton/weights/best.pt"
DEFAULT_TARGET = "models/best.pt"
DEFAULT_DATA = "data/dataset/data.yaml"


def find_weights(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Best weights not found: {path}")
    return path


def copy_weights(source, target):
    source = Path(source)
    target = Path(target)
    if not source.is_file():
        raise FileNotFoundError(f"Cannot copy missing weights: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def build_val_kwargs(args):
    return {
        "data": args.data,
        "split": args.split,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "device": args.device,
        "conf": args.conf,
        "project": str(Path(args.project).resolve()),
        "name": args.name,
        "exist_ok": True,
        "plots": not args.no_plots,
        "verbose": True,
    }


def format_metrics(results):
    box = getattr(results, "box", None)
    speed = getattr(results, "speed", {}) or {}
    return {
        "precision": round(float(getattr(box, "mp", 0.0)), 4),
        "recall": round(float(getattr(box, "mr", 0.0)), 4),
        "mAP50": round(float(getattr(box, "map50", 0.0)), 4),
        "mAP50-95": round(float(getattr(box, "map", 0.0)), 4),
        "inference_ms": round(float(speed.get("inference", 0.0)), 2),
    }


def validate_model(weights_path, kwargs):
    from ultralytics import YOLO

    model = YOLO(str(weights_path))
    return model.val(**kwargs)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate fine-tuned YOLOv8n on the test split and copy best.pt."
    )
    parser.add_argument("--weights", default=DEFAULT_WEIGHTS)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--split", default="test")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--conf", type=float, default=0.001)
    parser.add_argument("--project", default="runs/train")
    parser.add_argument("--name", default="test")
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument("--no-copy", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    dataset = setup_env.validate_dataset(args.data)
    print(f"Dataset: {dataset['base']}")
    for split, count in dataset["counts"].items():
        print(f"  {split}: {count} images")

    weights_path = find_weights(args.weights)
    print(f"Weights: {weights_path}")

    kwargs = build_val_kwargs(args)
    print("Validation config:")
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

    if args.dry_run:
        print("Dry run, not validating.")
        return None

    results = validate_model(weights_path, kwargs)
    metrics = format_metrics(results)
    print("Test metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    if not args.no_copy:
        target = copy_weights(weights_path, args.target)
        print(f"Copied best weights to: {target}")
    return metrics


if __name__ == "__main__":
    main()
