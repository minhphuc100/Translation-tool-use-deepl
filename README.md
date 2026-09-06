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




"""
Japanese -> English file translator

Usage:
    python translator.py "C:\\path\\to\\input.txt"

Requirements:
    pip install deepl
(
API key:
    Set the DEEPL_API_KEY environment variable.

Windows PowerShell:
    $env:DEEPL_API_KEY="your_api_key"
[System.Environment]::SetEnvironmentVariable("MY_VARIABLE", "MyValue", "User")
) i don't want to use env vari so i directly set the vari in code
The script:
- Detects UTF-8 / UTF-8 BOM / CP932 (Windows Japanese) / Shift-JIS.
- Translates text in chunks so large files do not become one huge API request.
- Writes <original_name>_translated.txt beside the input file.

"""
