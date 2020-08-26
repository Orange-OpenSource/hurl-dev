---
layout: doc
title: Frequently Asked Questions
---

# {{ page.title }}

1. [Why "Hurl"?](#why-hurl)
2. [Yet Another Tool, I already use X](#yet-another-tool-i-already-use-x)
 

## Why "Hurl"? {#why-hurl}

The name Hurl is a tribute to the awesome [curl](https://curl.haxx.se), and also an artifact of Hurl early 
[Haskell](https://www.haskell.org) implementation. While it informal meaning is not particularly elegant, 
[other eminent tools](https://git.wiki.kernel.org/index.php/GitFaq#Why_the_.27Git.27_name.3F) have set a precedence in naming.

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
 similar features but offers also much more at a cost of an increased complexity (Karate is ~ 33,000 line of Java
  code, while Hurl-JVM is around 6,600 line of Kotlin code).
  
Comparing Karate file format:

```
Scenario: create and retrieve a cat

Given url 'http://myhost.com/v1/cats'
And request { name: 'Billie' }
when method post
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
directly test a backend endpoint. Finally, with no headless browser and working on the raw HTTP data, Hurl is also
really reliable with a very small probability of false positives. Integration tests with tools like 
[Selenium](https://www.selenium.dev) can, in this regard, be challenging to maintain.

Finally, just use what is convenient for you. In our case, it's Hurl!
 
 

