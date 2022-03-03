# String/Template Specification

Strings in Hurl can be encoded:
- either within quotes
- or without any quote (delimited implicitly by of Hurl structure)

They can also contain templates. A template is an expression enclosed between  {{ and }}.

The expression language must be stay independent of the String specification.
We must be able to update the expression language without touching the String spec.



## Quoted Strings

Example: Xpath expression

```xpath "//div"```

It has the following standard escape sequences (found in JSON String):
- \\"
- \\\
- \\b
- \\f
- \\n
- \\r
- \\t
  
It has also a unicode escaping sequence:
- \\u{ unicode char in hex digit}

This is slightly different from JSON. 
Encoding a character that takes more than 2 bytes will take only one \u escaping in Hurl but 2 in JSON.

Example: encoding the unicode Character 'MUSICAL SYMBOL G CLEF' (U+1D11E)

in Hurl
```\u{1D11E}```

in JSON
```\uD834\uDD1E```

Due to the templating, we have an additional valid escaping sequence `\{` in order to avoid treating the template.

Valid String/Template
```
Hello {{name}}!    // the template {{name}} will be evaluated at run time
Hello {name}!      // Simple string without template
Hello \{{name}}!   // Simple String without template. The \ is not part of the String value
Hello {{name\}}}! // Template contains a trailing right curly bracket
```

You can also use the unicode escape sequence `\u{7b}` to encode a literal `{` (not treated as special character)
If you need to express literally `{{`, you need to escape at least of one the bracket.
with a backslash `\{{` or a unicode escape sequence `\u{7b}{`

> [Handlebar template escaping](https://handlebarsjs.com/guide/expressions.html#escaping-handlebars-expressions):
> 
> ```
> \{{escaped}}
> 
> {{{{raw}}}}
>  {{escaped}}
> {{{{/raw}}}}
> ```
> 
> [httpYac template escaping](https://httpyac.github.io/guide/variables.html#variable-substitution-in-request)
>
> ```
> If the replacement is not desired, this can be prevented using \{\{...\}\}. This is replaced by {{...}}
> ```


Parse Errors
```
Hello {{name}!     // The template starts but does not terminate
Hello {{name\}}!   // The template starts but does not terminate. The first right (escaped) curly braket is part of the expression.
```


## Unquoted Strings

Unquoted Strings are a lot more complicated to encode.
The main motivation for using unquoted strings is to make simple/common strings very easy to read/write.

```
GET /images/logo.png HTTP/1.1
Host: www.example.com
Accept-Language: en
```

They are specific to the location of the string.
They are delimited implicitly by the Hurl file structure: newline, colon between header name and value, ...

The unquoted string can contain spaces. 
But the trailing space will have to be encoded/escaped as whitespace in Hurl file can be ignored.

The table below lists all possible encodings/escaping

| Type                                                             |  Additional escape characters  |
|------------------------------------------------------------------|--------------------------------|
| url                                                              | '#'                            |
| key name (header name, param name, cookie name and capture name) | '#' and the ':'                |
| key value (header value, param value, cookie value)              | '#'                            |
|...

Key/Value examples (section [Headers], [QueryString], [FormParams])

| Input     | Decoded                 |
|-----------|-------------------------|
|`X:Y`      | name="X", value="Y"     |
|`X : Y`    | name="X", value="Y"     |
|`X::Y`     | name="X", value=":Y"    |
|`X\::Y`    | name="X:", value="Y"    |
|`X\\:Y`    | name="X\", value="Y"    |
|`X:Y#Z`    | name="X", value="Y"     |
|`X\#:Y`    | name="X#", value="Y"    |
|`X X\ :Y`  | name="X X ", value="Y"  |

Parse Error
```
X\:  => expecting ':'
X#   => expecting ':'
```

## Multiline string

A Hurl String is always encoded on one line. Newline are encoded with the escaped sequence `\n`.
For multiline Strings, there is a specific syntax ```.
