"""Patch LabelImg 1.8.6 for PyQt5 5.15.11 / Python 3.14.

PyQt5 no longer accepts float coordinates in QPainter.drawLine/drawRect/drawText.
LabelImg passes QPointF components directly, which aborts the app with
``TypeError: arguments did not match any overloaded call``.
"""

import importlib.util
from pathlib import Path

CANVAS_OLD = """            p.drawRect(left_top.x(), left_top.y(), rect_width, rect_height)

        if self.drawing() and not self.prev_point.isNull() and not self.out_of_pixmap(self.prev_point):
            p.setPen(QColor(0, 0, 0))
            p.drawLine(self.prev_point.x(), 0, self.prev_point.x(), self.pixmap.height())
            p.drawLine(0, self.prev_point.y(), self.pixmap.width(), self.prev_point.y())"""

CANVAS_NEW = """            p.drawRect(
                int(left_top.x()),
                int(left_top.y()),
                int(rect_width),
                int(rect_height),
            )

        if self.drawing() and not self.prev_point.isNull() and not self.out_of_pixmap(self.prev_point):
            p.setPen(QColor(0, 0, 0))
            p.drawLine(
                int(self.prev_point.x()),
                0,
                int(self.prev_point.x()),
                self.pixmap.height(),
            )
            p.drawLine(
                0,
                int(self.prev_point.y()),
                self.pixmap.width(),
                int(self.prev_point.y()),
            )"""

SHAPE_OLD = "painter.drawText(min_x, min_y, self.label)"
SHAPE_NEW = "painter.drawText(int(min_x), int(min_y), self.label)"


def module_path(name):
    spec = importlib.util.find_spec(name)
    if spec is None or spec.origin is None:
        raise SystemExit(f"Cannot find {name}; is LabelImg installed?")
    return Path(spec.origin)


def patch(path, old, new):
    text = path.read_text(encoding="utf-8")
    if new in text and old not in text:
        print(f"[ok] already patched: {path}")
        return
    if old not in text:
        raise SystemExit(f"[error] expected code not found in {path}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print(f"[fixed] {path}")


def main():
    patch(module_path("libs.canvas"), CANVAS_OLD, CANVAS_NEW)
    patch(module_path("libs.shape"), SHAPE_OLD, SHAPE_NEW)
    print("Restart LabelImg.")


if __name__ == "__main__":
    main()
