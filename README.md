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

MapleBench, RuneBench, and the [Factorio Learning Environment](https://github.com/JackHopkins/factorio-learning-environment) inform the design. No upstream implementation has been copied into this repository; any future reuse must preserve its applicable license and attribution.

## Project license

A license for this project's original work has not been selected yet. Public availability is not a license grant. The upstream projects and game content retain their own licenses and rights.
