---
title: Announcing Hurl 1.6.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

The Hurl team is happy to announce [a new version of Hurl, 1.6.0].

[Hurl] is a command line tool powered by [curl], that runs HTTP requests defined 
in a simple plain text format:

```hurl
# Get home:
GET https://example.net

HTTP/1.1 200
[Captures]
csrf_token: xpath "string(//meta[@name='_csrf_token']/@content)"

# Do login!
POST https://example.net/login?user=toto&password=1234
X-CSRF-TOKEN: {{csrf_token}}

HTTP/1.1 302
```


So, __what's new in 1.6.0__?

## Simplify basic authentification

Before 1.6.0, basic authentification could be achieved by computing and sending
an [Authorization] header:

```hurl
# Authorization header value can be computed with:
# `echo -n 'bob:secret' | base64`
GET http://example.com/protected
Authorization: Basic Ym9iOnNlY3JldA==
```

In 1.6.0, we've introduced a basic authentification section to pass username/password
explicitly, without base64 encoding:

```hurl
GET http://example.com/protected
[BasicAuth]
bob: secret
```

Basic authentification allows per request authentification. If you want to add 
basic authentification to all the request of a Hurl file you could use [`-u/--user` option].

## Regex literal

`matches` predicates values are regex. Before 1.6.0, metacharacters in pattern 
values should be escaped (like `\d` etc...):

```hurl
GET https://sample.org/hello

HTTP/1.0 200
[Asserts]
jsonpath "$.date" matches "^\\d{4}-\\d{2}-\\d{2}$"
jsonpath "$.name" matches "Hello [a-zA-Z]+!"
```

In 1.6.0, we've added regex literal for `matches`:

```hurl
GET https://sample.org/hello

HTTP/1.0 200
[Asserts]
jsonpath "$.date" matches /^\d{4}-\d{2}-\d{2}$/
jsonpath "$.name" matches /Hello [a-zA-Z]+!/
```

The new asserts are much more readable and easier to write.

Basic authentification section and regex literal has been suggested to us 
by [David Humphrey] so thanks again David fo your ideas!

## Interactive mode improvements

In [interactive mode], Hurl plays each request and pauses between each entry, 
allowing to [debug a session step by step]. We've improved the interactive 
mode to display the next request to be played:

```
...
< Last-Modified: Fri, 11 Feb 2022 13:28:20 GMT
< Connection: keep-alive
< ETag: "62066474-6f02"
< Accept-Ranges: bytes
< 
* 

interactive mode

next request:

GET https://hurl.dev/docs/man-page.html

Press Q (Quit) or C (Continue)
```

## Other changes

Under the hood, we've improved our code and Hurl should be quicker than ever.
There are other changes and bug fixes in the Hurl 1.6.0 release: check out [the release note!]

If you like Hurl, don't hesitate [to give us a star]!

And, finally, a big thanks to all our contributors!

[Hurl]: https://hurl.dev
[curl]: https://curl.se
[a new version of Hurl, 1.6.0]: https://github.com/Orange-OpenSource/hurl/releases/tag/1.6.0
[David Humphrey]: https://github.com/humphd
[`-u/--user` option]: {% link _docs/man-page.md %}#user
[the release note!]: https://github.com/Orange-OpenSource/hurl/releases/tag/1.6.0
[interactive mode]: {% link _docs/man-page.md %}#interactive
[debug a session step by step]: {% link _docs/tutorial/debug-tips.md %}#interactive-mode
[Authorization]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization
[to give us a star]: https://github.com/Orange-OpenSource/hurl/stargazers