# ADR 0002: Adopt A Harness-First Agent Workflow

## Status

Accepted

## Context

仅靠聊天记录驱动长周期 agent 协作，会导致上下文丢失、重复探索、误判完成状态，以及规则漂移。当前仓库需要一套以仓库工件为中心的稳定工作方式。

## Decision

采用以仓库工件为中心的 harness-first 工作流，要求：

- 长期知识必须写入仓库并纳入版本控制
- `AGENTS.md` 作为入口和导航，不承载完整知识库
- 每次会话开始先读取进度、任务列表和近期历史
- 每次只推进一个清晰且高优先级的目标
- 完成状态必须建立在最小必要验证之上
- 重复性问题通过规则、模板、脚本或 CI 约束修复

具体执行规则维护在 `docs/standards/agent-harness-rules.md`。

## Consequences

- 跨会话恢复成本下降
- 聊天记录不再承担长期记忆职责
- 规则与决策来源更清晰，可审查、可追踪
- 文档维护成本会增加，但可显著降低返工和漂移
