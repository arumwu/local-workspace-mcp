import runpy
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("extra,registered", [([], False), (["--no-register"], False),
                                             (["--register-local-client"], True)])
def test_chatgpt_install_does_not_register_local_client_by_default(tmp_path, monkeypatch, extra, registered):
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("subprocess.run", run)
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/true" if name == "uv" else None)
    monkeypatch.setattr(sys, "argv", ["install.py", "--workspace", str(tmp_path / "files"),
                                     "--state", str(tmp_path / "state"), "--skip-worker", *extra])
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/install.py"), run_name="__main__")
    assert any("local_workspace_mcp.client_setup" in call for call in calls) is registered
    assert (tmp_path / "state/launch.sh").is_file()
