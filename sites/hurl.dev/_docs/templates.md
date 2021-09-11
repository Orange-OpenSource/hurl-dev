---
layout: doc
title: Templates
section: File Format
---
# {{ page.title }}


## Variables {#variables}
In Hurl file, you can generate value using two curly braces, i.e {% raw %}`{{my_variable}}`{% endraw %}. For instance, if you want to 
reuse a value from an HTTP response in the next entries, you can capture this value in a variable and reuse it in a 
template.

{% raw %}
```hurl
GET https://example.net

HTTP/1.1 200
[Captures]
csrf_token: xpath "string(//meta[@name='_csrf_token']/@content)"

# Do the login !
POST https://acmecorp.net/login?user=toto&password=1234
X-CSRF-TOKEN: {{csrf_token}}

HTTP/1.1 302
```
{% endraw %}

In this example, we capture the value of the [CSRF token](https://en.wikipedia.org/wiki/Cross-site_request_forgery) from
the body a first response, and inject it as a header in the next POST request. 

{% raw %}
```hurl
GET http://api.example.net/index
HTTP/* 200
[Captures]
index: body

GET http://api.example.net/status
HTTP/* 200
[Asserts]
jsonpath "$.errors[{{index}}].id" == "error"
```
{% endraw %}

In this second example, we capture the body in a variable `index`, and reuse this value in the query 
{% raw %}`jsonpath "$.errors[{{index}}].id"`{% endraw %}.

## Types {#types}

Variable are typed, and can be either string, bool, number, `null` or collections. Depending on the variable type, 
templates can be rendered differently. Let's say we have captured an integer value into a variable named
 `count`:

```hurl
GET https://sample/counter
HTTP/* 200
[Captures]
count: jsonpath "$.results[0]"
```

The following entry:

{% raw %}
```hurl
GET https://sample/counter/{{counter}} 
HTTP/* 200
[Asserts]
jsonpath "$.id" == "{{counter}}"
```
{% endraw %}

will be rendered at runtime to:

```hurl
GET https://sample/counter/458 
HTTP/* 200
[Asserts]
jsonpath "$.id" == "458"
```

resulting in a comparaison between the [JSONPath]({% link _docs/asserting-response.md %}#jsonpath-assert)
expression and a string value.

On the other hand, the following assert:

{% raw %}
```hurl
GET https://sample/counter/{{counter}} 
HTTP/* 200
[Asserts]
jsonpath "$.index" == {{counter}}
```
{% endraw %}

will be rendered at runtime to:

```hurl
GET https://sample/counter/458 
HTTP/* 200
[Asserts]
jsonpath "$.index" == 458
```

resulting in a comparaison between the [JSONPath]({% link _docs/asserting-response.md %}#jsonpath-assert) expression 
and an integer value.

So if you want to use typed values (in asserts for instances), you can use {% raw %}`{{my_var}}`{% endraw %}.
 If you're interested in the string representation of a variable, you can surround the variable with double quotes
 , as in {% raw %}`"{{my_var}}"`{% endraw %}.

> When there is no possible ambiguities, like using a variable in an url, or 
> in a header, you can omit the double quotes. The value will always be rendered 
> as a string.

## Injecting Variables {#injecting-variables}

Variables can also be injected in a Hurl file, by using [`--variable` option]({% link _docs/man-page.md %}#variable) :

```
$ hurl --variable host=example.net test.hurl
``` 

where `test.hurl` is the following file:

{% raw %}
```hurl
GET https://{{host}}/status
HTTP/1.1 304

GET https://{{host}}/health
HTTP/1.1 200
```
{% endraw %}

## Templating Body {#templating-body}

Using templates with [JSON body]({% link _docs/request.md %}#json-body) or [XML body]({% link _docs/request.md %}#xml-body) 
is not currently supported in Hurl. Besides, you can use templates in [raw string body]({% link _docs/request.md%}#raw-string-body) 
with variables to send a JSON or XML body:

{% raw %}
~~~hurl
PUT https://api.example.net/hits
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

```bash
$ hurl --variable key0=apple --variable key1=true --variable key2=null --variable key3=42 test.hurl
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
