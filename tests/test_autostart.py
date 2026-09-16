import importlib.util
import plistlib
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("autostart", ROOT / "scripts/install_macos_autostart.py")
autostart = importlib.util.module_from_spec(spec)
spec.loader.exec_module(autostart)


def test_named_app_and_arguments(tmp_path):
    binary = tmp_path / "external disk/client"
    config = tmp_path / "private ' config.json"
    app, info, plist, data = autostart.service_files(binary, config, tmp_path, "ChatGPT 本機工具")
    decoded = plistlib.loads(plistlib.dumps(data))
    assert app.name == "ChatGPT 本機工具.app"
    assert info["CFBundleDisplayName"] == "ChatGPT 本機工具"
    assert decoded["ProgramArguments"][1:] == [str(binary), str(config)]
    assert decoded["AssociatedBundleIdentifiers"] == [info["CFBundleIdentifier"]]
    assert "/bin/sh" not in decoded["ProgramArguments"]
    assert decoded["KeepAlive"] and decoded["RunAtLoad"]
    assert plist.name == "ChatGPT 本機工具.plist"


@pytest.mark.skipif(not shutil.which("cc"), reason="C compiler required")
def test_launcher_missing_volume_and_exact_arguments(tmp_path):
    compiled = tmp_path / "launcher"
    subprocess.run(["cc", str(ROOT / "scripts/tunnel_launcher.c"), "-o", str(compiled)], check=True)
    binary = tmp_path / "client with spaces"
    marker = tmp_path / "called"
    binary.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "' + str(marker) + '"\n')
    binary.chmod(0o700)
    config = tmp_path / "config with spaces.json"
    assert subprocess.run([str(compiled), str(binary), str(config)]).returncode == 66
    assert not marker.exists()
    config.write_text("{}")
    subprocess.run([str(compiled), str(binary), str(config)], check=True)
    assert marker.read_text().splitlines() == ["run", "--config", str(config)]
    marker.unlink()
    guard = tmp_path / "guard"
    guard.write_text("#!/bin/sh\nexit 1\n")
    guard.chmod(0o700)
    assert subprocess.run([str(compiled), str(binary), str(config), str(guard)]).returncode == 73
    assert not marker.exists()


@pytest.mark.parametrize("name", ["", "bad/name", "bad\nname"])
def test_reject_invalid_service_names(tmp_path, name):
    with pytest.raises(ValueError):
        autostart.service_files(tmp_path / "client", tmp_path / "config", tmp_path, name)
