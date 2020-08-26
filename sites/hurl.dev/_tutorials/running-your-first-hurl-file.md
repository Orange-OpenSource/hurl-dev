---
layout: tutorial
title: Running your first Hurl file
published: false
---
# {{page.title}}


Welcome to Hurl's tutorial!

Throughout this tutorial, we’ll walk you through the creation of a basic pet shop application, and 
learn how to test it with Hurl.

Our web application consist of two parts:

- a be site that have a public home page and a logged page for returning customers,
- a REST api that let you add, change and delete pets.

We'll assume that you have [Hurl installed](), you can tell Hurl is installed by running the following command in
a shell prompt:

```bash
$ hurl --version
```

If Hurl is installed, you should see the version of your installation.