# Contributing

Keep changes narrow and tested. Preserve default document isolation and explicit opt-in host permissions.
Follow README development commands. Integration tests must use temporary directories and only terminate
processes they created. Never commit owner keys, tokens, local settings, tool output or customer files.
Update source hashes and THIRD_PARTY_NOTICES when changing the upstream engine. Privacy patches must fail
closed against an unexpected source version. Do not replace them with unrestricted search-and-replace.
Describe the problem, behavior change and actual validation in a pull request. No telemetry by default.
