---
name: super-harness
description: Bootstrap a repository-level "super harness" for long-running agent and human collaboration, so durable team knowledge, experiment progress, comparisons, reviewed findings, and verification evidence live in the repo rather than individual chat history. Use when initializing or normalizing the harness structure in a new or messy repository, especially to add `harness/plans/feature-list.json`, `harness/plans/progress.md`, `harness/scripts/harness_run.py`, `harness/scripts/record_experiment.py`, `harness/scripts/compare_experiments.py`, `harness/scripts/promote_finding.py`, `harness/standards/`, `harness/architecture/adr/`, `harness/verification/experiments/`, `harness/verification/comparisons/`, `harness/verification/findings/`, `.github/CODEOWNERS`, `harness/reference/`, and the agent entrypoints (`AGENTS.md` plus IDE-specific stubs for Claude Code, Cursor, etc.) that keep durable knowledge out of chat.
---

# Super Harness

## Overview

Initialize a reusable harness that treats the repository as the team's durable memory instead of relying on each contributor's individual agent chat history. The bundled script scaffolds a `harness/` execution layer, creates a lightweight `AGENTS.md` entrypoint, adds experiment recording and comparison tools, and (optionally) emits stubs for IDE-specific agent files (Claude Code's `CLAUDE.md`, Cursor's `.cursor/rules/super-harness.mdc`) so that anyone in the team can open the repo with their own agent and immediately recover the shared context.

## Workflow

1. Inspect the target repository before writing anything.
   Check whether `AGENTS.md`, `harness/`, or an existing planning system already exists. If the repository already has partial structure, prefer merging manually instead of overwriting.
2. Run a dry-run first.

   ```bash
   python3 scripts/bootstrap_harness.py --dry-run /path/to/repo
   ```

3. Apply the scaffold.

   ```bash
   python3 scripts/bootstrap_harness.py /path/to/repo
   ```

   - Use `--project-name` when the repository folder name is not the desired project name.
   - Use `--ide auto|claude|cursor|codex|all|none` to control which IDE-specific stubs are generated. `auto` (default) detects existing markers (`CLAUDE.md`, `.claude/`, `.cursor/`, `AGENTS.md`) and only emits the missing ones; `all` forces every supported stub; `none` skips all stubs.
   - Use `--force` only when you have already reviewed the target files and intentionally want to overwrite them.
4. Tailor the generated files immediately.
   Replace bootstrap placeholders with the repository's real roadmap, architecture baseline, deployment constraints, and collaboration rules. The generated `feature-list.json` is a starting point, not a final backlog.
5. For experiment-heavy work, use the generated recorder.

   ```bash
   python3 harness/scripts/harness_run.py --title "baseline smoke test" -- pytest -q
   ```

   The recorder writes `harness/verification/experiments/<id>/record.md`, captures stdout/stderr artifacts, appends `experiments/index.jsonl`, records git/environment provenance, writes a per-experiment resource bundle, and appends a progress summary. It does not monitor the shell by itself; agents should wrap experiment, benchmark, training, evaluation, or key validation commands with it whenever practical.
6. For cross-branch or cross-author claims, generate a comparison.

   ```bash
   python3 harness/scripts/compare_experiments.py --title "baseline vs tuned config" --evidence <record-id>
   ```

   Comparisons write `harness/verification/comparisons/*.md`, include evidence links and fairness checks, and are the preferred place to solidify reviewed conclusions.
7. Promote reviewed findings when a conclusion is accepted.

   ```bash
   python3 harness/scripts/promote_finding.py --title "accepted result" --comparison <comparison-id>
   ```

   Findings write `harness/verification/findings/<id>/finding.md` and should be protected by PR review/CODEOWNERS in shared repositories.
8. Validate the result.
   Read the created files, confirm skipped files are expected, and make sure the harness reflects the repository's actual state before treating it as the new baseline.

## Existing Repositories

- If the target already contains `harness/plans/feature-list.json` or `harness/plans/progress.md`, treat the scaffold as reference material and merge carefully.
- Do not overwrite existing `AGENTS.md` / `CLAUDE.md` / Cursor rules unless the user explicitly asks for it.
- Do not copy business-specific roadmap items from another repository into the new one without rewriting them.

## Resources

- `scripts/bootstrap_harness.py`: create the scaffold, support dry-run mode, detect target IDE, and avoid overwriting by default.
- `references/blueprint.md`: explain the generated structure, adaptation checklist, and merge strategy for existing repositories.
- `assets/templates/`: store the scaffold templates copied into target repositories, including IDE-specific stub templates under `assets/templates/ide-stubs/`.
