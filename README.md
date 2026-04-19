# Phosphor Branding

<!-- SPDX-FileCopyrightText: 2026 fuddlesworth -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

Canonical brand assets for the Phosphor library suite — the cyan /
blue / purple / rose gradient logos you see on
[phosphor-works.github.io](https://phosphor-works.github.io).

## Layout

```
svg/
├── dark/                   assets tuned for dark surfaces
│   ├── phosphor.svg        main app icon
│   ├── phosphor-editor.svg editor app icon
│   └── phosphor-settings.svg
└── light/                  light-mode variants (deeper accents,
    ├── phosphor.svg        near-white bg, lower halation)
    ├── phosphor-editor.svg
    └── phosphor-settings.svg
```

All logos are 1024 × 1024 SVG with `viewBox="96 96 832 832"`.  The
corner rounding, stroke widths, and gradient stops are shared across
variants so they read as a family.

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
