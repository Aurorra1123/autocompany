# Experiment Records

本目录用于保存 Codex、人工或 CI 执行的实验过程、命令输出摘要、关键指标和后续判断。

## 推荐方式

优先使用仓库内置记录脚本包住实验命令：

```bash
python3 harness/scripts/record_experiment.py \
  --title "baseline smoke test" \
  --goal "确认当前实现是否能通过最小回归" \
  --param "dataset=sample" \
  --metric "passed=12/12" \
  --result "最小回归通过，可继续下一步" \
  --next "扩大测试数据集" \
  -- pytest -q
```

脚本会自动创建：

- `harness/verification/experiments/<timestamp>-<title>.md`
- `harness/verification/experiments/artifacts/*.stdout.log`
- `harness/verification/experiments/artifacts/*.stderr.log`
- `harness/plans/progress.md` 中的实验摘要

## 记录要求

- 每次实验至少记录目标、命令、状态、结果和下一步。
- 关键指标使用 `--metric "name=value"` 追加。
- 外部产物、图表、模型权重或报告路径使用 `--artifact` 追加。
- 如果实验已手动执行，可用 `--command` 和 `--result` 记录事后摘要，不需要再执行命令。
