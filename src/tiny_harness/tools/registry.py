from typing import Protocol

from tiny_harness.schema.message import ToolCall, ToolDefinition, ToolResult


class Registry(Protocol):
    """工具的注册与分发执行接口。"""

    def get_available_tools(self) -> list[ToolDefinition]:
        """返回当前系统挂载的所有可用工具的 Schema。"""
        ...

    async def execute(self, call: ToolCall) -> ToolResult:
        """实际执行模型请求的工具，并返回结果。"""
        ...


class ToolRegistry:
    """Registry 的默认实现。目前还没有挂载任何工具。"""

    # TODO: register(tool)，挂载 BashTool 等具体工具

    def get_available_tools(self) -> list[ToolDefinition]:
        return []

    async def execute(self, call: ToolCall) -> ToolResult:
        return ToolResult(tool_call_id=call.id, output=f"未知工具: {call.name}", is_error=True)
