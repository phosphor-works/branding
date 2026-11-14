#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 fuddlesworth
# SPDX-License-Identifier: CC-BY-SA-4.0
"""Generate the Phosphor mascots: Glim, Wisp and Nocti.

Each mascot is drawn as a standalone mark on a transparent background
(svg/mascot/<name>.svg) and as a Discord style avatar on a deep navy disc
(svg/mascot/avatar/<name>.svg). The tentacles, ribbons and rim lights are
computed, so edit this script rather than the SVGs, then run:

    python3 scripts/mascots.py
"""

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "svg" / "mascot"
(OUT / "avatar").mkdir(parents=True, exist_ok=True)

CYAN, BLUE, PURPLE, ROSE = "#22D3EE", "#3B82F6", "#A855F7", "#F43F5E"
NAVY, ABYSS, VOID = "#0B1730", "#070F22", "#050916"

# The four crescents of the Phosphor mark, from svg/mark/dark/phosphor.svg.
PHI_ARCS = [
    "M583 358L598 362L612 367L626 374L639 381L652 389L664 398L676 408L686 419L695 431L703 444L709 458L714 472L716 487L714 502L702 516L689 504L685 492L681 480L678 469L674 457L669 446L664 434L658 423L650 412L641 401L632 391L621 382L609 373L597 365L583 358Z",
    "M696 553L706 571L704 588L698 603L690 618L680 631L668 643L654 653L640 661L624 669L608 674L592 678L575 681L559 682L541 676L555 665L569 658L582 651L594 643L605 635L616 626L626 617L635 607L643 598L652 589L660 579L668 570L678 560L696 553Z",
    "M483 676L465 682L449 681L432 678L416 674L400 669L384 661L370 653L356 643L344 631L334 618L326 603L320 588L318 571L328 553L346 560L356 570L364 579L372 589L381 598L389 607L398 617L408 626L419 635L430 643L442 651L455 658L469 665L483 676Z",
    "M322 516L310 502L308 487L310 472L315 458L321 444L329 431L338 419L348 408L360 398L372 389L385 381L398 374L412 367L426 362L441 358L427 365L415 373L403 382L392 391L383 401L374 412L366 423L360 434L355 446L350 457L346 469L343 480L339 492L335 504L322 516Z",
]
PHI_SPINDLE = "M512 206 C540 372 540 652 512 818 C484 652 484 372 512 206 Z"


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def blur(id_, sd):
    return (f'<filter id="{id_}" x="-60%" y="-60%" width="220%" height="220%" '
            f'color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{sd}"/></filter>')


def star(cx, cy, r, fill, op=1.0):
    """Four point sparkle."""
    k = r * 0.22
    d = (f"M{f(cx)} {f(cy-r)} Q{f(cx+k)} {f(cy-k)} {f(cx+r)} {f(cy)} "
         f"Q{f(cx+k)} {f(cy+k)} {f(cx)} {f(cy+r)} Q{f(cx-k)} {f(cy+k)} {f(cx-r)} {f(cy)} "
         f"Q{f(cx-k)} {f(cy-k)} {f(cx)} {f(cy-r)}Z")
    return f'<path d="{d}" fill="{fill}" opacity="{op}"/>'


def eye(p, n, cx, cy, rx, ry, look=(0, 0), dark=False):
    """A simple stylised eye: a dark oval, two catchlights and a faint glow
    reflected along its lower edge. dark=True adds a soft halo so the eye
    holds against a bright surface. look is kept for call compatibility."""
    rx, ry = rx * .78, ry * .92
    cid = f"{p}eye{n}"
    s = [f'<defs><clipPath id="{cid}"><ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}"/></clipPath></defs>']
    if dark:
        s.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx+5)}" ry="{f(ry+5)}" fill="#ECFEFF" opacity=".6" filter="url(#{p}b3)"/>')
    s.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="url(#{p}pupil)"/>')
    s.append(f'<g clip-path="url(#{cid})">'
             f'<ellipse cx="{f(cx)}" cy="{f(cy+ry*1.05)}" rx="{f(rx*.9)}" ry="{f(ry*.5)}" fill="{CYAN}" opacity=".55" filter="url(#{p}b3)"/></g>')
    s.append(f'<ellipse cx="{f(cx-rx*.28)}" cy="{f(cy-ry*.36)}" rx="{f(rx*.34)}" ry="{f(ry*.26)}" fill="#fff"/>')
    s.append(f'<circle cx="{f(cx+rx*.3)}" cy="{f(cy+ry*.18)}" r="{f(rx*.13)}" fill="#fff" opacity=".8"/>')
    return "".join(s)


def eye_defs(p):
    return (
        f'<radialGradient id="{p}pupil" cx=".45" cy=".35" r=".75"><stop offset="0" stop-color="#1E2A55"/>'
        f'<stop offset="1" stop-color="{VOID}"/></radialGradient>'
        + blur(f"{p}b3", 3)
    )


def svg(title, desc, body, defs):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<!-- {title}: a Phosphor mascot. -->\n'
        '<svg width="512" height="512" viewBox="0 0 512 512" fill="none" '
        'xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">\n'
        f'  <title id="title">{title}</title>\n'
        f'  <desc id="desc">{desc}</desc>\n'
        f'  <defs>{defs}</defs>\n'
        f'  {body}\n'
        '</svg>\n'
    )


# ── Glim, the firefly ────────────────────────────────────────────────────────

def glim():
    p = "gl-"
    # Body: head, thorax and abdomen share one gradient and one clip, so they
    # read as a single lit form rather than stacked parts.
    head = '<ellipse cx="184" cy="210" rx="82" ry="76"/>'
    thorax = '<ellipse cx="252" cy="268" rx="56" ry="48" transform="rotate(38 252 268)"/>'
    abdomen = '<ellipse cx="320" cy="338" rx="104" ry="74" transform="rotate(38 320 338)"/>'
    parts = head + thorax + abdomen
    far_wing = ("M262 230 C262 160 300 92 352 70 C392 54 412 84 396 124 "
                "C378 170 320 212 274 238Z")
    near_wing = ("M276 246 C312 176 380 128 438 124 C478 122 488 156 462 188 "
                 "C428 228 352 254 290 260Z")
    far_ely = ("M246 238 C262 176 310 140 356 136 C386 134 396 156 380 178 "
               "C350 214 300 236 256 250Z")
    near_ely = ("M250 256 C298 208 366 192 416 208 C450 220 452 262 418 278 "
                "C366 300 300 296 258 278Z")
    defs = eye_defs(p) + blur(f"{p}b6", 6) + blur(f"{p}b12", 12) + blur(f"{p}b24", 24) + f"""
<radialGradient id="{p}halo" cx="396" cy="404" r="240" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{CYAN}" stop-opacity=".6"/><stop offset=".35" stop-color="{CYAN}" stop-opacity=".2"/>
  <stop offset=".7" stop-color="{BLUE}" stop-opacity=".07"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}body" x1="120" y1="150" x2="420" y2="430" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#7AA7FA"/><stop offset=".22" stop-color="#4F63E6"/><stop offset=".36" stop-color="#4338CA"/>
  <stop offset=".5" stop-color="#5B21B6"/><stop offset=".7" stop-color="#7E22CE"/>
  <stop offset=".82" stop-color="#5EC7F2"/><stop offset="1" stop-color="#ECFEFF"/></linearGradient>
<radialGradient id="{p}lamp" cx="398" cy="404" r="96" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#FFFFFF"/><stop offset=".3" stop-color="#CFFAFE"/>
  <stop offset=".62" stop-color="{CYAN}" stop-opacity=".9"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}ely" x1="340" y1="200" x2="350" y2="296" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#8B5CF6"/><stop offset=".4" stop-color="#5B21B6"/><stop offset="1" stop-color="#2E1065"/></linearGradient>
<linearGradient id="{p}elyF" x1="250" y1="140" x2="390" y2="250" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#4C1D95"/><stop offset="1" stop-color="#1E1B4B"/></linearGradient>
<linearGradient id="{p}wing" x1="290" y1="260" x2="460" y2="120" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#A5F3FC" stop-opacity=".6"/><stop offset=".5" stop-color="#93C5FD" stop-opacity=".26"/>
  <stop offset="1" stop-color="#C4B5FD" stop-opacity=".14"/></linearGradient>
<linearGradient id="{p}wingF" x1="270" y1="236" x2="380" y2="60" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#67E8F9" stop-opacity=".34"/><stop offset="1" stop-color="#A78BFA" stop-opacity=".1"/></linearGradient>
<linearGradient id="{p}ant" x1="0" y1="1" x2="1" y2="0">
  <stop offset="0" stop-color="#312E81"/><stop offset="1" stop-color="{PURPLE}"/></linearGradient>
<radialGradient id="{p}rim" cx="398" cy="404" r="130" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#ECFEFF" stop-opacity=".9"/><stop offset=".6" stop-color="#A5F3FC" stop-opacity=".6"/>
  <stop offset="1" stop-color="#A5F3FC" stop-opacity="0"/></radialGradient>
<clipPath id="{p}bodyc">{parts}</clipPath>
<clipPath id="{p}nec"><path d="{near_ely}"/></clipPath>
"""
    b = []
    b.append(f'<circle cx="396" cy="404" r="240" fill="url(#{p}halo)"/>')

    # light trail
    for x, y, r, o in ((452, 460, 6, .8), (478, 482, 4.4, .6), (500, 500, 3.2, .4), (424, 482, 3, .5), (456, 504, 2.2, .3)):
        b.append(f'<circle cx="{x}" cy="{y}" r="{f(r*2.6)}" fill="{CYAN}" opacity="{f(o*.4)}" filter="url(#{p}b6)"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="{f(r)}" fill="#ECFEFF" opacity="{f(o)}"/>')

    # far membrane wing and far wing cover, behind the body
    b.append(f'<path d="{far_wing}" fill="url(#{p}wingF)" stroke="#C7D2FE" stroke-width="1.4" stroke-opacity=".3"/>')
    for d in ("M268 226 C290 170 318 118 360 84", "M272 232 C306 196 340 162 384 120"):
        b.append(f'<path d="{d}" stroke="#E0E7FF" stroke-width="1.1" stroke-opacity=".2" stroke-linecap="round"/>')
    b.append(f'<path d="{far_ely}" fill="url(#{p}elyF)"/>')
    b.append(f'<path d="M280 192 C304 162 334 142 362 140" stroke="{ROSE}" stroke-width="1.6" opacity=".45" stroke-linecap="round"/>')

    # legs, tucked under the thorax
    for d in ("M226 300 C214 320 206 330 194 334", "M256 320 C252 342 246 354 234 362", "M290 344 C292 366 288 378 278 388"):
        b.append(f'<path d="{d}" stroke="#1E1B4B" stroke-width="6" stroke-linecap="round"/>')
        b.append(f'<path d="{d}" stroke="#818CF8" stroke-width="1.4" stroke-linecap="round" opacity=".45"/>')

    # antennae
    for shape, tip, col in (("M156 146 C136 106 120 80 88 66 C128 78 150 102 170 140Z", (88, 66), CYAN),
                            ("M196 136 C196 96 206 66 232 42 C212 66 208 96 212 136Z", (232, 42), ROSE)):
        b.append(f'<path d="{shape}" fill="url(#{p}ant)"/>')
        x, y = tip
        b.append(f'<circle cx="{x}" cy="{y}" r="16" fill="{col}" opacity=".55" filter="url(#{p}b6)"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="{col}"/>')
        b.append(f'<circle cx="{x-1.5}" cy="{y-1.5}" r="2.2" fill="#fff"/>')

    # body
    b.append(f'<ellipse cx="392" cy="400" rx="70" ry="58" fill="{CYAN}" opacity=".85" filter="url(#{p}b24)"/>')
    b.append(f'<g fill="url(#{p}body)">{parts}</g>')
    b.append(f'<g clip-path="url(#{p}bodyc)">')
    b.append(f'<ellipse cx="238" cy="262" rx="58" ry="46" fill="#1E1B4B" opacity=".5" filter="url(#{p}b24)"/>')
    b.append(f'<path d="M112 230 C122 262 148 282 180 286" stroke="{CYAN}" stroke-width="8" stroke-linecap="round" opacity=".28" filter="url(#{p}b6)"/>')
    # key light top left, shade along the underside
    b.append(f'<ellipse cx="158" cy="168" rx="52" ry="36" fill="#fff" opacity=".24" filter="url(#{p}b24)"/>')
    b.append(f'<path d="M112 240 C150 300 214 300 262 330 C300 356 330 392 366 420" stroke="{VOID}" stroke-width="40" stroke-linecap="round" opacity=".34" filter="url(#{p}b24)"/>')
    # abdominal segments under the wing covers, fading toward the lantern
    for i, (x, y) in enumerate(((304, 334), (330, 356), (354, 378))):
        o = .34 - i * .08
        b.append(f'<path d="M{x-52} {y+44} Q{x-6} {y+16} {x+30} {y-40}" stroke="#1E1B4B" stroke-width="3" opacity="{f(o)}" stroke-linecap="round"/>')
        b.append(f'<path d="M{x-46} {y+46} Q{x} {y+18} {x+36} {y-38}" stroke="{ROSE}" stroke-width="1.4" opacity="{f(o)}" stroke-linecap="round"/>')
    b.append(f'<circle cx="398" cy="404" r="96" fill="url(#{p}lamp)"/>')
    # where the head meets the thorax: a soft occlusion shadow, and the rose
    # sheen of a firefly's pronotum on the thorax
    b.append(f'<path d="M244 196 C266 230 262 270 226 290" stroke="{VOID}" stroke-width="22" stroke-linecap="round" opacity=".45" filter="url(#{p}b12)"/>')
    b.append(f'<ellipse cx="262" cy="250" rx="34" ry="22" transform="rotate(38 262 250)" fill="{ROSE}" opacity=".45" filter="url(#{p}b12)"/>')
    b.append('</g>')
    # rim light from the lantern along the lower edge
    b.append(f'<ellipse cx="320" cy="338" rx="104" ry="74" transform="rotate(38 320 338)" stroke="url(#{p}rim)" stroke-width="2.6"/>')
    b.append(f'<path d="M110 186 C120 156 146 136 176 134" stroke="#BFDBFE" stroke-width="2.4" stroke-linecap="round" opacity=".6"/>')

    # near membrane wing, lit from below by the lantern
    b.append(f'<path d="{near_wing}" fill="url(#{p}wing)"/>')
    for d in ("M284 252 C330 206 380 168 440 140", "M290 256 C340 236 396 208 456 170", "M380 170 C392 154 406 142 424 132"):
        b.append(f'<path d="{d}" stroke="#ECFEFF" stroke-width="1.2" stroke-opacity=".3" stroke-linecap="round"/>')
    b.append(f'<path d="{near_wing}" stroke="#E0F2FE" stroke-width="1.6" stroke-opacity=".5"/>')
    b.append(f'<path d="M290 260 C352 254 428 228 462 188" stroke="#A5F3FC" stroke-width="2.4" stroke-linecap="round" opacity=".6"/>')

    # near wing cover: glossy, rose edged, lifted open
    b.append(f'<path d="{near_ely}" fill="url(#{p}ely)"/>')
    b.append(f'<g clip-path="url(#{p}nec)">'
             f'<path d="M276 246 C324 220 374 212 420 224" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity=".28" filter="url(#{p}b3)"/>'
             f'<path d="M262 280 C320 300 384 294 428 270" stroke="{CYAN}" stroke-width="10" opacity=".4" filter="url(#{p}b6)"/>'
             f'<ellipse cx="254" cy="262" rx="34" ry="30" fill="#1E1B4B" opacity=".7" filter="url(#{p}b12)"/></g>')
    b.append(f'<path d="M262 244 C304 206 366 194 416 208 C450 220 452 262 418 278" stroke="{ROSE}" stroke-width="2.4" stroke-opacity=".75" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(f'<path d="M290 238 C334 218 382 212 414 222" stroke="#F5D0FE" stroke-width="2" stroke-linecap="round" opacity=".55"/>')

    # face
    b.append(f'<ellipse cx="132" cy="240" rx="13" ry="7" fill="{ROSE}" opacity=".4" filter="url(#{p}b3)"/>')
    b.append(f'<ellipse cx="216" cy="244" rx="13" ry="7" fill="{ROSE}" opacity=".4" filter="url(#{p}b3)"/>')
    b.append(eye(p, 1, 150, 214, 22, 26))
    b.append(eye(p, 2, 200, 216, 22, 26))

    b.append(star(78, 330, 9, "#CFFAFE", .5))
    b.append(star(470, 72, 7, "#E9D5FF", .45))
    return svg("Glim", "A glowing firefly in flight: rose edged wing covers lifted open over translucent wings, and a bright cyan lantern at its tail.",
               f'<g transform="translate(-4 4)">{"".join(b)}</g>', defs)


# ── Wisp, the will-o'-the-wisp ───────────────────────────────────────────────

def wisp():
    p = "wi-"
    flame = ("M256 424 C186 424 142 374 146 312 C150 254 188 222 196 168 C210 192 222 204 232 204 "
             "C224 146 244 100 270 46 C282 104 318 138 314 200 C328 190 338 168 340 136 "
             "C368 192 370 252 366 312 C362 378 322 424 256 424Z")
    defs = eye_defs(p) + blur(f"{p}b6", 6) + blur(f"{p}b12", 12) + blur(f"{p}b30", 30) + f"""
<radialGradient id="{p}halo" cx="256" cy="300" r="230" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{PURPLE}" stop-opacity=".5"/><stop offset=".5" stop-color="{BLUE}" stop-opacity=".16"/>
  <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}l1" x1="0" y1="40" x2="0" y2="430" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{ROSE}" stop-opacity=".2"/><stop offset=".35" stop-color="{ROSE}" stop-opacity=".85"/>
  <stop offset="1" stop-color="{PURPLE}"/></linearGradient>
<linearGradient id="{p}l2" x1="0" y1="40" x2="0" y2="430" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{PURPLE}" stop-opacity=".3"/><stop offset=".5" stop-color="{PURPLE}"/>
  <stop offset="1" stop-color="{BLUE}"/></linearGradient>
<linearGradient id="{p}l3" x1="0" y1="40" x2="0" y2="430" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{BLUE}" stop-opacity=".4"/><stop offset=".55" stop-color="{BLUE}"/>
  <stop offset="1" stop-color="{CYAN}"/></linearGradient>
<radialGradient id="{p}core" cx="256" cy="340" r="110" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#F0FDFF"/><stop offset=".45" stop-color="#A5F3FC"/>
  <stop offset="1" stop-color="{CYAN}" stop-opacity=".0"/></radialGradient>
<linearGradient id="{p}tail" x1="300" y1="400" x2="150" y2="480" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{PURPLE}" stop-opacity=".9"/><stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></linearGradient>
<linearGradient id="{p}curl" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FDA4AF" stop-opacity="0"/><stop offset="1" stop-color="#FDA4AF" stop-opacity=".9"/></linearGradient>
"""

    def scaled(k, cx=256, cy=330):
        return f'transform="translate({cx} {cy}) scale({k}) translate({-cx} {-cy})"'

    b = ['<g transform="translate(0 18) scale(.96) translate(10 0)">']
    b.append(f'<circle cx="256" cy="300" r="230" fill="url(#{p}halo)"/>')
    # trailing tail curling off to the lower left
    b.append(f'<path d="M318 400 C306 452 250 482 200 470 C160 460 150 424 178 414 C198 408 212 424 202 438 '
             f'C196 446 184 444 182 438 C192 452 222 452 236 436 C256 414 270 404 300 380Z" fill="url(#{p}tail)"/>')
    # bloom
    b.append(f'<path d="{flame}" fill="{PURPLE}" opacity=".7" filter="url(#{p}b30)"/>')
    # layered flame
    b.append(f'<path d="{flame}" fill="url(#{p}l1)"/>')
    b.append(f'<path d="{flame}" fill="url(#{p}l2)" {scaled(.84)}/>')
    b.append(f'<path d="{flame}" fill="url(#{p}l3)" {scaled(.66, 256, 350)}/>')
    b.append(f'<ellipse cx="256" cy="340" rx="110" ry="96" fill="url(#{p}core)"/>')
    # inner licks of light
    b.append(f'<path d="M226 300 C214 262 226 228 246 204 C244 240 252 262 262 280" stroke="#ECFEFF" stroke-width="4" stroke-linecap="round" opacity=".45" filter="url(#{p}b3)"/>')
    b.append(f'<path d="M300 262 C306 236 304 214 296 196" stroke="#FCE7F3" stroke-width="3" stroke-linecap="round" opacity=".45"/>')
    # rim light along the outer edge
    b.append(f'<path d="M146 312 C150 254 188 222 196 168" stroke="#FDA4AF" stroke-width="2.4" stroke-linecap="round" opacity=".65"/>')
    b.append(f'<path d="M340 136 C368 192 370 252 366 312" stroke="#FDA4AF" stroke-width="2.4" stroke-linecap="round" opacity=".5"/>')
    # wisps rising from the tongues
    for d, w in (("M270 50 C262 26 282 14 290 -4", 5), ("M196 170 C184 146 196 128 188 104", 4), ("M340 138 C350 116 340 98 350 80", 4)):
        b.append(f'<path d="{d}" stroke="url(#{p}curl)" stroke-width="{w*2.4}" stroke-linecap="round" filter="url(#{p}b6)"/>')
        b.append(f'<path d="{d}" stroke="url(#{p}curl)" stroke-width="{w*.5}" stroke-linecap="round"/>')
    # embers
    embers = [(206, 96, 4, ROSE), (318, 78, 3.2, PURPLE), (372, 112, 2.6, ROSE), (150, 140, 3, PURPLE),
              (296, 30, 2.4, "#FDA4AF"), (394, 200, 2.4, CYAN), (118, 230, 2.2, CYAN), (236, 40, 2, "#E9D5FF")]
    for x, y, r, c in embers:
        b.append(f'<circle cx="{x}" cy="{y}" r="{f(r*3)}" fill="{c}" opacity=".45" filter="url(#{p}b6)"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="{f(r)}" fill="{c}"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="{f(r*.45)}" fill="#fff" opacity=".9"/>')
    b.append(star(112, 330, 8, "#CFFAFE", .5))
    b.append(star(410, 360, 10, "#FCE7F3", .5))
    # face
    b.append(eye(p, 1, 224, 334, 20, 25, look=(1.5, 2.5), dark=True))
    b.append(eye(p, 2, 290, 334, 20, 25, look=(1.5, 2.5), dark=True))
    b.append(f'<ellipse cx="200" cy="370" rx="12" ry="6" fill="{ROSE}" opacity=".45" filter="url(#{p}b3)"/>')
    b.append(f'<ellipse cx="314" cy="370" rx="12" ry="6" fill="{ROSE}" opacity=".45" filter="url(#{p}b3)"/>')
    b.append('</g>')
    return svg("Wisp", "A will o the wisp: a layered rose, purple, blue and cyan flame spirit with a curling tail and drifting embers.",
               "".join(b), defs)


# ── Nocti, the jellyfish ─────────────────────────────────────────────────────

def nocti():
    p = "no-"
    L, R, TOP = 106, 406, 64

    def rim_y(x):
        u = (x - 256) / ((R - L) / 2)
        return 226 + 30 * (1 - u * u)

    n = 10
    xs = [L + (R - L) * i / n for i in range(n + 1)]
    pts = [(x, rim_y(x)) for x in xs]
    scal = f"M{f(R)} {f(rim_y(R))} "
    for i in range(n, 0, -1):
        x0, y0 = pts[i]
        x1, y1 = pts[i - 1]
        scal += f"Q{f((x0+x1)/2)} {f((y0+y1)/2+18)} {f(x1)} {f(y1)} "
    bell = (f"M{L} {f(rim_y(L))} C{L-6} 150 172 {TOP} 256 {TOP} C340 {TOP} {R+6} 150 {R} {f(rim_y(R))} "
            + scal.replace(f"M{f(R)} {f(rim_y(R))} ", "") + "Z")

    defs = eye_defs(p) + blur(f"{p}b6", 6) + blur(f"{p}b12", 12) + blur(f"{p}b30", 30) + f"""
<radialGradient id="{p}halo" cx="256" cy="210" r="240" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{CYAN}" stop-opacity=".45"/><stop offset=".5" stop-color="{BLUE}" stop-opacity=".16"/>
  <stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
<radialGradient id="{p}bell" cx="256" cy="96" r="230" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#A5F3FC" stop-opacity=".75"/><stop offset=".35" stop-color="{CYAN}" stop-opacity=".55"/>
  <stop offset=".7" stop-color="{BLUE}" stop-opacity=".55"/><stop offset="1" stop-color="{PURPLE}" stop-opacity=".85"/></radialGradient>
<radialGradient id="{p}sub" cx="256" cy="260" r="150" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#ECFEFF" stop-opacity=".5"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<linearGradient id="{p}tent" x1="0" y1="230" x2="0" y2="500" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#A5F3FC" stop-opacity=".9"/><stop offset=".45" stop-color="{PURPLE}" stop-opacity=".6"/>
  <stop offset="1" stop-color="{ROSE}" stop-opacity="0"/></linearGradient>
<linearGradient id="{p}arm" x1="0" y1="250" x2="0" y2="480" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{ROSE}" stop-opacity=".95"/><stop offset=".6" stop-color="{PURPLE}" stop-opacity=".6"/>
  <stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>
<linearGradient id="{p}phi" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#FBCFE8"/><stop offset="1" stop-color="{ROSE}"/></linearGradient>
<clipPath id="{p}bellc"><path d="{bell}"/></clipPath>
"""
    b = []
    b.append(f'<circle cx="256" cy="210" r="240" fill="url(#{p}halo)"/>')

    # tentacles from each scallop point
    tent = []
    for i, (x, y) in enumerate(pts):
        if i in (0, n):
            continue
        length = 200 + 50 * math.sin(i * 1.7)
        amp = 10 + 4 * math.cos(i)
        ph = i * .9
        d = f"M{f(x)} {f(y+6)}"
        steps = 6
        for s in range(1, steps + 1):
            t = s / steps
            yy = y + 6 + length * t
            xx = x + (x - 256) * .18 * t + amp * math.sin(ph + t * 5)
            cx_ = x + (x - 256) * .18 * (t - .5 / steps) + amp * math.sin(ph + (t - .5 / steps) * 5) * 1.6
            cy_ = yy - length / steps / 2
            d += f" Q{f(cx_)} {f(cy_)} {f(xx)} {f(yy)}"
        w = 3.2 if i % 2 else 2.2
        tent.append(f'<path d="{d}" stroke="url(#{p}tent)" stroke-width="{w}" stroke-linecap="round"/>')
    b.append("".join(tent))

    # oral arms: four frilled ribbons
    def ribbon(x0, sway, length, ph):
        left, right = [], []
        N = 40
        for k in range(N + 1):
            t = k / N
            y = 250 + length * t
            cx_ = x0 + sway * math.sin(ph + t * 3.2) + (x0 - 256) * .6 * t
            w = (11 - 8.5 * t) * (1 + .28 * math.sin(t * 38 + ph))
            left.append((cx_ - w, y))
            right.append((cx_ + w, y))
        poly = left + right[::-1]
        return "M" + " L".join(f"{f(a)} {f(c)}" for a, c in poly) + "Z"
    for x0, sway, length, ph in ((232, 14, 210, 0.3), (280, 14, 220, 2.2), (214, 10, 170, 4.1), (298, 10, 180, 5.4)):
        d = ribbon(x0, sway, length, ph)
        b.append(f'<path d="{d}" fill="url(#{p}arm)" opacity=".7"/>')
        b.append(f'<path d="{d}" stroke="#FBCFE8" stroke-width="1" stroke-opacity=".35"/>')

    # bell
    b.append(f'<path d="{bell}" fill="{CYAN}" opacity=".55" filter="url(#{p}b30)"/>')
    b.append(f'<path d="{bell}" fill="url(#{p}bell)"/>')
    b.append(f'<g clip-path="url(#{p}bellc)">')
    # subumbrella glow
    b.append(f'<ellipse cx="256" cy="262" rx="150" ry="70" fill="url(#{p}sub)"/>')
    # radial canals
    for k in range(-5, 6):
        x_end = 256 + k * 28
        b.append(f'<path d="M256 {TOP+20} Q{f(256+k*20)} 150 {f(x_end)} {f(rim_y(x_end)+10)}" stroke="#ECFEFF" stroke-width="1.4" opacity=".22"/>')
    # the Phosphor crescents, glowing inside the bell like a moon jelly's four rings
    phi = f'translate(256 170) scale(.5) translate(-512 -512)'
    arcs = "".join(f'<path d="{d}"/>' for d in PHI_ARCS)
    b.append(f'<g transform="{phi}" fill="{ROSE}" opacity=".5" filter="url(#{p}b12)">{arcs}</g>')
    b.append(f'<g transform="{phi}" fill="url(#{p}phi)" opacity=".38">{arcs}</g>')
    # specular sheen
    b.append(f'<path d="M150 178 C160 124 202 92 250 86" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".35" filter="url(#{p}b3)"/>')
    b.append(f'<path d="M156 170 C166 128 200 102 238 96" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".6"/>')
    b.append(f'<ellipse cx="350" cy="120" rx="10" ry="16" fill="#fff" opacity=".25" transform="rotate(35 350 120)" filter="url(#{p}b3)"/>')
    b.append('</g>')
    b.append(f'<path d="M{L} {f(rim_y(L))} C{L-6} 150 172 {TOP} 256 {TOP} C340 {TOP} {R+6} 150 {R} {f(rim_y(R))}" stroke="#CFFAFE" stroke-width="2.2" opacity=".55"/>')
    b.append(f'<path d="{scal}" stroke="#A5F3FC" stroke-width="2.4" opacity=".7"/>')
    # rim lights
    for x, y in pts:
        b.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="10" fill="{CYAN}" opacity=".6" filter="url(#{p}b6)"/>')
        b.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="3.4" fill="#ECFEFF"/>')
    # face
    b.append(eye(p, 1, 228, 186, 19, 22, look=(1.5, 2.5)))
    b.append(eye(p, 2, 284, 186, 19, 22, look=(1.5, 2.5)))
    b.append(f'<ellipse cx="210" cy="214" rx="10" ry="6" fill="{ROSE}" opacity=".5" filter="url(#{p}b3)"/>')
    b.append(f'<ellipse cx="302" cy="214" rx="10" ry="6" fill="{ROSE}" opacity=".5" filter="url(#{p}b3)"/>')
    # drifting motes
    for x, y, r in ((80, 300, 4), (430, 300, 3), (66, 150, 2.6), (446, 190, 3.4), (120, 440, 2.6), (400, 440, 3)):
        b.append(f'<circle cx="{x}" cy="{y}" r="{r}" stroke="#A5F3FC" stroke-width="1.2" opacity=".5"/>')
        b.append(f'<circle cx="{x-r*.3}" cy="{y-r*.3}" r="{f(r*.3)}" fill="#fff" opacity=".6"/>')
    b.append(star(96, 92, 8, "#CFFAFE", .5))
    return svg("Nocti", "A bioluminescent jellyfish whose bell glows with the four crescents of the Phosphor mark, trailing frilled rose arms and fine tentacles.",
               "".join(b), defs)


def avatar(name, inner_svg, box=(40, 40, 432)):
    """Discord avatar: the mascot on a navy disc with room for the round crop."""
    import re
    inner = re.sub(r"^.*?<svg[^>]*>", "", inner_svg, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner)
    inner = re.sub(r'<title id="title">.*?</title>|<desc id="desc">.*?</desc>', "", inner, flags=re.S)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg width="1024" height="1024" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-labelledby="title desc">\n  <title id="title">{name}</title>\n'
        f'  <desc id="desc">{name}, the Phosphor mascot, on a deep navy disc.</desc>\n'
        '  <defs><clipPath id="av-c"><circle cx="256" cy="256" r="256"/></clipPath>'
        f'<radialGradient id="av-bg" cx=".5" cy=".42" r=".62"><stop offset="0" stop-color="#13234A"/>'
        f'<stop offset=".6" stop-color="{NAVY}"/><stop offset="1" stop-color="{VOID}"/></radialGradient></defs>\n'
        '  <g clip-path="url(#av-c)"><rect width="512" height="512" fill="url(#av-bg)"/>'
        f'<svg x="{box[0]}" y="{box[1]}" width="{box[2]}" height="{box[2]}" viewBox="0 0 512 512" overflow="visible">{inner}</svg></g>\n</svg>\n'
    )


# Per mascot framing inside the avatar disc: x, y, size.
BOX = {"glim": (44, 46, 424), "wisp": (40, 30, 440), "nocti": (-4, 22, 520)}

for name, fn in (("glim", glim), ("wisp", wisp), ("nocti", nocti)):
    s = fn()
    (OUT / f"{name}.svg").write_text(s)
    (OUT / "avatar" / f"{name}.svg").write_text(avatar(name.capitalize(), s, BOX[name]))
print(f"wrote {OUT.relative_to(ROOT)}")
