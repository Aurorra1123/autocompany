# Git Workflow

## 分支建议

- 默认主分支使用 `main`
- 复杂任务可使用短生命周期分支

## 提交原则

- 一次提交只解决一个小问题
- 提交必须对应可解释的进度变化
- 不把多个无关改动混进同一个提交

## 提交信息格式

推荐格式：

```text
type(scope): summary
```

示例：

```text
docs(harness): bootstrap docs execution layer
docs(progress): record repository baseline
chore(repo): align AGENTS and standards
```

## 每次会话的最小流程

1. 阅读 `git log --oneline -20`
2. 阅读 `docs/progress/agent-progress.md`
3. 阅读 `docs/plans/feature-list.json`
4. 选择一个任务推进
5. 修改文件并自检
6. 更新进度文档
7. 提交 git commit

## 禁止事项

- 不要在没有说明的情况下一次提交大量无关文件
- 不要跳过进度记录直接结束会话
- 不要把聊天中的关键决策留在聊天里而不写入仓库
