---
title: Announcing Hurl 6.1.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

The Hurl team is thrilled to announce [Hurl 6.1.0] <picture><source srcset="{{ '/assets/img/emoji-party-popper.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/emoji-party-popper.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/emoji-party-popper.png' | prepend:site.baseurl }}" type="image/png"><img class="emoji" src="{{ '/assets/img/emoji-party-popper.png' | prepend:site.baseurl }}" width="20" height="20" alt="Partying Face"></picture> !

[Hurl] is a command line tool powered by [curl], that runs HTTP requests defined in a simple plain text format:

```hurl
GET https://example.org/api/tests/4567
HTTP 200
[Asserts]
header "x-foo" contains "bar"
certificate "Expire-Date" daysAfterNow > 15
ip == "2001:0db8:85a3:0000:0000:8a2e:0370:733"
jsonpath "$.status" == "RUNNING"    # Check the status code
jsonpath "$.tests" count == 25      # Check the number of items
jsonpath "$.id" matches /\d{4}/     # Check the format of the id
```

## What’s New in This Release

- [Redacting Sensitive Values from Reports and Logs with Secrets](#redacting-sensitive-values-from-reports-and-logs-with-secrets)
- [New Queries: IP Address, HTTP Version](#new-queries-ip-address-http-version)
- [New Filters: base64Encode/Decode, toString](#new-filters-base64encodedecode-tostring)
- [More curl Options](#more-curl-options)

## Redacting Sensitive Values from Reports and Logs with Secrets

In Hurl 6.1.0, we're introducing _secrets_, a simple way to redact sensitive datas from logs and reports. In HTTP workflows, 
it's highly probable that authentication tokens, API keys or other confidential values will be used in some parts of 
the network transfers. Sensitive data can transit in HTTP headers, URL or in HTTP request/response body and be accidentally 
leaked in the run.

When a user enables logging for instance, Hurl outputs various part of the HTTP transactions on standard error. Let's say 
our Hurl file is using a secret header `x-password` with the value `sesame-ouvre-toi`:

```hurl
GET https://foo.com
Content-Type: application/json
x-password: sesame-ouvre-toi
HTTP 200
```

A first step to not leak a secret is [to use a variable] so the Hurl file doesn't contain the secret value:

{% raw %}
```hurl
GET https://foo.com
Content-Type: application/json
x-password: {{password}}
HTTP 200
```
{% endraw %}

To run this file, traditionally we set the variable value with an environment variable: 

```shell
$ hurl --variable password=$PASSWORD foo.hurl
```

But, if we run this file with [`--verbose`]({% link _docs/manual.md %}#verbose) option, we can accidentally leak the value of the secret header:

```shell
$ hurl --verbose foo.hurl
* ------------------------------------------------------------------------------
* Executing entry 1
*
* Cookie store:
*
* Request:
* GET http://foo.com
[1;31m* x-secret: sesame-ouvre-toi[0m
*
* Request can be run with the following curl command:
* curl --request GET [1;31m--header 'x-secret: sesame-ouvre-toi'[0m --header 'Content-Type: application/json' 'http://foo.com'
*
> GET / HTTP/1.1
> Host: foo.com:80
> Accept: */*
[1;31m> x-secret: sesame-ouvre-toi[0m
> Content-Type: application/json
> User-Agent: hurl/6.1.0
> Content-Length: 24
>
* Request body:
*
< HTTP/1.1 200 OK
< Server: Werkzeug
...
```

Even without `--verbose` mode, assertion errors can leak secrets:

```shell
$ hurl --error-format long foo.hurl
HTTP/2 200
date: Fri, 14 Mar 2025 08:55:46 GMT
content-type: text/html
...
[1;31mx-secret: TOP_SECRET_VALUE[0m
x-content-type-options: nosniff
accept-ranges: bytes

<!DOCTYPE html>
<html lang="en">
...
</html>

error: Assert status code
  --> /tmp/err.hurl:2:6
   |
   | GET https://hurl.dev
 2 | HTTP 400
   |      ^^^ actual value is <200>
   |
```

Started with Hurl 6.1.0, you can inject a variable whose value will be redacted from any logs using [`--secret` option]({%link _docs/templates.md %}#secrets):

```
$ hurl --secret password=$PASSWORD foo.hurl
```

You can use `--secret` also to hide values even if these variables are not used in a Hurl file. This way, you can also protect 
your secrets when secret values are processed (turned on uppercase, encoded to base64 etc...), even if they're not actually
used as Hurl variables:

```
$ PASSWORD_UPPER=$(printf "%s" "$PASSWORD" | tr '[:lower:]' '[:upper:]')
$ PASSWORD_BASE_64=$(printf "%s" "$PASSWORD" | base64)
$ hurl --secret password=$PASSWORD \
       --secret password_1=$PASSWORD_UPPER \
       --secret password_2=$PASSWORD_BASE_64 \
       foo.hurl
```

Various CI/CD platforms like [GitHub Actions] or [GitLab CI/CD] can be configured to hide specific values from logs. 
But secrets in Hurl are also redacted from the reports ([HTML], [JSON], [JUnit] etc...) so you can safely store these reports
as artifacts of your CI/CD pipelines.

Finally, sometimes you don't know a secret value beforehand, or the secret value is not static. In that case, the keyword
[`redact` combined with captures]({% link _docs/capturing-response.md %}#redacting-secrets) allows you to extract data from HTTP responses and redact it through the run:

```hurl
GET http://bar.com/api/get-token
HTTP 200
[Captures]
token: header "X-Token" redact
```

## New Queries: IP Address, HTTP Version

Hurl allows you [to capture] and [assert data] from HTTP responses. Hurl is particular as it can extract "high level" data, 
like applying a JSONPath or a XPath expression to a response body, but Hurl can also work on a lower HTTP level: thanks
to its [libcurl HTTP engine], you can extract SSL certificates attributes for instance:

```hurl
GET https://example.org
HTTP 200
[Captures]
cert_subject: certificate "Subject"
cert_issuer: certificate "Issuer"
cert_expire_date: certificate "Expire-Date"
cert_serial_number: certificate "Serial-Number"
```

With Hurl 6.1.0, we have added an [IP address query] that allows you to get the IP address from HTTP response:

```hurl
GET https://example.org/hello
HTTP 200
[Captures]
server_ip: ip
```

IP address are strings and can be tested like any other values:

```hurl
GET https://example.org/api/tests/4567
HTTP 200
[Asserts]
ip == "2001:0db8:85a3:0000:0000:8a2e:0370:733"
```

As a convenience, we have also added two new predicates [`isIpv4` and `isIpv6`]({% link _docs/asserting-response.md%}#ip-address-assert) 
that perform format check on string values. For instance, you can set a request to [use IPv6 addresses]({% link _docs/manual.md %}#ipv6) 
and check that the response IP is well in the expected protocol:

```hurl
GET https://example.org/foo
[Options]
ipv6: true
HTTP 200
[Asserts]
ip isIpv6
```

With prior Hurl versions, user have been able to test response [HTTP version] with `HTTP/1.0`, `HTTP/1.1`, `HTTP/2`, `HTTP/3`:

```hurl
GET https://example.org/http3
HTTP/3 200

GET https://example.org/http2
HTTP/2 200

# Or simply use HTTP to not test version!
GET https://example.org/http2
HTTP 200
```

With Hurl 6.1.0, we have added the query `version`, that allows to explicitly test HTTP versions, or even to capture its
value:

```hurl
# You can explicitly test HTTP version 1.0, 1.1, 2 or 3:
GET https://example.org/http3
HTTP 200
[Asserts]
version == "3"

GET https://example.org/http2
HTTP 200
[Asserts]
version toFloat >= 2.0

# You can even capture the HTTP version in a variable:
GET https://example.org/http2
HTTP 200
[Captures]
endpoint_version: version
```

## New Filters: base64Encode/Decode, toString

When extracting data from HTTP response, you can transform it with [filters]. With Hurl 6.1.0, we have added three 
new filters:

- `base64Encode/base64Decode`: as the name suggests, these filters allow to encode and decode data with [Base64 encoding]
  (standard variant with `=` padding and `+/` characters):

```hurl
GET https://example.org/api
HTTP 200
[Asserts]
jsonpath "$.token" base64Decode == hex,e4bda0e5a5bde4b896e7958c;
```

- `toString`: allow to transforms value to a string

```hurl
GET https://example.org/foo
HTTP 200
[Asserts]
status toString matches /(200|204)/
```

## More curl Options

Finally, a last small evolution. Hurl adopts a lot of curl options, whether in command line:

```shell
$ hurl --location bar.hurl
```

Or in [`[Options]` section]({% link _docs/request.md %}#options):

```hurl
GET https://bar.com
[Options]
location: true
HTTP 200
```

With this new version, we have added [`--header`]({% link _docs/manual.md %}#header) option, that will add a specific HTTP header to all requests of a run: 

```shell
$ hurl --header 'x-header-b:baz' --header 'x-header-c:qux' foo.hurl
```

__That's all for today!__

There are a lot of other improvements with Hurl 6.1.0 and also a lot of bug fixes, you can check the complete list of 
enhancements and bug fixes [in our release note].

If you like Hurl, don't hesitate to [give us a star on GitHub] or share it on [𝕏 / Twitter] / [Bluesky]!

We'll be happy to hear from you, either for enhancement requests or for sharing your success story using Hurl!


[Hurl 6.1.0]: https://github.com/Orange-OpenSource/hurl/releases/tag/6.1.0
[Hurl]: https://hurl.dev
[curl]: https://curl.se
[to use a variable]: {% link _docs/templates.md %}#injecting-variables
[GitHub Actions]: https://github.com/features/actions
[GitLab CI/CD]: https://docs.gitlab.com/ci/
[to capture]: {% link _docs/capturing-response.md %}
[assert data]: {% link _docs/asserting-response.md %}
[libcurl HTTP engine]: https://curl.se/libcurl/
[IP address query]: {% link _docs/asserting-response.md %}#ip-address-assert
[use IPv6 addresses]: {% link _docs/manual.md %}#ipv6
[HTTP version]: {% link _docs/asserting-response.md %}#version-status
[filters]: {% link _docs/filters.md %}
[HTML]: {% link _docs/running-tests.md %}#html-report
[JSON]: {% link _docs/running-tests.md %}#json-report
[JUnit]: {% link _docs/running-tests.md %}#junit-report
[Base64 encoding]: https://en.wikipedia.org/wiki/Base64
[in our release note]: https://github.com/Orange-OpenSource/hurl/releases/tag/6.1.0
[𝕏 / Twitter]: https://x.com/HurlDev
[Bluesky]: https://bsky.app/profile/hurldev.bsky.social
[give us a star on GitHub]: https://github.com/Orange-OpenSource/hurl/stargazers
