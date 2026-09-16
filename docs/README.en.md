# Local Workspace MCP

Local files, terminal, documents and Python for **ordinary ChatGPT conversations**, through a private MCP tunnel.
**Early alpha: ordinary ChatGPT web Python calls verified; native ChatGPT App acceptance pending.**
Start with the [ChatGPT connection guide](CHATGPT.en.md) and the [current source ZIP](https://github.com/arumwu/local-workspace-mcp/archive/refs/heads/main.zip).
This does not unlock ChatGPT Work, add AI credits, or guarantee that every ChatGPT mode supports local MCP.

[繁體中文首頁](../README.md) · [中文安裝教學](README.zh-TW.md) · [Connections](CONNECT.md) · [Feature coverage](FEATURES.md) · [Validation](VALIDATION.md) · [Security](../SECURITY.md)


Already installed? Read the [everyday user guide: computers, phones and host availability](USAGE.en.md).

## Two explicit modes

| Mode | Access |
|---|---|
| `documents` (default) | Dedicated workspace; Python runs in Docker with read-only inputs, writable `exports`, no network. Word, Excel, PowerPoint, PDF, charts, LibreOffice/Poppler previews. |
| `full` | Adds 25 tools from MIT-licensed Desktop Commander 0.2.50: read/search/edit files, PDF creation/modification, interactive processes, configuration and activity. **Full OS user-account access**, including network and destructive commands. Directory settings are not a sandbox. |

Named computers connect through your existing SSH credentials, or another owner-configured stdio command.
There is no maintainer-run relay, account service, subscription, or feedback collection.
Selected file contents/tool results go to your AI provider. SSH uses your own hosts; an optional tunnel uses its provider.

## Install (macOS / Linux)

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/), Git; full mode also requires Node.js 20.9+, npm and ripgrep.
Docker is required for isolated document jobs. Existing Chrome/Chromium is required for `host_write_pdf`;
no browser is downloaded automatically.

**Native Windows is not currently supported or validated.** The code relies on POSIX-only APIs such as
`fcntl`, `os.getuid`, `os.O_NOFOLLOW` and `dir_fd`, and there is no Windows CI job or native Windows installer.
The installation instructions below target macOS/Linux.

```sh
git clone https://github.com/arumwu/local-workspace-mcp.git
cd local-workspace-mcp
./Install.command --workspace /absolute/path/task-files \
  --state /absolute/path/private-state --mode full
```

Choose existing storage appropriate to your computer. Keep private state outside the workspace.
Use `--mode documents` for isolated document work, or `--skip-worker` when Docker is not needed.
The installer installs checkout-local dependencies and builds the worker. By default it does **not** change
Codex/local STDIO client settings. Connect the generated `private-state/launch.sh` using the
[official private tunnel workflow](CHATGPT.en.md), then verify a real ordinary ChatGPT conversation.
Double-click `Install.command` for guided local setup. Prerequisites and account setup remain necessary.

Optional `--register-local-client` enables the older local STDIO registration, with backups and preservation
of existing names/disabled settings. Explicit `--client-config` also opts in unless `--no-register` is given.
This optional compatibility path is not the primary ChatGPT chat setup. Historical v0.1.1-alpha.1 archives
lack the new ChatGPT discovery fix; use current source. macOS named login startup is documented in the guide.

## Useful requests

- Analyze a CSV, create an Excel report and a chart, then verify the totals.
- Read Word/Excel/PDF inputs and produce edited documents; render previews and inspect them.
- In full mode: explore a repository, change code, start a development server and read its output.
- Pair another computer, then address its tools by name.

`get_workflow_instructions` explains the document workflow. `run_python` sees `/workspace` and writes `/output`.
Office/PDF libraries plus LibreOffice and Poppler are preinstalled. Each job is fresh: 90 seconds, 512 MiB,
1 CPU, 64 PIDs, 64 KiB per output stream. One job at a time; output disk usage is not quota-limited.
For LibreOffice use `-env:UserInstallation=file:///tmp/lo`; temporary files belong in `/tmp`.
In full mode, after checking an edited document in exports, host tools can replace its original path.
Back up originals first; the server does not provide automatic version history.

`list_artifacts` plus `get_artifact_path` exposes local output paths. Client rendering/download support varies.
HTTP mode adds ten-minute bearer download links. Anyone holding such a link can read that one file.

## Advanced server options

```sh
uv run local-workspace-mcp serve --help
uv run local-workspace-mcp init-key /absolute/private-state/owner.key
uv run local-workspace-mcp serve --root /absolute/task-files --write --python \
  --transport http --public-url https://mcp.example.com \
  --key-file /absolute/private-state/owner.key
```

HTTP binds loopback only, requires your HTTPS reverse proxy and OAuth consent, and stores tokens in memory.
Full host tools require explicit `--host-engine /path/to/patched/dist/index.js --engine-state /private/state`.
The installer supplies these in full mode. Restarting revokes tokens/download links.

## Development

```sh
uv sync --frozen
npm ci --ignore-scripts
uv run python scripts/patch_engine.py
uv run ruff check src tests scripts
uv run pytest
# Build worker first; these tests really execute Docker and local tools in temporary folders:
LWMCP_DOCKER_TESTS=1 uv run pytest
# Also exercise existing Chrome for PDF (optional):
LWMCP_PDF_TESTS=1 uv run pytest tests/test_engine.py
```

`npm audit --omit=dev` and `uv run pip-audit --skip-editable` check dependencies.
The upstream version, integrity lock and explicit source-hash-checked privacy patches are committed.
Sharp/uuid overrides fix known upstream dependency advisories; see [third-party notices](../THIRD_PARTY_NOTICES.md).
MIT licensed. No affiliation with OpenAI or Desktop Commander.
