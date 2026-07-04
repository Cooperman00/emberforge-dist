# Emberforge — Distribution Architecture

This document describes how Emberforge is split across repositories and how a
build flows from source to a player's machine.

## Repositories

| Repo | Visibility | Contains | Never contains |
|------|-----------|----------|----------------|
| `emberforge` | **private** | Server source, client source (dev), launcher source, build & obfuscation pipeline, cabbage sprite/item cache work | Public downloads |
| `emberforge-dist` (this repo) | **public** | `manifest.json`, docs, publish scripts; launcher installer + launcher build + obfuscated client build as **GitHub Releases** | Any source code, unobfuscated client, server code |

**Rule of thumb:** if it's source, it belongs in the private repo. If it's a
thing a player downloads and runs, it's published here as a release artifact and
referenced from `manifest.json`.

## The update flow

```
 private emberforge repo                         emberforge-dist (public)                player machine
 ────────────────────────                        ────────────────────────                ──────────────
 1. build client  ──▶ obfuscate (ProGuard) ──▶   5. upload jar to GitHub Release          8. launcher starts
 2. build launcher/installer            │        6. run scripts/update_manifest.py  ──▶   9. fetch manifest.json (raw)
 3. run tests                           │        7. commit + push manifest.json           10. compare local vs manifest version
 4. tag release ───────────────────────┘                                                  11. download + verify sha256
                                                                                           12. swap in new client, launch
```

1–4 happen in the **private** repo's CI. 5–7 publish here. 8–12 are the launcher
on the player's machine.

## What the launcher does (client contract)

1. On start, fetch `manifest.json` from this repo's raw URL:
   `https://raw.githubusercontent.com/cooperman00/emberforge-dist/main/manifest.json`
2. Compare the local installed **client** version to `client.version`.
   If older, download `client.artifact.url`, verify its SHA-256 matches
   `client.artifact.sha256`, and only then replace the local client.
3. Compare the local **launcher** version to `launcher.version`. If the local
   launcher is below `launcher.minimumSupported`, force a self-update before
   letting the player continue; otherwise offer it.
4. Never run an artifact whose SHA-256 does not match the manifest. A checksum
   mismatch means a corrupted download or a tampered mirror — abort and re-fetch.

## Obfuscation (why and where)

The client is developed in the clear inside the private repo, but the build that
ships here **must be obfuscated** so players can't trivially decompile it and lift
the source.

- Obfuscation is a **build step in the private repo**, not something this repo
  does. Only the obfuscated jar is ever uploaded here.
- For a Java / cabbage-based client, use **ProGuard** (or Allatori) in the build:
  rename classes/methods/fields, strip debug line numbers and source-file
  attributes, and keep only the real entry point (`public static void main`) plus
  any reflectively-referenced classes.
- Keep the **ProGuard mapping file** (`mapping.txt`) private and archived per
  release so obfuscated crash/stack traces can still be de-obfuscated internally.
  Never publish the mapping file here.
- Obfuscation raises the cost of theft; it is not DRM. Anything shipped to a
  client can ultimately be reversed. Keep all authoritative game logic on the
  **server**, never trust the client, and treat the obfuscated jar as a
  deterrent, not a guarantee.

## Channels

`manifest.json` has a `channel` field (`release` by default). If you later want a
`beta` or `staging` track, publish a second manifest (e.g. `manifest.beta.json`)
and point testing launchers at it. Keep the schema identical.
