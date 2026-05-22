# Harness System

本目录分为两层：

- `reference/`：原始输入、历史资料和外部参考
- `plans/`、`standards/`、`architecture/`、`verification/`：执行层

## 目录说明

- `reference/`：需求原文、PDF、截图、旧文档、外部导出资料
- `plans/`：任务清单（`feature-list.json`）、会话进度日志（`progress.md`）、阶段执行计划（`exec-plan/`）
- `scripts/`：协作自动化脚本，例如统一实验入口 `harness_run.py`、实验记录器 `record_experiment.py`、对比生成器 `compare_experiments.py` 和 finding 晋升器 `promote_finding.py`
- `standards/`：长期有效的工程规则、协作规则、部署基线
- `architecture/`：正式技术方案、架构图、环境核查；其中 `architecture/adr/` 存放架构与流程决策记录
- `verification/`：验证证据、实验记录、对比结论、审核 finding、测试摘要、截图和回归结果

## 推荐工作流

1. 先阅读 `plans/progress.md` 和 `plans/feature-list.json`
2. 盘点已有资料并整理到 `reference/`
3. 确认当前最高优先级且边界清晰的目标
4. 小步修改
5. 保存最小必要验证证据；实验或 benchmark 优先用 `python3 harness/scripts/harness_run.py --title "..." -- <command>` 包住命令
6. 更新进度文档与任务状态
7. 如需要比较不同实验，用 `python3 harness/scripts/compare_experiments.py --title "..." --evidence <record-id>` 生成对比结论
8. 对经过审核的结论，用 `python3 harness/scripts/promote_finding.py --title "..." --comparison <comparison-id>` 晋升到 findings
9. 提交 git commit 并保持仓库可继续工作

## 当前目标

当前仓库的首要目标是把 `{{PROJECT_NAME}}` 的长期知识、计划、规则和验证沉淀为可维护、可交接、可审查的 harness。
