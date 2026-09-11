import json
import os
import re
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    not (ROOT / "node_modules").exists(), reason="Run npm ci and patch_engine first"
)


async def test_real_stdio_engine_and_devices(tmp_path):
    root = tmp_path / "files"
    root.mkdir()
    peer_root = tmp_path / "peer"
    peer_root.mkdir()
    (peer_root / "identity.txt").write_text("second machine")
    peers = tmp_path / "devices.json"
    python = str(ROOT / ".venv/bin/python")
    peers.write_text(
        json.dumps(
            {
                "second": {
                    "command": python,
                    "args": ["-m", "local_workspace_mcp.cli", "serve", "--root", str(peer_root)],
                }
            }
        )
    )
    peers.chmod(0o600)
    args = [
        "-m",
        "local_workspace_mcp.cli",
        "serve",
        "--root",
        str(root),
        "--write",
        "--host-engine",
        str(ROOT / "node_modules/@wonderwhy-er/desktop-commander/dist/index.js"),
        "--engine-state",
        str(tmp_path / "state"),
        "--devices",
        str(peers),
    ]
    async with stdio_client(StdioServerParameters(command=python, args=args)) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            assert len([t for t in tools if t.name.startswith("host_")]) == 25

            async def call(name, **args):
                result = await session.call_tool(name, args)
                assert not result.isError, result
                return "\n".join(c.text for c in result.content if c.type == "text")

            a = str(root / "a.txt")
            await call("host_write_file", path=a, content="hello needle")
            await call("host_edit_block", file_path=a, old_string="hello", new_string="hi")
            assert "hi needle" in await call("host_read_multiple_files", paths=[a])
            await call("host_get_file_info", path=a)
            await call("host_move_file", source=a, destination=str(root / "b.txt"))
            await call("host_create_directory", path=str(root / "folder"))
            await call("host_list_directory", path=str(root))
            search = await call("host_start_search", path=str(root), pattern="needle", searchType="content")
            match = re.search(r"search_\S+", search)
            assert match, search
            search_id = match.group().rstrip('" ,')
            await call("host_get_more_search_results", sessionId=search_id)
            await call("host_list_searches")
            await call("host_stop_search", sessionId=search_id)
            started = await call("host_start_process", command="cat", timeout_ms=100)
            pid = int(re.search(r"PID[: ]+(\d+)", started, re.I).group(1))
            try:
                reply = await call("host_interact_with_process", pid=pid, input="ping\n", timeout_ms=1000)
                reply += await call("host_read_process_output", pid=pid, timeout_ms=1000)
                assert "ping" in reply
                await call("host_list_sessions")
            finally:
                await call("host_force_terminate", pid=pid)
            # Only terminate a process created by this test.
            started = await call("host_start_process", command="sleep 30", timeout_ms=100)
            pid = int(re.search(r"PID[: ]+(\d+)", started, re.I).group(1))
            try:
                assert str(pid) in await call("host_list_processes")
            finally:
                await call("host_kill_process", pid=pid)
            await call("host_get_config")
            await call("host_set_config_value", key="fileReadLineLimit", value=500)
            await call("host_get_usage_stats")
            recent = await call("host_get_recent_tool_calls")
            assert "hello needle" not in recent
            assert "second" in await call("list_paired_devices")
            await call("ping_device", device="second")
            assert "read_text" in await call("list_device_tools", device="second")
            assert "second machine" in await call(
                "call_device_tool", device="second", tool="read_text", arguments={"path": "identity.txt"}
            )
            await call("current_user_info")
            await call("submit_feedback", message="local feedback test")
            await call("get_prompt_library")
            await call("host_get_prompts", action="get_prompt", promptId="onb2_02")
            if os.environ.get("LWMCP_PDF_TESTS"):
                pdf = str(root / "sample.pdf")
                await call("host_write_pdf", path=pdf, content="# Local PDF\n\nVerified text.")
                assert (root / "sample.pdf").read_bytes().startswith(b"%PDF")
                assert "Verified text" in await call("host_read_file", path=pdf)
                await call(
                    "host_write_pdf",
                    path=pdf,
                    content=[{"type": "insert", "pageIndex": 1, "markdown": "# Second page"}],
                )
                assert "Second page" in await call("host_read_file", path=pdf)

    assert (root / "b.txt").read_text() == "hi needle"
    assert not (tmp_path / "state/browser-cache").exists()
