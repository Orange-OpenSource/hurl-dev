---
title: Announcing Hurl 4.0.0
layout: blog
section: Blog
permalink: /blog/:year/:month/:day/:title.html
---

# {{ page.title }}

- Waterfall in HTML export
  - libcurl timings (available also in --very-verbose)
  - performance asserts
- Long error format for CI/CD
- decode filter
- minor syntax change
  - any custom method QUERY
  - deprecated lessThan etc...


We've improved [Hurl HTML report]. The HTLM report is pure HTML, without any JavaScript and with inlined CSS, so it's should be 
easy to integrate in your favorite CI/CD solution (like GitLab CI/CD or GItHub aAction for instance). Now, each run produces:

- a __waterfall timeline__: each request/respone is displayed on a beautiful graph, with easy access to response timings (DNS, 
TCP handshake, time to first byte etc...). These timings are provided by `libcurl` and you can find an explanation of each 
indicator [in the documentation]

<img class="u-drop-shadow u-border" src="{{ '/assets/img/timeline.png' | prepend:site.baseurl }}" width="100%" alt="Requests timeline"/>

- a run log with request and response headers, certificate info etc...

<img class="u-drop-shadow u-border" src="{{ '/assets/img/run.png' | prepend:site.baseurl }}" width="100%" alt="Requests run"/>

- a syntax colored source file with inline errors

<img class="u-drop-shadow u-border" src="{{ '/assets/img/source.png' | prepend:site.baseurl }}" width="100%" alt="Requests source"/>





[Hurl HTML report]: [`--html-report`]: {% link _docs/manual.md %}#html-report
[in the documentation]: {% link _docs/response.md %}#timings
