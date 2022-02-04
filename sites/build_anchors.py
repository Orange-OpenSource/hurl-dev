#!/usr/bin/env python3
import re
from pathlib import Path


def main():
    print(f"Building anchors...")

    for filename in Path("hurl.dev", "_site").glob("**/*.html"):
        print(f"Processing {filename}...")
        file = Path(filename)
        text = file.read_text()
        text_anchored = add_anchors(text)
        file.write_text(text_anchored)


def add_anchors(text: str) -> str:
    """Add anchors to the html file.

    Replaces html header with id like this:
        <h2 id="some-stuff">Some Title</h2>
    With this
        <h2 id="some-stuff"><a href="#some-stuff">Some Title</a></h2>
    """
    pattern = (
        r"<(?P<tag>h[1-6])"  # start of of header tag <h1, <h2 etc...
        r"\s+"  # whitespace between tag and id
        r'id="(?P<id>[a-z0-9\-_]+)"'  # id of the tag, eg id="whats-hurl"
        r">"  # end of the opening tag
        r"(?P<title>.*?)"  # content of the header tag
        r"</(?P=tag)>"  # closing header tag
    )
    p = re.compile(pattern)

    def replacement(match):
        tag = match.group("tag")
        _id = match.group("id")
        _id = re.sub(r"-{2,}", "-", _id)
        title = match.group("title")
        return f'<{tag} id="{_id}"><a href="#{_id}">{title}</a></{tag}>'

    text_anchored = p.sub(replacement, text)
    return text_anchored


if __name__ == "__main__":
    main()
