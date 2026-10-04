#!/usr/bin/env python3
"""Generate and independently score original, synthetic demonstration evidence."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "showcase" / "data" / "examples.json"
TASK = {
    "id": "iron-bootstrap",
    "evaluation_start_tick": 54000,
    "evaluation_end_tick": 72000,
    "window_ticks": 3600,
    "minimum_per_window": 30,
}
SOURCES = {
    "mine": "electric-drill",
    "smelt": "furnace",
    "deliver": "inserter",
    "manual-deliver": "player",
    "power": "grid",
}
COUNTERS = {
    "mine": "mined", "smelt": "smelted", "deliver": "delivered",
    "manual-deliver": "manual_delivered",
}


def verify(events):
    """Validate a toy trace and derive its verdict without consulting case metadata.

    Source names are fixture labels, not an authentication mechanism. A native
    implementation will need independent, trusted observation of the game.
    """
    start, end = TASK["evaluation_start_tick"], TASK["evaluation_end_tick"]
    width, minimum = TASK["window_ticks"], TASK["minimum_per_window"]
    windows = [
        {
            "index": index + 1,
            "start_tick": tick,
            "end_tick": tick + width,
            "mined": 0,
            "smelted": 0,
            "delivered": 0,
            "manual_delivered": 0,
            "powered": False,
        }
        for index, tick in enumerate(range(start, end, width))
    ]
    totals = {counter: 0 for counter in COUNTERS.values()}
    seen, power_windows = set(), set()
    previous_tick = start
    for event in events:
        if not isinstance(event, dict) or set(event) != {"id", "tick", "kind", "quantity", "source"}:
            raise ValueError("Every event must have the five defined evidence fields.")
        identifier, tick = event["id"], event["tick"]
        kind, quantity, source = event["kind"], event["quantity"], event["source"]
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("Evidence identifiers must be nonempty and unique.")
        if type(tick) is not int or not start <= tick < end or tick < previous_tick:
            raise ValueError("Evidence must be ordered and inside the half-open evaluation horizon.")
        if not isinstance(kind, str) or kind not in SOURCES or source != SOURCES[kind]:
            raise ValueError("Unknown event kind or unexpected source label.")
        if type(quantity) is not int or (quantity not in (0, 1) if kind == "power" else quantity <= 0):
            raise ValueError("Material quantities must be positive integers; power markers are zero or one.")
        seen.add(identifier)
        previous_tick = tick
        index = (tick - start) // width
        window = windows[index]
        if kind == "power":
            if tick != window["start_tick"] or index in power_windows:
                raise ValueError("At most one power marker is permitted at each window start.")
            power_windows.add(index)
            window["powered"] = quantity == 1
        else:
            counter = COUNTERS[kind]
            window[counter] += quantity
            totals[counter] += quantity
            if not totals["delivered"] <= totals["smelted"] <= totals["mined"]:
                raise ValueError("The synthetic material chain cannot consume future production.")
    for window in windows:
        window["passed"] = window["powered"] and window["manual_delivered"] == 0 and all(
            window[counter] >= minimum for counter in ("mined", "smelted", "delivered")
        )
    return {
        "verdict": "pass" if all(window["passed"] for window in windows) else "fail",
        "windows": windows,
        "events": events,
        "totals": totals,
    }


def trace(case_id, amounts):
    """Author a small deterministic fixture; no world simulation is performed."""
    events = []

    def append(tick, kind, quantity):
        events.append({
            "id": f"{case_id}-{len(events) + 1:03d}",
            "tick": tick, "kind": kind, "quantity": quantity,
            "source": SOURCES[kind],
        })

    for index, (mined, smelted, delivered, manual) in enumerate(amounts):
        start = TASK["evaluation_start_tick"] + index * TASK["window_ticks"]
        append(start, "power", 1)
        # Four ordered batches make progression visible without pretending to
        # implement Factorio's recipes, movement, machine rates or energy model.
        for batch in range(4):
            for offset, (kind, total) in enumerate(zip(COUNTERS, (mined, smelted, delivered, manual))):
                quotient, remainder = divmod(total, 4)
                quantity = quotient + (batch < remainder)
                if quantity:
                    append(start + 300 + batch * 800 + offset * 80, kind, quantity)
    return events


def build_examples():
    cases = [
        {
            "id": "steady-line", "title": "The steady line",
            "subtitle": "Production holds after handoff.",
            "description": "An authored trace of a balanced ore-to-plate line. Every evaluation window clears all three output thresholds.",
            "diagnosis": "The line sustains useful output in all five windows. Passing is based on each window, so a brief production spike cannot carry the result.",
            "amounts": [(value, value, value, 0) for value in (40, 42, 40, 44, 42)],
        },
        {
            "id": "fuel-starved", "title": "The fading furnace",
            "subtitle": "A strong start hides a supply failure.",
            "description": "An authored fuel-shortage scenario: mining continues while furnace output declines. The first two windows pass; the remaining three fail.",
            "diagnosis": "Smelting falls below the threshold in window 3, then stops. The fuel-shortage explanation is part of the authored scenario; these counters alone do not prove its cause.",
            "amounts": [(40, value, value, 0) for value in (40, 38, 16, 0, 0)],
        },
        {
            "id": "hand-fed", "title": "The hand-fed shortcut",
            "subtitle": "A full chest does not prove automation.",
            "description": "An adversarial authored trace adds player deposits to a weak delivery line. The total stock looks healthy, but only inserter transfers count toward automated delivery.",
            "diagnosis": "Each window has only 8 qualifying deliveries. The 32 manual deposits are shown separately and excluded from the delivery score; they cannot turn a failing line into a pass.",
            "amounts": [(40, 40, 8, 32)] * 5,
        },
    ]
    for case in cases:
        amounts = case.pop("amounts")
        case.update(verify(trace(case["id"], amounts)))
    return {
        "schema_version": "factorio-bench.demo.v1",
        "provenance": "Synthetic illustration — no game or model was run.",
        "task": TASK,
        "cases": cases,
    }


def serialized_examples():
    return json.dumps(build_examples(), indent=2, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the checked-in fixture matches the generator")
    arguments = parser.parse_args()
    expected = serialized_examples()
    if arguments.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            parser.exit(1, "Synthetic examples are missing or stale; run python3 scripts/run_examples.py.\n")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected, encoding="utf-8")
    print("Synthetic illustration — no game or model was run.")
    for case in build_examples()["cases"]:
        passing = sum(window["passed"] for window in case["windows"])
        print(f"{case['id']}: {case['verdict'].upper()} ({passing}/5 windows; {case['totals']['delivered']} qualifying deliveries)")
    print("Checked showcase/data/examples.json" if arguments.check else "Wrote showcase/data/examples.json")


if __name__ == "__main__":
    main()
