# Project Checkpoints

本文件是高层 checkpoint / handoff log，不是完整活动流水账。详细实验、命令输出、参数、指标和过程日志应放在 `verification/`、`architecture/adr/` 或 `reference/`，这里只保留短摘要和链接。

如果旧内容已经变成流水账，先运行 `python3 harness/scripts/compact_progress.py --dry-run`，确认后将旧内容归档到 `harness/reference/` 并重写本文件。

## 写入标准

只有满足下面任一条件时才更新：

- onboarding、milestone 或阶段性交接完成
- 一组实验、comparison 或 reviewed finding 改变了后续判断
- 项目方向、优先级、核心假设、blocker、risk 或 open question 发生变化
- 会话结束时下个 contributor/agent 需要快速恢复主线

## {{TODAY}}

### Checkpoint

Initialized the `{{PROJECT_NAME}}` harness baseline. The content is still a template and must be adapted to the real repo goal, ideas, tasks, standards, and evidence.

### Evidence Links

- Project brief: `harness/project/brief.md`
- Idea index: `harness/ideas/index.jsonl`
- Task list: `harness/plans/feature-list.json`
- Evidence root: `harness/verification/`

### Next

1. Fill `harness/project/brief.md` with the repo-level goal, non-goals, constraints, and success criteria.
2. Replace the template ideas and task list with the real validation plan.
3. Run the first real smoke test through `harness/scripts/harness_run.py` and keep detailed evidence under `harness/verification/`.

### Open Questions

- 真实 repo-level 目标是什么？
- 第一个需要验证的 idea 或 hypothesis 是什么？
- 哪些旧资料应进入 `harness/reference/`？
