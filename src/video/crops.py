from __future__ import annotations

import os
from pathlib import Path

import cv2


def ensure_crops_dir(crops_dir: str | Path) -> Path:
    p = Path(crops_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_crop(
    frame,
    bbox,
    crops_dir: str | Path,
    video_stem: str,
    frame_idx: int,
    cls_id: int,
) -> Path | None:
    try:
        x1, y1, x2, y2 = map(int, bbox)
        if x2 <= x1 or y2 <= y1:
            return None
        crop = frame[y1:y2, x1:x2]
        if crop is None or getattr(crop, "size", 0) == 0:
            return None
        out_dir = ensure_crops_dir(crops_dir)
        crop_name = f"{video_stem}_frame{frame_idx:06d}_cls{cls_id}.jpg"
        crop_path = out_dir / crop_name
        cv2.imwrite(str(crop_path), crop)
        return crop_path
    except Exception:
        return None
