#!/usr/bin/env python3
"""Определяет, тесты каких библиотек (лабораторных) затронуты изменениями.

Лабораторная — это каталог, в котором есть tests/CMakeLists.txt.
Изменение файла внутри лабораторной запускает её тесты; изменение общего кода
(common, allocator/allocator, ...) запускает тесты всех зависящих от него лабораторных.

Примеры:
    python3 .github/scripts/changed_labs.py --base origin/master
    python3 .github/scripts/changed_labs.py --all
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Изменение этих файлов затрагивает сборку всех лабораторных.
GLOBAL_FILES = {
    "CMakeLists.txt",
    ".github/workflows/pr-checks.yml",
    ".github/scripts/changed_labs.py",
}

# Общий код вне лабораторных: префикс каталога -> префиксы лабораторных, которые от него зависят.
# Выбирается самый длинный подходящий префикс.
SHARED_DIRS = {
    "common/": [""],
    "allocator/allocator/": ["allocator/", "associative_container/"],
    "allocator/": ["allocator/"],
    "associative_container/": ["associative_container/"],
}


def discover_labs():
    labs = []
    for cmake in sorted(ROOT.glob("**/tests/CMakeLists.txt")):
        rel = cmake.relative_to(ROOT)
        if rel.parts[0].startswith(("build", "cmake-build")):
            continue
        match = re.search(r"add_executable\(\s*([^\s)]+)", cmake.read_text(encoding="utf-8"))
        if not match:
            continue
        lab_dir = rel.parent.parent.as_posix()
        labs.append({
            "name": lab_dir.rsplit("/", 1)[-1],
            "dir": lab_dir,
            "target": match.group(1),
        })
    return labs


def changed_files(base, head=None):
    """Файлы, изменённые с момента ответвления от base. Без head учитывается рабочая копия."""
    revs = [f"{base}...{head}"] if head else ["--merge-base", base]
    out = subprocess.run(
        ["git", "diff", "--name-only", "--no-renames", *revs],
        cwd=ROOT, check=True, capture_output=True, text=True).stdout
    return [line for line in out.splitlines() if line]


def owning_lab(path, labs):
    for lab in labs:
        if path.startswith(lab["dir"] + "/"):
            return lab
    return None


def affected_labs(paths, labs):
    affected = set()
    for path in paths:
        if path in GLOBAL_FILES:
            return labs
        lab = owning_lab(path, labs)
        if lab:
            affected.add(lab["dir"])
            continue
        prefixes = [p for p in SHARED_DIRS if path.startswith(p)]
        if not prefixes:
            continue
        dependents = SHARED_DIRS[max(prefixes, key=len)]
        affected.update(l["dir"] for l in labs if any(l["dir"].startswith(d) for d in dependents))
    return [lab for lab in labs if lab["dir"] in affected]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--base", help="git-ревизия, с которой сравниваются изменения (например, origin/master)")
    group.add_argument("--all", action="store_true", help="выбрать все лабораторные")
    parser.add_argument("--head", help="git-ревизия с изменениями (по умолчанию — рабочая копия)")
    parser.add_argument("--github-output", action="store_true",
                        help="записать результат в $GITHUB_OUTPUT (labs, has_labs)")
    args = parser.parse_args()

    labs = discover_labs()
    selected = labs if args.all else affected_labs(changed_files(args.base, args.head), labs)

    if args.github_output:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
            out.write(f"labs={json.dumps(selected)}\n")
            out.write(f"has_labs={'true' if selected else 'false'}\n")

    if selected:
        print("Затронутые лабораторные:")
        for lab in selected:
            print(f"  {lab['dir']} ({lab['target']})")
    else:
        print("Изменения не затрагивают ни одну лабораторную — тесты запускаться не будут.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
