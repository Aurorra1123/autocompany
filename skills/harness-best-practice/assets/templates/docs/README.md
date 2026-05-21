# Docs System

本目录分为两层：

- `reference/`：原始输入、历史资料和外部参考
- `plans/`、`progress/`、`standards/`、`adr/`、`architecture/`、`verification/`、`exec-plan/`：执行层

## 目录说明

- `reference/`：需求原文、PDF、截图、旧文档、外部导出资料
- `plans/`：任务拆解、里程碑、待办状态
- `progress/`：会话级进度记录和交接信息
- `standards/`：长期有效的工程规则、协作规则、部署基线
- `adr/`：架构与流程决策记录
- `architecture/`：正式技术方案、架构图、环境核查
- `verification/`：验证证据、测试摘要、截图和回归结果
- `exec-plan/`：阶段性执行计划

## 推荐工作流

1. 先阅读 `progress/agent-progress.md` 和 `plans/feature-list.json`
2. 盘点已有资料并整理到 `reference/`
3. 确认当前最高优先级且边界清晰的目标
4. 小步修改
5. 保存最小必要验证证据
6. 更新进度文档与任务状态
7. 提交 git commit 并保持仓库可继续工作

## 当前目标

当前仓库的首要目标是把 `{{PROJECT_NAME}}` 的长期知识、计划、规则和验证沉淀为可维护、可交接、可审查的 docs harness。
