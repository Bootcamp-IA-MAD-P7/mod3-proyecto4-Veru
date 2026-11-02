#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from src.video.processor import process_video


def main() -> None:
    parser = argparse.ArgumentParser(description="Process video to detect proton_logo")
    parser.add_argument("video", type=str, help="Path to input video")
    parser.add_argument("--model", type=str, default="models/best.pt", help="Path to YOLO model")
    parser.add_argument("--conf", type=float, default=0.5, help="Confidence threshold")
    parser.add_argument("--crops-dir", type=str, default="data/crops", help="Directory to save crops")
    parser.add_argument("--no-crops", action="store_true", help="Do not save crops")
    args = parser.parse_args()

    res = process_video(
        video_path=args.video,
        model_path=args.model,
        conf=args.conf,
        crops_dir=args.crops_dir,
        save_crops=not args.no_crops,
    )

    print("Video:", res["video_path"])
    print(f"FPS: {res['fps']:.3f}  Total frames: {res['total_frames']}  Duration: {res['duration_sec']:.2f}s")
    print(f"Frames with logo: {res['frames_with_logo']}")
    print(f"Logo time: {res['logo_time_sec']:.2f}s  Percentage: {res['percentage']:.2f}%")


if __name__ == "__main__":
    main()
