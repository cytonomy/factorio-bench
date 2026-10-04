# Explore the evidence demo

**Status:** runnable synthetic examples, with an original schematic viewer. No game, simulator, or AI model is run. The examples explain the proposed evaluation contract; they are not benchmark results or evidence of Factorio compatibility.

This guide is for readers who want to see how a successful factory and two failure cases would be judged. Read the [environment design](factorio-bench-design.md) for the proposed native integration and its acceptance criteria.

## Run the examples

From the repository root, with Python 3.9 or later:

```sh
make examples
```

The script authors three deterministic traces, calculates their outcomes from the events, and writes [the viewer fixture](../showcase/data/examples.json). It has no third-party dependencies, uses no credentials, and makes no network requests.

```text
Synthetic illustration — no game or model was run.
steady-line: PASS (5/5 windows; 208 qualifying deliveries)
fuel-starved: FAIL (2/5 windows; 94 qualifying deliveries)
hand-fed: FAIL (0/5 windows; 40 qualifying deliveries)
Wrote showcase/data/examples.json
```

To verify the checked-in fixture without changing it:

```sh
python3 -B scripts/run_examples.py --check
```

To open the local viewer:

```sh
make demo
```

Open `http://127.0.0.1:8765` in a browser. The server binds to loopback and exposes only the showcase files on its allowlist. Stop it with Ctrl+C when finished. If port 8765 is busy, run `python3 scripts/serve_demo.py --port 8766` and use that port in the browser.

## Three scenarios, one contract

| Scenario | Qualifying deliveries | Passing windows | What it illustrates |
| --- | ---: | ---: | --- |
| The steady line | 208 | 5 / 5 | Sustained useful output after handoff |
| The fading furnace | 94 | 2 / 5 | An early success cannot compensate for later failure |
| The hand-fed shortcut | 40 | 0 / 5 | Player deposits do not count as automated delivery |

The evaluation covers ticks 54,000 through 71,999: five windows of 3,600 ticks. Each window requires at least 30 units mined, 30 smelted, and 30 delivered by the synthetic inserter source, plus a positive power-availability marker and no manual deposits. A case passes only when all five windows pass. A tick on a window boundary belongs to the following window; tick 72,000 is outside the evaluation.

The hand-fed case includes another 160 units deposited by the synthetic player source. These remain visible in the evidence but cannot increase the qualifying delivery counter. A manual deposit also fails that window's hands-off condition even if automated production is sufficient.

## What is implemented

The [generator and verifier](../scripts/run_examples.py) are separate functions. The generator authors events; the verifier derives counters and verdicts from those events without consulting scenario titles, descriptions, or expected outcomes. The checked-in JSON contains both the events and those derived values so the viewer can display a small, reproducible artifact.

The verifier checks unique event identifiers, ordered integer ticks, evaluation boundaries, expected source labels, integer quantities, and cumulative material balance along the mined → smelted → delivered chain. Repeated event identifiers are rejected, rather than counted twice. Each window may have one power marker at its start; a missing or zero marker fails that window. [Regression tests](../tests/test_examples.py) cover these boundaries, manual intervention, and production spikes that hide later failures.

## What the demo does not establish

These traces are authored examples, not a simulation of Factorio. The schematic has original graphics and makes no claim about actual machine placement, reach, recipe timing, resource consumption, transport, fuel, power, or game physics. Tick spacing is chosen for readable playback. The power marker is an authored availability flag, not continuous telemetry.

Event source names are validated labels inside a local fixture; they do not authenticate their origin. A native benchmark will need evidence collected across a trusted game boundary, reconciled action receipts, verified inventory transitions, and independent scoring. A matching string such as `inserter` is not sufficient proof of native behavior.

The fuel-shortage explanation is scenario metadata supplied by the author. The counters show declining smelting while mining continues; they cannot independently prove why it happened. No agent performance, model ranking, native compatibility, or speed comparison can be inferred from these examples.

## Publishing example visuals

Screenshots of this synthetic viewer are illustrations of the implemented viewer. Keep the synthetic provenance label visible and use an image caption that says what is shown. Review the complete image before publishing it. Game captures, account chrome, local terminal output, and private run evidence are outside this example's publication scope; follow the [sharing policy](data-sharing.md) for other exports.

## Check the viewer

The viewer uses plain HTML, CSS, JavaScript, and original SVG artwork. It has no package installation, external fonts, analytics, or remote data calls. To review a UI change:

1. Switch through all three scenarios and compare the verdict, five-window chart, and event ledger with `make examples`.
2. Select windows with the slider, arrow keys, and chart buttons. Confirm that counts and tick intervals change together.
3. Play, pause, and replay the sequence. Playback should stop at window 5; choosing another scenario should reset it.
4. Check narrow and wide screens. The initial showcase was exercised at 320, 390, 768, 1024, and 1440 pixels with no horizontal overflow.
5. Enable reduced motion and check keyboard focus. The conveyor animation should stop; controls and the ledger should remain usable.

The reviewed [desktop](assets/showcase-desktop.png) and [mobile](assets/showcase-mobile.png) captures show the steady-line and fuel-starved examples respectively. See the [media guide](assets/README.md) before replacing them.
