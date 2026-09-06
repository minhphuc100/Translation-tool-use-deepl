#!/usr/bin/env python3
"""
Japanese Filename Translator / Renamer

Usage:
    python rename_translator.py "C:\\path\\to\\folder"
    python rename_translator.py "C:\\path\\to\\file.mkv"

Requirements:
    pip install deepl

API key:
    Set DEEPL_API_KEY in your environment.

The script:
- Accepts a single file or a directory.
- Translates only the filename, never the extension.
- Shows a preview before renaming.
- Skips files that do not contain Japanese characters.
- Avoids overwriting existing files.
- Uses DeepL for Japanese -> English translation.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import deepl


JAPANESE_RE = re.compile(
    r"[\u3040-\u309F\u30A0-\u30FF\u3400-\u4DBF\u4E00-\u9FFF]"
)


def contains_japanese(text: str) -> bool:
    return bool(JAPANESE_RE.search(text))


def clean_filename(name: str) -> str:
    """Clean characters that are problematic in Windows filenames."""
    # Windows does not allow these characters in filenames.
    name = re.sub(r'[<>:"/\\|?*]', "", name)

    # Control characters are also invalid.
    name = "".join(ch for ch in name if ord(ch) >= 32)

    # Windows filenames cannot end in a space or period.
    name = name.rstrip(" .")

    return name


def collect_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]

    if path.is_dir():
        return sorted(
            p for p in path.iterdir()
            if p.is_file()
        )

    raise FileNotFoundError(f"Path not found: {path}")


def translate_names(files: list[Path], translator: deepl.DeepLClient):
    candidates = []

    for file in files:
        # suffix preserves .mkv, .mp4, .pdf, etc.
        stem = file.stem

        if not contains_japanese(stem):
            continue

        candidates.append((file, stem))

    if not candidates:
        print("No filenames containing Japanese characters were found.")
        return []

    results = []

    for index, (file, stem) in enumerate(candidates, start=1):
        print(
            f"Translating {index}/{len(candidates)}: {file.name}",
            end=" ... ",
            flush=True,
        )

        result = translator.translate_text(
            stem,
            source_lang="JA",
            target_lang="EN-US",
        )

        translated_stem = clean_filename(result.text.strip())

        if not translated_stem:
            print("skipped (empty translation)")
            continue

        new_path = file.with_name(
            translated_stem + file.suffix
        )

        results.append((file, new_path))
        print("done")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Translate Japanese filenames to English."
    )
    parser.add_argument(
        "path",
        help="A file or directory containing files to rename.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Rename without asking for confirmation.",
    )
    args = parser.parse_args()

    path = Path(args.path).expanduser()

    if not path.exists():
        print(f"Error: path not found: {path}", file=sys.stderr)
        return 1

    api_key = os.environ.get("DEEPL_API_KEY")
    if not api_key:
        print(
            "Error: DEEPL_API_KEY environment variable is not set. using default api key for testing. Please set your own key for production use.",
            file=sys.stderr
        )
        api_key="add your own key here"
        return 1

    try:
        files = collect_files(path)
        translator = deepl.DeepLClient(api_key)
        results = translate_names(files, translator)
    except Exception as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1

    if not results:
        return 0

    print("\nPreview:")
    print("-" * 70)

    valid_results = []

    for old_path, new_path in results:
        print(f"{old_path.name}")
        print(f"  -> {new_path.name}")

        if new_path.exists() and new_path != old_path:
            print("  [SKIP] Destination already exists.")
            continue

        if new_path == old_path:
            print("  [SKIP] Name is unchanged.")
            continue

        valid_results.append((old_path, new_path))

    print("-" * 70)

    if not valid_results:
        print("Nothing to rename.")
        return 0

    if not args.yes:
        answer = input(
            f"\nRename {len(valid_results)} file(s)? [y/N]: "
        ).strip().lower()

        if answer not in ("y", "yes"):
            print("Cancelled. No files were renamed.")
            return 0

    renamed = 0

    for old_path, new_path in valid_results:
        try:
            old_path.rename(new_path)
            print(f"Renamed: {old_path.name} -> {new_path.name}")
            renamed += 1
        except OSError as exc:
            print(
                f"Failed: {old_path.name}: {exc}",
                file=sys.stderr,
            )

    print(f"\nFinished. Renamed {renamed}/{len(valid_results)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
