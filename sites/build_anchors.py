#!/usr/bin/env python3
import re
from pathlib import Path

import sys
from bs4 import BeautifulSoup


def main():
    print(f"Building anchors...")

    for filename in Path("hurl.dev", "_site").glob('**/*.html'):
        print(f"Processing {filename}...")
        src = Path(filename)
        add_anchors(src)


def add_anchors(file: Path) -> None:
    """Add anchors to the html file."""
    soup = BeautifulSoup(file.read_text(), "html.parser")
    root = soup.find("div", class_=re.compile("indexed"))
    if not root:
        print(f"No indexed content in path {file}")
        return

    # Add a <a> link to all indexed headers
    for i in range(1, 7):
        hs = root.find_all(f"h{i}")
        for h in hs:
            id_ = h["id"]
            content = h.string
            if not id_:
                print(f"Warning tag {h} has not id")
                continue
            if h.a:
                print(f"Tag {h} already have a link")
            new_tag = soup.new_tag("a", href=f"#{id_}")
            new_tag.string = content
            h.string.replace_with("")
            h.string.wrap(new_tag)

    file.write_text(str(soup))


if __name__ == "__main__":
    main()
