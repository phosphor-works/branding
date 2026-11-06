#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 fuddlesworth
# SPDX-License-Identifier: CC-BY-SA-4.0
#
# Build the branding release archive, the one artifact apps pin:
#
#   scripts/build-release.sh <version> <out dir>
#
# writes <out dir>/phosphor-branding-<version>.tar.gz and its .sha256. The
# archive holds the framed icons as hicolor (dark themes) and hicolor-light
# trees, scalable and rendered to PNG, the palette, the matugen template,
# cmake/PhosphorBranding.cmake and the licence. The tarball is reproducible:
# sorted entries, fixed times and owners, so the same tree gives the same
# SHA-256. Needs rsvg-convert (librsvg).
set -euo pipefail

version=${1:?usage: build-release.sh <version> <out dir>}
out=${2:?usage: build-release.sh <version> <out dir>}
root=$(cd "$(dirname "$0")/.." && pwd)
name="phosphor-branding-${version}"
mkdir -p "$out"
out=$(cd "$out" && pwd)
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
dest="$stage/$name"

python3 "$root/scripts/check.py"

sizes=(16 22 24 32 48 64 128 256 512)
for pair in dark:hicolor light:hicolor-light; do
    variant=${pair%%:*}
    theme=${pair#*:}
    mkdir -p "$dest/$theme/scalable/apps"
    for svg in "$root"/svg/square/"$variant"/*.svg; do
        icon=$(basename "$svg" .svg)
        cp "$svg" "$dest/$theme/scalable/apps/$icon.svg"
        for size in "${sizes[@]}"; do
            mkdir -p "$dest/$theme/${size}x${size}/apps"
            rsvg-convert --width "$size" --height "$size" --keep-aspect-ratio \
                --output "$dest/$theme/${size}x${size}/apps/$icon.png" "$svg"
        done
    done
done

cp -r "$root/palette" "$dest/palette"
mkdir -p "$dest/matugen"
cp -r "$root/matugen/templates" "$dest/matugen/templates"
mkdir -p "$dest/cmake"
cp "$root/cmake/PhosphorBranding.cmake" "$dest/cmake/"
cp "$root/LICENSE" "$dest/LICENSE"
printf '%s\n' "$version" > "$dest/VERSION"

tar --sort=name --mtime='@0' --owner=0 --group=0 --numeric-owner \
    -C "$stage" -cf - "$name" | gzip -n -9 > "$out/$name.tar.gz"
(cd "$out" && sha256sum "$name.tar.gz" > "$name.tar.gz.sha256")
cat "$out/$name.tar.gz.sha256"
