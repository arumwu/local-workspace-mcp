# Validation record — 2026-09-11

Release status: **alpha**. Actual ChatGPT app acceptance is incomplete.

## Verified locally on macOS

- 24 pytest cases passed, including actual upstream stdio and Docker runs (10.79 seconds).
- Actual full installer completed; generated launcher initialized through the official MCP Python client,
  listed **41 tools**, and ran the Docker worker successfully.
- File read/write/edit/move, directory operations, streaming search/list/page/stop.
- Interactive process stdin/output; session and system process lists; termination only of test-owned processes.
- PDF generation and page insertion using existing Chrome; PDF text extraction.
- Configuration, prompt retrieval/library, redacted activity history, usage and local feedback.
- Two independent local agents: pairing list, MCP ping, remote schemas and named-device tool invocation.
- DOCX/XLSX/PPTX/PDF/PNG generation and reopening; totals verified as 300.
- Chinese DOCX converted by LibreOffice to PDF/PNG; preview visually inspected and readable.
- XLSX formula recalculated by LibreOffice and verified with data_only=True as 300.
- Docker input write/network attempts blocked; excessive output stops job; next job still works.
- OAuth code flow, PKCE, consent CSRF/owner-key checks, redirect/resource checks, refresh replay revocation,
  unauthorized HTTP, Host/Origin/body limits, temporary artifact download and changed-file invalidation.
- Actual shutdown_device_agent returned a response and stopped only its own process.
- Sharp 0.35.4 image round trip and ExcelJS/uuid 11.1.1 XLSX round trip passed.
- npm dependency audit: zero known vulnerabilities. Python dependency audit: zero known vulnerabilities (own editable package skipped).
- Ruff passed. Worker base digest and Python requirements hashes are pinned.

Two deprecation warnings arise from Starlette test-client dependencies; tests pass.
PDF rendering emitted a nonfatal Java/font-cache warning in the manual run; PDF/PNG output was valid.
This is not an exhaustive security audit, performance benchmark or upstream conformance suite.

## Still unverified / blocked

- **Actual ChatGPT desktop/web end-to-end acceptance.** The available computer-control tool refused the
  resolved app with `Computer Use is not allowed to use app com.openai.codex`; that restriction was respected.
  No claim is made that ordinary ChatGPT chat has access to local MCP or that a particular plan unlocks it.
- Physical two-Mac SSH pairing (no second-machine connection/credentials supplied).
- Customer-owned public HTTPS deployment, official tunnel/account availability and client download display.
- Maintainer reproduction on Windows (native Windows / WSL2), signed macOS distribution and clean-machine prerequisite installation.

No public endpoint, third-party account or remote daemon was provisioned. Use CONNECT.md for real-client
acceptance. The project is installed and protocol-tested, but these outstanding checks prevent calling the
entire ChatGPT Work-equivalent experience complete.

## Installer update — v0.1.1-alpha.1

The owner completed registration manually. A read-only check confirmed the launcher was configured and
enabled; the updater was not run against the owner's real client settings.
Five new registration tests cover preservation/backups, custom names and disabled entries, malformed data,
conflicts, intentional config symlinks, first installation and inline tables.
An independent source copy was installed against a synthetic client config, which retained its previous
settings. The automatically registered command was then launched through the official MCP SDK and a
host_write_file call wrote and verified a test file. This verifies installation/configuration/transport,
not an actual model-initiated ChatGPT conversation. The Docker worker is unchanged from the previous release.

## Community report — Windows (2026-09-12)

The project owner relayed that another user successfully tested Windows. This is a community report,
not a maintainer-run test. The Windows version, native Windows versus WSL2 environment, package version,
and exact features tested have not yet been supplied. No Windows CI run or native Windows installer
is included in this release.
