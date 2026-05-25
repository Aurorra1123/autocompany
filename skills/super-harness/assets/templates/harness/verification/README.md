# Verification Evidence

本目录用于存放功能验证、实验过程、回归验证、UI 截图、压测结果和其他可追溯证据。

## 目标

- 将“验证通过”从口头结论变成可追溯证据
- 为跨会话回归提供依据
- 为将任务状态从未通过改成通过提供凭证
- 为多人分支实验提供可比较、可 review、可追溯的证据链

## 适用场景

- 前端页面或交互流程验证
- E2E 测试结果存档
- API 自测结果存档
- 模型、算法、数据、prompt、参数或性能实验
- 压测与性能报告
- 无障碍检查报告
- Docker、部署与环境验证记录

## 建议结构

- 一般验证可按日期建立子目录，例如 `2026-04-16/`
- 实验记录统一放入 `experiments/<experiment-id>/`，命令输出放入每个实验目录下的 `artifacts/`
- 跨实验对比结论统一放入 `comparisons/`
- 审核后的 solid finding 统一放入 `findings/`

示例：

```text
harness/verification/
├── experiments/
│   ├── index.jsonl
│   └── 20260416-101530-baseline-smoke-test/
│       ├── record.md
│       ├── metrics.json
│       ├── artifacts.md
│       ├── configs/
│       └── artifacts/
│           ├── stdout.log
│           └── stderr.log
├── comparisons/
│   ├── 20260416-120000-cache-v1-vs-cache-v2.md
│   └── index.jsonl
├── findings/
│   ├── index.jsonl
│   └── 20260416-130000-cache-v2-reduces-p95-latency/
│       └── finding.md
└── 2026-04-16/
    └── auth-flow/
        ├── api-check.txt
        └── login-page.png
```

## 实验记录脚本

运行实验、benchmark、训练或关键验证命令时，优先用脚本包住命令。主示例使用通用 idea validation，避免把 harness 限定为模型研发工具：

```bash
python3 harness/scripts/harness_run.py \
  --title "cache strategy benchmark" \
  --goal "验证新的 cache 策略是否降低接口 p95 延迟" \
  --tag "idea=IDEA-001" \
  --experiment-type "benchmark" \
  --param "baseline=cache-v1" \
  --param "variant=cache-v2" \
  --param "traffic_profile=checkout-read-heavy" \
  --dataset "requests=replay-2026-05-20" \
  --metric "p95_latency_ms=184" \
  --metric "error_rate=0.01%" \
  --result "cache-v2 在相同 traffic profile 下 p95 延迟下降 18%" \
  --next "扩大到写多读少场景" \
  -- python3 benchmarks/cache_latency.py --strategy cache-v2
```

如果实验已经执行过，使用 `--command` 和 `--result` 补录摘要：

```bash
python3 harness/scripts/record_experiment.py \
  --title "manual cache benchmark review" \
  --command "python3 benchmarks/cache_latency.py --strategy cache-v2" \
  --tag "idea=IDEA-001" \
  --param "baseline=cache-v1" \
  --param "variant=cache-v2" \
  --dataset "requests=replay-2026-05-20" \
  --metric "p95_latency_ms=184" \
  --result "cache-v2 在相同输入回放下优于 baseline"
```

基础模型或 ML 实验可以在同一套记录方式上额外补充 `--model-base`、`--data-mix`、`--tokenizer`、`--train-tokens`、`--eval-suite` 等领域控制变量。

脚本会自动记录 author、branch、commit、dirty worktree、source dirty、平台和 Python 版本，创建独立实验资源目录，并追加 `experiments/index.jsonl`。默认不会写入 `progress.md`；只有 milestone、handoff、重要实验批次或 blocker 才使用 `--progress-checkpoint` 追加高层 checkpoint。

## 实验对比脚本

形成跨人、跨分支或跨配置结论时，引用具体实验记录：

```bash
python3 harness/scripts/compare_experiments.py \
  --title "cache-v1 vs cache-v2" \
  --status reviewed \
  --claim "cache-v2 reduces p95 latency under checkout-read-heavy traffic" \
  --evidence 20260416-101530-cache-v1-benchmark \
  --evidence 20260416-113000-cache-v2-benchmark \
  --metric "p95_latency_delta=-18%" \
  --fairness-note "Both runs used requests=replay-2026-05-20 and the same traffic profile" \
  --result "cache-v2 is faster under the recorded setup, pending review."
```

## Finding 晋升脚本

经过审核的结论应从 comparison 晋升，不应直接手写：

```bash
python3 harness/scripts/promote_finding.py \
  --title "cache-v2 reduces checkout p95 latency" \
  --comparison 20260416-120000-cache-v1-vs-cache-v2 \
  --status reviewed \
  --reviewer "Performance Reviewer <reviewer@example.com>" \
  --limitation "Only verified on checkout-read-heavy replay traffic" \
  --conclusion "cache-v2 reduces p95 latency by 18% without increasing recorded error rate."
```

默认情况下，`reviewed` finding 只能从 `reviewed` comparison 晋升。

## 证据类型

- `*.png` / `*.jpg`：页面截图
- `*.txt` / `*.log`：命令输出摘要、测试输出、部署结果
- `*.md`：人工验证记录与结论
- `experiments/<id>/record.md`：实验目标、命令、参数、指标、溯源信息、结论和下一步
- `experiments/<id>/metrics.json`：机器可读指标、参数、领域上下文和标签
- `experiments/index.jsonl`：机器可读实验索引，供 agent 汇总、筛选和对比
- `comparisons/*.md`：跨实验对比结论，必须链接到具体实验证据
- `comparisons/index.jsonl`：机器可读对比索引
- `findings/<id>/finding.md`：审核后的结论，必须链接到 comparison
- `findings/index.jsonl`：机器可读结论索引
- 外部录屏或报告链接：建议附一份同名 `*.md` 说明链接与上下文

## 使用规则

- 将功能项从未通过改为通过前，应至少留下一份对应证据
- 回归失败时，应在证据目录追加失败记录，而不是只在聊天中说明
- 证据文件名应包含日期、主题和验证动作，避免使用无意义名称
- 如果形成 `progress.md` checkpoint，应只引用对应证据目录或文件
- `progress.md` 只记录 checkpoint 和链接，不记录完整实验细节或每次命令输出
- 服务于具体 idea 的实验应引用 `harness/ideas/index.jsonl` 中的 idea ID
- 对实验型 checkpoint，应引用 `experiments/<id>/record.md`，不要只写最终结论
- 对比型结论应引用 `comparisons/*.md`，并说明 idea、输入数据、控制变量、commit、metric 定义和 source dirty 状态是否一致
- solid conclusion 应引用 `findings/*.md`，并通过 PR review 或 CODEOWNERS 规则保护
