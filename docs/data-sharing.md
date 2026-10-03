# Data sharing and publication

This is a public source repository. Publish the design, original source, and reviewed evidence needed to understand the benchmark. Keep credentials, personal information, restricted game content, and raw experiment records out of Git. A public repository is not the default destination for everything produced by an experiment.

## What belongs in the repository

| Material | Publication rule |
| --- | --- |
| Design and original source | Include clear status, assumptions, primary-source citations, and the applicable license. |
| Task definitions and manifests | Include rules, versions, seeds where intended, and checksums. Use portable paths and non-secret identifiers. Keep held-out evaluation content separate. |
| Configuration examples | Use obvious placeholders such as `REPLACE_LOCALLY`. Never copy a working credential or a personal configuration file. |
| Small synthetic fixtures | Include only data created for testing that contains no credentials, personal information, or restricted assets. Label it synthetic. |
| Reviewed results | Publish aggregates and selected evidence with task, engine, agent, and verifier provenance. Preserve failed-attempt counts and explain exclusions. |
| Upstream references | Link to the source and record the reviewed revision. Track attribution and license obligations before incorporating code. |

Game executables, proprietary art/audio, downloaded game data, local saves, raw observations and model transcripts, recordings, crash dumps, authentication material, and personal tool state stay in local storage or a separately controlled artifact store. Git stores manifests and approved references to those artifacts only when access and sharing rights have been reviewed. A checksum identifies an artifact; it does not make that artifact safe to distribute.

The native game and upstream projects retain their own names, licenses, and asset rules. Factorio-Bench's [license](../LICENSE) covers only rights we are entitled to grant. Follow [the independent implementation and provenance policy](../THIRD_PARTY.md); an architectural citation does not authorize copying covered code.

## Public architecture and private operations

Public design documents may describe component responsibilities, documented game APIs, agent-facing contracts, scoring rules, illustrative tasks, and reproducibility requirements. These are research specifications, not a map of a live deployment. Keep enough detail for readers to assess what a benchmark would measure.

Keep actual hostnames and addresses, administrative endpoints, account and tenant identifiers, deployment inventories, private network topology, credential-store locations, customer configuration, internal incident procedures, and commercially sensitive capacity or cost plans out of the repository. Held-out tasks, their unreleased seeds and saves, and private training or evaluation datasets also stay in separately controlled storage. These exclusions apply to diagrams, screenshots, commit messages, pull requests, issue text, and CI logs as well as source files.

Before publication, manually inspect the exact diff and its context for private architectural information. A secret detector cannot determine whether an endpoint, diagram, or business plan is confidential. Replace sensitive examples with synthetic, portable descriptions; do not invent deployments or imply a proposed system is already running. The public bootstrap task is an illustrative development task, not a held-out evaluation fixture.

Information already pushed to a public repository cannot be made confidential by deleting the latest copy or changing the license. If private material is discovered in published history, stop further publication and follow [the security policy](../SECURITY.md); do not describe a later cleanup as undoing prior exposure.

## Collect less and separate records

Keep three destinations distinct:

1. **Source repository:** Reviewed code, documentation, configuration templates, and task contracts.
2. **Private run storage:** Raw evidence required to reproduce or diagnose an attempt, with controlled access and an explicit retention period.
3. **Publication export:** A new, reviewed bundle containing only the records selected for sharing.

Do not publish directly from a live run directory. Generate an export with an explicit field allowlist. Remove credential fields, authorization headers, personal paths, account identifiers that are not needed for attribution, private URLs, and free-form diagnostics unless specifically reviewed. Inspect images and recordings for visible account data, browser UI, or terminal content. Automated text scans cannot clear visual media for publication.

Experiment manifests must state the retention period and who can read the raw records. Keep an immutable original only in its authorized storage; create a redacted derivative for sharing. Describe redaction and missing evidence in the publication so readers can assess its limits. Do not claim a public result is fully reproducible when necessary inputs are unavailable.

## Before committing or pushing

Review the proposed file list locally. Check that examples are synthetic, paths are portable, links are intentionally public, and factual claims have the right evidence. Use a GitHub no-reply email if you do not intend to publish a personal commit email.

Run the repository checks:

```sh
make check
make check-secrets
```

Stage the specific reviewed files and run the checks again against the final candidate state. The secret check must cover existing history and the staged snapshot, because removing a secret from the working copy does not remove it from either location. Do not bypass a failing check or add a broad exception to silence it. Resolve false positives narrowly and document why a proposed exception is safe.

`.gitignore` prevents routine staging of local artifacts. It does not untrack files already committed, block force-adds, or remove old commits. Secret detectors also miss some credential formats and private data. Manual review remains necessary. If a credential may have been exposed, follow [the security policy](../SECURITY.md) before continuing.

## Publishing results responsibly

Every result export must identify the task and scoring version, game/backend version, observation and action track, agent configuration, budgets, number of planned and completed trials, failure categories, and uncertainty. Label reconstructed viewers separately from native footage and label simulated runs separately from native Factorio runs.

Keep provenance without exposing credentials or private account details. Sharing a benchmark result does not authorize uploading its full raw transcript or save. Maintainers review each export before publication; the repository's CI does not upload run artifacts.
