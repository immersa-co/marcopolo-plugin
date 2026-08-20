#!/usr/bin/env python3
"""Validate plugin versions and require release bumps for runtime changes."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CLAUDE_MANIFEST = Path(".claude-plugin/plugin.json")
CODEX_MANIFEST = Path(".codex-plugin/plugin.json")
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
RUNTIME_FILES = {
    ".mcp.json",
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".codex/config.toml",
}
RUNTIME_DIRECTORIES = ("agents/", "assets/", "skills/")
CODEX_TOP_LEVEL_FIELDS = {
    "id",
    "name",
    "version",
    "description",
    "skills",
    "apps",
    "mcpServers",
    "interface",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
}
CODEX_INTERFACE_STRINGS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
}


def load_manifest(path: Path) -> dict[str, object]:
    with (ROOT / path).open(encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def version_at(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{CLAUDE_MANIFEST.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return str(json.loads(result.stdout)["version"])


def changed_runtime_paths(base: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", base, "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = [path for path in result.stdout.splitlines() if path]
    return [
        path
        for path in paths
        if path in RUNTIME_FILES or path.startswith(RUNTIME_DIRECTORIES)
    ]


def validate_codex_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    unknown_fields = sorted(set(manifest) - CODEX_TOP_LEVEL_FIELDS)
    if unknown_fields:
        errors.append(
            "Codex manifest has unsupported top-level fields: "
            + ", ".join(unknown_fields)
        )

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        return errors + ["Codex manifest interface must be an object"]

    for field in sorted(CODEX_INTERFACE_STRINGS):
        value = interface.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Codex manifest interface.{field} must be a string")

    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities or not all(
        isinstance(value, str) and value.strip() for value in capabilities
    ):
        errors.append("Codex manifest interface.capabilities must contain strings")

    prompts = interface.get("defaultPrompt", interface.get("default_prompt"))
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3 or not all(
        isinstance(value, str) and value.strip() and len(value) <= 128
        for value in prompts
    ):
        errors.append(
            "Codex manifest interface.defaultPrompt must contain 1-3 strings "
            "of at most 128 characters"
        )

    for field in ("composerIcon", "logo", "logoDark"):
        value = interface.get(field)
        if value is not None and (
            not isinstance(value, str) or not (ROOT / value).is_file()
        ):
            errors.append(f"Codex manifest interface.{field} must reference a file")

    for field in ("skills", "mcpServers"):
        value = manifest.get(field)
        if isinstance(value, str) and not (ROOT / value).exists():
            errors.append(f"Codex manifest {field} path does not exist: {value}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="Base git ref used to enforce a version bump")
    parser.add_argument("--tag", help="Release tag that must equal v<manifest version>")
    args = parser.parse_args()

    claude_manifest = load_manifest(CLAUDE_MANIFEST)
    codex_manifest = load_manifest(CODEX_MANIFEST)
    claude_version = str(claude_manifest.get("version", ""))
    codex_version = str(codex_manifest.get("version", ""))
    errors: list[str] = []

    errors.extend(validate_codex_manifest(codex_manifest))

    if not SEMVER.fullmatch(claude_version):
        errors.append(f"Claude manifest version is not valid semver: {claude_version!r}")
    if not SEMVER.fullmatch(codex_version):
        errors.append(f"Codex manifest version is not valid semver: {codex_version!r}")
    if claude_version != codex_version:
        errors.append(
            "Claude and Codex manifest versions differ: "
            f"{claude_version!r} != {codex_version!r}"
        )

    if args.tag and args.tag != f"v{claude_version}":
        errors.append(
            f"Release tag {args.tag!r} does not match manifest version "
            f"v{claude_version}"
        )

    if args.base:
        runtime_paths = changed_runtime_paths(args.base)
        if runtime_paths:
            base_version = version_at(args.base)
            if base_version == claude_version:
                formatted_paths = "\n  - ".join(runtime_paths)
                errors.append(
                    "Plugin runtime files changed without a version bump "
                    f"from {base_version}:\n  - {formatted_paths}"
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Release metadata valid at version {claude_version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
