import os

import pytest

from local_workspace_mcp.workspace import MAX_BYTES, Workspace


@pytest.fixture
def ws(tmp_path):
    w = Workspace(tmp_path, writable=True)
    yield w
    w.close()


@pytest.mark.parametrize(
    "path",
    [
        "../secret.txt",
        "/etc/passwd",
        "a/../../x.txt",
        ".env",
        "a/.key.txt",
        "a\\b.txt",
        "a//b.txt",
        "x\x00.txt",
        "C:/x.txt",
        "",
        "a/./x.txt",
    ],
)
def test_reject_path(ws, path):
    with pytest.raises(ValueError):
        ws.read_text(path)


def test_create_read_no_overwrite(ws, tmp_path):
    ws.create_directory("reports")
    ws.create_text("reports/test.md", "測試\nHello")
    assert ws.read_text("reports/test.md") == "測試\nHello"
    with pytest.raises(FileExistsError):
        ws.create_text("reports/test.md", "destroy")
    assert (tmp_path / "reports/test.md").read_text() == "測試\nHello"


def test_symlink_and_hardlink(ws, tmp_path):
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret")
    (tmp_path / "link.txt").symlink_to(outside)
    (tmp_path / "escape").symlink_to(tmp_path.parent, target_is_directory=True)
    os.link(outside, tmp_path / "hard.txt")
    for name in ("link.txt", "escape/outside.txt", "hard.txt"):
        with pytest.raises((ValueError, OSError)):
            ws.read_text(name)
    with pytest.raises(OSError):
        ws.create_text("escape/new.txt", "no")
    assert ws.list_directory()["entries"] == []


def test_fifo_binary_large(ws, tmp_path):
    os.mkfifo(tmp_path / "pipe.txt")
    (tmp_path / "binary.txt").write_bytes(b"\x00")
    (tmp_path / "large.txt").write_bytes(b"a" * (MAX_BYTES + 1))
    for name in ("pipe.txt", "binary.txt", "large.txt"):
        with pytest.raises(ValueError):
            ws.read_text(name)


def test_readonly_and_extension(tmp_path):
    ws = Workspace(tmp_path)
    try:
        with pytest.raises(PermissionError):
            ws.create_text("x.txt", "no")
        with pytest.raises(PermissionError):
            ws.create_directory("no")
        with pytest.raises(ValueError):
            ws.read_text("owner.key")
    finally:
        ws.close()
