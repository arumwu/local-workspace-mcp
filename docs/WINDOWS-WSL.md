# Windows through WSL2 (document mode)

This runs the Linux server inside WSL2; it does **not** add native Windows support.
Keep the repository, Python environment, private state and official Linux
tunnel-client and tunnel-client-runtime in the Linux filesystem. A dedicated
document workspace can live under `/mnt/c/Users/YOUR_WINDOWS_USER/Documents/LocalWorkspace`.

## Download, extract, double-click

1. Extract the source ZIP; do not run files inside the ZIP viewer.
2. Double-click `Install-Windows.cmd`. If WSL/Ubuntu is missing, follow the printed
   `wsl --install -d Ubuntu` instruction in an Administrator terminal, reboot if
   Windows requests it, and open Ubuntu once to create its Linux user. Then rerun.
3. Review the displayed workspace and type `y`. Missing Ubuntu dependencies are
   installed through apt (sudo may ask for your Linux password); uv is installed
   in a dedicated Linux virtual environment through pip. Docker access must work
   for that Linux user. If it does not, the installer stops with instructions;
   it does not silently change group membership or permissions.
4. Run `Connect-ChatGPT-Windows.cmd`. The official architecture-matched Linux
   tunnel-client is downloaded and SHA256-verified when no saved connection exists.
   Create the tunnel/runtime key in your account and enter them at the prompts.
5. Run `Start-Windows.cmd`, keep its window open, and finish the ChatGPT plugin
   connection and real tool test below. Ctrl-C stops that foreground tunnel.

The entry points use Windows PowerShell 5.1 and WSL's Python. They do not require
Python on Windows. The execution policy override applies only to this process;
no machine/user execution policy is changed. Keep the extracted folder for these
shortcuts. Account login, new keys and connector consent remain interactive.
There is no Windows login-autostart task. Do not start a second copy of a tunnel
already running as a service or in another terminal.

### Existing installation / update / repair

Rerun `Install-Windows.cmd` from a newer extracted release. It detects `launch.sh`
in the same Linux user's private state, preserves its workspace, refuses to
replace full host mode, and installs a content-addressed Linux release copy.
Existing keys and tunnel profiles are untouched. The prior launcher is restored
if installation fails; old release directories are retained, not deleted.
Stop your tunnel before updating and start it again afterward.

Default state is the Linux user's `~/.local/state/local-workspace-mcp`; a new
workspace defaults to `~/LocalWorkspace` inside Ubuntu. Windows Explorer can open
it through `\\wsl.localhost\Ubuntu\home\YOUR_LINUX_USER\LocalWorkspace`.
Outputs are in its `exports` folder. To select a Windows workspace or reuse a
different distro/user/state, run from PowerShell:

```powershell
.\Install-Windows.cmd -Distro Ubuntu -LinuxUser YOUR_LINUX_USER -Workspace 'C:\Users\YOU\Documents\LocalWorkspace'
.\Connect-ChatGPT-Windows.cmd -Distro Ubuntu -LinuxUser YOUR_LINUX_USER
.\Start-Windows.cmd -Distro Ubuntu -LinuxUser YOUR_LINUX_USER
# Read-only prerequisite and existing-install inspection:
powershell -NoProfile -File .\scripts\windows_download.ps1 -Action Check -Distro Ubuntu -LinuxUser YOUR_LINUX_USER
```

Pass `-State /absolute/linux/private-state` consistently if using a custom state.
An existing installation owned by root requires `-LinuxUser root`; choosing a
different Linux user selects that user's separate installation. The installer
does not migrate credentials between users. To select an existing state whose
workspace differs from a supplied `-Workspace`, it refuses instead of moving data.

## Prerequisites

- An installed WSL2 Ubuntu distribution (`wsl.exe --list --verbose`).
- Git, Python 3.12+, uv, and a working Docker CLI/daemon inside that distribution.
  Verify `docker info` as the same Linux user that will run MCP. Docker Desktop
  WSL integration and Docker inside WSL are alternatives; choose one working setup.
- Both official Linux v0.0.15 or newer binaries matching `uname -m`: `tunnel-client`
  for setup/diagnostics and `tunnel-client-runtime` for the running connection.
  Download them from https://github.com/openai/tunnel-client/releases and verify
  the archives against that release's SHA256SUMS.txt. Keep both binaries together.
- OpenAI tunnel/workspace access and a key restricted to Tunnels Read + Use.

Use a regular Linux user where possible. The existing installation tested below
was root-owned; other installations do not need to copy that choice. Full host
mode was not tested. This guide does not install WSL or Docker.

## Install and connect

In an interactive Ubuntu terminal, clone the repository into a permanent Linux
directory. From that directory, adapt these absolute paths to your Linux user:

```sh
python3 scripts/install.py \
  --workspace /mnt/c/Users/YOUR_WINDOWS_USER/Documents/LocalWorkspace \
  --state /home/YOUR_LINUX_USER/.local/state/local-workspace-mcp \
  --mode documents

.venv/bin/python scripts/connect_chatgpt.py --interactive --run \
  --state /home/YOUR_LINUX_USER/.local/state/local-workspace-mcp \
  --tunnel-client /home/YOUR_LINUX_USER/tools/tunnel-client/tunnel-client \
  --runtime-client /home/YOUR_LINUX_USER/tools/tunnel-client/tunnel-client-runtime
```

Keep private state on the Linux filesystem, outside the document workspace, so
0700/0600 permissions are meaningful. Do not use Linux client registration to
configure a Windows client: that writes the Linux user's client configuration.

Follow [the ChatGPT account guide](CHATGPT.md) to create a tunnel associated with
the intended ChatGPT workspace and its restricted runtime key. Enter the tunnel
ID at the ID prompt. At the hidden key prompt, **paste once and press Enter**.
No visible characters is normal. Do not paste again just because nothing appears.
Run a launcher rather than editing its source: never paste a key into a `.cmd`,
PowerShell script, command argument, chat, screenshot or Git commit.

Keep Docker and the tunnel running. In another Ubuntu terminal:

```sh
/home/YOUR_LINUX_USER/tools/tunnel-client/tunnel-client health \
  --url-file /home/YOUR_LINUX_USER/.local/state/local-workspace-mcp/tunnel-health.url \
  --require-control-plane-poll
```

`doctor` validates configuration; it does not prove the key is accepted. Even
`/readyz` alone is insufficient. Require a successful authenticated control-plane
poll and a real ChatGPT tool call. Inspect error codes locally; do not publish
unredacted logs or credentials.

In ChatGPT, add a custom MCP server using **Tunnel**, the tunnel ID, and **no
additional authentication** (the private tunnel has its own access checks).
Connect the plugin and use it in an ordinary chat:

> Call get_workflow_instructions, then this plugin's run_python with
> print('WINDOWS_WSL_TUNNEL_OK'). Do not substitute built-in Python.
> Report actual stdout and exit_code.

Stop only your tunnel (Ctrl-C), start it again and repeat health and chat checks.
Do not shut down all WSL distributions for this test. Closing the terminal,
shutting down WSL, sleeping or turning off the PC can disconnect ChatGPT.
This recipe does not install a Windows login task or promise reboot persistence.

## Windows install and connect launchers (experimental)

`Install.cmd` and `Connect ChatGPT.cmd` provide Windows entry points for an
**existing Linux checkout**. They use the same `scripts/install.py` and
`scripts/connect_chatgpt.py` described above, including the runtime-only connection
and hidden key prompt. They do not install WSL, clone another version of the
server, download tunnel binaries, register clients, or configure login startup.
The `.cmd` wrappers use Windows PowerShell 5.1 with process-only `RemoteSigned`;
company execution policies still apply.

1. Complete the prerequisites above and clone this repository inside your
   non-root WSL user's Linux filesystem, for example `~/local-workspace-mcp`.
   Use a checkout containing `scripts/windows_wsl.py`.
2. On Windows, take `Install.cmd`, `Connect ChatGPT.cmd` and
   `scripts/windows.ps1` from the **same revision**, preserving the `scripts`
   subdirectory. They can be kept in a regular Windows folder. The repository,
   virtual environment, private state and tunnel binaries remain inside Linux.
3. In PowerShell in that Windows folder, run the following, replacing the distro
   with its actual name from `wsl --list --verbose`:

   ```powershell
   .\Install.cmd -Distro Ubuntu-24.04 -Repository "~/local-workspace-mcp" -Workspace "C:\MCP Documents"
   & '.\Connect ChatGPT.cmd'
   ```

The default workspace is `~/LocalWorkspace` and the default state directory is
`~/.local/state/local-workspace-mcp-wsl`. Supply `-State` for a different dedicated
Linux directory under your WSL home. State, workspace and source must not overlap.
Windows workspace paths are converted with `wslpath`; Linux absolute and `~/`
workspace paths are accepted too. Paths with spaces and Unicode are forwarded as
arguments. Quotes and line breaks in paths are rejected.

After a successful installation, only the distro, repository, state and workspace
choices are saved in `%LOCALAPPDATA%\LocalWorkspaceMCPWSL\settings.json`.
Reconnection reuses these choices; full permissions are never restored implicitly
for a new installation. With multiple distros and no saved selection, specify
`-Distro`. This settings file is separate from the community Windows integration's
settings; there is no automatic migration of existing private installations.

Documents mode remains the default and requires working Docker inside WSL. The
optional full mode requires `-Mode full -AcceptFullPermissions` on **each install**;
use a separate state and workspace when trying it. Add `-SkipWorker` only with
explicitly accepted full mode. Full mode runs with the WSL user's permissions,
including accessible Windows mounts; it is not confined to the workspace.

For a GitHub ZIP blocked by Windows, review the source and unblock the downloaded
ZIP through Properties before extracting again; do not weaken the global execution
policy. Launch failures return a nonzero exit code and leave saved Windows settings
unchanged. Keep the connection terminal open and stop with Ctrl+C. Use the health
and real ChatGPT checks above after connecting.

These entry points are adapted from the MIT-licensed
[community Windows/WSL integration](https://github.com/oscar2012-dot/local-workspace-mcp-windows).
Automated bridge tests use mocked subprocesses; Windows CI uses a fake `wsl.exe`
to test argument forwarding, saved settings and failure handling. Neither is a
clean Windows/WSL installation, Docker document workflow or ChatGPT end-to-end test.
Those checks remain required, including restart behavior and both installation modes.

## Optional Windows STDIO client

Windows clients can launch the Linux MCP independently of the ChatGPT tunnel.
Adapt distro, Linux username and absolute launcher path:

```toml
[mcp_servers.local-workspace]
command = "wsl.exe"
args = ["-d", "Ubuntu", "-u", "YOUR_LINUX_USER", "--", "/home/YOUR_LINUX_USER/.local/state/local-workspace-mcp/launch.sh"]
```

Docker must already be ready in that distro. Preserve other client entries rather
than replacing the whole configuration file. Merely installing Docker Desktop
on Windows does not verify Docker access inside Ubuntu.

## Validation scope

The contributor reported the observations below for commit `ba42837`, before
the runtime-only change. They are historical evidence, not a clean-install or
WSL validation of the current runtime recipe. Repeat the health/control-plane
and ChatGPT checks above after migrating to `tunnel-client-runtime`; see
[the migration notes](TUNNEL-LIFECYCLE.md).

On 2026-10-04 an existing Windows + WSL Ubuntu document-mode installation was
updated to `ba42837`. A Windows MCP client launched `wsl.exe`, discovered 14 tools
and successfully ran Docker Python. Official Linux tunnel-client v0.0.15 passed
health/ready and an authenticated control-plane poll. Ordinary ChatGPT web chat
used the document workflow and returned the Python marker with exit code 0.
After restarting only the tunnel process, a second ordinary ChatGPT Python call
returned a different marker with exit code 0 as well.

The Windows PowerShell 5.1 installer was also exercised against a separate new
Linux state and a Windows workspace containing spaces. It built the environment
and Docker image, exposed 14 MCP tools and executed Docker Python. Rerunning it
preserved a workspace sentinel. The official Linux client download, digest check
and `--version` invocation succeeded. Unit tests cover launcher parsing, full-mode
refusal, workspace migration refusal, payload exclusions and failure rollback.

WSL, Python, uv and Docker were already present for that installer test; initial
WSL provisioning and missing-dependency installation were not tested on a clean PC.
Native Windows, full host mode, ChatGPT desktop/mobile, Windows reboot/login
startup, and Docker Desktop WSL integration were not tested.
