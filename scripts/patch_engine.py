"""Auditable, version-pinned privacy adaptations; refuse unexpected upstream files."""

import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "node_modules/@wonderwhy-er/desktop-commander"
assert json.loads((root / "package.json").read_text())["version"] == "0.2.50"
patches = {
    "tools/pdf/markdown.js": (
        "223a7cf36d662c04a29b9472e8b523f04fe80fdba23e3d836bf0b879c6d686a9",
        [
            (
                "const installedChrome = await installChrome();",
                "throw new Error('Install Chrome explicitly before using host_write_pdf.');\n"
                "            const installedChrome = null;",
            )
        ],
    ),
    "config.js": (
        "81117d84afe32b414b79aed2a01a00f8388686cb030641906d7af55a697ed7c7",
        [
            (
                "path.join(USER_HOME, '.claude-server-commander')",
                "path.resolve(process.env.LWMCP_ENGINE_STATE_DIR)",
            )
        ],
    ),
    "index.js": (
        "a4145198dc75cd34e7c7452c2054b4cc0d29e199ae1459961a17e4da25a13500",
        [
            ("await featureFlagManager.initialize();", "/* Local Workspace: no remote feature flags. */"),
            ("ensureChromeAvailable();", "/* Local Workspace: no automatic browser download. */"),
        ],
    ),
    "utils/toolHistory.js": (
        "9ba40b29b628af7fa4e336d9c88a00880948c4bf532af272c74b1fef5311f641",
        [
            (
                "path.join(os.homedir(), '.claude-server-commander')",
                "path.resolve(process.env.LWMCP_ENGINE_STATE_DIR)",
            ),
            ("arguments: args,", "arguments: {},"),
            ("output: this.capOutput(output),", "output: { redacted: true },"),
        ],
    ),
    "utils/fuzzySearchLogger.js": (
        "01cca1e415e91da50f24d36c454e3cca8a0170f71940725528f6569b9cdfc9f8",
        [
            (
                "path.join(os.homedir(), '.claude-server-commander-logs')",
                "path.join(process.env.LWMCP_ENGINE_STATE_DIR, 'logs')",
            ),
            (
                "async log(entry) {",
                "async log(entry) { return; // Local Workspace: no document content in logs.\n",
            ),
        ],
    ),
}
for name, (expected, edits) in patches.items():
    p = root / "dist" / name
    original = p.with_suffix(p.suffix + ".upstream")
    source = original.read_text() if original.exists() else p.read_text()
    if hashlib.sha256(source.encode()).hexdigest() != expected:
        raise SystemExit("Unexpected upstream source: " + name)
    for old, new in edits:
        assert source.count(old) == 1, name
        source = source.replace(old, new)
    if not original.exists():
        original.write_bytes(p.read_bytes())
    p.write_text(source)
print("Desktop Commander 0.2.50 privacy adaptations applied.")
