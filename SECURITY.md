# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 3.11.x  | Yes       |
| < 3.11  | No        |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for an undisclosed vulnerability.

Report privately via GitHub Security Advisories:

https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/security/advisories/new

Include a description, affected version, and reproduction steps. We will acknowledge the report and work on a fix before any public disclosure.

## Secrets

Never commit API keys, tokens, or `.streamlit/secrets.toml`. Use environment variables (`XAI_API_KEY`) or local gitignored secret files. This is an independent community project and is not affiliated with xAI.

Intimate / NSFW pipelines require a local `nsfw attest` (gitignored `.aup_attestation.json`) with all four flags: 18+, imaginary adults only, not a real person, and AUP acknowledged. Operators must follow the [SpaceXAI Acceptable Use Policy](https://x.ai/legal/acceptable-use-policy).
