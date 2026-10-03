## Change

Explain the problem, the resulting behavior, and any design decision a reviewer needs to assess.

## Validation

List the checks performed and any remaining limitations. For a documentation change, verify claims, examples, and links.

- [ ] `make check` passes.
- [ ] `make check-secrets` passes locally.
- [ ] The proposed files contain no credentials, personal data, raw run artifacts, or restricted game assets.
- [ ] The change exposes no private deployment details, customer information, or held-out evaluation data.
- [ ] Any incorporated third-party material has reviewed provenance, compatible permissions, and required notices; external contribution rights are resolved before merge.
- [ ] Documentation distinguishes proposed behavior from implemented or measured behavior.

Do not paste scanner matches, private logs, credentials, or unreviewed recordings into this pull request.
