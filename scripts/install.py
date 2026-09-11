#!/usr/bin/env python3
"""Install this checkout and register its server with ChatGPT desktop/Codex."""

import argparse
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--workspace", type=Path)
p.add_argument("--state", type=Path)
p.add_argument("--mode", choices=["documents", "full"], default="documents")
p.add_argument("--skip-worker", action="store_true", help="Skip Docker document support")
p.add_argument("--no-register", action="store_true", help="Install only; do not register with ChatGPT/Codex")
p.add_argument("--client-config", type=Path, help="Override the documented shared config.toml location")
p.add_argument("--server-name", default="local-workspace", help="Name used for a new client entry")
p.add_argument("--interactive", action="store_true", help="Guided installation for double-click launch")
a = p.parse_args()
if a.interactive:
    print("Local Workspace MCP：安裝本機工具並自動加入 ChatGPT/Codex；既有設定會先備份。")
    if a.workspace is None:
        a.workspace = Path(input(f"工作資料夾 [{repo / 'workspace'}]: ").strip() or str(repo / "workspace"))
    if a.state is None:
        a.state = Path(
            input(f"私有設定資料夾 [{repo / '.local/state'}]: ").strip() or str(repo / ".local/state")
        )
    if input("啟用完整電腦工具（可改檔案、執行命令與連網）？[y/N]: ").strip().lower() == "y":
        a.mode = "full"
if a.workspace is None or a.state is None:
    p.error("Supply --workspace and --state, or use --interactive.")
workspace = a.workspace.expanduser().resolve()
state = a.state.expanduser().resolve()
if state.is_relative_to(workspace) or workspace == Path.home() or workspace == Path("/"):
    p.error("Choose a dedicated workspace and separate private state directory.")
for tool in (
    ["uv"] + (["node", "npm", "rg"] if a.mode == "full" else []) + ([] if a.skip_worker else ["docker"])
):
    if not shutil.which(tool):
        p.error(f"Install {tool} first, then rerun. No global tools are installed automatically.")
# Respect this Mac's storage guard when present; never install through an absent mount.
guard_command = shutil.which("ai-storage-guard")
guard = Path(guard_command) if guard_command else None
if guard:
    result = subprocess.run([str(guard)], text=True, capture_output=True)
    if result.returncode or "STATUS=OK" not in result.stdout:
        raise SystemExit("Storage Guard did not report STATUS=OK. Installation stopped.")
for folder in [repo, workspace, state]:
    if str(folder).startswith("/Volumes/") and not Path("/Volumes", folder.parts[2]).is_mount():
        raise SystemExit(f"Volume is not mounted: {folder.parts[2]}")
workspace.mkdir(parents=True, exist_ok=True)
state.mkdir(mode=0o700, parents=True, exist_ok=True)
state.chmod(0o700)
subprocess.run(["uv", "sync", "--frozen", "--no-dev"], cwd=repo, check=True)
if a.mode == "full":
    subprocess.run(["npm", "ci", "--ignore-scripts", "--no-fund", "--no-audit"], cwd=repo, check=True)
    subprocess.run([str(repo / ".venv/bin/python"), str(repo / "scripts/patch_engine.py")], check=True)
if not a.skip_worker:
    subprocess.run(
        ["docker", "build", "-t", "local-workspace-mcp-worker:0.1.0", "worker"], cwd=repo, check=True
    )
command = [str(repo / ".venv/bin/local-workspace-mcp"), "serve", "--root", str(workspace), "--write"]
if not a.skip_worker:
    command += ["--python"]
if a.mode == "full":
    command += [
        "--host-engine",
        str(repo / "node_modules/@wonderwhy-er/desktop-commander/dist/index.js"),
        "--engine-state",
        str(state / "engine"),
    ]
launch = state / "launch.sh"
fragment = state / "mcp-server.json"
for target in (launch, fragment):
    if target.exists():
        import time

        shutil.copy2(target, target.with_name(target.name + f".backup-{time.time_ns()}"))
launch.write_text(
    "#!/bin/sh\nset -eu\n"
    + (f"{shlex.quote(str(guard))} >/dev/null\n" if guard else "")
    + f"export PATH={shlex.quote(os.environ['PATH'])}\n"
    + "exec "
    + shlex.join(command)
    + ' "$@"\n'
)
launch.chmod(0o700)
fragment.write_text(
    json.dumps({"mcpServers": {"local-workspace": {"command": str(launch), "args": []}}}, indent=2) + "\n"
)
fragment.chmod(0o600)
if not a.no_register:
    registration = [
        str(repo / ".venv/bin/python"),
        "-m",
        "local_workspace_mcp.client_setup",
        "--launch",
        str(launch),
        "--server-name",
        a.server_name,
        "--receipt",
        str(state / "client-registration.json"),
    ]
    if a.client_config:
        registration += ["--config", str(a.client_config.expanduser().resolve())]
    subprocess.run(registration, check=True)
print(f"Installed. STDIO command: {launch}\nClient configuration fragment: {fragment}")
print(
    "Other client settings were preserved. FULL mode has user-account permissions."
    if a.mode == "full"
    else "Document mode runs Python inside Docker with read-only inputs."
)
