# Factorio-Bench

Factorio-Bench is a proposed environment for evaluating AI agents on factory construction, production, logistics, diagnosis, and long-horizon planning in Factorio.

**Status: design only.** This repository contains the environment design and contribution safeguards. It does not yet contain a runnable benchmark, game integration, simulator, or benchmark results.

## Approach

The design draws on [MapleBench](https://github.com/dmarzzz/maplebench) and [RuneBench](https://github.com/MaxBittker/RuneBench): agents use a narrow interface to act in a persistent game world, and an independent verifier measures outcomes from game evidence.

- **Use real Factorio first.** Pin the engine, content, starting save, and agent rules so comparisons have a defined meaning.
- **Measure operating factories.** Score sustained production and useful delivery, with explicit time and resource budgets.
- **Keep the evidence.** Record initial conditions, actions, failures, and authoritative outcomes so a result can be inspected and recomputed.
- **Test a simulator separately.** A future implementation from scratch must pass behavioral comparisons against Factorio for each supported task. Sharing an API does not establish gameplay compatibility.

The proposed long-term scope includes the base game and Space Age under separate content profiles. The first task is smaller: build an automated iron-plate factory, then keep mining, smelting, and delivering during a hands-off verification period.

## Read the design

| Document | Purpose |
| --- | --- |
| [Environment design](docs/factorio-bench-design.md) | Mechanics, agent interface, clocks, tasks, scoring, and acceptance gates |
| [Documentation index](docs/README.md) | Find architecture, evaluation, and implementation sections |
| [Contributing](CONTRIBUTING.md) | Propose changes, write evidence-based documentation, and run checks |
| [Data sharing](docs/data-sharing.md) | Decide what belongs in a public change or result bundle |
| [Security](SECURITY.md) | Handle credentials and report security issues |
| [Third-party references](THIRD_PARTY.md) | Separate design inspiration from incorporated material and game rights |

The [implementation milestones](docs/factorio-bench-design.md#implementation-milestones-and-acceptance) begin with a native capability audit, controlled player actions, and one independently verified task. The [architecture](docs/factorio-bench-design.md#architecture-and-trust-boundaries) keeps the agent, game adapter, verifier, and viewer separate.

## Contribute

Useful early contributions include checking native API behavior, finding gaps in action or scoring rules, and proposing reproducible acceptance cases. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a change.

Repository checks require Git, Make, Python 3.9 or newer, and [Gitleaks](https://github.com/gitleaks/gitleaks/releases) 8.30.1 or newer on your local `PATH`. CI uses a pinned Gitleaks release. No game installation or API credentials are needed for these checks.

Run them before submitting:

```sh
make check
make check-secrets
```

These checks support repository hygiene; they do not validate Factorio gameplay or replace a review of material intended for publication.

## Game content and attribution

Factorio-Bench is an independent project and is not affiliated with or endorsed by Wube Software. Factorio belongs to Wube Software. Game executables, proprietary assets, and private run artifacts are not distributed in this repository. The native backend design requires a separately provisioned game installation.

MapleBench, RuneBench, and the [Factorio Learning Environment](https://github.com/JackHopkins/factorio-learning-environment) inform the design. The default is an independent implementation informed by public documentation and observed behavior. No upstream implementation has been incorporated into this repository. See [THIRD_PARTY.md](THIRD_PARTY.md) for provenance and the review required before any code reuse.

## Project license

Original source and accompanying original documentation are available under [PolyForm Noncommercial 1.0.0](LICENSE), except material explicitly identified as subject to separate terms. The project is **source available**; PolyForm Noncommercial is not an open-source license. Preserve the [required notice](NOTICE).

The license permits noncommercial purposes and the institutional uses specified in its terms. Uses outside those permissions require a separate agreement from the relevant rights holder. Cytonomy can discuss commercial terms for rights it controls; open a non-confidential licensing inquiry through [GitHub Issues](https://github.com/cytonomy/factorio-bench/issues). An inquiry is not permission to begin the proposed use. The full license controls, and neither it nor a commercial harness agreement grants rights to the game or third-party material.
