# Contributing to Factorio-Bench

Factorio-Bench is currently a design repository. Start with the [README](README.md) and [environment design](docs/factorio-bench-design.md). Contributions should make the proposed environment easier to implement, evaluate, or audit without implying that unbuilt features already work.

## Propose a focused change

For a small correction, open a pull request with the change and its reason. For a change to mechanics, agent privileges, task objectives, clocks, or scoring, describe the problem, a concrete example, and the evidence that would establish the new behavior. An issue or draft pull request is a useful place to discuss a substantial design change before implementation.

Keep each change focused enough to review. Separate unrelated cleanup. Explain the resulting behavior and any remaining uncertainty in the pull request; record durable decisions in the design rather than leaving them only in a discussion.

Useful contributions at this stage include:

- Verifying a proposed native API mechanism against a pinned Factorio release.
- Identifying a way an agent could bypass costs, gain hidden information, or exploit a score.
- Defining a fixture and expected outcome for an acceptance test.
- Improving terminology, navigation, citations, or an ambiguous requirement.

## Write claims that can be checked

Distinguish a proposal, a documented API capability, and observed behavior in a running environment. Cite primary sources for external facts. Use a commit or version permalink for implementation details when available, and state when a reference follows a moving branch. Record the relevant version, setup, and limitations with experimental observations.

Use plain language and consistent terms. Define unfamiliar terms when first used. Keep examples small, label illustrative configuration, and avoid invented results or unsupported claims of exact compatibility. A change to a score must explain what success means, how the verifier obtains evidence, and which failure cases it rejects.

The full design is the source of truth for proposed behavior. Keep the README concise and update its status only when the corresponding implementation and acceptance evidence exist. Add new documentation to the [index](docs/README.md) so readers can find it.

## Keep public material safe to share

Follow the [data-sharing policy](docs/data-sharing.md) and [security guidance](SECURITY.md). Never include secret values in issues, pull requests, commits, screenshots, logs, examples, or assistant transcripts. Enter credentials directly through an approved local credential store or native secure prompt; use credential names and non-secret status when discussing setup.

Keep raw runs, game saves, recordings, local configuration, downloaded game content, and private evaluation fixtures outside public changes. Publish only deliberately reviewed exports with the necessary rights and provenance. Use small synthetic examples when explaining a problem. Ignored files and a passing scanner do not establish that material is safe to publish.

If you find a credential exposure or other sensitive security issue, follow [SECURITY.md](SECURITY.md) instead of posting the material in a public issue.

## Check a change

From the repository root, run:

Use Git, Make, Python 3.9 or newer, and Gitleaks 8.30.1 or newer on `PATH`. The repository checks need no game installation or model credentials.

```sh
make check
make check-secrets
```

Enable the included commit and push hooks for this checkout:

```sh
git config --local core.hooksPath .githooks
```

The hooks run both checks before a commit or push. This setting is local and is not installed automatically by cloning. Hooks can be bypassed, so they complement review, CI, and GitHub push protection. The secret checker suppresses matched content and scanner diagnostics; investigate a failure in a trusted local editor without copying potentially sensitive material into a transcript.

Read the check output and resolve failures before submitting. These commands are repository checks, not tests of a running Factorio environment. Do not claim gameplay validation from them.

Review the files selected for the commit, the rendered Markdown, and relative links. Review content in a local editor before including it in terminal output or a transcript if there is any chance it contains private material. For design changes, walk through at least one success case and one relevant failure case and explain how the proposed verifier distinguishes them. For implementation changes, include the smallest meaningful validation of the behavior and its failure modes; do not add tests that merely repeat the implementation.

## Describe validation and limitations

In the pull request, explain the problem, the final change, and what was checked. Mention behavior that remains proposed or untested. A future runtime change should identify the affected content profile, track, task, and compatibility claims where applicable.

Use public upstream links for references. Before introducing a dependency or copying source, check its license and preserve the required notices. Do not add proprietary game code or assets. Contribution review does not substitute for the native conformance and benchmark acceptance gates in the design.
