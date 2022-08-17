#!/usr/bin/env python3
import subprocess
from subprocess import CalledProcessError
import re
from pathlib import Path
from typing import List, Callable
import platform
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter


def main():
    highlight_code(language="hurl", to_html_func=hurl_to_html)
    highlight_code(language="bash", to_html_func=bash_to_html)
    highlight_code(language="shell", to_html_func=shell_to_html)


def get_os() -> str:
    """Return linux, osx or windows."""
    if platform.system() == "Linux":
        return "linux"
    elif platform.system() == "Darwin":
        return "osx"
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
            unescaped_snippet = unescape_html(snippet)
            colored_snippet = to_html_func(unescaped_snippet)
            dst = dst.replace(
                f'<pre><code class="language-{language}">{snippet}</code></pre>',
                f'<pre><code class="language-{language}">{colored_snippet}</code></pre>',
            )
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
    cmd = [get_os() + "/hurlfmt", "--format", "html"]
    try:
        ret = subprocess.run(
            args=cmd,
            check=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            input=snippet.strip(),
        )
    except CalledProcessError:
        print(f"Error highlighting snippet:\n{snippet}")
        raise
    output = ret.stdout
    # sys.stderr.write('<<<' + output + '>>>\n')
    # On extrait le code html
    # return extract(output, "<pre><code>", "</code></pre>")
    return extract(output, '<pre><code class="language-hurl">', "</code></pre>")


def bash_to_html(snippet: str) -> str:
    output = highlight(snippet, BashLexer(), HtmlFormatter(nowrap=True))
    # From https://github.com/richleland/pygments-css/blob/master/default.css
    output = output.replace('class="ch"', 'class="comment-hashbang"')
    output = output.replace('class="c1"', 'class="comment-single"')
    output = output.replace('class="k"', 'class="keyword"')
    output = output.replace('class="m"', 'class="literal-number"')
    output = output.replace('class="nb"', 'class="name-builtin"')
    output = output.replace('class="nv"', 'class="name-variable"')
    output = output.replace('class="o"', 'class="operator"')
    output = output.replace('class="s2"', 'class="literal-string-double"')
    output = output.replace('class="si"', 'class="literal-string-interpol"')

    # FIXME: Simulate docker as built-in
    for word in ["docker", "wait_for_url", "sleep"]:
        output = output.replace(word, f'<span class="name-builtin">{word}</span>')
    return output


def shell_to_html(snippet: str) -> str:
    escaped_snippet = escape_html(snippet)
    output = escaped_snippet.replace("$ ", '<span class="prompt">$ </span>')

    # Replace ANSI escape code with HTML tag
    output = output.replace("\x1B[1m", '<span class="bold">')
    output = output.replace("\x1B[0m", "</span>")
    output = output.replace("\x1B[1;31m", '<span class="bright-red">')
    output = output.replace("\x1B[1;32m", '<span class="bright-green">')
    output = output.replace("\x1B[1;34m", '<span class="bright-blue">')
    output = output.replace("\x1B[1;35m", '<span class="bright-magenta">')
    output = output.replace("\x1B[1;36m", '<span class="bright-cyan">')
    return output


def extract_snippet(language: str, text: str) -> List[str]:

    prefix = f'<pre><code class="language-{language}">'
    suffix = "</code></pre>"
    index = 0

    snippets: List[str] = []
    while True:
        begin = text.find(prefix, index)
        if begin == -1:
            break
        end = text.find(suffix, begin)
        index = end
        snippet = text[begin + len(prefix) : end]
        snippets.append(snippet)
    return snippets


def extract(text, prefix, suffix):
    reg = re.compile(f"""{prefix}(.+?){suffix}""", re.DOTALL)
    match = reg.search(text)
    if match:
        return match.group(1)
    else:
        return None


if __name__ == "__main__":
    main()
