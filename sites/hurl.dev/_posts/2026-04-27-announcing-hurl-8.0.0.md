---
title: Announcing Hurl 8.0.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

<p>The Hurl team is thrilled to announce <a href="https://github.com/Orange-OpenSource/hurl/releases/tag/8.0.0">Hurl 8.0.0</a>!
<picture><source srcset="{{ '/assets/img/emoji-partying-face.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/emoji-partying-face.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/emoji-partying-face.png' | prepend:site.baseurl }}" type="image/png"><img class="emoji" src="{{ '/assets/img/emoji-partying-face.png' | prepend:site.baseurl }}" width="20" height="20" alt="Partying Face"></picture>
</p>

[Hurl] is a command line tool powered by [curl], that runs HTTP requests defined in a simple plain text format:

```hurl
GET https://example.org/api/tests/4567
HTTP 200
[Asserts]
jsonpath "$.status" == "RUNNING"    # Check the status code
jsonpath "$.tests" count == 25      # Check the number of items
jsonpath "$.id" matches /\d{4}/     # Check the format of the id


POST https://example.org/api/tests
{
  "name": "foo"
}
HTTP 201
[Asserts]
header "x-foo" contains "bar"
certificate "Expire-Date" daysAfterNow > 15
ip == "2001:0db8:85a3:0000:0000:8a2e:0370:733"
```

## What’s New in This Release

- [Brand New JSONPath - RFC 9535 Support](#brand-new-jsonpath-rfc-9535-support)
- [Hurl Support in GitHub](#hurl-support-in-github)
- [Configure Hurl with Environment Variables](#configure-hurl-with-environment-variables)
- [--no-cookie-store Option to Test Cookie-less Workflows](#-no-cookie-store-option-to-test-cookie-less-workflows)
- [SSL/TLS Certificate Improvements](#ssltls-certificate-improvements)
- [Others](#others) 

### Brand New JSONPath - RFC 9535 Support

In Feb 2024, the JSONPath RFC ([RFC 9535]) standard was published, 17 years after Stefan Gössner wrote his
influential blog post JSONPath – XPath for JSON that resulted in some 50 implementations in various languages (with, 
unfortunately, differences among them).

When the JSONPath was originally introduced in Hurl, no formal specification existed, the only reference was the original
article from [goessner.net], and we based our code on it.

With [Hurl 8.0.0], the star of the show is our full [RFC 9535] implementation!

You can now write more powerful queries such as `$[?length(@.authors) >= 5]` or 
`$.store.book[?(@.category == 'fiction' && @.price >= 10)]`

[RFC 9535] also defines functions `length`, `count`, `match`, `search` and `value`:

```hurl
GET http://localhost:8000/jsonpath/function
HTTP 200
[Asserts]
jsonpath "$.items[?length(@.name) > 3]" count == 2
jsonpath "$.items[?count(@.tags) == 1]" count == 3
jsonpath "$.items[?match(@.name, '^ca.*')].name" == "car"
jsonpath "$.items[?search(@.name, 'ca')].name" == "car"
jsonpath "$.items[?search(@.name, $.string)].name" == "car"
jsonpath "$.items[?value(@.heavy) == true]" count == 2
```

Combining filters and booleans expression is now possible: 

```hurl
GET http://localhost:8000/json/store
HTTP 200
[Asserts]
jsonpath "$.store.book[?(@.published==true)].title" == "Moby Dick"         # filter on published books
jsonpath "$.store.book[?(@.category == 'fiction' && @.price >= 10)]" count == 2 # filter all fiction books with price >= 10
```

#### Normalized JSONPath results

With this brand-new implementation, JSONPath results in Hurl have been standardized and aligned with 
other queries (like XPath).

JSONPath queries always return arrays, the Hurl [jsonpath] filter/query now maps the results as follows:

1. empty array → None value

   `jsonpath "$.store.book[5].title" not exists`

2. single-element array → the element itself

   `jsonpath "$.store.book[1].title" == "Sword of Honour"`

3. multiple elements → the full array of elements

   `jsonpath "$.store.book[0,2]" count == 2`

#### Breaking Changes

Unfortunately, this new [RFC 9535] support forces us to make breaking changes. While most of the
existing JSONPath queries works without any modification in your Hurl files when upgrading to 8.0.0, 
you might have some changes to make.

Notably, '-' in keypath: it's not supported by the new spec and this kind of JSONPath 

`$.headers.X-Custom` 

must be rewritten as

`$.headers['X-Custom']`

For instance, before Hurl 8.0.0:

```hurl
GET http://localhost:8000/json/store
HTTP 200
[Asserts]
jsonpath "$.not-exist" count == 5
jsonpath "$.not-exist" startsWith "foo"
jsonpath "$.not-exist" endsWith "foo"
```

With Hurl 8.0.0:

```hurl
GET http://localhost:8000/json/store
HTTP 200
[Asserts]
jsonpath "$['not-exist']" count == 5
jsonpath "$['not-exist']" startsWith "foo"
jsonpath "$['not-exist']" endsWith "foo"
```

You can test the validity of your JSONPath expression with <https://jsonpath.com>, selecting RFC 9535: 

<picture><source srcset="{{ '/assets/img/jsonpath.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/jsonpath.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/jsonpath.png' | prepend:site.baseurl }}" type="image/png"><img  src="{{ '/assets/img/jsonpath.png' | prepend:site.baseurl }}" width="600" height="374" alt="jsonpath.com"></picture>

Finally, our new JSONPath evaluation might also break existing tests written for previous versions.

For example:

`jsonpath "$..book[5:7].title" count == 0`

If there are only 4 books, this query now returns no value instead of an empty array. You will therefore get the following
error:

```
error: Filter error
  --> /tmp/test.hurl:4:31
   |
   | GET http://localhost:8000/books.json
   | ...
 4 | jsonpath "$..book[5:7].title" count == 0
   |                               ^^^^^ missing value to apply filter
   |
```

You must fix the assertion as follows:

`jsonpath "$..book[5:7].title" not exists`

Because of the potential breaking changes, we're trying to contact public repos on GitHub that are using Hurl when we 
detect that they may have some changes to make for Hurl 8.0.0. Usually the changes are simple so this should not be a 
big issue. In exchange, we hope that the new RFC 9535 will give you some useful new test capabilities.

### Hurl Support in GitHub

Not specifically tied to this new 8.0.0 version, but Hurl is now an official language on GitHub!

You can search for Hurl snippets:

<picture><source srcset="{{ '/assets/img/github-hurl-search.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/github-hurl-search.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/github-hurl-search.png' | prepend:site.baseurl }}" type="image/png"><img  src="{{ '/assets/img/github-hurl-search.png' | prepend:site.baseurl }}" width="600" height="407" alt="Search on GitHub for Hurl snippet"></picture>

Repo top languages shows Hurl support:

<picture><source srcset="{{ '/assets/img/github-repo-languages.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/github-repo-languages.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/github-repo-languages.png' | prepend:site.baseurl }}" type="image/png"><img  src="{{ '/assets/img/github-repo-languages.png' | prepend:site.baseurl }}" width="375" height="172" alt="Repo top languages with Hurl"></picture>

And Hurl code is syntactically colored:

<picture><source srcset="{{ '/assets/img/github-highlight.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/github-highlight.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/github-highlight.png' | prepend:site.baseurl }}" type="image/png"><img  src="{{ '/assets/img/github-highlight.png' | prepend:site.baseurl }}" width="600" height="512" alt="Repo top languages with Hurl"></picture>

Thanks to Niklas Mollenhauer ([@nikee](https://github.com/nikeee)) and all other people that have made this possible, you rock! 

### Configure Hurl with Environment Variables

Hurl options can be used in command line like `--location` to follow redirection, and overridden per request in `[Options]` 
section. For instance, this Hurl file:

```hurl
GET https://example.org
HTTP 301

GET https://example.org
[Options]
location: true
HTTP 200
```

will follow a redirection only for the second entry.

With Hurl 8.0.0, most of the options can also be defined with environment variables (like `HURL_INSECURE` for [`--insecure`][insecure]). 
So, in order to configure Hurl, there are three sources from the lowest priority (most easily overridden) to highest 
(overrides all others):

- Environment variables (ex: `HURL_INSECURE`)
- Command-line options (ex: `--insecure`)
- Options section options (ex: `insecure: true` in file)

You can check the [Hurl manual] to see all the configurable environment variables, there are plenty (i.e. `HURL_COMPRESSED`, 
`HURL_CONNECT_TIMEOUT`, `HURL_HEADER`, `HURL_HTTP3` etc...)

### --no-cookie-store Option to Test Cookie-less Workflows

By default, requests in the same Hurl file share cookie storage. A new option [`--no-cookie-store`][no-cookie-store] 
deactivates cookie engine allowing you to test cookie-less workflows. And you can configure it by environment variable 
with `export HURL_NO_COOKIE_STORE=1`.

### SSL/TLS Certificate Improvements

Certificate queries allow you to assert and capture TLS/SSL certificates attributes like: subject, issue, start date, 
expire date and serial number. With Hurl 8.0.0, you can now get subject alternative name and certificate value.

```hurl
GET https://example.org
HTTP 200
[Asserts]
certificate "Subject" == "CN=example.org"
certificate "Issuer" == "C=US, O=Let's Encrypt, CN=R3"
certificate "Expire-Date" daysAfterNow > 15
certificate "Serial-Number" matches "[0-9af]+"
certificate "Subject-Alt-Name" contains "DNS:example.org"
certificate "Subject-Alt-Name" split "," count == 2
certificate "Value" startsWith "-----BEGIN CERTIFICATE-----"
```

### Others

#### Raw multilines

Making a JSON body request in Hurl is super simple, you just have to write a JSON body without any modification and it will be 
sent as is, with the right `application/json` [Content-Type] header. With this body, templates are also supported, in order 
to set variations on your requests.

{% raw %}
~~~hurl
POST https://example.org/api/cats
{
  "id": 42,
  "name": "{{ name }}"
}
~~~

`{{name}}` is evaluated as a template and the file will fail if there is no `name` variable.

With Hurl 8.0.0, you can disable variable rendering and send `{{ foo }}` as it is, without Hurl trying to render it with
    a variable. Using [multiline string body] and `raw` identifier you can send an unmodified body over the wire.

~~~hurl
POST https://example.org/api/cats
Content-Type: application/json
```raw
{
  "id": 42,
  "name": "{{ name }}"
}
```
~~~

{% endraw %}

Without the `raw` identifier, the body will be a classic multiline body and will render every variable.

#### rawbytes query

HTTP body responses can be encoded by server but captures and asserts in Hurl files are not affected by the content 
compression. In Hurl, captures and asserts work automatically on the decompressed response body, as if there weren’t 
any compression.

Unlike `bytes` query, the new `rawbytes` query returns the raw bytes before any content decoding. For uncompressed responses, `rawbytes`
and `bytes` return the same data.

```hurl
GET https://example.org/data.bin
HTTP 200
Content-Encoding: gzip
[Asserts]
header "Content-Length" == "32"
rawbytes count == 32 # matches Content-Length (compressed size)
bytes count == 100 # decompressed size is larger
rawbytes startsWith hex,1f8b; # gzip magic bytes
bytes startsWith hex,48656c6c6f; # decompressed content starts with "Hello"
```

__That's all for today!__

There are a lot of other improvements with Hurl 8.0.0 and also a lot of bug fixes, you can check the complete list of
enhancements and bug fixes [in our release note].

If you like Hurl, don't hesitate to [support us with a star on GitHub] and share it on [𝕏 / Twitter] and [Bluesky]!

We'll be happy to hear from you, either for enhancement requests or for sharing your success story using Hurl!


[Hurl]: https://hurl.dev
[curl]: https://curl.se
[in our release note]: https://github.com/Orange-OpenSource/hurl/releases/tag/8.0.0
[𝕏 / Twitter]: https://x.com/HurlDev
[Bluesky]: https://bsky.app/profile/hurldev.bsky.social
[support us with a star on GitHub]: https://github.com/Orange-OpenSource/hurl/stargazers
[RFC 9535]: https://datatracker.ietf.org/doc/rfc9535
[Hurl 8.0.0]: https://github.com/Orange-OpenSource/hurl/releases/tag/8.0.0
[goessner.net]: https://goessner.net/articles/JsonPath
[jsonpath]: {% link _docs/filters.md %}#jsonpath
[insecure]: {% link _docs/manual.md %}#insecure
[no-cookie-store]: {% link _docs/manual.md %}#no-cookie-store
[Content-Type]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Type
[multiline string body]: {% link _docs/request.md %}#multiline-string-body
[Hurl manual]: {% link _docs/manual.md %}
