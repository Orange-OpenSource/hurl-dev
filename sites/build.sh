#!/usr/bin/env bash
set -eu

function echo_step () {
  echo ''
  echo -e "\033[32m\033[1m$1...\033[0m"
}

rm -rfd hurl.dev/_site/*

export CI_COMMIT_SHORT_SHA
CI_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)

echo_step 'First pass static build'
# First pass, build static site with git commit.
jekyll build --source hurl.dev --destination hurl.dev/_site --future

echo_step 'Search index build'
# Then build search index from the first pass.
mkdir -p hurl.dev/assets/data/
python3 build_index.py > hurl.dev/assets/data/index.json

echo_step 'Second pass static build'
# Second pass to take the rebuilt search index into account.
jekyll build --source hurl.dev --destination hurl.dev/_site --future

echo_step 'Highlight code snippets'
# Second pass to take the rebuilt search index into account.
# Highlight Hurl snippet.
python3 highlight.py

echo_step 'Replace home samples'
python3 build_home_samples.py

echo_step 'Add title anchors'
python3 build_anchors.py

echo_step 'Generating sitemap'
python3 build_sitemap.py > hurl.dev/_site/sitemap.txt

echo_step 'Generating feed.xml'
cp hurl.dev/_posts/feed.xml hurl.dev/_site/blog/

echo ''
echo 'Run local site'
echo '-------------------'
echo '    Build & watch: jekyll serve --source hurl.dev --destination hurl.dev/_site'
echo '    Static: python3 -m http.server --dir hurl.dev/_site 4000'
