#!/usr/bin/env python3
import subprocess
from subprocess import CalledProcessError
import re
from pathlib import Path
from typing import List
import platform


# return linux, osx or windows
def get_os():
    if platform.system() == 'Linux':
        return 'linux'
    elif platform.system() == 'Darwin':
        return 'osx'
    elif platform.system() == 'Windows':
        return 'windows'
    else:
        raise Error('Invalid Platform ' + platform.system())


def main():
    print(f"Highlighting Hurl snippets...")

    for filename in Path("hurl.dev", "_site").glob('**/*.html'):
        print(f"Processing {filename}...")
        src = Path(filename).read_text()
        snippets = extract_hurl_snippet(src)
        if not len(snippets):
            continue

        print(f"Highlighting {filename}")
        dst = src
        for snippet in snippets:
            unescaped_snippet = unescape_html(snippet)
            colored_snippet = hurl_to_html(unescaped_snippet)
            dst = dst.replace(
                f"<pre><code class=\"language-hurl\">{snippet}</code></pre>",
                f"<pre><code class=\"language-hurl\">{colored_snippet}</code></pre>"
            )
        Path(filename).write_text(dst)


def unescape_html(text: str) -> str:
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    return text


def hurl_to_html(snippet: str) -> str:
    #import sys
    #sys.stderr.write('<<<' + snippet + '>>>\n')
    #cmd = ["java", "-jar", "hurlfmt-1.0.43-SNAPSHOT.jar", "--format", "html", "-"]
    cmd = [get_os() + "/hurlfmt", "--format", "html"]
    try:
        ret = subprocess.run(
            args=cmd,
            check=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            #stderr=subprocess.PIPE,
            input=snippet.strip()
        )
    except CalledProcessError:
        print(f"Error highlighting snippet:\n{snippet}")
        raise
    output = ret.stdout
    #sys.stderr.write('<<<' + output + '>>>\n')
    # On extrait le code html
    #return extract(output, "<pre><code>", "</code></pre>")
    return extract(output, "<pre><code class=\"language-hurl\">", "</code></pre>")


def extract_hurl_snippet(text: str) -> List[str]:

    prefix = "<pre><code class=\"language-hurl\">"
    suffix = "</code></pre>"
    index = 0

    snippets: List[str] = []
    while True:
        begin = text.find(prefix, index)
        if begin == -1:
            break
        end = text.find(suffix, begin)
        index = end
        snippet = text[begin + len(prefix):end]
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

