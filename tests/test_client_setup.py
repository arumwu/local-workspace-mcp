from pathlib import Path

import pytest
import tomlkit

from local_workspace_mcp.client_setup import register_client


@pytest.fixture
def launcher(tmp_path):
    p = tmp_path / "private state" / "launch.sh"
    p.parent.mkdir()
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o700)
    return p


def test_registration_preserves_comments_settings_and_backup(tmp_path, launcher):
    config = tmp_path / "config.toml"
    original = '# keep my comment\nmodel = "existing-model"\n[mcp_servers.other]\ncommand = "other-server"\n'
    config.write_text(original)
    result = register_client(launcher, config)
    assert result["changed"]
    assert Path(result["backup"]).read_text() == original
    assert Path(result["backup"]).stat().st_mode & 0o077 == 0
    text = config.read_text()
    assert "# keep my comment" in text
    data = tomlkit.parse(text)
    assert data["model"] == "existing-model"
    assert data["mcp_servers"]["other"]["command"] == "other-server"
    assert data["mcp_servers"]["local-workspace"]["command"] == str(launcher)
    assert not register_client(launcher, config)["changed"]
    assert config.read_text() == text


def test_existing_custom_name_is_preserved(tmp_path, launcher):
    config = tmp_path / "config.toml"
    document = {
        "mcp_servers": {
            "my_name": {"command": str(launcher), "args": ["--devices", "/private/peers"], "enabled": False}
        }
    }
    config.write_text(tomlkit.dumps(document))
    original = config.read_bytes()
    result = register_client(launcher, config)
    assert result["server_name"] == "my_name"
    assert result["enabled"] is False
    assert config.read_bytes() == original


def test_conflict_and_malformed_config_remain_untouched(tmp_path, launcher):
    config = tmp_path / "config.toml"
    for content in ["not = [valid", '[mcp_servers.local-workspace]\ncommand="different"\n']:
        config.write_text(content)
        with pytest.raises(ValueError):
            register_client(launcher, config)
        assert config.read_text() == content


def test_new_config_and_intentional_symlink(tmp_path, launcher):
    real = tmp_path / "external/config.toml"
    link = tmp_path / "config.toml"
    real.parent.mkdir()
    real.write_text("# external settings\n")
    link.symlink_to(real)
    register_client(launcher, link)
    assert link.is_symlink()
    assert "local-workspace" in real.read_text()
    new = tmp_path / "fresh/config.toml"
    result = register_client(launcher, new)
    assert result["changed"] and result["backup"] is None
    assert new.stat().st_mode & 0o077 == 0


def test_inline_table_is_extended_without_losing_other_server(tmp_path, launcher):
    config = tmp_path / "inline.toml"
    config.write_text('mcp_servers = {other = {command = "other"}} # preserve inline comment\n')
    register_client(launcher, config)
    document = tomlkit.parse(config.read_text())
    assert document["mcp_servers"]["other"]["command"] == "other"
    assert document["mcp_servers"]["local-workspace"]["command"] == str(launcher)
    assert "# preserve inline comment" in config.read_text()
