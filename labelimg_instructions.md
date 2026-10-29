# LabelImg instructions (#5)

## 1. Install

```bash
python -m pip install labelImg
```

## 2. Prepare the image pool

```bash
python scripts/prepare_labeling.py
```

This hardlinks (or copies with `--copy`) every image from `data/raw/metadata.csv`
into a flat folder:

- `data/labeled/images/` — images (ignored by Git)
- `data/labeled/labels/` — YOLO `.txt` labels (versioned)
- `data/labeled/classes.txt` — `proton_logo`
- `data/labeled/manifest.csv` — maps each file to its source URL and license

Originals in `data/raw/` are never modified.

## 3. Launch

```bash
labelImg data/labeled/images data/labeled/classes.txt data/labeled/labels
```

Configure before labeling:

1. **Format → YOLO** (toolbar button must show `YOLO`, not `PascalVOC`).
2. **View → Auto Save mode** (saves when moving to the next image).
3. **View → Single class mode** (always uses `proton_logo`).

## 4. Labeling rules

- One **tight** box per visible Proton logo instance.
- Icon + wordmark lockup: one box around the full lockup.
- Only icon or only wordmark: one box around the visible mark.
- Label when the logo is recognizable and at least ~30% visible.
- Skip tiny, blurred, or unreadable logos.
- Do **not** label body text such as "Proton" or third-party logos.
- Negatives and frames without the logo: leave them without boxes.
- If two separate logo instances appear, draw two boxes.

## 5. Shortcuts

| Key | Action |
| --- | --- |
| `W` | Draw box |
| `D` | Next image |
| `A` | Previous image |
| `Ctrl+S` | Save |
| `Del` | Delete selected box |
| `Ctrl+Z` | Undo |
| `Ctrl+=` | Fit window |

## 6. Verify

```bash
python scripts/check_labels.py
```

When all positives are labeled, fill empty labels for backgrounds and validate:

```bash
python scripts/check_labels.py --fill-empty
```

The checker validates class id `0`, YOLO coordinates in `[0,1]`, positive sizes,
missing labels, and orphan label files.

Then commit `data/labeled/labels/`, `classes.txt`, and `manifest.csv`. Images stay
ignored by Git.
