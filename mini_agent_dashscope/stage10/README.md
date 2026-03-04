# Stage 10：总验收（进阶）

## 目标

- 一次性验证 Stage02/06/07/08
- 可选验证 Stage09（依赖本机已安装 `mini-agent`）

## 运行

```bash
python mini_agent_dashscope/stage10/main.py
```

严格模式（Stage09 失败也算整体失败）：

```bash
python mini_agent_dashscope/stage10/main.py --strict-mini-agent
```

## 验收

- 默认模式显示 `ALL REQUIRED CHECKS PASSED`
- 严格模式在 `mini-agent` 可用时显示 `ALL CHECKS PASSED`
