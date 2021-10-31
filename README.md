[![deploy status](https://github.com/Orange-OpenSource/hurl-dev/workflows/Publish/badge.svg)](https://github.com/Orange-OpenSource/hurl-dev/actions)

# Hurl Official Documentation Site

The official [documentation site](https://hurl.dev) for [Hurl](https://github.com/Orange-OpenSource/hurl).
This repo contains only the documentation, tutorials, and test suites for Hurl. If you're looking for
Hurl source code, please check out <https://github.com/Orange-OpenSource/hurl>.


## Contributing

Edits on documentation are done via pull request. Once a pul request is accepted, modifications are automatically published
to <https://hurl.dev> via [the publish GitHub action].

## Local build

### Prerequites

- [Jekyll]
- Python 3, with [Beautiful Soup 4 package (`bs4`)]


### Build

```shell
$ cd sites
$ ./build.sh
```

### Run local static site

```shell
$ cd sites
$ python3 -m http.server --dir hurl.dev/_site 4000
```

### Run and watch local site

```shell
$ cd sites
$ jekyll serve --source hurl.dev --destination hurl.dev/_site
```

When running with Jekyll, the local built is rerun automatically for each modification. 
In this mode, Hurl code snippets haven't any syntax coloring.

### Scripts

- [`build.sh`]: uber-script to build <hurl.dev> from scratch
- [`build_anchors.py`]: add anchors to every HTML tag. Exemple: `<h2 id="some-stuff">Some Title</h2>` becomes `<h2 id="some-stuff"><a href="#some-stuff">Some Title</a></h2>`
- [`build_github_readme.py`]: use documentation to generate [Hurl README.md]
- [`build_index.py`]: construct search index (search is entirely done viz Javascript in the browser, without any server apis.) 
- [`build_sitemap.py`]: generate <https://hurl.dev/sitemap.txt>
- [`deploy.sh`]: deploy a local build to <https://hurl.dev>
- [`grammar2html.py`]: generate <https://hurl.dev/docs/grammar.html> from [grammar spec]
- [`highlight.py`]: generate syntax coloring for Hurl snippets
- others: utilities


[Jekyll]: https://jekyllrb.com
[the publish GitHub action]: https://github.com/Orange-OpenSource/hurl-dev/actions/workflows/publish.yml
[Beautiful Soup 4 package (`bs4`)]: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
[Hurl README.md]: https://github.com/Orange-OpenSource/hurl
[`build.sh`]: sites/build.sh
[`build_anchors.py`]: sites/build_anchors.py
[`build_github_readme.py`]: sites/build_github_readme.py
[`build_index.py`]: sites/build_index.py
[`build_sitemap.py`]: sites/build_sitemap.py
[`deploy.sh`]: sites/deploy.sh
[`grammar2html.py`]: sites/grammar2html.py
[grammar spec]: spec/hurl.grammar
[`highlight.py`]: sites/highlight.py

