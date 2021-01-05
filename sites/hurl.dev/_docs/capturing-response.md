---
layout: doc
title: Capturing Response
---

# {{ page.title }}

## Captures {#captures}

Captures are optional values captured from the HTTP response, in a named variable. Captures can be the
 response status code, part or the entire of the body, and response headers.

Captured variables are available through a run session; each new value of a given variable overrides the last value.

Captures allow using data from one request to another request, when working with
[CSRF tokens](https://en.wikipedia.org/wiki/Cross-site_request_forgery) for instance. Variables can also be initialized
at the start of the session, by passing [variable values]({% link _docs/man-page.md %}#variable),
or can used in [templates]({% link _docs/templates.md %})

{% raw %}
```hurl
# An example to show how to pass a CSRF token from one request
# to another:

# First GET request to get CSRF token value:
GET https://example.net

HTTP/1.1 200
# Capture the CSRF token value from html body.
[Captures]
csrf_token: xpath "normalize-space(//meta[@name='_csrf_token']/@content)"

# Do the login !
POST https://acmecorp.net/login?user=toto&password=1234
X-CSRF-TOKEN: {{csrf_token}}

HTTP/1.1 302
```
{% endraw %}

Structure of a capture:

<div class="drawing">
<picture>
    <source srcset="{{ '/assets/img/capture-dark.svg' | prepend:site.baseurl }}" media="(prefers-color-scheme: dark)" width="300px">
    <img src="{{ '/assets/img/capture-light.svg' | prepend:site.baseurl }}" width="300px"/>
</picture>
</div>

A capture consists of a variable name, followed by `:` and a query. The captures section starts with `[Captures]`.


### Query {#query}

Query can be of the following type:

- [`status`](#status-capture)
- [`header`](#header-capture)
- [`cookie`](#cookie-capture)
- [`body`](#body-capture)
- [`xpath`](#xpath-capture)
- [`jsonpath`](#jsonpath-capture)
- [`regex`](#regex-capture)
- [`variable`](#variable-capture)
- [`duration`](#duration-capture)


### Status capture {#status-capture}

Capture the received HTTP response status code. Status capture consists of a variable name, followed by a `:`, and the
keyword `status`.

```hurl
GET https://example.net

HTTP/1.1 200
[Captures]
my_status: status
```

### Header capture {#header-capture}

Capture a header from the received HTTP response headers. Header capture consists of a variable name, followed by a `:`,
 then the keyword `header` and a header name.

```hurl
POST https://example.net/login
[FormParams]
user: toto
password: 12345678

HTTP/1.1 302
[Captures]
next_url: header "Location"
```

### Cookie capture {#cookie-capture}

Capture a [`Set-Cookie`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie) header from the received
HTTP response headers. Cookie capture consists of a variable name, followed by a `:`, then the keyword `cookie` and a
 cookie name.

```hurl
GET http://example.net/cookies/set

HTTP/1.0 200
[Captures]
session-id: cookie "LSID"
```

Cookie attributes value can also be captured by using the following format: `<cookie-name>[cookie-attribute]`. The
 following attributes are supported: `Value`, `Expires`, `Max-Age`, `Domain`, `Path`, `Secure`, `HttpOnly` and
 `SameSite`.

```hurl
GET http://example.net/cookies/set

HTTP/1.0 200
[Captures]
value1: cookie "LSID"
value2: cookie "LSID[Value]"     # Equivalent to the previous capture
expires: cookie "LSID[Expires]"
max-age: cookie "LSID[Max-Age]"
domain: cookie "LSID[Domain]"
path: cookie "LSID[Path]"
secure: cookie "LSID[Secure]"
http-only: cookie "LSID[HttpOnly]"
same-site: cookie "LSID[SameSite]"
```


### Body capture {#body-capture}

Capture the entire body (decoded as text) from the received HTTP response

```hurl
GET https://example.net/home

HTTP/1.1 200
[Captures]
my_body: body
```

### XPath capture {#xpath-capture}

Capture a [XPath](https://en.wikipedia.org/wiki/XPath) query from the received HTTP body decoded as a string.
Currently, only XPath 1.0 expression can be used.

{% raw %}
```hurl
GET https://example.net/home

# Capture the identifier from the dom node <div id="pet0">5646eaf23</div
HTTP/1.1 200
[Captures]
ped-id: xpath "normalize-space(//div[@id='pet0'])"

# Open the captured page.
GET https://example.net/home/pets/{{pet-id}}

HTTP/1.1 200
```
{% endraw %}

XPath captures are not limited to node values (like string, or boolean); any valid XPath can be captured
and assert with variable asserts.

```hurl
# Test that the XML endpoint return 200 pets
GET https://api.example.net/pets
HTTP/* 200
[Captures]
pets: xpath "//pets"
[Asserts]
variable "pets" countEquals 200
```


### JSONPath capture {#jsonpath-capture}

Capture a [JSONPath](https://goessner.net/articles/JsonPath/) query from the received HTTP body.

{% raw %}
```hurl
POST https://example.net/api/contact
[FormParams]
token: {{token}}
email: toto@rookie.net

HTTP/1.1 200
[Captures]
contact-id: jsonpath "$['id']"
```
{% endraw %}

> Explain that the value selected by the JSONPath is coerced to a string when only one node is selected.

As with [XPath captures](#xpath-capture), JSONPath captures can be anything from string, number, to object and collections.
For instance, if we have a JSON endpoint that returns the following JSON:

```
{
  "a_null": null,
  "an_object": {
    "id": "123"
  },
  "a_list": [
    1,
    2,
    3
  ],
  "an_integer": 1,
  "a float": 1.1,
  "a_bool": true,
  "a_string": "hello"
}
```

We can capture the following paths:

```hurl
GET http://sample.org/captures-json
HTTP/1.0 200
[Captures]
an_object:  jsonpath "$['an_object']"
a_list:     jsonpath "$['a_list']"
a_null:     jsonpath "$['a_null']"
an_integer: jsonpath "$['an_integer']"
a_float:    jsonpath "$['a_float']"
a_bool:     jsonpath "$['a_bool']"
a_string:   jsonpath "$['a_string']"
all:        jsonpath "$"
```


### Regex capture {#regex-capture}

Capture a regex pattern from the HTTP received body, decoded as text.

```hurl
GET https://sample.org/helloworld

HTTP/1.0 200
[Captures]
id_a: regex "id_a:([0-9]+)!"
id_b: regex "id_b:(\\d+)!"
name: regex "Hello ([a-zA-Z]+)!"
```

Pattern of the regex query must have at least one capture group, otherwise the capture will fail.
Special characters beginning with a backslash in the pattern (like `\d`, `\s`) must be escaped: `regex "(\\d+)!"`
will capture one or more digit.

> raw string for specifying pattern could be used in a future version.

### Variable capture {#variable-capture}

### Duration capture {#duration-capture}

Capture the response time of the request in ms.

```hurl
GET https://sample.org/helloworld

HTTP/1.0 200
[Captures]
duration_in_ms: duration

```
### Subquery {#subquery}

Optionally, the query can be refined using a subquery. Currently, only `regex` are supported:

 <div class="drawing">
 <picture>
     <source srcset="{{ '/assets/img/subquery-dark.svg' | prepend:site.baseurl }}" media="(prefers-color-scheme: dark)" width="400px">
     <img src="{{ '/assets/img/subquery-light.svg' | prepend:site.baseurl }}" width="400px"/>
 </picture>
 </div>



