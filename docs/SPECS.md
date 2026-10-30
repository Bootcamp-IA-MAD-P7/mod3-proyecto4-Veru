# SPECS - LogoExposure-Tracker

## 1. Goal
Build a local PoC to detect Proton logo (`proton_logo`) in videos, compute screen time and % of duration, generate a report and save detections + crops in SQLite.

## 2. Scope
### In scope (MVP)
- Detect Proton logo with bbox
- Analyze uploaded video (.mp4/.webm/.mkv)
- Compute frames_with_logo/FPS -> seconds
- Compute % = (frames_with_logo/total_frames)*100
- Show class + confidence
- Save crops + metadata in SQLite
- Local UI to upload and see report
- Organized repo with branches/commits/README

### Out of scope
- Mass scraping
- Real-time streaming
- Training from scratch
- Public cloud deploy

### Bonus
- PeerTube URL with yt-dlp
- Vision+Audio with faster-whisper tiny
- CSV/PDF export

## 3. Functional Requirements
| ID | Req | Priority | Acceptance |
| --- | --- | --- | --- |
| RF-01 | Dataset >=70 images labeled YOLO `proton_logo` | P0 | train/val/test + data.yaml |
| RF-02 | Fine-tune YOLOv8n | P0 | models/best.pt + basic metrics |
| RF-03 | Upload video | P0 | Save to data/uploads/ |
| RF-04 | Frame by frame detection | P0 | Draw bbox, class, conf |
| RF-05 | Screen time | P0 | logo_time_sec correct |
| RF-06 | Percentage | P0 | (frames/total)*100 shown |
| RF-07 | Save crops | P0 | data/crops/ + path in DB |
| RF-08 | SQLite persistence | P0 | videos + detections filled |
| RF-09 | Report view | P0 | duration, time, %, gallery |
| RF-10 | Confidence visible | P1 | % shown |
| RF-11 | History | P1 | list previous analyses |
| RF-12 | PeerTube URL | P2 | yt-dlp optional |
| RF-13 | Vision+Audio | P2 | whisper tiny optional |

## 4. Non-Functional
| ID | Req |
| --- | --- |
| RNF-01 | Local-first |
| RNF-02 | Privacy by Design |
| RNF-03 | Open Source |
| RNF-04 | Reproducible (requirements + Docker) |
| RNF-05 | Efficient (YOLOv8n) |
| RNF-06 | Clean modular code |
| RNF-07 | Clean Git history |
| RNF-08 | Automated tests (pytest) run via `make test` |

## 5. Dataset with LabelImg
- Goal: 70-90 varied images
- Class: `proton_logo`
- Format: YOLO
- Split: ~80/10/10
- data.yaml: nc:1, names:['proton_logo']

## 6. Training
- setup: `python scripts/train/setup_env.py` checks the environment, downloads `models/yolov8n.pt` and validates `data.yaml`
- base: yolov8n.pt
- epochs: 50-70
- imgsz: 640
- copy best.pt -> models/best.pt
- validate on test set

## 7. Video processing
1. `cv2.VideoCapture` to open the video
2. Read `fps`, `frame_count` and compute `duration = frame_count / fps`
3. Iterate frames sequentially (`while cap.read()`)
4. Run YOLOv8n inference per frame (conf >= 0.5, class `proton_logo`)
5. Count frames with at least one detection -> `frames_with_logo`
6. Draw bbox + `proton_logo` + confidence and keep visual evidence
7. Save the crop of each detection in `data/crops/`
8. Compute `logo_time_sec = frames_with_logo / fps`
9. Compute `percentage = (frames_with_logo / total_frames) * 100`
10. Persist video metrics + detections in SQLite

## 8. Database
- File: `data/db/logotracker.db`
- Tables: `videos` and `detections` (schema in README section 7)
- `detections.video_id` references `videos.id`
- One `videos` row per analyzed video; N `detections` rows for frames with logo

## 9. UI
- Local app (Streamlit or NiceGUI)
- Upload `.mp4`/`.webm`/`.mkv` -> saved in `data/uploads/`
- Button to run analysis with progress state
- Report: duration, `logo_time_sec`, `percentage`, confidence and crop gallery
- History: list previous analyses from SQLite

## 10. Deliverables
- `data.yaml` + labeled dataset (70-90 images, YOLO format)
- `models/best.pt` (fine-tuned YOLOv8n)
- Modular source (`src/detect`, `src/video`, `src/db`) + scripts
- SQLite DB populated (`videos` + `detections`)
- Demo video and screenshots in `assets/`
- README with setup, training and run instructions
- `requirements.txt` + Docker for reproducible run

## 11. Testing
Testing is incremental: every epic is closed only when its tests are green.
The suite is orchestrated from the `Makefile` and lives in `tests/` with pytest
markers per epic (`epic2`..`epic6`) plus `smoke` for fast integration checks.

| Epic | Make target | Coverage |
| --- | --- | --- |
| 2 - Dataset & labeling | `make test-epic2` | `allocate`, label parsing, manifest dedupe, split without overlap, `data.yaml` |
| 3 - Model & training | `make test-epic3` | dataset loading, `models/best.pt` exists, single-image inference schema |
| 4 - Video + metrics + DB | `make test-epic4` | `logo_time_sec`, `percentage`, crop paths, SQLite FK and rows |
| 5 - Frontend | `make test-epic5` | app imports/runs headless |
| 6 - Polish & Docker | `make test-epic6` | end-to-end with a real video (issue #21) |

Commands:
```bash
make install      # runtime + dev dependencies (pytest)
make test         # full suite
make test-unit    # everything not marked smoke
make test-smoke   # fast integration checks
make check        # compileall + full suite
```

Unit tests must not hit the network nor require the real dataset: use `tmp_path`
and small synthetic files. Tests that need training weights, videos or ffmpeg are
marked with their epic and skipped when the artifact is missing.

## 12. Acceptance criteria (MVP)
- Logo detected with bbox, class name and confidence
- `logo_time_sec` and `percentage` correct for a test video
- Crops saved and linked in the DB
- Report and history visible in the local UI
- Full pipeline runs locally following the README steps
- `make check` passes before closing any issue
