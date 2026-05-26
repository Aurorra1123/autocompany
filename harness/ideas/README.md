# Ideas

本目录保存需要验证的 idea、hypothesis 和探索方向。它连接最高层项目目标与后续任务、实验、对比和 finding。

## 文件

- `idea-template.md`：新增 idea 时复制使用的模板。
- `index.jsonl`：机器可读 idea 索引，便于 agent 汇总、去重和关联实验。

## 使用规则

- 每个重要 idea 都应有稳定 ID，例如 `IDEA-001`。
- idea 应先说明 hypothesis、baseline、variant、控制变量和成功标准，再进入实验。
- 如果 idea 还不清楚，先按 `harness/onboarding/questions.md` 的 Idea Validation 部分逐步确认。
- 新增、删除或实质修改 `index.jsonl` 中的 idea 前，agent 必须先停下来向用户确认。
- 请求确认时必须说明拟登记的 idea、证据或来源、目标文件和后续验证计划。
- 未确认的想法只能写在实验记录或临时草稿中，并标为 `provisional`。
- `feature-list.json` 用来拆任务；`ideas/` 用来说明为什么这些任务值得做。
- 实验记录应引用相关 idea ID，例如 `--tag idea=IDEA-001` 或在记录中写明 `Idea: IDEA-001`。
- idea 状态建议使用 `proposed`、`testing`、`validated`、`rejected`、`superseded`。

## 推荐流程

1. 在 `index.jsonl` 登记 idea。
2. 复制 `idea-template.md` 写清背景、假设和验证计划。
3. 在 `feature-list.json` 拆出可执行任务。
4. 用 `harness/scripts/harness_run.py` 记录实验。
5. 用 comparison 和 finding 固化可复用结论。
