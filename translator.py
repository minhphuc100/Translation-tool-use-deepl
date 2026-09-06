#!/usr/bin/env python3
"""
Japanese -> English file translator

Usage:
    python translator.py "C:\\path\\to\\input.txt"

Requirements:
    pip install deepl

API key:
    Set the DEEPL_API_KEY environment variable.

Windows PowerShell:
    $env:DEEPL_API_KEY="your_api_key"

The script:
- Detects UTF-8 / UTF-8 BOM / CP932 (Windows Japanese) / Shift-JIS.
- Translates text in chunks so large files do not become one huge API request.
- Writes <original_name>_translated.txt beside the input file.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import deepl


MAX_CHARS_PER_REQUEST = 45000


def read_text_auto(path: Path) -> tuple[str, str]:
    """Try common encodings and return (text, encoding_used)."""
    raw = path.read_bytes()

    # BOMs are unambiguous.
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig"), "utf-8-sig"

    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        # Not normally expected for Japanese text, but let Python handle it.
        for enc in ("utf-16",):
            try:
                return raw.decode(enc), enc
            except UnicodeDecodeError:
                pass

    # UTF-8 first.
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        pass

    # CP932 is usually the best choice for Japanese Windows text.
    try:
        return raw.decode("cp932"), "cp932"
    except UnicodeDecodeError:
        pass

    # Strict Shift-JIS fallback.
    try:
        return raw.decode("shift_jis"), "shift_jis"
    except UnicodeDecodeError as exc:
        raise UnicodeError(
            "Could not decode the file as UTF-8, CP932, or Shift-JIS."
        ) from exc


def split_text(text: str, max_chars: int = MAX_CHARS_PER_REQUEST) -> list[str]:
    """Split text preferably at paragraph/newline boundaries."""
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for block in text.splitlines(keepends=True):
        if current and current_len + len(block) > max_chars:
            chunks.append("".join(current))
            current = []
            current_len = 0

        # A single enormous line still needs to be split.
        if len(block) > max_chars:
            if current:
                chunks.append("".join(current))
                current = []
                current_len = 0

            for i in range(0, len(block), max_chars):
                chunks.append(block[i:i + max_chars])
            continue

        current.append(block)
        current_len += len(block)

    if current:
        chunks.append("".join(current))

    return chunks


def translate_file(input_path: Path, api_key: str = "add your API key here") -> Path:
    text, detected_encoding = read_text_auto(input_path)
    chunks = split_text(text)

    print(f"Input encoding: {detected_encoding}")
    print(f"Characters: {len(text):,}")
    print(f"Translation chunks: {len(chunks)}")

    translator = deepl.DeepLClient(api_key)

    translated_chunks: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        print(f"Translating chunk {index}/{len(chunks)}...", end="", flush=True)

        result = translator.translate_text(
            chunk,
            source_lang="JA",
            target_lang="EN-US",
        )

        translated_chunks.append(result.text)
        print(" done")

    output_path = input_path.with_name(
        f"{input_path.stem}_translated{input_path.suffix}"
    )

    output_path.write_text(
        "\n".join(translated_chunks) if len(translated_chunks) > 1 else translated_chunks[0],
        encoding="utf-8",
        newline="",
    )

    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Translate a Japanese text file to English."
    )
    parser.add_argument(
        "input_file",
        help="Path to the input text file",
    )
    args = parser.parse_args()

    input_path = Path(args.input_file).expanduser()

    if not input_path.is_file():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        return 1

    api_key = "add your API key here"
        

    try:
        output_path = translate_file(input_path, api_key)
    except Exception as exc:
        print(f"\nTranslation failed: {exc}", file=sys.stderr)
        return 1

    print(f"\nFinished!")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
