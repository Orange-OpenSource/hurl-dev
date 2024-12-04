---
title: Announcing Hurl 6.0.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

Christmas is early this year: <picture><source srcset="{{ '/assets/img/emoji-father-christmas.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/emoji-father-christmas.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/emoji-father-christmas.png' | prepend:site.baseurl }}" type="image/png"><img class="emoji" src="{{ '/assets/img/emoji-father-christmas.png' | prepend:site.baseurl }}" width="20" height="20" alt="Father Christmas emoji"></picture> the Hurl team is thrilled to announce [Hurl 6.0.0]!

[Hurl] is a command line tool powered by [curl], that runs HTTP requests defined in a simple plain text format:

```hurl
GET https://example.org/api/tests/4567
HTTP 200
[Asserts]
header "x-foo" contains "bar"
certificate "Expire-Date" daysAfterNow > 15
jsonpath "$.status" == "RUNNING"    # Check the status code
jsonpath "$.tests" count == 25      # Check the number of items
jsonpath "$.id" matches /\d{4}/     # Check the format of the id
```

## What’s New in This Release

- [Generating Dynamic Values with Functions](#generating-dynamic-values-with-functions)
- [curl Run Export](#curl-run-export)
- [Shorter Syntax for Sections](#shorter-syntax-for-sections)

## Generating Dynamic Values with Functions

Before 6.0.0, Hurl files could be only [templatized] with variables. Variables are either injected in the command line,
in `[Options]` section or through [captures].

For instance, let's take this Hurl file:

{% raw %}
```hurl
PUT https://example.org/api/hits
Content-Type: application/json
{
    "key0": "{{a_string}}",
    "key1": {{a_bool}},
    "key2": {{a_null}},
    "key3": {{a_number}}
}
```
{% endraw %}

When called with these options:

```shell
$ hurl --variable a_string=apple \
       --variable a_bool=true \
       --variable a_null=null \
       --variable a_number=42 \
       test.hurl
```

it runs a PUT request with the following JSON body:

```
{
    "key0": "apple",
    "key1": true,
    "key2": null,
    "key3": 42
}
```


With Hurl 6.0.0, we're introducing [functions] to generate dynamic values. Current functions are:

- `newUuid` to generate an [UUID v4 random string],
- `newDate` to generate an [RFC 3339] UTC date string, at the current time.

In the following example, we use the `newDate` function to generate a dynamic query parameter:

{% raw %}
```hurl
GET https://example.org/api/foo
[QueryStringParams]
date: {{newDate}}
HTTP 200
```
{% endraw %}

We run a `GET` request to `https://example.org/api/foo?date=2024%2D12%2D02T10%3A35%3A44%2E461731Z` where the `date`
query parameter value is `2024-12-02T10:35:44.461731Z` URL encoded.

In this second example, we use the `newUuid` function to generate an email dynamically:

{% raw %}
```hurl
POST https://example.org/api/foo
{
  "name": "foo",
  "email": "{{newUuid}}@test.com"
}
```
{% endraw %}

When run, the request body will be:

```
{
  "name": "foo",
  "email": "0531f78f-7f87-44be-a7f2-969a1c4e6d97@test.com"
}
```

Functions are a really nice addition to the Hurl file format, we've started small with these two functions, but we plan to add many more; don't hesitate [to open a discussion] for
your use case!  

## curl Run Export

In 6.0.0, we have added a new option to help debug and export your Hurl files: with the new [`--curl` option], we can export
run files to a list of curl commands. It's really convenient:

```shell
$ hurl --curl commands.txt *.hurl
$ cat commands.txt
curl 'https://google.com'
curl --head 'https://google.com'
curl 'https://google.com'
```

Debug curl command for each request is still available with [`--verbose`] mode but `--curl` makes it easy to get instead of
grepping the standard error.

Speaking of debug curl command, we have also added it to [JSON] and [HTML report], nice! 

## Shorter Syntax for Sections

With this new version, we have made the syntax a little shorter for sections: instead of `[QueryStringParams]` we can 
use `[Query]` now, `[FormParams]` becomes `[Form]` and `[MultipartFormData]` becomes `[Multipart]`. 

```hurl
POST https://foo.com/login
[Form]
user: alice
password: secret
token: 1234578
HTTP 302
```

```hurl
GET https://foo.com/search
[Query]
q: Mbappé
HTTP 200
```

Shorter names make a nicer Hurl file and are simpler to remember. We will support longer sections names for a long time
of course, but we'll remove them someday! For the moment, documentation is still using longer names and, progressively,
it will be updated with shorter names.

## Others

In this new version we have implemented two curl options:

- [`--limit-rate`][limit-rate]: limit request to the specified speed in bytes per second. This option is available as a CLI option
and can be set on a specific request
- [`--connect-timeout`][connect-timeout]: maximum time that connections are allowed to take. This option is set in seconds, but can also 
use [time units] like `10s`, `20000ms` etc...

```hurl
GET https://foo.com
[Options]
connect-timeout: 30s
limit-rate: 32000
```

Speaking of CLI options, help in `hurl --help` has been redesigned and categorized, to make it a little more readable.

We have also fixed a lot of bugs: a particular one [was a nasty (but rare) bug] in our parallel implementation. 
Shout-out to [Lambros Petrou] for having identified this one: TLDR, don't exit a main entry point program when there
are still living threads... Lambros is the mind behind [Skybear.NET], a managed platform to automate HTTP API 
testing. Give it a try, it's really powerful, simple and super cool (besides using Hurl of course!)

There are a lot of other improvements with Hurl 6.0.0 and also a lot of bug fixes, you can check the complete list of 
enhancements and bug fixes [in our release note].

If you like Hurl, don't hesitate to [give us a star on GitHub] or share it on [𝕏 / Twitter]!

We'll be happy to hear from you, either for enhancement requests or for sharing your success story using Hurl!


[Hurl 6.0.0]: https://github.com/Orange-OpenSource/hurl/releases/tag/6.0.0
[Hurl]: https://hurl.dev
[curl]: https://curl.se
[functions]: {% link _docs/templates.md %}#functions
[UUID v4 random string]: https://en.wikipedia.org/wiki/Universally_unique_identifier
[RFC 3339]: https://www.rfc-editor.org/rfc/rfc3339
[templatized]: {% link _docs/templates.md %}
[captures]: {% link _docs/capturing-response.md %}
[in our release note]: https://github.com/Orange-OpenSource/hurl/releases/tag/6.0.0
[𝕏 / Twitter]: https://x.com/HurlDev
[give us a star on GitHub]: https://github.com/Orange-OpenSource/hurl/stargazers
[to open a discussion]: https://github.com/Orange-OpenSource/hurl/discussions
[`--curl` option]: {% link _docs/manual.md %}#curl
[`--verbose`]: {% link _docs/manual.md %}#verbose
[JSON]: {% link _docs/running-tests.md %}#json-report
[HTML report]: {% link _docs/running-tests.md %}#html-report
[Lambros Petrou]: https://www.lambrospetrou.com
[Skybear.NET]: https://www.skybear.net
[limit-rate]: {% link _docs/manual.md %}#limit-rate
[connect-timeout]: {% link _docs/manual.md %}#connect-timeout
[was a nasty (but rare) bug]: https://github.com/Orange-OpenSource/hurl/issues/3297
[time units]: http://hurl.dev/blog/2024/08/29/hurl-5.0.0-the-parallel-edition.html#time-units