#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 fuddlesworth
# SPDX-License-Identifier: CC-BY-SA-4.0
"""Check the framed icons before a release.

Every icon in svg/square and svg/circle must be accessible: role="img",
aria-labelledby="title desc", and one non-empty <title id="title"> and
<desc id="desc">. Screen readers announce both, so they follow the suite's
plain-prose rules: no em or en dash, no spaced hyphen standing in for a dash,
and no semicolon joining two clauses. The circle variants must also be up to
date with the squares (scripts/variants.py --check).

    python3 scripts/check.py      # exit 1 and list every problem
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRAMED = ("square", "circle")


def problems_in(path: Path) -> list[str]:
    text = path.read_text()
    rel = path.relative_to(ROOT).as_posix()
    found: list[str] = []
    head = re.search(r"<svg\b([^>]*)>", text)
    if not head:
        return [f"{rel}: no <svg> element"]
    attrs = head.group(1)
    if 'role="img"' not in attrs:
        found.append(f'{rel}: <svg> lacks role="img"')
    if 'aria-labelledby="title desc"' not in attrs:
        found.append(f'{rel}: <svg> lacks aria-labelledby="title desc"')
    for tag in ("title", "desc"):
        matches = re.findall(rf'<{tag} id="{tag}">([^<]*)</{tag}>', text)
        if len(matches) != 1 or not matches[0].strip():
            found.append(f'{rel}: needs exactly one non-empty <{tag} id="{tag}">')
            continue
        prose = matches[0]
        if "—" in prose or "–" in prose:
            found.append(f"{rel}: <{tag}> uses a dash; write two sentences or join with a word")
        if " - " in prose:
            found.append(f"{rel}: <{tag}> uses a spaced hyphen as a dash")
        if ";" in prose:
            found.append(f"{rel}: <{tag}> joins clauses with a semicolon")
    return found


def main() -> int:
    problems: list[str] = []
    for shape in FRAMED:
        for path in sorted((ROOT / "svg" / shape).glob("*/*.svg")):
            problems.extend(problems_in(path))
    variants = subprocess.run([sys.executable, str(ROOT / "scripts" / "variants.py"), "--check"],
                              capture_output=True, text=True)
    if variants.returncode != 0:
        problems.extend(line for line in variants.stdout.splitlines() if line)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
