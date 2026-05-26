# Harness System

本目录分为五类信息：

- `onboarding/`：首次接手或初始化仓库时的问题清单和输出落位规则
- `project/`：仓库最高层背景、目标、边界和成功标准
- `ideas/`：待验证的 idea、hypothesis、baseline、variant 和成功标准
- `reference/`：原始输入、历史资料和外部参考
- `plans/`、`scripts/`、`standards/`、`architecture/`、`verification/`：执行、规则和证据层

## 目录说明

- `onboarding/`：guided onboarding 问题清单，帮助 agent 先扫描 repo、再逐步确认项目目标和验证主线
- `project/`：repo-level brief，回答当前仓库最终要完成什么、什么不是目标、如何判断成功
- `ideas/`：idea registry 和 idea template，连接项目目标、任务拆解、实验和 reviewed finding
- `reference/`：需求原文、PDF、截图、旧文档、外部导出资料
- `plans/`：任务清单（`feature-list.json`）、高层 checkpoint / 交接索引（`progress.md`）、阶段执行计划（`exec-plan/`）
- `scripts/`：协作自动化脚本，例如统一实验入口 `harness_run.py`、实验记录器 `record_experiment.py`、对比生成器 `compare_experiments.py`、finding 晋升器 `promote_finding.py` 和旧进度压缩器 `compact_progress.py`
- `standards/`：长期有效的工程规则、协作规则、部署基线
- `architecture/`：正式技术方案、架构图、环境核查；其中 `architecture/adr/` 存放架构与流程决策记录
- `verification/`：验证证据、实验记录、对比结论、审核 finding、测试摘要、截图和回归结果

## 推荐工作流

1. 先阅读 `onboarding/questions.md`，扫描 repo 并判断项目背景是否仍是模板
2. 阅读 `project/brief.md`，确认 repo-level 目标和非目标
3. 阅读 `ideas/index.jsonl`、`plans/progress.md` 和 `plans/feature-list.json`
4. 如果 `progress.md` 已经变成流水账，先运行 `python3 harness/scripts/compact_progress.py --dry-run`，确认后再压缩归档
5. 如目标、idea 或任务仍不清楚，按 onboarding 问题一次问一个关键问题，并把答案写回正式文件
6. 盘点已有资料并整理到 `reference/`
7. 确认当前最高优先级且边界清晰的 idea、任务或验证目标
8. 小步修改
9. 保存最小必要验证证据；实验或 benchmark 优先用 `python3 harness/scripts/harness_run.py --title "..." -- <command>` 包住命令
10. 更新任务状态；只有 milestone、handoff、重要结论或 blocker 才更新 `progress.md`
11. 如需要比较不同实验，用 `python3 harness/scripts/compare_experiments.py --title "..." --evidence <record-id>` 生成对比结论
12. 对经过审核的结论，用 `python3 harness/scripts/promote_finding.py --title "..." --comparison <comparison-id>` 晋升到 findings
13. 提交 git commit 并保持仓库可继续工作

## 当前目标

当前仓库的首要目标是把 `autocompany` 的项目背景、idea 验证主线、长期知识、计划、规则和验证证据沉淀为可维护、可交接、可审查的 harness。
