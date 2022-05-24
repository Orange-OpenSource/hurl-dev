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


def process_local_link(match) -> str:
    base = match.group("base")
    anchor = match.group("anchor")
    title = match.group("title")
    if anchor:
        link = f"[{title}]({{% link _docs/{base} %}}#{anchor})"
    else:
        link = f"[{title}]({{% link _docs/{base} %}})"
    return link


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

        if (
            isinstance(node, Code)
            and re.match(
                r"[`~]{3}hurl", node.content
            )  # Hurl language ~~~hurl or ```hurl
            and re.search(
                r"\{\{.+}}", node.content, re.MULTILINE
            )  # Hurl snippet containing templates must be escaped
        ):
            # Add Jekyll escape directive around code
            # so Hurl templates (ex: {{foo}}) are well rendered.
            begin_escape_node = Paragraph(content="{% raw %}\n")
            whitespace_node = Whitespace(content="\n")
            end_escape_node = Paragraph(content="{% endraw %}\n")
            md_escaped.add_child(begin_escape_node)
            md_escaped.add_child(node)
            md_escaped.add_child(whitespace_node)
            md_escaped.add_child(end_escape_node)
        elif isinstance(node, Paragraph):

            # Escape inline code that contains {{ }}.
            content = node.content
            content = re.sub(
                r"(`.*\{\{.+}}.*`)", r"{% raw %}\1{% endraw %}", content
            )

            # Convert local links to Jekyll link
            content = re.sub(
                r"\[(?P<title>.+)]\((?P<base>.+\.md)#?(?P<anchor>.*)\)",
                process_local_link,
                content
            )
            p_node = Paragraph(content=content)
            md_escaped.add_child(p_node)
        elif (
            isinstance(node, RefLink)
            and ".md" in node.link
            and not node.link.startswith("http")
        ):
            # Convert local reference links to Jekyll reference link
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

    def convert(self):
        md = convert_to_jekyll(path=self.file_src, front_matter=self.front_matter)
        self.file_dst.write_text(md)


def build():
    docs = [
        (
            Path("../hurl/docs/installation.md"),
            Path("sites/hurl.dev/_docs/installation.md"),
            FrontMatter(
                layout="doc",
                section="Getting Started",
                description="How to install or build Hurl on Linux, macOS and Windows platform.",
            ),
        ),
        (
            Path("../hurl/docs/man-page.md"),
            Path("sites/hurl.dev/_docs/man-page.md"),
            FrontMatter(
                layout="doc",
                section="Getting Started",
                description="Hurl command line usage, with options descriptions.",
            ),
        ),
        (
            Path("../hurl/docs/samples.md"),
            Path("sites/hurl.dev/_docs/samples.md"),
            FrontMatter(
                layout="doc",
                section="Getting Started",
                description="Various Hurl samples to show how to run and tests HTTP requests and responses.",
            ),
        ),
        (
            Path("../hurl/docs/grammar.md"),
            Path("sites/hurl.dev/_docs/grammar.md"),
            FrontMatter(layout="doc", section="File Format"),
        ),
        (
            Path("../hurl/docs/hurl-file.md"),
            Path("sites/hurl.dev/_docs/hurl-file.md"),
            FrontMatter(layout="doc", section="File Format"),
        ),
        (
            Path("../hurl/docs/entry.md"),
            Path("sites/hurl.dev/_docs/entry.md"),
            FrontMatter(layout="doc", section="File Format"),
        ),
        (
            Path("../hurl/docs/request.md"),
            Path("sites/hurl.dev/_docs/request.md"),
            FrontMatter(layout="doc", section="File Format"),
        ),
        (
            Path("../hurl/docs/response.md"),
            Path("sites/hurl.dev/_docs/response.md"),
            FrontMatter(layout="doc", section="File Format"),
        ),
        (
            Path("../hurl/docs/capturing-response.md"),
            Path("sites/hurl.dev/_docs/capturing-response.md"),
            FrontMatter(layout="doc", section="File Format"),
        ),
        (
            Path("../hurl/docs/asserting-response.md"),
            Path("sites/hurl.dev/_docs/asserting-response.md"),
            FrontMatter(layout="doc", section="File Format"),
        ),
        (
            Path("../hurl/docs/templates.md"),
            Path("sites/hurl.dev/_docs/templates.md"),
            FrontMatter(
                layout="doc",
                section="File Format",
                description="Hurl file format variables and templating.",
            ),
        ),
        (
            Path("../hurl/docs/grammar.md"),
            Path("sites/hurl.dev/_docs/grammar.md"),
            FrontMatter(layout="doc", section="File Format"),
        ),
    ]

    for (src, dst, front_matter) in docs:
        task = ConvertTask(
            file_src=src,
            file_dst=dst,
            front_matter=front_matter,
        )
        task.convert()


def main():
    build()


if __name__ == "__main__":
    main()
