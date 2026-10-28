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

## 5. Dataset with LabelImg
- Goal: 70-90 varied images
- Class: `proton_logo`
- Format: YOLO
- Split: ~80/10/10
- data.yaml: nc:1, names:['proton_logo']

## 6. Training
- base: yolov8n.pt
- epochs: 50-70
- imgsz: 640
- copy best.pt -> models/best.pt
- validate on test set

## 7. Video processing
1. cv2.VideoCapture
2. get fps/frame_count/duration
3
