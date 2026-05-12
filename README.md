# Phosphor Branding

<!-- SPDX-FileCopyrightText: 2026 fuddlesworth -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

Canonical brand assets for the Phosphor library suite — the cyan /
blue / purple / rose gradient logos you see on
[phosphor-works.github.io](https://phosphor-works.github.io).

## Layout

```
svg/
├── dark/                           assets tuned for dark surfaces
│   ├── phosphor.svg                umbrella brand mark (Φ)
│   ├── phosphor-shell.svg          PhosphorShell library mark
│   ├── plasmazones.svg             PlasmaZones app icon
│   ├── plasmazones-editor.svg      PlasmaZones layout editor
│   └── plasmazones-settings.svg    PlasmaZones settings
└── light/                          near-white variants
    ├── phosphor.svg
    ├── phosphor-shell.svg
    ├── plasmazones.svg
    ├── plasmazones-editor.svg
    └── plasmazones-settings.svg
```

All marks share the same outer frame: a 1024 × 1024 SVG with
`viewBox="96 96 832 832"`, a 4-stop cyan → blue → purple → rose
gradient border, and a radial navy (dark) or near-white (light)
inner fill.  The inner content distinguishes them:

| Mark                   | Inner                                                        |
|------------------------|--------------------------------------------------------------|
| `phosphor`             | Φ — stylized flux symbol, umbrella brand.                    |
| `phosphor-shell`       | Three nested rounded rectangles — containment framework wrapping inner surfaces. |
| `plasmazones`          | Five stroked zones, the core tiling motif.                   |
| `plasmazones-editor`   | Zone motif wrapped in a canvas mark.                         |
| `plasmazones-settings` | Zone motif wrapped in a cog outline.                         |

## Color tokens

| Role      | Dark     | Light     | Notes |
|-----------|----------|-----------|-------|
| Cyan      | `#22D3EE`| `#0EA5E9` | accent gradient stop 0 |
| Blue      | `#3B82F6`| `#3B82F6` | accent gradient stop 1 / primary |
| Purple    | `#A855F7`| `#7C3AED` | accent gradient stop 2 |
| Rose      | `#F43F5E`| `#E11D48` | accent gradient stop 3 |
| Surface   | `#0B1730`| `#E8EEFF` | inner-square fill on the topbar logo |

Full palette + Material You role map lives at
[phosphor-works.github.io/palette/](https://phosphor-works.github.io/palette/).

## Usage

**Consuming from another repo:** add this repo as a git submodule.

```sh
git submodule add https://github.com/phosphor-works/branding.git submodules/branding
git submodule update --init --recursive
```

**One-off download:** `curl` the raw SVG:

```sh
curl -O https://raw.githubusercontent.com/phosphor-works/branding/main/svg/dark/phosphor.svg
```

## License

Brand assets are **CC-BY-SA 4.0** — use them to refer to Phosphor, fork
them if you're making a derivative, share-alike if you redistribute a
modified version.  Code in consuming projects (phosphor-web, etc.) is
GPL-3.0-or-later; the license boundary is deliberate so brand assets
can travel into docs, blog posts, release announcements without
dragging the copyleft with them.
