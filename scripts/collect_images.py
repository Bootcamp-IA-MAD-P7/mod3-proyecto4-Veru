import argparse
import csv
import hashlib
import mimetypes
import sys
import urllib.error
import urllib.request
from pathlib import Path

FIELDS = ["file", "source", "url", "license", "notes", "sha256"]
MAGIC = {
    b"\xff\xd8\xff": ".jpg",
    b"\x89PNG\r\n\x1a\n": ".png",
    b"GIF87a": ".gif",
    b"GIF89a": ".gif",
    b"RIFF": ".webp",
}


def detect_ext(data):
    for magic, ext in MAGIC.items():
        if not data.startswith(magic):
            continue
        if ext == ".webp" and data[8:12] != b"WEBP":
            continue
        return ext
    return None


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_metadata(path):
    rows = []
    hashes = set()
    if path.exists():
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                rows.append(row)
                if row.get("sha256"):
                    hashes.add(row["sha256"])
    return rows, hashes


def save_metadata(path, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def next_index(out_dir):
    indexes = []
    for item in out_dir.iterdir():
        if not item.is_file() or not item.stem.startswith("proton_"):
            continue
        suffix = item.stem.split("_", 1)[1]
        if suffix.isdigit():
            indexes.append(int(suffix))
    return max(indexes, default=0) + 1


def download(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; LogoExposureTracker/1.0)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type", "")
    if content_type and not content_type.startswith("image/"):
        raise ValueError(f"not an image (Content-Type: {content_type})")
    ext = (
        detect_ext(data)
        or mimetypes.guess_extension(content_type.split(";")[0])
        or ".img"
    )
    return data, ext


def main():
    parser = argparse.ArgumentParser(
        description="Download Proton logo images from a CSV list."
    )
    parser.add_argument("--input", default="data/raw/urls.csv")
    parser.add_argument("--out", default="data/raw")
    parser.add_argument("--metadata", default="data/raw/metadata.csv")
    args = parser.parse_args()

    input_path = Path(args.input)
    out_dir = Path(args.out)
    metadata_path = Path(args.metadata)

    if not input_path.exists():
        sys.exit(f"Input CSV not found: {input_path} (see data/raw/urls.example.csv)")

    out_dir.mkdir(parents=True, exist_ok=True)
    rows, hashes = load_metadata(metadata_path)
    index = next_index(out_dir)

    with input_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if "url" not in (reader.fieldnames or []):
            sys.exit("Input CSV must contain a 'url' column")

        for line, entry in enumerate(reader, start=2):
            url = (entry.get("url") or "").strip()
            if not url:
                continue
            try:
                data, ext = download(url)
            except (urllib.error.URLError, ValueError, TimeoutError) as exc:
                print(f"[skip] line {line}: {url} -> {exc}")
                continue

            digest = sha256(data)
            if digest in hashes:
                print(f"[dup] line {line}: {url}")
                continue

            filename = f"proton_{index:03d}{ext}"
            (out_dir / filename).write_bytes(data)
            rows.append(
                {
                    "file": filename,
                    "source": (entry.get("source") or "").strip(),
                    "url": url,
                    "license": (entry.get("license") or "").strip(),
                    "notes": (entry.get("notes") or "").strip(),
                    "sha256": digest,
                }
            )
            hashes.add(digest)
            index += 1
            print(f"[ok] {filename} <- {url}")

    save_metadata(metadata_path, rows)
    print(f"Saved {len(rows)} records to {metadata_path}")


if __name__ == "__main__":
    main()
