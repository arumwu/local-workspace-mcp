# v0.1.1-alpha.1

Install and automatically register Local Workspace MCP with the shared ChatGPT desktop/Codex configuration.
Double-click Install.command for guided setup, or use the existing CLI. Reload MCP servers or open a new
task after installation; active apps are never restarted automatically.

The installer backs up config.toml, preserves comments/unrelated settings, reuses custom server names,
retains disabled entries and refuses conflicts. --no-register and --client-config provide explicit control.
Client registration tests cover new files, inline tables, comments/backups, duplicates, malformed input,
conflicts and config symlinks. An independent source installation registered a launcher and successfully
performed an actual host-tool file write from that configuration.

All 25 upstream tools and document functionality remain available. No hosted relay or signed app/pkg.
Full mode grants OS user-account access. Actual ChatGPT conversation tool execution and physical multi-Mac
SSH remain unverified. The earlier manual registration on the development Mac was detected read-only;
it was not modified by this update.

Use the source ZIP for the complete installer; the wheel alone does not contain the Node engine/worker context.
