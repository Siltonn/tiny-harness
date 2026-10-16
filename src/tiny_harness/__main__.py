import asyncio
import sys

from tiny_harness.engine.loop import run
from tiny_harness.provider.anthropic import AnthropicProvider


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit('用法: tiny-harness "你的问题"')

    prompt = " ".join(sys.argv[1:])
    print(asyncio.run(run(AnthropicProvider(), prompt)))


if __name__ == "__main__":
    main()
