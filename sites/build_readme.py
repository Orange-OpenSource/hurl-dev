#!/usr/bin/env python3
# ./build_readme.py github > ../../hurl/README.md
# ./build_readme.py crates > ../../hurl/packages/hurl/README.md
import os
import re
import sys
from pathlib import Path
from textwrap import dedent

from markdown import parse_markdown, Header, MarkdownDoc


def get_markdown_doc(src: Path) -> MarkdownDoc:
    doc = parse_markdown(text=src.read_text(), use_front_matter=True)

    # Delete all nodes up to first header
    first_header = doc.find_first(lambda it: isinstance(it, Header))
    if first_header:
        index = doc.children.index(first_header)
        doc.children = doc.children[index:]
    return doc


def main(dest: str) -> int:

    header: str

    if dest == "github":
        header = dedent("""\
            <img src="https://raw.githubusercontent.com/Orange-OpenSource/hurl/master/docs/logo-dark.svg?sanitize=true#gh-dark-mode-only" alt="Hurl Logo" width="264px"><img src="https://raw.githubusercontent.com/Orange-OpenSource/hurl/master/docs/logo-light.svg?sanitize=true#gh-light-mode-only" alt="Hurl Logo" width="264px">
            
            <br/>
            
            [![deploy status](https://github.com/Orange-OpenSource/hurl/workflows/CI/badge.svg)](https://github.com/Orange-OpenSource/hurl/actions)
            [![CircleCI](https://circleci.com/gh/lepapareil/hurl/tree/master.svg?style=shield)](https://circleci.com/gh/lepapareil/hurl/tree/master)
            [![Crates.io](https://img.shields.io/crates/v/hurl.svg)](https://crates.io/crates/hurl)
            [![documentation](https://img.shields.io/badge/-documentation-informational)](https://hurl.dev)
            
            """)
    elif dest == "crates":
        header = dedent("""\
            <img src="https://raw.githubusercontent.com/Orange-OpenSource/hurl/master/docs/logo-light.svg" alt="Hurl Logo" width="264px">
            
            <br/>
            
            [![deploy status](https://github.com/Orange-OpenSource/hurl/workflows/CI/badge.svg)](https://github.com/Orange-OpenSource/hurl/actions)
            [![CircleCI](https://circleci.com/gh/lepapareil/hurl/tree/master.svg?style=shield)](https://circleci.com/gh/lepapareil/hurl/tree/master)
            [![Crates.io](https://img.shields.io/crates/v/hurl.svg)](https://crates.io/crates/hurl)
            [![documentation](https://img.shields.io/badge/-documentation-informational)](https://hurl.dev)
            
            """)
    else:
        sys.stderr.write("build_readme.py [github, crates]\n")
        return os.EX_USAGE

    header_md = parse_markdown(text=header, use_front_matter=False)

    home_md = get_markdown_doc(src=Path("hurl.dev/index.md"))
    samples_md = get_markdown_doc(src=Path("hurl.dev/_docs/samples.md"))
    usage_md = get_markdown_doc(src=Path("hurl.dev/_docs/man-page.md"))
    installation_md = get_markdown_doc(src=Path("hurl.dev/_docs/installation.md"))

    # Process Home / Why Hurl
    # We adapt the "Why Hurl" part to transform h2 tag back to markdown
    def showcase_rep(m):
        return f"<li><b>{m.group(1)}:</b> {m.group(2).lower()}</li>"
    why_paragraph = home_md.find_first(lambda it: '<ul class="showcase-container">'in it.content)
    r = re.compile(r'<li class="showcase-item"><h2 class="showcase-item-title">(.+?)<\/h2>(.+?)<\/li>', re.DOTALL)
    why_paragraph.content = r.sub(showcase_rep, why_paragraph.content)

    body_md = MarkdownDoc()
    body_md.extend(samples_md)
    body_md.extend(usage_md)
    body_md.extend(installation_md)
    toc = body_md.toc()
    toc_md = parse_markdown(text=toc, use_front_matter=False)

    readme_md = MarkdownDoc()
    readme_md.extend(header_md)

    readme_md.extend(home_md)
    readme_md.extend(toc_md)
    readme_md.extend(body_md)

    readme = readme_md.to_text()

    print(readme)
    return os.EX_OK


if __name__ == "__main__":
    main(dest=sys.argv[1])
