#!/usr/bin/env python3
# ./build_man.py ../../hurl/docs/hurl.md > hurl.dev/_docs/man-page.md
import sys
import re


def header():
   return '''---
layout: doc
title: Man Page
---
# {{ page.title }}
'''


def process_code_block(s):
    output = ''
    in_code = False
    for line in s.split('\n'):
        if not in_code and line.startswith('```'):
            output += '{% raw %}\n'
            output += line + '\n'
            in_code = True
        elif in_code and line.startswith('```'):
            output += line + '\n'
            output += '{% endraw %}\n'
            in_code = False
        else:
            output += line + '\n'

    return output


def normalize_h2(s):
    lines = []
    p = re.compile('^## (.*)$')
    for line in s.split('\n'):
        m = p.match(line)
        if m:
            value = m.group(1).title()
            # Add exception for www acronym
            if value == "Www":
                value = "WWW"
            lines.append('## ' + value)
        else:
            lines.append(line)
    return '\n'.join(lines)


def escape(s):
    return s.replace('<', '&lt;').replace('--', '\\-\\-')


def main():
    input_file = sys.argv[1]
    lines = open(input_file).readlines()
    s = ''.join(lines)
    s = escape(s)
    s = normalize_h2(s)
    s = process_code_block(s)
    print(header() + s)


if __name__ == '__main__':
    main()
