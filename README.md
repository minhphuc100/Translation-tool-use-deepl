"""
Japanese Filename Translator / Renamer

Usage:
    python rename_translator.py "C:\\path\\to\\folder"
    python rename_translator.py "C:\\path\\to\\file.mkv"

Requirements:
    pip install deepl

API key:
    Set DEEPL_API_KEY

The script:
- Accepts a single file or a directory.
- Translates only the filename, never the extension.
- Shows a preview before renaming.
- Skips files that do not contain Japanese characters.
- Avoids overwriting existing files.
- Uses DeepL for Japanese -> English translation.
"""
