---
layout: doc
title: Installation
section: Getting Started
hurl-version: 1.3.1
---
# {{ page.title }}

## Binaries Installation

### Linux

Precompiled binary is available at [hurl-{{page.hurl-version}}-x86_64-linux.tar.gz](https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-x86_64-linux.tar.gz)

```
INSTALL_DIR=/tmp
curl -sL https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-x86_64-linux.tar.gz | tar xvz -C $INSTALL_DIR
export PATH=$INSTALL_DIR/hurl-{{page.hurl-version}}:$PATH

hurl --version
hurl {{page.hurl-version}}
```


#### Debian / Ubuntu {#debian-ubuntu}

For Debian / Ubuntu, Hurl can be installed using a binary .deb file provided in each Hurl release.

```
curl -LO https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl_{{page.hurl-version}}_amd64.deb
sudo dpkg -i hurl_{{page.hurl-version}}_amd64.deb
```

#### Arch Linux / Manjaro (via [AUR](https://wiki.archlinux.org/index.php/Arch_User_Repository)) {#arch-linux-manjaro-via-aur}

`hurl-bin` [package](https://aur.archlinux.org/packages/hurl-bin/) for Arch Linux and derived distros.

### macOS

Precompiled binary is available at [hurl-{{page.hurl-version}}-x86_64-osx.tar.gz](https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-x86_64-osx.tar.gz)

Hurl can also be installed with [Homebrew](https://brew.sh):

```
brew tap jcamiel/hurl
brew install hurl

hurl --version
hurl {{page.hurl-version}}
```

### Windows

#### Zip File

Hurl can be installed from a standalone zip file [hurl-{{page.hurl-version}}-win64.zip](https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-win64.zip).
You will need to update your PATH variable.


#### Installer

<span style="color:red">**!! There is an ongoing [issue](https://github.com/Orange-OpenSource/hurl/issues/267) with current installer [hurl-{{page.hurl-version}}-win64-installer.exe](https://github.com/Orange-OpenSource/hurl/releases/download/{{page.hurl-version}}/hurl-{{page.hurl-version}}-win64-installer.exe) 
for environment with PATH greater tham 1MB. You should probably save your PATH in this case !!**</span>

It should be fixed in the next release. { {

### Cargo

If you're a Rust programmer, Hurl can be installed with cargo.

```
cargo install hurl
```

## Building From Sources

Hurl sources are available in [GitHub](https://github.com/Orange-OpenSource/hurl)

### Build on Linux, macOS

Hurl depends on libssl, libcurl and libxml2 native libraries. You will need their development files in your platform.

```shell
# debian based distributions
apt install -y pkg-config libssl-dev libcurl4-openssl-dev libxml2-dev

# redhat based distributions
yum install -y pkg-config gcc openssl-devel libxml2-devel

# arch based distributions
pacman -Sy --noconfirm pkgconf gcc openssl libxml2

# osx
brew install pkg-config gcc openssl libxml2
```

Hurl is written in [Rust](https://www.rust-lang.org/). You should [install](https://www.rust-lang.org/tools/install) 
the latest stable release.

```shell
curl https://sh.rustup.rs -sSf | sh -s -- -y
source $HOME/.cargo/env
rustc --version
cargo --version
```

Build

```shell
git clone https://github.com/Orange-OpenSource/hurl
cd hurl
cargo build --release
./target/release/hurl --version
```

### Build on Windows

Please follow the [contrib/windows section](https://github.com/Orange-OpenSource/hurl/contrib/windows/README.md)




