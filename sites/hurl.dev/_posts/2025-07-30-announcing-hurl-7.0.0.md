---
title: Announcing Hurl 7.0.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

<p>
<picture><source srcset="{{ '/assets/img/emoji-desert-island.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/emoji-desert-island.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/emoji-desert-island.png' | prepend:site.baseurl }}" type="image/png"><img class="emoji" src="{{ '/assets/img/emoji-desert-island.png' | prepend:site.baseurl }}" width="20" height="20" alt="Partying Face"></picture> In this hot summer, the Hurl team is super happy to announce <a href="https://github.com/Orange-OpenSource/hurl/releases/tag/7.0.0">Hurl 7.0.0</a>!
</p>

[Hurl] is a command line tool powered by [curl], that runs HTTP requests defined in a simple plain text format:

```hurl
GET https://example.org/api/tests/4567
HTTP 200
[Asserts]
jsonpath "$.status" == "RUNNING"    # Check the status code
jsonpath "$.tests" count == 25      # Check the number of items
jsonpath "$.id" matches /\d{4}/     # Check the format of the id
# Some tests on the HTTP layer:
header "x-foo" contains "bar"
certificate "Expire-Date" daysAfterNow > 15
ip == "2001:0db8:85a3:0000:0000:8a2e:0370:733"
```

## What’s New in This Release

- [More Redirections Checks](#more-redirections-checks)
- [New Template Filters](#new-template-filters)
- [New Supported curl Options](#new-supported-curl-options)

## More Redirections Checks

Like its HTTP engine libcurl, Hurl doesn't follow redirection by default: on a 30x response status code, Hurl returns 
the HTTP response and does not trigger a new request following [`Location` header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Location).
Redirections have to be done manually:

```hurl
# First request, users are redirected to /login 
GET https://foo.com/home
HTTP 302
[Asserts]
header "Location" == "/login"

# We manually follow the redirection
GET https://foo.com/login
HTTP 200
```

This way, one can test each step of a redirection and insure that everything works as expected.

Like `curl`, we can use [`--location`]({% link _docs/manual.md %}#location) option to ask Hurl to follow redirection,
either globally using the command line option:

```shell
$ hurl --location foo.hurl
```

Or per request using [`[Options]` section]({% link _docs/request.md %}#options):

```hurl
GET https://foo.com/home
[Options]
location: true
HTT 200
```

Using [`--location`]({% link _docs/manual.md %}#location) (or [`--location-trusted`]({% link _docs/manual.md %}#location-trusted)), 
Hurl obeys the redirection and will issue requests until redirection ends. Before Hurl 7.0.0, we were losing the ability
to check each redirection steps using this option. The only check we could have done was using [`url` query]({% link _docs/asserting-response.md %}#url-assert)
to give us the final effective URL:

```hurl
GET https://foo.com/home
[Options]
location: true
HTTP 200
[Asserts]
url == "https://foo.com/login"
```

Starting with Hurl 7.0.0, we're introducing the `redirects` query, that give us access to each redirection step:

```hurl
GET https://foo.com/home
[Options]
location: true
HTTP 200
[Asserts]
redirects count == 3
redirects nth 0 location == "https://foo.com/redirect-1"
redirects nth 1 location == "https://foo.com/redirect-2"
redirects nth 2 location == "https://foo.com/landing"
```

The `redirects` query returns the list of each step followed during redirection. By combining [`nth`]({% link _docs/filters.md %}#nth) 
and [`location`]({% link _docs/filters.md %}#location) filters, we are now able to check redirection steps while letting
Hurl runs automatically to the final URL.

## New Template Filters

[Filters] allow to transform data extracted from HTTP responses. In the following sample, `replaceRegex`, `split`, `count` and `nth`
are filters that process input; they can be chained to transform values in asserts and captures:

```hurl
GET https://example.org/api
HTTP 200
[Captures]
name: jsonpath "$.user.id" replaceRegex /\d/ "x"
[Asserts]
header "x-servers" split "," count == 2
header "x-servers" split "," nth 0 == "rec1"
header "x-servers" split "," nth 1 == "rec3"
jsonpath "$.books" count == 12
```

In Hurl 7.0.0, we've added new filters:

- __`urlQueryParam`__
- __`base64UrlSafeDecode`__ and __`base64UrlSafeEncode`__
- __`location`__
- __`toHex`__
- __`first`__ and __`last`__

In detail, 

- __`urlQueryParam`__: extracts the value of a query parameter from an URL

```hurl
GET https://example.org/foo
HTTP 200
[Asserts]
jsonpath "$.url" urlQueryParam "x" == "шеллы"
```

This filter can be useful when you need to process URL received in payload, like a back URL.

- __`base64UrlSafeDecode`__ and __`base64UrlSafeEncode`__: decodes and encodes using [Base64 URL safe encoding]. There is also
`base64Decode` and `base64Encode` for their [Base 64 encoding] variants.

```hurl
GET https://example.org/api
HTTP 200
[Asserts]
jsonpath "$.token" base64UrlSafeDecode == hex,3c3c3f3f3f3e3e;
```

- __`location`__: returns the target URL location of a redirection. Combined with the new `redirects` query, you can 
check each step of a redirection:

```hurl
GET https://example.org/step1
[Options]
location: true
HTTP 200
[Asserts]
redirects count == 2
redirects nth 0 location == "https://example.org/step2"
redirects nth 1 location == "https://example.org/step3"
```

- __`toHex`__: converts bytes to an hexadecimal string.

```hurl
GET https://example.org/foo
HTTP 200
[Asserts]
bytes toHex == "d188d0b5d0bbd0bbd18b"
```

- __`first`__ and __`last`__: applied to a list, returns the first and last element:

```hurl
GET https://example.org/api
HTTP 200
[Asserts]
jsonpath "$..books" last jsonpath "$.title" == "Dune"
```

Alongside `first` and `last`, `nth` filter now supports negative index value for indexing from the end of the
collection:

```hurl
GET https://example.org/api
HTTP 200
[Asserts]
jsonpath "$..books" nth -2 jsonpath "$.title" == "Dune"
```


## New Supported curl Options

Using libcurl as its HTTP engine, Hurl exposes many curl options. In Hurl 7.0.0, we have added these two options:

- [`--max-time` per request]({% link _docs/manual.md %}#max-time): allows you to configure timeout per request, 
- [`--ntlm`]({% link _docs/manual.md %}#ntlm): uses NTLM authentication,
- [`--negotiate`]({% link _docs/manual.md %}#ntlm): uses Negotiate (SPNEGO) authentication,
- [`--pinnedpubkey`]({% link _docs/manual.md %}#pinnedpubkey): compares the certificate public key to a local public key
  and abort connection if not match. Can be use either globally on command line or per request:

```hurl
GET https://foo.com/hello
[Options]
# With a pinned public key local file
pinnedpubkey: tests_ssl/certs/server/key.pub.pem
# With a pinned public Hash
pinnedpubkey: "sha256//dGhpc2lzbm5vdGFyZWFsa2V5"
HTTP 200
```

__That's all for today!__

There are a lot of other improvements with Hurl 7.0.0 and also a lot of bug fixes, you can check the complete list of
enhancements and bug fixes [in our release note].

If you like Hurl, don't hesitate to [support us with a star on GitHub] and share it on [𝕏 / Twitter] and [Bluesky]!

We'll be happy to hear from you, either for enhancement requests or for sharing your success story using Hurl!


[Hurl]: https://hurl.dev
[curl]: https://curl.se
[in our release note]: https://github.com/Orange-OpenSource/hurl/releases/tag/7.0.0
[𝕏 / Twitter]: https://x.com/HurlDev
[Bluesky]: https://bsky.app/profile/hurldev.bsky.social
[support us with a star on GitHub]: https://github.com/Orange-OpenSource/hurl/stargazers
[Filters]: {% link _docs/filters.md %}
[Base 64 encoding]: https://datatracker.ietf.org/doc/html/rfc4648#section-4
[Base64 URL safe encoding]: https://datatracker.ietf.org/doc/html/rfc4648#section-5
