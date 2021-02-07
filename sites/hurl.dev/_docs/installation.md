---
layout: doc
title: Installation
hurl-version: 1.1.0
---
# {{ page.title }}

## Linux {#linux}

Precompiled binary is available at [hurl-{{page.hurl-version}}-x86_64-linux.tar.gz](https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-x86_64-linux.tar.gz)

```
INSTALL_DIR=/tmp
curl -sL https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-x86_64-linux.tar.gz | tar xvz -C $INSTALL_DIR
export PATH=$INSTALL_DIR/hurl-$VERSION:$PATH

hurl --version
hurl {{page.hurl-version}}
```


### Debian / Ubuntu {#debian-ubuntu}

For Debian / Ubuntu, Hurl can be installed using a binary .deb file provided in each Hurl release.

```
curl -LO https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl_{{page.hurl-version}}_amd64.deb
sudo dpkg -i hurl_{{page.hurl-version}}_amd64.deb
```

### Arch Linux / Manjaro (via [AUR](https://wiki.archlinux.org/index.php/Arch_User_Repository)) {#arch}

`hurl-bin` [package](https://aur.archlinux.org/packages/hurl-bin/) for Arch Linux and derived distros.


## macOS {#macos}

Precompiled binary is available at [hurl-{{page.hurl-version}}-x86_64-osx.tar.gz](https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-x86_64-osx.tar.gz)

Hurl can also be installed with [Homebrew](https://brew.sh):

```
brew tap jcamiel/hurl
brew install hurl

hurl --version
hurl {{page.hurl-version}}
```

## Windows {#windows}

Installation for Windows is coming soon (next release).


## Building {#building}

Hurl can be build from source (available in [GitHub](https://github.com/Orange-OpenSource/hurl))


## Hurl - JVM Based {#hurl-jvm-based}

A jvm flavour is also available as a standalone fat JAR at [Hurl JVM](https://github.com/Orange-OpenSource/hurl-jvm).



