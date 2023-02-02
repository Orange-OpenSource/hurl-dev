import re
from typing import List, Optional

from parser import Parser


class Node:
    content: Optional[str]

    def __init__(self, content: Optional[str]) -> None:
        self.content = content


class Code(Node):
    pass


class Paragraph(Node):
    pass


class Whitespace(Node):
    pass


def build_header(title: str, level: int) -> str:
    hashes = "#" * level
    return f"{hashes} {title}\n"


class Header(Node):
    title: str
    level: int

    def __init__(self, title: str, level: int) -> None:
        super().__init__(content=None)
        self.title = title
        self.level = level
        self.update_content()

    def indent(self, count: int) -> str:
        self.level += count
        self.update_content()

    def update_content(self):
        self.content = build_header(title=self.title, level=self.level)


class RefLink(Node):
    ref: str
    link: str

    def __init__(self, ref: str, link: str) -> None:
        super().__init__(content=None)
        self.ref = ref
        self.link = link
        self.update_content()

    def update_content(self):
        self.content = f"[{self.ref}]: {self.link}\n"


def parse_paragraph(parser: Parser) -> Paragraph:
    content = ""
    while parser.peek() != "":
        if parser.peek() == "\n":
            content += parser.read()
            line = parser.peek_while(lambda it: it != "\n")
            if is_blank(line):
                return Paragraph(content=content)
            continue
        content += parser.read()
    return Paragraph(content=content)


def is_blank(line: str) -> bool:
    for c in line:
        if not is_whitespace(c):
            return False
    return True


def is_whitespace(c: str) -> bool:
    return c == " " or c == "\t" or c == "\n"


def parse_whitespace(parser: Parser) -> Whitespace:
    content = parser.read_while(is_whitespace)
    return Whitespace(content=content)


def parse_code(parser: Parser) -> Code:
    separator = parser.read(3)
    content = separator

    while parser.peek() != "":
        c = parser.peek(3)
        if c == separator:
            content += parser.read(3)
            return Code(content=content)
        content += parser.read()
    return Code(content=content)


def parse_header(parser: Parser) -> Header:
    hashes = parser.read_while(lambda it: it == "#")
    _ = parser.read_while(lambda it: is_whitespace(it))
    title = parser.read_while(lambda it: it != "\n")
    _ = parser.read()
    return Header(title=title, level=len(hashes))


def parse_ref_link(parser: Parser) -> RefLink:
    line = parser.read_while(lambda it: it != "\n")
    _ = parser.read()
    ret = re.match(r"\[(?P<ref>.+)]:\s+(?P<link>.+)", line)
    return RefLink(ref=ret.group("ref"), link=ret.group("link"))


def parse_markdown(text: str) -> "MarkdownDoc":
    processed_text = text
    parser = Parser(buffer=processed_text)

    root = MarkdownDoc()

    while parser.peek() != "":
        c = parser.peek()

        # Whitespace parsing:
        if is_whitespace(c):
            node = parse_whitespace(parser=parser)
            root.add_child(node)
            continue

        # Code parsing:
        if c == "-" or c == "~" or c == "`":
            sep = parser.peek(3)
            if sep in ("---", "~~~", "```"):
                node = parse_code(parser=parser)
                root.add_child(node)
                continue

        # Header parsing:
        if c == "#":
            node = parse_header(parser=parser)
            root.add_child(node)
            continue

        # Parse Reference-style Links
        if c == "[":
            line = parser.peek_while(lambda it: it != "\n")
            if re.match(r"\[.+]: .+", line):
                node = parse_ref_link(parser=parser)
                root.add_child(node)
                continue

        # Default node parsing:
        node = parse_paragraph(parser=parser)
        root.add_child(node)

    return root


class MarkdownDoc:
    children: List[Node]

    def __init__(self) -> None:
        self.children = []

    def add_child(self, node) -> None:
        self.children.append(node)

    def find_first(self, func, start: Optional[Node] = None) -> Optional[Node]:
        if start:
            start_index = self.children.index(start)
        else:
            start_index = 0
        for child in self.children[start_index:]:
            if func(child):
                return child
        return None

    def to_text(self) -> str:
        ref_links_nodes = [c for c in self.children if isinstance(c, RefLink)]
        other_nodes = [c for c in self.children if not isinstance(c, RefLink)]
        nodes = [*other_nodes, *ref_links_nodes]
        return "".join([node.content for node in nodes])

    def indent(self, count: int = 1):
        [c.indent(count=count) for c in self.children if isinstance(c, Header)]

    def extend(self, other: "MarkdownDoc") -> None:
        self.children.extend(other.children)

    def insert_node(self, start: Node, node: Node) -> None:
        index = self.children.index(start)
        self.children.insert(index, node)

    def insert_nodes(self, start: Node, nodes: List[Node]) -> None:
        index = self.children.index(start)
        self.children[index:index] = nodes

    def remove_node(self, node: Node) -> None:
        try:
            index = self.children.index(node)
            self.children.pop(index)
        except ValueError:
            pass

    def remove_nodes(self, nodes: List[Node]) -> None:
        self.children = [node for node in self.children if node not in nodes]

    def slice(self, node_a: Node, node_b: Node) -> List[Node]:
        index_a = self.children.index(node_a)
        index_b = self.children.index(node_b)
        return self.children[index_a:index_b]

    def next_node(self, node: Node) -> Node:
        index = self.children.index(node)
        return self.children[index + 1]

    def previous_node(self, node: Node) -> Node:
        index = self.children.index(node)
        return self.children[index - 1]
