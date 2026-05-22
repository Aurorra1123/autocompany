#!/usr/bin/env python3
"""Record experiment commands and outcomes into the local harness."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import shlex
import subprocess
import sys
from typing import Any


OUTPUT_TAIL_CHARS = 8000
HARNESS_RECORD_PREFIXES = (
    "harness/verification/",
    "harness/plans/progress.md",
)


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


def run_quiet(command: list[str], cwd: Path) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.rstrip("\n")


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


def parse_pairs(values: list[str]) -> dict[str, str]:
    parsed = {}
    for value in values:
        if "=" not in value:
            continue
        key, raw = value.split("=", 1)
        key = key.strip()
        if key:
            parsed[key] = raw.strip()
    return parsed


def status_path(line: str) -> str:
    raw_path = line[3:].strip() if len(line) > 3 else ""
    if " -> " in raw_path:
        return raw_path.split(" -> ", 1)[1]
    return raw_path


def source_status(status_short: str) -> str:
    lines = []
    for line in status_short.splitlines():
        path = status_path(line)
        if any(path.startswith(prefix) for prefix in HARNESS_RECORD_PREFIXES):
            continue
        lines.append(line)
    return "\n".join(lines)


def git_metadata(root: Path) -> dict[str, Any]:
    status_short = run_quiet(["git", "status", "--short"], root)
    source_status_short = source_status(status_short)
    return {
        "branch": run_quiet(["git", "rev-parse", "--abbrev-ref", "HEAD"], root),
        "commit": run_quiet(["git", "rev-parse", "HEAD"], root),
        "short_commit": run_quiet(["git", "rev-parse", "--short", "HEAD"], root),
        "remote_origin": run_quiet(["git", "remote", "get-url", "origin"], root),
        "author_name": run_quiet(["git", "config", "user.name"], root),
        "author_email": run_quiet(["git", "config", "user.email"], root),
        "dirty": bool(status_short),
        "source_dirty": bool(source_status_short),
        "status_short": status_short,
        "source_status_short": source_status_short,
    }


def environment_metadata(cwd: Path) -> dict[str, str]:
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "user": os.environ.get("USER") or os.environ.get("USERNAME") or "",
        "cwd": str(cwd),
    }


def format_author(args: argparse.Namespace, git: dict[str, Any], env: dict[str, str]) -> str:
    if args.author:
        return args.author
    name = git.get("author_name") or env.get("user") or "unknown"
    email = git.get("author_email")
    if email:
        return f"{name} <{email}>"
    return name


def reliability_flags(git: dict[str, Any], args: argparse.Namespace) -> list[str]:
    flags = []
    if not git.get("commit"):
        flags.append("Git commit was not detected; reproducibility is weaker.")
    if git.get("source_dirty"):
        flags.append("Source worktree had uncommitted or untracked non-harness changes when recorded.")
    elif git.get("dirty"):
        flags.append("Only harness progress/verification records were dirty when recorded.")
    if not args.dataset:
        flags.append("Dataset/source version was not recorded.")
    if not args.seed:
        flags.append("Seed was not recorded.")
    return flags


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
    git: dict[str, Any],
    env: dict[str, str],
    author: str,
) -> str:
    timestamp = now_utc() if run is None else run["started"]
    lines = [
        f"# Experiment: {args.title}",
        "",
        f"- Record ID: `{record_id}`",
        f"- Status: `{status}`",
        f"- Author: {author}",
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
    if args.claim:
        lines.append(f"- Supported claim: {args.claim}")
    lines.append("")

    lines.extend(
        [
            "## Provenance",
            "",
            f"- Branch: `{git.get('branch') or 'unknown'}`",
            f"- Commit: `{git.get('commit') or 'unknown'}`",
            f"- Dirty worktree: `{str(bool(git.get('dirty'))).lower()}`",
            f"- Source dirty: `{str(bool(git.get('source_dirty'))).lower()}`",
            f"- Remote: `{git.get('remote_origin') or 'unknown'}`",
            f"- Host: `{env.get('hostname') or 'unknown'}`",
            f"- Platform: `{env.get('platform') or 'unknown'}`",
            f"- Python: `{env.get('python') or 'unknown'}`",
            f"- CWD: `{env.get('cwd') or 'unknown'}`",
            "",
        ]
    )
    fenced_text(lines, "Git Status", git.get("status_short", ""))
    fenced_text(lines, "Source Git Status", git.get("source_status_short", ""))

    flags = reliability_flags(git, args)
    lines.extend(["## Reliability Flags", ""])
    if flags:
        lines.extend(f"- {flag}" for flag in flags)
    else:
        lines.append("- No automatic flags")
    lines.append("")

    append_list(lines, "Parameters", args.param)
    append_list(lines, "Datasets", args.dataset)
    append_list(lines, "Seeds", args.seed)
    append_list(lines, "Metrics", args.metric)
    append_list(lines, "Artifacts", args.artifact)
    append_list(lines, "Tags", args.tag)
    append_list(lines, "Fairness Notes", args.fairness_note)

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


def build_index_row(
    args: argparse.Namespace,
    root: Path,
    record_id: str,
    record_path: Path,
    stdout_path: Path | None,
    stderr_path: Path | None,
    command_text: str,
    status: str,
    run: dict[str, Any] | None,
    git: dict[str, Any],
    env: dict[str, str],
    author: str,
) -> dict[str, Any]:
    started = now_utc() if run is None else run["started"]
    ended = None if run is None else run["ended"]
    return {
        "schema_version": 1,
        "record_id": record_id,
        "title": args.title,
        "status": status,
        "author": author,
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat() if ended else "",
        "exit_code": "" if run is None else run["exit_code"],
        "command": command_text,
        "goal": args.goal,
        "claim": args.claim,
        "params": args.param,
        "param_map": parse_pairs(args.param),
        "datasets": args.dataset,
        "seeds": args.seed,
        "metrics": args.metric,
        "metric_map": parse_pairs(args.metric),
        "artifacts": args.artifact,
        "tags": args.tag,
        "fairness_notes": args.fairness_note,
        "result": args.result,
        "next_steps": args.next_steps,
        "record_path": rel_path(record_path, root),
        "stdout_path": rel_path(stdout_path, root) if stdout_path else "",
        "stderr_path": rel_path(stderr_path, root) if stderr_path else "",
        "git": git,
        "environment": env,
        "reliability_flags": reliability_flags(git, args),
    }


def append_index(root: Path, row: dict[str, Any]) -> Path:
    index_path = root / "harness" / "verification" / "experiments" / "index.jsonl"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return index_path


def append_progress(
    root: Path,
    args: argparse.Namespace,
    record_path: Path,
    command_text: str,
    status: str,
    git: dict[str, Any],
    author: str,
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
        f"- Author: {author}",
        f"- Record: `{rel_path(record_path, root)}`",
        f"- Branch: `{git.get('branch') or 'unknown'}`",
        f"- Commit: `{git.get('short_commit') or git.get('commit') or 'unknown'}`",
        f"- Dirty worktree: `{str(bool(git.get('dirty'))).lower()}`",
        f"- Source dirty: `{str(bool(git.get('source_dirty'))).lower()}`",
        f"- Command: `{command_text or 'not recorded'}`",
        f"- Result: {single_line(args.result)}",
    ]
    if args.metric:
        entry.append(f"- Metrics: {single_line('; '.join(args.metric))}")
    if args.dataset:
        entry.append(f"- Datasets: {single_line('; '.join(args.dataset))}")
    if args.seed:
        entry.append(f"- Seeds: {single_line('; '.join(args.seed))}")
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
    parser.add_argument("--claim", default="", help="Claim or comparison hypothesis this experiment supports.")
    parser.add_argument("--author", default="", help="Override author, e.g. Name <email>.")
    parser.add_argument(
        "--status",
        choices=("passed", "failed", "inconclusive", "skipped"),
        default="",
        help="Manual status. If a command is executed, defaults from its exit code.",
    )
    parser.add_argument("--command", default="", help="Command text to record without executing it.")
    parser.add_argument("--param", action="append", default=[], help="Parameter/config item, e.g. lr=0.001.")
    parser.add_argument("--dataset", action="append", default=[], help="Dataset/source version, e.g. dataset=v2.")
    parser.add_argument("--seed", action="append", default=[], help="Random seed or split identifier.")
    parser.add_argument("--metric", action="append", default=[], help="Metric item, e.g. accuracy=0.91.")
    parser.add_argument("--artifact", action="append", default=[], help="Artifact path or URL.")
    parser.add_argument("--tag", action="append", default=[], help="Free-form tag for later grouping.")
    parser.add_argument("--fairness-note", action="append", default=[], help="Fairness/reproducibility note.")
    parser.add_argument("--result", default="", help="Result summary or conclusion.")
    parser.add_argument("--next", dest="next_steps", action="append", default=[], help="Follow-up action.")
    parser.add_argument("--notes", default="", help="Additional notes.")
    parser.add_argument("--cwd", default=".", help="Working directory relative to the repository root.")
    parser.add_argument("--timeout", type=int, default=0, help="Optional command timeout in seconds.")
    parser.add_argument("--no-index", action="store_true", help="Do not append to experiments/index.jsonl.")
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

    git = git_metadata(root)
    env = environment_metadata(cwd)
    author = format_author(args, git, env)

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
        git=git,
        env=env,
        author=author,
    )
    record_path.write_text(record_text, encoding="utf-8")

    index_path = None
    if not args.no_index:
        row = build_index_row(
            args=args,
            root=root,
            record_id=record_id,
            record_path=record_path,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            command_text=command_text,
            status=status,
            run=run,
            git=git,
            env=env,
            author=author,
        )
        index_path = append_index(root, row)

    if not args.no_progress:
        append_progress(root, args, record_path, command_text, status, git, author)

    print(f"[RECORDED] {rel_path(record_path, root)}")
    if index_path:
        print(f"[INDEX] {rel_path(index_path, root)}")
    if stdout_path:
        print(f"[STDOUT] {rel_path(stdout_path, root)}")
    if stderr_path:
        print(f"[STDERR] {rel_path(stderr_path, root)}")
    if run is not None:
        return int(run["exit_code"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
