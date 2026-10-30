import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import setup_env

DEFAULT_EPOCHS = 60
MIN_EPOCHS = 50
MAX_EPOCHS = 70


def build_train_kwargs(args):
    return {
        "data": args.data,
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "patience": args.patience,
        "device": args.device,
        "workers": args.workers,
        "project": str(Path(args.project).resolve()),
        "name": args.name,
        "seed": args.seed,
        "exist_ok": args.exist_ok,
        "plots": not args.no_plots,
        "val": True,
        "save": True,
        "verbose": True,
    }


def resolve_weights(path, allow_download=True):
    return setup_env.ensure_weights(path, allow_download=allow_download)


def train_model(weights_path, kwargs):
    from ultralytics import YOLO

    model = YOLO(str(weights_path))
    model.train(**kwargs)
    save_dir = Path(model.trainer.save_dir)
    return save_dir


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Fine-tune YOLOv8n to detect the Proton logo."
    )
    parser.add_argument("--weights", default="models/yolov8n.pt")
    parser.add_argument("--data", default="data/dataset/data.yaml")
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--patience", type=int, default=15)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--project", default="runs/train")
    parser.add_argument("--name", default="proton")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--exist-ok", action="store_true")
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.epochs < 1:
        raise SystemExit("--epochs must be >= 1")
    if args.epochs < MIN_EPOCHS:
        print(
            f"Warning: {args.epochs} epochs is below the recommended "
            f"{MIN_EPOCHS}-{MAX_EPOCHS}."
        )

    dataset = setup_env.validate_dataset(args.data)
    print(f"Dataset: {dataset['base']}")
    for split, count in dataset["counts"].items():
        print(f"  {split}: {count} images")

    weights_path, downloaded = resolve_weights(
        args.weights, allow_download=not args.no_download
    )
    state = "downloaded" if downloaded else "present"
    print(f"Weights: {weights_path} ({state})")

    kwargs = build_train_kwargs(args)
    print("Training config:")
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

    if args.dry_run:
        print("Dry run, not starting training.")
        return None

    save_dir = train_model(weights_path, kwargs)
    print(f"Run saved to: {save_dir}")
    best = save_dir / "weights" / "best.pt"
    if best.is_file():
        print(f"Best weights: {best}")
    return save_dir


if __name__ == "__main__":
    main()
