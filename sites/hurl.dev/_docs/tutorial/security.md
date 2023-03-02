---
layout: doc
title: Security
section: Tutorial
---

# Security

In the previous part, we have tested the basic creation of a quiz, through the <http://localhost:8080/new-quiz>
endpoint. Our test file `create-quiz.hurl` now looks like:

{% raw %}
```hurl
# First, get the quiz creation page to capture
# the CSRF token (see https://en.wikipedia.org/wiki/Cross-site_request_forgery)
GET http://localhost:8080/new-quiz

HTTP 200
[Captures]
csrf_token: xpath "string(//input[@name='_csrf']/@value)"


# Create a new quiz, using the captured CSRF token.
POST http://localhost:8080/new-quiz
[FormParams]
name: Simpson
question0: 16f897ab
question1: dd894cca
question2: 4edc1fdb
question3: 37b9eff3
question4: 0fec576c
_csrf: {{csrf_token}}

HTTP 302
[Captures]
detail_url: header "Location"
[Asserts]
header "Location" matches "/quiz/detail/[a-f0-9]{8}"


# Open the newly created quiz detail page:
GET {{detail_url}}
HTTP 200
```
{% endraw %}


So far, we have tested a "simple" form creation: every value of the form is valid and sanitized, but what if the user
put an invalid email?

## Server Side Validation

In the browser, there is client-side validation helping users enter data and avoid unnecessary server load.

Our HTML form is:

```html
<form action="/new-quiz" method="POST">
    ...
    <input id="name" type="text" name="name" minlength="4" maxlength="32" value="" required>...
    <input id="email" type="email" name="email" value="">...
    ...
</form>
```

The first input, name, has validation HTML attributes: `minlength="4"`, `maxlength="32"` and `required`.
In a browser, these attributes will prevent the user from entering invalid data like a missing value or a name that is too long. If your
tests rely on a "headless" browser, it can stop you from testing your server-side
validation. Client-side validation can also use JavaScript, and it can be a challenge to send invalid data to your server.

But server-side validation is critical to secure your app. You must always validate and sanitize data on your backend,
and try to test it.

As Hurl is not a browser, but merely an HTTP runner on top of [curl], sending and testing invalid data is easy.

{:start="1"}
1. Add a POST request to create a new quiz in `create-quiz.hurl`, with an invalid name. We check that the status code is 200 (user is
   not redirected to the quiz detail page), and that the label for "name" field has an `invalid` class:

{% raw %}
```hurl
# First, get the quiz creation page to capture
# ...

# Create a new quiz, using the captured CSRF token.
# ...

# Open the newly created quiz detail page:
# ...

# Test various server-side validations: 

# Invalid form name value: too short
POST http://localhost:8080/new-quiz
[FormParams]
name: x
question0: 16f897ab
question1: dd894cca
question2: 4edc1fdb
question3: 37b9eff3
question4: 0fec576c
_csrf: {{csrf_token}}

HTTP 200
[Asserts]
xpath "//label[@for='name'][@class='invalid']" exists
```
{% endraw %}


{:start="2"}
2. Add a POST request to create a new quiz with an email name. We check that the status
   code is 200 (user is not redirected to the quiz detail page), and that the label for "email" field has an
   `invalid` class:

{% raw %}
```hurl
# First, get the quiz creation page to capture
# ...

# Create a new quiz, using the captured CSRF token.
# ...

# Open the newly created quiz detail page:
# ...

# Test various server-side validations: 

# Invalid form name value: too short
# ...
# Invalid email parameter
POST http://localhost:8080/new-quiz
[FormParams]
name: Barth
email: barthsimpson
question0: 16f897ab
question1: dd894cca
question2: 4edc1fdb
question3: 37b9eff3
question4: 0fec576c
_csrf: {{csrf_token}}

HTTP 200
[Asserts]
xpath "//label[@for='email'][@class='invalid']" exists
```
{% endraw %}


{:start="3"}
3. Finally, add a POST request with no CSRF token, to test that our endpoint has CRSF protection:

```hurl
# First, get the quiz creation page to capture
# ...

# Create a new quiz, using the captured CSRF token.
# ...

# Open the newly created quiz detail page:
# ...

# Test various server-side validations: 

# Invalid form name value: too short
# ...
# Invalid email parameter
# ...
# No CSRF token:
POST http://localhost:8080/new-quiz
[FormParams]
name: Barth
email: barth.simpson@provider.net
question0: 16f897ab
question1: dd894cca
question2: 4edc1fdb
question3: 37b9eff3
question4: 0fec576c
HTTP 403
```

> We're using [the exist predicate] to check labels in the DOM

{:start="4"}
4. Run `create-quiz.hurl` and verify that everything is ok:

```shell
[1mcreate-quiz.hurl[0m: [1;36mRunning[0m [1/1]
[1mcreate-quiz.hurl[0m: [1;32mSuccess[0m (6 request(s) in 33 ms)
--------------------------------------------------------------------------------
Executed files:  1
Succeeded files: 1 (100.0%)
Failed files:    0 (0.0%)
Duration:        41 ms
```

## Comments

So Hurl, being close to the HTTP layer, has no "browser protection" / client-side validation: it facilitates
the testing of your app's security with no preconception.

Another use case is checking if there are no comments in your served HTML. Comments can reveal sensitive information
and [is it recommended] to trim HTML comments in your production files.

Popular front-end frameworks like [ReactJS] or [Vue.js] use client-side JavaScript.
If you use one of these frameworks, and you inspect the DOM with the browser developer tools, you won't see any comments
because the framework is managing the DOM and is removing them.

But, if you look at the HTML page sent on the network, i.e. the real HTML document sent by the
server (and not _the document dynamically created by the framework_), you can still see those HTML comments.

With Hurl, you will be able to check the content of the _real_ network data.

{:start="1"}
1. In the first entry of `create-quiz.hurl`, add a [XPath assert] when getting the quiz creation page:

```hurl
# First, get the quiz creation page to capture
# the CSRF token (see https://en.wikipedia.org/wiki/Cross-site_request_forgery)
GET http://localhost:8080/new-quiz

HTTP 200
[Captures]
csrf_token: xpath "string(//input[@name='_csrf']/@value)"
[Asserts]
xpath "//comment" count == 0     # Check that we don't leak comments

# ...
```


{:start="2"}
2. Run `create-quiz.hurl` and verify that everything is ok:

```shell
$ hurl --test create-quiz.hurl
[1mcreate-quiz.hurl[0m: [1;36mRunning[0m [1/1]
[1mcreate-quiz.hurl[0m: [1;32mSuccess[0m (6 request(s) in 33 ms)
--------------------------------------------------------------------------------
Executed files:  1
Succeeded files: 1 (100.0%)
Failed files:    0 (0.0%)
Duration:        41 ms
```

## Recap

So, our test file `create-quiz.hurl` is now:

{% raw %}
```hurl
# First, get the quiz creation page to capture
# the CSRF token (see https://en.wikipedia.org/wiki/Cross-site_request_forgery)
GET http://localhost:8080/new-quiz

HTTP 200
[Captures]
csrf_token: xpath "string(//input[@name='_csrf']/@value)"
[Asserts]
xpath "//comment" count == 0     # Check that we don't leak comments


# Create a new quiz, using the captured CSRF token.
POST http://localhost:8080/new-quiz
[FormParams]
name: Simpson
question0: 16f897ab
question1: dd894cca
question2: 4edc1fdb
question3: 37b9eff3
question4: 0fec576c
_csrf: {{csrf_token}}

HTTP 302
[Captures]
detail_url: header "Location"
[Asserts]
header "Location" matches "/quiz/detail/[a-f0-9]{8}"


# Open the newly created quiz detail page:
GET {{detail_url}}
HTTP 200

# Test various server-side validations:

# Invalid form name value: too short
POST http://localhost:8080/new-quiz
[FormParams]
name: x
question0: 16f897ab
question1: dd894cca
question2: 4edc1fdb
question3: 37b9eff3
question4: 0fec576c
_csrf: {{csrf_token}}

HTTP 200
[Asserts]
xpath "//label[@for='name'][@class='invalid']" exists


# Invalid email parameter:
POST http://localhost:8080/new-quiz
[FormParams]
name: Barth
email: barthsimpson
question0: 16f897ab
question1: dd894cca
question2: 4edc1fdb
question3: 37b9eff3
question4: 0fec576c
_csrf: {{csrf_token}}

HTTP 200
[Asserts]
xpath "//label[@for='email'][@class='invalid']" exists


# No CSRF token:
POST http://localhost:8080/new-quiz
[FormParams]
name: Barth
email: barth.simpson@provider.net
question0: 16f897ab
question1: dd894cca
question2: 4edc1fdb
question3: 37b9eff3
question4: 0fec576c
HTTP 403
```
{% endraw %}


We have seen that Hurl can be used as a security tool, to check your server-side validation.
Until now, we have done all our tests locally, and in the next session we are going to see how simple
it is to integrate Hurl in a CI/CD pipeline like [GitHub Action] or [GitLab CI/CD].


[curl]: https://curl.se
[the exist predicate]: {% link _docs/asserting-response.md %}#predicates
[is it recommended]: https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/05-Review_Webpage_Content_for_Information_Leakage
[DOM]: https://en.wikipedia.org/wiki/Document_Object_Model
[ReactJS]: https://reactjs.org
[Vue.js]: https://vuejs.org
[XPath assert]: {% link _docs/asserting-response.md %}#xpath-assert
[GitHub Action]: https://github.com/features/actions
[GitLab CI/CD]: https://docs.gitlab.com/ee/ci/
