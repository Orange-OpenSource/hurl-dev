---
title: Announcing Hurl 1.7.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

The Hurl team is happy to announce [a new version of Hurl, 1.7.0].

[Hurl] is a command line tool powered by [curl], that runs HTTP requests defined 
in a simple plain text format:

```hurl
# Get home:
GET https://example.org

HTTP/1.1 200
[Captures]
csrf_token: xpath "string(//meta[@name='_csrf_token']/@content)"

# Do login!
POST https://example.org/login?user=toto&password=1234
X-CSRF-TOKEN: {{csrf_token}}

HTTP/1.1 302
```

Hurl can be used to get data like curl, or as an integration testing tool for JSON/XML HTTP apis / HTML content.

So, __what's new in 1.7.0__?

- [Verbose output improvement]
- [Use level request options]
- [Using Hurl in Node.js]
- [Support for XML namespace in XPath]
- [Others...]

## Verbose Output Improvement

We've improved [`-v/--verbose` option]:

- add more color!
- add [`--very-verbose` option] to output request and response body for each entry of your Hurl file 

First, we've added more color to the debug output.

In 1.6.1, a verbose output of Hurl looks like:

```shell
$ echo 'GET https://google.fr' | hurl --verbose
* fail fast: true
* insecure: false
* follow redirect: false
* max redirect: 50
* ------------------------------------------------------------------------------
* executing entry 1
* 
* Cookie store:
* 
* Request
* GET https://google.fr
* 
* request can be run with the following curl command:
* curl 'https://google.fr'
*
> GET / HTTP/2
> Host: google.fr
> accept: */*
> user-agent: hurl/1.6.1
> 
< HTTP/2 301 
< location: https://www.google.fr/
< content-type: text/html; charset=UTF-8
< date: Thu, 18 Aug 2022 09:55:23 GMT
< expires: Thu, 18 Aug 2022 09:55:23 GMT
< cache-control: private, max-age=2592000
< server: gws
< content-length: 219
< x-xss-protection: 0
< x-frame-options: SAMEORIGIN
< set-cookie: CONSENT=PENDING+677; expires=Sat, 17-Aug-2024 09:55:23 GMT; path=/; domain=.google.fr; Secure
< p3p: CP="This is not a P3P policy! See g.co/p3phelp for more info."
< alt-svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000,h3-Q050=":443"; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; ma=2592000,quic=":443"; ma=2592000; v="46,43"
< 
* 
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="https://www.google.fr/">here</A>.
</BODY></HTML>
```

In 1.7.0, headers are highlighted and requests and responses are more visible: 

```shell
$ echo 'GET https://google.fr' | hurl --verbose
[1;34m*[0m [1mOptions:[0m
[1;34m*[0m     fail fast: true
[1;34m*[0m     insecure: false
[1;34m*[0m     follow redirect: false
[1;34m*[0m     max redirect: 50
[1;34m*[0m [1m------------------------------------------------------------------------------[0m
[1;34m*[0m [1mExecuting entry 1[0m
[1;34m*[0m
[1;34m*[0m [1mCookie store:[0m
[1;34m*[0m
[1;34m*[0m [1mRequest:[0m
[1;34m*[0m GET https://google.fr
[1;34m*[0m
[1;34m*[0m Request can be run with the following curl command:
[1;34m*[0m curl 'https://google.fr'
[1;34m*[0m
> [1;35mGET / HTTP/2[0m
> [1;36mHost[0m: google.fr
> [1;36maccept[0m: */*
> [1;36muser-agent[0m: hurl/1.7.0-snapshot
>
[1;34m*[0m [1mResponse: (received 219 bytes in 111 ms)[0m
[1;34m*[0m
< [1;32mHTTP/2 301[0m
< [1;36mlocation[0m: https://www.google.fr/
< [1;36mcontent-type[0m: text/html; charset=UTF-8
< [1;36mdate[0m: Thu, 18 Aug 2022 09:56:40 GMT
< [1;36mexpires[0m: Thu, 18 Aug 2022 09:56:40 GMT
< [1;36mcache-control[0m: private, max-age=2592000
< [1;36mserver[0m: gws
< [1;36mcontent-length[0m: 219
< [1;36mx-xss-protection[0m: 0
< [1;36mx-frame-options[0m: SAMEORIGIN
< [1;36mset-cookie[0m: CONSENT=PENDING+308; expires=Sat, 17-Aug-2024 09:56:40 GMT; path=/; domain=.google.fr; Secure
< [1;36mp3p[0m: CP="This is not a P3P policy! See g.co/p3phelp for more info."
< [1;36malt-svc[0m: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000,h3-Q050=":443"; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; ma=2592000,quic=":443"; ma=2592000; v="46,43"
<
[1;34m*[0m
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="https://www.google.fr/">here</A>.
</BODY></HTML>
```

Error on asserts are also colored now:

```shell
[1;31merror[0m: [1mAssert status code[0m
  [1;34m-->[0m /tmp/test.hurl:2:8
   [1;34m|[0m
[1;34m 2[0m [1;34m|[0m HTTP/* 200
   [1;34m|[0m        [1;31m^^^[0m [1;31mactual value is <301>[0m
   [1;34m|[0m
```

Colors can be forced with [`--color`], or deactivated with [`--no-color`], and Hurl supports now `NO_COLOR` environnement
variables (see <http://no-color.org>).

Secondly, intermediary request and response bodies can be outputted in debug with [`--very-verbose` option]. By default, 
the last HTTP body response is outputted on standard output (like [curl]). With [`--verbose` option], request and response 
headers are also displayed on standard error, and with [`--very-verbose` option], request and response bodies are finally also
displayed on standard error. If your Hurl file has a lot of entries, debug logs can be pretty large, but you can mitigate it
with the brand new `[Options]` section that we're going to present now.

## Use Level Request Options

Options such as [`--location`], [`--verbose`], [`--insecure`] can be used at the command line and applied to every
request of an Hurl file. An `[Options]` section can be used to apply option to only one request (without passing options
to the command line), while other requests are unaffected.

```hurl
GET https://example.org
# An options section, each option is optional and applied only to this request...
[Options]
cacert: /etc/cert.pem   # a custom certificate file
compressed: true        # request a compressed response
insecure: true          # allows insecure SSL connections and transfers
location: true          # follow redirection for this request
max-redirs: 10          # maximum number of redirections
verbose: true           # allow verbose output
very-verbose: true      # allow more verbose output    
```

So, given this Hurl file

```hurl
GET https://google.fr
HTTP/* 301

GET https://google.fr
[Options]
location: true
HTTP/* 200

GET https://google.fr
HTTP/* 301
```

The second entry will follow location (and so we can test the status code to be 200 instead of 301).

You can use it to logs a specific entry:

```hurl
# ... previous entries

GET https://api.example.org
[Options]
very-verbose: true

HTTP/* 200

# ... next entries
```

And only the debug logs of the specific entry will be displayed on standard error.

## Using Hurl in Node.js

Started since 1.6.1, Hurl is [available on npm], and can be easily integrated in various JavaScript projects.
Hurl on npm is a thin JavaScript wrapper around the native binary.

To install it, just run:

```shell
$ npm install --save-dev @orangeopensource/hurl
```

And then edit your `package.json`:

```json
{
  "name": "sample-app",
  "scripts": {
    "test": "hurl --test --glob test/*.hurl",
    ...
  },
  ...
```

Now you can run your integration tests with Hurl:

```shell
$ npm test
[1mtest/bar.hurl[0m: [1;36mRunning[0m [1/3]
[1mtest/bar.hurl[0m: [1;32mSuccess[0m (5 request(s) in 136 ms)
[1mtest/baz.hurl[0m: [1;36mRunning[0m [2/3]
[1;31merror[0m: [1mAssert failure[0m
  [1;34m-->[0m test/baz.hurl:6:0
   [1;34m|[0m
[1;34m 6[0m [1;34m|[0m xpath "string(//title)" == "Something"
   [1;34m|[0m   [1;31mactual:   string <301 Moved>[0m
   [1;34m|[0m   [1;31mexpected: string <Something>[0m
   [1;34m|[0m

[1mtest/baz.hurl[0m: [1;31mFailure[0m (4 request(s) in 62 ms)
[1mtest/foo.hurl[0m: [1;36mRunning[0m [3/3]
[1mtest/foo.hurl[0m: [1;32mSuccess[0m (10 request(s) in 527 ms)
--------------------------------------------------------------------------------
Executed files:  3
Succeeded files: 2 (66.7%)
Failed files:    1 (33.3%)
Duration:        766 ms
```

## Support for XML namespace in XPath

JSON and XML are first class citizens in Hurl with [JSONPath assert] and [XPath assert]. 
For XPath, we now support asserts with namespaces:

```xml
<?xml version="1.0"?>
<!-- both namespace prefixes are available throughout -->
<bk:book xmlns:bk='urn:loc.gov:books'
         xmlns:isbn='urn:ISBN:0-395-36341-6'>
    <bk:title>Cheaper by the Dozen</bk:title>
    <isbn:number>1568491379</isbn:number>
</bk:book>
```

Can be tested with the following Hurl file:

```hurl
GET http://localhost:8000/assert-xpath

HTTP/1.0 200
[Asserts]

xpath "string(//bk:book/bk:title)" == "Cheaper by the Dozen"
xpath "string(//*[name()='bk:book']/*[name()='bk:title'])" == "Cheaper by the Dozen"
xpath "string(//*[local-name()='book']/*[local-name()='title'])" == "Cheaper by the Dozen"

xpath "string(//bk:book/isbn:number)" == "1568491379"
xpath "string(//*[name()='bk:book']/*[name()='isbn:number'])" == "1568491379"
xpath "string(//*[local-name()='book']/*[local-name()='number'])" == "1568491379"
```

For convenience, the first default namespace can be used with `_`.

This sample:

```xml
<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" 
              "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg xmlns="http://www.w3.org/2000/svg">
  <style type="text/css">
    circle:hover {fill-opacity:0.9;}
  </style>
  <g style="fill-opacity:0.7;">
    <circle cx="6.5cm" cy="2cm" r="100" style="fill:red; stroke:black; stroke-width:0.1cm" transform="translate(0,50)" />
    <circle cx="6.5cm" cy="2cm" r="100" style="fill:blue; stroke:black; stroke-width:0.1cm" transform="translate(70,150)" />
    <circle cx="6.5cm" cy="2cm" r="100" style="fill:green; stroke:black; stroke-width:0.1cm" transform="translate(-70,150)"/>
  </g>
</svg>
```

Can be tested with the following Hurl file:

```hurl
GET http://localhost:8000/assert-xpath-svg

HTTP/1.0 200
[Asserts]
xpath "//_:svg/_:g/_:circle" count == 3
xpath "//*[local-name()='svg']/*[local-name()='g']/*[local-name()='circle']" count ==  3
xpath "//*[name()='svg']/*[name()='g']/*[name()='circle']" count == 3
```

## Others...

Under the hood, we've improved our code and Hurl should be quicker than ever. We've completely 
rewritten [our grammar] to be more correct and support Hurl future evolutions.

There are other changes and bug fixes in the Hurl 1.7.0 release: check out [the release note!]

And, finally, a big thanks to all our contributors!


[Hurl]: https://hurl.dev
[curl]: https://curl.se
[a new version of Hurl, 1.7.0]: https://github.com/Orange-OpenSource/hurl/releases/tag/1.7.0
[`-v/--verbose` option]: {% link _docs/manual.md %}#verbose
[`--verbose` option]: {% link _docs/manual.md %}#verbose
[`--very-verbose` option]: {% link _docs/manual.md %}#very-verbose
[`--verbose`]: {% link _docs/manual.md %}#verbose
[`--very-verbose`]: {% link _docs/manual.md %}#very-verbose
[`--insecure`]: {% link _docs/manual.md %}#insecure
[`--location`]: {% link _docs/manual.md %}#location
[`--color`]: {% link _docs/manual.md %}#color
[`--no-color`]: {% link _docs/manual.md %}#no-color
[available on npm]: https://www.npmjs.com/package/@orangeopensource/hurl
[Verbose output improvement]: #verbose-output-improvement
[Use level request options]: #use-level-request-options
[Using Hurl in Node.js]: #using-hurl-in-nodejs
[Support for XML namespace in XPath]: #support-for-xml-namespace-in-xpath
[Others...]: #others
[XPath assert]: {% link _docs/asserting-response.md %}#xpath-assert
[JSONPath assert]: {% link _docs/asserting-response.md %}#jsonpath-assert
[the release note!]: https://github.com/Orange-OpenSource/hurl/releases/tag/1.7.0
[our grammar]: {% link _docs/grammar.md %}
