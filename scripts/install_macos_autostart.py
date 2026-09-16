#!/usr/bin/env python3
"""Start an already-configured ChatGPT tunnel at macOS login (explicit opt-in)."""

import argparse
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_NAME = "ChatGPT Local Workspace MCP"


def service_files(binary, config, home, name=DEFAULT_NAME, guard=None):
    """Associate the login item with a named app instead of displaying the interpreter as sh."""
    if not name or any(c in name for c in "/\n\r"):
        raise ValueError("Service name cannot be empty or contain slash/newline.")
    app = Path("/Applications") / f"{name}.app"
    executable = app / "Contents/MacOS/ChatGPT Local Workspace MCP"
    plist = home / "Library/LaunchAgents" / f"{name}.plist"
    info = {
        "CFBundleIdentifier": "org.localworkspace.chatgpt-tunnel",
        "CFBundleName": name,
        "CFBundleDisplayName": name,
        "CFBundleExecutable": executable.name,
        "CFBundlePackageType": "APPL",
        "CFBundleVersion": "1",
        "LSUIElement": True,
    }
    data = {
        "Label": name,
        "Comment": "Local files, documents and Python for ordinary ChatGPT conversations.",
        "AssociatedBundleIdentifiers": [info["CFBundleIdentifier"]],
        "ProgramArguments": [str(executable), str(binary), str(config)] + ([str(guard)] if guard else []),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 30,
        "StandardOutPath": "/dev/null",
        "StandardErrorPath": "/dev/null",
    }
    return app, info, plist, data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tunnel-client", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--name", default=DEFAULT_NAME, help="Human-readable login service name")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error("This helper is for macOS; use your operating system's service manager on Linux.")
    binary = args.tunnel_client.expanduser().resolve(strict=True)
    config = args.config.expanduser().resolve(strict=True)
    if not binary.is_file() or not os.access(binary, os.X_OK) or not config.is_file():
        parser.error("Supply an executable official tunnel-client and an existing private config.")
    guard = shutil.which("ai-storage-guard")
    if guard:
        check = subprocess.run([guard], capture_output=True, text=True, check=True)
        if "STATUS=OK" not in check.stdout:
            parser.error("Storage Guard did not report STATUS=OK.")
    subprocess.run([str(binary), "doctor", "--config", str(config)], check=True)
    app, info, plist, data = service_files(binary, config, Path.home(), args.name, guard)
    for target in (app, plist):
        if target.exists() or target.is_symlink():
            parser.error(f"Already exists: {target}. Stop/review the existing service before replacing it.")
    plist.parent.mkdir(parents=True, exist_ok=True)
    executable = app / "Contents/MacOS" / info["CFBundleExecutable"]
    domain = f"gui/{os.getuid()}"
    try:
        # Build on the configured data volume; delete intermediate files after installation.
        with tempfile.TemporaryDirectory(prefix="launcher-build-", dir=config.parent) as temp:
            compiled = Path(temp) / "launcher"
            subprocess.run([
                "xcrun", "clang", "-Os", "-Wall", "-Wextra",
                str(Path(__file__).with_name("tunnel_launcher.c")), "-o", str(compiled),
            ], check=True)
            executable.parent.mkdir(parents=True)
            shutil.copy2(compiled, executable)
        (app / "Contents/Info.plist").write_bytes(plistlib.dumps(info))
        subprocess.run(["codesign", "--force", "--sign", "-", str(app)], check=True)
        plist.write_bytes(plistlib.dumps(data))
        plist.chmod(0o600)
        subprocess.run(["launchctl", "bootstrap", domain, str(plist)], check=True)
        time.sleep(2)
        status = subprocess.check_output(["launchctl", "print", f"{domain}/{args.name}"], text=True)
        if "state = running" not in status:
            raise RuntimeError("Service did not remain running. Check configuration and disk access.")
    except Exception:
        subprocess.run(["launchctl", "bootout", f"{domain}/{args.name}"], capture_output=True)
        plist.unlink(missing_ok=True)
        if app.exists():
            shutil.rmtree(app)
        raise
    print(f"Login service: {args.name}\nNamed launcher app: {app}\nLaunchAgent: {plist}")
    print("Process started. Verify /readyz and a real ChatGPT tool call before claiming end-to-end success.")


if __name__ == "__main__":
    main()
