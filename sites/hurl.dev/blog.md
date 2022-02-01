---
title: Hurl Blog
layout: blog
section: Blog
permalink: /blog/
indexed: false
---

# {{ page.title }}

## Posts in 2021

<ul class="u-list-style-none">
  {% for post in site.posts %}
    {% capture year %}{{ post.date | date: "%Y" }}{% endcapture %}
    {% if year == "2021" %}
        <li class="row">
            <div class="col1 blog-post-short-date">{{ post.date | date: "%b. %d" }}</div>
            <div class="col6 blog-post-link"><a href="{{ post.url }}">{{ post.title }}</a></div>
        </li>
    {% endif %}
  {% endfor %}
</ul>