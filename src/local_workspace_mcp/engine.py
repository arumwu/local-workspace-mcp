"""Explicit opt-in host integration. This is full user-account access, not a sandbox."""

import json
import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Describe capabilities and effects, without directing the client's tool selection
# or treating upstream prompt text as authority to execute a task.
HOST_DESCRIPTIONS = {
    "start_process": (
        "Start a command or interactive process on the host with the OS user's permissions. "
        "Commands may read, modify or delete files, access the network, or keep running after this call. "
        "Provide command and timeout_ms; shell is optional. Returns process status, PID and initial output. "
        "For a running process, host_interact_with_process sends input "
        "and host_read_process_output reads output. "
        "Use absolute paths for local files. Stop task-owned processes when no longer needed."
    ),
    "interact_with_process": (
        "Send input to an existing host process by PID and return its output. "
        "Input to a shell or REPL executes with the OS user's permissions "
        "and may change files or use the network. "
        "Supports timeout_ms, wait_for_prompt and verbose_timing. "
        "A process can remain running or waiting for more input after the call."
    ),
    "get_prompts": (
        "Retrieve an upstream example workflow by promptId using action='get_prompt'. "
        "Returns reference text; retrieving it does not authorize or execute its suggested operations."
    ),
}


class HostEngine:
    def __init__(self, entry: Path, state: Path, root: Path):
        self.entry = entry.resolve(strict=True)
        self.state = state.resolve()
        self.root = root.resolve(strict=True)
        if self.state.is_relative_to(self.root):
            raise ValueError("Engine state must be outside the shared workspace.")
        self.session = None
        self.tools = {}

    @asynccontextmanager
    async def lifespan(self, _server):
        self.state.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.state, 0o700)
        config = self.state / "config.json"
        if not config.exists():
            config.write_text(json.dumps({"telemetryEnabled": False, "allowedDirectories": [str(self.root)]}))
            config.chmod(0o600)
        if "LWMCP_ENGINE_STATE_DIR" not in (self.entry.parent / "config.js").read_text():
            raise ValueError("Run scripts/patch_engine.py before enabling host tools.")
        env = {k: os.environ[k] for k in ("PATH", "HOME", "SHELL", "LANG", "TMPDIR") if k in os.environ}
        env.update(
            LWMCP_ENGINE_STATE_DIR=str(self.state),
            DESKTOP_COMMANDER_DISABLE_TELEMETRY="1",
            PUPPETEER_CACHE_DIR=str(self.state / "browser-cache"),
        )
        command = shutil.which("node")
        if not command:
            raise ValueError("Node.js is required for host tools.")
        params = StdioServerParameters(
            command=command, args=[str(self.entry), "--no-onboarding"], env=env, cwd=str(self.root)
        )
        async with stdio_client(params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                self.session = session
                result = await session.list_tools()
                self.tools = {
                    f"host_{t.name}": t
                    for t in result.tools
                    if t.name != "give_feedback_to_desktop_commander"
                }
                try:
                    yield {}
                finally:
                    self.session = None

    def attach(self, mcp):
        @mcp.tool()
        def get_prompt_library() -> dict:
            """List the bundled upstream prompt library, including prompt IDs and text."""
            return json.loads((self.entry.parent / "data/onboarding-prompts.json").read_text())

        @mcp.tool()
        def submit_feedback(message: str) -> dict:
            """Save feedback locally for the owner to review. Nothing is sent to any vendor."""
            import secrets

            if not message.strip() or len(message.encode()) > 8192:
                raise ValueError("Feedback must contain 1 to 8192 bytes.")
            folder = self.state / "feedback"
            folder.mkdir(mode=0o700, exist_ok=True)
            name = secrets.token_hex(12) + ".txt"
            fd = os.open(folder / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as stream:
                stream.write(message)
            return {"saved_locally": True, "id": name, "sent": False}

        @mcp._mcp_server.list_tools()
        async def list_tools():
            local = await mcp.list_tools()
            forwarded = []
            for name, tool in self.tools.items():
                # This bridge exposes tools, not the upstream UI resources.
                # Advertising those templates makes ChatGPT fetch missing resources.
                meta = {
                    key: value for key, value in (tool.meta or {}).items()
                    if key not in ("ui", "ui/resourceUri", "openai/outputTemplate", "openai/widgetAccessible")
                }
                forwarded.append(tool.model_copy(update={
                    "name": name,
                    "meta": meta or None,
                    "description": HOST_DESCRIPTIONS.get(tool.name, tool.description),
                }))
            return local + forwarded

        @mcp._mcp_server.call_tool(validate_input=False)
        async def call_tool(name, arguments):
            if name in self.tools:
                return await self.session.call_tool(self.tools[name].name, arguments)
            return await mcp.call_tool(name, arguments)
