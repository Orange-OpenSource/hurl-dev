#!/usr/bin/env python3
"""Create SHASUM from GitHub release artifacts for a given version

Example:
    $ python3 get_artifacts_hash.py 1.7.0

"""

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass

import requests


@dataclass
class Asset:
    name: str
    download_url: str

    def shasum256(self) -> str:
        resp = requests.get(self.download_url, allow_redirects=True)
        _hash = hashlib.sha256(resp.content).hexdigest()
        return _hash


def github_graphql(
    token: str,
    query: str,
) -> str:
    """Execute a GraphQL query using GitHub API."""
    url = "https://api.github.com/graphql"
    query_json = {"query": query}
    body = json.dumps(query_json)
    sys.stderr.write("* POST %s\n" % url)
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.post(url, data=body, headers=headers)
    if r.status_code != 200:
        raise Exception("HTTP Error %s - %s" % (r.status_code, r.text))
    return r.text


def get_release_assets(version: str, token: str) -> list[Asset]:
    """return assets release for the given tag"""
    query = """\
query {
  repository(owner:"Orange-OpenSource", name:"hurl") {
    release(tagName:"VERSION") {
      releaseAssets(first:20) {
        edges {
          node {
            name
            contentType
            downloadUrl
            url
          }
        }
      }
    }
  }
}
"""
    query = query.replace("VERSION", version)
    payload = github_graphql(token=token, query=query)
    response = json.loads(payload)
    assets_list = response["data"]["repository"]["release"]["releaseAssets"]["edges"]
    assets = []
    for node in assets_list:
        name = node["node"]["name"]
        download_url = node["node"]["downloadUrl"]
        asset = Asset(name=name, download_url=download_url)
        assets.append(asset)

    # We add source artifacts (not returned by the APIs)
    name = f"{version}.zip"
    download_url = f"https://github.com/Orange-OpenSource/hurl/archive/refs/tags/{name}"
    asset = Asset(name=name, download_url=download_url)
    assets.append(asset)

    name = f"{version}.tar.gz"
    download_url = f"https://github.com/Orange-OpenSource/hurl/archive/refs/tags/{name}"
    asset = Asset(name=name, download_url=download_url)
    assets.append(asset)

    return assets


def main():
    parser = argparse.ArgumentParser(description="Get Hurl release artifacts shasum")
    parser.add_argument("version", help="Hurl release version ex 4.2.0")
    parser.add_argument("--token", help="GitHub authentication token")
    args = parser.parse_args()
    if args.version == "":
        raise Exception("version can not be empty")

    assets = get_release_assets(version=args.version, token=args.token)
    # We keep only the binary files
    assets = [a for a in assets if not a.name.endswith(".sha256")]
    assets.sort(key=lambda x: x.name)
    for a in assets:
        print(f"{a.download_url},{a.shasum256()}")


if __name__ == "__main__":
    main()
