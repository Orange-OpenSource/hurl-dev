#!/usr/bin/env python3
import sys
import json
import re
from pathlib import Path
from typing import List, Optional, Any, Dict

from bs4 import BeautifulSoup, Tag


# This script build an JSON index so the documentation search can be
# executed locally in the browser.
# The index structure:
# - hits: a dictionary of indexed searched token.
# Each hits contains a list of reference.
# Example
# "hits": {
#    "add": [512, 123],
#    "adde": [512],
#    "added": [512],
#    ...
# - refs: a list of search results, referenced by the hits entry.
# Refs structure:
# - refs
#   - anchor
#   - anchor
#   - content
#   - page
#   - search
#   - start
# - pages: a list of page, referenced by the hits entry.
# Page structure:
# - pages
#   - section
#   - title
#   - url
# - anchors: a list of anchors, referenced by the hits entry.
# Anchor structure:
# - anchor
#   - title
#   - url
class Anchor:
    title: str
    url: str
    index: int

    def __init__(self, title: str, url: str, index: int) -> None:
        self.title = title
        self.url = url
        self.index = index

    def to_json(self):
        return {"title": self.title, "url": self.url}


class Anchors:
    anchors: List[Anchor]

    def __init__(self) -> None:
        self.anchors = []

    def get_or_create_anchor(self, title, url) -> Optional[Anchor]:
        for a in self.anchors:
            if a.title == title and a.url == url:
                return a
        anchor = Anchor(title=title, url=url, index=len(self.anchors))
        self.anchors.append(anchor)
        return anchor


class Page:
    title: str
    section: str
    url: str
    index: int
    path: Path
    soup: BeautifulSoup

    def __init__(
        self,
        title: str,
        section: str,
        url: str,
        index: int,
        path: Path,
        soup: BeautifulSoup,
    ) -> None:
        self.title = title
        self.section = section
        self.url = url
        self.index = index
        self.path = path
        self.soup = soup

    def to_json(self):
        return {"title": self.title, "section": self.section, "url": self.url}


class Token:
    search: str
    page: Page
    anchor: Anchor
    content: str
    start: int

    def __init__(
        self, search: str, page: Page, anchor: Anchor, content: str, start: int
    ) -> None:
        self.search = search
        self.page = page
        self.anchor = anchor
        self.content = content
        self.start = start

    def __str__(self) -> str:
        return f"Token(search={self.search} anchor_url={self.anchor.url} anchor_title={self.anchor.title}"

    def to_json(self):
        return {
            "search": self.search,
            "page": self.page.index,
            "anchor": self.anchor.index,
            "content": self.content,
            "start": self.start,
        }


def build_page(path: Path) -> Optional[Page]:
    """Construct a page from a path"""
    soup = BeautifulSoup(path.read_text(), "html.parser")
    try:
        title = soup.title.text
    except AttributeError:
        sys.stderr.write(f"Error in path {path}\n")
        raise
    relative_path = path.relative_to("hurl.dev/_site/")
    url: str
    if str(relative_path) == "index.html":
        url = "/"
    else:
        url = f"/{relative_path}"

    indexed = next(
        (tag for tag in soup.find_all("div", attrs={"data-indexed": True})), None
    )
    if not indexed:
        sys.stderr.write(f"No indexed content in path {path}\n")
        return None

    section = next(
        (
            tag["data-section"]
            for tag in soup.find_all("div", attrs={"data-section": True})
        )
    )
    return Page(title=title, section=section, url=url, index=0, path=path, soup=soup)


def build_file_index(page: Page, anchors: Anchors) -> List[Token]:
    """Construct an index from html file."""
    # On construit une représentation textuelle de la page
    # en agrégeant tous les tags contenant du text "significatif"
    tags: List[Tag] = []
    root = next(
        (tag for tag in page.soup.find_all("div", attrs={"data-indexed": True})), None
    )
    if not root:
        sys.stderr.write(f"No indexed content in path {page.path}\n")
        return []
    tags.extend(root.find_all("p"))
    tags.extend(root.find_all("td"))
    tags.extend(root.find_all("ul"))
    tags.extend(root.find_all("h2"))
    tags.extend(root.find_all("h3"))
    tags.extend(root.find_all("h4"))

    tokens = [build_tag_index(page=page, tag=tag, anchors=anchors) for tag in tags]
    return flatten(tokens)


non_significant_words = [
    "all",
    "also",
    "and",
    "any",
    "are",
    "both",
    "but",
    "can",
    "doc",
    "does",
    "etc",
    "for",
    "from",
    "has",
    "have",
    "into",
    "one",
    "only",
    "let",
    "may",
    "say",
    "see",
    "set",
    "the",
    "this",
    "than",
    "that",
    "use",
    "yet",
    "you",
    "very",
    "when",
    "will",
    "with",
]


def build_tag_index(page: Page, tag: Tag, anchors: Anchors) -> List[Token]:
    """Build search tokens from a p tag."""
    anchor_tag = find_anchor(tag)
    anchor_url: str
    anchor_title: str
    if anchor_tag:
        anchor_id = anchor_tag["id"]
        anchor_url = f"{page.url}#{anchor_id}"
        anchor_title = anchor_tag.text
    else:
        anchor_url = page.url
        anchor_title = page.title
    anchor = anchors.get_or_create_anchor(anchor_title, anchor_url)

    # Iterate over each word and construct indices
    text = tag.text
    text = text.replace(" \n", " ")
    text = text.replace("\n", " ")

    span = 120
    tokens: List[Token] = []
    for res in re.finditer(r"\w+", text):
        match = res[0]
        if len(match) < 3 or match.lower() in non_significant_words:
            continue
        # if len(match) == 4:
        #    sys.stderr.write(f"-> {match}\n")

        start = res.start()
        end = res.end()
        if start < span:
            content_before = text[:start]
        else:
            content_before = "..." + text[start - span : start]
        if (len(text) - end) < span:
            content_after = text[end:]
        else:
            content_after = text[end : end + span] + "..."
        content = content_before + match + content_after
        token = Token(
            search=match.lower(),
            page=page,
            anchor=anchor,
            content=content,
            start=len(content_before),
        )
        tokens.append(token)
    return tokens


def find_anchor(tag: Optional[Any]) -> Optional[Tag]:
    # Special case for options:
    if isinstance(tag, Tag) and tag.name == "td":
        child = tag.a
        if child and child.get("id"):
            return child

    if isinstance(tag, Tag) and tag.get("id"):
        return tag
    else:
        if tag.previous_sibling:
            return find_anchor(tag.previous_sibling)
        elif tag.parent:
            return find_anchor(tag.parent)
        else:
            return None


def split(word: str, start: int):
    return [word[:end] for end in range(start, len(word) + 1)]


def flatten(list_of_lists):
    flatten_list = []
    for l in list_of_lists:
        flatten_list.extend(l)
    return flatten_list


def serialize(pages: List[Page], tokens: List[Token], anchors: Anchors) -> str:

    hits: Dict[str, List[int]] = {}

    pages_json = [p.to_json() for p in pages]

    tokens_json = [t.to_json() for t in tokens]

    anchors_json = [a.to_json() for a in anchors.anchors]

    # Pour chaque hit, on construit une liste de reférences
    for i, token in enumerate(tokens):
        words = split(word=token.search, start=3)
        for w in words:
            hr = hits.get(w)
            if hr:
                hr.append(i)
            else:
                hr = [i]
            hits[w] = hr

    d = {
        "hits": hits,
        "refs": tokens_json,
        "pages": pages_json,
        "anchors": anchors_json,
    }
    return json.dumps(d, default=lambda o: o.__dict__, sort_keys=True)


def main():
    sys.stderr.write("Building search index...\n")

    site = Path("hurl.dev/_site")
    files = list(site.glob("**/*.html"))

    anchors = Anchors()
    pages = [build_page(path=f) for index, f in enumerate(files)]
    pages = [p for p in pages if p]
    for index, p in enumerate(pages):
        p.index = index

    tokens = flatten([build_file_index(page, anchors) for page in pages])
    index = serialize(pages=pages, tokens=tokens, anchors=anchors)
    print(index)


if __name__ == "__main__":
    main()
