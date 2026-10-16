# tiny-harness

用 Python 从零实现一个 LLM agent harness，用于学习和研究。整体结构参考 go-tiny-claw。

## 运行

需要 [uv](https://docs.astral.sh/uv/)。在 `.env` 里配置哪家的 API key，就使用哪家的 provider：

```bash
cp .env.example .env   # 然后填写 API key
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
├── config.py        # 统一的环境变量配置
├── schema/          # 组件之间传递的标准数据结构
├── engine/          # MainLoop 核心实现
├── provider/        # 大模型接口抽象与具体厂商 SDK 实现
└── tools/           # 工具注册表接口
```
