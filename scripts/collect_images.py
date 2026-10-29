import argparse
import csv
import hashlib
import mimetypes
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

FIELDS = ["file", "source", "url", "license", "notes", "sha256"]
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
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


def next_index(out_dir, prefix):
    indexes = []
    for item in out_dir.iterdir():
        if not item.is_file() or not item.stem.startswith(f"{prefix}_"):
            continue
        suffix = item.stem.split("_", 1)[1]
        if suffix.isdigit():
            indexes.append(int(suffix))
    return max(indexes, default=0) + 1


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(), response.headers.get("Content-Type", "")


def download(url, retries):
    for attempt in range(retries + 1):
        try:
            data, content_type = fetch(url)
            break
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 503) or attempt == retries:
                raise
            time.sleep(5 * (attempt + 1))

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
        description="Download images from a CSV list of URLs."
    )
    parser.add_argument("--input", default="data/raw/urls.csv")
    parser.add_argument("--out", default="data/raw")
    parser.add_argument("--metadata", default="data/raw/metadata.csv")
    parser.add_argument("--prefix", default="proton")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    input_path = Path(args.input)
    out_dir = Path(args.out)
    metadata_path = Path(args.metadata)

    if not input_path.exists():
        sys.exit(f"Input CSV not found: {input_path} (see data/raw/urls.example.csv)")

    out_dir.mkdir(parents=True, exist_ok=True)
    rows, hashes = load_metadata(metadata_path)
    index = next_index(out_dir, args.prefix)

    with input_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if "url" not in (reader.fieldnames or []):
            sys.exit("Input CSV must contain a 'url' column")

        for line, entry in enumerate(reader, start=2):
            url = (entry.get("url") or "").strip()
            if not url:
                continue
            try:
                data, ext = download(url, args.retries)
            except (urllib.error.URLError, ValueError, TimeoutError) as exc:
                print(f"[skip] line {line}: {url} -> {exc}")
                time.sleep(args.delay)
                continue

            digest = sha256(data)
            if digest in hashes:
                print(f"[dup] line {line}: {url}")
                time.sleep(args.delay)
                continue

            filename = f"{args.prefix}_{index:03d}{ext}"
            file_path = out_dir / filename
            file_path.write_bytes(data)
            rows.append(
                {
                    "file": file_path.relative_to(metadata_path.parent).as_posix(),
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
            time.sleep(args.delay)

    save_metadata(metadata_path, rows)
    print(f"Saved {len(rows)} records to {metadata_path}")


if __name__ == "__main__":
    main()
