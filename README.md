# Local Workspace MCP

Self-hosted local file, terminal, document, and named-device tools for MCP clients.
**Early alpha: protocol tests pass; actual ChatGPT desktop/web acceptance is still pending.**
This does not unlock ChatGPT Work, add AI credits, or guarantee that every ChatGPT mode supports local MCP.

[繁體中文](docs/README.zh-TW.md) · [Connections](docs/CONNECT.md) · [Feature coverage](docs/FEATURES.md) · [Validation](docs/VALIDATION.md) · [Security](SECURITY.md)

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
no browser is downloaded automatically. Native Windows and WSL are not validated.

```sh
git clone https://github.com/arumwu/local-workspace-mcp.git
cd local-workspace-mcp
./Install.command --workspace /absolute/path/task-files \
  --state /absolute/path/private-state --mode full
```

Choose existing storage appropriate to your computer. Keep private state outside the workspace.
Use `--mode documents` for isolated document work, or `--skip-worker` when Docker is not needed.
The installer installs only checkout-local dependencies and builds the worker. It backs up its own
launcher/config fragment before replacing them and does not modify any MCP client settings.
This is a source installer, **not a signed macOS app/pkg**. Missing prerequisites are reported, not auto-installed.

Add the generated `private-state/launch.sh` as a **STDIO command** in a compatible local MCP client.
The generated `mcp-server.json` is a configuration fragment, not a file to overwrite existing settings with.
No listening port, public URL, or API key is required for this local transport.
ChatGPT web cannot directly contact `127.0.0.1`; see [connection options and account limits](docs/CONNECT.md).

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
Sharp/uuid overrides fix known upstream dependency advisories; see [third-party notices](THIRD_PARTY_NOTICES.md).
MIT licensed. No affiliation with OpenAI or Desktop Commander.
