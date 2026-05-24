# AutoCompany

把团队的长期知识沉淀在仓库里，而不是每个人各自的 Agent 聊天记录里。

本仓库的核心产物是一个名为 **super-harness** 的 skill，位于 [`skills/super-harness/`](./skills/super-harness/)。

## 解决什么问题

### 从一个人多Agent开发

哪怕只有你一个人在写代码，今天的 AI 编程 Agent 已经不再是"开一次聊天就能搞定"的工具。一个稍微复杂一点的项目里，你会在不同窗口、不同 IDE、不同模型之间来回切换，而**每一次新会话都是从零开始的**。这背后有几个相当硬的事实：

1. **Session 是有限的。** Agent 的能力和它当前的 Context 紧密耦合，而任何上下文窗口（128K / 200K / 1M）都会被长任务耗尽；一旦触发压缩或重置，信息就开始丢失。
2. **沉淀已验证的核心上下文。** 我们希望把最关键、且**已经被验证过**的判断（架构决策、踩坑结论、验证证据、当前进度）显式地落到仓库的固定位置，而不是留在某一次聊天里——下次新开窗口，它们依然在。
3. **仓库是唯一的记录系统。** 用 OpenAI 那篇博客的原话讲："从智能体的角度来看，它在运行时无法在情境中访问的任何内容都是不存在的。" 散落在聊天、Google Docs、个人脑子里的知识，对下一个 Agent 会话来说统统不存在。
4. **渐进式披露（Progressive Disclosure）。** 新会话不应该被一份冗长的总文档淹没。`AGENTS.md` 只做一个稳定的短入口，由它指向 `harness/` 下分门别类的内容；Agent 按当前任务的需要再深入对应文档，既能拿到所需上下文，又能把工作窗口留给真正的代码任务。

### 再到多个人多Agent信息沟通

把上面这套放大到团队、公司或课题组之后，问题不会变简单，反而会再叠加几层：

- **每个人的 Agent 都看不到彼此的进度和决策。** 同事昨晚跟 Claude Code 讨论出来的架构选型、上周修一个 bug 时踩过的坑，下一个人开会话的时候完全获取不到。
- **多套 IDE 入口文件各写各的，规则容易漂移。** Claude Code 用 `CLAUDE.md`、Codex 用 `AGENTS.md`、Cursor 用 `.cursor/rules/`，每个人维护自己那份，团队规则很快就不一致了。
- **任务状态变更缺乏协调。** "这个功能做完了吗 / 谁在做 / 验证了没有" 这种问题，如果只靠聊天对齐，跨人、跨分支很快就会乱。

super-harness 的思路是把上面两层痛点一次性收拢：**把仓库本身当作团队 Agent 的共享记忆体**——所有 IDE 入口都指向同一份 `harness/`，所有人的 Agent 在开始工作前先读它，进度、决策、验证证据、任务认领也都在这里留痕。

## 能做什么

在任意目标仓库里跑一次 bootstrap 脚本，就会生成下面这套最小可用的协作骨架：

```
target-repo/
├── AGENTS.md                          # 入口（仅做导航）
├── CLAUDE.md                          # Claude Code 入口 → 指向 AGENTS.md
├── .cursor/rules/super-harness.mdc    # Cursor 入口 → 指向 AGENTS.md
└── harness/
    ├── plans/
    │   ├── feature-list.json          # 结构化任务清单，带通过状态和 owner
    │   ├── progress.md                # 会话进度 / 交接记录
    │   └── exec-plan/                 # 阶段性执行方案
    ├── standards/                     # 长期工程规则、git workflow、agent 规则
    ├── architecture/
    │   └── adr/                       # 架构决策记录
    ├── verification/                  # 验证证据（截图、日志、报告）
    └── reference/                     # 原始输入材料、外部资料
```

具体能力：

- **多 IDE 入口自动检测**：`--ide auto` 默认根据已有标记（`CLAUDE.md`、`.claude/`、`.cursor/`、`AGENTS.md`）只补缺失的入口；空仓库则一次性生成全部三种入口。可用 `--ide all|none|claude,codex` 等手动覆盖。
- **单一信息源**：所有 IDE 入口都是短 stub，统一指向 `AGENTS.md` 和 `harness/` 下的真实内容；规则改一处即可。
- **任务状态闭环**：`feature-list.json` 里的 `passes` 字段必须有 `harness/verification/` 中的证据支撑，并在 `progress.md` 留下变更说明，才能改为通过。
- **多人协作软约束**：每条任务带 `owner` 字段做软认领；ADR 文件名带日期前缀避免不同分支撞编号；冲突时优先合并 progress 记录。
- **幂等**：默认 `if_missing`，不会覆盖已有文件；需要强覆盖时显式加 `--force`。

## 怎么用

直接用自然语言让你的 Coding Agent（Claude Code / Codex / Cursor 等）帮你装并启动它就行，不需要手动跑命令。例如：

> 请帮我安装并启用这个 skill：https://github.com/Aurorra1123/autocompany

或者已经在目标仓库里，想直接初始化：

> 请用 super-harness 在当前仓库里初始化一套团队共享的 harness 结构。

Agent 会自己读 [`skills/super-harness/SKILL.md`](./skills/super-harness/SKILL.md) 里的说明，把模板生成到你的仓库里，并根据已有的 IDE 标记决定该补哪些入口文件。

生成完成后，让 Agent 按照 [`skills/super-harness/references/blueprint.md`](./skills/super-harness/references/blueprint.md) 里的「Adaptation Checklist」把模板内容替换成你仓库的真实信息即可。

## 参考资料

super-harness 的设计直接对应了近期两份业界实践的核心结论：

- **Anthropic — [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)（2025-11）**
  提出长任务必须跨多个上下文窗口推进，每次新会话都从零开始。其解决方式是用 *initializer + coding agent* 双角色结构，把外部工件（progress 文件、git 历史、结构化 feature list）当作 Agent 的记忆体；每次会话先重读这些工件再开工。super-harness 的 `harness/plans/feature-list.json` 和 `harness/plans/progress.md` 即对应这一模式。

- **OpenAI — [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)（2026-02）**
  记录了一支团队用 Codex 五个月内交付 ~100 万行、零手写代码的过程。两个关键结论：
  - *"从智能体的角度来看，它在运行时无法在情境中访问的任何内容都是不存在的。"* —— 仓库即唯一记录系统，散落在聊天 / Google Docs / 个人脑中的知识对 Agent 不可见。
  - **渐进式披露（Progressive Disclosure）**：*"智能体从一个小而稳定的切入点开始，并被指导下一步该去哪里查看，而不是一开始就被淹没。"* 因此 `AGENTS.md` 应当只做约 100 行的"目录页"，把 Agent 引到结构化的设计文档、执行计划、参考资料等深层来源。super-harness 的 `AGENTS.md`-as-stub + `harness/{plans,standards,architecture,verification,reference}/` 分层就是这种结构的直接落地。

两篇博客的共同结论是：**真正决定长任务可靠性的不是模型本身，而是包裹模型的 harness——仓库结构、文档分层、执行规则、验证证据**。super-harness 把这套约束打包成一份可一键生成的模板，让中小团队也能用得起。
