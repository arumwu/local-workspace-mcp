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

Dependency overrides: sharp 0.35.5 includes the earlier image fixes and fixes
[GHSA-wq5f-xc86-pv6w](https://github.com/advisories/GHSA-wq5f-xc86-pv6w);
MCP SDK 1.31.0 fixes [GHSA-6qxp-vccf-f47h](https://github.com/advisories/GHSA-6qxp-vccf-f47h);
proxy-addr 2.0.8 fixes [GHSA-jqcg-44mw-7w3h](https://github.com/advisories/GHSA-jqcg-44mw-7w3h).
Argparse 2.0.1 removes the unpatched sprintf-js dependency
([GHSA-hp3w-g68c-fv3c](https://github.com/advisories/GHSA-hp3w-g68c-fv3c)); its v1 compatibility
API preserves the js-yaml 3 CLI used alongside gray-matter's safeLoad/safeDump API.
ExcelJS uses uuid 11.1.1 to fix GHSA-w5hq-g745-h8pq. Integration tests cover the pinned engine,
YAML front matter/CLI, image round trips and the literal-file PDF watcher.
Other dependencies retain their respective licenses in installed distributions. The Docker worker contains
LibreOffice, Poppler, fonts and Python/Node packages under their upstream licenses; no binary image is
redistributed by this source release.
