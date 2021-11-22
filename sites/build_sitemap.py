#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import List


def remove_prefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def sitemap() -> List[str]:

    def is_blacklisted(f: Path) -> bool:
        return 'data-indexed="true"' not in f.read_text()

    files = [f for f in Path("hurl.dev", "_site").glob('**/*.html') if not is_blacklisted(f)]
    files = [remove_prefix(str(f), "hurl.dev/_site/") for f in files]
    files = [f"https://hurl.dev/{f}" for f in files]
    files.sort()
    return files


def main():
    sys.stderr.write("Generating sitemap...\n")
    [print(f) for f in sitemap()]


if __name__ == "__main__":
    main()
