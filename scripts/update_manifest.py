#!/usr/bin/env python3
"""Update manifest.json for a newly published Emberforge build.

Computes SHA-256 and size from a local artifact file, stamps updatedAt, sets the
version, and validates the result. Run after uploading the artifact to a GitHub
Release, passing the release asset download URL.

Examples
--------
  python3 scripts/update_manifest.py client \\
      --version 1.4.2 --file client.jar \\
      --url https://github.com/cooperman00/emberforge-dist/releases/download/client-v1.4.2/emberforge-client.jar

  python3 scripts/update_manifest.py launcher \\
      --version 1.1.0 --platform windows-x64 --file EmberforgeSetup.exe \\
      --url https://github.com/cooperman00/emberforge-dist/releases/download/launcher-v1.1.0/EmberforgeSetup.exe
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys

MANIFEST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manifest.json")
PLATFORMS = ("windows-x64", "macos-arm64", "macos-x64", "linux-x64")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load() -> dict:
    with open(MANIFEST) as f:
        return json.load(f)


def save(data: dict) -> None:
    with open(MANIFEST, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def validate(data: dict) -> None:
    assert data.get("schemaVersion") == 1, "schemaVersion must be 1"
    for key in ("channel", "updatedAt", "launcher", "client"):
        assert key in data, f"missing top-level key: {key}"
    assert SEMVER.match(data["launcher"]["version"]), "launcher.version not semver"
    assert SEMVER.match(data["client"]["version"]), "client.version not semver"
    assert data["client"].get("obfuscated") is True, "client.obfuscated must be true for a public release"
    for plat, art in data["launcher"]["artifacts"].items():
        assert plat in PLATFORMS, f"unknown launcher platform: {plat}"
        _check_artifact(art, f"launcher.artifacts.{plat}")
    _check_artifact(data["client"]["artifact"], "client.artifact")


def _check_artifact(art: dict, where: str) -> None:
    for k in ("url", "sha256", "size"):
        assert k in art, f"{where} missing {k}"
    # empty artifacts (not-yet-shipped) are allowed; a populated one must be consistent
    if art["url"] or art["sha256"] or art["size"]:
        assert art["url"], f"{where}: url set but empty"
        assert re.fullmatch(r"[0-9a-f]{64}", art["sha256"] or ""), f"{where}: sha256 must be 64 hex chars"
        assert isinstance(art["size"], int) and art["size"] > 0, f"{where}: size must be positive int"


def main() -> int:
    p = argparse.ArgumentParser(description="Update manifest.json for a new Emberforge build.")
    p.add_argument("kind", choices=("client", "launcher"))
    p.add_argument("--version", required=True, help="semver, e.g. 1.4.2")
    p.add_argument("--file", required=True, help="local path to the built artifact")
    p.add_argument("--url", required=True, help="download URL (GitHub Release asset URL)")
    p.add_argument("--platform", choices=PLATFORMS, help="required for --kind launcher")
    p.add_argument("--notes", help="optional changelog note for this version")
    args = p.parse_args()

    if not SEMVER.match(args.version):
        p.error(f"--version {args.version!r} is not valid semver")
    if not os.path.isfile(args.file):
        p.error(f"--file not found: {args.file}")
    if args.kind == "launcher" and not args.platform:
        p.error("--platform is required for launcher builds")

    digest = sha256_of(args.file)
    size = os.path.getsize(args.file)
    artifact = {"url": args.url, "sha256": digest, "size": size}

    data = load()
    data["updatedAt"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if args.kind == "client":
        data["client"]["version"] = args.version
        data["client"]["artifact"] = artifact
    else:
        data["launcher"]["version"] = args.version
        data["launcher"]["artifacts"][args.platform] = artifact

    if args.notes:
        entry = {"version": args.version, "notes": args.notes}
        data.setdefault("changelog", [])
        data["changelog"] = [e for e in data["changelog"] if e.get("version") != args.version]
        data["changelog"].insert(0, entry)

    validate(data)
    save(data)
    print(f"Updated {args.kind} -> {args.version}")
    print(f"  sha256: {digest}")
    print(f"  size:   {size} bytes")
    print(f"  url:    {args.url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
