import argparse
import os
import re
import secrets
import signal
import stat
from pathlib import Path

import uvicorn

from .devices import Devices
from .engine import HostEngine
from .server import create_server, http_app


def read_key(path: Path, root: Path) -> str:
    resolved = path.resolve(strict=True)
    if resolved.is_relative_to(root.resolve(strict=True)):
        raise ValueError("Owner key must be OUTSIDE the shared workspace.")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_nlink != 1:
            raise ValueError("Owner key must be a regular, single-link file with permissions 0600.")
        value = os.read(fd, 256).decode().strip()
    finally:
        os.close(fd)
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", value):
        raise ValueError("Invalid owner key. Generate one with init-key.")
    return value


def main():
    parser = argparse.ArgumentParser(description="Self-hosted workspace tools for ChatGPT and MCP clients")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init-key", help="Generate a private owner key; never put it inside the workspace")
    init.add_argument("path", type=Path)
    serve = sub.add_parser("serve")
    serve.add_argument(
        "--root", type=Path, required=True, help="Dedicated input workspace, not your home folder"
    )
    serve.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    serve.add_argument("--public-url", help="HTTPS origin, e.g. https://mcp.example.com (HTTP mode)")
    serve.add_argument("--key-file", type=Path, help="Owner key file OUTSIDE --root (HTTP mode)")
    serve.add_argument("--write", action="store_true", help="Allow creation of new text files/directories")
    serve.add_argument(
        "--python", action="store_true", help="Allow Docker Python jobs to modify exports; needs --write"
    )
    serve.add_argument("--python-image", default="local-workspace-mcp-worker:0.1.0")
    serve.add_argument(
        "--host-engine", type=Path, help="Opt in to FULL user-account access: patched engine dist/index.js"
    )
    serve.add_argument("--engine-state", type=Path, help="Private engine state directory outside --root")
    serve.add_argument("--devices", type=Path, help="Private 0600 owner-configured named SSH/stdio peers")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument(
        "--redirect-host", action="append", help="Exact HTTPS OAuth callback hostname; repeatable"
    )
    args = parser.parse_args()
    try:
        if args.command == "init-key":
            fd = os.open(args.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as stream:
                stream.write(secrets.token_urlsafe(32) + "\n")
            print("Owner key created. Keep it private; enter it only on your own server's consent page.")
            return
        if args.python and not args.write:
            parser.error("--python requires --write")
        if args.transport == "http" and (not args.public_url or not args.key_file):
            parser.error("HTTP requires --public-url and --key-file. Anonymous HTTP is not supported.")
        if not 1 <= args.port <= 65535:
            parser.error("Invalid port")
        if args.host_engine and not args.engine_state:
            parser.error("--host-engine requires --engine-state")
        engine = HostEngine(args.host_engine, args.engine_state, args.root) if args.host_engine else None
        base = args.public_url.rstrip("/") if args.transport == "http" else None
        key = read_key(args.key_file, args.root) if base else None
        mcp, workspace, provider = create_server(
            args.root,
            writable=args.write,
            host_engine=engine,
            devices=Devices(args.devices, args.root),
            shutdown=lambda: os.kill(os.getpid(), signal.SIGTERM),
            base_url=base,
            owner_secret=key,
            python_image=args.python_image if args.python else None,
            redirect_hosts=tuple(args.redirect_host or ["chatgpt.com", "chat.openai.com"]),
        )
        try:
            if base:
                # Bind only loopback; user's HTTPS reverse proxy/tunnel forwards to this port.
                # Disable access logs: query strings and artifact paths contain capabilities.
                uvicorn.run(
                    http_app(mcp, base, provider),
                    host="127.0.0.1",
                    port=args.port,
                    access_log=False,
                    proxy_headers=False,
                    log_level="warning",
                )
            else:
                mcp.run(transport="stdio")
        finally:
            workspace.close()
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Configuration error: {exc}\n")


if __name__ == "__main__":
    main()
