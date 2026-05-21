# 协作规范

## 目标

将长期有效的信息沉淀到仓库中，而不是停留在聊天记录里。

## 开始工作前

- 先阅读 `docs/progress/agent-progress.md`
- 先阅读 `docs/plans/feature-list.json`
- 如仓库已有最近 git 历史，先确认当前基线
- 每次只推进一个高优先级且边界清晰的目标

## 文档落位

- 长期规则写入 `docs/standards/`
- 重要决策写入 `docs/adr/`
- 会话交接写入 `docs/progress/agent-progress.md`
- 任务状态写入 `docs/plans/feature-list.json`
- 验证证据写入 `docs/verification/`
- 原始资料和外部输入放在 `docs/reference/`

## 执行规则

- `AGENTS.md` 只做入口、约束和导航，不做完整知识库
- 不要把关键背景只留在聊天中
- 未验证前不要标记任务完成
- 发现重复性问题时，优先补规则、模板或脚本
- 如目标较大，先给出方案，再执行

## 会话结束前

- 更新 `docs/progress/agent-progress.md`
- 更新对应任务状态
- 记录验证证据或缺失原因
- 保持仓库处于可继续工作的状态
