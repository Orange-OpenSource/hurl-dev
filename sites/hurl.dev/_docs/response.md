---
layout: doc
title: Response
---
# {{ page.title }}

## Definition {#definition}

Responses can be used to capture values to perform subsequent requests, or add asserts to HTTP responses.

A response describes the expected HTTP response, with mandatory [version and status](#url), followed by optional [headers](#headers), 
[captures](#captures), [asserts](#asserts) and [body](#body). Assertions in the expected HTTP response describe values
of the received HTTP response. Captures capture values from the received HTTP response and populate a set of named
variables.


## Example {#example}

```hurl
GET http://example.net

HTTP/1.1 200
Last-Modified: Wed, 21 Oct 2015 07:28:00 GMT
[Asserts]
xpath "normalize-space(//head/title)" startsWith "Welcome"
xpath "//li" countEquals 18
```

## Capture and Assertion

With the response section, one can optionaly [capture value from headers, body]({% link _docs/capturing-response.md %}),
 or [add assert on status code, body or headers]({% link _docs/asserting-response.md %}).