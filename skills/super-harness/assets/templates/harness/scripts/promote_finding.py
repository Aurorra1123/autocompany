#!/usr/bin/env python3
"""Promote a reviewed comparison into a durable finding record."""

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
    return slug[:64] or "finding"


def repo_root() -> Path:
    # Generated location is harness/scripts/promote_finding.py.
    return Path(__file__).resolve().parents[2]


def rel_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def single_line(value: str) -> str:
    return " ".join(value.strip().split()) or "Not recorded"


def load_comparison_index(root: Path) -> list[dict[str, Any]]:
    index_path = root / "harness" / "verification" / "comparisons" / "index.jsonl"
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


def resolve_comparison(root: Path, value: str) -> dict[str, Any]:
    rows = load_comparison_index(root)
    by_id = {row.get("comparison_id"): row for row in rows if row.get("comparison_id")}
    by_path = {row.get("comparison_path"): row for row in rows if row.get("comparison_path")}
    if value in by_id:
        return by_id[value]
    if value in by_path:
        return by_path[value]

    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / value
    if candidate.exists():
        relative = rel_path(candidate.resolve(), root)
        if relative in by_path:
            return by_path[relative]
        return {
            "comparison_id": candidate.stem,
            "title": candidate.stem,
            "status": "unknown",
            "comparison_path": relative,
            "evidence": [],
            "claim": "",
            "result": "",
        }

    raise SystemExit(f"[ERROR] Comparison not found by id or path: {value}")


def append_progress(root: Path, args: argparse.Namespace, finding_path: Path) -> None:
    progress_path = root / "harness" / "plans" / "progress.md"
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    if not progress_path.exists():
        progress_path.write_text("# Agent Progress Log\n", encoding="utf-8")

    entry = [
        "",
        f"## {now_utc().date().isoformat()} Finding: {args.title}",
        "",
        f"- Status: `{args.status}`",
        f"- Finding: `{rel_path(finding_path, root)}`",
        f"- Comparison: `{args.comparison}`",
        f"- Conclusion: {single_line(args.conclusion)}",
        "",
    ]
    with progress_path.open("a", encoding="utf-8") as file:
        file.write("\n".join(entry))


def write_finding(
    root: Path,
    args: argparse.Namespace,
    finding_id: str,
    finding_dir: Path,
    comparison: dict[str, Any],
) -> Path:
    finding_path = finding_dir / "finding.md"
    comparison_path = comparison.get("comparison_path") or args.comparison
    lines = [
        f"# Finding: {args.title}",
        "",
        f"- Finding ID: `{finding_id}`",
        f"- Status: `{args.status}`",
        f"- Created: `{now_utc().isoformat()}`",
        f"- Comparison: `{comparison_path}`",
        f"- Comparison status: `{comparison.get('status') or 'unknown'}`",
    ]
    if args.reviewer:
        lines.extend(f"- Reviewer: {reviewer}" for reviewer in args.reviewer)
    if args.owner:
        lines.append(f"- Owner: {args.owner}")
    lines.append("")

    lines.extend(["## Claim", "", args.claim or comparison.get("claim") or "Not recorded", ""])
    lines.extend(["## Conclusion", "", args.conclusion or comparison.get("result") or "Not recorded", ""])

    lines.extend(["## Evidence", ""])
    evidence = comparison.get("evidence") or []
    if evidence:
        for item in evidence:
            record_id = item.get("record_id") or "unknown"
            record_path = item.get("record_path") or ""
            if record_path:
                lines.append(f"- `{record_id}`: `{record_path}`")
            else:
                lines.append(f"- `{record_id}`")
    else:
        lines.append("- Not recorded")
    lines.append("")

    lines.extend(["## Limitations", ""])
    if args.limitation:
        lines.extend(f"- {item}" for item in args.limitation)
    else:
        lines.append("- Not recorded")
    lines.append("")

    if args.note:
        lines.extend(["## Notes", ""])
        lines.extend(f"- {item}" for item in args.note)
        lines.append("")

    finding_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return finding_path


def append_index(
    root: Path,
    args: argparse.Namespace,
    finding_id: str,
    finding_path: Path,
    comparison: dict[str, Any],
) -> Path:
    index_path = root / "harness" / "verification" / "findings" / "index.jsonl"
    row = {
        "schema_version": 1,
        "finding_id": finding_id,
        "title": args.title,
        "status": args.status,
        "created_at": now_utc().isoformat(),
        "claim": args.claim or comparison.get("claim") or "",
        "conclusion": args.conclusion or comparison.get("result") or "",
        "comparison_id": comparison.get("comparison_id") or "",
        "comparison_path": comparison.get("comparison_path") or args.comparison,
        "finding_path": rel_path(finding_path, root),
        "reviewers": args.reviewer,
        "owner": args.owner,
        "limitations": args.limitation,
        "evidence": comparison.get("evidence") or [],
    }
    with index_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return index_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Promote a comparison into a durable reviewed finding.")
    parser.add_argument("--title", required=True, help="Short finding title.")
    parser.add_argument("--comparison", required=True, help="Comparison id or path.")
    parser.add_argument(
        "--status",
        choices=("provisional", "reviewed", "rejected", "superseded"),
        default="reviewed",
        help="Finding governance status.",
    )
    parser.add_argument("--claim", default="", help="Claim to preserve. Defaults from comparison when omitted.")
    parser.add_argument("--conclusion", default="", help="Reviewed conclusion. Defaults from comparison when omitted.")
    parser.add_argument("--reviewer", action="append", default=[], help="Reviewer name/email.")
    parser.add_argument("--owner", default="", help="Finding owner.")
    parser.add_argument("--limitation", action="append", default=[], help="Known limitation.")
    parser.add_argument("--note", action="append", default=[], help="Additional note.")
    parser.add_argument(
        "--allow-provisional-comparison",
        action="store_true",
        help="Allow a reviewed finding from a non-reviewed comparison. Use only with explicit reviewer approval.",
    )
    parser.add_argument("--no-progress", action="store_true", help="Do not append to progress.md.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    comparison = resolve_comparison(root, args.comparison)
    if (
        args.status == "reviewed"
        and comparison.get("status") != "reviewed"
        and not args.allow_provisional_comparison
    ):
        print(
            "[ERROR] Reviewed findings require a reviewed comparison. "
            "Pass --allow-provisional-comparison only when reviewers explicitly accept this.",
            file=sys.stderr,
        )
        return 2
    finding_id = f"{now_utc().strftime('%Y%m%d-%H%M%S')}-{slugify(args.title)}"
    finding_dir = root / "harness" / "verification" / "findings" / finding_id
    finding_dir.mkdir(parents=True, exist_ok=True)
    finding_path = write_finding(root, args, finding_id, finding_dir, comparison)
    index_path = append_index(root, args, finding_id, finding_path, comparison)

    if not args.no_progress:
        append_progress(root, args, finding_path)

    print(f"[FINDING] {rel_path(finding_path, root)}")
    print(f"[INDEX] {rel_path(index_path, root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
