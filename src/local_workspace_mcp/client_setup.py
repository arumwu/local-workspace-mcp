"""Register a local server in the documented shared ChatGPT/Codex TOML configuration."""

import argparse
import fcntl
import json
import os
import re
import secrets
import stat
import tempfile
import time
from pathlib import Path

import tomlkit


def default_config_path() -> Path:
    # Read the owner's configured location; never change environment variables.
    return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml"


def register_client(launch: Path, config: Path, server_name: str = "local-workspace") -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", server_name):
        raise ValueError("Server name must contain 1-80 letters, digits, underscores or hyphens.")
    launch = launch.resolve(strict=True)
    if not launch.is_file() or not os.access(launch, os.X_OK):
        raise ValueError("The installed launcher must be an executable file.")
    # Follow an intentional config symlink without replacing the symlink itself.
    config = config.expanduser().resolve()
    if str(config).startswith("/Volumes/") and not Path("/Volumes", config.parts[2]).is_mount():
        raise ValueError("The configuration volume is not mounted.")
    config.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = os.open(config.parent / ".local-workspace-mcp.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        existed = config.exists()
        original = config.read_bytes() if existed else b""
        info = config.stat() if existed else None
        if info and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
            raise ValueError("Client configuration must be a regular, single-link file.")
        document = tomlkit.parse(original.decode("utf-8"))
        entries = document.get("mcp_servers", {})
        if not isinstance(entries, dict):
            raise ValueError("mcp_servers must be a TOML table.")
        # A user may already have registered the launcher with a different display name.
        for name, entry in entries.items():
            if isinstance(entry, dict) and entry.get("command") == str(launch):
                return {
                    "changed": False,
                    "server_name": name,
                    "config": str(config),
                    "enabled": entry.get("enabled", True),
                    "backup": None,
                }
        if server_name in entries:
            raise ValueError(
                f"Server '{server_name}' already points elsewhere. Choose --server-name; nothing replaced."
            )
        before = document.unwrap()
        if "mcp_servers" not in document:
            document["mcp_servers"] = tomlkit.table()
        entry = (
            tomlkit.inline_table()
            if isinstance(document["mcp_servers"], tomlkit.items.InlineTable)
            else tomlkit.table()
        )
        entry["command"] = str(launch)
        entry["args"] = []
        entry["enabled"] = True
        document["mcp_servers"][server_name] = entry
        encoded = tomlkit.dumps(document).encode("utf-8")
        # Verify that all other settings survived before touching the original.
        checked = tomlkit.parse(encoded.decode()).unwrap()
        del checked["mcp_servers"][server_name]
        if "mcp_servers" not in before:
            del checked["mcp_servers"]
        if checked != before:
            raise ValueError("Unrelated client settings changed; registration refused.")
        backup = None
        if existed:
            backup = config.with_name(config.name + f".lwmcp-backup-{time.time_ns()}-{secrets.token_hex(3)}")
            with os.fdopen(os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as stream:
                stream.write(original)
                stream.flush()
                os.fsync(stream.fileno())
        fd, temporary = tempfile.mkstemp(prefix=".lwmcp-config-", dir=config.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            if config.exists() != existed or (existed and config.read_bytes() != original):
                raise ValueError("Client configuration changed during setup. Retry after closing settings.")
            os.chmod(temporary, stat.S_IMODE(info.st_mode) if info else 0o600)
            os.replace(temporary, config)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return {
            "changed": True,
            "server_name": server_name,
            "config": str(config),
            "enabled": True,
            "backup": str(backup) if backup else None,
        }
    finally:
        os.close(lock)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=default_config_path())
    parser.add_argument("--server-name", default="local-workspace")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    try:
        result = register_client(args.launch, args.config, args.server_name)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Client registration stopped; existing settings preserved: {exc}\n")
    if args.receipt:
        with os.fdopen(
            os.open(args.receipt, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600), "w"
        ) as f:
            json.dump(result, f, indent=2)
            f.write("\n")
    print(json.dumps(result, ensure_ascii=False))
    if not result["enabled"]:
        print("An existing disabled entry was preserved; enable it in the client when ready.")
    else:
        print("Restart/reload MCP servers in ChatGPT desktop to load the registration. No app was restarted.")


if __name__ == "__main__":
    main()
