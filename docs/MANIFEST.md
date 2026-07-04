# `manifest.json` schema

The launcher reads this file to decide what to download. It is the single source
of truth for "what is the latest launcher and client, and how do I verify them."

Fetch it from the raw URL (no GitHub API/auth needed):

```
https://raw.githubusercontent.com/cooperman00/emberforge-dist/main/manifest.json
```

## Fields

| Field | Type | Meaning |
|-------|------|---------|
| `schemaVersion` | int | Manifest format version. Currently `1`. Bump only on breaking format changes. |
| `channel` | string | Release track: `release`, `beta`, etc. |
| `updatedAt` | string (ISO-8601 UTC) | When the manifest was last published. Set automatically by the publish script. |
| `launcher.version` | string (semver) | Latest launcher version. |
| `launcher.minimumSupported` | string (semver) | Launchers below this **must** self-update before continuing. |
| `launcher.artifacts` | object | Per-platform launcher downloads, keyed by platform id. |
| `client.version` | string (semver) | Latest client version. |
| `client.obfuscated` | bool | Must be `true` for any public release. A sanity flag the publish script can assert on. |
| `client.artifact` | object | The single client download (one cross-platform jar). |
| `changelog` | array | Optional list of `{ "version": "...", "notes": "..." }` entries, newest first. |

### Artifact object

Every download (`launcher.artifacts.<platform>` and `client.artifact`) is:

| Field | Type | Meaning |
|-------|------|---------|
| `url` | string | Direct download URL (a GitHub Release asset URL). |
| `sha256` | string | Lowercase hex SHA-256 of the file. The launcher **must** verify this. |
| `size` | int | File size in bytes (lets the launcher show a progress bar and sanity-check). |

Platform ids for `launcher.artifacts`: `windows-x64`, `macos-arm64`,
`macos-x64`, `linux-x64`. Leave a platform's fields empty (`""` / `0`) if you
don't ship that platform yet.

## Publishing a new build

Never hand-edit `sha256`/`size`/`updatedAt`. Use the script:

```bash
# after uploading the file to a GitHub Release and getting its download URL:
python3 scripts/update_manifest.py client \
  --version 1.4.2 \
  --file /path/to/emberforge-client.jar \
  --url  https://github.com/cooperman00/emberforge-dist/releases/download/client-v1.4.2/emberforge-client.jar

python3 scripts/update_manifest.py launcher \
  --version 1.1.0 \
  --platform windows-x64 \
  --file /path/to/EmberforgeSetup.exe \
  --url  https://github.com/cooperman00/emberforge-dist/releases/download/launcher-v1.1.0/EmberforgeSetup.exe
```

The script computes the SHA-256 and size from the local file, stamps
`updatedAt`, updates the version, and validates the result. Then commit and push
`manifest.json`.
