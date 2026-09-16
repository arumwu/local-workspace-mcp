# Connection options

**Primary path: [ordinary ChatGPT conversations via private tunnel](CHATGPT.en.md) ([中文](CHATGPT.md)).**
Real web conversation Python calls were verified on 2026-09-17; native App acceptance is separate.

## Local desktop

With explicit `--register-local-client`, the installer registers `launch.sh` in the documented shared ChatGPT/Codex TOML config.
Reload MCP servers or start a new task after installing. It does not restart the app automatically.
The original file is backed up before writing; comments/other servers remain intact. A matching launcher
under another name is reused, including existing arguments and enabled/disabled preference.
To skip registration use `--no-register`; to target a specific config use `--client-config /path/config.toml`.
For manual setup in another compatible client, use `launch.sh` as a STDIO command with empty arguments.
The client starts/stops the process; there is no local listening port.
Do not assume ordinary ChatGPT chat mode can use local tools because a separate desktop Work/Codex mode can.
Check that your actual app/mode exposes a local MCP setting and that `list_directory` really returns your files.
Local STDIO UI acceptance is separate from the verified ordinary web conversation through a tunnel.

Current official references (checked 2026-09-11):
- [ChatGPT MCP documentation](https://learn.chatgpt.com/zh-Hant/docs/extend/mcp)
- [ChatGPT developer mode](https://developers.openai.com/api/docs/guides/developer-mode)
- [Secure MCP tunnels](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)

## ChatGPT web / cloud execution

Cloud ChatGPT cannot directly reach your computer's localhost. Choose either:
1. An official secure MCP tunnel, if your account/workspace supports it. Follow the official guide: tunnel ID,
   associated workspace, a runtime OpenAI Platform key and appropriate tunnel permissions are required.
   This does not require renting a server, but is not key-free and availability/cost must be checked on your account.
2. Your own HTTPS origin/reverse proxy forwarding to this server's HTTP OAuth transport.

The base installer does not provision either account connection or store an OpenAI key.
Follow the primary tunnel guide to configure your own private runtime key; do not commit it.
Do not expose the STDIO engine as anonymous HTTP.

For a reverse proxy on the same machine, forward **all paths**, not just `/mcp`:

```caddy
mcp.example.com {
    reverse_proxy 127.0.0.1:8765
}
```

Replace with an origin you control. DNS, TLS and network reachability are your responsibility.
In ChatGPT developer mode, add `https://mcp.example.com/mcp` using OAuth. Enter the local owner key only on
that origin's consent page, never in a chat. Registered client display names are unverified.
Consent identifies full host/paired-device access when enabled. Refresh lasts up to eight hours.
Stop/restart the server to revoke every connection. Do not run multiple server workers.

## Pair computers by name with SSH

Install this project on each target, test its launcher locally, and configure SSH normally.
Verify the host key and login yourself; never disable host-key checks or put passwords in this configuration.
Store the following file **outside the shared workspace**, with permissions `0600`:

```json
{
  "studio": {
    "command": "/usr/bin/ssh",
    "args": ["-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
             "owner@studio.local", "/absolute/private-state/launch.sh"]
  }
}
```

Start the local launcher with `--devices /absolute/private-state/devices.json`.
Use `list_paired_devices`, `ping_device`, `list_device_tools`, then `call_device_tool` with the returned schema.
The destination is owner configured; the model cannot add arbitrary peers through a pairing tool.
Sessions remain open so remote interactive processes/search IDs survive calls.
`shutdown_device_agent` stops that agent process, **not the computer**. An on-demand SSH agent can start again
when reconnected; no remote daemon service is installed. Physical multi-Mac SSH verification is pending;
two independent local stdio agents have been tested.

## Acceptance checklist

1. Confirm the exact ChatGPT app/mode sees tools and lists a harmless local input file.
2. Ask for a CSV analysis, XLSX and DOCX; open actual output files, verify totals and inspect previews.
3. Test a harmless full-mode edit and short terminal command with the client's approval policy.
4. Stop the agent and verify access is lost. For HTTPS, test OAuth login and expired/revoked downloads.

These steps must be executed in the real client before claiming full end-to-end ChatGPT compatibility.
