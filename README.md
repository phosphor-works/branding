<!-- SPDX-FileCopyrightText: 2026 Phosphor Works Team -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Phosphor Branding

This repository holds the canonical brand assets of the Phosphor library suite. These are the cyan, blue, purple and
rose gradient logos of [phosphor-works.org](https://phosphor-works.org), the mascots, the brand palette and the
matugen template.

## Contents

```
svg/                                brand icons, by shape then theme
├── square/                         rounded-square framed icons (the sources)
│   ├── dark/                       tuned for dark surfaces
│   │   ├── phosphor.svg            umbrella brand mark (Φ)
│   │   ├── lambent.svg             Lambent shell
│   │   ├── afterglow.svg           Afterglow terminal
│   │   ├── facet.svg               Facet settings manager
│   │   ├── limn.svg                Limn text editor
│   │   ├── glisten.svg             Glisten screen capture and recorder
│   │   ├── cresset.svg             Cresset file explorer
│   │   ├── illume.svg              Illume image viewer
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
    │   ├── facet.svg
    │   ├── limn.svg
    │   ├── glisten.svg
    │   ├── cresset.svg
    │   └── illume.svg
    ├── light/                      deep gradient, for light backgrounds
    └── mono/                       single colour via currentColor
└── mascot/                         the mascots, generated (see below)
    ├── glim.svg                    standalone, transparent background
    ├── wisp.svg
    ├── nocti.svg
    └── avatar/                     the same inside the gradient ring, for bot avatars

scripts/
├── variants.py                     glow fix for the framed icons + circle
│                                   variant generator (see below)
├── check.py                        accessibility and prose check for the
│                                   framed icons, run by CI
├── mascots.py                      generates svg/mascot
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

All framed icons have the same outer frame:

- A 1024 × 1024 SVG with `viewBox="96 96 832 832"`
- A border with a 4-stop gradient from cyan through blue and purple to rose
- An inner panel with a radial fill, navy (dark) or a pastel with a brand tint (light)
- Three soft accent glows

The inner content makes each icon different:

| Mark | Inner |
| --- | --- |
| `phosphor` | Φ, a stylized flux symbol, the umbrella brand |
| `plasmazones` | Five stroked zones, the core tiling motif |
| `plasmazones-editor` | The zone motif in a canvas mark |
| `plasmazones-settings` | The zone motif in a cog outline |
| `lambent` | A curved L that holds a small flame |
| `afterglow` | A tapered A with a split elliptical crossbar, as in the Phosphor mark |
| `facet` | A brilliant-cut gem seen from above, with an octagonal table and eight star facets |
| `limn` | A slanted pen nib, split by its slit and vent, that draws a tapered stroke |
| `glisten` | A lens ring around a record dot, with a four-pointed glint of light on its rim |
| `cresset` | A beacon fire, with a three-tongued flame in a crescent bowl on a tapered pole |
| `illume` | An almond eye of two crescent lids, with a small sun of eight rays as its iris |

## Use

To use the assets from another repository, pin a release archive, as
[Releases and installing icons](#releases-and-installing-icons) tells.

To download one file, use `curl` on the raw SVG:

```sh
curl -O https://raw.githubusercontent.com/phosphor-works/branding/main/svg/square/dark/phosphor.svg
curl -O https://raw.githubusercontent.com/phosphor-works/branding/main/svg/circle/dark/phosphor.svg
```

## Mascots

The project has three Phosphor mascots. The project uses each mascot in many places, the Discord bot included. Each
mascot uses the brand palette on a 512 × 512 canvas:

| Mascot | Character |
| --- | --- |
| `glim` | A firefly in flight. Its wing covers have rose edges and are open over its translucent wings. A cyan lantern tail gives it light. |
| `wisp` | A will o the wisp. It is a rose, purple, blue and cyan flame with a white hot core, a curling tail and drifting embers. |
| `nocti` | A bioluminescent jellyfish with the Phosphor mark that glows on the crown of its bell. |

A script calculates the bodies, tentacles, ribbons and rim lights. Thus edit `scripts/mascots.py`, not the SVGs, and
run the script again.

The avatar variants are in the same gradient ring as `svg/circle`. Their framing keeps the face easy to read at the
smallest sizes of Discord after the round crop. `FIT` in the script sets the framing of each avatar. `MARK_SCALE`
makes a standalone drawing smaller when its glow goes past the edge of the canvas.

To render one avatar for upload, use
`rsvg-convert -w 1024 svg/mascot/avatar/glim.svg -o glim.png`.

## Releases and installing icons

No app copies icons or adds this repository as a submodule. Apps and the website pin a branding release by version,
URL and SHA-256. Apps install their icons from the archive. The website serves its `svg/` tree and reads its palette.
A tag `vX.Y.Z` publishes `phosphor-branding-X.Y.Z.tar.gz`:

```
phosphor-branding-X.Y.Z/
├── hicolor/scalable/apps/<name>.svg       square/dark, for dark themes
├── hicolor/<N>x<N>/apps/<name>.png        16, 22, 24, 32, 48, 64, 128, 256, 512
├── hicolor-light/...                      the same from square/light
├── svg/{square,circle,mark,mascot}/...    the source SVGs, as in this repo
├── palette/  matugen/templates/
├── cmake/PhosphorBranding.cmake
├── LICENSE  VERSION
```

An app installs each icon under its own app ID. This ID is also its `.desktop` id and its AppStream id:

```cmake
include(${branding_SOURCE_DIR}/cmake/PhosphorBranding.cmake)
phosphor_install_brand_icons(org.phosphor_works.PlasmaZones plasmazones
                             org.phosphor_works.PlasmaZones.Editor plasmazones-editor)
```

`scripts/build-release.sh <version> <out dir>` builds the same archive locally. For a given librsvg, the archive is
reproducible. The script runs `scripts/check.py` first. That check requires each framed icon to have a `<title>` and a
`<desc>` in plain prose, because screen readers announce both.

## Circle variants and the glow fix

`svg/circle/{dark,light}/` holds a round-framed copy of each framed icon, for avatars, Discord and social cards.
The rounded square becomes a circle with the same 36-unit border (outer radius 416, panel radius 380). The artwork
does not change. These files are generated. To change one, edit the square icon and run the script again.

The accent glows are circles larger than the panel. Browsers and librsvg cut them with a `clipPath`. QtSvg draws
icons for KDE and ignores `clipPath`, so the glows colored the transparent corners outside the frame. Thus the script
stores each glow as its exact intersection with the panel (square or circle). It keeps the source circle in
`data-glow="cx cy r"`. No renderer can then draw a glow outside the panel.

```sh
python3 scripts/variants.py           # fix glows in svg/square, regenerate svg/circle
python3 scripts/variants.py --check   # exit 1 if anything is out of date
```

Run the script after you add or edit a framed icon. A new icon can keep the plain glow `<circle>` elements from the
template. The script converts them.

## Color tokens

| Role | Dark | Light | Notes |
| --- | --- | --- | --- |
| Cyan | `#22D3EE` | `#0EA5E9` | Accent gradient stop 0 |
| Blue | `#3B82F6` | `#3B82F6` | Accent gradient stop 1, primary |
| Purple | `#A855F7` | `#7C3AED` | Accent gradient stop 2 |
| Rose | `#F43F5E` | `#E11D48` | Accent gradient stop 3 |
| Surface | `#0B1730` | `#E8EEFF` | Inner-square fill on the topbar logo |

The full palette and the Material You role map are at
[phosphor-works.org/palette/](https://phosphor-works.org/palette/). That page comes from the canonical
[`palette/phosphor.toml`](palette/phosphor.toml) in this repository.

## Palette

`palette/phosphor.toml` is the canonical static brand palette. It has the seven brand colors (`cyan`, `blue`,
`purple`, `rose`, `navy`, `abyss`, `void`) and the full Material You role map for the dark and light themes. It uses
the role vocabulary of [matugen](https://github.com/InioX/matugen), so apps that already use templates for matugen
output can read it directly.

To use it as a palette that does not change with the wallpaper, download it:

```sh
mkdir -p ~/.config/plasmazones
curl -L \
    https://raw.githubusercontent.com/phosphor-works/branding/main/palette/phosphor.toml \
    -o ~/.config/plasmazones/palette.toml
```

`palette/preview.html` is a self-contained preview of the swatches and the role grid. It opens directly in a browser.
[phosphor-works.org/palette/](https://phosphor-works.org/palette/) loads the same three preview CSS files
(`preview.css`, `preview.dark.css`, `preview.light.css`) at run time.

## Matugen template

`matugen/templates/phosphor-palette.toml` is the variant that changes with the wallpaper. It has the same role
structure as the static palette. The Material You engine of [matugen](https://github.com/InioX/matugen) makes it from
the dominant hues of a wallpaper. To install the template and connect it to matugen with the example config, run
these commands:

```sh
mkdir -p ~/.config/matugen/templates
curl -L \
    https://raw.githubusercontent.com/phosphor-works/branding/main/matugen/templates/phosphor-palette.toml \
    -o ~/.config/matugen/templates/phosphor-palette.toml
cat matugen/config.example.toml >> ~/.config/matugen/config.toml   # merge by hand
matugen image /path/to/wallpaper.png
```

The last command makes `~/.config/plasmazones/palette.toml` again from the wallpaper.

## License

The brand assets are licensed under **CC-BY-SA 4.0**. Use them to refer to Phosphor. You can fork them to make a
derivative. If you distribute a changed version, use the same license. The code in the projects that use the assets
(phosphor-web and others) is GPL-3.0-or-later. This license boundary is intentional. It lets the brand assets go into
documentation, blog posts and release announcements without the copyleft. The license text is in `LICENSE`.
