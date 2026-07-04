# Emberforge Dist

Public distribution repository for **Emberforge**.

Players get everything they run from here. This repo does **not** contain game
or client source code — that lives in the private `emberforge` repo. This repo
holds only:

- **`manifest.json`** — the auto-update contract the launcher reads to decide
  whether a newer launcher or client is available, where to download it, and
  how to verify it (SHA-256).
- **Launcher installer** and **launcher builds** (published as GitHub Releases).
- **Latest obfuscated client build** (published as a GitHub Release).
- **`docs/`** — how distribution, updates, and obfuscation work.
- **`scripts/`** — helper to update `manifest.json` when a new build is published.

Large binaries (installers, jars) are attached to **GitHub Releases**, not
committed into git, so the repo stays small. `manifest.json` points at those
release download URLs.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full picture and
[`docs/MANIFEST.md`](docs/MANIFEST.md) for the manifest schema.
