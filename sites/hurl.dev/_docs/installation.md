---
layout: doc
title: Installation
section: Getting Started
hurl-version: 1.3.0
---
# {{ page.title }}

## Linux {#linux}

Precompiled binary is available at [hurl-{{page.hurl-version}}-x86_64-linux.tar.gz](https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-x86_64-linux.tar.gz)

```
INSTALL_DIR=/tmp
curl -sL https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-x86_64-linux.tar.gz | tar xvz -C $INSTALL_DIR
export PATH=$INSTALL_DIR/hurl-{{page.hurl-version}}:$PATH

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

An installer is available at [hurl-{{page.hurl-version}}-win64-installer.exe](https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-win64-installer.exe)

Hurl can also be installed from a standalone zip file [hurl-{{page.hurl-version}}-win64.zip](https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-win64.zip).
You will need to update your PATH variable.


## Cargo

If you're a Rust programmer, Hurl can be installed with cargo.

```
cargo install hurl
```


## Building {#building}

Hurl can be build from source (available in [GitHub](https://github.com/Orange-OpenSource/hurl))


## Hurl - JVM Based {#hurl-jvm-based}

A jvm flavour is also available as a standalone fat JAR at [Hurl JVM](https://github.com/Orange-OpenSource/hurl-jvm).



