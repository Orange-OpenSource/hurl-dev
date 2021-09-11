---
layout: doc
title: Asserting Response
section: File Format
---

# {{ page.title }}

## Version - Status {#version-status}

Expected protocol version and status code of the HTTP response. 

Protocol version is one of `HTTP/1.0`, `HTTP/1.1`, `HTTP/2` or
`HTTP/*`; `HTTP/*` describes any version. Note that there are no status text following the status code.

```hurl
GET http://example.net/404.html

HTTP/1.0 404
```

Wildcard keywords (`HTTP/*`, `*`) can be used to disable tests on protocol version and status:

```hurl
GET http://api/.example.net/pets

HTTP/1.0 *
# Check that response status code is > 400 and <= 500
[Asserts]
status > 400
status <= 500
```
 

## Headers {#headers} 

Optional list of the expected HTTP response headers that must be in the received response. 

A header consists of a name, followed by a `:` and a value.

For each expected header, the received response headers are checked. If the received header is not equal to the expected,
or not present, an error is raised. Note that the expected headers list is not fully descriptive: headers present in the response
and not in the expected list doesn't raise error.

```hurl
# Check that user toto is redirected to home after login.
POST https://example.net/login
[FormParams]
user: toto
password: 12345678

HTTP/1.1 302
Location: https://example.net/home
```

> Quotes in the header value are part of the value itself.
>
> This is used by the [ETag](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag) Header
> ```
> ETag: W/"<etag_value>"
> ETag: "<etag_value>"
> ```


Testing duplicated headers is also possible.

For example with the Set-Cookie header:
 
```
Set-Cookie: theme=light
Set-Cookie: sessionToken=abc123; Expires=Wed, 09 Jun 2021 10:18:14 GMT
```

You can either test the two header values:

```hurl
GET http://www.example.org/index.html
Host: www.example.org

HTTP/1.0 200
Set-Cookie: theme=light
Set-Cookie: sessionToken=abc123; Expires=Wed, 09 Jun 2021 10:18:14 GMT
```

Or only one:

```hurl
GET http://www.example.org/index.html 
Host: www.example.org

HTTP/1.0 200
Set-Cookie: theme=light
```

If you want to test specifically the number of headers returned for a given header name, or
if you want to test header value with [predicates](#predicates) (like `startsWith`, `contains`, `exists`) 
you can use the explicit [header assert](#header-assert).


## Asserts {#asserts}

Optional list of assertions on the HTTP response. Assertions can describe checks on status code, 
on the received body (or part of it) and on response headers.

Structure of an assert:

<div class="schema-container schema-container u-font-size-1 u-font-size-2-sm u-font-size-3-md">
 <div class="schema">
   <span class="schema-token schema-color-2">jsonpath "$.book"<span class="schema-label">query</span></span>
   <span class="schema-token schema-color-1">contains<span class="schema-label">predicate type</span></span>
   <span class="schema-token schema-color-3">"Dune"<span class="schema-label">predicate value</span></span>
 </div>
</div>


An assert consists of a query followed by a predicate. The format of the query is shared with [captures](#captures), and 
can be one of :

- [`status`](#status-assert)
- [`header`](#header-assert)
- [`cookie`](#cookie-assert)
- [`body`](#body-assert)
- [`xpath`](#xpath-assert)
- [`jsonpath`](#jsonpath-assert)
- [`regex`](#regex-assert)
- [`variable`](#variable-assert)
- [`duration`](#duration-assert)

### Predicates {#predicates}

Predicates consist of a predicate function, and a predicate value. Predicate functions are:

- `equals`: check equality of query and predicate value
- `greaterThan`: check that query number is greater than predicate value  
- `greaterThanOrEquals`: check that query number is greater than or equal to the predicate value
- `lessThan`: check that query number is less than that predicate value
- `lessThanOrEquals`: check that query number is less than or equal to the predicate value   
- `countEquals`: check equality of query size collections
- `startsWith`: check that query string starts with the predicate value
- `contains`: check that query string contains the predicate value
- `includes`: check that query collections includes the predicate value
- `matches`: check that query string matches the regex pattern described by the predicate value
- `exists`: check that query returns a value
- `isInteger`: check that query returns an integer
- `isFloat`: check that query returns a float
- `isBoolean`: check that query returns a boolean
- `isString`: check that query returns a string
- `isCollection`: check that query returns a collection


Each predicate can be negated by prefixing it with `not` (for instance, `not contains` or `not exists`)

<div class="schema-container schema-container u-font-size-1 u-font-size-2-sm u-font-size-3-md">
 <div class="schema">
   <span class="schema-token schema-color-2">jsonpath "$.book"<span class="schema-label">query</span></span>
   <span class="schema-token schema-color-1">not contains<span class="schema-label">predicate type</span></span>
   <span class="schema-token schema-color-3">"Dune"<span class="schema-label">predicate value</span></span>
 </div>
</div>


A predicate values is typed, and can be a string, a boolean, a number, `null` or a collection. Note that `"true"` is a
 string, whereas `true` is a boolean.
  
For instance, to test the presence of a h1 node in an HTML response, the following assert can be used:

```hurl
GET https://example.net/home

HTTP/1.1 200
[Asserts]
xpath "boolean(count(//h1))" == true
xpath "//h1" exists # Equivalent but simpler
```

As the XPath query `boolean(count(//h1))` returns a boolean, the predicate value in the assert must be either
`true` or `false` without double quotes. On the other side, say you have an article node and you want to check the value of some 
[data attributes](https://developer.mozilla.org/en-US/docs/Learn/HTML/Howto/Use_data_attributes):

```xml
<article
  id="electric-cars"
  data-visible="true"
...
</article>
```

The following assert will check the value of the `data-visible` attribute:

```hurl
GET https://example.net/home

HTTP/1.1 200
[Asserts]
xpath "string(//article/@data-visible)" == "true"
```

In this case, the XPath query `string(//article/@data-visible)` returns a string, so the predicate value must be a
string.

The predicate function `equals` can work with string, number or boolean while `matches`, `startWith` and `contains` work
only on string. If a query returns a number, a `contains` predicate will raise a runner error.

```hurl
# A really well tested web page...
GET https://example.net/home

HTTP/1.1 200
[Asserts]
header "Content-Type" contains "text/html"
header "Last-Modified" == "Wed, 21 Oct 2015 07:28:00 GMT"
xpath "//h1" exists  # Check we've at least one h1
xpath "normalize-space(//h1)" contains "Welcome"
xpath "//h2" count == 13
xpath "string(//article/@data-id)" startsWith "electric"
```

### Status assert {#status-assert}

Check the received HTTP response status code. Status assert consists of the keyword `status` followed by a predicate
function and value. 

```hurl
GET https://example.net

HTTP/1.1 *
[Asserts]
status < 300
```

### Header assert {#header-assert}

Check the value of a received HTTP response header. Header assert consists of the keyword `header` followed by a predicate
function and value. 

```hurl
GET https://example.net

HTTP/1.1 302
[Asserts]
header "Location" contains "www.example.net"
```

### Cookie assert {#cookie-assert}

Check value or attributes of a [`Set-Cookie`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie
) response header. Cookie assert consists of the keyword `cookie`, followed by the cookie name (and optionally a cookie
attribute), a predicate function and value.

Cookie attributes value can be checked by using the following format: `<cookie-name>[cookie-attribute]`. The
 following attributes are supported: `Value`, `Expires`, `Max-Age`, `Domain`, `Path`, `Secure`, `HttpOnly` and
 `SameSite`.

```hurl
GET http://localhost:8000/cookies/set

HTTP/1.0 200

# Explicit check of Set-Cookie header value. If the attributes are
# not in this excat order, this assert will fail. 
Set-Cookie: LSID=DQAAAKEaem_vYg; Expires=Wed, 13 Jan 2021 22:23:01 GMT; Secure; HttpOnly; Path=/accounts; SameSite=Lax;
Set-Cookie: HSID=AYQEVnDKrdst; Domain=.localhost; Expires=Wed, 13 Jan 2021 22:23:01 GMT; HttpOnly; Path=/
Set-Cookie: SSID=Ap4PGTEq; Domain=.localhost; Expires=Wed, 13 Jan 2021 22:23:01 GMT; Secure; HttpOnly; Path=/

# Using cookie assert, one can check cookie value and various attributes.
[Asserts]
cookie "LSID" == "DQAAAKEaem_vYg"
cookie "LSID[Value]" == "DQAAAKEaem_vYg"
cookie "LSID[Expires]" exists
cookie "LSID[Expires]" contains "Wed, 13 Jan 2021"
cookie "LSID[Max-Age]" not exists
cookie "LSID[Domain]" not exists
cookie "LSID[Path]" == "/accounts"
cookie "LSID[Secure]" exists
cookie "LSID[HttpOnly]" exists
cookie "LSID[SameSite]" equals "Lax"
```

> `Secure` and `HttpOnly` attributes can only be tested with `exists` or `not exists` predicates
> to reflect the [Set-Cookie header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie) semantic.
> (in other words, queries `<cookie-name>[HttpOnly]` and `<cookie-name>[Secure]` don't return boolean) 

### Body assert {#body-assert}

Check the value of the received HTTP response body when decoded as a string. Body assert consists of the keyword `body` 
followed by a predicate function and value. The encoding used to decode the body is based on the `charset` value in the
`Content-Type` header response.

```hurl
GET https://example.net

HTTP/1.1 200
[Asserts]
body contains "<h1>Welcome!</h1>"
```

> Precise the encoding used to decode the text body. 

### XPath assert {#xpath-assert}

Check the value of a [XPath](https://en.wikipedia.org/wiki/XPath) query on the received HTTP body decoded as a string. 
Currently, only XPath 1.0 expression can be used. Body assert consists of the keyword `xpath` followed by a predicate
function and value. Values can be string, boolean or number depending on the XPath query.

Let's say we want to check this HTML response:
 
```plain
$ curl -v http://example.com/

< HTTP/1.1 200 OK
< Content-Type: text/html; charset=UTF-8
...
<!doctype html>
<html>
  <head>
    <title>Example Domain</title>
    ...
  </head>

  <body>
    <div>
      <h1>Example</h1>
      <p>This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.</p>
      <p><a href="https://www.iana.org/domains/example">More information...</a></p>
    </div>
  </body>
</html>
```

With Hurl, we can write multiple XPath asserts describing the DOM content:

```hurl
GET https://example.com

HTTP/1.1 200
Content-Type: text/html; charset=UTF-8

[Asserts]
xpath "string(/html/head/title)" contains "Example" # Check title
xpath "count(//p)" == 2                             # Check the number of p
xpath "//p" count == 2                              # Similar assert for p
xpath "boolean(count(//h2))" == false               # Check there is no h2  
xpath "//h2" not exists                             # Similar assert for h2 
```

### JSONPath assert {#jsonpath-assert}

Check the value of a [JSONPath](https://goessner.net/articles/JsonPath/) query on the received HTTP body decoded as a JSON
document. Body assert consists of the keyword `jsonpath` followed by a predicate function and value. 

Let's say we want to check this JSON response:

```plain
curl -v http://httpbin.org/json

< HTTP/1.1 200 OK
< Content-Type: application/json
...

{
  "slideshow": {
    "author": "Yours Truly",
    "date": "date of publication",
    "slides": [
      {
        "title": "Wake up to WonderWidgets!",
        "type": "all"
      },
       ...
    ],
    "title": "Sample Slide Show"
  }
}
```

With Hurl, we can write multiple JSONPath asserts describing the DOM content:


```hurl
GET http://httpbin.org/json

HTTP/1.1 200

[Asserts]
jsonpath "$.slideshow.author" == "Yours Truly"
jsonpath "$.slideshow.slides[0].title" contains "Wonder"
jsonpath "$.slideshow.slides" count == 2
jsonpath "$.slideshow.date" not == null
jsonpath "$.slideshow.slides[*].title" includes "Mind Blowing!"
```

> Explain that the value selected by the JSONPath is coerced to a string when only one node is selected.

### Regex assert {#regex-assert}

### Variable assert {#variable-assert}

```hurl
# Test that the XML endpoint return 200 pets 
GET https://api.example.net/pets
HTTP/* 200
[Captures]
pets: xpath "//pets"
[Asserts]
variable "pets" count == 200
```

### Duration assert {#duration-assert}

Check the total duration (sending plus receiving time) of the HTTP transaction.
 
```hurl
GET https://sample.org/helloworld

HTTP/1.0 200
[Asserts]
duration < 1000   # Check that response time is less than one second
```

## Body {#body}

Optional assertion on the received HTTP response body. Body section can be seen as syntactic sugar 
over [body asserts](#body-assert) (with `equals` predicate function). If the body of the response is a 
[JSON](https://www.json.org) string or a [XML](https://en.wikipedia.org/wiki/XML) string, 
the body assertion can be directly inserted without any modification. For a text based body that is not JSON nor XML, 
one can use multiline string that starts with <code>&#96;&#96;&#96;</code> and ends with <code>&#96;&#96;&#96;</code>. 
For a precise byte control of the response body, a [Base64](https://en.wikipedia.org/wiki/Base64) encoded string can be 
used to describe exactly the body byte content to check.

### JSON body {#json-body}

```hurl
# Get a doggy thing:
GET https://example.net/api/dogs/{{dog-id}}

HTTP/1.1 200
{
    "id": 0,
    "name": "Frieda",
    "picture": "images/scottish-terrier.jpeg",
    "age": 3,
    "breed": "Scottish Terrier",
    "location": "Lisco, Alabama"
}
```

### XML body {#xml-body}

~~~hurl
GET https://example.net/api/catalog

HTTP/1.1 200
<?xml version="1.0" encoding="UTF-8"?>
<catalog>
   <book id="bk101">
      <author>Gambardella, Matthew</author>
      <title>XML Developer's Guide</title>
      <genre>Computer</genre>
      <price>44.95</price>
      <publish_date>2000-10-01</publish_date>
      <description>An in-depth look at creating applications with XML.</description>
   </book>
</catalog>
~~~

### Raw string body {#raw-string-body}

~~~hurl
GET https://example.net/models

HTTP/1.1 200
```
Year,Make,Model,Description,Price
1997,Ford,E350,"ac, abs, moon",3000.00
1999,Chevy,"Venture ""Extended Edition""","",4900.00
1999,Chevy,"Venture ""Extended Edition, Very Large""",,5000.00
1996,Jeep,Grand Cherokee,"MUST SELL! air, moon roof, loaded",4799.00
```
~~~

The standard usage of a raw string is :

~~~
```
line1
line2
line3
```
~~~

is evaluated as "line1\nline2\nline3\n".


To construct an empty string :

~~~
```
```
~~~

or

~~~
``````
~~~


Finaly, raw string can be used without any newline:

~~~
```line``` 
~~~

is evaluated as "line".

### Base64 body {#base64-body}

Base64 body assert starts with `base64,` and end with `;`. MIME's Base64 encoding is supported (newlines and white spaces may be
 present anywhere but are to be ignored on decoding), and `=` padding characters might be added.

```hurl
GET https://example.net

HTTP/1.1 200
base64,TG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIGNvbnNlY3RldHVyIG
FkaXBpc2NpbmcgZWxpdC4gSW4gbWFsZXN1YWRhLCBuaXNsIHZlbCBkaWN0dW0g
aGVuZHJlcml0LCBlc3QganVzdG8gYmliZW5kdW0gbWV0dXMsIG5lYyBydXRydW
0gdG9ydG9yIG1hc3NhIGlkIG1ldHVzLiA=;
```

### File body {#file-body}

To use the binary content of a local file as the body response assert, file body can be used. File body starts with
`file,` and ends with `;``

```hurl
GET https://example.net

HTTP/1.1 200
file,data.bin;
```

File are relative to the input Hurl file, and cannot contain implicit parent directory (`..`). You can use  
[`--file-root` option]({% link _docs/man-page.md %}#file-root) to specify the root directory of all file nodes.
