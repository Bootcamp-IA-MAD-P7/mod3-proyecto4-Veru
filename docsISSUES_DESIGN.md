# Issues Design for GitHub Projects + Roadmap

## Labels
`setup`, `data`, `model`, `video`, `db`, `ui`, `docker`, `docs`, `bonus`, `priority:P0`, `priority:P1`, `priority:P2`

## Epics

### EPIC 1: SETUP & STRUCTURE
- [ ] #1 [SETUP] Init repo & dev branch
- [ ] #2 [SETUP] Create folder structure
- [ ] #3 [DOCS] README + SPECS

### EPIC 2: DATASET & LABELING
- [ ] #4 [DATA] Collect Proton logo images (70-90)
- [ ] #5 [DATA] Label with LabelImg (proton_logo, YOLO)
- [ ] #6 [DATA] Split + data.yaml

### EPIC 3: MODEL & TRAINING
- [ ] #7 [MODEL] Env + yolov8n.pt
- [ ] #8 [MODEL] Fine-tune YOLOv8n (50-70)
- [ ] #9 [MODEL] Validate & copy best.pt to models/

### EPIC 4: VIDEO + METRICS + DB
- [ ] #10 [VIDEO] process_video.py core
- [ ] #11 [VIDEO] frames/fps/time/%
- [ ] #12 [VIDEO] crops saving
- [ ] #13 [DB] SQLite schema (videos+detections)
- [ ] #14 [DB] Integrate save

### EPIC 5: FRONTEND
- [ ] #15 [UI] App base
- [ ] #16 [UI] Upload + run analysis
- [ ] #17 [UI] Report + gallery
- [ ] #18 [UI] History

### EPIC 6: POLISH & DOCKER
- [ ] #19 [DOCKER] Dockerfile + compose
- [ ] #20 [DOCS] Polish README + assets
- [ ] #21 [TEST] End-to-end with real video
- [ ] #22 [CLEAN] Final cleanup

### EPIC 7: BONUS
- [ ] #23 [BONUS] yt-dlp PeerTube URL
- [ ] #24 [BONUS] faster-whisper tiny
- [ ] #25 [BONUS] CSV/PDF export

## Kanban columns
Backlog | Todo | In Progress | Review | Done

## Roadmap
| Day | Focus | Issues |
| --- | --- | --- |
| Day1 | Setup+Dataset | #1-#6 |
| Day2 | Training | #7-#9 |
| Day3 | Video+DB | #10-#14 |
| Day4 AM | UI | #15-#18 |
| Day4 PM | Polish+Demo | #19-#22 (bonus only if free) |

**Rule:** MVP first. Earned Media / Share of Screen. Use `proton_logo`. PeerTube only for demo.
