from typing import Protocol

from tiny_harness.schema.message import Message, ToolDefinition


class ProviderError(Exception):
    """provider 层的统一错误。各厂商 SDK 的异常都转换成它，上层不需要认识具体 SDK。"""


class RefusalError(ProviderError):
    """模型出于安全策略拒绝了请求。"""


class LLMProvider(Protocol):
    """与大模型通信的统一契约。engine 只依赖这个协议，不直接接触厂商 SDK。"""

    async def generate(
        self, messages: list[Message], available_tools: list[ToolDefinition]
    ) -> Message:
        """接收当前的上下文历史和可用工具列表，发起一次大模型推理。"""
        ...
