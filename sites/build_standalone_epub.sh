#!/usr/bin/env bash
# Build the standalone EPUB doc from the original standalone Markdown doc.
# Usage:
# $ ./build_standalone_epub.sh INPUT.md CSS_FILE
# Example:
# $ ./build_standalone_epub.sh ../../hurl/docs/standalone/hurl-8.1.0.md hurl.dev/_includes/standalone.css
#
# CSS_FILE is the site CSS. To regenerate hurl.dev/_includes/standalone.css from the site Sass sources:
# $ sass --no-source-map --load-path hurl.dev/_sass hurl.dev/_sass/main.scss > hurl.dev/_includes/standalone.css

set -Eeuo pipefail


input="$1"
css="$2"
base="${input%.md}"
output="${base}.epub"
title="Hurl Documentation"

echo "Building ${base}.epub"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# EPUB images must be embedded: we use the local site images instead of the remote ones, and remove
# `<source>` alternatives (AVIF, WebP are not EPUB core media types, the `<img>` PNG fallback is kept).
sed -e "s|https://hurl.dev/assets/img/|$(pwd)/hurl.dev/assets/img/|g" \
    -e '/<source /d' \
    "$input" > "$work/doc.md"

# The site CSS is designed for browsers: we override font sizes so the e-reader text size setting is the base.
cat "$css" - > "$work/style.css" <<'CSS'

/* EPUB overrides */
body {
    font-size: 1em;
}
h1 {
    font-size: 1.8em;
}
pre, code {
    font-size: 0.85em;
}
pre code {
    font-size: 1em;
}
/* `<hr>` separates the doc pages: we replace it by a page break. */
hr {
    border: 0;
    height: 0;
    margin: 0;
    page-break-after: always;
    break-after: page;
}
CSS

# Raw HTML blocks are kept as is (no Markdown parsing inside, like on the site).
pandoc "$work/doc.md" \
    --from markdown-native_divs-markdown_in_html_blocks \
    --to epub3 \
    --syntax-highlighting=none \
    --metadata title="$title" \
    --metadata lang=en \
    --metadata author=https://hurl.dev \
    --css "$work/style.css" \
    --output "$work/doc.epub"

# Highlight code snippets in the EPUB chapters.
mkdir "$work/epub"
unzip -q "$work/doc.epub" -d "$work/epub"

# Pandoc generate `<pre class="LANG">...</code></pre>` and we want `<pre><code class="language-LANG">...</code></pre>`
sed -i.bak 's|<pre class="\([^"]*\)"><code>|<pre><code class="language-\1">|g' "$work"/epub/EPUB/text/*.xhtml
rm "$work"/epub/EPUB/text/*.xhtml.bak

# Raw HTML from the Markdown is copied as is: void elements (`<hr>`, `<br>`...) must be closed in XHTML.
sed -E -i.bak 's#<(area|br|hr|img|input|meta|source|wbr)( [^>]*[^/>])?>#<\1\2/>#g' "$work"/epub/EPUB/text/*.xhtml
rm "$work"/epub/EPUB/text/*.xhtml.bak

python3 highlight.py "$work"/epub/EPUB/text/*.xhtml

# Repackage the EPUB: `mimetype` must be the first entry and stored uncompressed.
(
    cd "$work/epub"
    zip -q -X -0 ../out.epub mimetype
    zip -q -X -r -9 ../out.epub . -x mimetype
)
mv "$work/out.epub" "$output"
