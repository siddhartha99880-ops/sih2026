# Security

This is a prototype handling potentially sensitive land-record information.

- Use synthetic or explicitly authorized records only.
- Never commit `.env`, credentials, private keys, or raw private documents.
- Keep secrets in environment variables and never log them.
- Do not expose server-side secrets through frontend configuration.
- Treat OCR and risk output as advisory, not legal truth.
- Keep owner information out of responses unless the workflow requires it.
- Hash audit state; do not place documents, images, or personal information on-chain.

Report suspected vulnerabilities privately to the repository maintainers rather than opening a public issue with sensitive details.
