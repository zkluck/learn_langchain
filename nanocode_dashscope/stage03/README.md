# Stage 03: Shell 与搜索工具

实现更丰富的工具集：glob 搜索、文本 grep、bash 命令执行。

## 目标

- `glob`: 使用通配符列出文件
- `grep`: 在文件中查找匹配的文本
- `bash`: 执行受限 shell 命令并返回输出、错误、退出码

## 运行

```bash
python main.py
```

## 预期输出

```
=== nanocode_dashscope Stage 03: Shell 与搜索工具 ===

--- glob 示例 ---
找到 3 个文件:
README.md
stage00/main.py
...

--- grep 示例 ---
找到 1 个匹配:
README.md:1: # nanocode_dashscope

--- bash 示例 ---
输出:
README.md
stage00
stage01
...
退出码: 0
```
