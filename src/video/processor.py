from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, List

import cv2
from ultralytics import YOLO


def process_video(
    video_path: str | Path,
    model_path: str | Path = "models/best.pt",
    conf: float = 0.5,
    crops_dir: str | Path = "data/crops",
    save_crops: bool = True,
) -> Dict[str, Any]:
    video_path = Path(video_path)
    model_path = Path(model_path)
    crops_dir = Path(crops_dir)
    crops_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(model_path))

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration_sec = total_frames / fps if fps > 0 else 0.0

    frames_with_logo = 0
    detections_list: List[Dict[str, Any]] = []

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, conf=conf, verbose=False)
        has_logo = False

        for r in results:
            if not hasattr(r, "boxes") or r.boxes is None:
                continue
            for box in r.boxes:
                cls_id = int(box.cls[0]) if hasattr(box, "cls") and len(box.cls) > 0 else -1
                # Try to get class name
                cls_name = None
                if hasattr(model, "names") and cls_id in model.names:
                    cls_name = model.names[cls_id]
                conf_score = float(box.conf[0]) if hasattr(box, "conf") and len(box.conf) > 0 else 0.0
                xyxy = box.xyxy[0].cpu().numpy() if hasattr(box.xyxy[0], "cpu") else box.xyxy[0]
                x1, y1, x2, y2 = map(int, xyxy)
                if save_crops and x2 > x1 and y2 > y1:
                    crop = frame[y1:y2, x1:x2]
                    crop_name = f"{video_path.stem}_frame{frame_idx:06d}_cls{cls_id}.jpg"
                    crop_path = crops_dir / crop_name
                    cv2.imwrite(str(crop_path), crop)
                    detections_list.append(
                        {
                            "frame_idx": frame_idx,
                            "class_id": cls_id,
                            "class_name": cls_name,
                            "confidence": conf_score,
                            "bbox": [x1, y1, x2, y2],
                            "crop_path": str(crop_path),
                        }
                    )
                else:
                    detections_list.append(
                        {
                            "frame_idx": frame_idx,
                            "class_id": cls_id,
                            "class_name": cls_name,
                            "confidence": conf_score,
                            "bbox": [x1, y1, x2, y2],
                            "crop_path": None,
                        }
                    )
                has_logo = True

        if has_logo:
            frames_with_logo += 1

        frame_idx += 1

    cap.release()

    logo_time_sec = frames_with_logo / fps if fps > 0 else 0.0
    percentage = (frames_with_logo / total_frames * 100.0) if total_frames > 0 else 0.0

    return {
        "video_path": str(video_path),
        "fps": fps,
        "total_frames": total_frames,
        "duration_sec": duration_sec,
        "frames_with_logo": frames_with_logo,
        "logo_time_sec": logo_time_sec,
        "percentage": percentage,
        "detections": detections_list,
    }
