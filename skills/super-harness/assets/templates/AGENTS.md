# 协作规范

## 目标

将长期有效的信息沉淀到仓库中，而不是停留在聊天记录里。

## 开始工作前

- 先阅读 `harness/onboarding/questions.md`
- 先阅读 `harness/project/brief.md`
- 先阅读 `harness/ideas/index.jsonl`
- 先阅读 `harness/plans/progress.md`
- 先阅读 `harness/plans/feature-list.json`
- 如仓库已有最近 git 历史，先确认当前基线
- 每次只推进一个高优先级且边界清晰的目标

## 文档落位

- 首次接手仓库的问题、假设和输出落位规则写入 `harness/onboarding/`
- repo-level 目标、边界和成功标准写入 `harness/project/brief.md`
- idea、hypothesis、baseline、variant 和成功标准写入 `harness/ideas/`
- 长期规则写入 `harness/standards/`
- 重要决策写入 `harness/architecture/adr/`
- 高层 checkpoint、阶段交接、重要风险和 open questions 写入 `harness/plans/progress.md`
- 任务状态写入 `harness/plans/feature-list.json`
- 验证证据写入 `harness/verification/`
- 实验过程和结果写入 `harness/verification/experiments/`
- 跨实验对比结论写入 `harness/verification/comparisons/`
- 审核后的团队结论写入 `harness/verification/findings/`
- 原始资料和外部输入放在 `harness/reference/`

## 执行规则

- `AGENTS.md` 只做入口、约束和导航，不做完整知识库
- 不要把关键背景只留在聊天中
- `progress.md` 是 checkpoint log，不是流水账；详细实验、对比和结论分别放在 `verification/experiments/`、`comparisons/`、`findings/`
- 如果 `project/brief.md`、`ideas/index.jsonl` 或 `feature-list.json` 仍是模板内容，先按 `harness/onboarding/questions.md` 执行 guided onboarding
- onboarding 时先扫描仓库，再一次问一个关键问题；确认后的答案必须写回 `project/`、`ideas/`、`plans/` 和 `progress.md`
- 未验证前不要标记任务完成
- 运行实验、benchmark、训练、评测或关键验证命令时，优先使用 `python3 harness/scripts/harness_run.py --title "..." -- <command>` 记录
- 实验如属于某个 idea，记录时使用 `--tag idea=IDEA-001` 或在结果说明中引用 idea ID
- 对比不同人或不同分支的实验时，使用 `python3 harness/scripts/compare_experiments.py --title "..." --evidence <record-id-or-path> ...` 生成带依据链接的结论
- 审核后的 solid conclusion 必须用 `python3 harness/scripts/promote_finding.py --title "..." --comparison <comparison-id>` 晋升到 findings
- 发现重复性问题时，优先补规则、模板或脚本
- 如目标较大，先给出方案，再执行

## 会话结束前

- 如形成 milestone、handoff、重要结论或 blocker，更新 `harness/plans/progress.md`
- 更新对应任务状态
- 记录验证/实验依据或缺失原因
- 保持仓库处于可继续工作的状态
