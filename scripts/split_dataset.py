import argparse
import csv
import os
import random
import shutil
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
SPLITS = ("train", "val", "test")


def allocate(n, fractions):
    """Return per-split counts, keeping at least one image in every split."""
    raw = [n * fraction for fraction in fractions]
    counts = [int(value) for value in raw]
    remainder = n - sum(counts)
    order = sorted(
        range(len(raw)),
        key=lambda index: (raw[index] - counts[index], SPLITS[index] == "test"),
        reverse=True,
    )
    for index in range(remainder):
        counts[order[index % len(order)]] += 1

    if n >= len(SPLITS):
        for index in (1, 2):
            if counts[index] == 0:
                donor = max(range(len(counts)), key=lambda i: counts[i])
                if counts[donor] > 1:
                    counts[donor] -= 1
                    counts[index] += 1
    return counts


def count_boxes(label_path):
    try:
        return sum(1 for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip())
    except FileNotFoundError:
        return 0


def place(source, target, copy):
    if target.exists():
        return
    if not copy:
        try:
            os.link(source, target)
            return
        except OSError:
            pass
    shutil.copy2(source, target)


def main():
    parser = argparse.ArgumentParser(
        description="Split a labeled YOLO dataset into train/val/test."
    )
    parser.add_argument("--images", default="data/labeled/images")
    parser.add_argument("--labels", default="data/labeled/labels")
    parser.add_argument("--out", default="data/dataset")
    parser.add_argument("--train", type=float, default=0.8)
    parser.add_argument("--val", type=float, default=0.1)
    parser.add_argument("--test", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of hardlinking them.",
    )
    args = parser.parse_args()

    fractions = [args.train, args.val, args.test]
    if abs(sum(fractions) - 1.0) > 1e-6:
        raise SystemExit("Train/val/test fractions must sum to 1.0")

    images_dir = Path(args.images)
    labels_dir = Path(args.labels)
    out_dir = Path(args.out)
    split_images = out_dir / "images"
    split_labels = out_dir / "labels"

    images = sorted(
        path
        for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS
    )
    if not images:
        raise SystemExit(f"No images found in {images_dir}")

    positives = []
    backgrounds = []
    for image in images:
        label_path = labels_dir / f"{image.stem}.txt"
        if not label_path.is_file():
            raise SystemExit(f"Missing label for {image.name}")
        entry = (image, label_path, count_boxes(label_path))
        (positives if entry[2] else backgrounds).append(entry)

    rng = random.Random(args.seed)
    rng.shuffle(positives)
    rng.shuffle(backgrounds)

    for split in SPLITS:
        shutil.rmtree(split_images / split, ignore_errors=True)
        shutil.rmtree(split_labels / split, ignore_errors=True)
        (split_images / split).mkdir(parents=True, exist_ok=True)
        (split_labels / split).mkdir(parents=True, exist_ok=True)

    assignments = {split: [] for split in SPLITS}
    for stratum in (positives, backgrounds):
        counts = allocate(len(stratum), fractions)
        cursor = 0
        for split, count in zip(SPLITS, counts):
            for image, label_path, boxes in stratum[cursor : cursor + count]:
                target_image = split_images / split / image.name
                target_label = split_labels / split / f"{image.stem}.txt"
                place(image, target_image, args.copy)
                place(label_path, target_label, args.copy)
                assignments[split].append((image.name, boxes))
            cursor += count

    seen = {}
    for split, items in assignments.items():
        for name, _ in items:
            if name in seen:
                raise SystemExit(f"Duplicate assignment: {name} in {seen[name]} and {split}")
            seen[name] = split

    out_dir.mkdir(parents=True, exist_ok=True)
    path_value = out_dir.as_posix() if not out_dir.is_absolute() else str(out_dir)
    data_yaml = (
        f"path: {path_value}\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "nc: 1\n"
        "names: ['proton_logo']\n"
    )
    (out_dir / "data.yaml").write_text(data_yaml, encoding="utf-8")

    with (out_dir / "split.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["file", "split", "positive", "boxes"])
        for split in SPLITS:
            for name, boxes in sorted(assignments[split]):
                writer.writerow([name, split, int(boxes > 0), boxes])

    print(f"Dataset: {out_dir}")
    print(f"Seed: {args.seed}")
    for split in SPLITS:
        items = assignments[split]
        positive_count = sum(1 for _, boxes in items if boxes)
        box_count = sum(boxes for _, boxes in items)
        print(
            f"  {split:<5} images={len(items):>2} "
            f"positives={positive_count:>2} backgrounds={len(items) - positive_count:>2} "
            f"boxes={box_count:>2}"
        )
    print(f"Wrote {out_dir / 'data.yaml'} and {out_dir / 'split.csv'}")


if __name__ == "__main__":
    main()
