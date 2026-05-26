#!/usr/bin/env python3
"""Archive a verbose progress.md and replace it with a concise checkpoint."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys


PROGRESS_INTRO = """# Project Checkpoints

本文件是高层 checkpoint / handoff log，不是完整活动流水账。详细实验、命令输出、参数、指标和过程日志应放在 `verification/`、`architecture/adr/` 或 `reference/`，这里只保留短摘要和链接。

## 写入标准

只有满足下面任一条件时才更新：

- onboarding、milestone 或阶段性交接完成
- 一组实验、comparison 或 reviewed finding 改变了后续判断
- 项目方向、优先级、核心假设、blocker、risk 或 open question 发生变化
- 会话结束时下个 contributor/agent 需要快速恢复主线
"""


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def repo_root() -> Path:
    # Generated location is harness/scripts/compact_progress.py.
    return Path(__file__).resolve().parents[2]


def rel_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def single_line(value: str) -> str:
    return " ".join(value.strip().split())


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise SystemExit(f"[ERROR] Could not find a free archive path near {path}")


def parse_link(value: str) -> tuple[str, str]:
    if "=" in value:
        label, target = value.split("=", 1)
        label = single_line(label)
        target = single_line(target)
        if label and target:
            return label, target
    target = single_line(value)
    if not target:
        raise SystemExit("[ERROR] --link values must not be empty.")
    return "Evidence", target


def default_links(root: Path, archive_path: Path) -> list[tuple[str, str]]:
    links = [("Legacy progress archive", rel_path(archive_path, root))]
    candidates = [
        ("Project brief", root / "harness" / "project" / "brief.md"),
        ("Idea index", root / "harness" / "ideas" / "index.jsonl"),
        ("Task list", root / "harness" / "plans" / "feature-list.json"),
        ("Experiment index", root / "harness" / "verification" / "experiments" / "index.jsonl"),
        ("Comparison index", root / "harness" / "verification" / "comparisons" / "index.jsonl"),
        ("Finding index", root / "harness" / "verification" / "findings" / "index.jsonl"),
    ]
    for label, path in candidates:
        if path.exists():
            links.append((label, rel_path(path, root)))
    return links


def archive_text(original: str, source_rel: str, archived_at: str, reason: str) -> str:
    digest = hashlib.sha256(original.encode("utf-8")).hexdigest()
    line_count = len(original.splitlines())
    return "\n".join(
        [
            "# Legacy Progress Archive",
            "",
            f"- Source: `{source_rel}`",
            f"- Archived at: `{archived_at}`",
            f"- SHA256: `{digest}`",
            f"- Lines: `{line_count}`",
            f"- Reason: {single_line(reason) or 'Progress compaction'}",
            "",
            "## How To Use This Archive",
            "",
            "- Treat this file as historical source material, not current project truth.",
            "- Promote durable conclusions into `harness/verification/findings/` after review.",
            "- Move reproducibility details into experiment, comparison, ADR, or reference records instead of copying them back into `progress.md`.",
            "",
            "## Original Progress Content",
            "",
            original.rstrip(),
            "",
        ]
    )


def progress_text(root: Path, archive_path: Path, args: argparse.Namespace) -> str:
    date = now_utc().date().isoformat()
    title = single_line(args.checkpoint_title)
    summary = [single_line(item) for item in args.summary if single_line(item)]
    if not summary:
        summary = [
            "Archived the previous verbose progress log and reset this file to concise checkpoint format.",
            "Use linked evidence files for details; keep future entries short and reviewable.",
        ]

    links = default_links(root, archive_path)
    links.extend(parse_link(item) for item in args.link)

    next_items = [single_line(item) for item in args.next if single_line(item)]
    if not next_items:
        next_items = [
            "Review the archive and promote stable conclusions to findings, ADRs, or comparison records.",
            "Keep future `progress.md` updates limited to milestones, handoffs, blockers, and direction changes.",
        ]

    questions = [single_line(item) for item in args.open_question if single_line(item)]
    if not questions:
        questions = ["Which legacy notes are reviewed enough to become durable findings or ADRs?"]

    lines = [
        PROGRESS_INTRO.rstrip(),
        "",
        f"## {date} Checkpoint: {title}",
        "",
        "### Summary",
        "",
    ]
    lines.extend(f"- {item}" for item in summary)
    lines.extend(["", "### Evidence Links", ""])
    lines.extend(f"- {label}: `{target}`" for label, target in links)
    lines.extend(["", "### Next", ""])
    lines.extend(f"{index}. {item}" for index, item in enumerate(next_items, 1))
    lines.extend(["", "### Open Questions", ""])
    lines.extend(f"- {item}" for item in questions)
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Archive a verbose harness progress.md and replace it with a concise checkpoint log.",
    )
    parser.add_argument(
        "--checkpoint-title",
        default="progress compacted",
        help="Title for the replacement checkpoint entry.",
    )
    parser.add_argument(
        "--summary",
        action="append",
        default=[],
        help="Summary bullet for the replacement checkpoint. May be repeated.",
    )
    parser.add_argument(
        "--next",
        action="append",
        default=[],
        help="Next-step item for the replacement checkpoint. May be repeated.",
    )
    parser.add_argument(
        "--open-question",
        action="append",
        default=[],
        help="Open question for the replacement checkpoint. May be repeated.",
    )
    parser.add_argument(
        "--link",
        action="append",
        default=[],
        help="Extra evidence link as LABEL=path or path. May be repeated.",
    )
    parser.add_argument(
        "--archive-name",
        help="Archive filename under harness/reference/. Defaults to legacy-progress-<timestamp>.md.",
    )
    parser.add_argument(
        "--reason",
        default="Compacted progress.md into checkpoint format.",
        help="Reason recorded in the archive metadata.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned paths and replacement preview without writing.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = repo_root()
    progress_path = root / "harness" / "plans" / "progress.md"
    reference_dir = root / "harness" / "reference"

    if not progress_path.exists():
        print(f"[ERROR] Missing progress file: {rel_path(progress_path, root)}")
        return 1

    archive_name = args.archive_name
    if archive_name:
        if "/" in archive_name or "\\" in archive_name:
            print("[ERROR] --archive-name must be a filename, not a path.")
            return 1
        if not archive_name.endswith(".md"):
            archive_name = f"{archive_name}.md"
    else:
        stamp = now_utc().strftime("%Y%m%d-%H%M%S")
        archive_name = f"legacy-progress-{stamp}.md"

    archive_path = unique_path(reference_dir / archive_name)
    original = progress_path.read_text(encoding="utf-8")
    archived_at = now_utc().isoformat(timespec="seconds")
    replacement = progress_text(root, archive_path, args)
    archive = archive_text(original, rel_path(progress_path, root), archived_at, args.reason)

    print(f"[ARCHIVE] {rel_path(progress_path, root)} -> {rel_path(archive_path, root)}")
    print(f"[REWRITE] {rel_path(progress_path, root)}")
    if args.dry_run:
        print()
        print("[DRY-RUN] Replacement preview:")
        print(replacement)
        return 0

    reference_dir.mkdir(parents=True, exist_ok=True)
    archive_path.write_text(archive, encoding="utf-8")
    progress_path.write_text(replacement, encoding="utf-8")
    print("[DONE] progress.md compacted. Review the archive before promoting legacy conclusions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
