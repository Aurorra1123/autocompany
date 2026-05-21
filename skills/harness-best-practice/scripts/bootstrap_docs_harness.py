#!/usr/bin/env python3
"""Bootstrap a repository-local docs harness scaffold."""

import argparse
from datetime import date
from pathlib import Path
import sys
from typing import NamedTuple


class TemplateOp(NamedTuple):
    source: str
    target: str
    condition: str = "always"


TEMPLATE_OPS = (
    TemplateOp("AGENTS.md", "AGENTS.md", "if_missing"),
    TemplateOp("docs/README.md", "docs/README.md"),
    TemplateOp("docs/plans/feature-list.json", "docs/plans/feature-list.json"),
    TemplateOp("docs/progress/agent-progress.md", "docs/progress/agent-progress.md"),
    TemplateOp("docs/standards/engineering-rules.md", "docs/standards/engineering-rules.md"),
    TemplateOp("docs/standards/git-workflow.md", "docs/standards/git-workflow.md"),
    TemplateOp(
        "docs/standards/agent-harness-rules.md",
        "docs/standards/agent-harness-rules.md",
    ),
    TemplateOp(
        "docs/standards/deployment-baseline.md",
        "docs/standards/deployment-baseline.md",
    ),
    TemplateOp("docs/adr/README.md", "docs/adr/README.md"),
    TemplateOp(
        "docs/adr/0001-repo-as-agent-memory.md",
        "docs/adr/0001-repo-as-agent-memory.md",
    ),
    TemplateOp(
        "docs/adr/0002-harness-first-agent-workflow.md",
        "docs/adr/0002-harness-first-agent-workflow.md",
    ),
    TemplateOp("docs/architecture/README.md", "docs/architecture/README.md"),
    TemplateOp("docs/verification/README.md", "docs/verification/README.md"),
    TemplateOp("docs/exec-plan/README.md", "docs/exec-plan/README.md"),
    TemplateOp("docs/reference/README.md", "docs/reference/README.md"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bootstrap a docs harness scaffold into a target repository.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--project-name",
        help="Project name used in template placeholders. Defaults to the target directory name.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing target files instead of skipping them.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned operations without writing files.",
    )
    parser.add_argument(
        "--skip-agents",
        action="store_true",
        help="Do not create AGENTS.md even if it is missing.",
    )
    return parser


def render_template(raw_text: str, project_name: str, today: str) -> str:
    return raw_text.replace("{{PROJECT_NAME}}", project_name).replace("{{TODAY}}", today)


def load_template(source_root: Path, relative_path: str, project_name: str, today: str) -> str:
    template_path = source_root / relative_path
    raw_text = template_path.read_text()
    return render_template(raw_text, project_name, today)


def determine_action(destination: Path, force: bool, condition: str) -> str:
    if condition == "if_missing" and destination.exists():
        return "skip"
    if destination.exists() and not force:
        return "skip"
    if destination.exists() and force:
        return "overwrite"
    return "create"


def main() -> int:
    args = build_parser().parse_args()

    script_dir = Path(__file__).resolve().parent
    templates_root = script_dir.parent / "assets" / "templates"
    target_root = Path(args.target).resolve()

    if not target_root.exists():
        print(f"[ERROR] Target path does not exist: {target_root}")
        return 1
    if not target_root.is_dir():
        print(f"[ERROR] Target path is not a directory: {target_root}")
        return 1

    project_name = args.project_name or target_root.name
    today = date.today().isoformat()

    ops = []
    for op in TEMPLATE_OPS:
        if op.target == "AGENTS.md" and args.skip_agents:
            continue
        destination = target_root / op.target
        action = determine_action(destination, args.force, op.condition)
        ops.append((action, op, destination))

    print(f"Target: {target_root}")
    print(f"Project name: {project_name}")
    print(f"Date token: {today}")
    print()

    created = []
    overwritten = []
    skipped = []

    for action, op, destination in ops:
        if action == "skip":
            skipped.append(str(destination))
            print(f"[SKIP] {destination}")
            continue

        rendered = load_template(templates_root, op.source, project_name, today)
        if args.dry_run:
            label = "OVERWRITE" if action == "overwrite" else "CREATE"
            print(f"[DRY-RUN {label}] {destination}")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered)
            if action == "overwrite":
                overwritten.append(str(destination))
                print(f"[OVERWRITE] {destination}")
            else:
                created.append(str(destination))
                print(f"[CREATE] {destination}")

    print()
    if args.dry_run:
        print("Dry-run complete.")
    else:
        print("Bootstrap complete.")
    print(f"Created: {len(created)}")
    print(f"Overwritten: {len(overwritten)}")
    print(f"Skipped: {len(skipped)}")

    if skipped:
        print()
        print("Review skipped files and merge manually if the repository already has partial docs structure.")

    if not (target_root / ".git").exists():
        print()
        print("Warning: target does not appear to be a git repository.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
