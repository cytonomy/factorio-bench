# Security policy

Factorio-Bench is in the design stage. There is no supported runtime release or hosted service. Security-sensitive work includes the proposed agent sandbox, game control channel, verifier, experiment records, and the repository's publication checks.

## Report a vulnerability privately

Use GitHub's [private vulnerability reporting form](https://github.com/cytonomy/factorio-bench/security/advisories/new). Do not open a public issue containing exploit details, credentials, private game saves, or raw agent transcripts. If the private form is unavailable, open an issue requesting a private reporting channel without including the sensitive details.

Describe the affected revision, expected boundary, observed behavior, and a minimal reproduction using synthetic data. Do not send live credentials, even in a private report. There is no guaranteed response deadline at this stage.

## Handle suspected exposure

Stop further publication and notify a maintainer privately. Revoke or rotate exposed credentials through the provider's secure interface. Then remove the material from the proposed files, history, logs, and artifacts as appropriate. Deleting the latest file alone does not remove earlier copies or make an exposed credential safe again.

Use local tools that suppress secret values in their output. Reports should identify the affected credential by a non-secret name and describe remediation status. Do not test an exposed credential or paste it into an issue, chat, command argument, or online scanner.

## Repository safeguards

Local checks reject common private-file paths and run secret scanning before publication. GitHub Actions repeats the checks with read-only repository permissions and no project credentials. These checks reduce accidental exposure; they cannot determine whether every document, image, or generated artifact is appropriate to share.

For permitted public material and review steps, see [the data sharing policy](docs/data-sharing.md). GitHub's secret scanning and push protection settings are additional controls and must be verified in repository settings rather than assumed from this document.
