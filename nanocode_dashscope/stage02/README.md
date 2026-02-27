# Stage 02: 文本编辑工具

在上一阶段文件读写的基础上，加入「查找并替换」能力，模拟编辑器功能。

## 目标

- 复用 `read`/`write`，实现 `edit` 工具
- 支持查找目标文本并替换为新内容
- 提供错误提示：文件不存在、未找到目标文本等

## 运行

```bash
python main.py
```

## 预期输出

```
=== nanocode_dashscope Stage 02: 文本编辑工具 ===

--- 初始内容 ---
1: TODO: replace me
2: 第二行保持不变

--- 执行 edit 工具 ---
✓ 成功替换文本: TODO: replace me -> DONE

--- 编辑后内容 ---
1: DONE
2: 第二行保持不变
```
