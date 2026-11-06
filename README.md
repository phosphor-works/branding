# Phosphor Branding

<!-- SPDX-FileCopyrightText: 2026 fuddlesworth -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

Canonical brand assets for the Phosphor library suite — the cyan /
blue / purple / rose gradient logos you see on
[phosphor-works.github.io](https://phosphor-works.github.io).

## Layout

```
svg/                                brand icons, by shape then theme
├── square/                         rounded-square framed icons (the sources)
│   ├── dark/                       tuned for dark surfaces
│   │   ├── phosphor.svg            umbrella brand mark (Φ)
│   │   ├── lambent.svg             Lambent shell
│   │   ├── afterglow.svg           Afterglow terminal
│   │   ├── facet.svg               Facet settings manager
│   │   ├── phosphor-shell.svg      PhosphorShell library mark
│   │   ├── phosphor-shader.svg     PhosphorShader app icon
│   │   ├── plasmazones.svg         PlasmaZones app icon
│   │   ├── plasmazones-editor.svg  PlasmaZones layout editor
│   │   └── plasmazones-settings.svg PlasmaZones settings
│   └── light/                      the same set for light surfaces
├── circle/                         round-framed variants, generated
│   ├── dark/                       one per square/dark icon
│   └── light/                      one per square/light icon
└── mark/                           badge-free marks, no frame
    ├── dark/                       gradient, for dark or transparent backgrounds
    │   ├── phosphor.svg
    │   ├── lambent.svg
    │   ├── afterglow.svg
    │   └── facet.svg
    ├── light/                      deep gradient, for light backgrounds
    └── mono/                       single colour via currentColor

scripts/
├── variants.py                     glow fix for the framed icons + circle
│                                   variant generator (see below)
├── check.py                        accessibility and prose check for the
│                                   framed icons, run by CI
└── build-release.sh                builds the release archive apps pin

cmake/
└── PhosphorBranding.cmake          phosphor_install_brand_icons(), shipped
                                    in the release archive

palette/                            canonical brand palette
├── phosphor.toml                   static palette in matugen role vocabulary
├── preview.html                    self-contained swatch + role-grid preview
├── preview.css                     shared preview styles
├── preview.dark.css                dark-theme tokens
└── preview.light.css               light-theme tokens

matugen/                            wallpaper-reactive palette template
├── config.example.toml             example matugen config wiring
└── templates/
    └── phosphor-palette.toml       Phosphor-structured palette regenerated
                                    from any wallpaper via Material You
```

All framed icons share the same outer frame: a 1024 × 1024 SVG with
`viewBox="96 96 832 832"`, a 4-stop cyan → blue → purple → rose
gradient border, a radial navy (dark) or brand-tinted pastel (light)
inner panel, and three soft accent glows.  The inner content
distinguishes them:

| Mark                   | Inner                                                        |
|------------------------|--------------------------------------------------------------|
| `phosphor`             | Φ — stylized flux symbol, umbrella brand.                    |
| `phosphor-shell`       | Three nested rounded rectangles — containment framework wrapping inner surfaces. |
| `plasmazones`          | Five stroked zones, the core tiling motif.                   |
| `plasmazones-editor`   | Zone motif wrapped in a canvas mark.                         |
| `plasmazones-settings` | Zone motif wrapped in a cog outline.                         |
| `phosphor-shader`      | Two input nodes wired into an output node.                   |
| `lambent`              | A curved L cradling a small flame.                           |
| `afterglow`            | Tapered A with a split elliptical crossbar, echoing the Phosphor mark. |
| `facet`                | A brilliant-cut gem seen from above: octagonal table, eight star facets. |

## Releases and installing icons

Apps don't copy icons. Each pins a branding release by version, URL and
SHA-256 and installs its icons from the archive. A tag `vX.Y.Z` publishes
`phosphor-branding-X.Y.Z.tar.gz`:

```
phosphor-branding-X.Y.Z/
├── hicolor/scalable/apps/<name>.svg       square/dark, for dark themes
├── hicolor/<N>x<N>/apps/<name>.png        16, 22, 24, 32, 48, 64, 128, 256, 512
├── hicolor-light/...                      the same from square/light
├── palette/  matugen/templates/
├── cmake/PhosphorBranding.cmake
├── LICENSE  VERSION
```

An app installs each icon under its own app ID, which is also its `.desktop`
id and AppStream id:

```cmake
include(${branding_SOURCE_DIR}/cmake/PhosphorBranding.cmake)
phosphor_install_brand_icons(org.phosphor_works.PlasmaZones plasmazones
                             org.phosphor_works.PlasmaZones.Editor plasmazones-editor)
```

`scripts/build-release.sh <version> <out dir>` builds the same archive
locally. It is reproducible for a given librsvg, and it runs
`scripts/check.py` first, which requires every framed icon to carry a
`<title>` and a `<desc>` in plain prose, since screen readers announce both.

## Circle variants and the glow fix

`svg/circle/{dark,light}/` holds a round-framed copy of every framed
icon (avatars, Discord, social cards).  The rounded square becomes a
circle with the same 36-unit border (outer radius 416, panel radius
380) and the artwork is unchanged.  These files are generated; edit
the square icon and re-run the script.

The accent glows are circles larger than the panel.  Browsers and
librsvg trim them with a `clipPath`, but QtSvg, which KDE uses to draw
icons, ignores `clipPath`, so the glows used to tint the transparent
corners outside the frame.  Each glow is now stored as its exact
intersection with the panel (square or circle), with its source circle
kept in `data-glow="cx cy r"`, so no renderer can draw it outside.

```sh
python3 scripts/variants.py           # fix glows in svg/square, regenerate svg/circle
python3 scripts/variants.py --check   # exit 1 if anything is out of date
```

Run it after adding or editing a framed icon.  A new icon can keep the
plain glow `<circle>` elements from the template; the script converts
them.

## Color tokens

| Role      | Dark     | Light     | Notes |
|-----------|----------|-----------|-------|
| Cyan      | `#22D3EE`| `#0EA5E9` | accent gradient stop 0 |
| Blue      | `#3B82F6`| `#3B82F6` | accent gradient stop 1 / primary |
| Purple    | `#A855F7`| `#7C3AED` | accent gradient stop 2 |
| Rose      | `#F43F5E`| `#E11D48` | accent gradient stop 3 |
| Surface   | `#0B1730`| `#E8EEFF` | inner-square fill on the topbar logo |

Full palette + Material You role map lives at
[phosphor-works.github.io/palette/](https://phosphor-works.github.io/palette/),
rendered from the canonical [`palette/phosphor.toml`](palette/phosphor.toml)
in this repo.

## Palette

`palette/phosphor.toml` is the canonical static brand palette: the
seven brand colors (`cyan`, `blue`, `purple`, `rose`, `navy`, `abyss`,
`void`) plus the full Material You role map for both dark and light
themes, written in [matugen](https://github.com/InioX/matugen)'s role
vocabulary so apps that already template against matugen output read
it directly.

Drop it in as a wallpaper-independent palette:

```sh
mkdir -p ~/.config/plasmazones
curl -L \
    https://raw.githubusercontent.com/phosphor-works/branding/main/palette/phosphor.toml \
    -o ~/.config/plasmazones/palette.toml
```

`palette/preview.html` is a self-contained swatch + role-grid preview
that opens directly in a browser; the three preview CSS files
(`preview.css`, `preview.dark.css`, `preview.light.css`) are the same
ones [phosphor-works.github.io/palette/](https://phosphor-works.github.io/palette/)
loads at runtime.

## Matugen template

`matugen/templates/phosphor-palette.toml` is the wallpaper-reactive
variant — the same role structure as the static palette, but seeded
from the dominant hues of a user wallpaper via
[matugen](https://github.com/InioX/matugen)'s Material You engine.
Install the template + wire it into matugen with the example config:

```sh
mkdir -p ~/.config/matugen/templates
curl -L \
    https://raw.githubusercontent.com/phosphor-works/branding/main/matugen/templates/phosphor-palette.toml \
    -o ~/.config/matugen/templates/phosphor-palette.toml
cat matugen/config.example.toml >> ~/.config/matugen/config.toml   # merge by hand
matugen image /path/to/wallpaper.png
```

…regenerates `~/.config/plasmazones/palette.toml` from the wallpaper.

## Usage

**Consuming from another repo:** add this repo as a git submodule.

```sh
git submodule add https://github.com/phosphor-works/branding.git submodules/branding
git submodule update --init --recursive
```

**One-off download:** `curl` the raw SVG:

```sh
curl -O https://raw.githubusercontent.com/phosphor-works/branding/main/svg/square/dark/phosphor.svg
curl -O https://raw.githubusercontent.com/phosphor-works/branding/main/svg/circle/dark/phosphor.svg
```

## License

Brand assets are **CC-BY-SA 4.0** — use them to refer to Phosphor, fork
them if you're making a derivative, share-alike if you redistribute a
modified version.  Code in consuming projects (phosphor-web, etc.) is
GPL-3.0-or-later; the license boundary is deliberate so brand assets
can travel into docs, blog posts, release announcements without
dragging the copyleft with them.
