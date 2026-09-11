"""Owner-configured SSH/stdio pairing. No discovery service, hosted account, or stored passwords."""

import asyncio
import getpass
import json
import os
import platform
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class Devices:
    def __init__(self, path: Path | None, root: Path):
        self.entries = {}
        self.sessions = {}
        self.stack = None
        self.lock = asyncio.Lock()
        if path:
            path = path.resolve(strict=True)
            if path.is_relative_to(root.resolve()):
                raise ValueError("Device configuration must be outside the shared workspace.")
            if path.stat().st_mode & 0o077:
                raise ValueError("Device configuration requires permissions 0600.")
            entries = json.loads(path.read_text())
            if not isinstance(entries, dict) or len(entries) > 16:
                raise ValueError("Expected an object containing up to 16 named devices.")
            for name, entry in entries.items():
                if not isinstance(name, str) or not isinstance(entry, dict):
                    raise ValueError("Invalid device entry.")
                command = entry.get("command")
                args = entry.get("args", [])
                if (
                    not isinstance(command, str)
                    or not isinstance(args, list)
                    or not all(isinstance(a, str) for a in args)
                ):
                    raise ValueError("Device command and args must be strings.")
            self.entries = entries

    @asynccontextmanager
    async def lifespan(self, _server):
        async with AsyncExitStack() as stack:
            self.stack = stack
            try:
                yield {}
            finally:
                self.sessions.clear()
                self.stack = None

    @asynccontextmanager
    async def connect(self, name):
        # A dedicated task owns each anyio context; request tasks must not enter/exit them.
        if name not in self.entries:
            raise ValueError("Unknown device. Pair it in the private owner configuration first.")
        async with self.lock:
            if name not in self.sessions:
                ready = asyncio.Future()
                stop = asyncio.Event()

                async def worker():
                    entry = self.entries[name]
                    try:
                        async with stdio_client(
                            StdioServerParameters(command=entry["command"], args=entry.get("args", []))
                        ) as streams:
                            async with ClientSession(*streams) as session:
                                await session.initialize()
                                ready.set_result(session)
                                await stop.wait()
                    except BaseException as exc:
                        if not ready.done():
                            ready.set_exception(exc)
                        elif not isinstance(exc, asyncio.CancelledError):
                            self.sessions.pop(name, None)

                task = asyncio.create_task(worker())

                async def close():
                    stop.set()
                    await task

                if self.stack is None:
                    raise ValueError("Device manager is not running.")
                self.stack.push_async_callback(close)
                session = await ready
                self.sessions[name] = session
        yield self.sessions[name]

    def attach(self, mcp, shutdown=None):
        from mcp.types import ToolAnnotations

        read = ToolAnnotations(readOnlyHint=True, destructiveHint=False)

        @mcp.tool(annotations=read)
        def list_paired_devices() -> dict:
            """List local and owner-configured devices by name; never disclose SSH credentials."""
            return {"local": platform.node(), "paired": list(self.entries)}

        @mcp.tool(annotations=read)
        def current_user_info() -> dict:
            """Local OS identity. This project has no hosted subscription or vendor account."""
            return {"user": getpass.getuser(), "device": platform.node(), "platform": platform.system()}

        @mcp.tool(annotations=read)
        async def ping_device(device: str = "local") -> dict:
            """Check local availability or establish an authenticated configured SSH MCP session."""
            if device != "local":
                async with self.connect(device) as session:
                    await session.send_ping()
            return {"device": device, "reachable": True}

        @mcp.tool(annotations=read)
        async def list_device_tools(device: str) -> list[dict]:
            """Read the actual tool schemas of a named paired device."""
            async with self.connect(device) as session:
                result = await session.list_tools()
                return [t.model_dump(exclude_none=True) for t in result.tools]

        @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True))
        async def call_device_tool(device: str, tool: str, arguments: dict) -> dict:
            """Execute a tool on a named paired device. Inspect list_device_tools first.

            This can change files, run commands, or stop processes with the remote user's permissions.
            """
            if tool in {"call_device_tool", "list_device_tools"}:
                raise ValueError("Recursive device routing is not supported.")
            async with self.connect(device) as session:
                result = await session.call_tool(tool, arguments)
                return result.model_dump(exclude_none=True)

        if shutdown:

            @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
            async def shutdown_device_agent() -> dict:
                """Stop ONLY this MCP agent process. It does not shut down the computer.

                An SSH-launched on-demand agent may start again on the next connection.
                """
                import asyncio

                asyncio.get_running_loop().call_later(1, shutdown)
                return {"stopping": True, "pid": os.getpid()}
