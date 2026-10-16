import asyncio
import logging
import sys
from pathlib import Path

from tiny_harness.config import Settings
from tiny_harness.engine.loop import AgentEngine
from tiny_harness.provider.base import ProviderError
from tiny_harness.provider.factory import create_provider
from tiny_harness.tools.registry import ToolRegistry

log = logging.getLogger(__name__)


async def amain(task: str) -> None:
    # 0. 加载配置（环境变量 + .env）
    settings = Settings()

    # 1. 初始化模型 Provider（大脑）
    provider = create_provider(settings)

    # 2. 初始化 Tool Registry（手脚）
    registry = ToolRegistry()
    # TODO: registry.register(BashTool())

    # TODO: 3. 初始化上下文管理器（内存管理器，context/）
    # ctx_manager = ContextManager(...)

    # 4. 组装并启动核心 Engine（操作系统心脏），以当前目录作为工作区
    # TODO: 注入 ctx_manager
    engine = AgentEngine(provider, registry, work_dir=Path.cwd())

    log.info("开始执行任务...")
    await engine.run(task)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        sys.exit('用法: tiny-harness "你的任务"')

    task = " ".join(sys.argv[1:])
    try:
        asyncio.run(amain(task))
    except ProviderError as e:
        log.error("运行失败: %s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
