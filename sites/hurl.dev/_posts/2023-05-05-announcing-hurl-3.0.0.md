---
title: Announcing Hurl 3.0.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

<div class="blog-post-date">{{ page.date | date: "%b. %d, %Y" }}</div>

The Hurl team is happy to announce [Hurl 3.0.0]!

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

## What’s New in This Release

- [Checking SSL Attributes (Expiration Date, Issuer, etc...)]
- [Working with Date Values]
- [Convert curl to Hurl]
- [Simplify Hurl's Rust APIs]


## Checking SSL Attributes (Expiration Date, Issuer, etc...)

In Hurl 3.0.0, we can now check various attributes of a SSL certificate:

```hurl
# Check attributes of the SSL certificate            
GET https://example.org

HTTP 200
[Asserts]
certificate "Subject" == "CN=example.org"
certificate "Issuer" == "C=US, O=Let's Encrypt, CN=R3"
certificate "Expire-Date" daysAfterNow > 15
certificate "Serial-Number" matches /[\da-f]+/
```

The following properties are available to check: `Subject`,  `Issuer`, `Start-Date`, `Expire-Date` and  `Serial-Number`.
Using certificate asserts, you can simply create a cron job that will warn you if your certificate expires soon.   

If you want more information on the SSL layer, you can also use [`--very-verbose`] option that will output curl debug logs,
including SSL informations:

```shell
$ echo 'HEAD https://hurl.dev' | hurl --very-verbose
[1;34m*[0m [1mOptions:[0m
[1;34m*[0m     fail fast: true
...
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
...
```


## Working with Date Values

Introduced in [Hurl 2.0.0], [filters] allow you to transform the data extracted from an HTTP response, whether in asserts
or in captures:

```hurl
GET https://example.org/api

HTTP 200
[Captures]
name: jsonpath "$user.id" replace /\d/ "x"
[Asserts]
header "x-servers" split "," count == 2
header "x-servers" split "," nth 0 == "rec1"
header "x-servers" split "," nth 1 == "rec3"
jsonpath "$.books" count == 12
```

Now, we have filters to work on dates: [`daysAfterNow`], [`daysBeforeNow`], [`format`] and [`toDate`]. For instance, let's say we
have a JSON response like this:

```json
{
  "published": "2023-01-23T18:25:43.511Z"
}
```


We can do the following:

- extract the `published` string from the response => `jsonpath "$.published"`
- transform this value to a date variable => `toDate "%Y-%m-%dT%H:%M:%S%.fZ"`
- reformat this date to the day of the week => `format "%A"`

So, our Hurl test becomes:

```hurl
GET https://example.org/books/123
HTTP 200
[Asserts]
jsonpath "$.published" == "2023-01-23T18:25:43.511Z"
jsonpath "$.published" toDate "%Y-%m-%dT%H:%M:%S%.fZ" format "%A" == "Monday"
```

ISO 8601 / RFC 3339 date and time format have shorthand format `%+` so we can write:

```hurl
GET https://example.org/books/123
HTTP 200
[Asserts]
jsonpath "$.published" == "2023-01-23T18:25:43.511Z"
jsonpath "$.published" toDate "%+" format "%A" == "Monday"
```

Some queries are natively returning date values: [expiration date of SSL certificates] or [expiration date of cookies] for instance:

```hurl
GET https://example.org
HTTP 200
[Asserts]
cookie "LSID[Expires]" format "%a, %d %b %Y %H:%M:%S" == "Thu, 13 Jan 2078 22:23:01"
certificate "Expire-Date" daysAfterNow > 15
```

## Convert curl to Hurl

`hurlfmt` is our Swiss knife for working with Hurl formatted files. We use it to convert an Hurl file to a JSON file:

```
$ hurlfmt --out json test.hurl | jq
{
  "entries": [
    {
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/test.json"
      },
      "response": {
        "status": 200,
...
```

This can be useful if you want to convert your big Hurl tests suite to a solution that uses a different format.

With 3.0.0, we've added the ability to convert curl command lines to Hurl.

For instance, using `hurlfmt`:

```shell
$ hurlfmt --in curl curl.txt
```

We can convert this chain of curl commands:

```
curl http://localhost:8000/hello
curl http://localhost:8000/custom-headers -H 'Fruit:Raspberry' -H 'Fruit:Apple' -H 'Fruit:Banana' -H 'Fruit: Grape' -H 'Color:Green'
curl --header 'Content-Type: application/json' --data $'{"name": "Bob","password":"secret","age": 30}' 'http://localhost:8000/post-json'
curl --header 'Content-Type:' --data '@tests_ok/data.bin' 'http://localhost:8000/post-file'
curl --location 'http://localhost:8000/redirect-absolute'
curl -k https://localhost:8001/hello
```

to this Hurl file:

~~~hurl
GET http://localhost:8000/hello

GET http://localhost:8000/custom-headers
Fruit: Raspberry
Fruit: Apple
Fruit: Banana
Fruit: Grape
Color: Green

POST http://localhost:8000/post-json
Content-Type: application/json
```
{"name": "Bob","password":"secret","age": 30}
```

POST http://localhost:8000/post-file
Content-Type:
file, tests_ok/data.bin;

GET http://localhost:8000/redirect-absolute
[Options]
location: true

GET https://localhost:8001/hello
[Options]
insecure: true
~~~

### From your browser to Hurl

Another use case is to convert a request played in your favorite browser to Hurl format and replay it with Hurl. Using 
Firefox, in the Developer Tools / Network tab, you can export an HTTP request to a curl command:

<p>
    <img class="u-drop-shadow u-border" src="{{ '/assets/img/firefox.png' | prepend:site.baseurl }}" width="100%" alt="Export request to curl in Firefox" >
</p>

Then using `hurlfmt`, you will be able to convert this request to Hurl. We're very happy to have 
implemented this feature and we're looking forward to feedback!

## Simplify Hurl's Rust APIs

Hurl purpose has always been to be an excellent command line application, whether you want to get datas from a website or
you want to add integration tests in A CI/CD pipeline. Some people (to our surprise), are also using [Hurl's crate] (a library in the Rust world)
to integrate Hurl in there own program. With 3.0.0, we've given some attention to the APIs exposed by Hurl's crate and, now, 
it's even simpler to run an Hurl content and get result.

A minimal Rust sample using the `run` method:

```rust
// A simple Hurl sample
let content = r#"
GET http://localhost:8000/hello
HTTP 200
"#;

// Define runner options and logger
let options = RunnerOptionsBuilder::new()
    .follow_location(true)
    .verbosity(Some(Verbosity::Verbose))
    .build();
let logger = LoggerBuilder::new().build();

// Set variables
let mut variables = HashMap::default();
variables.insert("name".to_string(), Value::String("toto".to_string()));

// Run the Hurl sample
let result = runner::run(
    content,
    &options,
    &variables,
    &logger
);
```

To run a Hurl content, you have to provide the content as a string slice, a logger, some variables and runner options.
Runner options and logger are created [using the Rust builder pattern]: this way we can add more options without breaking binary
compatibility (thanks [@robjtede]).

## That's All

There are other improvements and bug fixes, you can check a complete list [in our release note].
If you like Hurl, don't hesitate to [give us a star on GitHub] or share it on [Twitter]!

We'll be happy to hear from you, either for enhancement requests or for sharing your success story using Hurl!


[Hurl]: https://hurl.dev
[curl]: https://curl.se
[Hurl 3.0.0]: https://github.com/Orange-OpenSource/hurl/releases/tag/3.0.0
[Checking SSL Attributes (Expiration Date, Issuer, etc...)]: #checking-ssl-attributes-expiration-date-issuer-etc
[Working with Date Values]: #working-with-date-values
[Convert curl to Hurl]: #convert-curl-to-hurl
[Simplify Hurl's Rust APIs]: #simplify-hurls-rust-apis
[`--very-verbose`]: {% link _docs/manual.md %}#very-verbose
[Hurl 2.0.0]: https://hurl.dev/blog/2023/01/25/hurl-2.0.0-the-graphql-edition.html
[filters]: {% link _docs/filters.md %}
[expiration date of SSL certificates]: {% link _docs/asserting-response.md %}#ssl-certificate-assert
[expiration date of cookies]: {% link _docs/asserting-response.md %}#cookie-assert
[Hurl's crate]: https://crates.io/crates/hurl
[using the Rust builder pattern]: https://rust-unofficial.github.io/patterns/patterns/creational/builder.html
[@robjtede]: https://twitter.com/robjtede
[give us a star on GitHub]: https://github.com/Orange-OpenSource/hurl/stargazers
[Twitter]: https://twitter.com/HurlDev
[in our release note]: https://github.com/Orange-OpenSource/hurl/releases/tag/3.0.0
[`daysAfterNow`]: {% link _docs/filters.md %}#daysafternow
[`daysBeforeNow`]: {% link _docs/filters.md %}#daysbeforenow
[`format`]: {% link _docs/filters.md %}#format
[`toDate`]: {% link _docs/filters.md %}#todate
