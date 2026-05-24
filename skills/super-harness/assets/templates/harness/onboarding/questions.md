# Onboarding Questions

这些问题用于把一个新仓库从“只有代码和聊天上下文”整理成可交接、可验证的 harness。agent 不应机械照读全部问题；应先扫描 repo，再一次问一个最关键的问题。

## 0. Repo Scan

先从仓库中提取初稿，不要直接问用户：

- 主要语言、框架、入口文件、测试命令和运行方式是什么？
- README、docs、issues、examples、notebooks 或 scripts 里是否说明了目标？
- 最近 git commit 暗示当前在做什么？
- 是否已经存在实验、benchmark、eval、日志、报告或结果表？
- 是否已有 AGENTS、CLAUDE、Cursor rules 或旧项目管理文档？

## 1. Project Frame

用于更新 `harness/project/brief.md`：

1. 这个 repo 最终要完成什么？
2. 当前阶段更像哪一种：prototype、feature development、idea validation、refactor、performance work、production hardening？
3. 当前阶段最重要的成功标准是什么？
4. 明确不在当前阶段目标内的 non-goals 是什么？
5. 主要使用者、reviewer 或决策人是谁？
6. 有哪些必须遵守的环境、数据、合规、成本或时间约束？

## 2. Idea Validation

用于更新 `harness/ideas/index.jsonl` 和后续 idea 文档：

1. 当前最重要的 idea 或 hypothesis 是什么？
2. baseline 是什么？
3. variant 或 new approach 是什么？
4. 哪些控制变量必须保持一致？
5. 用哪些 metric 判断是否支持该 hypothesis？
6. 什么结果说明 idea 不成立、需要回滚或需要重新定义？
7. 是否已有相关实验、对比、报告或口头结论需要补录？

## 3. Work Breakdown

用于更新 `harness/plans/feature-list.json`：

1. 当前最小可执行目标是什么？
2. 它对应哪些验收标准？
3. 哪些任务必须先完成，哪些可以并行？
4. 哪些任务需要实验或 benchmark 支撑？
5. 谁是 owner，或者暂时无人认领？

## 4. Evidence Plan

用于规划 `harness/verification/`：

1. 下一个最小可验证实验是什么？
2. 需要记录哪些 input、config、dataset、seed、traffic profile、环境或 artifact？
3. 哪些指标必须机器可读？
4. 哪些结论需要 comparison 后才能相信？
5. 什么条件下 finding 可以进入 `reviewed` 状态？

## 5. Output Contract

onboarding 结束后，agent 应更新：

- `harness/project/brief.md`：真实项目目标、当前阶段、non-goals、users、success criteria、constraints。
- `harness/ideas/index.jsonl`：至少一条真实 idea，或明确记录暂无可验证 idea。
- `harness/plans/feature-list.json`：把 starter backlog 替换为当前 repo 的真实任务和验收标准。
- `harness/plans/progress.md`：追加 onboarding 摘要、assumptions、open questions 和下一步。

如果用户只给出部分信息，先写入已确认内容，并把未确认内容列为 open questions。
