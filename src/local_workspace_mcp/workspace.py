"""Descriptor-relative filesystem access for POSIX. Never follows symlinks."""

import os
import stat
from contextlib import contextmanager
from pathlib import Path

MAX_BYTES = 1_048_576
MAX_ENTRIES = 500
TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".tsv", ".json", ".yaml", ".yml", ".toml"}


class Workspace:
    def __init__(self, root: Path, writable: bool = False):
        if os.name != "posix":
            raise ValueError("Use Linux Docker on Windows; native Windows is not supported.")
        root = root.resolve(strict=True)
        if root in (Path(root.anchor), Path.home().resolve()):
            raise ValueError("Choose a dedicated folder, not the filesystem root or your home directory.")
        self.fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        self.writable = writable

    def close(self):
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1

    @staticmethod
    def parts(path: str, directory: bool = False) -> list[str]:
        if directory and path in ("", "."):
            return []
        parts = path.split("/")
        if (
            len(path) > 1024
            or len(parts) > 20
            or any(
                not p
                or p.startswith(".")
                or "\\" in p
                or ":" in p
                or len(p.encode()) > 200
                or any(ord(c) < 32 or ord(c) == 127 for c in p)
                for p in parts
            )
        ):
            raise ValueError("Use a relative path without hidden names, traversal, or special characters.")
        return parts

    @contextmanager
    def directory(self, parts: list[str]):
        fd = os.dup(self.fd)
        try:
            for name in parts:
                next_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = next_fd
            yield fd
        finally:
            os.close(fd)

    def list_directory(self, path: str = ".") -> dict:
        entries = []
        with self.directory(self.parts(path, directory=True)) as fd:
            with os.scandir(fd) as iterator:
                # Cap inspected entries too, so huge folders cannot monopolize the process.
                for index, entry in enumerate(iterator):
                    if index >= MAX_ENTRIES:
                        return {"entries": sorted(entries, key=lambda e: e["name"]), "truncated": True}
                    try:
                        self.parts(entry.name)
                        info = entry.stat(follow_symlinks=False)
                        if stat.S_ISDIR(info.st_mode):
                            entries.append({"name": entry.name, "type": "directory"})
                        elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                            if Path(entry.name).suffix.lower() in TEXT_EXTENSIONS:
                                entries.append({"name": entry.name, "type": "file", "bytes": info.st_size})
                    except (ValueError, OSError):
                        continue
        return {"entries": sorted(entries, key=lambda e: e["name"]), "truncated": False}

    def file_parts(self, path: str) -> list[str]:
        parts = self.parts(path)
        if Path(parts[-1]).suffix.lower() not in TEXT_EXTENSIONS:
            raise ValueError("Supported text files: " + ", ".join(sorted(TEXT_EXTENSIONS)))
        return parts

    def read_text(self, path: str) -> str:
        parts = self.file_parts(path)
        with self.directory(parts[:-1]) as parent:
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_BYTES:
                    raise ValueError("Only regular, single-link text files up to 1 MiB can be read.")
                with os.fdopen(fd, "rb", closefd=False) as stream:
                    data = stream.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES or b"\x00" in data:
                    raise ValueError("File is too large or contains binary data.")
                return data.decode("utf-8")
            finally:
                os.close(fd)

    def create_text(self, path: str, content: str) -> dict:
        if not self.writable:
            raise PermissionError("Writes are disabled. Restart with --write to allow creation.")
        parts = self.file_parts(path)
        data = content.encode("utf-8")
        if len(data) > MAX_BYTES or b"\x00" in data:
            raise ValueError("Text must be UTF-8, without NUL, and at most 1 MiB.")
        with self.directory(parts[:-1]) as parent:
            # O_EXCL refuses existing files, symlinks, and concurrent duplicate writes.
            fd = os.open(
                parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent
            )
            try:
                with os.fdopen(fd, "wb", closefd=False) as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(fd)
            except BaseException:
                os.unlink(parts[-1], dir_fd=parent)
                raise
            finally:
                os.close(fd)
        return {"path": path, "bytes": len(data), "created": True}

    def create_directory(self, path: str) -> dict:
        if not self.writable:
            raise PermissionError("Writes are disabled.")
        parts = self.parts(path)
        with self.directory(parts[:-1]) as parent:
            os.mkdir(parts[-1], 0o700, dir_fd=parent)
        return {"path": path, "created": True}
