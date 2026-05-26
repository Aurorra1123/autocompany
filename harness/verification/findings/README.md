# Reviewed Findings

本目录用于保存经过审核或明确治理状态的结论。实验记录是原始证据，comparison 是对比分析，finding 才是团队可复用的结论层。

## 推荐方式

先用 `record_experiment.py` 记录实验，再用 `compare_experiments.py` 生成对比，最后用 `promote_finding.py` 晋升结论：

```bash
python3 harness/scripts/promote_finding.py \
  --title "cache-v2 reduces checkout p95 latency" \
  --comparison 20260522-120000-cache-v1-vs-cache-v2 \
  --status reviewed \
  --reviewer "Performance Reviewer <reviewer@example.com>" \
  --limitation "Only verified on checkout-read-heavy replay traffic" \
  --conclusion "cache-v2 reduces p95 latency by 18% without increasing recorded error rate."
```

脚本会生成：

- `harness/verification/findings/<finding-id>/finding.md`
- `harness/verification/findings/index.jsonl`

默认不会写入 `harness/plans/progress.md`。如果 finding 代表团队结论变化或交接点，追加 `--progress-checkpoint`。

## 状态

- `provisional`：有证据但尚未完成审核。
- `reviewed`：经过 reviewer 确认，可作为团队共享结论。
- `rejected`：证据不足或结论不成立。
- `superseded`：被后续更强证据替代。

## 规则

- finding 必须引用 comparison；不要直接从单个实验手写 solid conclusion。
- `reviewed` finding 默认必须来自 `reviewed` comparison；只有 reviewer 明确接受时才使用 `--allow-provisional-comparison`。
- agent 创建、修改或晋升 finding 前必须停下来向用户确认；未经确认只能保留为实验记录或 provisional comparison。
- 请求确认时必须给出 proposed conclusion、comparison/evidence 路径、limitation 和目标 finding 文件。
- 修改 `reviewed` finding 应通过 PR review。
- 如果证据的 idea、输入数据、控制变量、metric 或 source dirty 状态不可比，应保留 limitation。
