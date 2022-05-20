#!/usr/bin/env python3
import re
from pathlib import Path
from typing import Optional

from markdown import (
    parse_markdown,
    Code,
    Paragraph,
    MarkdownDoc,
    Whitespace,
    Header,
    RefLink,
)


class FrontMatter:
    layout: str
    section: str
    description: Optional[str]

    def __init__(self, layout: str, section: str, description: Optional[str] = None):
        self.layout = layout
        self.description = description
        self.section = section


def convert_to_jekyll(path: Path, front_matter: FrontMatter) -> str:
    text = path.read_text()
    md_raw = parse_markdown(text)
    md_escaped = MarkdownDoc()

    # Extract title from source to inject it in the front matter header:
    h1s = (f for f in md_raw.children if isinstance(f, Header) and f.level == 1)
    h1 = next(h1s)

    # Construct front matter header:
    header = "---\n"
    header += f"layout: {front_matter.layout}\n"
    if h1:
        header += f"title: {h1.title}\n"
    if front_matter.description:
        header += f"description: {front_matter.description}\n"
    header += f"section: {front_matter.section}\n"
    header += "---\n"
    header_node = Paragraph(content=header)
    whitespace_node = Whitespace(content="\n")
    md_escaped.add_child(header_node)
    md_escaped.add_child(whitespace_node)

    for node in md_raw.children:

        if isinstance(node, Code) and node.content.startswith("```hurl"):
            # Add Jekyll escape directive around code
            # so Hurl templates (ex: {{foo}}) are well rendered.
            begin_escape_node = Paragraph(content="{% raw %}\n")
            whitespace_node = Whitespace(content="\n")
            end_escape_node = Paragraph(content="{% endraw %}\n")
            md_escaped.add_child(begin_escape_node)
            md_escaped.add_child(node)
            md_escaped.add_child(whitespace_node)
            md_escaped.add_child(end_escape_node)
        elif isinstance(node, RefLink) and ".md" in node.link:
            # Convert reference links to Jekyll reference link
            ret = re.match(r"(?P<base>.+\.md)#?(?P<anchor>.*)", node.link)
            base = ret.group("base")
            anchor = ret.group("anchor")
            if anchor:
                link = f"{{% link _docs/{base} %}}#{anchor}"
            else:
                link = f"{{% link _docs/{base} %}}"
            ref_link = RefLink(ref=node.ref, link=link)
            md_escaped.add_child(ref_link)
        else:
            md_escaped.add_child(node)

    return md_escaped.to_text()


class ConvertTask:
    file_src: Path
    file_dst: Path
    front_matter: FrontMatter

    def __init__(
        self, file_src: Path, file_dst: Path, front_matter: FrontMatter
    ) -> None:
        self.file_src = file_src
        self.file_dst = file_dst
        self.front_matter = front_matter

    def run(self):
        md = convert_to_jekyll(path=self.file_src, front_matter=self.front_matter)
        self.file_dst.write_text(md)


def build():
    task = ConvertTask(
        file_src=Path("../hurl/docs/hurl-file.md"),
        file_dst=Path("sites/hurl.dev/_docs/hurl-file.md"),
        front_matter=FrontMatter(layout="doc", section="File Format"),
    )
    task.run()

    task = ConvertTask(
        file_src=Path("../hurl/docs/entry.md"),
        file_dst=Path("sites/hurl.dev/_docs/entry.md"),
        front_matter=FrontMatter(layout="doc", section="File Format"),
    )
    task.run()

    task = ConvertTask(
        file_src=Path("../hurl/docs/request.md"),
        file_dst=Path("sites/hurl.dev/_docs/request.md"),
        front_matter=FrontMatter(layout="doc", section="File Format"),
    )
    task.run()

    task = ConvertTask(
        file_src=Path("../hurl/docs/response.md"),
        file_dst=Path("sites/hurl.dev/_docs/response.md"),
        front_matter=FrontMatter(layout="doc", section="File Format"),
    )
    task.run()

    task = ConvertTask(
        file_src=Path("../hurl/docs/capturing-response.md"),
        file_dst=Path("sites/hurl.dev/_docs/capturing-response.md"),
        front_matter=FrontMatter(layout="doc", section="File Format"),
    )
    task.run()

    task = ConvertTask(
        file_src=Path("../hurl/docs/asserting-response.md"),
        file_dst=Path("sites/hurl.dev/_docs/asserting-response.md"),
        front_matter=FrontMatter(layout="doc", section="File Format"),
    )
    task.run()


def main():
    build()


if __name__ == "__main__":
    main()
