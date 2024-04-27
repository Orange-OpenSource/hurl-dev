---
title: Announcing Hurl 4.3.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

The Hurl team is thrilled to announce [Hurl 4.3.0] <picture><source srcset="{{ '/assets/img/emoji-surfer.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/emoji-surfer.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/emoji-surfer.png' | prepend:site.baseurl }}" type="image/png"><img class="emoji" src="{{ '/assets/img/emoji-surfer.png' | prepend:site.baseurl }}" width="20" height="20" alt="Surfer"></picture> !

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

- [Quality of Life Improvements](#quality-of-life-improvements)
- [Shell Completion](#shell-completion)
- [One More Thing...](#one-more-thing)
- [Others](#others)

## Quality of Life Improvements

Hurl 4.3.0 is about bringing various __quality of life improvements__. Nothing fancy, but Hurl keeps iterating, 
improving and increasing usefulness on each new release.  


### Error display

Errors display have been slightly improved, with request line displayed to give context without having to look in 
the Hurl source file.

Before 4.3.0:

{% raw %}
```shell
[1;31merror[0m: [1mUndefined variable[0m
[1;34m-->[0m tests_ok/post_file.hurl:6:8
[1;34m   |[0m
[1;34m 6 |[0m file,{{filename}};
[1;34m   |[0m[1;31m        ^^^^^^^^ [0m[1;31myou must set the variable filename[0m
[1;34m   |[0m
```
{% endraw %}

With 4.3.0:

{% raw %}
```shell
[1;31merror[0m: [1mUndefined variable[0m
[1;34m-->[0m tests_ok/post_file.hurl:6:8
[1;34m   |[0m
[1;34m   |[0m [90mPOST http://localhost:8000/post-file[0m
[1;34m   |[0m [90m...[0m
[1;34m 6 |[0m file,{{filename}};
[1;34m   |[0m[1;31m        ^^^^^^^^ [0m[1;31myou must set the variable filename[0m
[1;34m   |[0m
```
{% endraw %}

### --netrc, --netrc-file, --netrc-optional

Like its HTTP engine [curl], Hurl supports now the classic `.netrc` file (typically stored in a user's home directory).
With [`--netrc`]({% link _docs/manual.md %}#netrc) option, you can tells Hurl to look for and use the `.netrc` file. [`--netrc-file`]({% link _docs/manual.md %}#netrc-file) is similar to `--netrc`, except that you can provide the path to the actual file to use.

```shell
$ hurl --test --netrc-file /home/foo/.netrc *.hurl
```

### Per request --user

Let's keep talking about curl options. Like curl, one can use the command line option [`--user`]({% link _docs/manual.md %}#user)
to add basic authentication to all the requests of a Hurl file:

```shell
$ hurl --user bob:secret login.hurl
```

`--user` option can now be set _per request_, in an [`[Options]` section]({% link _docs/request.md %}#options):

```hurl
# Login with Bob is OK
POST http://foo.com/login
[Options]
user: bob:secret
location: true
HTTP 200

# Login with Alice is KO
POST http://foo.com/login
[Options]
user: alice:secret
location: true
HTTP 401
```

`--user` is useful when using [AWS Signature Version 4]: Amazon S3 authenticated sessions can be set now per
request:

```hurl
GET https://foo.execute-api.us-east-1.amazonas.com/dev/bafe12
[Options]
aws-sigv4: aws:amz:eu-central-1:foo
user: someAccessKeyId:someSecretKey
HTTP 200
```

And, last but not least, `--user` option can use [variables]:

{% raw %}
```hurl
GET https://foo.execute-api.us-east-1.amazonas.com/dev/bafe12
[Options]
aws-sigv4: aws:amz:eu-central-1:foo
user: {{login}}:{{password}}
HTTP 200
```
{% endraw %}

Like many other Hurl option, `--user` option can be used in the command line (take effect for all requests of a Hurl 
file), or per request, with an `[Options]` section:

```hurl
GET https://example.org
# An options section, each option is optional and applied only to this request...
[Options]
aws-sigv4: aws:amz:sts  # generate AWS SigV4 Authorization header
cacert: /etc/cert.pem   # custom certificate file
compressed: true        # request a compressed response
delay: 3000             # delay in ms for this request
http3: true             # use HTTP/3 protocol version
insecure: true          # allow insecure SSL connections and transfers
ipv6: true              # use IPv6 addresses
location: true          # follow redirection for this request
max-redirs: 10          # maximum number of redirections
output: out.html        # dump the response to this file
path-as-is: true        # do not handle sequences of /../ or /./ in URL path
skip: false             # skip this request
unix-socket: sock       # use Unix socket for transfer
user: bob:secret        # use basic authentication
variable: country=Italy # define variable country
variable: planet=Earth  # define variable planet
verbose: true           # allow verbose output
very-verbose: true      # allow more verbose output    
```

The [options documentation] and the Hurl man page have been improved to show which option can be used only in command line
and which option can be used in command line _and_ in an `[Options]` section. When option can only be used in command line
the option is tagged "cli-only option". For instance:

```
--color
    Colorize debug output (the HTTP response output is not colorized).
    This is a cli-only option.
```

When "cli-only option" is not specified, the option can be set per request within an [`[Options]`]({% link _docs/request.md %}#options) section.

### --max-filesize

One last new option backported from curl, [`--max-filesize`]({% link _docs/manual.md %}#max-filesize) allows to limit the size of HTTP response data (in bytes):

```shell
$ hurl --max-filesize 100000 https://example.com/
```

### New Predicates: isNumber, isIsoDate

[Predicates] are used to check HTTP responses:

```hurl
GET http://httpbin.org/json
HTTP 200
[Asserts]
jsonpath "$.slideshow.author" == "Yours Truly"
jsonpath "$.slideshow.slides[0].title" contains "Wonder"
jsonpath "$.slideshow.slides" count == 2
jsonpath "$.slideshow.date" != null
jsonpath "$.slideshow.slides[*].title" includes "Mind Blowing!"
```

Two new predicates are introduced with 4.3.0:

- `isNumber`: a companion to `isInteger` / `isFloat` existing predicates to test if a certain value is a number
- `isIsoDate`: check if a string value conforms to the [RFC-3339] date format `YYYY-MM-DDTHH:mm:sssZ`

```hurl
GET http://httpbin.org/json
HTTP 200
[Asserts]
jsonpath "$.slideshow.version" isNumber
jsonpath "$.slideshow.date" isIsoDate
jsonpath "$.slideshow.date" == "1937-01-01T12:00:27.87+00:20"
```

## Shell Completion

Hurl now offers shell completion scripts for various shell: [bash], [fish], [zsh] and [PowerShell]. Usually, packet 
managers package the completion scripts, but you can still install it yourself from [Hurl's GitHub repository].


## One More Thing...

One last thing, and this is a pretty big thing (at least for us <picture><source srcset="{{ '/assets/img/emoji-smiling-face.avif' | prepend:site.baseurl }}" type="image/avif"><source srcset="{{ '/assets/img/emoji-smiling-face.webp' | prepend:site.baseurl }}" type="image/webp"><source srcset="{{ '/assets/img/emoji-smiling-face.png' | prepend:site.baseurl }}" type="image/png"><img class="emoji" src="{{ '/assets/img/emoji-smiling-face.png' | prepend:site.baseurl }}" width="20" height="20" alt="Surfer"></picture>) !

In Hurl 4.3.0, we've addressed [one of our oldest issue], proposed in 2020: __a `--parallel` option!__
<div class="picture">
    <picture>
        <source srcset="{{ '/assets/img/pinto-light.avif' | prepend:site.baseurl }}" type="image/avif">
        <source srcset="{{ '/assets/img/pinto-light.webp' | prepend:site.baseurl }}" type="image/webp">
        <source srcset="{{ '/assets/img/pinto-light.png' | prepend:site.baseurl }}" type="image/png">
        <img class="u-theme-light u-drop-shadow u-border u-max-width-100" src="{{ '/assets/img/pinto-light.png' | prepend:site.baseurl }}" width="600" alt="Parallel GitHub issue"/>
    </picture>
    <picture>
        <source srcset="{{ '/assets/img/pinto-dark.avif' | prepend:site.baseurl }}" type="image/avif">
        <source srcset="{{ '/assets/img/pinto-dark.webp' | prepend:site.baseurl }}" type="image/webp">
        <source srcset="{{ '/assets/img/pinto-dark.png' | prepend:site.baseurl }}" type="image/png">
        <img class="u-theme-dark u-drop-shadow u-border u-max-width-100" src="{{ '/assets/img/pinto-dark.png' | prepend:site.baseurl }}" width="600" alt="Parallel GitHub issue"/>
    </picture>
</div>

It has been a long run since this issue, but we always kept in our mind that, at a moment, we want to be able to 
run Hurl files in parallel. Now, with 4.3.0, we're introducing an opt-in [`--parallel`]({% link _docs/manual.md %}#parallel)
option that will enable parallel
execution of Hurl files.

In Hurl 4.3.0, running files in test mode is (no change):

```shell
$ hurl --test *.hurl
```

With `--parallel`, you can choose to run your tests in parallel:

```shell
$ hurl --test --parallel *.hurl
```

To develop this feature, we take a lot of inspiration of the venerable [GNU Parallel].

In the parallel mode, each Hurl file is executed on its own thread, sharing nothing with other jobs. There is a thread
pool which size is roughly the current amount of CPUs and that can be configured with [`--jobs`]({% link _docs/manual.md %}#jobs) option. During parallel execution, standard output and error are buffered for each file and only displayed on screen when a job file is finished. This way, debug logs and messages are never interleaved between execution. Order of execution is not guaranteed 
in `--parallel` mode but reports ([HTML], [TAP], [JUnit]) keep the input files order.

The parallelism used is multithread sync: the thread pool is instantiated for the whole run, each Hurl file is run 
in its own thread, synchronously . We've not gone through the full multithreaded async route for implementation 
simplicity. Moreover, there is no additional dependency, only the standard Rust lib with "classic" threads and 
[multiple producers / single consumer channels] to communicate between threads.

For the 4.3.0, we've marked the `--parallel` option as "experimental" as we want to have feedbacks on it and insure that
everything works as designed. We plan to make this mode of execution the default when executing Hurl files with `--test` 
in the Hurl 5.0.0 version.

Give it a try, if you think Hurl is fast, Oh Boy... Wait until you see the new parallel mode!   

## Others

There are a lot other improvements with Hurl 4.3.0 and also a lot of bug fixes,
you can check the complete list of enhancements and bug fixes [in our release note].

If you like Hurl, don't hesitate to [give us a star on GitHub] or share it on [Twitter]!

We'll be happy to hear from you, either for enhancement requests or for sharing your success story using Hurl!


[Hurl]: https://hurl.dev
[curl]: https://curl.se
[Hurl 4.3.0]: https://github.com/Orange-OpenSource/hurl/releases/tag/4.3.0
[AWS Signature Version 4]: https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html
[variables]: {% link _docs/templates.md %}#injecting-variables
[options documentation]: {% link _docs/manual.md %}#options
[Predicates]: {% link _docs/asserting-response.md %}#predicates
[RFC-3339]: https://www.rfc-editor.org/rfc/rfc3339
[fish]: https://fishshell.com
[zsh]: https://ohmyz.sh
[PowerShell]: https://learn.microsoft.com/en-us/powershell/
[bash]: https://ftp.gnu.org/gnu/bash/
[Hurl's GitHub repository]: https://github.com/Orange-OpenSource/hurl/tree/master/completions
[one of our oldest issue]: https://github.com/Orange-OpenSource/hurl/issues/87
[GNU Parallel]: https://www.gnu.org/software/parallel/
[multiple producers / single consumer channels]: https://doc.rust-lang.org/book/ch16-02-message-passing.html
[HTML]: {% link _docs/running-tests.md %}#html-report
[TAP]: {% link _docs/running-tests.md %}#tap-report
[JUnit]: {% link _docs/running-tests.md %}#junit-report
[in our release note]: https://github.com/Orange-OpenSource/hurl/releases/tag/4.3.0
[Twitter]: https://twitter.com/HurlDev
[give us a star on GitHub]: https://github.com/Orange-OpenSource/hurl/stargazers
