# Stage 01: 文件读写工具

实现基础的文件读取和写入工具，展示如何使用 Python 标准库进行文件操作。

## 目标

- 实现 `read` 工具：读取文件内容并显示行号
- 实现 `write` 工具：将内容写入文件
- 添加错误处理（文件不存在、权限问题等）

## 运行

```bash
python main.py
```

## 预期输出

```
=== nanocode_dashscope Stage 01: 文件读写工具 ===

--- 测试 write 工具 ---
[OK] 写入文件: test.txt (内容: Hello, World!)

--- 测试 read 工具 ---
文件内容: test.txt
1: Hello, World!

--- 工具定义 ---
read: 读取文件内容
write: 写入文件内容
```
