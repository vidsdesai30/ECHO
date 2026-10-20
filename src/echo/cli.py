"""Command-line entry point for the ECHO reconstruction core."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .ingestion import ingest_records, load_json_records
from .reconstruction import ReconstructionConfig, reconstruct
from .scenarios.generator import DegradationConfig, generate_scenario

DESCRIPTION = "Attack Chain Reconstruction Engine for evidence-supported research."


def build_parser() -> argparse.ArgumentParser:
    """Build the service-independent ECHO command-line interface."""
    parser = argparse.ArgumentParser(
        prog="echo",
        description=DESCRIPTION,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"ECHO {__version__}",
    )
    commands = parser.add_subparsers(dest="command")

    generate = commands.add_parser("generate", help="generate a deterministic synthetic scenario")
    generate.add_argument("--output", type=Path, required=True, help="JSON output path")
    generate.add_argument("--seed", type=int, default=7)
    generate.add_argument("--scenario-id", default="scenario-demo")
    generate.add_argument("--missing-rate", type=float, default=0.0)
    generate.add_argument("--duplicate-rate", type=float, default=0.0)
    generate.add_argument("--delayed-rate", type=float, default=0.0)
    generate.add_argument("--missing-attribute-rate", type=float, default=0.0)
    generate.add_argument("--noise-count", type=int, default=1)

    ingest = commands.add_parser("import", help="validate and report on event JSON")
    ingest.add_argument("--input", type=Path, required=True, help="event JSON path")

    reconstruct_command = commands.add_parser("reconstruct", help="reconstruct a graph from event JSON")
    reconstruct_command.add_argument("--input", type=Path, required=True, help="event JSON path")
    reconstruct_command.add_argument("--output", type=Path, help="optional graph JSON output path")
    reconstruct_command.add_argument("--max-gap-seconds", type=int, default=1800)
    reconstruct_command.add_argument("--minimum-score", type=int, default=2)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run a local command and return its process exit code."""
    args = build_parser().parse_args(argv)
    if args.command is None:
        print("ECHO - Attack Chain Reconstruction Engine")
        print(f"Version: {__version__}")
        print("Purpose: reconstruct probable attack chains from imperfect security events.")
        print("Commands: generate, import, reconstruct")
        print("Use --help for command usage.")
        print("The reconstruction engine is implemented for Master Prompt 2.")
        return 0
    try:
        if args.command == "generate":
            return _generate(args)
        if args.command == "import":
            return _import_events(args)
        if args.command == "reconstruct":
            return _reconstruct(args)
    except (OSError, ValueError, TypeError) as exc:
        print(f"ECHO error: {exc}", file=sys.stderr)
        return 2
    return 2


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _generate(args: argparse.Namespace) -> int:
    scenario = generate_scenario(
        seed=args.seed,
        scenario_id=args.scenario_id,
        degradation=DegradationConfig(
            missing_event_rate=args.missing_rate,
            duplicate_rate=args.duplicate_rate,
            delayed_arrival_rate=args.delayed_rate,
            missing_attribute_rate=args.missing_attribute_rate,
            noise_count=args.noise_count,
        ),
    )
    _write_json(args.output, scenario.to_mapping())
    print(f"Generated {len(scenario.observed_events)} observed events at {args.output}")
    print(f"Ground-truth relationships are stored separately in the generated JSON: {len(scenario.ground_truth)}")
    return 0


def _import_events(args: argparse.Namespace) -> int:
    records, _ = load_json_records(args.input)
    report = ingest_records(records)
    print(json.dumps(report.to_mapping(), indent=2, sort_keys=True))
    return 0 if not report.invalid_records else 2


def _reconstruct(args: argparse.Namespace) -> int:
    records, metadata = load_json_records(args.input)
    report = ingest_records(records)
    if report.invalid_records:
        print(json.dumps(report.to_mapping(), indent=2, sort_keys=True), file=sys.stderr)
        return 2
    graph = reconstruct(
        report.events,
        ReconstructionConfig(
            max_event_gap_seconds=args.max_gap_seconds,
            minimum_edge_score=args.minimum_score,
        ),
    )
    payload = {
        "metadata": {key: value for key, value in metadata.items() if key != "ground_truth"},
        "ingestion": report.to_mapping(),
        "graph": graph.to_mapping(),
    }
    if args.output:
        _write_json(args.output, payload)
        print(f"Reconstructed {len(graph.nodes)} nodes and {len(graph.edges)} proposed edges at {args.output}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
