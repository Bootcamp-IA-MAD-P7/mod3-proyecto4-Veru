import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageStat

THUMB = 320
COLS = 6
PER_SHEET = 30
DUP_DISTANCE = 5


def dhash(image):
    gray = ImageOps.exif_transpose(image).convert("L").resize(
        (9, 8), Image.Resampling.LANCZOS
    )
    pixels = list(gray.tobytes())
    bits = 0
    for row in range(8):
        for col in range(8):
            left = pixels[row * 9 + col]
            right = pixels[row * 9 + col + 1]
            bits = (bits << 1) | (1 if left > right else 0)
    return bits


def hamming(a, b):
    return (a ^ b).bit_count()


def sharpness(image):
    edges = ImageOps.exif_transpose(image).convert("L").filter(ImageFilter.FIND_EDGES)
    return ImageStat.Stat(edges).var[0]


def group_key(relative_path):
    return relative_path.split("/", 1)[0] if "/" in relative_path else "root"


def load_rows(metadata_path, root):
    rows = []
    with metadata_path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows.append((row, root / row["file"]))
    return rows


def make_sheets(items, out_dir, key):
    items = sorted(items, key=lambda item: item[0]["file"])
    sheets = math.ceil(len(items) / PER_SHEET)
    for sheet_index in range(sheets):
        chunk = items[sheet_index * PER_SHEET : (sheet_index + 1) * PER_SHEET]
        rows_count = math.ceil(len(chunk) / COLS)
        sheet = Image.new(
            "RGB", (COLS * THUMB, rows_count * (THUMB + 18)), (28, 28, 28)
        )
        draw = ImageDraw.Draw(sheet)
        for index, (row, path) in enumerate(chunk):
            try:
                image = Image.open(path)
                image = ImageOps.exif_transpose(image).convert("RGBA")
            except OSError:
                continue
            background = Image.new("RGBA", image.size, (28, 28, 28, 255))
            image = Image.alpha_composite(background, image).convert("RGB")
            image.thumbnail((THUMB, THUMB), Image.Resampling.LANCZOS)
            x = (index % COLS) * THUMB
            y = (index // COLS) * (THUMB + 18)
            sheet.paste(
                image,
                (x + (THUMB - image.width) // 2, y + (THUMB - image.height) // 2),
            )
            draw.text(
                (x + 4, y + THUMB + 2),
                Path(row["file"]).name,
                fill=(235, 235, 235),
            )
        suffix = f"_{sheet_index + 1}" if sheets > 1 else ""
        out_path = out_dir / f"contact_{key}{suffix}.jpg"
        sheet.save(out_path, quality=85)
        print(f"[sheet] {out_path} ({len(chunk)} images)")


def main():
    parser = argparse.ArgumentParser(
        description="Validate images, detect near-duplicates and build contact sheets."
    )
    parser.add_argument("--metadata", default="data/raw/metadata.csv")
    parser.add_argument("--root", default="data/raw")
    parser.add_argument("--out", default="data/raw/qa")
    parser.add_argument("--distance", type=int, default=DUP_DISTANCE)
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    root = Path(args.root)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    report = []
    hashes = {}
    groups = defaultdict(list)

    for row, path in load_rows(metadata_path, root):
        try:
            with Image.open(path) as image:
                image = ImageOps.exif_transpose(image)
                width, height = image.size
                mode = image.mode
                digest = dhash(image)
                sharp = sharpness(image)
        except OSError as exc:
            print(f"[bad] {path}: {exc}")
            continue
        report.append(
            {
                "file": row["file"],
                "width": width,
                "height": height,
                "mode": mode,
                "bytes": path.stat().st_size,
                "sharpness": round(sharp, 2),
            }
        )
        hashes[row["file"]] = digest
        groups[group_key(row["file"])].append((row, path))

    items = list(hashes.items())
    duplicates = []
    assigned = set()
    for index, (name, digest) in enumerate(items):
        if name in assigned:
            continue
        group = [name]
        for other_name, other_digest in items[index + 1 :]:
            if other_name in assigned:
                continue
            if hamming(digest, other_digest) <= args.distance:
                group.append(other_name)
                assigned.add(other_name)
        if len(group) > 1:
            assigned.add(name)
            duplicates.append(group)

    report_path = out_dir / "qa_report.csv"
    with report_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["file", "width", "height", "mode", "bytes", "sharpness"],
        )
        writer.writeheader()
        writer.writerows(report)

    print(f"Checked {len(report)} images")
    print(f"Report: {report_path}")
    print(f"Near-duplicate groups (distance <= {args.distance}): {len(duplicates)}")
    for group in duplicates[:20]:
        print("  - " + ", ".join(Path(name).name for name in group))

    small = [row for row in report if min(row["width"], row["height"]) < 400]
    print(f"Small images (short side < 400): {len(small)}")
    for row in small[:10]:
        print(f"  - {row['file']} ({row['width']}x{row['height']})")

    for key, items in groups.items():
        make_sheets(items, out_dir, key)


if __name__ == "__main__":
    main()
