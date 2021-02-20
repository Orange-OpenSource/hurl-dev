#!/usr/bin/env python3

from pathlib import Path
from typing import Optional

import sys
from bs4 import BeautifulSoup, NavigableString

class Option:
    def __init__(self, id_, name) -> None:
        self.contents = []
        self.id_ = id_
        self.name = name


def main(man_page: Path) -> Optional[str]:
    sys.stderr.write("Building options table...\n")
    soup = BeautifulSoup(man_page.read_text(), "html.parser")

    h2_old = soup.find(id="options")
    options = []    # Options that are build and identified
    tags = []       # All tags to remove from the dom

    # TODO: see how to keep the first p after the h2 option header
    #  which are not options
    cur = h2_old
    if not cur:
        sys.stderr.write("No h2 options...\n")
        return None
    while cur.name != "h3":
        tags.append(cur)
        cur = cur.nextSibling

    # First construct a list of option name and description

    while cur:
        #if isinstance(cur, NavigableString):
        #    tags.append(cur)
        #    cur = cur.next_sibling
        #   continue
        if cur.name == "h2":
            break
        if cur.name == "h3":
            id_ = cur.get("id")
            name = cur.text
            option = Option(id_, name)
            options.append(option)
        if cur.name == "p":
            if len(option.contents):
                option.contents.append(soup.new_tag("br"))
                option.contents.append(soup.new_tag("br"))
            option.contents.extend(cur.contents)
        tags.append(cur)
        cur = cur.next_sibling

    if not len(options):
        sys.stderr.write("No options to process...\n")
        return None

    tbody = soup.new_tag("tbody")
    for option in options:
        tr = soup.new_tag("tr")
        td0 = soup.new_tag("td")
        a = soup.new_tag("a", id=option.id_, href=f"#{option.id_}")
        code = soup.new_tag("code")
        code.append(option.name)
        a.append(code)
        td0.append(a)
        tr.append(td0)
        td1 = soup.new_tag("td")
        [td1.append(c) for c in option.contents]
        tr.append(td1)
        tbody.append(tr)

    h2_html = f"""
<h2 id="options">OPTIONS</h2>

<p>Options that exist in curl have exactly the same semantic.</p>

<table>
    <thead>
        <tr>
            <th>Option</th>
            <th>Description</th>
        </tr>
    </thead>
    {tbody}
</table>
    """
    h2_new = BeautifulSoup(h2_html, "html.parser")
    h2_old.replace_with(h2_new)
    [t.extract() for t in tags]
    return str(soup)


if __name__ == "__main__":
    man_page = Path("hurl.dev/_site/docs/man-page.html")
    content = main(man_page)
    if content:
        man_page.write_text(content)
