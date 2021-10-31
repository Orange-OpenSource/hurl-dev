#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import List


def remove_prefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def sitemap() -> List[str]:

    def is_blacklisted(f) -> bool:
        blacklists = ["404.html", "search.html"]
        for blacklist in blacklists:
            if blacklist in f:
                return True
        return False

    files = [remove_prefix(str(f), "hurl.dev/_site/") for f in Path("hurl.dev", "_site").glob('**/*.html')]
    files = [f"https://hurl.dev/{f}" for f in files if not is_blacklisted(f)]
    return files


def main():
    sys.stderr.write("Generating sitemap...\n")
    [print(f) for f in sitemap()]


if __name__ == "__main__":
    main()
