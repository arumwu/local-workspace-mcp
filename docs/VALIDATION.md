# Validation record — updated 2026-10-19

Release status: **alpha**. Ordinary ChatGPT web Python calls verified; native App acceptance incomplete.

## Windows ZIP installer review — 2026-10-19

- ZIP entry points install/repair document mode in WSL2, then configure and start the official runtime.
- Regression tests demonstrated that WSL1 was previously accepted; it is now rejected before dependency checks.
- Commands bypass the Linux shell with `--exec`; Windows CI exercises argument preservation and failure handling
  using a fake WSL executable, including the new ZIP wrapper. This is not an actual Windows/WSL installation.
- On an isolated macOS source checkout: `82 passed` with `LWMCP_DOCKER_TESTS=1`, including full-engine stdio,
  Docker document/isolation checks, YAML front matter/CLI and Sharp image round trips. Two existing dependency
  deprecation warnings remain. The local Docker checks reused the existing, unchanged worker image.
- Ruff and `git diff --check` passed. Current npm and Python dependency scans report no known vulnerabilities
  (the project's editable Python package is skipped). Desktop Commander remains pinned at 0.2.50;
  [third-party notices](../THIRD_PARTY_NOTICES.md) document the narrow dependency overrides.
- The contributor's separate real Windows/WSL checks and their limits are recorded in [WINDOWS-WSL.md](WINDOWS-WSL.md).
  This maintenance review did not repeat those tests, provision a clean PC, or validate a new ChatGPT round trip.
- The owner's installed Mac service, tunnel, credentials and original source checkout were not updated or restarted.

The dated records below describe their original test environments and versions.

## Ordinary ChatGPT chat — 2026-09-17

- Personal ChatGPT account, ordinary Chat interface, model 6 Pro; not Codex or Work.
- Official tunnel-client v0.0.14 on macOS arm64, private workspace-associated STDIO tunnel.
- Plugin discovery succeeded with 41 tools after removing upstream UI template metadata whose resources
  are not exposed by this tool bridge. Tool functionality and non-UI metadata are preserved.
- Actual get_workflow_instructions and run_python calls returned CHATGPT_TUNNEL_OK_0917, exit code 0.
- After tunnel restart, actual run_python returned CHATGPT_RESTART_OK_0917, exit code 0.
- After removing the local Codex MCP registration, ordinary ChatGPT returned CHATGPT_ONLY_OK_0917, exit code 0.
- macOS background-item records identify the named launcher app rather than sh.
- Local suite: 31 passed, 3 optional Docker cases skipped; startup/installer-default tests: 8 passed.
  Ruff and git diff --check passed.
- These tests used print only and did not read private files or generate documents.
- macOS login startup was exercised by launchctl bootstrap and restart; a physical reboot was not performed.
- No private key, workspace/tunnel ID, personal chat URL or machine-specific configuration is published.


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

- **Native ChatGPT App and complete document-workflow acceptance.** The available computer-control tool refused the
  resolved app with `Computer Use is not allowed to use app com.openai.codex`; that restriction was respected.
  Ordinary web chat through the private tunnel is verified above; native App and all-plan support are not.
- Physical two-Mac SSH pairing (no second-machine connection/credentials supplied).
- Customer-owned public HTTPS deployment, tunnel availability on other accounts and client download display.
- Signed macOS distribution and clean-machine prerequisite installation.
- Native Windows. Execution is blocked by POSIX-only code paths; see "Windows status" below.

The 2026-09-11 checks below did not provision a public endpoint. The 2026-09-17 follow-up provisioned a
private official tunnel and a local background process with owner authorization. Use CHATGPT.en.md for
ordinary-chat setup. The project does not claim equivalence to ChatGPT Work.

## Installer update — v0.1.1-alpha.1

The owner completed registration manually. A read-only check confirmed the launcher was configured and
enabled; the updater was not run against the owner's real client settings.
Five new registration tests cover preservation/backups, custom names and disabled entries, malformed data,
conflicts, intentional config symlinks, first installation and inline tables.
An independent source copy was installed against a synthetic client config, which retained its previous
settings. The automatically registered command was then launched through the official MCP SDK and a
host_write_file call wrote and verified a test file. This verifies installation/configuration/transport,
not an actual model-initiated ChatGPT conversation. The Docker worker is unchanged from the previous release.

## Windows status — corrected 2026-09-14

A 2026-09-12 note recorded the owner's confirmation that Windows validation was complete. That note did
not add code, tests, a Windows CI job or a native installer, and native Windows execution is currently
blocked by POSIX-only code paths:

- `Workspace` refuses non-POSIX systems: "Use Linux Docker on Windows; native Windows is not supported."
- `client_setup.py` imports `fcntl`, which does not exist on Windows.
- `runner.py` passes `os.getuid()` / `os.getgid()` to Docker.
- `cli.py`, `server.py` and `workspace.py` use `os.O_NOFOLLOW`, `os.O_DIRECTORY` and `dir_fd`.
- `scripts/install.py` uses `.venv/bin/...` paths and writes a `#!/bin/sh` launcher; `Install.command` is POSIX sh.
- CI runs only on `ubuntu-latest` and `macos-latest`.

On Windows 11 with CPython 3.14.2, `fcntl` is unavailable, `os.O_NOFOLLOW`, `os.O_DIRECTORY` and
`os.getuid` are absent, and `os.open` does not support `dir_fd`. Native Windows is therefore listed as
unsupported and unverified. Linux environments on Windows (for example WSL2 or a container) have not
been validated either.
