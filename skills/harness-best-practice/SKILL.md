---
name: harness-best-practice
description: Bootstrap a repository-level docs harness for long-running agent and human collaboration. Use when Codex needs to initialize or normalize documentation structure in a new or messy repository, especially to add `docs/plans/feature-list.json`, `docs/progress/agent-progress.md`, `docs/standards/`, `docs/adr/`, `docs/verification/`, `docs/exec-plan/`, and a lightweight `AGENTS.md` entrypoint that keeps durable knowledge out of chat.
---

# Harness Best Practice

## Overview

Initialize a reusable docs harness that treats the repository as durable memory instead of relying on chat history. Use the bundled script to scaffold a `docs/` execution layer and create a minimal `AGENTS.md` only when the target repository does not already have one.

## Workflow

1. Inspect the target repository before writing anything.
   Check whether `AGENTS.md`, `docs/`, or an existing planning system already exists. If the repository already has partial structure, prefer merging manually instead of overwriting.
2. Run a dry-run first.

   ```bash
   python3 scripts/bootstrap_docs_harness.py --dry-run /path/to/repo
   ```

3. Apply the scaffold.

   ```bash
   python3 scripts/bootstrap_docs_harness.py /path/to/repo
   ```

   Use `--project-name` when the repository folder name is not the desired project name. Use `--force` only when you have already reviewed the target files and intentionally want to overwrite them.
4. Tailor the generated files immediately.
   Replace bootstrap placeholders with the repository's real roadmap, architecture baseline, deployment constraints, and collaboration rules. The generated `feature-list.json` is a starting point, not a final backlog.
5. Validate the result.
   Read the created files, confirm skipped files are expected, and make sure the harness reflects the repository's actual state before treating it as the new baseline.

## Existing Repositories

- If the target already contains `docs/plans/feature-list.json` or `docs/progress/agent-progress.md`, treat the scaffold as reference material and merge carefully.
- Do not overwrite existing `AGENTS.md` unless the user explicitly asks for it.
- Do not copy business-specific roadmap items from another repository into the new one without rewriting them.

## Resources

- `scripts/bootstrap_docs_harness.py`: create the scaffold, support dry-run mode, and avoid overwriting by default.
- `references/blueprint.md`: explain the generated structure, adaptation checklist, and merge strategy for existing repositories.
- `assets/templates/`: store the scaffold templates copied into target repositories.
