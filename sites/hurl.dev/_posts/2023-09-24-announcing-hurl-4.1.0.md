---
title: Announcing Hurl 4.1.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

The Hurl team is happy to announce [Hurl 4.1.0] <picture><source srcset="{{ '/assets/img/rocket.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/rocket.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/rocket.png' | prepend:site.baseurl }}" type="image/png"><img class="emoji" src="{{ '/assets/img/rocket.png' | prepend:site.baseurl }}" width="20" height="20" alt="Rocket"></picture> !

[Hurl] is a command line tool powered by [curl], that runs HTTP requests defined
in a simple plain text format:

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

What's new in this release:

- [TAP Report](#tap-report)
- [Add Delay Between Requests](#add-delay-between-requests)
- [`--connect-to` and `--resolve` per Request Option](#-connect-to-and-resolve-per-request-option)
- [AWS Signature Version 4](#aws-signature-version-4)
- [ARM 64 bits Docker Image](#arm-64-bits-docker-image)

## TAP Report

We've added a new test report: TAP, the [Test Anything Protocol]. TAP is a simple text-based
interface between testing modules in a test harness. With [HTML report] and [JUnit report], Hurl supports now 
[TAP report].

Let's say we run some tests. We can use `--report-tap REPORT-FILE` option to set the report TAP file. If the report file
exists, results will be appended to it.

```shell
$ hurl --test --report-tap report.txt *.hurl
[1madd-favorite.hurl[0m: [1;36mRunning[0m [1/6]
[1madd-favorite.hurl[0m: [1;32mSuccess[0m (7 request(s) in 5516 ms)
[1mbasic.hurl[0m: [1;36mRunning[0m [2/6]
[1mbasic.hurl[0m: [1;32mSuccess[0m (7 request(s) in 1537 ms)
[1mcsrf.hurl[0m: [1;36mRunning[0m [3/6]
[1;31merror[0m: [1mAssert status code[0m
  [1;34m-->[0m csrf.hurl:3:6
   [1;34m|[0m
[1;34m 3[0m [1;34m|[0m HTTP 301
   [1;34m|[0m      [1;31m^^^[0m [1;31mactual value is <200>[0m
   [1;34m|[0m

[1mcsrf.hurl[0m: [1;31mFailure[0m (2 request(s) in 5527 ms)
[1mlogin.hurl[0m: [1;36mRunning[0m [4/6]
[1mlogin.hurl[0m: [1;32mSuccess[0m (3 request(s) in 3091 ms)
[1mperf.hurl[0m: [1;36mRunning[0m [5/6]
[1mperf.hurl[0m: [1;32mSuccess[0m (4 request(s) in 1317 ms)
[1msecurity.hurl[0m: [1;36mRunning[0m [6/6]
[1msecurity.hurl[0m: [1;32mSuccess[0m (5 request(s) in 2278 ms)
write tap report report.txt
--------------------------------------------------------------------------------
Executed files:  6
Succeeded files: 5 (83.3%)
Failed files:    1 (16.7%)
Duration:        19304 ms
```

Then, we can see what our TAP report looks like:

```shell
$ cat report.txt
1..6
ok 1 - add-favorite.hurl
ok 2 - basic.hurl
not ok 3 - csrf.hurl
ok 4 - login.hurl
ok 5 - perf.hurl
ok 6 - security.hurl
```

Simple and neat! TAP has wide support across many language and there are many tools that can convert TAP
to other formats, so it's a nice addition to Hurl!


## Add Delay Between Requests

With the new [`--delay` option]({% link _docs/manual.md %}#delay), you can add a delay between requests:

```shell
$ hurl --delay 2000 --test *.hurl
```

This command add a 2 seconds delay between each request. As with a lot of Hurl command line options, you
can specify a delay for a single request, with an [`[Options]` section]({% link _docs/request.md %}#options),
without impacting other requests:

```hurl
GET https://foo.com/a
HTTP 200

# This next request will be runned 5s after the
# first one
GET https://foo.com/b
[Options]
delay: 5000
HTTP 200
```

## --connect-to and --resolve per Request Option

Speaking of [`[Options]` sections]({% link _docs/request.md %}#options), [`--connect-to`]({% link _docs/manual.md %}#connect-to) 
and [`--resolve`]({% link _docs/manual.md %}#resolve) can now be specified per request:

```hurl
GET https://foo.com/a
[Options]
connect-to: foo.com:80:localhost:8000
HTTP 200

# --resolve option allow to us custom address for a specific host and port pair.
GET http://foo.com:8000/resolve
[Options]
resolve: foo.com:8000:127.0.0.1
HTTP 200
```

As of Hurl 4.1.0, the [`[Options]` section]({% link _docs/request.md %}#options) supports:

```hurl
GET https://example.org
# An options section, each option is optional and applied only to this request...
[Options]
aws-sigv4: aws:amz:sts  # generate AWS SigV4 Authorization header
cacert: /etc/cert.pem   # a custom certificate file
compressed: true        # request a compressed response
insecure: true          # allows insecure SSL connections and transfers
location: true          # follow redirection for this request
max-redirs: 10          # maximum number of redirections
path-as-is: true        # tell curl to not handle sequences of /../ or /./ in the given URL path
variable: country=Italy # define variable country
variable: planet=Earth  # define variable planet
verbose: true           # allow verbose output
very-verbose: true      # allow more verbose output
```

If you need an Hurl command line option (which make sense for a single request) to be on this list, don't 
hesitate to [fill an issue]!

## AWS Signature Version 4

Every interaction with Amazon S3 is either authenticated or anonymous. Authenticating to AWS 
is done through [AWS Signature Version 4]. With [`--aws-sigv4`]({% link _docs/manual.md %}#aws-sigv4), 
you can use AWS Signature Version 4 to authenticate your requests

```shell
$ hurl --user someAccessKeyId:someSecretKey \
 --aws-sigv4 aws:amz:eu-central-1:foo \
 file.hurl
```

And of course, `--aws-sigv4` can be specified for a single request:

```hurl
GET https://foo.execute-api.us-east-1.amazonas.com/dev/bafe12
[Options]
aws-sigv4: aws:amz:eu-central-1:foo
HTTP 200
```

## ARM 64 bits Docker Image

Hurl can be [installed as a native binary] on a large number of platforms. We also provide
a [Docker image]. Since 4.1.0, Hurl Docker's image is a [multi-arch build]: along x86 architectures, 
the image supports now ARM 64 bits targets such as Raspberry Pis, AWS A1 instances or even ARM's Apple computers.

```shell
$ docker run -v /tmp/:/tmp/ ghcr.io/orange-opensource/hurl:4.1.0 --test example.hurl
[1mexample.hurl[0m: [1;36mRunning[0m [1/1]
[1mexample.hurl[0m: [1;32mSuccess[0m (1 request(s) in 190 ms)
--------------------------------------------------------------------------------
Executed files:  1
Succeeded files: 1 (100.0%)
Failed files:    0 (0.0%)
Duration:        193 ms
```

## Others

Changes that require a particular attention:

- we have renamed `--fail-at-end` option to
[[`--continue-on-error`]]({% link _docs/manual.md %}#continue-on-error) as the latter is more
understandable
- we have fixed [[`--path-as-is`]]({% link _docs/manual.md %}#path-as-is) option name (instead of `--path_as_is`)

There are other improvements and bug fixes, you can check a complete list [in our release note].
If you like Hurl, don't hesitate to [give us a star on GitHub] or share it on [Twitter / X]!

We'll be happy to hear from you, either for enhancement requests or for sharing your success story using Hurl!


[Hurl]: https://hurl.dev
[curl]: https://curl.se
[Hurl 4.1.0]: https://github.com/Orange-OpenSource/hurl/releases/tag/4.1.0
[Test Anything Protocol]: https://testanything.org
[HTML report]: {% link _docs/running-tests.md %}#html-report
[JUnit report]: {% link _docs/running-tests.md %}#junit-report
[TAP report]: {% link _docs/running-tests.md %}#tap-report
[fill an issue]: https://github.com/Orange-OpenSource/hurl/issues
[AWS Signature Version 4]: https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html
[installed as a native binary]: https://hurl.dev/docs/installation.html
[multi-arch build]: https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/
[in our release note]: https://github.com/Orange-OpenSource/hurl/releases/tag/4.1.0
[give us a star on GitHub]: https://github.com/Orange-OpenSource/hurl/stargazers
[Twitter / X]: https://twitter.com/HurlDev
[Docker Image]: https://github.com/Orange-OpenSource/hurl/pkgs/container/hurl
