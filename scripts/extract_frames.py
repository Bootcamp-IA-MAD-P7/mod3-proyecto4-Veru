import argparse
import csv
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

FIELDS = ["file", "source", "url", "license", "notes", "sha256"]


def require_tools(names):
    missing = [name for name in names if not shutil.which(name)]
    if missing:
        sys.exit(
            "Missing required tools: "
            + ", ".join(missing)
            + "\nInstall them first, e.g.:\n"
            + "  python -m pip install yt-dlp\n"
            + "  winget install Gyan.FFmpeg\n"
            + "Then reopen the terminal so PATH is refreshed."
        )


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def sanitize(text, limit=60):
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("._-")
    return (cleaned or "video")[:limit]


def download_video(url, videos_dir, height):
    template = str(videos_dir / "%(id)s.%(ext)s")
    command = [
        "yt-dlp",
        "--no-simulate",
        "--no-playlist",
        "-f",
        f"bv*[height<={height}]+ba/b",
        "--print",
        "after_move:filepath",
        "-o",
        template,
        url,
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        raise RuntimeError(detail[-1] if detail else "yt-dlp failed")
    for line in reversed(result.stdout.splitlines()):
        candidate = Path(line.strip())
        if line.strip() and candidate.exists():
            return candidate
    raise RuntimeError("yt-dlp did not report a downloaded file")


def extract_frames(video, frames_dir, interval, image_format):
    prefix = sanitize(video.stem)
    pattern = str(frames_dir / f"{prefix}_%05d.{image_format}")
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(video),
        "-vf",
        f"fps=1/{interval:g}",
        "-q:v",
        "2",
        pattern,
    ]
    subprocess.run(command, check=True)
    return sorted(frames_dir.glob(f"{prefix}_*.{image_format}"))


def main():
    parser = argparse.ArgumentParser(
        description="Download videos with yt-dlp and extract frames with ffmpeg."
    )
    parser.add_argument("--input", default="data/raw/video_urls.csv")
    parser.add_argument("--videos", default="data/raw/videos")
    parser.add_argument("--out", default="data/raw/frames")
    parser.add_argument("--metadata", default="data/raw/metadata.csv")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--format", choices=["jpg", "png"], default="jpg")
    parser.add_argument("--keep-video", action="store_true")
    args = parser.parse_args()

    require_tools(["yt-dlp", "ffmpeg"])

    input_path = Path(args.input)
    videos_dir = Path(args.videos)
    frames_dir = Path(args.out)
    metadata_path = Path(args.metadata)

    if not input_path.exists():
        sys.exit(
            f"Input CSV not found: {input_path} "
            "(see data/raw/video_urls.example.csv)"
        )

    videos_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)
    rows, hashes = load_metadata(metadata_path)

    failures = 0
    with input_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if "url" not in (reader.fieldnames or []):
            sys.exit("Input CSV must contain a 'url' column")

        for line, entry in enumerate(reader, start=2):
            url = (entry.get("url") or "").strip()
            if not url:
                continue
            print(f"[video] line {line}: {url}")
            try:
                video = download_video(url, videos_dir, args.height)
            except (RuntimeError, OSError) as exc:
                print(f"[skip] line {line}: {exc}")
                failures += 1
                continue

            try:
                frames = extract_frames(video, frames_dir, args.interval, args.format)
            except (subprocess.CalledProcessError, OSError) as exc:
                print(f"[skip] line {line}: ffmpeg failed ({exc})")
                failures += 1
                continue

            if not args.keep_video:
                video.unlink(missing_ok=True)

            kept = 0
            for frame in frames:
                digest = sha256_file(frame)
                if digest in hashes:
                    frame.unlink()
                    continue
                seconds = (int(frame.stem.rsplit("_", 1)[1]) - 1) * args.interval
                notes = (entry.get("notes") or "").strip()
                rows.append(
                    {
                        "file": str(frame.relative_to(metadata_path.parent)),
                        "source": f"video:{(entry.get('source') or 'video').strip()}",
                        "url": url,
                        "license": (entry.get("license") or "").strip(),
                        "notes": f"frame ~{seconds:.0f}s {notes}".strip(),
                        "sha256": digest,
                    }
                )
                hashes.add(digest)
                kept += 1

            print(f"[ok] {kept} frames kept from {video.name}")

    save_metadata(metadata_path, rows)
    print(f"Saved {len(rows)} metadata records to {metadata_path}")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
