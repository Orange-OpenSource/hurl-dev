#!/usr/bin/env python3
import sys
import json
import re
from pathlib import Path
from typing import List, Optional, Any, Dict

from bs4 import BeautifulSoup, Tag


class Hit:
    search: str
    title: str
    anchor: str
    content: str
    start: int

    def __init__(self,
                 search: str,
                 page_url: str,
                 page_title: str,
                 anchor_url: str,
                 anchor_title: str,
                 content: str,
                 start: int) -> None:
        self.search = search
        self.page_url = page_url
        self.page_title = page_title
        self.anchor_url = anchor_url
        self.anchor_title = anchor_title
        self.content = content
        self.start = start

    def __str__(self) -> str:
        return f"Hit(search={self.search} anchor_url={self.anchor_url} anchor_title={self.anchor_title}"


def build_file_index(f: Path) -> List[Hit]:
    """Construct an index from html file."""
    soup = BeautifulSoup(f.read_text(), "html.parser")
    try:
        title = soup.title.text
    except AttributeError:
        sys.stderr.write(f"Error in path {f}\n")
        raise
    relative_path = f.relative_to("hurl.dev/_site/")
    url: str
    if str(relative_path) == "index.html":
        url = "/"
    else:
        url = f"/{relative_path}"

    # On construit une représentation textuelle de la page
    # en agrégeant tous les tags contenant du text "significatif"
    all_hits: List[Hit] = []
    all_tags: List[Tag] = []
    root = soup.find("div", class_=re.compile("content"))
    all_tags.extend(root.find_all("p"))
    all_tags.extend(root.find_all("ul"))
    all_tags.extend(root.find_all("h2"))
    all_tags.extend(root.find_all("h3"))
    all_tags.extend(root.find_all("h4"))

    for tag in all_tags:
        hits = build_tag_index(url=url, title=title, soup=soup, tag=tag)
        all_hits.extend(hits)
    return all_hits


def build_tag_index(url: str, title: str, soup: BeautifulSoup, tag: Tag) -> List[Hit]:
    """Build serach hit from a p tag."""
    anchor_tag = find_anchor(tag)
    anchor_url: str
    anchor_title: str
    if anchor_tag:
        anchor_id = anchor_tag["id"]
        anchor_url = f"{url}#{anchor_id}"
        anchor_title = anchor_tag.text
    else:
        anchor_url = url
        anchor_title = title

    # Iterate over each word and construct indices
    text = tag.text
    text = text.replace(" \n", " ")
    text = text.replace("\n", " ")

    span = 120
    hits: List[Hit] = []
    for res in re.finditer(r"\w+", text):
        match = res[0]
        if len(match) < 3:
            continue
        start = res.start()
        end = res.end()
        if start < span:
            content_before = text[:start]
        else:
            content_before = "..." + text[start-span:start]
        if (len(text) - end) < span:
            content_after = text[end:]
        else:
            content_after = text[end:end+span] + "..."
        content = content_before + match + content_after
        hit = Hit(
            search=match.lower(),
            page_url=url,
            page_title=title,
            anchor_url=anchor_url,
            anchor_title=anchor_title,
            content=content,
            start=len(content_before)
        )
        hits.append(hit)
    return hits


def find_anchor(tag: Optional[Any]) -> Optional[Tag]:
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
    return [word[:end] for end in range(start, len(word)+1)]


def serialize_hits(hits: List[Hit]) -> str:

    hits_refs: Dict[str, List[int]] = {}

    # Pour chaque hit, on construit une list de
    for i in range(0, len(hits)):
        h = hits[i]
        words = split(h.search, 3)
        for w in words:
            hr = hits_refs.get(w)
            if hr:
                hr.append(i)
            else:
                hr = [i]
            hits_refs[w] = hr

    d = {"hits": hits_refs, "refs": hits}
    return json.dumps(d, default=lambda o: o.__dict__, sort_keys=True)


def main():
    sys.stderr.write("Building search index...\n")

    site = Path("hurl.dev/_site")
    files = list(site.glob("**/*.html"))
    all_hits: List[Hit] = []
    for f in files:
        hits = build_file_index(f)
        all_hits.extend(hits)
    index = serialize_hits(all_hits)
    print(index)


if __name__ == "__main__":
    main()
