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

Configure before labeling. There is **no “Configura” button** and no **Format** menu:

1. In the **left toolbar**, find the button whose text is `PascalVOC`. Click it once; it becomes `YOLO` (the next click would be `CreateML`, and another returns to `PascalVOC`). The same toggle is in **File → PascalVOC**.
2. Menu **View → Auto Save mode** (leave it checked).
3. Menu **View → Single class mode** (leave it checked).

If you do not see the menu or left toolbar, maximize the window. If the toolbar is still missing, right-click on the top bar area and enable **Tools**.

> **Important:** when the label dialog opens, type or select `proton_logo` **before** pressing OK/Enter. Pressing OK with an empty field crashes LabelImg 1.8.6 (assertion error in `set_last_label`).

To draw a box: press `W`, then **press and hold** the left mouse button at one corner of the logo, drag to the opposite corner and release. A single click without dragging does not create a box.

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
| `Ctrl+F` | Fit window |
| `Space` | Verify image |
| `Ctrl+R` | Change save dir |

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
