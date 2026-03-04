# Stage 05：Skills 机制

## 目标

- 理解 Skills 的渐进披露设计
- 掌握 `get_skill` 的按需加载方式

## 实践步骤

1. 初始化技能库

```bash
git submodule update --init --recursive
```

2. 启动 Agent，观察 skills metadata 注入

- 查看启动日志中 Skills 加载条目
- 查看 system prompt 中 `{SKILLS_METADATA}` 的替换行为

3. 在任务中触发技能

- 让 Agent 先 `list/识别` 可用技能
- 再调用 `get_skill(skill_name)` 获取完整说明

## 关键知识点

- Level 1：只注入技能元数据（省 token）
- Level 2：按需加载技能全文
- Level 3+：技能内脚本/文档路径自动改写为绝对路径

## 验收标准

- 能成功触发至少一个技能加载
- 能解释为什么这套机制比“全量注入所有 SKILL.md”更稳

## 对应源码

- `mini_agent/tools/skill_loader.py`
- `mini_agent/tools/skill_tool.py`
- `mini_agent/config/system_prompt.md`
