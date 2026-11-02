from __future__ import annotations


def compute_duration(total_frames: int, fps: float) -> float:
    if fps <= 0 or total_frames < 0:
        return 0.0
    return total_frames / fps


def compute_screen_time(frames_with_logo: int, fps: float) -> float:
    if fps <= 0 or frames_with_logo < 0:
        return 0.0
    return frames_with_logo / fps


def compute_percentage(frames_with_logo: int, total_frames: int) -> float:
    if total_frames <= 0 or frames_with_logo < 0:
        return 0.0
    pct = (frames_with_logo / total_frames) * 100.0
    if pct < 0.0:
        return 0.0
    if pct > 100.0:
        return 100.0
    return pct
