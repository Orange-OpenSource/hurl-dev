---
title: Announcing Hurl 1.8.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

The Hurl team is happy to announce [Hurl 1.8.0] <img class="emoji" src="{{ '/assets/img/emoji-partying-face.png' | prepend:site.baseurl }}" width="20" height="20" alt="Partying Face">!
.

[Hurl] is a command line tool powered by [curl], that runs HTTP requests defined 
in a __simple plain text format__:

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

Hurl can be used to get data like [curl], or as a __testing tool for JSON/XML apis__ and HTML content.

So, __what's new in 1.8.0__?

- [Polling and Retry]
- [URL Assert](#url-assert)
- [curl Debug Logs]

## Polling and Retry

You can now __retry requests__ which asserts and captures have failed. This way, you can write
__polling scenarios__ or create robust tests even in flaky conditions. To activate retry, you can either use [`--retry` option] (every request of the run can be retried), or you can target a specific request with an [`[Options]` section][options]. 

Let's say we have an API to create a ressource. Once created, we want to poll this resource and wait until it reaches
a certain state.

First we create a new resource with a `POST` request. We capture the id of the resource to be able to use it 
in the following requests:

```hurl
# Create a new job
POST https://api.example.org/jobs

HTTP/* 201
[Captures]
job_id: jsonpath "$.id"
[Asserts]
jsonpath "$.state" == "RUNNING"
````

Then, we pull the resource with a `GET` request and check its `state` value. We've configured the `GET` request to 
be retried with an [`[Options]` section][options]. The [JSONPath assert] tests the value of `state` field. Because
of the retry option, the `GET` request is going to be retried until `state`'s value is `COMPLETED`:

```hurl
# ...

# Pull job status until it is completed
GET https://api.example.org/jobs/{{job_id}}
[Options]
retry: true

HTTP/* 200
[Asserts]
jsonpath "$.state" == "COMPLETED"
```

So, the full scenario looks like:

```hurl
# Create a new job
POST https://api.example.org/jobs

HTTP/* 201
[Captures]
job_id: jsonpath "$.id"
[Asserts]
jsonpath "$.state" == "RUNNING"


# Pull job status until it is completed
GET https://api.example.org/{{job_id}}
[Options]
retry: true

HTTP/* 200
[Asserts]
jsonpath "$.state" == "COMPLETED"
```

Retry work on any asserts, whether they're explicit (with an [`[Asserts]` section][asserts]), or implicit (the [status code]). For instance, the following snippet:

```hurl
GET https://api.example.org/123456
[Options]
retry: true
retry-interval: 4000
HTTP/* 200
```

will poll until `https://api.example.org/123456` returns a `200 OK`, with a 4 seconds delay between each retry.

Finally, one common need in shell script is to wait until a specific URL is ready and returns a 200 OK. This can be
easily done now with Hurl:

```shell
$ echo -e 'GET https://example.org/health\nHTTP/* 200' | hurl --retry
```

## URL Assert

The [URL assert] allows check on the final URL of a request: it's particularly interesting when you tell Hurl to follow
redirects (either with [`--location` option] or with an [`Options` section][options]):

```hurl
# Check that HTTP is redirected to HTTPS:
GET http://example.org
[Options]
location: true

HTTP/* 200
[Asserts]
url == "https://example.org"
```


## curl Debug Logs

In Hurl 1.7.0, we introduced [`--very-verbose` option] to output request and response bodies. Now, when `very-verbose` is used, Hurl displays debug logs from libcurl (prefixed with `**`), allowing displaying SSL certificates infos for instance:

```shell
$ echo 'HEAD https://hurl.dev' | hurl --very-verbose
[1;34m*[0m [1mOptions:[0m
[1;34m*[0m     fail fast: true
[1;34m*[0m     follow redirect: false
[1;34m*[0m     insecure: false
[1;34m*[0m     max redirect: 50
[1;34m*[0m     retry: false
[1;34m*[0m     retry max count: 10
[1;34m*[0m [1m------------------------------------------------------------------------------[0m
[1;34m*[0m [1mExecuting entry 1[0m
[1;34m*[0m
[1;34m*[0m [1mCookie store:[0m
[1;34m*[0m
[1;34m*[0m [1mRequest:[0m
[1;34m*[0m HEAD https://hurl.dev
[1;34m*[0m
[1;34m*[0m Request can be run with the following curl command:
[1;34m*[0m curl 'https://hurl.dev' --head
[1;34m*[0m
[1;34m**[0m [32m  Trying 145.239.78.213:443...[0m
[1;34m**[0m [32mConnected to hurl.dev (145.239.78.213) port 443 (#0)[0m
[1;34m**[0m [32mALPN, offering h2[0m
[1;34m**[0m [32mALPN, offering http/1.1[0m
[1;34m**[0m [32msuccessfully set certificate verify locations:[0m
[1;34m**[0m [32m CAfile: /etc/ssl/cert.pem[0m
[1;34m**[0m [32m CApath: none[0m
[1;34m**[0m [32m(304) (OUT), TLS handshake, Client hello (1):[0m
[1;34m**[0m [32m(304) (IN), TLS handshake, Server hello (2):[0m
[1;34m**[0m [32mTLSv1.2 (IN), TLS handshake, Certificate (11):[0m
[1;34m**[0m [32mTLSv1.2 (IN), TLS handshake, Server key exchange (12):[0m
[1;34m**[0m [32mTLSv1.2 (IN), TLS handshake, Server finished (14):[0m
[1;34m**[0m [32mTLSv1.2 (OUT), TLS handshake, Client key exchange (16):[0m
[1;34m**[0m [32mTLSv1.2 (OUT), TLS change cipher, Change cipher spec (1):[0m
[1;34m**[0m [32mTLSv1.2 (OUT), TLS handshake, Finished (20):[0m
[1;34m**[0m [32mTLSv1.2 (IN), TLS change cipher, Change cipher spec (1):[0m
[1;34m**[0m [32mTLSv1.2 (IN), TLS handshake, Finished (20):[0m
[1;34m**[0m [32mSSL connection using TLSv1.2 / ECDHE-RSA-CHACHA20-POLY1305[0m
[1;34m**[0m [32mALPN, server accepted to use h2[0m
[1;34m**[0m [32mServer certificate:[0m
[1;34m**[0m [32m subject: CN=hurl.dev[0m
[1;34m**[0m [32m start date: Sep 30 22:15:32 2022 GMT[0m
[1;34m**[0m [32m expire date: Dec 29 22:15:31 2022 GMT[0m
[1;34m**[0m [32m subjectAltName: host "hurl.dev" matched cert's "hurl.dev"[0m
[1;34m**[0m [32m issuer: C=US; O=Let's Encrypt; CN=R3[0m
[1;34m**[0m [32m SSL certificate verify ok.[0m
[1;34m**[0m [32mUsing HTTP2, server supports multiplexing[0m
[1;34m**[0m [32mConnection state changed (HTTP/2 confirmed)[0m
[1;34m**[0m [32mCopying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0[0m
[1;34m**[0m [32mUsing Stream ID: 1 (easy handle 0x14c811800)[0m
> [1;35mHEAD / HTTP/2[0m
> [1;36mHost[0m: hurl.dev
> [1;36maccept[0m: */*
> [1;36muser-agent[0m: hurl/1.8.0-SNAPSHOT
>
[1;34m*[0m [1mRequest body:[0m
[1;34m*[0m
[1;34m**[0m [32mConnection state changed (MAX_CONCURRENT_STREAMS == 128)![0m
[1;34m**[0m [32mConnection #0 to host hurl.dev left intact[0m
[1;34m*[0m [1mResponse: (received 0 bytes in 110 ms)[0m
[1;34m*[0m
< [1;32mHTTP/2 200[0m
< [1;36mserver[0m: nginx/1.14.2
< [1;36mdate[0m: Mon, 31 Oct 2022 13:12:41 GMT
< [1;36mcontent-type[0m: text/html
< [1;36mcontent-length[0m: 28370
< [1;36mlast-modified[0m: Thu, 27 Oct 2022 14:15:30 GMT
< [1;36metag[0m: "635a9282-6ed2"
< [1;36maccept-ranges[0m: bytes
<
[1;34m*[0m [1mResponse body:[0m
[1;34m*[0m
[1;34m*[0m
```

## That's All

If you like Hurl, don't hesitate to [give us a star on GitHub] or share it on [Twitter]! 

We'll be happy to hear from you, either for enhancement requests or for sharing your success story using Hurl!

[Hurl]: https://hurl.dev
[curl]: https://curl.se
[Polling and Retry]: #polling-and-retry
[URL Assert]: {% link _docs/asserting-response.md %}#url-assert
[curl Debug Logs]: #libcurl-debug-logs
[Hurl 1.8.0]: https://github.com/Orange-OpenSource/hurl/releases/tag/1.8.0
[`--retry` option]: {% link _docs/manual.md %}#retry
[`--location` option]: {% link _docs/manual.md %}#location
[`--very-verbose` option]: {% link _docs/manual.md %}#very-verbose
[options]: {% link _docs/request.md %}#options
[asserts]: {% link _docs/asserting-response.md %}#asserts
[JSONPath assert]: {% link _docs/asserting-response.md %}#jsonpath-assert
[status code]: {% link _docs/asserting-response.md %}#version-status
[give us a star on GitHub]: https://github.com/Orange-OpenSource/hurl/stargazers
[Twitter]: https://twitter.com/HurlDev