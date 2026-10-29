import argparse
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def parse_label(path, class_count):
    problems = []
    boxes = 0
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return boxes, problems
    for line_number, line in enumerate(text.splitlines(), 1):
        parts = line.split()
        if len(parts) != 5:
            problems.append(f"{path.name}:{line_number} expected 5 fields")
            continue
        try:
            class_id = int(parts[0])
            cx, cy, width, height = (float(value) for value in parts[1:])
        except ValueError:
            problems.append(f"{path.name}:{line_number} non-numeric value")
            continue
        if not 0 <= class_id < class_count:
            problems.append(
                f"{path.name}:{line_number} class {class_id} out of range"
            )
        for name, value in (
            ("cx", cx),
            ("cy", cy),
            ("width", width),
            ("height", height),
        ):
            if not 0.0 <= value <= 1.0:
                problems.append(
                    f"{path.name}:{line_number} {name}={value} outside [0,1]"
                )
        if width <= 0 or height <= 0:
            problems.append(f"{path.name}:{line_number} non-positive size")
        boxes += 1
    return boxes, problems


def main():
    parser = argparse.ArgumentParser(
        description="Validate YOLO labels and optionally fill background files."
    )
    parser.add_argument("--images", default="data/labeled/images")
    parser.add_argument("--labels", default="data/labeled/labels")
    parser.add_argument("--classes", type=int, default=1)
    parser.add_argument(
        "--fill-empty",
        action="store_true",
        help="Create empty .txt files for images without boxes (background).",
    )
    args = parser.parse_args()

    images_dir = Path(args.images)
    labels_dir = Path(args.labels)
    labels_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(
        path
        for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS
    )

    positives = 0
    backgrounds = 0
    missing = []
    problems = []
    total_boxes = 0

    for image in images:
        label_path = labels_dir / f"{image.stem}.txt"
        if not label_path.exists():
            missing.append(image.name)
            if args.fill_empty:
                label_path.write_text("", encoding="utf-8")
                backgrounds += 1
            continue
        boxes, label_problems = parse_label(label_path, args.classes)
        total_boxes += boxes
        problems.extend(label_problems)
        if boxes:
            positives += 1
        else:
            backgrounds += 1

    known_stems = {image.stem for image in images}
    orphans = sorted(
        path.name
        for path in labels_dir.glob("*.txt")
        if path.stem not in known_stems
    )

    print(f"Images: {len(images)}")
    print(f"Positives: {positives}")
    print(f"Backgrounds: {backgrounds}")
    print(f"Boxes: {total_boxes}")
    print(f"Missing labels: {len(missing)}")
    if missing and not args.fill_empty:
        for name in missing[:20]:
            print(f"  - {name}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
    print(f"Invalid labels: {len(problems)}")
    for problem in problems[:20]:
        print(f"  - {problem}")
    print(f"Orphan labels: {len(orphans)}")
    for name in orphans[:20]:
        print(f"  - {name}")

    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
