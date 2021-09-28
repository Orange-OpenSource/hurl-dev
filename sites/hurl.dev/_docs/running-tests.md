---
layout: doc
title: Running tests
section: Getting Started
---

# {{ page.title }}

Hurl is run by default as an HTTP client, returning the body of the last HTTP response.

For testing, we are only interested in the asserts results.
Several options relating to testing can be used:

- do not output response body (`--output /dev/null`)
- show progress (`--progress`)
- print summary (`--summary`)

For convenience, all these options can also be set with the unique option `--test`.

```
hurl --test hello.hurl error_assert_status.hurl 
hello.hurl: running [1/2]
hello.hurl: success
error_assert_status.hurl: running [2/2]
error: Assert Status
  --> error_assert_status.hurl:2:10
   |
 2 | HTTP/1.0 200
   |          ^^^ actual value is <404>
   |

error_assert_status.hurl: failure
-------------------------------------------------------------
executed: 2
success: 1 (50.0%)
failed: 1 (50.0%)
execution time: 52ms
```


## Generating an HTML report

Hurl can also generates an HTML by using the `--html HTML_DIR` option.

If the HTML report already exists, the test results will be appended to it.

![Hurl HTML Report](/assets/img/hurl-html-report.png)

The input Hurl files (HTML version) are also included and are easily accessed from the main page.

![Hurl HTML file](/assets/img/hurl-html-file.png)