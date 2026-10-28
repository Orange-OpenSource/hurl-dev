#!/usr/bin/env bash
# Build the standalone PDF doc from the original standalone Markdown doc.
# The standalone HTML doc is built first, then printed to PDF with headless Google Chrome.
# Usage:
# $ ./build_standalone_pdf.sh INPUT.md CSS_FILE
# Example:
# $ ./build_standalone_pdf.sh ../../hurl/docs/standalone/hurl-8.1.0.md hurl.dev/_includes/standalone.css
#
# CSS_FILE is the site CSS. To regenerate hurl.dev/_includes/standalone.css from the site Sass sources:
# $ sass --no-source-map --load-path hurl.dev/_sass hurl.dev/_sass/main.scss > hurl.dev/_includes/standalone.css
#
# Chrome path can be changed with the CHROME environment variable.

set -Eeuo pipefail


input="$1"
css="$2"
base="${input%.md}"
output="${base}.pdf"
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"

echo "Building ${base}.pdf"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# The site CSS is designed for screens: we add print overrides.
cat "$css" - > "$work/style.css" <<'CSS'

/* PDF overrides */
@page {
    size: A4;
    margin: 2cm 1.5cm;
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-family: Helvetica, Arial, sans-serif;
        font-size: 0.8rem;
        color: #8c8c8c;
    }
}
/* Long code lines are wrapped instead of being cut */
pre {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    overflow-x: visible;
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

cp "$input" "$work/doc.md"
./build_standalone_html.sh "$work/doc.md" "$work/style.css"

"$chrome" \
    --headless \
    --disable-gpu \
    --no-pdf-header-footer \
    --print-to-pdf="$work/doc.pdf" \
    "file://$work/doc.html" 2>/dev/null

mv "$work/doc.pdf" "$output"
