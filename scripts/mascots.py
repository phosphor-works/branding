#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 fuddlesworth
# SPDX-License-Identifier: CC-BY-SA-4.0
"""Generate the Phosphor mascots: Glim, Wisp and Nocti.

Each mascot is drawn as a standalone mark on a transparent background
(svg/mascot/<name>.svg) and as a Discord style avatar inside the suite's
gradient ring (svg/mascot/avatar/<name>.svg). The bodies, tentacles, ribbons
and rim lights are computed, so edit this script rather than the SVGs, then
run:

    python3 scripts/mascots.py
"""

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "svg" / "mascot"

CYAN, BLUE, PURPLE, ROSE = "#22D3EE", "#3B82F6", "#A855F7", "#F43F5E"
NAVY, ABYSS, VOID = "#0B1730", "#070F22", "#050916"
INK = "#1E1B4B"

# The Phosphor mark, from svg/mark/dark/phosphor.svg: a spindle and four crescents.
PHI_SPINDLE = "M512 206 C540 372 540 652 512 818 C484 652 484 372 512 206 Z"
PHI_ARCS = [
    "M583 358L598 362L612 367L626 374L639 381L652 389L664 398L676 408L686 419L695 431L703 444L709 458L714 472L716 487L714 502L702 516L689 504L685 492L681 480L678 469L674 457L669 446L664 434L658 423L650 412L641 401L632 391L621 382L609 373L597 365L583 358Z",
    "M696 553L706 571L704 588L698 603L690 618L680 631L668 643L654 653L640 661L624 669L608 674L592 678L575 681L559 682L541 676L555 665L569 658L582 651L594 643L605 635L616 626L626 617L635 607L643 598L652 589L660 579L668 570L678 560L696 553Z",
    "M483 676L465 682L449 681L432 678L416 674L400 669L384 661L370 653L356 643L344 631L334 618L326 603L320 588L318 571L328 553L346 560L356 570L364 579L372 589L381 598L389 607L398 617L408 626L419 635L430 643L442 651L455 658L469 665L483 676Z",
    "M322 516L310 502L308 487L310 472L315 458L321 444L329 431L338 419L348 408L360 398L372 389L385 381L398 374L412 367L426 362L441 358L427 365L415 373L403 382L392 391L383 401L374 412L366 423L360 434L355 446L350 457L346 469L343 480L339 492L335 504L322 516Z",
]


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def smooth(pts, closed=False, k=1 / 6):
    """A Catmull-Rom spline through pts, written as cubic Beziers."""
    n = len(pts)

    def at(i):
        return pts[i % n] if closed else pts[max(0, min(n - 1, i))]

    d = f"M{f(pts[0][0])} {f(pts[0][1])}"
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = at(i - 1), at(i), at(i + 1), at(i + 2)
        d += (f" C{f(p1[0] + (p2[0] - p0[0]) * k)} {f(p1[1] + (p2[1] - p0[1]) * k)}"
              f" {f(p2[0] - (p3[0] - p1[0]) * k)} {f(p2[1] - (p3[1] - p1[1]) * k)}"
              f" {f(p2[0])} {f(p2[1])}")
    return d + ("Z" if closed else "")


def blur(id_, sd):
    return (f'<filter id="{id_}" x="-60%" y="-60%" width="220%" height="220%" '
            f'color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{sd}"/></filter>')


def star(cx, cy, r, fill, op=1.0):
    """Four point sparkle."""
    k = r * 0.2
    d = (f"M{f(cx)} {f(cy-r)} Q{f(cx+k)} {f(cy-k)} {f(cx+r)} {f(cy)} "
         f"Q{f(cx+k)} {f(cy+k)} {f(cx)} {f(cy+r)} Q{f(cx-k)} {f(cy+k)} {f(cx-r)} {f(cy)} "
         f"Q{f(cx-k)} {f(cy-k)} {f(cx)} {f(cy-r)}Z")
    return f'<path d="{d}" fill="{fill}" opacity="{op}"/>'


def eye(p, n, cx, cy, rx, ry, halo=False):
    """A stylised eye: a dark oval, a glow reflected along its lower edge and
    two catchlights. halo=True adds a soft light ring so the eye holds
    against a bright surface."""
    cid = f"{p}eye{n}"
    s = [f'<clipPath id="{cid}"><ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}"/></clipPath>']
    if halo:
        s.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx+5)}" ry="{f(ry+5)}" fill="#ECFEFF" opacity=".7" filter="url(#{p}b3)"/>')
    s.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="url(#{p}pupil)"/>')
    s.append(f'<g clip-path="url(#{cid})">'
             f'<ellipse cx="{f(cx)}" cy="{f(cy+ry*.95)}" rx="{f(rx*.95)}" ry="{f(ry*.5)}" fill="{PURPLE}" opacity=".55" filter="url(#{p}b3)"/>'
             f'<ellipse cx="{f(cx)}" cy="{f(cy+ry*1.1)}" rx="{f(rx*.8)}" ry="{f(ry*.42)}" fill="{CYAN}" opacity=".8" filter="url(#{p}b3)"/></g>')
    s.append(f'<ellipse cx="{f(cx-rx*.3)}" cy="{f(cy-ry*.36)}" rx="{f(rx*.38)}" ry="{f(ry*.3)}" fill="#fff"/>')
    s.append(f'<circle cx="{f(cx+rx*.34)}" cy="{f(cy+ry*.2)}" r="{f(rx*.16)}" fill="#fff" opacity=".85"/>')
    return "".join(s)


def smile(cx, cy, w, col=INK, op=.85):
    return (f'<path d="M{f(cx-w)} {f(cy)} Q{f(cx)} {f(cy+w*.95)} {f(cx+w)} {f(cy)}" stroke="{col}" '
            f'stroke-width="{f(w*.36)}" stroke-linecap="round" opacity="{op}"/>')


def blush(p, cx, cy, rx, ry, op=.5):
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{ROSE}" opacity="{op}" filter="url(#{p}b3)"/>'


def common_defs(p):
    return (
        f'<radialGradient id="{p}pupil" cx=".42" cy=".3" r=".8"><stop offset="0" stop-color="#27346B"/>'
        f'<stop offset=".7" stop-color="#0B1030"/><stop offset="1" stop-color="{VOID}"/></radialGradient>'
        + blur(f"{p}b3", 3) + blur(f"{p}b6", 6) + blur(f"{p}b12", 12) + blur(f"{p}b24", 24)
    )


# ── Glim, the firefly ────────────────────────────────────────────────────────

def glim():
    p = "gl-"
    HX, HY, HR = 186, 226, 94

    # The body is one egg from under the head to the lantern tip: an axis
    # with a half width profile, fatter toward the tail.
    ax0, ay0, ax1, ay1 = 232, 258, 400, 410
    dx, dy = ax1 - ax0, ay1 - ay0
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux                      # toward the belly

    def half(t):
        return 76 * (2 * math.sqrt(t * (1 - t))) ** .8 * (.56 + .44 * t)

    def on(t, side=0.0):
        w = half(t) * side
        return ax0 + dx * t + nx * w, ay0 + dy * t + ny * w

    N = 40
    ts = [(1 - math.cos(math.pi * i / N)) / 2 for i in range(N + 1)]
    body = smooth([on(t, -1) for t in ts] + [on(t, 1) for t in ts[::-1]][1:-1], closed=True)

    def leaf(L, W):
        """A wing in its own frame: hinge at the origin, tip along +x."""
        return (f"M0 0 C{f(.16*L)} {f(-.8*W)} {f(.6*L)} {f(-1.08*W)} {f(.9*L)} {f(-.6*W)} "
                f"C{f(1.05*L)} {f(-.34*W)} {f(1.04*L)} {f(.16*W)} {f(.9*L)} {f(.32*W)} "
                f"C{f(.6*L)} {f(.62*W)} {f(.2*L)} {f(.42*W)} 0 0Z")

    JX, JY = 258, 250                     # wing hinge, on the back behind the head

    def hinge(a):
        return f'transform="translate({JX} {JY}) rotate({a})"'

    lx, ly = on(.8)
    # The lantern sits low and right, so the halo must fade out before the
    # nearest canvas edge; a wider one is cut off there in a visible box.
    HALO = 150
    defs = common_defs(p) + f"""
<radialGradient id="{p}halo" cx="{f(lx)}" cy="{f(ly)}" r="{HALO}" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{CYAN}" stop-opacity=".55"/><stop offset=".35" stop-color="{CYAN}" stop-opacity=".2"/>
  <stop offset=".7" stop-color="{BLUE}" stop-opacity=".07"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
<radialGradient id="{p}head" cx=".36" cy=".28" r=".85">
  <stop offset="0" stop-color="#C3D5FF"/><stop offset=".32" stop-color="#8FA3FA"/>
  <stop offset=".72" stop-color="#5B5FE8"/><stop offset="1" stop-color="#3F2FB8"/></radialGradient>
<linearGradient id="{p}body" x1="{ax0}" y1="{ay0}" x2="{ax1}" y2="{ay1}" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#4F46E5"/><stop offset=".3" stop-color="#6D28D9"/><stop offset=".46" stop-color="#8B3FE0"/>
  <stop offset=".6" stop-color="#4FB4F0"/><stop offset=".76" stop-color="#A5F3FC"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
<radialGradient id="{p}lamp" cx="{f(lx)}" cy="{f(ly)}" r="92" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#FFFFFF"/><stop offset=".35" stop-color="#E0FCFF" stop-opacity=".95"/>
  <stop offset=".7" stop-color="{CYAN}" stop-opacity=".5"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}ely" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#A78BFA"/><stop offset=".45" stop-color="#6D28D9"/><stop offset="1" stop-color="#3B1A8C"/></linearGradient>
<linearGradient id="{p}elyF" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#5B21B6"/><stop offset="1" stop-color="#2E1A6E"/></linearGradient>
<linearGradient id="{p}wing" x1="0" y1="1" x2="1" y2="0">
  <stop offset="0" stop-color="#A5F3FC" stop-opacity=".7"/><stop offset=".55" stop-color="#93C5FD" stop-opacity=".36"/>
  <stop offset="1" stop-color="#DDD6FE" stop-opacity=".3"/></linearGradient>
<linearGradient id="{p}ant" x1="0" y1="1" x2="0" y2="0">
  <stop offset="0" stop-color="#5B5FE8"/><stop offset="1" stop-color="#C4B5FD"/></linearGradient>
<clipPath id="{p}bodyc"><path d="{body}"/></clipPath>
<clipPath id="{p}headc"><circle cx="{HX}" cy="{HY}" r="{HR}"/></clipPath>
"""
    b = [f'<circle cx="{f(lx)}" cy="{f(ly)}" r="{HALO}" fill="url(#{p}halo)"/>']

    # light trail drifting off behind the lantern
    for x, y, r, o in ((440, 446, 6, .9), (460, 466, 4.2, .65), (476, 482, 3, .45), (420, 466, 3, .5)):
        b.append(f'<circle cx="{x}" cy="{y}" r="{f(r*2.6)}" fill="{CYAN}" opacity="{f(o*.45)}" filter="url(#{p}b6)"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="{f(r)}" fill="#ECFEFF" opacity="{f(o)}"/>')

    # wings fan up from one hinge: far membrane, far cover, near membrane
    def membrane(a, L, W, op):
        d = leaf(L, W)
        veins = "".join(
            f'<path d="M4 0 C{f(L*.3)} {f(v*W*.7)} {f(L*.6)} {f(v*W)} {f(L*.88)} {f(v*W*.8)}" stroke="#ECFEFF" '
            f'stroke-width="1.3" stroke-opacity=".4" stroke-linecap="round"/>' for v in (-.62, -.18, .2))
        return (f'<g {hinge(a)} opacity="{op}"><path d="{d}" fill="url(#{p}wing)"/>{veins}'
                f'<path d="{d}" stroke="#E0F2FE" stroke-width="2" stroke-opacity=".75" stroke-linejoin="round"/></g>')

    b.append(membrane(-72, 176, 50, .7))
    b.append(f'<path {hinge(-54)} d="{leaf(128, 36)}" fill="url(#{p}elyF)" stroke="#8B5CF6" stroke-width="1.6" stroke-opacity=".6"/>')
    b.append(membrane(-36, 214, 60, 1))

    # legs, tucked under the body
    for t, reach in ((.17, 26), (.31, 30), (.45, 27)):
        x0, y0 = on(t, .8)
        x1, y1 = x0 + nx * reach - 2, y0 + ny * reach + 12
        d = f"M{f(x0)} {f(y0)} Q{f(x0+nx*reach*.55+ux*11)} {f(y0+ny*reach*.55+uy*11)} {f(x1)} {f(y1)}"
        b.append(f'<path d="{d}" stroke="#4338CA" stroke-width="7" stroke-linecap="round"/>')
        b.append(f'<circle cx="{f(x1)}" cy="{f(y1)}" r="4.6" fill="#6366F1"/>')

    # body: lantern bloom, the lit form, then shading clipped to it
    b.append(f'<circle cx="{f(lx)}" cy="{f(ly)}" r="78" fill="{CYAN}" opacity=".8" filter="url(#{p}b24)"/>')
    b.append(f'<path d="{body}" fill="url(#{p}body)"/>')
    b.append(f'<g clip-path="url(#{p}bodyc)">')
    bx, by = on(.36, .95)
    ex, ey = on(.56, .95)
    b.append(f'<path d="M{f(on(.1,.9)[0])} {f(on(.1,.9)[1])} Q{f(bx)} {f(by)} {f(ex)} {f(ey)}" stroke="{VOID}" stroke-width="44" stroke-linecap="round" opacity=".42" filter="url(#{p}b12)"/>')
    hx0, hy0 = on(.18, -.62)
    hx1, hy1 = on(.46, -.66)
    b.append(f'<path d="M{f(hx0)} {f(hy0)} L{f(hx1)} {f(hy1)}" stroke="#E9D5FF" stroke-width="16" stroke-linecap="round" opacity=".4" filter="url(#{p}b6)"/>')
    b.append(f'<circle cx="{f(lx)}" cy="{f(ly)}" r="92" fill="url(#{p}lamp)"/>')
    # lantern segments, crossing the body and bowed toward the tail
    for t, col, o, w in ((.5, INK, .5, 3.4), (.64, "#0E7490", .42, 3), (.78, "#0891B2", .3, 2.6)):
        a, c, e = on(t, -1.02), on(t + .075), on(t, 1.02)
        b.append(f'<path d="M{f(a[0])} {f(a[1])} Q{f(c[0])} {f(c[1])} {f(e[0])} {f(e[1])}" stroke="{col}" stroke-width="{w}" opacity="{o}" stroke-linecap="round"/>')
    # shade where the head overhangs
    b.append(f'<circle cx="{HX+10}" cy="{HY+12}" r="{HR+4}" fill="{VOID}" opacity=".5" filter="url(#{p}b12)"/>')
    b.append('</g>')
    # rim light around the lantern end
    rim = smooth([on(t, -1) for t in ts if t > .6] + [on(t, 1) for t in ts[::-1][1:] if t > .7])
    b.append(f'<path d="{rim}" stroke="#ECFEFF" stroke-width="2.4" stroke-linecap="round" opacity=".75"/>')

    # near wing cover: glossy, rose edged, lifted clear of the back
    ely = leaf(150, 44)
    b.append(f'<g {hinge(-13)}><path d="{ely}" fill="url(#{p}ely)"/>'
             f'<path d="M22 -14 C54 -34 98 -38 130 -24" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".45" filter="url(#{p}b3)"/>'
             f'<path d="M30 -17 C58 -31 92 -34 118 -26" stroke="#F5F3FF" stroke-width="2.4" stroke-linecap="round" opacity=".7"/>'
             f'<path d="M40 22 C78 30 116 24 140 8" stroke="{CYAN}" stroke-width="8" stroke-linecap="round" opacity=".45" filter="url(#{p}b6)"/>'
             f'<path d="{ely}" stroke="{ROSE}" stroke-width="2.4" stroke-opacity=".85" stroke-linejoin="round"/></g>')

    # antennae
    for d, tip, col in (("M158 142 C150 108 132 86 100 80", (100, 80), CYAN),
                        ("M204 136 C204 100 216 74 244 58", (244, 58), ROSE)):
        b.append(f'<path d="{d}" stroke="url(#{p}ant)" stroke-width="6" stroke-linecap="round"/>')
        x, y = tip
        b.append(f'<circle cx="{x}" cy="{y}" r="20" fill="{col}" opacity=".6" filter="url(#{p}b6)"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{col}"/>')
        b.append(f'<circle cx="{x-2.5}" cy="{y-2.5}" r="3.2" fill="#fff" opacity=".9"/>')

    # head
    b.append(f'<circle cx="{HX}" cy="{HY}" r="{HR}" fill="url(#{p}head)"/>')
    b.append(f'<g clip-path="url(#{p}headc)">'
             f'<ellipse cx="{HX-34}" cy="{HY-52}" rx="50" ry="30" fill="#fff" opacity=".3" filter="url(#{p}b12)"/>'
             f'<circle cx="{HX+70}" cy="{HY+78}" r="46" fill="{CYAN}" opacity=".5" filter="url(#{p}b24)"/></g>')
    b.append(f'<path d="M{HX-80} {HY-34} A{HR-6} {HR-6} 0 0 1 {HX-22} {HY-84}" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".55"/>')
    b.append(blush(p, HX - 58, HY + 40, 15, 8))
    b.append(blush(p, HX + 44, HY + 44, 15, 8))
    b.append(eye(p, 1, HX - 36, HY + 8, 18, 24))
    b.append(eye(p, 2, HX + 26, HY + 11, 18, 24))
    b.append(smile(HX - 5, HY + 42, 9))

    b.append(star(84, 352, 10, "#CFFAFE", .6))
    b.append(star(452, 96, 8, "#E9D5FF", .55))
    b.append(star(330, 46, 5, "#CFFAFE", .4))
    return ("Glim", "A glowing firefly in flight: rose edged wing covers lifted open over translucent wings, and a bright cyan lantern at its tail.",
            defs, "".join(b))


# ── Wisp, the will-o'-the-wisp ───────────────────────────────────────────────

def wisp():
    p = "wi-"
    outer = ("M256 454 C192 454 140 404 140 338 C140 290 168 262 182 222 C190 198 188 172 176 146 "
             "C206 160 228 186 236 218 C228 160 232 98 270 38 C276 100 318 138 322 200 "
             "C334 182 342 158 338 128 C366 170 372 262 372 338 C372 404 320 454 256 454Z")
    mid = ("M256 440 C200 440 158 398 158 340 C158 300 182 274 194 240 C200 222 200 204 194 186 "
           "C216 200 232 222 240 246 C236 196 240 140 268 92 C274 140 304 172 308 226 "
           "C318 212 324 194 322 172 C344 208 354 280 354 340 C354 398 312 440 256 440Z")
    inner = ("M256 428 C208 428 174 392 174 344 C174 310 196 290 206 262 C210 250 210 238 206 226 "
             "C224 238 236 254 242 272 C240 232 246 190 266 150 C272 190 292 214 296 256 "
             "C302 246 306 234 304 220 C322 250 338 300 338 344 C338 392 304 428 256 428Z")
    tail = "M346 388 C350 452 298 494 226 486 C190 482 164 462 158 432 C180 456 214 466 246 460 C282 452 300 436 306 418Z"
    defs = common_defs(p) + f"""
<radialGradient id="{p}halo" cx="256" cy="310" r="240" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{PURPLE}" stop-opacity=".5"/><stop offset=".5" stop-color="{BLUE}" stop-opacity=".16"/>
  <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}l1" x1="0" y1="38" x2="0" y2="454" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#FDA4AF"/><stop offset=".22" stop-color="{ROSE}"/>
  <stop offset=".6" stop-color="#D0409A"/><stop offset="1" stop-color="{PURPLE}"/></linearGradient>
<linearGradient id="{p}l2" x1="0" y1="92" x2="0" y2="440" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#E879F9"/><stop offset=".3" stop-color="{PURPLE}"/>
  <stop offset=".7" stop-color="#6366F1"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
<linearGradient id="{p}l3" x1="0" y1="150" x2="0" y2="428" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#93C5FD"/><stop offset=".35" stop-color="{BLUE}"/>
  <stop offset=".75" stop-color="#38BDF8"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
<radialGradient id="{p}core" cx="256" cy="350" r="104" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" stop-color="#CFFAFE" stop-opacity=".95"/>
  <stop offset=".8" stop-color="#67E8F9" stop-opacity=".6"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}tail" x1="340" y1="410" x2="160" y2="440" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{PURPLE}"/><stop offset=".55" stop-color="#D0409A" stop-opacity=".9"/>
  <stop offset="1" stop-color="{ROSE}" stop-opacity=".25"/></linearGradient>
<linearGradient id="{p}curl" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FDA4AF" stop-opacity="0"/><stop offset="1" stop-color="#FDA4AF" stop-opacity=".9"/></linearGradient>
<linearGradient id="{p}rim" x1="150" y1="60" x2="330" y2="400" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#FFE4E6" stop-opacity=".95"/><stop offset=".55" stop-color="#FECDD3" stop-opacity=".45"/>
  <stop offset="1" stop-color="#FECDD3" stop-opacity="0"/></linearGradient>
<clipPath id="{p}outc"><path d="{outer}"/></clipPath>
"""
    b = [f'<circle cx="256" cy="310" r="240" fill="url(#{p}halo)"/>']
    # tail curling off to the lower left
    b.append(f'<path d="{tail}" fill="{PURPLE}" opacity=".5" filter="url(#{p}b12)"/>')
    b.append(f'<path d="{tail}" fill="url(#{p}tail)"/>')
    # bloom, then three flames nested toward a white hot core
    b.append(f'<path d="{outer}" fill="{PURPLE}" opacity=".75" filter="url(#{p}b24)"/>')
    b.append(f'<path d="{outer}" fill="url(#{p}l1)"/>')
    b.append(f'<g clip-path="url(#{p}outc)">'
             f'<path d="{mid}" fill="{PURPLE}" opacity=".6" filter="url(#{p}b6)"/>'
             f'<path d="{mid}" fill="url(#{p}l2)"/>'
             f'<path d="{inner}" fill="{BLUE}" opacity=".6" filter="url(#{p}b6)"/>'
             f'<path d="{inner}" fill="url(#{p}l3)"/>'
             f'<ellipse cx="256" cy="350" rx="104" ry="92" fill="url(#{p}core)"/>'
             # light climbing the middle tongue
             f'<path d="M262 276 C254 240 256 204 266 172" stroke="#ECFEFF" stroke-width="7" stroke-linecap="round" opacity=".5" filter="url(#{p}b3)"/>'
             f'</g>')
    # rim light along the outer edge
    b.append(f'<path d="{outer}" stroke="url(#{p}rim)" stroke-width="2.6" stroke-linejoin="round"/>')
    # smoke wisps rising from the tongues
    for d, w in (("M270 40 C262 26 280 16 272 2", 5),):
        b.append(f'<path d="{d}" stroke="url(#{p}curl)" stroke-width="{w*2.2}" stroke-linecap="round" filter="url(#{p}b6)"/>')
        b.append(f'<path d="{d}" stroke="url(#{p}curl)" stroke-width="{w*.5}" stroke-linecap="round"/>')
    # embers
    for x, y, r, c in ((212, 96, 4.4, ROSE), (322, 74, 3.4, PURPLE), (388, 132, 3, ROSE), (132, 152, 3.4, PURPLE),
                       (404, 236, 2.6, CYAN), (110, 250, 2.6, CYAN), (238, 30, 2.4, "#E9D5FF")):
        b.append(f'<circle cx="{x}" cy="{y}" r="{f(r*3)}" fill="{c}" opacity=".5" filter="url(#{p}b6)"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="{f(r)}" fill="{c}"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="{f(r*.45)}" fill="#fff" opacity=".9"/>')
    b.append(star(96, 356, 9, "#CFFAFE", .6))
    b.append(star(420, 384, 11, "#FCE7F3", .6))
    # face
    b.append(blush(p, 196, 384, 15, 8, .55))
    b.append(blush(p, 316, 384, 15, 8, .55))
    b.append(eye(p, 1, 220, 348, 19, 26, halo=True))
    b.append(eye(p, 2, 292, 348, 19, 26, halo=True))
    b.append(smile(256, 380, 9))
    return ("Wisp", "A will o the wisp: a rose, purple, blue and cyan flame spirit with a white hot core, a curling tail and drifting embers.",
            defs, "".join(b))


# ── Nocti, the jellyfish ─────────────────────────────────────────────────────

def nocti():
    p = "no-"
    L, R, TOP = 96, 416, 60

    def rim_y(x):
        u = (x - 256) / ((R - L) / 2)
        return 230 + 30 * (1 - u * u)

    n = 10
    pts = [(L + (R - L) * i / n, rim_y(L + (R - L) * i / n)) for i in range(n + 1)]
    scallops = ""
    for i in range(n, 0, -1):
        (x0, y0), (x1, y1) = pts[i], pts[i - 1]
        scallops += f"Q{f((x0+x1)/2)} {f((y0+y1)/2+18)} {f(x1)} {f(y1)} "
    dome = f"M{L} {f(rim_y(L))} C{L-10} 146 166 {TOP} 256 {TOP} C346 {TOP} {R+10} 146 {R} {f(rim_y(R))}"
    bell = f"{dome} {scallops}Z"
    hem = f"M{R} {f(rim_y(R))} {scallops}"

    defs = common_defs(p) + f"""
<radialGradient id="{p}halo" cx="256" cy="210" r="250" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{CYAN}" stop-opacity=".45"/><stop offset=".5" stop-color="{BLUE}" stop-opacity=".16"/>
  <stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
<radialGradient id="{p}bell" cx="236" cy="104" r="240" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#CFFAFE" stop-opacity=".9"/><stop offset=".3" stop-color="#4FD8F0" stop-opacity=".78"/>
  <stop offset=".62" stop-color="{BLUE}" stop-opacity=".72"/><stop offset="1" stop-color="{PURPLE}" stop-opacity=".9"/></radialGradient>
<radialGradient id="{p}sub" cx="256" cy="262" r="160" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#ECFEFF" stop-opacity=".6"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}tent" x1="0" y1="236" x2="0" y2="462" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#A5F3FC" stop-opacity=".95"/><stop offset=".45" stop-color="{PURPLE}" stop-opacity=".7"/>
  <stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></linearGradient>
<linearGradient id="{p}arm" x1="0" y1="250" x2="0" y2="458" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#FB7185"/><stop offset=".5" stop-color="#C850C8" stop-opacity=".85"/>
  <stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>
<linearGradient id="{p}phi" x1="0" y1="206" x2="0" y2="818" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#FFD5DC"/></linearGradient>
<clipPath id="{p}bellc"><path d="{bell}"/></clipPath>
""" + blur(f"{p}phib", 40)
    b = [f'<circle cx="256" cy="210" r="250" fill="url(#{p}halo)"/>']

    # tentacles from each scallop point, longest in the middle
    for i, (x, y) in enumerate(pts):
        if i in (0, n):
            continue
        length = 126 + 70 * math.sin(math.pi * i / n) + 18 * math.sin(i * 2.3)
        amp, ph = 9 + 3 * math.cos(i), i * .9
        line = [(x + (x - 256) * .16 * t + amp * t ** .5 * math.sin(ph + t * 5.2), y + 4 + length * t)
                for t in (s / 14 for s in range(15))]
        b.append(f'<path d="{smooth(line)}" stroke="url(#{p}tent)" stroke-width="{3.4 if i % 2 else 2.4}" stroke-linecap="round"/>')

    # oral arms: four frilled ribbons
    def ribbon(x0, sway, length, ph):
        left, right = [], []
        steps = 44
        for k in range(steps + 1):
            t = k / steps
            y = 248 + length * t
            mid_x = x0 + sway * math.sin(ph + t * 3.2) + (x0 - 256) * .55 * t
            w = (13 - 10.5 * t) * (1 + .26 * math.sin(t * 20 + ph))
            left.append((mid_x - w, y))
            right.append((mid_x + w, y))
        return smooth(left + right[::-1], closed=True), smooth([((a[0] + c[0]) / 2, a[1]) for a, c in zip(left, right)])
    for x0, sway, length, ph in ((214, 10, 160, 4.1), (298, 10, 168, 5.4), (234, 13, 196, 0.3), (280, 13, 204, 2.2)):
        d, spine = ribbon(x0, sway, length, ph)
        b.append(f'<path d="{d}" fill="url(#{p}arm)" opacity=".8"/>')
        b.append(f'<path d="{spine}" stroke="#FFE4E6" stroke-width="1.6" stroke-linecap="round" opacity=".35"/>')

    # bell
    b.append(f'<path d="{bell}" fill="{CYAN}" opacity=".55" filter="url(#{p}b24)"/>')
    b.append(f'<path d="{bell}" fill="url(#{p}bell)"/>')
    b.append(f'<g clip-path="url(#{p}bellc)">')
    # depth: the far wall of the bell, darker toward the rim, and the glow under it
    b.append(f'<path d="{bell}" stroke="#312E81" stroke-width="44" opacity=".34" filter="url(#{p}b12)"/>')
    b.append(f'<ellipse cx="256" cy="268" rx="160" ry="62" fill="url(#{p}sub)"/>')
    # radial canals, fanning from the crown down to the rim
    for k in (-5, -4, -3, 3, 4, 5):
        x_end = 256 + k * 29
        b.append(f'<path d="M{f(256+k*9)} 136 Q{f(256+k*24)} 170 {f(x_end)} {f(rim_y(x_end)+10)}" stroke="#ECFEFF" stroke-width="1.6" stroke-linecap="round" opacity=".2"/>')
    # the Phosphor mark on the crown, where a moon jelly carries its four rings
    phi = 'translate(256 110) scale(.15) translate(-512 -512)'
    arcs = "".join(f'<path d="{d}"/>' for d in PHI_ARCS + [PHI_SPINDLE])
    b.append(f'<g transform="{phi}" fill="{ROSE}" filter="url(#{p}phib)">{arcs}</g>')
    b.append(f'<g transform="{phi}" fill="url(#{p}phi)">{arcs}</g>')
    # specular sheen
    b.append(f'<path d="M132 190 C140 132 184 92 236 80" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity=".3" filter="url(#{p}b6)"/>')
    b.append(f'<path d="M140 176 C150 134 184 104 222 94" stroke="#fff" stroke-width="3.4" stroke-linecap="round" opacity=".7"/>')
    b.append(f'<ellipse cx="368" cy="130" rx="6" ry="13" fill="#fff" opacity=".5" transform="rotate(-40 368 130)"/>')
    b.append('</g>')
    b.append(f'<path d="{dome}" stroke="#CFFAFE" stroke-width="2.4" opacity=".6"/>')
    b.append(f'<path d="{hem}" stroke="#A5F3FC" stroke-width="2.6" opacity=".8"/>')
    # rim lights
    for x, y in pts:
        b.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="11" fill="{CYAN}" opacity=".65" filter="url(#{p}b6)"/>')
        b.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="3.8" fill="#ECFEFF"/>')
    # face
    b.append(blush(p, 200, 224, 14, 7, .6))
    b.append(blush(p, 312, 224, 14, 7, .6))
    b.append(eye(p, 1, 222, 195, 18, 24))
    b.append(eye(p, 2, 290, 195, 18, 24))
    b.append(smile(256, 223, 9))
    # drifting motes
    for x, y, r in ((70, 300, 4.4), (442, 306, 3.4), (58, 150, 3), (456, 176, 3.8), (108, 420, 3), (412, 428, 3.4)):
        b.append(f'<circle cx="{x}" cy="{y}" r="{r}" stroke="#A5F3FC" stroke-width="1.4" opacity=".55"/>')
        b.append(f'<circle cx="{f(x-r*.3)}" cy="{f(y-r*.3)}" r="{f(r*.3)}" fill="#fff" opacity=".7"/>')
    b.append(star(100, 100, 9, "#CFFAFE", .6))
    b.append(star(424, 92, 6, "#E9D5FF", .5))
    return ("Nocti", "A bioluminescent jellyfish with the Phosphor mark glowing on the crown of its bell, trailing frilled rose arms and fine tentacles.",
            defs, "".join(b))


# ── Output ───────────────────────────────────────────────────────────────────

def mark(title, desc, defs, body, scale=1.0):
    """The mascot alone on a transparent 512 canvas, scaled about its centre."""
    if scale != 1.0:
        body = f'<g transform="translate({f(256 * (1 - scale))} {f(256 * (1 - scale))}) scale({scale})">{body}</g>'
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<!-- {title}: a Phosphor mascot. Generated by scripts/mascots.py. -->\n'
        '<svg width="512" height="512" viewBox="0 0 512 512" fill="none" '
        'xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">\n'
        f'  <title id="title">{title}</title>\n'
        f'  <desc id="desc">{desc}</desc>\n'
        f'  <defs>{defs}</defs>\n'
        f'  {body}\n'
        '</svg>\n'
    )


RING = 234  # inner radius of the gradient ring, the same proportion as svg/circle


def avatar(title, defs, body, fit):
    """Discord avatar: the mascot inside the suite's gradient ring, on the navy
    panel of the framed icons. fit is (x, y, scale), placing the 512 canvas so
    the face stays large after the round crop."""
    x, y, k = fit
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<!-- {title}: a Phosphor mascot avatar. Generated by scripts/mascots.py. -->\n'
        '<svg width="1024" height="1024" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg" '
        'role="img" aria-labelledby="title desc">\n'
        f'  <title id="title">{title}</title>\n'
        f'  <desc id="desc">{title}, the Phosphor mascot, inside a gradient ring on deep navy.</desc>\n'
        f'  <defs>{defs}\n'
        '<linearGradient id="av-ring" x1="60" y1="60" x2="452" y2="452" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset=".45" stop-color="{BLUE}"/>'
        f'<stop offset=".75" stop-color="{PURPLE}"/><stop offset="1" stop-color="{ROSE}"/></linearGradient>'
        f'<radialGradient id="av-bg" cx=".42" cy=".36" r=".8"><stop offset="0" stop-color="#132450"/>'
        f'<stop offset=".5" stop-color="{NAVY}"/><stop offset="1" stop-color="{VOID}"/></radialGradient>'
        f'<clipPath id="av-c"><circle cx="256" cy="256" r="{RING}"/></clipPath></defs>\n'
        '  <circle cx="256" cy="256" r="256" fill="url(#av-ring)"/>\n'
        f'  <circle cx="256" cy="256" r="{RING}" fill="url(#av-bg)"/>\n'
        f'  <g clip-path="url(#av-c)"><g transform="translate({x} {y}) scale({k})">{body}</g></g>\n'
        f'  <circle cx="256" cy="256" r="{RING - 1}" stroke="{VOID}" stroke-width="2" opacity=".55"/>\n'
        '</svg>\n'
    )


# Per mascot framing inside the ring: x, y, scale.
FIT = {"glim": (14, 32, .93), "wisp": (2.6, -4, .99), "nocti": (-12.8, 16, 1.05)}

# Per mascot scale of the standalone drawing, so its glow clears the canvas edge.
MARK_SCALE = {"glim": .9}


def main():
    (OUT / "avatar").mkdir(parents=True, exist_ok=True)
    for name, fn in (("glim", glim), ("wisp", wisp), ("nocti", nocti)):
        title, desc, defs, body = fn()
        (OUT / f"{name}.svg").write_text(mark(title, desc, defs, body, MARK_SCALE.get(name, 1.0)))
        (OUT / "avatar" / f"{name}.svg").write_text(avatar(title, defs, body, FIT[name]))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
