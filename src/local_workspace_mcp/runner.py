"""Run untrusted Python ONLY inside a disposable, network-disabled Docker container."""

import asyncio
import os
import secrets
from pathlib import Path

MAX_CODE = 65_536
MAX_OUTPUT = 65_536


class PythonRunner:
    def __init__(self, root: Path, image: str):
        self.root = root.resolve(strict=True)
        if "," in str(self.root):
            raise ValueError("Docker workspace path must not contain commas.")
        self.output = self.root / "exports"
        self.output.mkdir(mode=0o700, exist_ok=True)
        if self.output.is_symlink() or not self.output.is_dir():
            raise ValueError("exports must be a real directory, not a symlink.")
        self.image = image
        self.lock = asyncio.Lock()

    async def run(self, code: str) -> dict:
        if len(code.encode()) > MAX_CODE:
            raise ValueError("Python code exceeds 64 KiB.")
        if self.lock.locked():
            raise ValueError("A Python job is already running. Try again after it completes.")
        async with self.lock:
            # Never create a missing workspace after a removable volume disconnects.
            if not self.root.is_dir() or self.output.is_symlink() or not self.output.is_dir():
                raise ValueError("Workspace or exports directory is unavailable.")
            name = "lwmcp-" + secrets.token_hex(12)
            args = [
                "docker",
                "run",
                "--rm",
                "--pull=never",
                "--name",
                name,
                "-i",
                "--network=none",
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--pids-limit=64",
                "--memory=512m",
                "--cpus=1",
                "--user",
                f"{os.getuid()}:{os.getgid()}",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=64m",
                "--env",
                "MPLCONFIGDIR=/tmp/matplotlib",
                "--env",
                "XDG_CACHE_HOME=/tmp/cache",
                "--mount",
                f"type=bind,src={self.root},dst=/workspace,readonly",
                "--mount",
                f"type=bind,src={self.output},dst=/output",
                "--workdir=/output",
                self.image,
                "python",
                "-",
            ]
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            async def read_bounded(stream):
                data = bytearray()
                while chunk := await stream.read(8192):
                    data.extend(chunk)
                    if len(data) > MAX_OUTPUT:
                        raise ValueError("Python output exceeded 64 KiB; job stopped.")
                return data.decode("utf-8", errors="replace")

            async def exchange():
                proc.stdin.write(code.encode())
                await proc.stdin.drain()
                proc.stdin.close()
                readers = [
                    asyncio.create_task(read_bounded(proc.stdout)),
                    asyncio.create_task(read_bounded(proc.stderr)),
                ]
                try:
                    stdout, stderr = await asyncio.gather(*readers)
                    return {
                        "exit_code": await proc.wait(),
                        "stdout": stdout,
                        "stderr": stderr,
                        "output_directory": "exports",
                    }
                finally:
                    for task in readers:
                        task.cancel()
                    await asyncio.gather(*readers, return_exceptions=True)

            try:
                async with asyncio.timeout(90):
                    return await exchange()
            except TimeoutError:
                raise ValueError("Python job exceeded 90 seconds; container stopped.") from None
            finally:
                # docker CLI exit/timeout is not proof that its container stopped.
                cleanup = await asyncio.create_subprocess_exec(
                    "docker",
                    "rm",
                    "-f",
                    name,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                try:
                    await asyncio.wait_for(cleanup.wait(), 10)
                except TimeoutError:
                    cleanup.kill()
                    await cleanup.wait()
                if proc.returncode is None:
                    proc.kill()
                await proc.wait()
