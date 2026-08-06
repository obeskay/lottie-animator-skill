# Security Policy

## Reporting a Vulnerability

Please **do not** open a public issue for security problems.

Use GitHub's private reporting: go to the **Security** tab of this repository
and click **Report a vulnerability**. Private vulnerability reporting is enabled,
so the report reaches the maintainer without ever being public.

Please do not use a public channel (issues, discussions, social media) to
disclose the details before a fix is available.

Include, where possible:

- affected version, branch or commit
- steps to reproduce or a proof of concept
- the impact you believe it has

You can expect an initial response within **72 hours** and a status update at
least every 7 days until the report is resolved.

## Supported Versions

Only the latest commit on the default branch is supported. Older tags and
branches do not receive security fixes.

## Secrets

This repository must never contain real credentials. `.env` files, API keys and
tokens are gitignored and blocked in CI. If you believe a secret was committed
at any point, report it privately using the process above so it can be rotated.

---

Reportes en español son bienvenidos.
