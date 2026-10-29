import argparse
import csv
import os
import shutil
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def unique_names(rows):
    used = {}
    prepared = []
    for row in rows:
        source = Path(row["file"])
        name = source.name
        if name in used and used[name] != row["file"]:
            group = row["file"].split("/", 1)[0] if "/" in row["file"] else "root"
            name = f"{group}__{source.name}"
        used[name] = row["file"]
        prepared.append((row, source, name))
    return prepared


def place(source, target, copy):
    if target.exists():
        return "exists"
    if not copy:
        try:
            os.link(source, target)
            return "link"
        except OSError:
            pass
    shutil.copy2(source, target)
    return "copy"


def main():
    parser = argparse.ArgumentParser(
        description="Prepare a flat image pool and manifest for LabelImg."
    )
    parser.add_argument("--metadata", default="data/raw/metadata.csv")
    parser.add_argument("--root", default="data/raw")
    parser.add_argument("--out", default="data/labeled")
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of hardlinking them.",
    )
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    root = Path(args.root)
    out_dir = Path(args.out)
    images_dir = out_dir / "images"
    labels_dir = out_dir / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    classes_path = out_dir / "classes.txt"
    classes_path.write_text("proton_logo\n", encoding="utf-8")

    with metadata_path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    manifest = []
    counts = {"link": 0, "copy": 0, "exists": 0, "missing": 0}
    for row, source, name in unique_names(rows):
        source_path = root / source
        if not source_path.is_file():
            print(f"[missing] {source_path}")
            counts["missing"] += 1
            continue
        if source_path.suffix.lower() not in IMAGE_EXTS:
            print(f"[skip] {source_path}")
            continue
        target = images_dir / name
        action = place(source_path, target, args.copy)
        counts[action] += 1
        manifest.append(
            {
                "file": name,
                "source_file": row["file"],
                "source": row.get("source", ""),
                "url": row.get("url", ""),
                "license": row.get("license", ""),
                "notes": row.get("notes", ""),
                "sha256": row.get("sha256", ""),
            }
        )

    manifest_path = out_dir / "manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "file",
                "source_file",
                "source",
                "url",
                "license",
                "notes",
                "sha256",
            ],
        )
        writer.writeheader()
        writer.writerows(manifest)

    print(f"Images: {images_dir} ({len(manifest)} ready)")
    print(f"Labels: {labels_dir}")
    print(f"Manifest: {manifest_path}")
    print(
        "Actions: "
        + ", ".join(f"{name}={count}" for name, count in counts.items())
    )
    print("\nLaunch LabelImg with:")
    print(
        f"labelImg {images_dir} {classes_path} {labels_dir}"
    )


if __name__ == "__main__":
    main()
