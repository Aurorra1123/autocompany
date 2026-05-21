#!/usr/bin/env python3
"""Bootstrap a repository-local super-harness scaffold."""

import argparse
from datetime import date
from pathlib import Path
import sys
from typing import NamedTuple


class TemplateOp(NamedTuple):
    source: str
    target: str
    condition: str = "always"  # "always" | "if_missing"
    ide: str = ""  # "" for core ops, otherwise one of CORE_IDE keys


CORE_OPS = (
    TemplateOp("harness/README.md", "harness/README.md"),
    TemplateOp("harness/plans/feature-list.json", "harness/plans/feature-list.json"),
    TemplateOp("harness/plans/progress.md", "harness/plans/progress.md"),
    TemplateOp("harness/plans/exec-plan/README.md", "harness/plans/exec-plan/README.md"),
    TemplateOp("harness/standards/engineering-rules.md", "harness/standards/engineering-rules.md"),
    TemplateOp("harness/standards/git-workflow.md", "harness/standards/git-workflow.md"),
    TemplateOp("harness/standards/agent-harness-rules.md", "harness/standards/agent-harness-rules.md"),
    TemplateOp("harness/standards/deployment-baseline.md", "harness/standards/deployment-baseline.md"),
    TemplateOp("harness/architecture/README.md", "harness/architecture/README.md"),
    TemplateOp("harness/architecture/adr/README.md", "harness/architecture/adr/README.md"),
    TemplateOp(
        "harness/architecture/adr/0001-repo-as-agent-memory.md",
        "harness/architecture/adr/0001-repo-as-agent-memory.md",
    ),
    TemplateOp(
        "harness/architecture/adr/0002-harness-first-agent-workflow.md",
        "harness/architecture/adr/0002-harness-first-agent-workflow.md",
    ),
    TemplateOp("harness/verification/README.md", "harness/verification/README.md"),
    TemplateOp("harness/reference/README.md", "harness/reference/README.md"),
)

# AGENTS.md is the canonical entrypoint, shared by Codex and the OpenAI Agents SDK.
# Other IDEs get a short stub that points at it.
IDE_OPS = {
    "codex": (TemplateOp("AGENTS.md", "AGENTS.md", "if_missing", "codex"),),
    "claude": (TemplateOp("ide-stubs/CLAUDE.md", "CLAUDE.md", "if_missing", "claude"),),
    "cursor": (
        TemplateOp(
            "ide-stubs/cursor-rules/super-harness.mdc",
            ".cursor/rules/super-harness.mdc",
            "if_missing",
            "cursor",
        ),
    ),
}

# Markers that indicate the target repo is already used with a given IDE.
IDE_MARKERS = {
    "codex": ("AGENTS.md",),
    "claude": ("CLAUDE.md", ".claude"),
    "cursor": (".cursor", ".cursorrules"),
}


def detect_ides(target_root: Path) -> list[str]:
    """Return IDEs that already have markers in the target repo.

    If none are detected, fall back to all supported IDEs so a fresh repo
    gets every entrypoint and any agent can pick it up.
    """
    found = []
    for ide, markers in IDE_MARKERS.items():
        if any((target_root / marker).exists() for marker in markers):
            found.append(ide)
    return found or list(IDE_OPS.keys())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bootstrap a super-harness scaffold into a target repository.",
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
        "--ide",
        default="auto",
        help=(
            "Which IDE entrypoint stubs to generate. "
            "auto (default) detects existing markers (CLAUDE.md/.claude, .cursor, AGENTS.md); "
            "all generates every supported stub; "
            "none skips IDE stubs entirely; "
            "or pass a comma-separated subset of: " + ",".join(IDE_OPS.keys())
        ),
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
    return parser


def resolve_ide_selection(arg: str, target_root: Path) -> list[str]:
    arg = arg.strip().lower()
    if arg in ("none", ""):
        return []
    if arg == "all":
        return list(IDE_OPS.keys())
    if arg == "auto":
        return detect_ides(target_root)
    selected = [item.strip() for item in arg.split(",") if item.strip()]
    unknown = [item for item in selected if item not in IDE_OPS]
    if unknown:
        raise SystemExit(
            f"[ERROR] Unknown --ide value(s): {', '.join(unknown)}. "
            f"Supported: {', '.join(IDE_OPS.keys())}, plus auto/all/none."
        )
    return selected


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
    selected_ides = resolve_ide_selection(args.ide, target_root)

    ops: list[TemplateOp] = list(CORE_OPS)
    for ide in selected_ides:
        ops.extend(IDE_OPS[ide])

    resolved = []
    for op in ops:
        destination = target_root / op.target
        action = determine_action(destination, args.force, op.condition)
        resolved.append((action, op, destination))

    print(f"Target: {target_root}")
    print(f"Project name: {project_name}")
    print(f"Date token: {today}")
    print(f"IDE stubs: {', '.join(selected_ides) if selected_ides else 'none'}")
    print()

    created = []
    overwritten = []
    skipped = []

    for action, op, destination in resolved:
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
        print("Review skipped files and merge manually if the repository already has partial harness structure.")

    if not (target_root / ".git").exists():
        print()
        print("Warning: target does not appear to be a git repository.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
