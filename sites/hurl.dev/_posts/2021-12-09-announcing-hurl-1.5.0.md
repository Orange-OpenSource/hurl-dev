---
title: Announcing Hurl 1.5.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

The Hurl team is happy to announce [a new version of Hurl, 1.5.0].
Hurl is a command line tool that runs HTTP requests defined in a simple plain text format.

So, __what's new in 1.5.0__?

## Which curl is used by Hurl?

Hurl relies upon curl for the HTTP engine. We've improved the version output 
[`--version/-h`] to provide informations about which libcurl Hurl is linked with:

```shell
$ hurl --version
hurl 1.5.0 libcurl/7.54.0 LibreSSL/2.6.5 zlib/1.2.11
```

## Tests can be launched with glob pattern

Now tests can be launched with [`--glob` option]. This is particularly useful on
Windows where it is less easy to `grep` and `find` your test:

```shell
$ hurl --glob "tests/**/*.hurl"
```

This command will run `tests/project1/test1.hurl`, `tests/project1/test2.hurl` and
`tests/project2/test3.hurl`. Note that to avoid your shell accidentally expanding glob patterns
before Hurl handles them, you should use single quotes or double quotes around each pattern.

## Using Environment Variables in Hurl files

Before 1.5.0, to inject variables in a Hurl file you can

- use command line option, with [`--variable`]:

    ```shell
$ hurl --variable host=example.net --variable user=jc test.hurl
    ```

- use an input file, with [`--variables-file`]:

    Given `file.env` defining each variable on a new line:

    ```
host=example.net
user=jc
    ```
        
    Variables are injected with `file.env`:

    ```shell
$ hurl --variables-files file.env test.hurl
    ```
    

Starting in 1.5.0, environment variables can be used to inject variables:

```shell
$ echo HURL_host=example.net
$ echo HURL_user=jc
$ hurl test.hurl
```

Each `HURL_foo` environment variables will resolve as a `foo` variable inside 
the Hurl file.

## JUnit and HTML report

Test report can be exported in JUnit format:

```shell
$ hurl --test --report-junit /tmp/result.xml *.hurl
```

To be consistent, we've also rename `--html` options to `--report-html`. Of course, 
one can combine the two kind of reports:

```shell
$ hurl --test --report-junit /tmp/result.xml --report-html /tmp/report/ *.hurl
```

## Other changes

There are other changes and bug fixes in the Hurl 1.5.0 release: check out [the release note!]

And, finally, a big thanks to our contributors!

[a new version of Hurl, 1.5.0]: https://github.com/Orange-OpenSource/hurl/releases/tag/1.5.0
[`--version/-h`]: {% link _docs/man-page.md %}#version
[`--glob` option]: {% link _docs/man-page.md %}#glob
[`--variable`]: {% link _docs/man-page.md %}#variable
[`--variables-file`]: {% link _docs/man-page.md %}#variables-file
[the release note!]: https://github.com/Orange-OpenSource/hurl/releases/tag/1.5.0