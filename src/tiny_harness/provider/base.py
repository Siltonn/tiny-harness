from typing import Protocol


class Provider(Protocol):
    """大模型接口抽象。engine 只依赖这个协议，不直接接触厂商 SDK。"""

    async def complete(self, prompt: str) -> str: ...
