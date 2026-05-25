#!/usr/bin/env python3
"""Create a comparison record from harness experiment evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "comparison"


def repo_root() -> Path:
    # Generated location is harness/scripts/compare_experiments.py.
    return Path(__file__).resolve().parents[2]


def rel_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def single_line(value: str) -> str:
    return " ".join(value.strip().split()) or "Not recorded"


def load_index(root: Path) -> list[dict[str, Any]]:
    index_path = root / "harness" / "verification" / "experiments" / "index.jsonl"
    if not index_path.exists():
        return []
    rows = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def resolve_evidence(root: Path, index_rows: list[dict[str, Any]], value: str) -> dict[str, Any]:
    by_record_id = {row.get("record_id"): row for row in index_rows if row.get("record_id")}
    by_path = {row.get("record_path"): row for row in index_rows if row.get("record_path")}
    if value in by_record_id:
        return by_record_id[value]
    if value in by_path:
        return by_path[value]

    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / value
    if candidate.is_dir():
        candidate = candidate / "record.md"
    if candidate.exists():
        relative = rel_path(candidate.resolve(), root)
        if relative in by_path:
            return by_path[relative]
        return {
            "record_id": candidate.stem,
            "title": candidate.stem,
            "status": "unknown",
            "author": "",
            "record_path": relative,
            "metrics": [],
            "metric_map": {},
            "datasets": [],
            "seeds": [],
            "git": {},
            "result": "",
            "reliability_flags": ["Evidence file was not found in experiments/index.jsonl."],
        }

    raise SystemExit(f"[ERROR] Evidence not found by record id or path: {value}")


def markdown_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Evidence | Status | Author | Branch | Commit | Source Dirty | Metrics |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        git = row.get("git") or {}
        metrics = "; ".join(row.get("metrics") or [])
        record = row.get("record_path") or row.get("record_id") or "unknown"
        title = row.get("title") or row.get("record_id") or "unknown"
        link = comparison_relative_link(record, title) if row.get("record_path") else title
        lines.append(
            "| "
            + " | ".join(
                [
                    link,
                    f"`{row.get('status') or 'unknown'}`",
                    row.get("author") or "",
                    f"`{git.get('branch') or 'unknown'}`",
                    f"`{git.get('short_commit') or git.get('commit') or 'unknown'}`",
                    f"`{str(bool(git.get('source_dirty', git.get('dirty')))).lower()}`",
                    metrics or "Not recorded",
                ]
            )
            + " |"
        )
    return lines


def compare_set(rows: list[dict[str, Any]], getter) -> str:
    values = {getter(row) for row in rows if getter(row)}
    if not values:
        return "unknown"
    if len(values) == 1:
        return "yes"
    return "no"


def comparison_relative_link(record_path: str, title: str) -> str:
    if record_path.startswith("harness/verification/experiments/"):
        relative = "../experiments/" + record_path.removeprefix("harness/verification/experiments/")
        return f"[{title}]({relative})"
    return f"[{title}]({record_path})"


def auto_fairness_checks(rows: list[dict[str, Any]]) -> list[str]:
    metric_names = set()
    for row in rows:
        metric_names.update((row.get("metric_map") or {}).keys())
        if not row.get("metric_map"):
            metric_names.update(row.get("metrics") or [])

    dirty_values = [
        bool((row.get("git") or {}).get("source_dirty", (row.get("git") or {}).get("dirty")))
        for row in rows
        if row.get("git")
    ]
    clean = "unknown" if not dirty_values else ("yes" if not any(dirty_values) else "no")

    return [
        f"Same commit: {compare_set(rows, lambda row: (row.get('git') or {}).get('commit'))}",
        f"Same model base: {compare_set(rows, lambda row: (row.get('model_context') or {}).get('model_base'))}",
        f"Same tokenizer: {compare_set(rows, lambda row: (row.get('model_context') or {}).get('tokenizer'))}",
        f"Same train tokens: {compare_set(rows, lambda row: (row.get('model_context') or {}).get('train_tokens'))}",
        f"Same eval suite: {compare_set(rows, lambda row: (row.get('model_context') or {}).get('eval_suite'))}",
        f"Same dataset entries: {compare_set(rows, lambda row: tuple(row.get('datasets') or []))}",
        f"Same seed entries: {compare_set(rows, lambda row: tuple(row.get('seeds') or []))}",
        f"All recorded source worktrees clean: {clean}",
        f"Metric fields present: {', '.join(sorted(metric_names)) if metric_names else 'unknown'}",
    ]


def append_progress(root: Path, args: argparse.Namespace, comparison_path: Path, _evidence: list[dict[str, Any]]) -> None:
    progress_path = root / "harness" / "plans" / "progress.md"
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    if not progress_path.exists():
        progress_path.write_text("# Project Checkpoints\n", encoding="utf-8")

    entry = [
        "",
        f"## {now_utc().date().isoformat()} Checkpoint: {args.title}",
        "",
        "### Summary",
        "",
        f"- Comparison status: `{args.status}`",
        f"- Result: {single_line(args.result)}",
        "",
        "### Links",
        "",
        f"- Comparison: `{rel_path(comparison_path, root)}`",
        f"- Claim: {single_line(args.claim)}",
        "",
    ]
    with progress_path.open("a", encoding="utf-8") as file:
        file.write("\n".join(entry))


def write_comparison(
    root: Path,
    args: argparse.Namespace,
    comparison_id: str,
    comparison_path: Path,
    evidence: list[dict[str, Any]],
) -> str:
    lines = [
        f"# Comparison: {args.title}",
        "",
        f"- Comparison ID: `{comparison_id}`",
        f"- Status: `{args.status}`",
        f"- Created: `{now_utc().isoformat()}`",
        f"- Record: `{rel_path(comparison_path, root)}`",
    ]
    if args.claim:
        lines.append(f"- Claim: {args.claim}")
    lines.append("")

    lines.extend(["## Evidence", ""])
    lines.extend(markdown_table(evidence))
    lines.append("")

    lines.extend(["## Fairness Check", ""])
    lines.extend(f"- {check}" for check in auto_fairness_checks(evidence))
    lines.extend(f"- {note}" for note in args.fairness_note)
    lines.append("")

    lines.extend(["## Comparison Metrics", ""])
    if args.metric:
        lines.extend(f"- {metric}" for metric in args.metric)
    else:
        lines.append("- Not recorded")
    lines.append("")

    lines.extend(["## Result", "", args.result.strip() or "Not recorded", ""])

    if args.note:
        lines.extend(["## Notes", ""])
        lines.extend(f"- {note}" for note in args.note)
        lines.append("")

    lines.extend(["## Evidence Results", ""])
    for row in evidence:
        title = row.get("title") or row.get("record_id") or "unknown"
        result = row.get("result") or "Not recorded"
        lines.extend([f"### {title}", "", result, ""])

    comparison_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return rel_path(comparison_path, root)


def append_index(
    root: Path,
    comparison_id: str,
    args: argparse.Namespace,
    comparison_path: Path,
    evidence: list[dict[str, Any]],
) -> Path:
    index_path = root / "harness" / "verification" / "comparisons" / "index.jsonl"
    row = {
        "schema_version": 1,
        "comparison_id": comparison_id,
        "title": args.title,
        "status": args.status,
        "created_at": now_utc().isoformat(),
        "claim": args.claim,
        "metrics": args.metric,
        "fairness_notes": args.fairness_note,
        "result": args.result,
        "comparison_path": rel_path(comparison_path, root),
        "evidence": [
            {
                "record_id": row.get("record_id"),
                "record_path": row.get("record_path"),
                "status": row.get("status"),
                "author": row.get("author"),
                "commit": (row.get("git") or {}).get("commit"),
                "dirty": (row.get("git") or {}).get("dirty"),
                "source_dirty": (row.get("git") or {}).get("source_dirty"),
            }
            for row in evidence
        ],
    }
    with index_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return index_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a harness comparison from experiment records.")
    parser.add_argument("--title", required=True, help="Short comparison title.")
    parser.add_argument("--claim", default="", help="Claim being evaluated.")
    parser.add_argument(
        "--status",
        choices=("provisional", "reviewed", "rejected"),
        default="provisional",
        help="Review status for this comparison.",
    )
    parser.add_argument("--evidence", action="append", required=True, help="Experiment record id or path.")
    parser.add_argument("--metric", action="append", default=[], help="Comparison metric, e.g. f1_delta=+0.03.")
    parser.add_argument("--fairness-note", action="append", default=[], help="Manual fairness note.")
    parser.add_argument("--result", default="", help="Comparison result or conclusion.")
    parser.add_argument("--note", action="append", default=[], help="Additional note.")
    parser.add_argument(
        "--progress-checkpoint",
        action="store_true",
        help="Append a concise checkpoint to progress.md. Default is to keep progress.md unchanged.",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Deprecated compatibility flag. progress.md is not updated unless --progress-checkpoint is passed.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    comparison_id = f"{now_utc().strftime('%Y%m%d-%H%M%S')}-{slugify(args.title)}"
    comparisons_dir = root / "harness" / "verification" / "comparisons"
    comparisons_dir.mkdir(parents=True, exist_ok=True)
    comparison_path = comparisons_dir / f"{comparison_id}.md"

    index_rows = load_index(root)
    evidence = [resolve_evidence(root, index_rows, item) for item in args.evidence]
    write_comparison(root, args, comparison_id, comparison_path, evidence)
    index_path = append_index(root, comparison_id, args, comparison_path, evidence)

    if args.progress_checkpoint and not args.no_progress:
        append_progress(root, args, comparison_path, evidence)

    print(f"[COMPARISON] {rel_path(comparison_path, root)}")
    print(f"[INDEX] {rel_path(index_path, root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
