#!/usr/bin/env python3
"""Compare the plugin release with Anthropic's pinned community version."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE_URL = (
    "https://raw.githubusercontent.com/anthropics/"
    "claude-plugins-community/main/.claude-plugin/marketplace.json"
)
PLUGIN_MANIFEST_URL = (
    "https://raw.githubusercontent.com/immersa-co/"
    "marcopolo-plugin/{sha}/.claude-plugin/plugin.json"
)


def fetch_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "marcopolo-sync-check"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def write_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output_file:
            output_file.write(f"{name}={value.replace(chr(10), ' ')}\n")


def write_summary(
    status: str,
    local_version: str,
    community_version: str,
    community_sha: str,
) -> None:
    summary = (
        "### Anthropic community marketplace sync\n\n"
        f"- Status: **{status}**\n"
        f"- Plugin repository version: `{local_version}`\n"
        f"- Community-pinned version: `{community_version}`\n"
        f"- Community-pinned SHA: `{community_sha}`\n"
    )
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary_file:
            summary_file.write(summary)
    print(summary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fail-if-stale",
        action="store_true",
        help="Return a failing status when the community version is behind",
    )
    args = parser.parse_args()

    with (ROOT / ".claude-plugin/plugin.json").open(encoding="utf-8") as file:
        local_version = str(json.load(file)["version"])

    try:
        marketplace = fetch_json(MARKETPLACE_URL)
        entry = next(
            plugin
            for plugin in marketplace["plugins"]
            if plugin.get("name") == "marcopolo"
        )
        community_sha = str(entry["source"]["sha"])
        community_manifest = fetch_json(
            PLUGIN_MANIFEST_URL.format(sha=community_sha)
        )
        community_version = str(community_manifest["version"])
    except (KeyError, StopIteration, OSError, urllib.error.URLError, json.JSONDecodeError) as error:
        message = str(error).replace("\n", " ")
        write_output("status", "error")
        write_output("error", message)
        print(f"ERROR: unable to inspect the community marketplace: {message}", file=sys.stderr)
        return 2

    status = "synced" if local_version == community_version else "stale"
    write_output("status", status)
    write_output("local_version", local_version)
    write_output("community_version", community_version)
    write_output("community_sha", community_sha)
    write_summary(status, local_version, community_version, community_sha)

    if status == "stale" and args.fail_if_stale:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
