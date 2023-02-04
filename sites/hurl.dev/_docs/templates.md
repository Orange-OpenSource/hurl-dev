---
layout: doc
title: Templates
description: Hurl file format variables and templating.
section: File Format
---

# Templates

## Variables

In Hurl file, you can generate value using two curly braces, i.e {% raw %}`{{my_variable}}`{% endraw %}. For instance, if you want to reuse a
value from an HTTP response in the next entries, you can capture this value in a variable and reuse it in a template.

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


In this example, we capture the value of the [CSRF token] from the body of the first response, and inject it
as a header in the next POST request.

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


In this second example, we capture the body in a variable `index`, and reuse this value in the query
{% raw %}`jsonpath "$.errors[{{index}}].id"`{% endraw %}.

## Types

Variables are typed, and can be either string, bool, number, `null` or collections. Depending on the variable type,
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

Variables can also be injected in a Hurl file:

- by using [`--variable` option]
- by using [`--variables-file` option]
- by defining environment variables, for instance `HURL_foo=bar`
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

We can use environment variables in the form of `HURL_name=value`:

```shell
$ export HURL_host=example.net
$ export HURL_id=1234 
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



## Templating Body

Using templates with [JSON body] or [XML body] is not currently supported in Hurl.
Besides, you can use templates in [multiline string body] with variables to send a JSON or XML body:

{% raw %}
~~~hurl
PUT https://example.org/api/hits
Content-Type: application/json
```
{
    "key0": "{{a_string}}",
    "key1": {{a_bool}},
    "key2": {{a_null}},
    "key3": {{a_number}}
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
    "key3": 42
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
