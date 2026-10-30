import argparse
import platform
import shutil
from pathlib import Path

import yaml

BASE_WEIGHTS = "yolov8n.pt"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
SPLITS = ("train", "val", "test")


def package_versions():
    try:
        import torch
        import ultralytics
    except ImportError as exc:
        raise SystemExit(
            f"Missing dependency: {exc}. Run: python -m pip install -r requirements.txt"
        ) from exc

    try:
        import cv2
    except ImportError:
        cv2 = None

    return {
        "python": platform.python_version(),
        "ultralytics": ultralytics.__version__,
        "torch": torch.__version__,
        "cuda": torch.cuda.is_available(),
        "opencv": cv2.__version__ if cv2 else None,
    }


def ensure_weights(weights_path, source=BASE_WEIGHTS, allow_download=True):
    weights_path = Path(weights_path)
    if weights_path.is_file():
        return weights_path, False
    if not allow_download:
        raise FileNotFoundError(f"Base weights not found: {weights_path}")

    from ultralytics import YOLO

    YOLO(source)
    downloaded = Path(source)
    if not downloaded.is_file():
        raise FileNotFoundError(f"Could not download base weights: {source}")

    weights_path.parent.mkdir(parents=True, exist_ok=True)
    if downloaded.resolve() != weights_path.resolve():
        shutil.move(str(downloaded), str(weights_path))
    return weights_path, True


def validate_dataset(config_path, check_files=True, root=None):
    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    for key in (*SPLITS, "nc", "names"):
        if key not in config:
            raise ValueError(f"Missing key '{key}' in {config_path}")
    if config["nc"] != len(config["names"]):
        raise ValueError("'nc' does not match the number of class names")

    base = Path(config.get("path", "."))
    if not base.is_absolute():
        base = (Path(root) if root else Path.cwd()) / base

    counts = {}
    for split in SPLITS:
        images_dir = base / config[split]
        images = []
        if images_dir.is_dir():
            images = sorted(
                path
                for path in images_dir.iterdir()
                if path.is_file() and path.suffix.lower() in IMAGE_EXTS
            )
        if check_files and not images:
            raise ValueError(f"No images for split '{split}' in {images_dir}")
        counts[split] = len(images)

    return {"config": config, "base": base, "counts": counts}


def first_image(dataset):
    for split in SPLITS:
        images_dir = dataset["base"] / dataset["config"][split]
        for path in sorted(images_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
                return path
    raise FileNotFoundError("No images available for smoke inference")


def smoke_inference(weights_path, dataset):
    from ultralytics import YOLO

    image = first_image(dataset)
    model = YOLO(str(weights_path))
    result = model.predict(str(image), conf=0.25, verbose=False)[0]
    return image, len(result.boxes)


def main():
    parser = argparse.ArgumentParser(
        description="Check the YOLOv8 training environment and base weights."
    )
    parser.add_argument("--weights", default="models/yolov8n.pt")
    parser.add_argument("--data", default="data/dataset/data.yaml")
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Fail instead of downloading yolov8n.pt when it is missing.",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run one-image inference with the base model.",
    )
    args = parser.parse_args()

    versions = package_versions()
    print("Environment:")
    for name, value in versions.items():
        print(f"  {name}: {value}")

    dataset = validate_dataset(args.data)
    print(f"Dataset: {dataset['base']}")
    for split, count in dataset["counts"].items():
        print(f"  {split}: {count} images")

    weights_path, downloaded = ensure_weights(
        args.weights, allow_download=not args.no_download
    )
    state = "downloaded" if downloaded else "present"
    print(f"Weights: {weights_path} ({state})")

    if args.smoke:
        image, boxes = smoke_inference(weights_path, dataset)
        print(f"Smoke inference: {image.name} -> {boxes} boxes")

    print("Environment ready.")


if __name__ == "__main__":
    main()
