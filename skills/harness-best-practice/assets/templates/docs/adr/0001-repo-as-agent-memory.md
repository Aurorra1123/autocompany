# ADR 0001: Use The Repository As Agent Memory

## Status

Accepted

## Context

agent 在跨会话工作时没有稳定的长期记忆。如果任务状态、设计意图和规则只存在于聊天记录中，后续会话会重复探索、误判完成状态，或者在不完整上下文下继续修改。

## Decision

将仓库作为 agent 协作的主记忆体，至少维护以下工件：

- `docs/progress/agent-progress.md`：会话进度与交接
- `docs/plans/feature-list.json`：任务列表与完成状态
- `docs/standards/`：长期有效的工程规则
- `docs/adr/`：重要设计决策

## Consequences

- 关键知识可被版本化、审查和追踪
- 新会话能够快速恢复上下文
- 需要额外维护这些文档，但可显著降低重复劳动和漂移
