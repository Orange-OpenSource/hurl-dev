#!/usr/bin/env python3
import subprocess
from subprocess import CalledProcessError
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Callable
import platform
from pygments import highlight
from pygments.lexers import BashLexer, RustLexer
from pygments.formatters import HtmlFormatter


def main():
    highlight_code(language="hurl", to_html_func=hurl_to_html)
    highlight_code(language="bash", to_html_func=bash_to_html)
    highlight_code(language="shell", to_html_func=shell_to_html)
    highlight_code(language="rust", to_html_func=rust_to_html)


@dataclass
class Snippet:
    """Represents a code snippet."""

    content: str
    title: str | None
    language: str


def get_os() -> str:
    """Return linux, macos or windows."""
    if platform.system() == "Linux":
        return "linux"
    elif platform.system() == "Darwin":
        return "macos"
    elif platform.system() == "Windows":
        return "windows"
    else:
        raise EnvironmentError("Invalid Platform " + platform.system())


def highlight_code(language: str, to_html_func: Callable[[str], str]) -> None:
    print(f"Highlighting {language.title()} snippets...")

    for filename in Path("hurl.dev", "_site").glob("**/*.html"):
        print(f"    Processing {filename}...")
        src = Path(filename).read_text()
        snippets = extract_snippet(language=language, text=src)
        if not len(snippets):
            continue

        print(f"    Highlighting {filename}")
        dst = src
        for snippet in snippets:
            title = snippet.title
            content = snippet.content
            unescaped_content = unescape_html(content)
            colored_content = to_html_func(unescaped_content)
            if title:
                old = f'<pre><code class="language-{language}:{title}">{content}</code></pre>'
                new = f'<div class="code-block"><div class="code-title">{title}</div>\n<pre><code class="language-{language}">{colored_content}</code></pre></div>'
            else:
                old = f'<pre><code class="language-{language}">{content}</code></pre>'
                new = f'<div class="code-block"><pre><code class="language-{language}">{colored_content}</code></pre></div>'
            dst = dst.replace(old, new)
        Path(filename).write_text(dst)


def unescape_html(text: str) -> str:
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    return text


def escape_html(text: str) -> str:
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def hurl_to_html(snippet: str) -> str:
    # import sys
    # sys.stderr.write('<<<' + snippet + '>>>\n')
    cmd = [get_os() + "/hurlfmt", "--out", "html"]
    try:
        ret = subprocess.run(
            args=cmd,
            check=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            input=snippet,
        )
    except CalledProcessError:
        print(f"Error highlighting snippet:\n{snippet}")
        raise
    output = ret.stdout

    # PATCH: https://github.com/Orange-OpenSource/hurl/issues/3242
    output = output.replace("cert.pem\\", "cert.pem")
    # To be uniform with other snippets, we're removing the <pre><code> tag
    return extract(output, '<pre><code class="language-hurl">', "</code></pre>")


def bash_to_html(snippet: str) -> str:
    output = highlight(snippet, BashLexer(), HtmlFormatter(nowrap=True))
    # From https://github.com/richleland/pygments-css/blob/master/default.css
    output = output.replace('class="ch"', 'class="comment-hashbang"')
    output = output.replace('class="c1"', 'class="comment-single"')
    output = output.replace('class="k"', 'class="keyword"')
    output = output.replace('class="kc"', 'class="literal-constant"')
    output = output.replace('class="kd"', 'class="keyword"')
    output = output.replace('class="m"', 'class="literal-number"')
    output = output.replace('class="nb"', 'class="name-builtin"')
    output = output.replace('class="n"', 'class="name-variable"')
    output = output.replace('class="nv"', 'class="name-variable"')
    output = output.replace('class="o"', 'class="operator"')
    output = output.replace('class="p"', "")
    output = output.replace('class="s"', 'class="literal-string-double"')
    output = output.replace('class="s2"', 'class="literal-string-double"')
    output = output.replace('class="si"', 'class="literal-string-interpol"')
    output = output.replace('class="w"', "")

    # FIXME: Simulate docker as built-in
    for word in ["docker", "wait_for_url", "sleep"]:
        output = output.replace(word, f'<span class="name-builtin">{word}</span>')
    return output


def rust_to_html(snippet: str) -> str:
    output = highlight(snippet, RustLexer(), HtmlFormatter(nowrap=True))
    # From https://github.com/richleland/pygments-css/blob/master/default.css
    output = output.replace('class="ch"', 'class="comment-hashbang"')
    output = output.replace('class="c1"', 'class="comment-single"')
    output = output.replace('class="k"', 'class="keyword"')
    output = output.replace('class="kc"', 'class="literal-constant"')
    output = output.replace('class="kd"', 'class="keyword"')
    output = output.replace('class="m"', 'class="literal-number"')
    output = output.replace('class="nb"', 'class="name-builtin"')
    output = output.replace('class="n"', 'class="name-variable"')
    output = output.replace('class="nv"', 'class="name-variable-toto"')
    output = output.replace('class="o"', 'class="operator"')
    output = output.replace('class="p"', "")
    output = output.replace('class="s"', 'class="literal-string-double"')
    output = output.replace('class="s2"', 'class="literal-string-double"')
    output = output.replace('class="si"', 'class="literal-string-interpol"')
    output = output.replace('class="w"', "")
    return output


def shell_to_html(snippet: str) -> str:
    if "no-escape" in snippet:
        escaped_snippet = snippet
    else:
        escaped_snippet = escape_html(snippet)
    output = escaped_snippet.replace("$ ", '<span class="prompt">$ </span>')

    # Replace ANSI escape code with HTML tag
    output = output.replace("\x1b[1m", '<span class="bold">')
    output = output.replace("\x1b[0m", "</span>")
    output = output.replace("\x1b[31m", '<span class="red">')
    output = output.replace("\x1b[0;31m", '<span class="red">')
    output = output.replace("\x1b[32m", '<span class="green">')
    output = output.replace("\x1b[0;32m", '<span class="green">')
    output = output.replace("\x1b[33m", '<span class="yellow">')
    output = output.replace("\x1b[0;33m", '<span class="yellow">')
    output = output.replace("\x1b[34m", '<span class="blue">')
    output = output.replace("\x1b[0;34m", '<span class="blue">')
    output = output.replace("\x1b[35m", '<span class="magenta">')
    output = output.replace("\x1b[0;35m", '<span class="magenta">')
    output = output.replace("\x1b[36m", '<span class="cyan">')
    output = output.replace("\x1b[0;36m", '<span class="cyan">')
    output = output.replace("\x1b[90m", '<span class="gray">')
    output = output.replace("\x1b[1;36m", '<span class="bold bright-cyan">')
    output = output.replace("\x1b[1;31m", '<span class="bright-red">')
    output = output.replace("\x1b[1;32m", '<span class="bright-green">')
    output = output.replace("\x1b[1;34m", '<span class="bright-blue">')
    output = output.replace("\x1b[1;35m", '<span class="bright-magenta">')
    output = output.replace("\x1b[1;36m", '<span class="bright-cyan">')
    output = output.replace("\x1b[1;39m", '<span class="bold">')
    return output


def extract_snippet(language: str, text: str) -> List[Snippet]:
    prefix = re.compile(f'<pre><code class="language\\-{language}(?P<title>:.*)?">')
    suffix = "</code></pre>"
    index = 0

    snippets: List[Snippet] = []
    while True:
        match = prefix.search(text, index)
        if not match:
            break
        prefix_end = match.end(0)
        title = match.group("title")
        if title:
            title = title[1:]
        end = text.find(suffix, prefix_end)
        index = end
        content = text[prefix_end:end]
        snippet = Snippet(content=content, title=title, language=language)
        snippets.append(snippet)
    return snippets


def extract(text: str, prefix: str, suffix: str) -> str | None:
    reg = re.compile(f"""{prefix}(.+?){suffix}""", re.DOTALL)
    match = reg.search(text)
    if match:
        return match.group(1)
    else:
        return None


if __name__ == "__main__":
    main()
