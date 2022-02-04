#!/usr/bin/env python3
from pathlib import Path
from typing import List, Optional
import re
import sys
from parser import Parser


class Token:
    value: str

    def __init__(self, value: str) -> None:
        self.value = value

    def to_html(self):
        return f"{self.value}"


class BeginGroup(Token):
    def __init__(self) -> None:
        super().__init__("(")


class EndGroup(Token):
    def __init__(self) -> None:
        super().__init__(")")


class Equal(Token):
    def __init__(self) -> None:
        super().__init__("=")

    def to_html(self) -> str:
        return f'<div class="associate">{self.value}</div>'


class Cardinality(Token):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class Or(Token):
    def __init__(self) -> None:
        super().__init__("|")


class Comment(Token):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class Terminal(Token):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class NonTerminal(Token):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class Definition(Token):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class Follow(Token):
    def __init__(self) -> None:
        super().__init__(" ")


class FollowEol(Token):
    def __init__(self) -> None:
        super().__init__("\n")


class Rule:
    non_terminal: NonTerminal
    tokens: List[Token]

    def __init__(self, non_terminal: NonTerminal, tokens: List[Token]) -> None:
        self.non_terminal = non_terminal
        self.tokens = tokens


class GrammarParser(Parser):
    def __init__(self, buffer) -> None:
        super().__init__(buffer)

    def parse_grammar(self) -> List[Rule]:
        rules: List[Rule] = []
        while self.left() > 0:
            rule = self.parse_rule()
            if rule:
                rules.append(rule)
        return rules

    def parse_rule(self) -> Optional[Rule]:

        # Parse potential comment
        if self.peek() == "#":
            _ = self.parse_comment()
            return None

        # Left side of association:
        non_terminal = self.parse_non_terminal()
        _ = self.parse_whitespaces()
        _ = self.parse_equal()
        _ = self.parse_whitespaces()
        sys.stderr.write(f"  parsing non_terminal: {non_terminal.value}\n")

        # Right side:
        tokens: List[Token] = []
        token: Token
        while self.left() > 0:
            c = self.peek()
            if c == "(":
                token = self.parse_begin_group()
            elif c == ")":
                token = self.parse_end_group()
            elif c == "|":
                token = self.parse_or()
            elif c == "<":
                token = self.parse_definition()
            elif c == "*" or c == "?" or c == "+":
                token = self.parse_cardinality()
            elif c == " " or c == "\n":
                sp = self.parse_whitespaces()
                if "\n\n" in sp:
                    break
                if "\n" in sp:
                    token = FollowEol()
                else:
                    token = Follow()
            elif c == '"':
                token = self.parse_terminal()
                sys.stderr.write(f"  parsing terminal: {token.value}\n")
            else:
                token = self.parse_non_terminal()
            tokens.append(token)

        return Rule(non_terminal=non_terminal, tokens=tokens)

    def parse_definition(self) -> Definition:
        def is_not_definition_end(current, prev):
            return not (current == ">" and prev != '"')

        c = self.read()
        assert c == "<"
        name = self.read_while_prev(is_not_definition_end)
        c = self.read()
        assert c == ">"
        return Definition(value=name)

    def parse_begin_group(self) -> BeginGroup:
        c = self.read()
        assert c == "("
        return BeginGroup()

    def parse_end_group(self) -> EndGroup:
        c = self.read()
        assert c == ")"
        return EndGroup()

    def parse_comment(self) -> Comment:
        value = self.read_while(lambda it: it != "\n")
        _ = self.parse_whitespaces()
        return Comment(value=value)

    def parse_non_terminal(self) -> NonTerminal:
        name = self.read_while(lambda it: re.search(r"[a-z\-|0-9]", it) is not None)
        return NonTerminal(value=name)

    def parse_terminal(self) -> Terminal:
        c = self.read()
        assert c == '"'
        offset = self.offset
        while self.left() > 0:
            c = self.peek()
            if c == "\\":
                _ = self.read(2)
            elif c == '"' and (self.offset != offset):
                break
            else:
                _ = self.read()
        name = self.buffer[offset : self.offset]
        c = self.read()
        assert c == '"'
        return Terminal(value=name)

    def parse_whitespaces(self) -> str:
        return self.read_while(lambda it: it == " " or it == "\n" or it == "\t")

    def parse_cardinality(self) -> Cardinality:
        c = self.read()
        assert c == "*" or c == "?" or c == "+"
        return Cardinality(value=c)

    def parse_equal(self) -> Equal:
        ret = self.read()
        assert ret == "="
        return Equal()

    def parse_or(self) -> Or:
        ret = self.read()
        assert ret == "|"
        return Or()


def rule_to_html(rule: Rule):
    txt = ""
    count = len(rule.tokens)
    for i in range(count):
        t = rule.tokens[i]
        if isinstance(t, Follow):
            txt += ""
        elif isinstance(t, FollowEol):
            txt += "<br>"
            # Manage the aligment
            next_t = rule.tokens[i + 1]
            if not isinstance(next_t, Or):
                txt += "&nbsp;"
        if isinstance(t, Definition):
            txt += f'<span class="definition">&lt;{t.value}&gt;</span>'
        elif isinstance(t, Terminal):
            txt += f'<span class="terminal">"{t.value}"</span>'
        elif isinstance(t, NonTerminal):
            txt += f'<a href="#{t.value}">{t.value}</a>'
        else:
            txt += t.value

    html = ""
    html += f'<div class="rule">\n'
    html += f'  <div class="non-terminal" id="{rule.non_terminal.value}">{rule.non_terminal.value}&nbsp;</div>\n'
    html += f'  <div class="tokens">=&nbsp;{txt}</div>'
    html += f"</div>\n"

    return html


def main():

    #  <style>
    #     .rule {
    #         font-family: "Courier New", Courier, monospace;
    #         font-weight: bold;
    #         width: 600px;
    #         display: table;
    #         margin: 20px 10px 20px 10px;
    #     }
    #
    #     .non-terminal {
    #         display: table-cell;
    #         /*background-color: mediumseagreen;*/
    #         white-space: nowrap;
    #     }
    #
    #     .terminal {
    #         color: darkgreen;
    #     }
    #
    #     .tokens {
    #         display: table-cell;
    #         /*background-color: darkorange;*/
    #         width: 100%;
    #     }
    # </style>

    sys.stderr.write("Parsing grammar...\n")

    text = Path("../spec/hurl.grammar").read_text()
    parser = GrammarParser(buffer=text)
    rules = parser.parse_grammar()
    body = "".join([rule_to_html(r) for r in rules])
    print(body)


if __name__ == "__main__":
    main()
