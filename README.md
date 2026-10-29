# LogoExposure-Tracker

> *"Medir lo que ya existe. Saber cuándo aparece orgánicamente para decidir mejor."*

## 1. Objetivo del proyecto

**LogoExposure-Tracker** es a Proof of Concept (PoC) that simulates a Media Monitoring system to calculate the **Share of Screen** of the **Proton** logo in videos. 

The objective is to detect, time and quantify how long the Proton logo appears organically in a video, presenting a report with total seconds, percentage of video duration and visual evidence of detections. 

This fits the assignment: *"Analyze a video, detect a new category (brand), indicate if detected, report time of appearance, percentage, and save detections to a database."*

## 2. Why this approach

### The real problem: *Earned Media*

Brands care not only about paid advertising, but also about visibility they get **without paying for it**.

- **Paid Media**: Paid ads (Google Ads, Meta, etc.)
- **Earned Media**: Organic/unpaid appearances (a youtuber recommending Proton, showing the app, a tech review...)

Tools like *Brandwatch*, *Talkwalker* or *Meltwater* already monitor this exact type of exposure.

### Why Proton?

We chose **[Proton](https://proton.me/)** for several reasons:

| Reason | Explanation |
| --- | --- |
| **Commercially real** | Proton has a marketing team that would benefit from knowing its organic reach outside campaigns. |
| **Privacy aligned** | Slogan *"Privacy by default"*. Fits the *open-source*, decentralized and *privacy-first* philosophy. |
| **YOLO-friendly** | Clean, recognizable logo with well-defined shapes. Ideal for retraining with 70-90 images. |
| **Organic presence** | Appears in privacy, Linux, self-hosting, VPN/email comparisons and Google alternatives. |
| **Differentiator** | Most will go for Nike/Adidas/Coca-Cola. Choosing Proton + *Earned Media* shows interpretation of the assignment. |

### What about PeerTube/Fediverse?

The goal is **NOT** to sell this to the Fediverse for advertising. 

**[PeerTube](https://joinpeertube.org/)** will be used **only as a demo video source**. Many privacy-focused creators organically recommend Proton there. This keeps our *privacy-first* touch without violating the Fediverse's anti-advertising philosophy.

## 3. Value proposition

**"LogoExposure-Tracker simulates a Media Monitoring system to quantify the organic *Share of Screen* of the Proton logo, allowing evaluation of the real reach of unpaid exposure."**

This directly answers *"evaluate where to direct efforts"* by looking at existing organic appearances.

## 4. Objectives

### Main (Essential + Medium)
- [ ] Train model by fine-tuning a pretrained model to detect `proton_logo`
- [ ] Localize Proton logo with bounding box in images/videos
- [ ] Analyze video frame by frame to detect the category
- [ ] Calculate screen time in seconds using FPS
- [ ] Calculate percentage: `(frames_with_logo / total_frames) * 100`
- [ ] Show class name under each detection
- [ ] Save all info to local database

### Additional (Advanced/Expert)
- [ ] Show confidence % next to class
- [ ] Save crops of each bounding box
- [ ] Save metadata (filename, duration, logo_time, percentage, date)
- [ ] Local frontend to upload videos easily
- [ ] Dockerized for local execution
- [ ] (Bonus) Vision+Audio correlation with faster-whisper

## 5. Tech stack (100% Open Source & Local-First)
| Component | Tech | Reason |
| --- | --- | --- |
| Version control | Git / GitHub | Organized branches/commits |
| Language | Python 3.11+ | Full pipeline |
| Labeling | LabelImg | Offline, no account |
| Detection | Ultralytics YOLOv8n + PyTorch | Transfer learning, lightweight, great for video |
| Video/Image | OpenCV | Standard, local |
| DB | SQLite | File-based, local |
| Frontend | Streamlit or NiceGUI | Open source local UI |
| Optional download | yt-dlp | PeerTube URL (optional) |
| Optional audio | FFmpeg + faster-whisper (tiny) | Bonus only |
| Containerization | Docker + Docker Compose | Reproducible local run |

## 6. Architecture
```text
[User] -> [Local UI] (upload .mp4/.webm/.mkv or PeerTube URL)
  -> [OpenCV frame extraction]
  -> [YOLOv8n fine-tune proton_logo inference]
  -> [count frames, fps, time%, crops]
  -> [SQLite save] -> [Report: metrics + gallery + history]
```

## 7. DB schema
### `videos`
| Field | Type | Desc |
| --- | --- | --- |
| id | INTEGER PK | ID |
| filename | TEXT | Name |
| source | TEXT | upload/peertube_url |
| duration_sec | REAL | Total duration |
| fps | REAL | FPS |
| total_frames | INTEGER | Total frames |
| frames_with_logo | INTEGER | Frames with detection |
| logo_time_sec | REAL | Time in screen |
| percentage | REAL | % of video |
| processed_at | DATETIME | Timestamp |

### `detections`
| Field | Type | Desc |
| --- | --- | --- |
| id | INTEGER PK | ID |
| video_id | INTEGER FK | FK to videos(id) |
| frame_number | INTEGER | Frame |
| class_name | TEXT | proton_logo |
| confidence | REAL | 0-1 |
| bbox_x1,y1,x2,y2 | REAL/INT | BBox |
| crop_path | TEXT | Path to crop |
| timestamp_sec | REAL | Approx time |

## 8. Repo structure
```plaintext
LogoExposure-Tracker/
├── app/
├── assets/
├── data/{raw,uploads,crops,db,samples}
├── docs/
├── models/
├── notebooks/
├── scripts/{collect_images.py,train,process}
├── src/{detect,video,db}
├── Dockerfile
├── docker-compose.yml
├── labelimg_instructions.md
├── README.md
└── requirements.txt
```

### Collecting images (#4)
1. Copy `data/raw/urls.example.csv` to `data/raw/urls.csv` and fill `url,source,license,notes`.
2. Run `python scripts/collect_images.py`.
3. Review downloads in `data/raw/`; duplicates are skipped via SHA-256.
4. `data/raw/metadata.csv` keeps provenance; raw images are not committed to Git.

## 9. Philosophy
- **Local-first** | **Open-Source** | **Privacy by Design** | **Earned Media Focus** | **Faithful to assignment**

## 10. Documentation
- [`docs/SPECS.md`](docs/SPECS.md)
- [`docs/ISSUES_DESIGN.md`](docs/ISSUES_DESIGN.md)

**Project:** `LogoExposure-Tracker` | **Target:** `Proton` | **Class:** `proton_logo` | **Focus:** *Earned Media | Share of Screen | Video Brand Exposure*
