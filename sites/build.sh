#!/usr/bin/env bash
set -eu

rm -rfd hurl.dev/_site/*

export CI_COMMIT_SHORT_SHA
CI_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)

echo 'First pass static build...'
echo '-------------------'
# First pass, build static site with git commit.
jekyll build --source hurl.dev --destination hurl.dev/_site

echo 'Search index build...'
echo '-------------------'
# Then build search index from the first pass.
mkdir -p hurl.dev/assets/data/
python3 build_index.py > hurl.dev/assets/data/index.json

echo 'Second pass static build...'
echo '-------------------'
# Second pass to take the rebuilt search index into account.
jekyll build --source hurl.dev --destination hurl.dev/_site

echo 'Highlight code snippets...'
echo '-------------------'
# Second pass to take the rebuilt search index into account.
# Highlight Hurl snippet.
python3 highlight.py

echo 'Add title anchors...'
echo '-------------------'
python3 build_anchors.py

echo 'Generating sitemap...'
echo '-------------------'
python3 build_sitemap.py > hurl.dev/_site/sitemap.txt


# Run local site
# jekyll serve --source hurl.dev --destination hurl.dev/_site
# python3 -m http.server --dir hurl.dev/_site 4000
