---
layout: doc
title: Response
section: File Format
---
# Response

## Definition

Responses can be used to capture values to perform subsequent requests, or add asserts to HTTP responses. Response on
requests are optional, a Hurl file can only be a sequence of [requests].

A response describes the expected HTTP response, with mandatory [version and status], followed by optional [headers],
[captures], [asserts] and [body]. Assertions in the expected HTTP response describe values of the received HTTP response.
Captures capture values from the received HTTP response and populate a set of named variables that can be used
in the following entries.

## Example

{% raw %}
```hurl
GET https://example.org

HTTP/1.1 200
Last-Modified: Wed, 21 Oct 2015 07:28:00 GMT
[Asserts]
xpath "normalize-space(//head/title)" startsWith "Welcome"
xpath "//li" count == 18
```
{% endraw %}


## Structure

<div class="hurl-structure-schema">
  <div class="hurl-structure">
    <div class="hurl-structure-col-0">
        <div class="hurl-part-0">
            HTTP/1.1 *
        </div>
        <div class=" hurl-part-1">
            content-length: 206<br>accept-ranges: bytes<br>user-agent: Test
        </div>
        <div class="hurl-part-2">
            [Captures]<br>...
        </div>
        <div class="hurl-part-2">
            [Asserts]<br>...
        </div>
        <div class="hurl-part-3">
            {<br>
            &nbsp;&nbsp;"type": "FOO",<br>
            &nbsp;&nbsp;"value": 356789,<br>
            &nbsp;&nbsp;"ordered": true,<br>
            &nbsp;&nbsp;"index": 10<br>
            }
        </div>
    </div>
    <div class="hurl-structure-col-1">
        <div class="hurl-request-explanation-part-0">
            <a href="/docs/asserting-response.html#version-status">Version and status (mandatory if response present)</a>
        </div>
        <div class="hurl-request-explanation-part-1">
            <br><a href="/docs/asserting-response.html#headers">HTTP response headers</a> (optional)
        </div>
        <div class="hurl-request-explanation-part-2">
            <br>
            <br>
        </div>
        <div class="hurl-request-explanation-part-2">
            <a href="/docs/capturing-response.html">Captures</a> and <a href="/docs/asserting-response.html#asserts">asserts</a> (optional sections, unordered)
        </div>
        <div class="hurl-request-explanation-part-2">
          <br>
          <br>
          <br>
          <br>
        </div>
        <div class="hurl-request-explanation-part-3">
            <a href="/docs/asserting-response.html#body">HTTP response body</a> (optional)
        </div>
    </div>
</div>
</div>


## Capture and Assertion

With the response section, one can optionally [capture value from headers, body],
or [add assert on status code, body or headers].

### Body compression

Hurl outputs the raw HTTP body to stdout by default. If response body is compressed (using [br, gzip, deflate]),
the binary stream is output, without any modification. One can use [`--compressed` option]
to request a compressed response and automatically get the decompressed body.

Captures and asserts work automatically on the decompressed body, so you can request compressed data (using [`Accept-Encoding`]
header by example) and add assert and captures on the decoded body as if there weren't any compression.


[requests]: {% link _docs/request.md %}
[version and status]: {% link _docs/asserting-response.md %}#url
[headers]: {% link _docs/asserting-response.md %}#headers
[captures]: {% link _docs/capturing-response.md %}#captures
[asserts]: {% link _docs/asserting-response.md %}#asserts
[body]: {% link _docs/asserting-response.md %}#body
[capture value from headers, body]: {% link _docs/capturing-response.md %}
[add assert on status code, body or headers]: {% link _docs/asserting-response.md %}
[br, gzip, deflate]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding
[`--compressed` option]: {% link _docs/man-page.md %}#compressed
[`Accept-Encoding`]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding
