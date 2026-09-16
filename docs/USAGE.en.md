# User guide: local tools in ordinary ChatGPT conversations

[繁體中文](USAGE.zh-TW.md) · [First-time setup](CHATGPT.en.md)

After connecting `Local Workspace MCP`, use ordinary ChatGPT chat to ask your computer to work with files,
documents and Python. Codex and Work are not required. The private tunnel carries tool requests;
your computer executes them. It does not move your runtime into the cloud.

## Keep the host available

The host must be powered on, awake, online and running the tunnel. The macOS login service requires you to
log in after restarting. Turning off the display is different from putting the computer to sleep: a locked
screen is fine only while networking, disks and background processes remain available.
Required external disks must be mounted. Docker must be running for `run_python`; other host tools may work
without it. This installation does not wake the computer remotely or change its sleep settings.
When the host is offline, ordinary ChatGPT still works, but cannot operate that host's local files.

## Computer and phone

Sign into the same ChatGPT account/workspace, start an ordinary conversation, and select or mention
`Local Workspace MCP`. If your mobile interface exposes the custom plugin, it can use the same private tunnel.
The phone sends instructions; the computer does the work. Python, Docker and MCP do not need to be installed
on the phone. The tunnel does not require the two devices to share Wi-Fi; both need appropriate internet access.

Custom-plugin availability can differ between mobile apps, mobile browsers and desktop apps, and by account
or workspace. Verify an actual tool call on each surface. Ordinary ChatGPT web calls have been tested;
mobile and native desktop App calls have not been independently tested by the maintainer.

## Connection test

> Use Local Workspace MCP: call get_workflow_instructions, then run_python with print('LOCAL_MCP_OK').
> Do not substitute built-in Python or read/write other files. Report the actual tool, stdout and exit code.

Expect an actual plugin call returning `LOCAL_MCP_OK` and exit code `0`. An installation claim or code example
is not a successful test.

## Everyday requests

- List the first level of a specified folder without changing anything.
- Analyze sales.csv in the configured workspace, create an Excel report and chart, and verify totals.
- Turn notes.md into Word and PDF, preserve the original, reopen outputs and report their locations.
- In full mode, back up and modify a specified document without changing unrelated files.

Use precise paths. Docker Python reads the dedicated workspace; full-mode host tools handle other permitted
locations. Full mode has OS user permissions, including file changes, process execution and network access;
its directory configuration is not a sandbox.

## Outputs and cleanup

Docker deliverables are saved on the host in the workspace's `exports` folder. Local paths are not downloadable
phone attachments. This STDIO tunnel does not automatically upload files or create public download links.
Use a separately approved file-transfer method to get outputs onto another device.

Disposable Docker job containers are removed; deliverables remain. The tunnel and MCP server stay running
and use memory. Stop full-mode processes created for a task when no longer needed.
The macOS login item is named `ChatGPT Local Workspace MCP` by default, or `ChatGPT 本機工具` in the Chinese guide.
Disconnecting the ChatGPT plugin does not stop the host service. See setup instructions for service removal;
do not remove unrelated shell/open login items.

For failures, check host power/login/sleep, network, external disks, tunnel, account/workspace and plugin
connection, then Docker if Python fails. Retest in a new chat instead of creating duplicate installations.

Reference: [OpenAI Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).
