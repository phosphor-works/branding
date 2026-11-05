#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 fuddlesworth
# SPDX-License-Identifier: CC-BY-SA-4.0
"""Keep the framed icons renderer-proof and derive their circular variants.

Every framed icon in svg/square/{dark,light} draws three large ambient glow
circles that overflow the inner panel.  Browsers and librsvg trim them with a
clipPath, but QtSvg (what KDE uses to draw icons) ignores clipPath, so there
the glows tint the transparent corners outside the frame.  This script
replaces each glow with its exact geometric intersection with the panel, so
nothing depends on clipping.  The glow's source circle is kept in a
``data-glow="cx cy r"`` attribute, which makes the rewrite repeatable.

It then writes svg/circle/{dark,light}/<name>.svg for each framed icon: the
same artwork with the rounded-square frame swapped for a circle (outer
radius 416, panel radius 380, matching the frame's 36-unit border) and the
glows re-intersected with the disc.

    python3 scripts/variants.py           # rewrite squares, regenerate circles
    python3 scripts/variants.py --check   # exit 1 if anything is out of date

Standard library only.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "svg"
THEMES = ("dark", "light")

# The three ambient glows shared by every framed icon: (cx, cy, r).
GLOWS = {(320.0, 310.0, 440.0), (790.0, 580.0, 460.0), (740.0, 360.0, 390.0)}

CENTER = 512.0
OUTER_SQUARE = dict(x="96", y="96", width="832", height="832", rx="190")
PANEL_SQUARE = dict(x="132", y="132", width="760", height="760", rx="170")
OUTER_RADIUS = 416.0
PANEL_RADIUS = 380.0

EPS = 1e-6


# --------------------------------------------------------------------------
# Geometry: intersection of a circle with a rounded rectangle.
#
# The rounded rectangle's boundary is walked clockwise on screen (SVG y points
# down) as eight pieces: top edge, top-right corner, right edge, bottom-right
# corner, bottom edge, bottom-left corner, left edge, top-left corner.  A
# position on the boundary is s in [0, 8): piece index plus local t in [0, 1).
# A circle is the special case where rx is half the side and the edges have
# zero length.
# --------------------------------------------------------------------------


class RoundedRect:
    def __init__(self, x0: float, y0: float, size: float, rx: float):
        self.x0, self.y0, self.x1, self.y1, self.rx = x0, y0, x0 + size, y0 + size, rx
        x0, y0, x1, y1, r = self.x0, self.y0, self.x1, self.y1, rx
        h = math.pi / 2
        # ("line", start, end) or ("arc", centre, start_angle)
        self.pieces = [
            ("line", (x0 + r, y0), (x1 - r, y0)),
            ("arc", (x1 - r, y0 + r), -h),
            ("line", (x1, y0 + r), (x1, y1 - r)),
            ("arc", (x1 - r, y1 - r), 0.0),
            ("line", (x1 - r, y1), (x0 + r, y1)),
            ("arc", (x0 + r, y1 - r), h),
            ("line", (x0, y1 - r), (x0, y0 + r)),
            ("arc", (x0 + r, y0 + r), 2 * h),
        ]

    def point(self, s: float) -> tuple[float, float]:
        i = int(math.floor(s)) % 8
        t = s - math.floor(s)
        kind, a, b = self.pieces[i]
        if kind == "line":
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        ang = b + t * math.pi / 2
        return (a[0] + self.rx * math.cos(ang), a[1] + self.rx * math.sin(ang))

    def contains(self, p: tuple[float, float]) -> bool:
        x, y = p
        r = self.rx
        cx = min(max(x, self.x0 + r), self.x1 - r)
        cy = min(max(y, self.y0 + r), self.y1 - r)
        return (x - cx) ** 2 + (y - cy) ** 2 <= r * r + EPS

    def crossings(self, c: tuple[float, float], R: float) -> list[float]:
        """Boundary positions s where the circle (c, R) crosses the boundary."""
        out: list[float] = []
        for i, (kind, a, b) in enumerate(self.pieces):
            if kind == "line":
                dx, dy = b[0] - a[0], b[1] - a[1]
                L2 = dx * dx + dy * dy
                if L2 < EPS:
                    continue
                fx, fy = a[0] - c[0], a[1] - c[1]
                B = 2 * (fx * dx + fy * dy)
                Cq = fx * fx + fy * fy - R * R
                disc = B * B - 4 * L2 * Cq
                if disc < 0:
                    continue
                for sgn in (-1, 1):
                    t = (-B + sgn * math.sqrt(disc)) / (2 * L2)
                    if -EPS <= t <= 1 + EPS:
                        out.append(i + min(max(t, 0.0), 1.0 - 1e-9))
            else:
                dx, dy = c[0] - a[0], c[1] - a[1]
                d = math.hypot(dx, dy)
                r = self.rx
                if d < EPS or d > r + R or d < abs(r - R):
                    continue
                along = (r * r - R * R + d * d) / (2 * d)
                h = math.sqrt(max(r * r - along * along, 0.0))
                base = math.atan2(dy, dx)
                spread = math.atan2(h, along)
                for ang in (base - spread, base + spread):
                    rel = (ang - b) % (2 * math.pi)
                    if rel <= math.pi / 2 + EPS:
                        out.append(i + min(rel / (math.pi / 2), 1.0 - 1e-9))
        out.sort()
        deduped: list[float] = []
        for s in out:
            if not deduped or min(abs(s - deduped[-1]), 8 - abs(s - deduped[-1])) > 1e-6:
                deduped.append(s)
        if len(deduped) > 1 and min(abs(deduped[0] - deduped[-1]), 8 - abs(deduped[0] - deduped[-1])) <= 1e-6:
            deduped.pop()
        return deduped

    def boundary_path(self, s_from: float, s_to: float) -> list[str]:
        """Path commands following the boundary clockwise from s_from to s_to."""
        if s_to <= s_from:
            s_to += 8
        cmds: list[str] = []
        s = s_from
        while s < s_to - EPS:
            nxt = min(math.floor(s + EPS) + 1, s_to)
            i = int(math.floor(s + EPS)) % 8
            end = self.point(nxt)
            if self.pieces[i][0] == "line":
                if nxt - s > EPS and self._len(i) > EPS:
                    cmds.append(f"L{fmt(end)}")
            else:
                cmds.append(f"A{num(self.rx)} {num(self.rx)} 0 0 1 {fmt(end)}")
            s = nxt
        return cmds

    def _len(self, i: int) -> float:
        _, a, b = self.pieces[i]
        return math.hypot(b[0] - a[0], b[1] - a[1])

    def full_path(self) -> str:
        return f"M{fmt(self.point(0))} " + " ".join(self.boundary_path(0, 8)) + " Z"


def num(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def fmt(p: tuple[float, float]) -> str:
    return f"{num(p[0])} {num(p[1])}"


def clip_circle(shape: RoundedRect, c: tuple[float, float], R: float) -> str:
    """SVG path data for circle (c, R) intersected with the rounded rect."""
    crossings = shape.crossings(c, R)
    if len(crossings) < 2:
        if shape.contains(c) and all(
            math.hypot(shape.point(k / 4)[0] - c[0], shape.point(k / 4)[1] - c[1]) >= R
            for k in range(32)
        ):
            return (f"M{num(c[0] - R)} {num(c[1])} A{num(R)} {num(R)} 0 1 1 {num(c[0] + R)} {num(c[1])} "
                    f"A{num(R)} {num(R)} 0 1 1 {num(c[0] - R)} {num(c[1])} Z")
        return shape.full_path()

    pts = [(s, shape.point(s)) for s in crossings]
    pts = [(s, p, math.atan2(p[1] - c[1], p[0] - c[0])) for s, p in pts]
    by_angle = sorted(pts, key=lambda q: q[2])
    n = len(by_angle)

    def arc_inside(k: int) -> bool:
        a0 = by_angle[k][2]
        a1 = by_angle[(k + 1) % n][2]
        span = (a1 - a0) % (2 * math.pi)
        mid = a0 + span / 2
        return shape.contains((c[0] + R * math.cos(mid), c[1] + R * math.sin(mid)))

    starts = [k for k in range(n) if arc_inside(k)]
    if not starts:
        return shape.full_path()
    by_s = sorted(pts, key=lambda q: q[0])

    first = starts[0]
    k = first
    cmds = [f"M{fmt(by_angle[k][1])}"]
    for _ in range(2 * n + 2):
        a0 = by_angle[k][2]
        nxt = (k + 1) % n
        span = (by_angle[nxt][2] - a0) % (2 * math.pi)
        large = 1 if span > math.pi else 0
        cmds.append(f"A{num(R)} {num(R)} 0 {large} 1 {fmt(by_angle[nxt][1])}")
        # Follow the frame clockwise to the next crossing that opens an inside arc.
        s_here = by_angle[nxt][0]
        idx = [q[0] for q in by_s].index(s_here)
        s_next = by_s[(idx + 1) % n][0]
        cmds.extend(shape.boundary_path(s_here, s_next))
        k = next(j for j in range(n) if by_angle[j][0] == s_next)
        if k == first:
            break
    else:
        raise RuntimeError("intersection walk did not close")
    return " ".join(cmds) + " Z"


SQUARE_PANEL = RoundedRect(132, 132, 760, 170)
CIRCLE_PANEL = RoundedRect(132, 132, 760, PANEL_RADIUS)


# --------------------------------------------------------------------------
# SVG rewriting.  Text-level so formatting, comments and attribute order of
# hand-written files survive untouched.
# --------------------------------------------------------------------------

ATTR = re.compile(r'([\w:-]+)="([^"]*)"')
GLOW_CIRCLE = re.compile(r"<circle\b([^>]*?)\s*/>")
GLOW_PATH = re.compile(r'<path\b(?=[^>]*\bdata-glow=")([^>]*?)\s*/>')
RECT = re.compile(r"<rect\b([^>]*?)\s*/>")


def attrs(s: str) -> list[tuple[str, str]]:
    return ATTR.findall(s)


def render_attrs(pairs: list[tuple[str, str]]) -> str:
    return "".join(f' {k}="{v}"' for k, v in pairs)


def rewrite_glows(text: str, shape: RoundedRect) -> str:
    def glow_path(c: tuple[float, float], R: float, rest: list[tuple[str, str]]) -> str:
        d = clip_circle(shape, c, R)
        return f'<path data-glow="{num(c[0])} {num(c[1])} {num(R)}" d="{d}"{render_attrs(rest)}/>'

    def on_circle(m: re.Match) -> str:
        a = attrs(m.group(1))
        kv = dict(a)
        try:
            key = (float(kv["cx"]), float(kv["cy"]), float(kv["r"]))
        except (KeyError, ValueError):
            return m.group(0)
        if key not in GLOWS:
            return m.group(0)
        rest = [(k, v) for k, v in a if k not in ("cx", "cy", "r")]
        return glow_path(key[:2], key[2], rest)

    def on_path(m: re.Match) -> str:
        a = attrs(m.group(1))
        kv = dict(a)
        cx, cy, r = (float(v) for v in kv["data-glow"].split())
        rest = [(k, v) for k, v in a if k not in ("data-glow", "d")]
        return glow_path((cx, cy), r, rest)

    text = GLOW_CIRCLE.sub(on_circle, text)
    return GLOW_PATH.sub(on_path, text)


def squares_to_circles(text: str) -> str:
    def on_rect(m: re.Match) -> str:
        a = attrs(m.group(1))
        kv = dict(a)
        geom = {k: kv.get(k) for k in ("x", "y", "width", "height", "rx")}
        if geom == OUTER_SQUARE:
            r = OUTER_RADIUS
        elif geom == PANEL_SQUARE:
            r = PANEL_RADIUS
        else:
            return m.group(0)
        rest = [(k, v) for k, v in a if k not in geom and k != "ry"]
        return f'<circle cx="{num(CENTER)}" cy="{num(CENTER)}" r="{num(r)}"{render_attrs(rest)}/>'

    return RECT.sub(on_rect, text)


def circle_variant(square_text: str, source: str) -> str:
    text = squares_to_circles(square_text)
    text = rewrite_glows(text, CIRCLE_PANEL)
    notice = (f"<!-- Generated by scripts/variants.py from {source}. "
              f"Edit the square icon and re-run the script. -->\n")
    if text.startswith("<?xml"):
        head, _, tail = text.partition("\n")
        return f"{head}\n{notice}{tail}"
    return notice + text


def framed_icons() -> list[Path]:
    return sorted(p for t in THEMES for p in (SVG / "square" / t).glob("*.svg"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="report out-of-date files and exit 1 instead of writing")
    args = ap.parse_args()

    planned: dict[Path, str] = {}
    for square in framed_icons():
        original = square.read_text()
        fixed = rewrite_glows(original, SQUARE_PANEL)
        planned[square] = fixed
        rel = square.relative_to(ROOT).as_posix()
        planned[SVG / "circle" / square.parent.name / square.name] = circle_variant(fixed, rel)

    stale = [p for p, body in planned.items() if not p.exists() or p.read_text() != body]
    if args.check:
        for p in stale:
            print(f"out of date: {p.relative_to(ROOT)}")
        return 1 if stale else 0
    for p in stale:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(planned[p])
        print(f"wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
