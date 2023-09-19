#!/usr/bin/env python3
"""Generate an <entry> RSS tag for a Markdown blog post source file.

Examples:
    $ python3 hurl.dev/_posts/2023-06-30-announcing-hurl-4.0.0.md
"""
from _datetime import datetime
import re
import sys
from pathlib import Path
from lxml.etree import Element, CDATA
from lxml import etree as ElementTree
from typing import Optional
import markdown
import pytz


class Post:
    """Represents a Markdown source blog post."""

    title: str
    publication_date: datetime
    slug: str
    html: str

    def __init__(self, md: Path) -> None:
        # Parsing of the publication date
        m = re.match(
            r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})-(?P<name>.*)", md.stem
        )
        if m:
            year = int(m.group("year"))
            month = int(m.group("month"))
            day = int(m.group("day"))
            name = m.group("name")
            publication_date_naive = datetime(year=year, month=month, day=day)
            self.publication_date = pytz.timezone("Europe/Paris").localize(
                publication_date_naive
            )
        else:
            raise ValueError("Unable to parse date")

        # Parsing of the Markdown content
        md_txt = md.read_text(encoding="utf-8")
        m = re.search(r"title: (?P<title>.*?)\n", md_txt, flags=re.DOTALL)
        if m:
            self.title = m.group("title")
        else:
            raise ValueError("Unable to parse title")

        # Remove Frontmatter header
        md_txt = re.sub(r"(---.*?---)", "", md_txt, flags=re.DOTALL, count=1)
        md_txt = md_txt.strip()

        # Remove controls char from shells snippets
        md_txt = re.sub(r"\[\d+(;\d+)?m", "", md_txt)

        # Process Jekyll tag
        md_txt = md_txt.replace("{{ page.title }}", self.title)
        md_txt = md_txt.replace(
            '{{ page.date | date: "%b. %d, %Y" }}',
            self.publication_date.strftime("%b. %d, %Y"),
        )
        md_txt = re.sub(
            r"\{\{ '(.*?)' \| prepend:site.baseurl }}", r"https://hurl.dev\1", md_txt
        )
        md_txt = re.sub(
            r"\{% link _docs/(.*).md %}", r"https://hurl.dev/docs\1.html", md_txt
        )

        # Construct the HTML content
        self.html = markdown.markdown(md_txt, extensions=["fenced_code", "smarty"])

        # Normalize some HTML entities
        self.html = self.html.replace("&rsquo;", "’")
        self.html = self.html.replace("&quot;", '"')
        self.html = self.html.replace("&hellip;", "...")

        self.slug = f"https://hurl.dev/blog/{year:04}/{month:02}/{day:02}/{name}.html"

    def __repr__(self):
        return f"Post('{self.title}', {self.publication_date}, '{self.slug}')"


def new_element(tag: str, text) -> Element:
    """Creates a new XLM tag with an inner context."""
    elt = Element(tag)
    elt.text = text
    return elt


class Link:
    """Represents a link tag in RSS format"""

    href: str
    rel: str
    type_: str
    title: Optional[str]

    def __init__(self, href: str, rel: str, type_: str, title=Optional[str]) -> None:
        self.href = href
        self.rel = rel
        self.type_ = type_
        self.title = title

    def to_elem(self) -> Element:
        attrib = {"href": self.href, "rel": self.rel, "type": self.type_}
        if self.title:
            attrib["title"] = self.title
        return Element("link", attrib=attrib)


class Entry:
    """Represents an entry tag in RSS format"""

    title: str
    link: Link
    publication_date: datetime
    id_: str
    html: str

    def __init__(self, post: Post) -> None:
        self.title = post.title
        self.link = Link(
            href=post.slug, rel="alternate", type_="text/html", title=post.title
        )
        self.publication_date = post.publication_date
        self.id_ = post.slug
        self.html = post.html

    def to_elem(self) -> Element:
        entry = Element("entry")
        title = new_element("title", self.title)
        entry.append(title)

        link = self.link.to_elem()
        entry.append(link)

        published = new_element("published", self.publication_date.isoformat())
        entry.append(published)
        updated = new_element("updated", self.publication_date.isoformat())
        entry.append(updated)

        id_ = new_element("id", self.id_)
        entry.append(id_)

        content = Element("content", {"type": "html"})
        # We remove control char from Shell snippet
        content.text = CDATA(self.html)
        entry.append(content)

        author = Element("author")
        ElementTree.SubElement(author, "name")
        entry.append(author)

        summary = Element("summary")
        entry.append(summary)

        return entry

    def to_xml(self) -> str:
        """Format this entry tag to an XML indented string."""
        entry = self.to_elem()
        ElementTree.indent(entry, space="    ")
        xml = ElementTree.tostring(entry, encoding="utf-8", xml_declaration=False)
        txt = xml.decode("utf-8")
        return txt


def build(path: Path) -> str:
    post = Post(md=path)
    entry = Entry(post=post)
    return entry.to_xml()


if __name__ == "__main__":
    ret = build(path=Path(sys.argv[1]))
    print(ret)
