# Third-party notices

The optional full-mode engine is [DesktopCommanderMCP](https://github.com/wonderwhy-er/DesktopCommanderMCP),
MIT licensed, copyright (c) 2024-2025 Eduard Ruzga and Desktop Commander Contributors.
The exact package is `@wonderwhy-er/desktop-commander@0.2.50`; npm integrity is pinned in package-lock.json.
Its original license is preserved in [docs/DesktopCommander-LICENSE](docs/DesktopCommander-LICENSE).
The proprietary hosted remote relay is not copied or provided.

Local changes in scripts/patch_engine.py: relocate state; disable telemetry feature initialization and
browser auto-install; redact argument/result history; disable fuzzy document-content logging.
The bridge forces the telemetry kill switch and replaces vendor feedback with local storage.
Every patched source is checked against its original SHA-256; originals remain in node_modules as .upstream.

Dependency overrides: sharp 0.35.4 fixes GHSA-f88m-g3jw-g9cj / GHSA-rgj7-g3m4-5g8c;
exceljs uses uuid 11.1.1 to fix GHSA-w5hq-g745-h8pq. They are integration-tested with this engine.
Other dependencies retain their respective licenses in installed distributions. The Docker worker contains
LibreOffice, Poppler, fonts and Python/Node packages under their upstream licenses; no binary image is
redistributed by this source release.
