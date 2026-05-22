# Experiment Records

本目录用于保存 Codex、人工或 CI 执行的实验过程、命令输出摘要、关键指标和后续判断。

## 推荐方式

优先使用仓库内置统一入口包住实验命令：

```bash
python3 harness/scripts/harness_run.py \
  --title "baseline smoke test" \
  --goal "确认当前实现是否能通过最小回归" \
  --experiment-type "eval" \
  --model-base "1b-pretrain-v0" \
  --data-mix "mix-a" \
  --data-version "data-2026-05-20" \
  --eval-suite "core-eval-v2" \
  --dataset "dataset=sample-v1" \
  --seed "seed=42" \
  --metric "passed=12/12" \
  --result "最小回归通过，可继续下一步" \
  --next "扩大测试数据集" \
  -- pytest -q
```

脚本会自动创建：

- `harness/verification/experiments/<timestamp>-<title>.md`
- `harness/verification/experiments/<timestamp>-<title>/record.md`
- `harness/verification/experiments/<timestamp>-<title>/metrics.json`
- `harness/verification/experiments/<timestamp>-<title>/artifacts.md`
- `harness/verification/experiments/index.jsonl`
- `harness/verification/experiments/<timestamp>-<title>/artifacts/stdout.log`
- `harness/verification/experiments/<timestamp>-<title>/artifacts/stderr.log`
- `harness/plans/progress.md` 中的实验摘要

## 记录要求

- 每次实验至少记录目标、命令、状态、结果和下一步。
- 关键指标使用 `--metric "name=value"` 追加。
- 基础模型实验应记录 `--model-base`、`--model-size`、`--data-mix`、`--data-version`、`--tokenizer`、`--train-tokens`、`--eval-suite` 等控制变量。
- 数据、样本、评测集或输入版本使用 `--dataset "name=version"` 追加。
- 随机种子、split、prompt 版本等影响公平性的变量使用 `--seed`、`--param` 或 `--fairness-note` 追加。
- 外部产物、图表、模型权重或报告路径使用 `--artifact` 追加；本地文件使用 `--artifact-file` 或 `--config-file` 复制进实验目录。
- 如果实验已手动执行，可用 `--command` 和 `--result` 记录事后摘要，不需要再执行命令。

## 自动溯源

脚本会自动记录：

- Git author、branch、commit、remote、dirty worktree 和 source dirty 状态
- 当前平台、Python 版本、主机名和执行目录
- stdout/stderr artifact 路径
- 每个实验独立资源目录，包含 `record.md`、`metrics.json`、`artifacts.md`、`configs/` 和 `artifacts/`
- 机器可读索引行，便于后续 `compare_experiments.py` 汇总

如果 `source_dirty` 为 `true`，结论默认只应作为 provisional evidence，除非 reviewer 明确接受该条件。`dirty=true` 但 `source_dirty=false` 通常表示只有 harness 记录文件尚未提交。
