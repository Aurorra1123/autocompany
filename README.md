# AutoCompany

把团队的长期知识沉淀在仓库里，而不是每个人各自的 Agent 聊天记录里。

本仓库的核心产物是一个名为 **super-harness** 的 skill，位于 [`skills/super-harness/`](./skills/super-harness/)。

## 仓库目标

AutoCompany 的目标是构建一套 repo-local 的协作与验证框架，让人和 AI Agent 在同一个仓库里持续推进复杂工作，而不是依赖分散的聊天记录。

这个仓库最终要产出的是一个可复用、可安装、可复制到其他项目中的 **super-harness** skill。它会在目标仓库中生成一套标准结构，用来记录项目目标、idea 和 hypothesis、任务计划、执行进度、实验过程、对比分析、审核结论和长期工程规则。

它不限定于基础模型研发，也适用于任何需要验证 idea 的项目：例如实现一个新功能、比较两个技术方案、做 ablation、跑 benchmark、整理多人实验结论，或者把探索性方向沉淀成可审查的团队知识。

最终判断这个 repo 是否成功，不是看它是否生成了一组文件，而是看它能否让一个新的人或新的 Agent 打开目标仓库后，快速知道：当前项目想完成什么、已经做过哪些尝试、哪些实验支持哪些结论、哪些结论经过 review、下一步应该继续验证什么。

## 解决什么问题

现在的 AI 编程 Agent（Claude Code、Codex、Cursor 等）几乎都是面向个人开发者的：每个人的上下文都活在自己的聊天记录里。在团队、公司或课题组中，这会带来几个直接的痛点：

- 同一个仓库里，不同人的 Agent 看不到彼此的进度和决策
- 重要的架构判断、踩过的坑、验证证据等只留在某一次会话里，下次别人接手只能从头摸索
- 不同 IDE / Agent（Claude Code 用 `CLAUDE.md`、Codex 用 `AGENTS.md`、Cursor 用 `.cursor/rules/`）各写一份入口文件，规则容易漂移

super-harness 的思路：**把仓库本身当作团队 Agent 的共享记忆体**，所有人的 Agent 都先读这套结构再开始工作。

## 能做什么

在任意目标仓库里跑一次 bootstrap 脚本，就会生成下面这套最小可用的协作骨架：

```
target-repo/
├── AGENTS.md                          # 入口（仅做导航）
├── CLAUDE.md                          # Claude Code 入口 → 指向 AGENTS.md
├── .cursor/rules/super-harness.mdc    # Cursor 入口 → 指向 AGENTS.md
└── harness/
    ├── project/
    │   └── brief.md                   # repo-level 目标、边界和成功标准
    ├── ideas/
    │   ├── index.jsonl                # idea / hypothesis 索引
    │   └── idea-template.md           # 新 idea 模板
    ├── plans/
    │   ├── feature-list.json          # 结构化任务清单，带通过状态和 owner
    │   ├── progress.md                # 会话进度 / 交接记录
    │   └── exec-plan/                 # 阶段性执行方案
    ├── standards/                     # 长期工程规则、git workflow、agent 规则
    ├── architecture/
    │   └── adr/                       # 架构决策记录
    ├── verification/                  # 实验、对比、finding 和验证证据
    │   ├── experiments/
    │   ├── comparisons/
    │   └── findings/
    └── reference/                     # 原始输入材料、外部资料
```

具体能力：

- **多 IDE 入口自动检测**：`--ide auto` 默认根据已有标记（`CLAUDE.md`、`.claude/`、`.cursor/`、`AGENTS.md`）只补缺失的入口；空仓库则一次性生成全部三种入口。可用 `--ide all|none|claude,codex` 等手动覆盖。
- **单一信息源**：所有 IDE 入口都是短 stub，统一指向 `AGENTS.md` 和 `harness/` 下的真实内容；规则改一处即可。
- **repo-level 背景**：`harness/project/brief.md` 记录仓库目标、非目标、当前重点、使用者、约束和成功标准。
- **idea 验证索引**：`harness/ideas/` 记录 hypothesis、baseline、variant、控制变量和成功标准，避免实验只剩命令日志。
- **任务状态闭环**：`feature-list.json` 里的 `passes` 字段必须有 `harness/verification/` 中的证据支撑，并在 `progress.md` 留下变更说明，才能改为通过。
- **实验到结论的证据链**：实验记录进入 `experiments/`，跨实验分析进入 `comparisons/`，审核后的团队结论进入 `findings/`。
- **多人协作软约束**：每条任务带 `owner` 字段做软认领；ADR 文件名带日期前缀避免不同分支撞编号；冲突时优先合并 progress 记录。
- **幂等**：默认 `if_missing`，不会覆盖已有文件；需要强覆盖时显式加 `--force`。

## 怎么用

### 方式一：作为 Claude Code Skill

把 `skills/super-harness/` 复制到你的 skills 目录后，在 Claude Code 里调用即可：

```
/super-harness
```

### 方式二：直接跑脚本

```bash
# 干跑，先看会做什么
python3 skills/super-harness/scripts/bootstrap_harness.py --dry-run /path/to/repo

# 实际写入
python3 skills/super-harness/scripts/bootstrap_harness.py /path/to/repo

# 只生成 Claude Code 和 Codex 入口，跳过 Cursor
python3 skills/super-harness/scripts/bootstrap_harness.py --ide claude,codex /path/to/repo
```

生成完成后，按照 [`skills/super-harness/references/blueprint.md`](./skills/super-harness/references/blueprint.md) 里的「Adaptation Checklist」把模板内容替换成你仓库的真实信息。

## 参考资料

设计思路结合了下面两篇博客：

- Anthropic — [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- OpenAI — [Harness engineering](https://openai.com/zh-Hans-CN/index/harness-engineering/)
