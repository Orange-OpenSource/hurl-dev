#!/usr/bin/env bash
# Build the standalone HTML doc from the original standalone Markdown doc.
# Usage:
# $ ./build_standalone_html.sh INPUT.md CSS_FILE
# Example:
# $ ./build_standalone_html.sh ../../hurl/docs/standalone/hurl-8.1.0.md hurl.dev/_includes/standalone.css
#
# CSS_FILE is the site CSS. To regenerate hurl.dev/_includes/standalone.css from the site Sass sources:
# $ sass --no-source-map --load-path hurl.dev/_sass hurl.dev/_sass/main.scss > hurl.dev/_includes/standalone.css

set -Eeuo pipefail


input="$1"
css="$2"
base="${input%.md}"
output="${base}.html"
title="Hurl Documentation"

echo "Building ${base}.html"

pandoc "$input" \
    --from markdown-native_divs-markdown_in_html_blocks \
    --syntax-highlighting=none \
    --standalone \
    --variable pagetitle:"$title" \
    --include-in-header <(echo '<style>'; cat "$css"; echo '</style>') \
    --variable include-before:'<div class="doc-content-col">' \
    --variable include-after:'</div>' \
    --metadata document-css=false \
    --output "$output"

# Pandoc generate `<pre class="LANG">...</code></pre>` and we want `<pre><code class="language-LANG">...</code></pre>`
sed -i.bak 's|<pre class="\([^"]*\)"><code>|<pre><code class="language-\1">|g' "${base}.html"
rm "${base}.html.bak"

python3 highlight.py "$output"