# Experiment Comparisons

本目录用于沉淀跨分支、跨作者、跨实验的对比结论。

## 推荐方式

先用 `record_experiment.py` 记录每个实验，再用 `compare_experiments.py` 引用证据生成对比：

```bash
python3 harness/scripts/compare_experiments.py \
  --title "cache-v1 vs cache-v2" \
  --status reviewed \
  --claim "cache-v2 reduces p95 latency under checkout-read-heavy traffic" \
  --evidence 20260522-101500-cache-v1-benchmark \
  --evidence 20260522-112000-cache-v2-benchmark \
  --metric "p95_latency_delta=-18%" \
  --fairness-note "Both runs used requests=replay-2026-05-20 and the same traffic profile" \
  --result "cache-v2 is faster under the recorded setup, pending review."
```

脚本会生成：

- `harness/verification/comparisons/<timestamp>-<title>.md`
- `harness/verification/comparisons/index.jsonl`

默认不会写入 `harness/plans/progress.md`。如果这次对比改变项目方向、结论或交接状态，追加 `--progress-checkpoint`。

## 审核重点

- 对比结论必须引用具体 `experiments/<id>/record.md` 或 record id。
- 优先比较相同 idea、输入数据、控制变量、metric 定义和相近 commit base 的实验。
- 如果任一实验记录显示 `source_dirty=true`，对比结论默认应标为 provisional。
- 经过 review 后再把 comparison 状态从 `provisional` 改成 `reviewed`。
