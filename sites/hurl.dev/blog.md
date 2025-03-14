---
title: Hurl Blog
layout: blog
section: Blog
permalink: /blog/
indexed: false
---

# {{ page.title }}


{% for year in (2021..2025) reversed %}

## {{year}}

<ul class="u-list-style-none">
  {% for post in site.posts %}
    {% capture current_year %}{{ post.date | date: "%Y" }}{% endcapture %}
        {% assign year_str = year | append : "" %}
        {% if current_year == year_str %}
            <li class="row">
                <div class="col1 blog-post-short-date">{{ post.date | date: "%b. %d" }}</div>
                <div class="col6 blog-post-link"><a href="{{ post.url }}">{{ post.title }}</a></div>
            </li>
        {% endif %}
  {% endfor %}
</ul>

{% endfor %}
