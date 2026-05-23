# Agent Progress Log

本文件用于跨会话交接，任何一次较完整的工作结束前都应更新。

## {{TODAY}}

### 已完成

- 初始化 `{{PROJECT_NAME}}` 的 harness 骨架
- 新增 `project/`、`ideas/`、`plans/`（含 `progress.md`、`feature-list.json`、`exec-plan/`）、`standards/`、`architecture/`（含 `adr/`）、`verification/`、`reference/` 基础目录与模板
- 新增 `harness/scripts/harness_run.py`、`harness/scripts/record_experiment.py`、`harness/scripts/compare_experiments.py`、`harness/scripts/promote_finding.py`、`harness/verification/experiments/`、`harness/verification/comparisons/` 和 `harness/verification/findings/`，用于记录实验命令、输出、指标、溯源信息、对比结论和审核 finding
- 如仓库原先缺少 `AGENTS.md`，已创建最小入口文件

### 当前状态

- 当前内容仍是 bootstrap 基线，需要按 `{{PROJECT_NAME}}` 的真实业务、技术栈和交付目标继续改写
- `project/brief.md` 仍是通用项目背景，需要替换为 repo 的真实目标、非目标和成功标准
- `ideas/index.jsonl` 仍是 starter idea，需要替换为真实 idea 或 hypothesis
- `feature-list` 仍是通用初始化任务，尚未替换为真实路线图
- `reference/` 仍待补充仓库现有输入材料
- 实验 tracking 和 comparison 规则已就位，但需要在后续真实实验中开始产生记录和对比结论

### 下一步建议

1. 改写 `harness/project/brief.md`，明确 repo-level 目标、非目标和成功标准
2. 把第一个真实 idea 或 hypothesis 登记到 `harness/ideas/index.jsonl`
3. 盘点现有输入资料并整理到 `harness/reference/`
4. 根据当前仓库真实目标改写 `harness/plans/feature-list.json`
5. 补齐 `harness/standards/` 中的环境、部署和协作规则
6. 根据仓库实际情况补第一轮架构文档和执行计划
7. 下次实验或 benchmark 使用 `python3 harness/scripts/harness_run.py --title "..." --tag "idea=IDEA-001" -- <command>` 记录
8. 需要跨人/跨分支对比时，使用 `python3 harness/scripts/compare_experiments.py --title "..." --evidence <record-id>` 生成结论
9. 结论经过 review 后，使用 `python3 harness/scripts/promote_finding.py --title "..." --comparison <comparison-id>` 晋升到 findings

### 注意事项

- 在核对真实状态前，不要将模板任务直接标记为通过
- 如仓库已有旧文档或旧流程，优先合并，不要机械覆盖
- 任何“已完成”都应建立在最小必要验证之上
