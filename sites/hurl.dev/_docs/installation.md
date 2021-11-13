---
layout: doc
title: Installation
description: How to install or build Hurl on Linux, macOS and Windows platform.
section: Getting Started
hurl-version: 1.4.0
---
# {{ page.title }}

## Binaries Installation

### Linux

Precompiled binary is available at [hurl-{{ page.hurl-version }}-x86_64-linux.tar.gz]:

```shell
$ INSTALL_DIR=/tmp
$ curl -sL https://github.com/Orange-OpenSource/hurl/releases/download/{{ page.hurl-version }}/hurl-{{ page.hurl-version }}-x86_64-linux.tar.gz | tar xvz -C $INSTALL_DIR
$ export PATH=$INSTALL_DIR/hurl-{{ page.hurl-version }}:$PATH

$ hurl --version
hurl {{ page.hurl-version }}
```

#### Debian / Ubuntu

For Debian / Ubuntu, Hurl can be installed using a binary .deb file provided in each Hurl release.

```shell
$ curl -LO https://github.com/Orange-OpenSource/hurl/releases/download/{{ page.hurl-version }}/hurl_{{ page.hurl-version }}_amd64.deb
$ sudo dpkg -i hurl_{{ page.hurl-version }}_amd64.deb
```

#### Arch Linux / Manjaro

[`hurl-bin` package] for Arch Linux and derived distros are available via [AUR].

### macOS

Precompiled binary is available at [hurl-{{ page.hurl-version }}-x86_64-osx.tar.gz].

Hurl can also be installed with [Homebrew]:

```shell
$ brew tap jcamiel/hurl
$ brew install hurl

$ hurl --version
hurl {{ page.hurl-version }}
```

### Windows

#### Zip File

Hurl can be installed from a standalone zip file [hurl-{{ page.hurl-version }}-win64.zip]. You will need to update your `PATH` variable.

#### Installer

An installer [hurl-{{ page.hurl-version }}-win64-installer.exe] is also available.

#### Chocolatey

```shell
$ choco install hurl
```

#### Scoop

```shell
$ scoop install hurl
```

#### Windows Package Manager

```shell
$ winget install hurl
```

### Cargo

If you're a Rust programmer, Hurl can be installed with cargo.

```shell
$ cargo install hurl
```

## Building From Sources

Hurl sources are available in [GitHub].

### Build on Linux, macOS

Hurl depends on libssl, libcurl and libxml2 native libraries. You will need their development files in your platform.

```shell
# debian based distributions
apt install -y pkg-config libssl-dev libcurl4-openssl-dev libxml2-dev

# redhat based distributions
yum install -y pkg-config gcc openssl-devel libxml2-devel

# arch based distributions
pacman -Sy --noconfirm pkgconf gcc openssl libxml2
```

Hurl is written in [Rust]. You should [install] the latest stable release.

```shell
$ curl https://sh.rustup.rs -sSf | sh -s -- -y
$ source $HOME/.cargo/env
$ rustc --version
$ cargo --version
```

Build

```shell
$ git clone https://github.com/Orange-OpenSource/hurl
$ cd hurl
$ cargo build --release
$ ./target/release/hurl --version
```

### Build on Windows

Please follow the [contrib on Windows section].

[GitHub]: https://github.com/Orange-OpenSource/hurl
[hurl-{{ page.hurl-version }}-win64.zip]: https://github.com/Orange-OpenSource/hurl/releases/download/{{ page.hurl-version }}/hurl-{{ page.hurl-version }}-win64.zip
[hurl-{{ page.hurl-version }}-win64-installer.exe]: https://github.com/Orange-OpenSource/hurl/releases/download/{{ page.hurl-version }}/hurl-{{ page.hurl-version }}-win64-installer.exe
[hurl-{{ page.hurl-version }}-x86_64-osx.tar.gz]: https://github.com/Orange-OpenSource/hurl/releases/download/{{ page.hurl-version }}/hurl-{{ page.hurl-version }}-x86_64-osx.tar.gz
[hurl-{{ page.hurl-version }}-x86_64-linux.tar.gz]: https://github.com/Orange-OpenSource/hurl/releases/download/{{ page.hurl-version }}/hurl-{{ page.hurl-version }}-x86_64-linux.tar.gz
[Homebrew]: https://brew.sh
[AUR]: https://wiki.archlinux.org/index.php/Arch_User_Repository
[`hurl-bin` package]: https://aur.archlinux.org/packages/hurl-bin/
[install]: https://www.rust-lang.org/tools/install
[Rust]: https://www.rust-lang.org
[contrib on Windows section]: https://github.com/Orange-OpenSource/hurl/blob/master/contrib/windows/README.md



