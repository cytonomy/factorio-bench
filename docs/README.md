# Documentation

Factorio-Bench is a proposed benchmark environment. The native benchmark is not implemented. A runnable synthetic evidence demo makes the proposed scoring contract tangible without running a game or an AI model.

Start with [the evidence demo](examples.md) to run three examples and explore their outcomes. The [reviewed media guide](assets/README.md) explains the provenance of its screenshots.

## Environment design

The [environment design](factorio-bench-design.md) is the main technical document. Read it in full when changing benchmark semantics, or use these entry points:

| Topic | Sections |
| --- | --- |
| Motivation and scope | [Research basis](factorio-bench-design.md#research-basis), [mechanical fidelity](factorio-bench-design.md#what-must-remain-faithful), [backend decision](factorio-bench-design.md#backend-decision) |
| System boundaries | [Architecture](factorio-bench-design.md#architecture-and-trust-boundaries), [agent tracks and actions](factorio-bench-design.md#agent-tracks-and-control-contract) |
| Time and task definitions | [Episode lifecycle](factorio-bench-design.md#time-and-episode-lifecycle), [task suite and metrics](factorio-bench-design.md#task-suite-and-outcome-metrics), [example contract](factorio-bench-design.md#example-task-contract) |
| Trustworthy evaluation | [Repeated trials](factorio-bench-design.md#repetition-and-trustworthy-comparisons), [evidence and playback](factorio-bench-design.md#evidence-playback-and-secrets) |
| Implementation | [Simulator compatibility](factorio-bench-design.md#building-a-compatible-simulator), [milestones and acceptance](factorio-bench-design.md#implementation-milestones-and-acceptance) |

## Repository practices

- [Contributing](../CONTRIBUTING.md): writing, review, validation, and public changes.
- [Data sharing](data-sharing.md): public source, private run evidence, and reviewed exports.
- [Security](../SECURITY.md): credential handling and sensitive issue reporting.
- [Third-party references](../THIRD_PARTY.md): independent implementation, provenance, and game rights.
- [License](../LICENSE) and [notice](../NOTICE): permissions for the project's original work.

Keep design requirements here and implementation instructions alongside the code they describe once that code exists. A new document should state its status, intended reader, and relationship to the main design. Update this index when adding documentation.
