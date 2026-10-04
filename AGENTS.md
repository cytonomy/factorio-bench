# Repository instructions

Factorio-Bench currently contains a proposed design, a runnable synthetic evidence demo, and repository checks. The demo is not a game backend or an AI evaluation. Do not describe the environment, simulator, integrations, or benchmark results as implemented until they exist and have been verified.

## Protect private information

- Never put secret values in chat, tool arguments, terminal output, screenshots, reports, commits, or issue text. Do not ask someone to paste credentials into a conversation.
- Let authorized local processes use a credential store or native secure prompt. Refer to credential names or paths and report only non-secret status.
- Do not dump environment variables, authentication headers, credential files, or verbose authentication traces. Filter diagnostics locally before returning any output.
- Keep game binaries, proprietary assets, saves, raw experiment traces, recordings, and personal agent state outside version control. Follow [the sharing policy](docs/data-sharing.md).
- A `.gitignore` rule or successful scanner is not proof that content is safe to publish. Review the exact proposed files and Git history before pushing.
- Keep live deployment topology, private endpoints, account identifiers, customer information, and held-out evaluation data out of public files. Describe public interfaces and conceptual boundaries without disclosing private operations.

## Make changes reviewable

- Keep source facts, proposed behavior, and measured results distinct. Cite primary sources and preserve version and compatibility limits.
- Use independent implementation informed by public documentation and authorized observations. Follow [THIRD_PARTY.md](THIRD_PARTY.md) before copying or adapting source; do not imply that our license replaces upstream terms.
- Preserve the unchanged license text and required notice. Resolve contributor permissions before merging external copyrighted patches intended for commercial relicensing.
- Use plain writing, descriptive headings, relative repository links, and small changes with a clear purpose. Update the documentation index when adding a durable document.
- Keep agent control separate from world administration and scoring. Do not introduce free resources, hidden information, or timing shortcuts into the player-equivalent track.
- Add dependencies only when they provide a clear benefit. Pin executable CI dependencies and keep workflow permissions minimal.
- Use `make check` for repository checks and `make check-secrets` before a commit or push. Inspect failures without printing matched secret text. Add meaningful tests when changing the publication checks or other sensitive behavior.
- Stage reviewed paths explicitly. Never force-add ignored files to bypass the publication policy. Do not publish private diagnostics to fix a failed check.
- Preserve unrelated work. Do not commit, push, or publish unless the current task authorizes it.
