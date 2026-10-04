import runpy
from pathlib import Path
from unittest.mock import patch

import pytest

MODULE = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/windows_download_wsl.py'))
existing = MODULE['existing_install']
stage = MODULE['stage_release']
install = MODULE['install']


def test_existing_workspace_with_spaces_and_full_mode(tmp_path):
    launch = tmp_path / 'launch.sh'
    launch.write_text("#!/bin/sh\nexec /opt/tool serve --root '/mnt/c/path with spaces' --write\n")
    assert existing(tmp_path)['workspace'] == '/mnt/c/path with spaces'
    launch.write_text('exec /opt/tool serve --root /data --host-engine /engine\n')
    with pytest.raises(ValueError, match='full-mode'):
        existing(tmp_path)


def test_workspace_change_refused_before_install(tmp_path):
    (tmp_path / 'launch.sh').write_text('exec /opt/tool serve --root /existing --write\n')
    with pytest.raises(ValueError, match='differs'):
        install(tmp_path, tmp_path / 'different')


def test_release_copy_excludes_credentials_and_is_repeatable(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    for name in MODULE['PAYLOAD']:
        (source / name).write_text('release data')
    (source / 'runtime-key').write_text('must not copy')
    (source / '.git').mkdir()
    state = tmp_path / 'private'
    first = stage(source, state)
    assert stage(source, state) == first
    assert not (first / 'runtime-key').exists()
    assert not (first / '.git').exists()


def test_failed_update_restores_launch_and_preserves_secrets(tmp_path):
    state = tmp_path / 'private'
    state.mkdir(mode=0o700)
    original = b'exec /old/tool serve --root /existing --write\n'
    (state / 'launch.sh').write_bytes(original)
    (state / 'runtime-key').write_text('private fixture')
    (state / 'connection.json').write_text('existing connection')
    globals_ = install.__globals__

    def failed_run(*args, **kwargs):
        (state / 'launch.sh').write_text('changed launcher')
        raise OSError('simulated installation failure')

    with patch.dict(globals_, {
        'ensure_dependencies': lambda **kw: None,
        'ensure_docker': lambda **kw: None,
        'stage_release': lambda *a: tmp_path / 'release',
        'run': failed_run,
    }), patch('builtins.input', return_value='y'):
        with pytest.raises(OSError):
            install(state, None)
    assert (state / 'launch.sh').read_bytes() == original
    assert (state / 'runtime-key').read_text() == 'private fixture'
    assert (state / 'connection.json').read_text() == 'existing connection'
    assert not (state / 'windows-install.json').exists()


def test_private_state_on_windows_mount_refused():
    with pytest.raises(ValueError, match='Linux filesystem'):
        MODULE['private_state'](Path('/mnt/c/private'))
