#!/usr/bin/env python3
"""Record experiment commands and outcomes into the local harness."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any


OUTPUT_TAIL_CHARS = 8000


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "experiment"


def repo_root() -> Path:
    # Generated location is harness/scripts/record_experiment.py.
    return Path(__file__).resolve().parents[2]


def clean_stream(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return str(value)


def normalize_command(command: list[str]) -> list[str]:
    if command and command[0] == "--":
        return command[1:]
    return command


def run_command(command: list[str], cwd: Path, timeout: int) -> dict[str, Any]:
    started = now_utc()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout or None,
        )
        return {
            "started": started,
            "ended": now_utc(),
            "exit_code": completed.returncode,
            "stdout": completed.stdout or "",
            "stderr": completed.stderr or "",
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "started": started,
            "ended": now_utc(),
            "exit_code": 124,
            "stdout": clean_stream(exc.stdout),
            "stderr": clean_stream(exc.stderr) + f"\nCommand timed out after {timeout} seconds.",
            "timed_out": True,
        }


def rel_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def write_if_present(path: Path, text: str) -> str:
    if not text:
        return ""
    path.write_text(text, encoding="utf-8")
    return path.name


def append_list(lines: list[str], title: str, values: list[str]) -> None:
    lines.extend([f"## {title}", ""])
    if values:
        lines.extend(f"- {value}" for value in values)
    else:
        lines.append("- Not recorded")
    lines.append("")


def fenced_text(lines: list[str], title: str, value: str) -> None:
    if not value:
        return
    tail = value[-OUTPUT_TAIL_CHARS:]
    if len(value) > OUTPUT_TAIL_CHARS:
        tail = "[truncated to final output]\n" + tail
    fence = "```"
    while fence in tail:
        fence += "`"
    lines.extend([f"### {title}", "", fence + "text", tail.rstrip(), fence, ""])


def single_line(value: str) -> str:
    return " ".join(value.strip().split()) or "Not recorded"


def build_record(
    args: argparse.Namespace,
    root: Path,
    record_id: str,
    record_path: Path,
    stdout_path: Path | None,
    stderr_path: Path | None,
    command_text: str,
    status: str,
    run: dict[str, Any] | None,
) -> str:
    timestamp = now_utc() if run is None else run["started"]
    lines = [
        f"# Experiment: {args.title}",
        "",
        f"- Record ID: `{record_id}`",
        f"- Status: `{status}`",
        f"- Started: `{timestamp.isoformat()}`",
        f"- Record: `{rel_path(record_path, root)}`",
    ]
    if run is not None:
        lines.extend(
            [
                f"- Ended: `{run['ended'].isoformat()}`",
                f"- Exit code: `{run['exit_code']}`",
            ]
        )
    if command_text:
        lines.append(f"- Command: `{command_text}`")
    if args.goal:
        lines.append(f"- Goal: {args.goal}")
    lines.append("")

    append_list(lines, "Parameters", args.param)
    append_list(lines, "Metrics", args.metric)
    append_list(lines, "Artifacts", args.artifact)

    lines.extend(["## Result", "", args.result.strip() or "Not recorded", ""])
    append_list(lines, "Next Steps", args.next_steps)

    if args.notes:
        lines.extend(["## Notes", "", args.notes.strip(), ""])

    if stdout_path or stderr_path:
        lines.extend(["## Captured Output", ""])
        if stdout_path:
            lines.append(f"- Stdout: `{rel_path(stdout_path, root)}`")
        if stderr_path:
            lines.append(f"- Stderr: `{rel_path(stderr_path, root)}`")
        lines.append("")

    if run is not None:
        fenced_text(lines, "Stdout Tail", run["stdout"])
        fenced_text(lines, "Stderr Tail", run["stderr"])

    return "\n".join(lines).rstrip() + "\n"


def append_progress(
    root: Path,
    args: argparse.Namespace,
    record_path: Path,
    command_text: str,
    status: str,
) -> None:
    progress_path = root / "harness" / "plans" / "progress.md"
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    if not progress_path.exists():
        progress_path.write_text("# Agent Progress Log\n", encoding="utf-8")

    entry = [
        "",
        f"## {now_utc().date().isoformat()} Experiment: {args.title}",
        "",
        f"- Status: `{status}`",
        f"- Record: `{rel_path(record_path, root)}`",
        f"- Command: `{command_text or 'not recorded'}`",
        f"- Result: {single_line(args.result)}",
    ]
    if args.metric:
        entry.append(f"- Metrics: {single_line('; '.join(args.metric))}")
    if args.next_steps:
        entry.append(f"- Next: {single_line('; '.join(args.next_steps))}")
    entry.append("")

    with progress_path.open("a", encoding="utf-8") as file:
        file.write("\n".join(entry))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run or summarize an experiment and write a harness verification record.",
    )
    parser.add_argument("--title", required=True, help="Short experiment title.")
    parser.add_argument("--goal", default="", help="What this experiment is checking.")
    parser.add_argument(
        "--status",
        choices=("passed", "failed", "inconclusive", "skipped"),
        default="",
        help="Manual status. If a command is executed, defaults from its exit code.",
    )
    parser.add_argument("--command", default="", help="Command text to record without executing it.")
    parser.add_argument("--param", action="append", default=[], help="Parameter/config item, e.g. lr=0.001.")
    parser.add_argument("--metric", action="append", default=[], help="Metric item, e.g. accuracy=0.91.")
    parser.add_argument("--artifact", action="append", default=[], help="Artifact path or URL.")
    parser.add_argument("--result", default="", help="Result summary or conclusion.")
    parser.add_argument("--next", dest="next_steps", action="append", default=[], help="Follow-up action.")
    parser.add_argument("--notes", default="", help="Additional notes.")
    parser.add_argument("--cwd", default=".", help="Working directory relative to the repository root.")
    parser.add_argument("--timeout", type=int, default=0, help="Optional command timeout in seconds.")
    parser.add_argument("--no-progress", action="store_true", help="Do not append to progress.md.")
    parser.add_argument("run_command", nargs=argparse.REMAINDER, help="Optional command to execute after --.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    command = normalize_command(args.run_command)
    cwd = (root / args.cwd).resolve()
    if command and not cwd.exists():
        print(f"[ERROR] Working directory does not exist: {cwd}", file=sys.stderr)
        return 2

    run = run_command(command, cwd, args.timeout) if command else None
    status = args.status
    if not status:
        if run is None:
            status = "inconclusive"
        else:
            status = "passed" if run["exit_code"] == 0 else "failed"

    command_text = shlex.join(command) if command else args.command.strip()
    created_at = now_utc()
    record_id = f"{created_at.strftime('%Y%m%d-%H%M%S')}-{slugify(args.title)}"
    experiments_dir = root / "harness" / "verification" / "experiments"
    artifacts_dir = experiments_dir / "artifacts"
    experiments_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    stdout_path = None
    stderr_path = None
    if run is not None:
        stdout_name = write_if_present(artifacts_dir / f"{record_id}.stdout.log", run["stdout"])
        stderr_name = write_if_present(artifacts_dir / f"{record_id}.stderr.log", run["stderr"])
        stdout_path = artifacts_dir / stdout_name if stdout_name else None
        stderr_path = artifacts_dir / stderr_name if stderr_name else None

    record_path = experiments_dir / f"{record_id}.md"
    record_text = build_record(
        args=args,
        root=root,
        record_id=record_id,
        record_path=record_path,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        command_text=command_text,
        status=status,
        run=run,
    )
    record_path.write_text(record_text, encoding="utf-8")

    if not args.no_progress:
        append_progress(root, args, record_path, command_text, status)

    print(f"[RECORDED] {rel_path(record_path, root)}")
    if stdout_path:
        print(f"[STDOUT] {rel_path(stdout_path, root)}")
    if stderr_path:
        print(f"[STDERR] {rel_path(stderr_path, root)}")
    if run is not None:
        return int(run["exit_code"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
