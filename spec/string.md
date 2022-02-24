# String Specification

Strings in Hurl can be encoded:
- either within quotes
- or without any quote (delimited implicitly by of Hurl structure)



## Quoted Strings

Example: Xpath expression

```xpath "//div"```

Similar to JSON String, it has the following escaped characters: BACKSLASH, DOUBLE QUOTE, ...

The unique escape sequence differs from JSON
it has the follwoing form  \u{unicode}

### Examples Valid String

Example param
param1

### Examples Invalid String



## Unquoted Strings

Unquoted Strings are more complicated to encode.
They are specific to the location of the string.

The main motivation for using unquoted strings is to make simple/common strings very easy to read/write.

```
GET /images/logo.png HTTP/1.1
Host: www.example.com
Accept-Language: en
```

They contain all the escape characters defined for the quoted string.

ly, while making it possible to write any possible string.
They also conatins 


The table below lists all possible encodings

| Type                                                             |  Additional escape characters  |
|------------------------------------------------------------------|--------------------------------|
| url                                                              | '#'                            |
| key name (header name, param name, cookie name and capture name) | '#' and the ':'                |
| key value (header value, param value, cookie value)              | '#'                            |



### Examples 

Valid Strings

Example param
param1


Invalid Strings



## Templating

Both quoted and unquoted string can contain templates.

```
GET http:://{{host}}
HTTP/1.1 200
[Asserts]
xpath "string(//head/title)" == "{{message}}"
```

A template is defined by `{{`... `}}`.

If 