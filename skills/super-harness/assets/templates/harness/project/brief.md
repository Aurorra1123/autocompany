# Project Brief

## Goal

`{{PROJECT_NAME}}` 的目标是建立一套 repo-local 的协作与验证基线，让人和 AI agent 可以围绕同一个仓库持续推进实现、实验、对比、结论沉淀和交接。

## Current Focus

当前阶段先把仓库目标、任务计划、实验记录、对比分析和 reviewed finding 放进可追溯的目录结构中，减少对个人聊天记录的依赖。

## Non-Goals

- 不替代成熟的实验平台、项目管理系统或 CI 系统。
- 不自动监听所有 shell 命令；关键实验和验证命令需要显式通过 harness 脚本记录。
- 不把未经验证的单次实验结果直接当作团队结论。

## Users

- 需要接手当前仓库的人类 contributor。
- 在 Codex、Claude Code、Cursor 等工具中工作的 AI agent。
- 需要复查实验依据、对比结论和项目进展的 reviewer。

## Success Criteria

- 新 contributor 或 agent 能快速理解当前 repo 要完成什么。
- 关键 idea、任务、实验、对比和 finding 都能链接到具体证据。
- reviewed conclusion 可以追溯到 comparison 和原始 experiment。
- 下一步工作能从 `plans/`、`ideas/` 和 `verification/` 中恢复，而不是依赖历史聊天。

## Constraints

- 长期项目背景写在本文件，原始材料放在 `harness/reference/`。
- 任务拆解和验收标准写在 `harness/plans/feature-list.json`。
- 执行进展写在 `harness/plans/progress.md`。
- 实验证据、对比分析和审核结论写在 `harness/verification/`。
