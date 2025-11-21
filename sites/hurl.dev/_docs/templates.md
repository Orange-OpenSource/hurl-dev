---
layout: doc
title: Templates
description: Hurl file format variables and templating.
section: File Format
---

# Templates

## Variables

In Hurl file, you can generate value using two curly braces, i.e {% raw %}`{{my_variable}}`{% endraw %}. For instance, if you want to reuse a
value from an HTTP response in the next entries, you can capture this value in a variable and reuse it in a placeholder.

In this example, we capture the value of a [CSRF token] from the body of the first response, and inject it
as a header in the next POST request:

{% raw %}
```hurl
GET https://example.org
HTTP 200
[Captures]
csrf_token: xpath "string(//meta[@name='_csrf_token']/@content)"

# Do the login !
POST https://acmecorp.net/login?user=toto&password=1234
X-CSRF-TOKEN: {{csrf_token}}
HTTP 302
```
{% endraw %}


In this second example, we capture the body in a variable `index`, and reuse this value in the query
{% raw %}`jsonpath "$.errors[{{index}}].id"`{% endraw %}:


{% raw %}
```hurl
GET https://example.org/api/index
HTTP 200
[Captures]
index: body

GET https://example.org/api/status
HTTP 200
[Asserts]
jsonpath "$.errors[{{index}}].id" == "error"
```
{% endraw %}



## Functions

Besides variables, functions can be used to generate dynamic values. Current functions are:

| Function  | Description                                                  |
|-----------|--------------------------------------------------------------|
| `newUuid` | Generates an [UUID v4 random string]                         |
| `newDate` | Generates an [RFC 3339] UTC date string, at the current time |

In the following example, we use `newDate` to generate a dynamic query parameter:

{% raw %}
```hurl
GET https://example.org/api/foo
[Query]
date: {{newDate}}
HTTP 200
```
{% endraw %}


We run a `GET` request to `https://example.org/api/foo?date=2024%2D12%2D02T10%3A35%3A44%2E461731Z` where the `date`
query parameter value is `2024-12-02T10:35:44.461731Z` URL encoded.

In this second example, we use `newUuid` function to generate an email dynamically:

{% raw %}
```hurl
POST https://example.org/api/foo
{
  "name": "foo",
  "email": "{{newUuid}}@test.com"
}
```
{% endraw %}


When run, the request body will be:

```
{
  "name": "foo",
  "email": "0531f78f-7f87-44be-a7f2-969a1c4e6d97@test.com"
}
```


## Types

Values generated from function and variables are typed, and can be either string, bool, number, `null` or collections. Depending on the value type,
templates can be rendered differently. Let's say we have captured an integer value into a variable named
`count`:

```hurl
GET https://sample/counter

HTTP 200
[Captures]
count: jsonpath "$.results[0]"
```

The following entry:

{% raw %}
```hurl
GET https://sample/counter/{{count}} 

HTTP 200
[Asserts]
jsonpath "$.id" == "{{count}}"
```
{% endraw %}


will be rendered at runtime to:

```hurl
GET https://sample/counter/458
 
HTTP 200
[Asserts]
jsonpath "$.id" == "458"
```

resulting in a comparison between the [JSONPath] expression and a string value.

On the other hand, the following assert:

{% raw %}
```hurl
GET https://sample/counter/{{count}} 

HTTP 200
[Asserts]
jsonpath "$.index" == {{count}}
```
{% endraw %}


will be rendered at runtime to:

```hurl
GET https://sample/counter/458 

HTTP 200
[Asserts]
jsonpath "$.index" == 458
```

resulting in a comparison between the [JSONPath] expression and an integer value.

So if you want to use typed values (in asserts for instances), you can use {% raw %}`{{my_var}}`{% endraw %}.
If you're interested in the string representation of a variable, you can surround the variable with double quotes
, as in {% raw %}`"{{my_var}}"`{% endraw %}.

> When there is no possible ambiguities, like using a variable in an URL, or
> in a header, you can omit the double quotes. The value will always be rendered
> as a string.

## Injecting Variables

Variables can be injected in a Hurl file:

- by using [`--variable` option]
- by using [`--variables-file` option]
- by defining environment variables, for instance `HURL_VARIABLE_foo=bar`
- by defining variables in an [`[Options]` section][options]

Lets' see how to inject variables, given this `test.hurl`:

{% raw %}
```hurl
GET https://{{host}}/{{id}}/status
HTTP 304

GET https://{{host}}/health
HTTP 200
```
{% endraw %}


### `variable` option

Variable can be defined with command line option:

```shell
$ hurl --variable host=example.net --variable id=1234 test.hurl
``` 


### `variables-file` option

We can also define all injected variables in a file:

```shell
$ hurl --variables-file vars.env test.hurl
``` 

where `vars.env` is

```
host=example.net
id=1234
```

### Environment variable

We can use environment variables in the form of `HURL_VARIABLE_name=value`:

```shell
$ export HURL_VARIABLE_host=example.net
$ export HURL_VARIABLE_id=1234 
$ hurl test.hurl
```

### Options sections

We can define variables in `[Options]` section. Variables defined in a section are available for the next requests.

{% raw %}
```hurl
GET https://{{host}}/{{id}}/status
[Options]
variable: host=example.net
variable: id=1234
HTTP 304

GET https://{{host}}/health
HTTP 200
```
{% endraw %}


### Secrets

Secrets are variables which value is redacted from standard error logs (for instance using [`--very-verbose`]) and [reports].
Secrets are injected through command-line with [`--secret` option]:

```shell
$ hurl --secret token=FooBar test.hurl
```

Values are redacted by _exact matching_: if a secret value is transformed, and you want to redact also the transformed value, 
you can add as many secrets as there are transformed values. Even if a secret is not used as a variable, all secrets values 
will be redacted from messages and logs.

```shell
$ hurl --secret token=FooBar \
       --secret token_alt_0=FOOBAR \
       --secret token_alt_1=foobar \
       test.hurl
```

> Secrets __are not redacted__ from HTTP responses outputted on standard output as Hurl considers the standard output as
> the correct unaltered output of a run. With this call `$ hurl --secret token=FooBar test.hurl`,
> the HTTP response is outputted unaltered and `FooBar` can appear in the HTTP response. Options that transforms Hurl
> output on standard output, like [`--include`] or [`--json`] works the same. [JSON report] also saves each unaltered HTTP
> response on disk so extra care must be taken when secrets are in the HTTP response body. 


## Templating Body

Variables and functions can be used in [JSON body]:

{% raw %}
~~~hurl
PUT https://example.org/api/hits
{
    "key0": "{{a_string}}",
    "key1": {{a_bool}},
    "key2": {{a_null}},
    "key3": {{a_number}},
    "key4": "{{newDate}}"
}
~~~
{% endraw %}


Note that we're writing a kind of JSON body directly without any delimitation marker. For the moment, [XML body] can't 
use variables directly. In order to templatize a XML body, you can use [multiline string body] with variables and 
functions. The multiline string body allows to templatize any text based body (JSON, XML, CSV etc...):

Multiline string body delimited by `` ``` ``:

{% raw %}
~~~hurl
PUT https://example.org/api/hits
Content-Type: application/json
```
{
    "key0": "{{a_string}}",
    "key1": {{a_bool}},
    "key2": {{a_null}},
    "key3": {{a_number}},
    "key4: "{{newDate}}"
}
```
~~~
{% endraw %}


Variables can be initialized via command line:

```shell
$ hurl --variable a_string=apple --variable a_bool=true --variable a_null=null --variable a_number=42 test.hurl
```

Resulting in a PUT request with the following JSON body:

```
{
    "key0": "apple",
    "key1": true,
    "key2": null,
    "key3": 42,
    "key4": "2024-12-02T13:39:45.936643Z"
}
```

[`--variable` option]: {% link _docs/manual.md %}#variable
[`--variables-file` option]: {% link _docs/manual.md %}#variables-file
[CSRF token]: https://en.wikipedia.org/wiki/Cross-site_request_forgery
[JSONPath]: {% link _docs/asserting-response.md %}#jsonpath-assert
[JSON body]: {% link _docs/request.md %}#json-body
[XML body]: {% link _docs/request.md %}#xml-body
[multiline string body]: {% link _docs/request.md %}#multiline-string-body
[options]: {% link _docs/request.md %}#options
[UUID v4 random string]: https://en.wikipedia.org/wiki/Universally_unique_identifier
[RFC 3339]: https://www.rfc-editor.org/rfc/rfc3339
[`--very-verbose`]: {% link _docs/manual.md %}#very-verbose
[reports]: {% link _docs/running-tests.md %}#generating-report
[`--secret` option]: {% link _docs/manual.md %}#secret
[`--include`]: {% link _docs/manual.md %}#include
[`--json`]: {% link _docs/manual.md %}#json
[JSON report]: {% link _docs/running-tests.md %}#json-report
