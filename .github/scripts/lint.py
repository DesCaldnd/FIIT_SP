#!/usr/bin/env python3
"""Линтер: запускает clang-tidy для C++ файлов, изменённых относительно базовой ревизии.

Каталоги tests/ не проверяются. Для заголовка проверяются все единицы трансляции
его библиотеки (включая тесты, чтобы инстанцировались шаблоны), но замечания
выводятся только по изменённым файлам.

Нужна сборочная директория с compile_commands.json:
    cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
    python3 .github/scripts/lint.py --base origin/master
"""

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from changed_labs import ROOT, changed_files  # noqa: E402

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx"}
HEADER_SUFFIXES = {".h", ".hh", ".hpp", ".hxx"}


def lintable(path):
    return (Path(path).suffix in SOURCE_SUFFIXES | HEADER_SUFFIXES
            and "tests" not in Path(path).parts
            and (ROOT / path).is_file())


def owner_dir(path):
    """Каталог библиотеки, которой принадлежит файл (родитель include/ или src/)."""
    parts = Path(path).parts
    for marker in ("include", "src"):
        if marker in parts:
            return Path(*parts[:parts.index(marker)]).as_posix()
    return Path(path).parent.as_posix()


def load_units(build_dir):
    db_path = build_dir / "compile_commands.json"
    if not db_path.is_file():
        sys.exit(f"Не найден {db_path}. Сконфигурируйте проект с -DCMAKE_EXPORT_COMPILE_COMMANDS=ON.")
    units = set()
    for entry in json.loads(db_path.read_text(encoding="utf-8")):
        file = Path(entry["directory"], entry["file"]).resolve()
        try:
            units.add(file.relative_to(ROOT).as_posix())
        except ValueError:
            pass  # файлы вне репозитория (googletest)
    return units


def plan(files, units):
    """Возвращает {единица трансляции: набор изменённых файлов, замечания по которым нужны}."""
    jobs = {}
    for path in files:
        if Path(path).suffix in SOURCE_SUFFIXES:
            targets = [path] if path in units else []
        else:
            owner = owner_dir(path) + "/"
            targets = [u for u in units if u.startswith(owner)]
        if not targets:
            print(f"предупреждение: {path} не входит ни в одну цель сборки, пропускаю")
        for unit in targets:
            jobs.setdefault(unit, set()).add(path)
    return jobs


def run_clang_tidy(clang_tidy, build_dir, unit, filter_files):
    line_filter = json.dumps([{"name": Path(f).name} for f in sorted(filter_files)])
    proc = subprocess.run(
        [clang_tidy, "-p", str(build_dir), "--quiet", f"--line-filter={line_filter}", unit],
        cwd=ROOT, capture_output=True, text=True)
    output = "\n".join(
        line for line in (proc.stdout + proc.stderr).splitlines()
        if line and not line.endswith(("warnings generated.", "warning generated."))
        and not line.startswith(("Suppressed ", "Use -header-filter", "Error while processing")))
    return unit, proc.returncode, output


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--base", help="git-ревизия, с которой сравниваются изменения (например, origin/master)")
    group.add_argument("--all", action="store_true", help="проверить все файлы (кроме tests/)")
    parser.add_argument("--head", help="git-ревизия с изменениями (по умолчанию — рабочая копия)")
    parser.add_argument("--build-dir", default="build", help="каталог сборки с compile_commands.json")
    parser.add_argument("--clang-tidy", default=os.environ.get("CLANG_TIDY", "clang-tidy"))
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 1)
    args = parser.parse_args()

    if args.all:
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True,
                                 capture_output=True, text=True).stdout.splitlines()
        files = [f for f in tracked if lintable(f)]
    else:
        files = [f for f in changed_files(args.base, args.head) if lintable(f)]

    if not files:
        print("Нет изменённых C++ файлов для проверки.")
        return 0

    print("Проверяемые файлы:")
    for f in files:
        print(f"  {f}")

    build_dir = (ROOT / args.build_dir).resolve()
    jobs = plan(files, load_units(build_dir))

    failed = False
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(run_clang_tidy, args.clang_tidy, build_dir, unit, filt)
                   for unit, filt in sorted(jobs.items())]
        for future in futures:
            unit, code, output = future.result()
            status = "OK" if code == 0 else "FAIL"
            print(f"\n[{status}] {unit}")
            if output:
                print(output)
            failed |= code != 0

    if failed:
        print("\nЛинтер нашёл проблемы (см. выше). Конфигурация проверок — в файле .clang-tidy.")
        return 1
    print("\nЛинтер: замечаний нет.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
