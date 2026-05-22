# Experiment Comparisons

本目录用于沉淀跨分支、跨作者、跨实验的对比结论。

## 推荐方式

先用 `record_experiment.py` 记录每个实验，再用 `compare_experiments.py` 引用证据生成对比：

```bash
python3 harness/scripts/compare_experiments.py \
  --title "baseline vs tuned config" \
  --claim "tuned config improves F1 on dataset=v2" \
  --evidence 20260522-101500-baseline \
  --evidence 20260522-112000-tuned-config \
  --metric "f1_delta=+0.03" \
  --fairness-note "Both runs used dataset=v2 and seed=42" \
  --result "Tuned config is better under the recorded setup, pending review."
```

脚本会生成：

- `harness/verification/comparisons/<timestamp>-<title>.md`
- `harness/verification/comparisons/index.jsonl`
- `harness/plans/progress.md` 中的对比摘要

## 审核重点

- 对比结论必须引用具体 `experiments/*.md` 或 record id。
- 优先比较相同 dataset、seed、metric 定义和相近 commit base 的实验。
- 如果任一实验记录显示 `source_dirty=true`，对比结论默认应标为 provisional。
- 经过 review 后再把 comparison 状态从 `provisional` 改成 `reviewed`。
