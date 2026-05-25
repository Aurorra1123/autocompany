---
name: super-harness
description: Use when initializing or normalizing a repository that needs shared agent memory, guided onboarding, project goals, idea validation, experiment records, comparisons, reviewed findings, verification evidence, and agent entrypoints.
---

# Super Harness

## Overview

Initialize a reusable harness that treats the repository as the team's durable memory instead of relying on each contributor's individual agent chat history. The bundled script scaffolds a `harness/` layer for guided onboarding, repo-level project context, idea validation, execution plans, experiment recording, comparison tools, and reviewed findings. It also creates a lightweight `AGENTS.md` entrypoint and optional IDE-specific stubs so that anyone in the team can open the repo with their own agent and immediately recover the shared context.

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
4. Run guided onboarding when the repository does not already have clear project memory.
   Read `harness/onboarding/questions.md`, inspect the repo first, then ask one question at a time. Use repo evidence to draft answers where possible. Write confirmed answers back to `harness/project/brief.md`, `harness/ideas/index.jsonl`, `harness/plans/feature-list.json`, and one concise onboarding checkpoint in `harness/plans/progress.md`.
5. Tailor the generated files immediately.
   Replace bootstrap placeholders with the repository's real project brief, idea backlog, roadmap, architecture baseline, deployment constraints, and collaboration rules. The generated `project/brief.md`, `ideas/index.jsonl`, and `feature-list.json` are starting points, not final project truth.
6. Compact noisy legacy progress logs when normalizing an existing harness.

   ```bash
   python3 harness/scripts/compact_progress.py --dry-run
   python3 harness/scripts/compact_progress.py --summary "legacy progress archived for review"
   ```

   The compactor archives the previous `harness/plans/progress.md` under `harness/reference/legacy-progress-*.md`, then rewrites `progress.md` as one concise checkpoint with evidence links and next steps. It does not infer findings from old notes; reviewed conclusions should be promoted separately through comparisons, findings, or ADRs.
7. For experiment-heavy work, use the generated recorder.

   ```bash
   python3 harness/scripts/harness_run.py --title "cache strategy benchmark" -- python3 benchmarks/cache_latency.py
   ```

   The recorder writes `harness/verification/experiments/<id>/record.md`, captures stdout/stderr artifacts, appends `experiments/index.jsonl`, records git/environment provenance, and writes a per-experiment resource bundle. It does not update `progress.md` by default; use `--progress-checkpoint` only for meaningful milestones, handoffs, experiment batches, comparisons, or reviewed findings. It does not monitor the shell by itself; agents should wrap experiment, benchmark, training, evaluation, or key validation commands with it whenever practical.
8. For cross-branch or cross-author claims, generate a comparison.

   ```bash
   python3 harness/scripts/compare_experiments.py --title "cache-v1 vs cache-v2" --evidence <record-id>
   ```

   Comparisons write `harness/verification/comparisons/*.md`, include evidence links and fairness checks, and are the preferred place to solidify reviewed conclusions.
9. Promote reviewed findings when a conclusion is accepted.

   ```bash
   python3 harness/scripts/promote_finding.py --title "accepted result" --comparison <comparison-id>
   ```

   Findings write `harness/verification/findings/<id>/finding.md` and should be protected by PR review/CODEOWNERS in shared repositories.
10. Validate the result.
   Read the created files, confirm skipped files are expected, and make sure the harness reflects the repository's actual state before treating it as the new baseline.

## Existing Repositories

- If the target already contains `harness/onboarding/`, `harness/project/brief.md`, `harness/plans/feature-list.json`, or `harness/plans/progress.md`, treat the scaffold as reference material and merge carefully.
- Do not overwrite existing `AGENTS.md` / `CLAUDE.md` / Cursor rules unless the user explicitly asks for it.
- Do not copy business-specific roadmap items from another repository into the new one without rewriting them.

## Resources

- `scripts/bootstrap_harness.py`: create the scaffold, support dry-run mode, detect target IDE, and avoid overwriting by default.
- `references/blueprint.md`: explain the generated structure, adaptation checklist, and merge strategy for existing repositories.
- `assets/templates/`: store the scaffold templates copied into target repositories, including `harness/onboarding/`, `harness/project/`, `harness/ideas/`, `harness/scripts/compact_progress.py`, and IDE-specific stub templates under `assets/templates/ide-stubs/`.
