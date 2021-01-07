---
layout: doc
title: Frequently Asked Questions
---

# {{ page.title }}

1. [Why "Hurl"?](#why-hurl)
2. [Yet Another Tool, I already use X](#yet-another-tool-i-already-use-x)
3. [Hurl is build on top of libcurl, but what is added?](#hurl-is-build-on-top-of-libcurl-but-what-is-added)
4. [Why shouldn't I use Hurl?](#why-shouldn-t-i-use-hurl)
5. [I have a large numbers of tests, how to run just specific tests?](#i-have-a-large-numbers-of-tests-how-to-run-just-specific-tests)
6. [How to report results in a CI pipeline?](#how-to-report-results-in-a-ci-pipeline)
7. [How can I use my Hurl files outside Hurl?](#how-can-i-use-my-hurl-files-outside-hurl)


## Why "Hurl"? {#why-hurl}

The name Hurl is a tribute to the awesome [curl](https://curl.haxx.se), with a focus on the HTTP protocol.
While it may have an informal meaning not particularly elegant, [other eminent tools](https://git.wiki.kernel.org/index.php/GitFaq#Why_the_.27Git.27_name.3F) have set a precedence in naming.

## Yet Another Tool, I already use X {#yet-another-tool-i-already-use-x}

We think that Hurl has some advantages compared to similar tools.

Hurl is foremost a command line tool and should be easy to use on a local computer, or in a CI/CD pipeline. Some
 tools in the same space as Hurl ([Postman](https://www.postman.com) for instance), are GUI oriented and we find it
 less attractive than CLI. As a command line tool, Hurl can be used to get HTTP datas (like [curl](https://curl.haxx.se)), 
 but also as a test tool for HTTP sessions, or even as documentation.

Having a text based [file format]({% link _docs/hurl-file.md %}) is another advantage. The Hurl format is simple,
focused on the HTTP domain, can serve as documentation and can be read or written by non technical people. 
 
For instance posting JSON data with Hurl can be done with this simple file:

``` 
POST http://localhost:3000/api/login
{
  "username": "xyz",
  "password": "xyz"
}
```

With [curl](https://curl.haxx.se):

```
curl --header "Content-Type: application/json" \
     --request POST \
     --data '{"username": "xyz","password": "xyz"}' \
     http://localhost:3000/api/login
``` 


[Karate](https://github.com/intuit/karate), a tool combining API test automation, mocking, performance-testing, has
 similar features but offers also much more at a cost of an increased complexity.
  
Comparing Karate file format:

```
Scenario: create and retrieve a cat

Given url 'http://myhost.com/v1/cats'
And request { name: 'Billie' }
When method post
Then status 201
And match response == { id: '#notnull', name: 'Billie }

Given path response.id
When method get
Then status 200
``` 

And Hurl:

{% raw %}
```
# Scenario: create and retrieve a cat

POST http://myhost.com/v1/cats
{ "name": "Billie" }
HTTP/* 201
[Captures]
cat_id: jsonpath "$.id"
[Asserts]
jsonpath "$.name" equals "Billie"

GET http://myshost.com/v1/cats/{{cat_id}}
HTTP/* 200
```
{% endraw %}

A key point of Hurl is to work on the HTTP domain. In particular, there is no Javascript runtime, Hurl works on the 
raw HTTP requests/responses, and not on a DOM managed by a HTML engine. For security, this can be seen as a feature:
let's say you want to test backend validation, you want to be able to bypass the browser or javascript validations and 
directly test a backend endpoint. 

Finally, with no headless browser and working on the raw HTTP data, Hurl is also
really reliable with a very small probability of false positives. Integration tests with tools like 
[Selenium](https://www.selenium.dev) can, in this regard, be challenging to maintain.

Just use what is convenient for you. In our case, it's Hurl!
 
 
## Hurl is build on top of libcurl, but what is added? {#hurl-is-build-on-top-of-libcurl-but-what-is-added}

Hurl has two main functionalities on top of [curl](https://curl.haxx.se/):

1. Chain several requests:

    With its [captures]({% link _docs/capturing-response.md %}), it enables to inject data received from a response into
    following requests. [CSRF tokens](https://en.wikipedia.org/wiki/Cross-site_request_forgery)
    are typical examples in a standard web session.

2. Test HTTP responses:

    With its [asserts]({% link _docs/asserting-response.md %}), responses can be easily tested.

## Why shouldn't I use Hurl {#why-shouldn-t-i-use-hurl}
 
If you need a GUI. Currently, Hurl does not offer a GUI version (like [Postman](https://www.postman.com)). While we
think that it can be useful, we prefer to focus for the time-being on the core, keeping something simple and fast. 
Contributions to build a GUI are welcome.
 
  
## I have a large numbers of tests, how to run just specific tests? {#i-have-a-large-numbers-of-tests-how-to-run-just-specific-tests}

By convention, you can organize Hurl files into different folders or prefix them.
 
For example, you can split your tests into two folders critical and additional.

```
critical/test1.hurl
critical/test2.hurl
additional/test1.hurl
additional/test2.hurl
```

You can simply run your critical tests with

```
hurl critical/*.hurl
```
 
 
 
## How to report results in a CI pipeline? {#how-to-report-results-in-a-ci-pipeline}

Hurl can generate a html report with the [`--html` option]({% link _docs/man-page.md %}#html)

```
 hurl tests/*.hurl --html output_folder
```

Note that in the previous step, all Hurl files are run together successively.

In some setup, we may want to execute arbitrary commands between each Hurl test.
In this case, you need to append test results into a common file.
 
For example

```
hurl --json /tmp/tests.json --append --html /tmp/html_report file1.hurl
hurl --json /tmp/tests.json --append --html /tmp/html_report file2.hurl
hurl --json /tmp/tests.json --append --html /tmp/html_report file3.hurl
``` 

 
## How can I use my Hurl files outside Hurl? {#how-can-i-use-my-hurl-files-outside-hurl}

Hurl file can be exported to a json file with `hurlfmt`. 
This json file can then be easily parsed for converting a different format, getting ad-hoc information,...

For example, the Hurl file

```hurl
GET http://example.com/api/users/1
User-Agent: Custom

HTTP/1.1 200
[Asserts]
jsonpath "$.name" equals "Bob"

```

will be converted to json with the following command:

```
hurlfmt test.hurl --format json | jq
{
  "entries": [
    {
      "request": {
        "method": "GET",
        "url": "http://example.com/api/users/1",
        "headers": [
          {
            "name": "User-Agent",
            "value": "Custom"
          }
        ]
      },
      "response": {
        "version": "HTTP/1.1",
        "status": 200,
        "asserts": [
          {
            "query": {
              "type": "jsonpath",
              "expr": "$.name"
            },
            "predicate": {
              "type": "equal",
              "value": "Bob"
            }
          }
        ]
      }
    }
  ]
}
```



