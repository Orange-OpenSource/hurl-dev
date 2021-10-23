#!/usr/bin/env python3
# ./build_github_readme.py > ../../hurl/README.md
import re
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


def main() -> int:

    presentation_md = parse_markdown("# Presentation\n\n", False)
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
    home_md.indent()

    readme_md = MarkdownDoc()
    readme_md.extend(presentation_md)
    readme_md.extend(home_md)
    readme_md.extend(samples_md)
    readme_md.extend(usage_md)
    readme_md.extend(installation_md)

    header = dedent("""\
        <a href="https://hurl.dev"><img src="https://raw.githubusercontent.com/Orange-OpenSource/hurl/master/docs/logo.svg?sanitize=true" align="center" width="264px"/></a>
        
        <br/>
        
        [![deploy status](https://github.com/Orange-OpenSource/hurl/workflows/CI/badge.svg)](https://github.com/Orange-OpenSource/hurl/actions)
        [![Crates.io](https://img.shields.io/crates/v/hurl.svg)](https://crates.io/crates/hurl)
        [![documentation](https://img.shields.io/badge/-documentation-informational)](https://hurl.dev)
        """)
    toc = readme_md.toc()
    body = readme_md.to_text()
    readme = f"{header}\n{toc}\n{body}"
    print(readme)
    return 0


if __name__ == "__main__":
    main()
