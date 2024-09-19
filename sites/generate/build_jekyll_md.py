#!/usr/bin/env python3
"""Build hurl.dev Jekyll site from Hurl canonical docs.

This script use Hurl canonical docs to build a Jekyll powered site.

Each Markdown file form the canonical is transformed:

- insert a FrontMatter header for Jekyll
- Hurl code snippets are escaped for Jekyll
- Local links are converted to Jekyll Links

Examples:
    $ python3 sites/generate/build_jekyll_md.py
"""
import re
import gzip
import shutil
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
    title: Optional[str]
    description: Optional[str]
    indexed: Optional[bool]

    def __init__(
        self,
        layout: str,
        section: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        indexed: Optional[bool] = None,
    ):
        self.layout = layout
        self.section = section
        self.title = title
        self.description = description
        self.indexed = indexed


def canonical_to_jekyll(local_path: str) -> str:
    """Returns a Jekyll path from a local path"""
    match = re.match(r"(?P<base>.+\.md)#?(?P<anchor>.*)", local_path)
    base = match.group("base")
    anchor = match.group("anchor")

    # Transform absolute path to Jekyll relatives path:
    base = base.replace("/docs/", "_docs/")
    if anchor:
        return f"{{% link {base} %}}#{anchor}"
    else:
        return f"{{% link {base} %}}"


def process_canonical_link(match) -> str:
    local_link = match.group("link")
    jekyll_link = canonical_to_jekyll(local_link)
    title = match.group("title")
    return f"[{title}]({jekyll_link})"


def convert_to_jekyll(
    path: Path, front_matter: FrontMatter, force_list_numbering: bool = False
) -> str:
    text = path.read_text()

    md_raw = parse_markdown(text)
    md_escaped = MarkdownDoc()

    # Extract title from source to inject it in the front matter header:
    if front_matter.title:
        title = front_matter.title
    else:
        h1s = (f for f in md_raw.children if isinstance(f, Header) and f.level == 1)
        h1 = next(h1s)
        title = h1.title

    # Construct front matter header:
    header = "---\n"
    header += f"layout: {front_matter.layout}\n"
    header += f"title: {title}\n"
    if front_matter.description:
        header += f"description: {front_matter.description}\n"
    header += f"section: {front_matter.section}\n"
    if front_matter.indexed is not None:
        header += f"indexed: {str(front_matter.indexed).lower()}\n"
    header += "---\n"
    header_node = Paragraph(content=header)
    whitespace_node = Whitespace(content="\n")
    md_escaped.add_child(header_node)
    md_escaped.add_child(whitespace_node)

    for node in md_raw.children:
        if (
            isinstance(node, Code)
            and re.match(r"(```|~~~)", node.content)  # Code block
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
            content = re.sub(r"(`.*\{\{.+}}.*`)", r"{% raw %}\1{% endraw %}", content)

            # If paragraph content is raw html, escape if it contains Hurl template
            if content.startswith("<div") and "{{" in content:
                content = f"{{% raw  %}}\n{content}{{% endraw %}}"

            # Convert local links to Jekyll link
            content = re.sub(
                r"\[(?P<title>.+)]\((?P<link>/.+\.md#?.*)\)",
                process_canonical_link,
                content,
            )

            # Convert canonical image to jekyll
            content = re.sub(
                r'''<img (.*)src="/docs/([a-z/\-.]+)"''',
                r'''<img \1src="{{ '/\2' | prepend:site.baseurl }}"''',
                content,
            )
            content = re.sub(
                r'''<source srcset="/docs/([a-z/\-.]+)"''',
                r'''<source srcset="{{ '/\1' | prepend:site.baseurl }}"''',
                content,
            )

            # Optionally force list number to be respected, because kramdown is resetting list when they're not
            # made of consecutive items.
            if force_list_numbering:
                content = re.sub(
                    r"^(\d+)\.", r'{:start="\1"}\n\1.', content, flags=re.MULTILINE
                )

            p_node = Paragraph(content=content)
            md_escaped.add_child(p_node)
        elif (
            isinstance(node, RefLink)
            and ".md" in node.link
            and not node.link.startswith("http")
        ):
            # Convert local reference links to Jekyll reference link
            ret = re.match(r"(.+\.md#?.*)", node.link)
            canonical_link = ret.group(1)
            jekyll_link = canonical_to_jekyll(canonical_link)
            ref_link = RefLink(ref=node.ref, link=jekyll_link)
            md_escaped.add_child(ref_link)
        else:
            md_escaped.add_child(node)

    return md_escaped.to_text()


class ConvertTask:
    file_src: Path
    file_dst: Path
    front_matter: FrontMatter
    force_list_numbering: bool

    def __init__(
        self,
        file_src: Path,
        file_dst: Path,
        front_matter: FrontMatter,
        force_list_numbering: bool,
    ) -> None:
        self.file_src = file_src
        self.file_dst = file_dst
        self.front_matter = front_matter
        self.force_list_numbering = force_list_numbering

    def convert(self):
        md = convert_to_jekyll(
            path=self.file_src,
            front_matter=self.front_matter,
            force_list_numbering=self.force_list_numbering,
        )
        self.file_dst.write_text(md)


def build():
    docs = [
        (
            Path("../hurl/docs/home.md"),
            Path("sites/hurl.dev/index.md"),
            FrontMatter(
                layout="home",
                section="Home",
                title="Hurl - Run and Test HTTP Requests",
                description="Hurl, run and test HTTP requests with plain text and curl. Hurl can run fast automated integration tests.",
            ),
            False,
        ),
        (
            Path("../hurl/docs/installation.md"),
            Path("sites/hurl.dev/_docs/installation.md"),
            FrontMatter(
                layout="doc",
                section="Getting Started",
                description="How to install or build Hurl on Linux, macOS and Windows platform.",
            ),
            False,
        ),
        (
            Path("../hurl/docs/manual.md"),
            Path("sites/hurl.dev/_docs/manual.md"),
            FrontMatter(
                layout="doc",
                section="Getting Started",
                description="Hurl command line usage, with options descriptions.",
            ),
            False,
        ),
        (
            Path("../hurl/docs/samples.md"),
            Path("sites/hurl.dev/_docs/samples.md"),
            FrontMatter(
                layout="doc",
                section="Getting Started",
                description="Various Hurl samples to show how to run and tests HTTP requests and responses.",
            ),
            False,
        ),
        (
            Path("../hurl/docs/running-tests.md"),
            Path("sites/hurl.dev/_docs/running-tests.md"),
            FrontMatter(
                layout="doc",
                section="Getting Started",
                description="How to run multiple tests with run and generate an HTML report.",
            ),
            False,
        ),
        (
            Path("../hurl/docs/frequently-asked-questions.md"),
            Path("sites/hurl.dev/_docs/frequently-asked-questions.md"),
            FrontMatter(layout="doc", section="Getting Started"),
            False,
        ),
        (
            Path("../hurl/docs/grammar.md"),
            Path("sites/hurl.dev/_docs/grammar.md"),
            FrontMatter(layout="doc", section="File Format"),
            False,
        ),
        (
            Path("../hurl/docs/hurl-file.md"),
            Path("sites/hurl.dev/_docs/hurl-file.md"),
            FrontMatter(layout="doc", section="File Format"),
            False,
        ),
        (
            Path("../hurl/docs/entry.md"),
            Path("sites/hurl.dev/_docs/entry.md"),
            FrontMatter(layout="doc", section="File Format"),
            False,
        ),
        (
            Path("../hurl/docs/request.md"),
            Path("sites/hurl.dev/_docs/request.md"),
            FrontMatter(layout="doc", section="File Format"),
            False,
        ),
        (
            Path("../hurl/docs/response.md"),
            Path("sites/hurl.dev/_docs/response.md"),
            FrontMatter(layout="doc", section="File Format"),
            False,
        ),
        (
            Path("../hurl/docs/capturing-response.md"),
            Path("sites/hurl.dev/_docs/capturing-response.md"),
            FrontMatter(layout="doc", section="File Format"),
            False,
        ),
        (
            Path("../hurl/docs/asserting-response.md"),
            Path("sites/hurl.dev/_docs/asserting-response.md"),
            FrontMatter(layout="doc", section="File Format"),
            False,
        ),
        (
            Path("../hurl/docs/filters.md"),
            Path("sites/hurl.dev/_docs/filters.md"),
            FrontMatter(layout="doc", section="File Format"),
            False,
        ),
        (
            Path("../hurl/docs/templates.md"),
            Path("sites/hurl.dev/_docs/templates.md"),
            FrontMatter(
                layout="doc",
                section="File Format",
                description="Hurl file format variables and templating.",
            ),
            False,
        ),
        (
            Path("../hurl/docs/grammar.md"),
            Path("sites/hurl.dev/_docs/grammar.md"),
            FrontMatter(layout="doc", section="File Format"),
            False,
        ),
        (
            Path("../hurl/docs/tutorial/your-first-hurl-file.md"),
            Path("sites/hurl.dev/_docs/tutorial/your-first-hurl-file.md"),
            FrontMatter(
                layout="doc",
                section="Tutorial",
                description="A tutorial to learn how to use Hurl to test REST API and HTML responses.",
            ),
            True,
        ),
        (
            Path("../hurl/docs/tutorial/adding-asserts.md"),
            Path("sites/hurl.dev/_docs/tutorial/adding-asserts.md"),
            FrontMatter(layout="doc", section="Tutorial"),
            True,
        ),
        (
            Path("../hurl/docs/tutorial/chaining-requests.md"),
            Path("sites/hurl.dev/_docs/tutorial/chaining-requests.md"),
            FrontMatter(layout="doc", section="Tutorial"),
            True,
        ),
        (
            Path("../hurl/docs/tutorial/debug-tips.md"),
            Path("sites/hurl.dev/_docs/tutorial/debug-tips.md"),
            FrontMatter(layout="doc", section="Tutorial"),
            True,
        ),
        (
            Path("../hurl/docs/tutorial/captures.md"),
            Path("sites/hurl.dev/_docs/tutorial/captures.md"),
            FrontMatter(layout="doc", section="Tutorial"),
            True,
        ),
        (
            Path("../hurl/docs/tutorial/security.md"),
            Path("sites/hurl.dev/_docs/tutorial/security.md"),
            FrontMatter(layout="doc", section="Tutorial"),
            True,
        ),
        (
            Path("../hurl/docs/tutorial/ci-cd-integration.md"),
            Path("sites/hurl.dev/_docs/tutorial/ci-cd-integration.md"),
            FrontMatter(layout="doc", section="Tutorial"),
            True,
        ),
        (
            Path("../hurl/docs/index.md"),
            Path("sites/hurl.dev/_docs/index.md"),
            FrontMatter(layout="doc", section="Documentation", indexed=False),
            False,
        ),
        (
            Path("../hurl/docs/tutorial/index.md"),
            Path("sites/hurl.dev/_docs/tutorial/index.md"),
            FrontMatter(layout="doc", section="Tutorial", indexed=False),
            False,
        ),
        (
            Path("../hurl/docs/license.md"),
            Path("sites/hurl.dev/_docs/license.md"),
            FrontMatter(layout="doc", section="Resources"),
            False,
        ),
        (
            Path("../hurl/docs/standalone/hurl-5.0.1.md"),
            Path("sites/hurl.dev/_docs/standalone/hurl-5.0.1.md"),
            FrontMatter(
                layout="standalone",
                section="Standalone",
                title="Hurl 5.0.1",
                indexed=False,
            ),
            False,
        ),
    ]

    for src, dst, front_matter, force_list_numbering in docs:
        task = ConvertTask(
            file_src=src,
            file_dst=dst,
            front_matter=front_matter,
            force_list_numbering=force_list_numbering,
        )
        task.convert()

    shutil.copy(
        "../hurl/docs/assets/img/github-action-dark.png",
        "sites/hurl.dev/assets/img/github-action-dark.png",
    )
    shutil.copy(
        "../hurl/docs/assets/img/github-action-light.png",
        "sites/hurl.dev/assets/img/github-action-light.png",
    )
    shutil.copy(
        "../hurl/docs/assets/img/github-new-repository-dark.png",
        "sites/hurl.dev/assets/img/github-new-repository-dark.png",
    )
    shutil.copy(
        "../hurl/docs/assets/img/github-new-repository-light.png",
        "sites/hurl.dev/assets/img/github-new-repository-light.png",
    )
    shutil.copy(
        "../hurl/docs/assets/img/hurl-html-file.png",
        "sites/hurl.dev/assets/img/hurl-html-file.png",
    )
    shutil.copy(
        "../hurl/docs/assets/img/hurl-html-report.png",
        "sites/hurl.dev/assets/img/hurl-html-report.png",
    )
    shutil.copy(
        "../hurl/docs/assets/img/logo-dark.svg",
        "sites/hurl.dev/assets/img/logo-dark.svg",
    )
    shutil.copy(
        "../hurl/docs/assets/img/logo-light.svg",
        "sites/hurl.dev/assets/img/logo-light.svg",
    )
    shutil.copy(
        "../hurl/docs/assets/img/quiz-dark.png",
        "sites/hurl.dev/assets/img/quiz-dark.png",
    )
    shutil.copy(
        "../hurl/docs/assets/img/quiz-light.png",
        "sites/hurl.dev/assets/img/quiz-light.png",
    )
    compress(src=Path("../hurl/docs/standalone/hurl-5.0.1.md"))
    shutil.move(
        "../hurl/docs/standalone/hurl-5.0.1.md.gz",
        "sites/hurl.dev/assets/docs/hurl-5.0.1.md.gz",
    )
    compress(src=Path("../hurl/docs/standalone/hurl-5.0.1.html"))
    shutil.move(
        "../hurl/docs/standalone/hurl-5.0.1.html.gz",
        "sites/hurl.dev/assets/docs/hurl-5.0.1.html.gz",
    )
    compress(src=Path("../hurl/docs/standalone/hurl-5.0.1.pdf"))
    shutil.move(
        "../hurl/docs/standalone/hurl-5.0.1.pdf.gz",
        "sites/hurl.dev/assets/docs/hurl-5.0.1.pdf.gz",
    )


def compress(src: Path):
    with src.open("rb") as f_in:
        with gzip.open(str(src) + ".gz", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def main():
    build()


if __name__ == "__main__":
    main()
