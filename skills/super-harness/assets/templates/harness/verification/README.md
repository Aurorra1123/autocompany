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
│   ├── 20260416-120000-baseline-vs-tuned-config.md
│   └── index.jsonl
├── findings/
│   ├── index.jsonl
│   └── 20260416-130000-data-mix-b-improves-math/
│       └── finding.md
└── 2026-04-16/
    └── auth-flow/
        ├── api-check.txt
        └── login-page.png
```

## 实验记录脚本

运行实验、benchmark、训练或关键验证命令时，优先用脚本包住命令：

```bash
python3 harness/scripts/harness_run.py \
  --title "baseline smoke test" \
  --goal "确认当前实现是否通过最小回归" \
  --experiment-type "eval" \
  --model-base "1b-pretrain-v0" \
  --data-mix "mix-a" \
  --data-version "data-2026-05-20" \
  --eval-suite "core-eval-v2" \
  --dataset "dataset=sample-v1" \
  --seed "seed=42" \
  --metric "passed=12/12" \
  --result "最小回归通过" \
  --next "扩大测试数据集" \
  -- pytest -q
```

如果实验已经执行过，使用 `--command` 和 `--result` 补录摘要：

```bash
python3 harness/scripts/record_experiment.py \
  --title "manual ablation review" \
  --command "python train.py --ablation dropout" \
  --param "dropout=0.2" \
  --dataset "dataset=v2" \
  --seed "seed=42" \
  --metric "f1=0.84" \
  --result "dropout=0.2 优于 baseline"
```

脚本会自动记录 author、branch、commit、dirty worktree、source dirty、平台和 Python 版本，创建独立实验资源目录，并追加 `experiments/index.jsonl`。

## 实验对比脚本

形成跨人、跨分支或跨配置结论时，引用具体实验记录：

```bash
python3 harness/scripts/compare_experiments.py \
  --title "baseline vs tuned config" \
  --status reviewed \
  --claim "tuned config improves F1 on dataset=v2" \
  --evidence 20260416-101530-baseline-smoke-test \
  --evidence 20260416-113000-tuned-config \
  --metric "f1_delta=+0.03" \
  --fairness-note "Both runs used dataset=v2 and seed=42" \
  --result "Tuned config is better under the recorded setup, pending review."
```

## Finding 晋升脚本

经过审核的结论应从 comparison 晋升，不应直接手写：

```bash
python3 harness/scripts/promote_finding.py \
  --title "data mix b improves math at 1b scale" \
  --comparison 20260416-120000-baseline-vs-tuned-config \
  --status reviewed \
  --reviewer "Model Reviewer <reviewer@example.com>" \
  --limitation "Only verified at 1B scale" \
  --conclusion "Data mix B improves math eval but slightly regresses code eval."
```

默认情况下，`reviewed` finding 只能从 `reviewed` comparison 晋升。

## 证据类型

- `*.png` / `*.jpg`：页面截图
- `*.txt` / `*.log`：命令输出摘要、测试输出、部署结果
- `*.md`：人工验证记录与结论
- `experiments/<id>/record.md`：实验目标、命令、参数、指标、溯源信息、结论和下一步
- `experiments/<id>/metrics.json`：机器可读指标、参数、模型上下文和标签
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
- 进度记录中应引用对应证据目录或文件
- 对实验型任务，进度记录中应引用 `experiments/<id>/record.md`，不要只写最终结论
- 对比型结论应引用 `comparisons/*.md`，并说明 dataset、seed、commit、metric 定义和 source dirty 状态是否一致
- solid conclusion 应引用 `findings/*.md`，并通过 PR review 或 CODEOWNERS 规则保护
