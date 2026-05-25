# Project Context

本目录保存仓库最高层的目标、边界和成功标准。它回答“这个 repo 最终要完成什么”，不记录日常执行流水。

## 文件

- `brief.md`：项目背景、当前阶段目标、非目标、用户、约束和成功标准。

## 使用规则

- 新 contributor 或 agent 进入仓库后，应先读 `harness/onboarding/questions.md` 和 `brief.md`，再读 `harness/plans/progress.md` 和 `harness/plans/feature-list.json`。
- 如果 `brief.md` 仍是模板内容，先完成 guided onboarding，再开始大规模实现。
- 当项目目标、阶段重点或非目标变化时，优先更新 `brief.md`，并在 `progress.md` 用一条 checkpoint 记录原因和证据链接。
- 不要把实验日志、临时结论或任务拆解写进这里；这些内容分别放入 `verification/` 和 `plans/`。
