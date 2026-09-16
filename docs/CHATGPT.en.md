# Ordinary ChatGPT conversations: private local tools

[繁體中文完整教學](CHATGPT.md) · [Prerequisites](README.en.md) · [Validation](VALIDATION.md)

The primary target is **ordinary ChatGPT chat**, with local files, terminal tools and document generation.
The supported setup described here is a private OpenAI Secure MCP Tunnel connected as a ChatGPT plugin.
Registering a STDIO server in a Codex/desktop config is not proof that ordinary chat can use it.
On 2026-09-17, real ordinary ChatGPT web conversations called `run_python` successfully, including after
restarting the tunnel. Native ChatGPT App conversation acceptance remains pending.


After setup, see the [everyday user guide](USAGE.en.md) for phones, host availability and output access.

## Install and connect

1. Download the [current source ZIP](https://github.com/arumwu/local-workspace-mcp/archive/refs/heads/main.zip).
   Install prerequisites, then run `./Install.command --workspace /absolute/task-files --state /absolute/private-state
   --mode full` as one line. Full mode explicitly grants OS user permissions; documents remains the safer default.
   Installation no longer changes local Codex/STDIO configuration by default.
2. In [Platform tunnel settings](https://platform.openai.com/settings/organization/tunnels), create a tunnel
   associated with the ChatGPT workspace you will use. Create a restricted runtime API key with **Tunnels Read + Use**.
   Account availability and charges must be checked against current official terms. No shared project key is provided.
3. Obtain the matching binary from [official tunnel-client releases](https://github.com/openai/tunnel-client/releases)
   and verify its checksum. Tested: v0.0.14 on macOS arm64. Store the runtime key in a private file with mode `0600`,
   outside shared files and Git. Never paste it into chat or pass its value as a command argument.
4. Generate a STDIO profile:

```sh
tunnel-client init --sample sample_mcp_stdio_local \
  --profile local-workspace --profile-dir /absolute/private-state/tunnel-profiles \
  --tunnel-id tunnel_YOUR_ID --mcp-command /absolute/private-state/launch.sh \
  --health-listen-addr 127.0.0.1:0
```

In the generated YAML, set `control_plane.api_key` to `file:/absolute/private-state/runtime-key`.
Set `health.url_file` to `/absolute/private-state/tunnel-health.url` and keep `health.listen_addr` on loopback.
Use mode `0600` for the profile, then run:

```sh
tunnel-client doctor --config /absolute/private-state/tunnel-profiles/local-workspace.yaml
tunnel-client run --config /absolute/private-state/tunnel-profiles/local-workspace.yaml
```

5. In ChatGPT, enable developer mode under Security/login. Go to Plugins → Create app, enter
   `Local Workspace MCP`, choose **Tunnel**, select your tunnel, and select **No authentication** for this
   STDIO target. The private tunnel still enforces its account/workspace and runtime-key access; this is not
   anonymous public HTTP. Review the requested access, create and connect.
6. Start a new ordinary **Chat** conversation, select/mention the plugin, and ask:

> Use Local Workspace MCP: call get_workflow_instructions, then run_python with print('CHATGPT_LOCAL_MCP_OK').
> Do not substitute built-in Python. Report actual stdout and exit code.

Expect the marker and exit code `0` from an actual tool call. Test the native App independently.

## macOS login startup

Stop the foreground process with Ctrl-C first. If using managed `runtimes connect`, stop that alias first
with `tunnel-client runtimes stop local-workspace`. Do not start two clients for the same tunnel.
With Xcode Command Line Tools installed, run from the project:

```sh
python3 scripts/install_macos_autostart.py \
  --tunnel-client /absolute/path/tunnel-client \
  --config /absolute/private-state/tunnel-profiles/local-workspace.yaml \
  --name 'ChatGPT Local Workspace MCP'
```

This compiles a small named app in `/Applications`, ad-hoc signs it locally, and associates the login agent
with that app. It is not a notarized distribution. The executable entry is no longer `/bin/sh`, so the service
has an identifiable app name. Runtime/data stay where configured. An existing Storage Guard is honored;
missing config/runtime files prevent execution. Retries are throttled to 30 seconds. It starts **after login**,
not before login, and does not start Docker Desktop. Existing same-name files are refused rather than overwritten.

```sh
launchctl print "gui/$(id -u)/ChatGPT Local Workspace MCP"
```

Verify `state = running`, then `/readyz` at the address in your health URL file, then a real ChatGPT tool call.
To disable/remove the login registration:

```sh
launchctl bootout "gui/$(id -u)/ChatGPT Local Workspace MCP"
rm "$HOME/Library/LaunchAgents/ChatGPT Local Workspace MCP.plist"
```

Disconnect the plugin in ChatGPT and remove its launcher app if no longer needed. Your files and key remain.
Do not reset the entire macOS background-item database to remove an old name, or delete unrelated shell agents.
Linux users should use their own service manager; no Linux autostart helper is supplied here.

## Files and ongoing processes

Docker jobs read `/workspace` and write `/output` (the workspace's `exports`). Containers are removed after jobs;
deliverables remain. Keep scripts/intermediates in container `/tmp`. Full-mode user-created host processes may
persist and should be stopped when no longer needed. The tunnel and MCP server themselves must stay running.
Local paths returned over STDIO are not automatically downloadable ChatGPT attachments.

Official references: [Connect a ChatGPT plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt),
[Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).
