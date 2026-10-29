# Dataset sources - Proton logo (`proton_logo`)

Target: **Proton AG (proton.me)** privacy company. Class: `proton_logo`.

> Do **not** include Proton Holdings (Malaysian car brand), Proton (Steam compatibility layer), or Proton Records. They are different "Proton" brands.

## 1. Direct image URLs (ready to download)

File: `data/raw/urls.csv` (ignored by Git). Run:

```bash
python scripts/collect_images.py
```

| # | Source | What it gives |
| --- | --- | --- |
| 1 | [Proton AG logo.svg](https://commons.wikimedia.org/wiki/File:Proton_AG_logo.svg) | Corporate wordmark + P icon since 2022 |
| 2 | [Proton AG Logo 02.svg](https://commons.wikimedia.org/wiki/File:Proton_AG_Logo_02.svg) | Alternate corporate logo extraction |
| 3 | [ProtonMail logo.svg](https://commons.wikimedia.org/wiki/File:ProtonMail_logo.svg) | Proton Mail logo since 2022 |
| 4 | [Protonmail logo.svg](https://commons.wikimedia.org/wiki/File:Protonmail_logo.svg) | Legacy ProtonMail logo (2014) |
| 5 | [ProtonMail icon.svg](https://commons.wikimedia.org/wiki/File:ProtonMail_icon.svg) | P icon only |
| 6 | [Proton VPN Logo.svg](https://commons.wikimedia.org/wiki/File:Proton_VPN_Logo.svg) | Proton VPN logo (2023) |
| 7 | [ProtonVPN Logo.svg](https://commons.wikimedia.org/wiki/File:ProtonVPN_Logo.svg) | Legacy ProtonVPN logo (2018) |
| 8 | [Proton Drive Logo.svg](https://commons.wikimedia.org/wiki/File:Proton_Drive_Logo.svg) | Proton Drive logo |
| 9 | [Proton Pass Logo.svg](https://commons.wikimedia.org/wiki/File:Proton_Pass_Logo.svg) | Proton Pass logo |
| 10 | [Proton Calendar Logo.svg](https://commons.wikimedia.org/wiki/File:Proton_Calendar_Logo.svg) | Proton Calendar logo |

Browse more: [Category:Proton AG](https://commons.wikimedia.org/wiki/Category:Proton_AG) and [Category:Proton Mail](https://commons.wikimedia.org/wiki/Category:Proton_Mail).

## 2. Official media kit (manual ZIP downloads)

1. Open [proton.me/media/kit](https://proton.me/media/kit).
2. Download the ZIPs (Proton Drive links):
   - Proton: <https://drive.proton.me/urls/50PRRX6MBW>
   - Proton Mail: <https://drive.proton.me/urls/KDMNN95QFM>
   - Proton Calendar: <https://drive.proton.me/urls/481R3SWQ38>
   - Proton Drive: <https://drive.proton.me/urls/A1JAK0WGY4>
   - Proton VPN: <https://drive.proton.me/urls/5VFT9FFVYR>
   - Proton Pass: <https://drive.proton.me/urls/X2DR4GWR60>
3. Unzip into `data/raw/media_kit/`.
4. Note: the helper only downloads image files, so unzip manually.

License: Proton allows these assets when the media refers back to proton.me.

## 3. Screenshots (web + app)

Capture with light/dark theme, different zoom and window sizes. Vary sections, not just the header.

- <https://proton.me/> (home, hero, product sections)
- <https://proton.me/mail>
- <https://protonvpn.com/>
- <https://proton.me/drive>
- <https://proton.me/calendar>
- <https://proton.me/pass>
- <https://proton.me/blog> (logo in header/footer)
- Actual apps: Proton Mail web, Proton VPN desktop, mobile apps (if available)

Tips:
- Include the logo small/big, top-left, centered, in footers and app splashes.
- Add a few captures with real backgrounds (desktop, terminal, browser tabs) for realism.
- Save as PNG/JPG in `data/raw/screenshots/`.

## 4. Video frames (varied backgrounds)

Official channels:
- <https://www.youtube.com/@ProtonAG>
- <https://www.youtube.com/@ProtonPrivacy>

PeerTube search (demo source): <https://sepiasearch.org/search?query=proton%20mail>

Automated workflow (requires `yt-dlp` and `ffmpeg`):

```bash
python -m pip install yt-dlp
winget install Gyan.FFmpeg
```

Copy `data/raw/video_urls.example.csv` to `data/raw/video_urls.csv`, add your URLs, then:

```bash
python scripts/extract_frames.py --interval 5
```

The script downloads each video, extracts one frame every `--interval` seconds to `data/raw/frames/`, skips exact duplicates by SHA-256, appends provenance to `metadata.csv`, and deletes the video unless you pass `--keep-video`.

YouTube often returns *"Sign in to confirm you're not a bot"*. Prefer PeerTube URLs (the example file includes two), or pass cookies to `yt-dlp` with `--cookies-from-browser`.

Manual fallback:

```bash
yt-dlp -f "bv*[height<=1080]+ba/b" -o "data/raw/video_%(id)s.%(ext)s" "<VIDEO_URL>"
ffmpeg -i data/raw/video_XXXX.mp4 -vf "fps=1/5" data/raw/frames/frame_%04d.png
```

Then review and keep frames where the logo is visible; delete near-duplicates. Record the source video URL in `metadata.csv` notes.

## 5. Negatives (no Proton logo)

Add ~10 negatives to reduce false positives. Do **not** label them; keep them as background-only images.

- Screenshots of Gmail, Outlook, Google, Apple, Mullvad, Signal.
- Desktop/terminal/wallpaper photos with no Proton UI.
- Frames from unrelated YouTube/PeerTube videos.

Save in `data/raw/negatives/` with:

```bash
python scripts/collect_images.py --input data/raw/negatives_urls.csv --out data/raw/negatives --prefix negative
```

Set `notes=negative` in `negatives_urls.csv` so the metadata records their role.

## 6. Target composition (70-90 images)

| Group | Count | Folder |
| --- | --- | --- |
| Official logos / media kit | ~20 | `data/raw/` + `data/raw/media_kit/` |
| Web/app screenshots | ~30 | `data/raw/screenshots/` |
| Video frames | ~25 | `data/raw/frames/` |
| Negatives (backgrounds) | ~10 | `data/raw/negatives/` |
| **Total** | **~85** | |

## 7. Quality checklist

- No exact duplicates: the helper skips identical SHA-256; also remove near-duplicates manually.
- Minimum ~600 px on the shortest side; prefer >= 1280 px wide.
- Formats: `.jpg`, `.png`, `.webp`.
- Logo box clearly visible; avoid heavily blurred or occluded logos.
- Provenance recorded in `data/raw/metadata.csv` (`source`, `url`, `license`).
- Raw images are ignored by Git; only metadata and templates are versioned.
