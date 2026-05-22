# Verification Evidence

本目录用于存放功能验证、实验过程、回归验证、UI 截图、压测结果和其他可追溯证据。

## 目标

- 将“验证通过”从口头结论变成可追溯证据
- 为跨会话回归提供依据
- 为将任务状态从未通过改成通过提供凭证

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
- 实验记录统一放入 `experiments/`，命令输出放入 `experiments/artifacts/`

示例：

```text
harness/verification/
├── experiments/
│   ├── 20260416-101530-baseline-smoke-test.md
│   └── artifacts/
│       ├── 20260416-101530-baseline-smoke-test.stdout.log
│       └── 20260416-101530-baseline-smoke-test.stderr.log
└── 2026-04-16/
    └── auth-flow/
        ├── api-check.txt
        └── login-page.png
```

## 实验记录脚本

运行实验、benchmark、训练或关键验证命令时，优先用脚本包住命令：

```bash
python3 harness/scripts/record_experiment.py \
  --title "baseline smoke test" \
  --goal "确认当前实现是否通过最小回归" \
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
  --metric "f1=0.84" \
  --result "dropout=0.2 优于 baseline"
```

## 证据类型

- `*.png` / `*.jpg`：页面截图
- `*.txt` / `*.log`：命令输出摘要、测试输出、部署结果
- `*.md`：人工验证记录与结论
- `experiments/*.md`：实验目标、命令、参数、指标、结论和下一步
- 外部录屏或报告链接：建议附一份同名 `*.md` 说明链接与上下文

## 使用规则

- 将功能项从未通过改为通过前，应至少留下一份对应证据
- 回归失败时，应在证据目录追加失败记录，而不是只在聊天中说明
- 证据文件名应包含日期、主题和验证动作，避免使用无意义名称
- 进度记录中应引用对应证据目录或文件
- 对实验型任务，进度记录中应引用 `experiments/*.md`，不要只写最终结论
