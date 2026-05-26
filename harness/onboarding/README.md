# Onboarding

本目录用于首次初始化或接手仓库时，引导人和 agent 明确 repo-level 背景、当前目标、待验证 idea 和下一步实验。

## 文件

- `questions.md`：交互式 onboarding 问题清单和输出落位规则。

## 使用规则

- 新仓库初始化 harness 后，优先完成 onboarding，再开始大规模修改。
- agent 应先扫描仓库已有代码、文档、测试和 git 历史，给出可验证的初稿，再向用户逐步确认。
- 每次只问一个关键问题；不要一次性要求用户填写完整问卷。
- onboarding 结果必须落到正式文件，不要只留在聊天中：
  - `harness/project/brief.md`
  - `harness/ideas/index.jsonl`
  - `harness/plans/feature-list.json`
  - `harness/plans/progress.md`
- 如果信息不足，明确写成 assumption 或 open question；只有会影响后续交接的内容才写入 `progress.md` checkpoint。
