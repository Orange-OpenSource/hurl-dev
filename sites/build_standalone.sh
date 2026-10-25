set -eu

original_dir="$(pwd)"
cd "$(dirname "$0")"

./build_standalone_html.sh ../../hurl/docs/standalone/hurl-8.1.0.md hurl.dev/_includes/standalone.css
./build_standalone_epub.sh ../../hurl/docs/standalone/hurl-8.1.0.md hurl.dev/_includes/standalone.css
./build_standalone_pdf.sh ../../hurl/docs/standalone/hurl-8.1.0.md hurl.dev/_includes/standalone.css
