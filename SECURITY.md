# Security model

Single owner, one process, no hosted multi-user service. Early alpha; no independent security audit.
Report vulnerabilities privately through GitHub's security advisory feature; do not publish credentials.

Full mode intentionally provides arbitrary OS user-account execution, network access and destructive operations.
Neither the upstream command blocklist nor allowedDirectories is a sandbox. Prompt injection, an untrusted
MCP client or a stolen authorized token can compromise everything this user can access, including SSH peers.
Use a separate low-privilege OS account/VM and backups when needed. Do not expose full mode casually.
Client approval policies remain important; tool annotations are hints, not authorization boundaries.

Document mode: descriptor-relative native access blocks traversal, symlinks/hardlinks, hidden names, special
files and overwrites. Docker sees the entire input directory read-only (including hidden files), and exports
read-write. Docker has no network/socket, capabilities, new privileges or writable root; resource/time/output
limits apply. Export disk growth is not capped. Do not allow concurrent untrusted writers to mount paths.
Docker protects less than a separate machine and does not guarantee immunity to runtime/kernel vulnerabilities.

STDIO trusts the launching account. Pairing files are private owner-supplied executable commands, not untrusted
input: they can run local programs. SSH should use verified host keys and existing authentication.
HTTP listens only on loopback and requires an HTTPS origin plus OAuth DCR/PKCE and explicit owner-key consent.
Host/Origin, CSRF, request-size/rate limits, exact redirect hosts, audience validation, hashed tokens,
one-time codes and refresh rotation are enforced. A refresh replay revokes its token family.
Owner keys are 256 random bits, outside the workspace, single-link files with mode 0600.
Tokens expire in one hour; refresh sessions have an eight-hour absolute limit. Restart revokes all.

Artifact links are temporary bearer capabilities to exact file bytes. Anyone holding the link can download;
changed files invalidate prior links. No access logging of bearer URLs. Never share sensitive links publicly.
Upstream telemetry/remote feature flags are disabled; history omits arguments/results and fuzzy document
logging is disabled. Vendor feedback is replaced by local files. Host commands and explicit URL reads can
still use the network; this is not an outbound firewall. Browser auto-download is disabled.

Known scope: no automatic file versioning, signed distribution, credential vault, durable OAuth database,
enterprise policy enforcement or browser/desktop clicking. Depend on OS/client controls for these.

Client registration is now an explicit part of installation (opt out with --no-register). It updates only
one documented MCP table, backs up the original with permissions 0600, validates unrelated settings are
unchanged, checks for concurrent changes and atomically replaces the target. Intentional config symlinks
are followed, not replaced. Existing matching or disabled entries are preserved; conflicting names fail.
No approval policy or sandbox setting is changed. The installer never restarts the client.
