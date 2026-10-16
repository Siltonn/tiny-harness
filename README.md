# tiny-harness

用 Python 从零实现一个 LLM agent harness，用于学习和研究。整体结构参考 go-tiny-claw。

## 运行

需要 [uv](https://docs.astral.sh/uv/) 和 Anthropic API 凭据：

```bash
export ANTHROPIC_API_KEY=...
uv run tiny-harness "你好"
```

## 开发

```bash
uv run ruff format
uv run ruff check --fix
```

## 结构

```
src/tiny_harness/
├── __main__.py      # 程序入口
├── engine/          # MainLoop 核心实现
└── provider/        # 大模型接口抽象与具体厂商 SDK 实现
```
