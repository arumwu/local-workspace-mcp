#!/usr/bin/env python3
"""Interactive Windows/WSL document installer; all credentials stay in Linux."""

import argparse
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
PAYLOAD = ('src', 'scripts', 'worker', 'docs', 'tests', 'pyproject.toml', 'uv.lock',
           'package.json', 'package-lock.json', 'README.md', 'LICENSE',
           'THIRD_PARTY_NOTICES.md')


def run(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, **kwargs)


def private_state(path):
    path = path.expanduser().absolute()
    if path.is_symlink() or str(path.resolve()).startswith('/mnt/'):
        raise ValueError('Private state must be on the Linux filesystem, not /mnt or a symlink.')
    if path.exists() and path.stat().st_mode & 0o077:
        raise ValueError('Existing private state must have mode 0700; permissions were not changed.')
    return path


def existing_install(state):
    """Read only the installer's exec line, never shell-evaluate a launcher."""
    launch = state / 'launch.sh'
    if not launch.exists():
        return None
    for line in launch.read_text().splitlines():
        if line.startswith('exec '):
            args = shlex.split(line)
            if '--host-engine' in args:
                raise ValueError('Existing full-mode install: refusing to replace it with document mode.')
            if '--root' in args and 'serve' in args:
                return {'workspace': args[args.index('--root') + 1]}
    raise ValueError('Unrecognized existing launcher; no changes made.')


def payload_files(source):
    for name in PAYLOAD:
        entry = source / name
        if not entry.exists():
            raise ValueError(f'Missing release file: {name}')
        if entry.is_symlink():
            raise ValueError('Release payload must not contain symlinks.')
        for item in sorted(entry.rglob('*')) if entry.is_dir() else [entry]:
            if item.is_symlink():
                raise ValueError('Release payload must not contain symlinks.')
            if '__pycache__' not in item.parts and item.is_file():
                yield item


def stage_release(source, state):
    files = list(payload_files(source))
    digest = hashlib.sha256()
    for file in files:
        digest.update(file.relative_to(source).as_posix().encode() + b'\0')
        digest.update(file.read_bytes())
    target = state / 'releases' / digest.hexdigest()[:20]
    if not target.exists():
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=target.parent) as scratch:
            for file in files:
                dest = Path(scratch) / file.relative_to(source)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(file, dest)
            Path(scratch).rename(target)
    return target


def ensure_dependencies(install=False):
    missing = [x for x in ('curl', 'docker') if not shutil.which(x)]
    uv = shutil.which('uv')
    managed_uv = Path.home() / '.local/share/local-workspace-installer/uv/bin/uv'
    if not uv and managed_uv.exists():
        uv = str(managed_uv)
    if not install:
        return missing + ([] if uv else ['uv'])
    sudo = [] if os.geteuid() == 0 else ['sudo']
    if missing or not uv:
        if not shutil.which('apt-get'):
            raise ValueError('Automatic dependencies require Ubuntu/Debian apt-get.')
        run(sudo + ['apt-get', 'update'])
        packages = ['python3-venv', 'ca-certificates']
        if 'curl' in missing:
            packages.append('curl')
        if 'docker' in missing:
            packages.append('docker.io')
        run(sudo + ['apt-get', 'install', '-y'] + packages)
    if not uv:
        run([sys.executable, '-m', 'venv', managed_uv.parent.parent])
        run([managed_uv.parent / 'python', '-m', 'pip', 'install', 'uv'])
        uv = str(managed_uv)
    os.environ['PATH'] = str(Path(uv).parent) + os.pathsep + os.environ['PATH']


def ensure_docker(start=False):
    result = subprocess.run(['docker', 'info'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode and start and shutil.which('systemctl'):
        service = subprocess.run(['systemctl', 'cat', 'docker.service'], capture_output=True)
        if service.returncode == 0:
            run(([] if os.geteuid() == 0 else ['sudo']) + ['systemctl', 'start', 'docker.service'])
            result = subprocess.run(['docker', 'info'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode:
        raise ValueError('Docker is unavailable to this Linux user. Start Docker Desktop with WSL '
                         'integration or configure Docker in Ubuntu. No group membership was changed.')


def install_client(state, runtime=False):
    """Download official architecture-specific release and verify GitHub's digest."""
    arch = {'x86_64': 'amd64', 'aarch64': 'arm64'}.get(platform.machine())
    if not arch:
        raise ValueError('Unsupported Linux architecture.')
    request = urllib.request.Request('https://api.github.com/repos/openai/tunnel-client/releases/latest',
                                     headers={'User-Agent': 'local-workspace-wsl-installer'})
    with urllib.request.urlopen(request, timeout=30) as response:
        release = json.load(response)
    package = 'tunnel-client-runtime' if runtime else 'tunnel-client'
    executable = 'tunnel-client-runtime' if runtime else 'tunnel-client'
    name = f'{package}-{release["tag_name"]}-linux-{arch}.zip'
    asset = next(x for x in release['assets'] if x['name'] == name)
    url = asset['browser_download_url']
    if not url.startswith('https://github.com/openai/tunnel-client/releases/download/'):
        raise ValueError('Unexpected release download URL.')
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    if asset.get('digest') != 'sha256:' + hashlib.sha256(data).hexdigest():
        raise ValueError('Official release SHA256 did not match; nothing executed.')
    target = state / 'clients' / hashlib.sha256(data).hexdigest()[:20]
    target.mkdir(parents=True, exist_ok=True, mode=0o700)
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = (executable, 'LICENSE', 'NOTICE')
        if not runtime:
            members += ('cloudflared', 'cloudflared-manifest.json')
        for member in members:
            (target / member).write_bytes(archive.read(member))
        for member in (executable,) if runtime else (executable, 'cloudflared'):
            (target / member).chmod(0o700)
    return target / executable


def install(state, workspace, source=SOURCE):
    old = existing_install(state)
    if old and workspace and Path(old['workspace']).resolve() != workspace.resolve():
        raise ValueError('Existing workspace differs; refusing to migrate data or change the workspace.')
    workspace = Path(old['workspace']) if old else workspace or Path.home() / 'LocalWorkspace'
    if state.resolve().is_relative_to(workspace.resolve()):
        raise ValueError('Private state must be outside the workspace.')
    print(f'Document mode only. Workspace: {workspace}\nPrivate state: {state}')
    print('Existing keys, tunnel profiles and document files will be preserved. '
          'Missing Ubuntu dependencies may require sudo. A new release directory will be created.')
    if input('Install/update/repair now? [y/N]: ').strip().lower() != 'y':
        return
    ensure_dependencies(install=True)
    ensure_docker(start=True)
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = stage_release(source, state)
    # The installer can regenerate launch.sh; preserve the prior launcher on failure.
    snapshots = {name: (state / name).read_bytes() if (state / name).exists() else None
                 for name in ('launch.sh', 'mcp-server.json')}
    try:
        run([sys.executable, target / 'scripts/install.py', '--workspace', workspace,
             '--state', state, '--mode', 'documents', '--no-register'])
        receipt = state / 'windows-install.json'
        fd, temp = tempfile.mkstemp(dir=state)
        with os.fdopen(fd, 'w') as stream:
            json.dump({'repo': str(target), 'workspace': str(workspace)}, stream)
        os.replace(temp, receipt)
    except Exception:
        for name, content in snapshots.items():
            path = state / name
            if content is not None:
                path.write_bytes(content)
                path.chmod(0o700 if name == 'launch.sh' else 0o600)
            elif path.exists():
                path.unlink()
        raise
    print('Installed. Run Connect-ChatGPT-Windows.cmd once, then Start-Windows.cmd for daily use.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'connect', 'start', 'check'])
    parser.add_argument('--state', type=Path, default=Path.home() / '.local/state/local-workspace-mcp')
    parser.add_argument('--workspace', type=Path)
    args = parser.parse_args(argv)
    try:
        if 'microsoft' not in platform.release().lower():
            raise ValueError('This entry point requires WSL2. Use the Linux/macOS installer elsewhere.')
        state = private_state(args.state)
        if args.action == 'check':
            print(json.dumps({'missing_dependencies': ensure_dependencies(),
                              'existing_install': existing_install(state), 'state': str(state)}))
            return 0
        if args.action == 'install':
            install(state, args.workspace)
            return 0
        receipt = state / 'windows-install.json'
        repo = Path(json.loads(receipt.read_text())['repo']) if receipt.exists() else SOURCE
        ensure_docker(start=True)
        if args.action == 'connect':
            connection = state / 'connection.json'
            client = (Path(json.loads(connection.read_text())['tunnel_client']) if connection.exists()
                      else install_client(state))
            saved = json.loads(connection.read_text()) if connection.exists() else {}
            runtime = Path(saved['runtime_client']) if saved.get('runtime_client') else install_client(
                state, runtime=True)
            run([repo / '.venv/bin/python', repo / 'scripts/connect_chatgpt.py', '--interactive',
                 '--state', state, '--tunnel-client', client, '--runtime-client', runtime])
        else:
            connection = json.loads((state / 'connection.json').read_text())
            if not connection.get('runtime_client'):
                raise ValueError('Run Connect-ChatGPT-Windows.cmd to select the official runtime first.')
            version = run([connection['runtime_client'], '--version'], capture_output=True, text=True)
            if 'flavor=runtime' not in version.stdout.split():
                raise ValueError('The saved executable is not the official runtime flavor.')
            run([connection['runtime_client'], 'run', '--config',
                 state / 'tunnel-profiles/local-workspace.yaml'])
        return 0
    except (OSError, ValueError, KeyError, StopIteration, EOFError,
            subprocess.CalledProcessError) as error:
        print(f'Windows/WSL setup stopped: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
