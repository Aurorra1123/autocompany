# Agent Progress Log

本文件用于跨会话交接，任何一次较完整的工作结束前都应更新。

## {{TODAY}}

### 已完成

- 初始化 `{{PROJECT_NAME}}` 的 harness 骨架
- 新增 `plans/`（含 `progress.md`、`feature-list.json`、`exec-plan/`）、`standards/`、`architecture/`（含 `adr/`）、`verification/`、`reference/` 基础目录与模板
- 新增 `harness/scripts/record_experiment.py`、`harness/scripts/compare_experiments.py`、`harness/verification/experiments/` 和 `harness/verification/comparisons/`，用于记录实验命令、输出、指标、溯源信息和对比结论
- 如仓库原先缺少 `AGENTS.md`，已创建最小入口文件

### 当前状态

- 当前内容仍是 bootstrap 基线，需要按 `{{PROJECT_NAME}}` 的真实业务、技术栈和交付目标继续改写
- `feature-list` 仍是通用初始化任务，尚未替换为真实路线图
- `reference/` 仍待补充仓库现有输入材料
- 实验 tracking 和 comparison 规则已就位，但需要在后续真实实验中开始产生记录和对比结论

### 下一步建议

1. 盘点现有输入资料并整理到 `harness/reference/`
2. 根据当前仓库真实目标改写 `harness/plans/feature-list.json`
3. 补齐 `harness/standards/` 中的环境、部署和协作规则
4. 根据仓库实际情况补第一轮架构文档和执行计划
5. 下次实验或 benchmark 使用 `python3 harness/scripts/record_experiment.py --title "..." -- <command>` 记录
6. 需要跨人/跨分支对比时，使用 `python3 harness/scripts/compare_experiments.py --title "..." --evidence <record-id>` 生成结论

### 注意事项

- 在核对真实状态前，不要将模板任务直接标记为通过
- 如仓库已有旧文档或旧流程，优先合并，不要机械覆盖
- 任何“已完成”都应建立在最小必要验证之上
