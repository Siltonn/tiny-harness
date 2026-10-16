"""系统的统一血液：各组件（大模型、工具、主循环）之间传递的标准数据结构。

不同厂商的 API 格式各不相同，engine 只认识这里的类型，格式转换由各 provider 负责。
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Role(StrEnum):
    """消息的角色，这是与大模型沟通的基石。"""

    SYSTEM = "system"  # 系统提示词：确立 Agent 的性格与红线
    USER = "user"  # 用户输入 / 工具执行的返回结果（Observation）
    ASSISTANT = "assistant"  # 模型的输出：包含推理（Reasoning）或工具调用（ToolCall）


@dataclass
class ToolCall:
    """模型请求调用某个具体的工具。"""

    id: str  # 工具调用的唯一 ID
    name: str  # 想要调用的工具名称（例如 "bash"）
    arguments: dict[str, Any]  # 已解析的 JSON 参数，由具体工具负责校验


@dataclass
class Message:
    """上下文中传递的单条消息。"""

    role: Role
    content: str = ""  # 纯文本内容

    # 模型决定调用工具时填充（支持并行调用多个工具）
    tool_calls: list[ToolCall] = field(default_factory=list)

    # 如果这是对某个工具调用的响应，必须填写，告诉模型它对应哪一次调用
    tool_call_id: str | None = None

    # 产生这条消息的 provider 的原始内容（例如 Claude 的 thinking 块）。
    # 只由该 provider 在下一轮原样回传，engine 不读取它。
    raw: Any = field(default=None, repr=False, compare=False)


@dataclass
class ToolResult:
    """工具在本地执行完毕后返回的结果。"""

    tool_call_id: str
    output: str  # 工具执行的控制台输出或报错堆栈
    is_error: bool = False  # 标记是否失败，供后续的错误自愈使用


@dataclass
class ToolDefinition:
    """工具的元信息，让模型理解这个工具有什么用。"""

    name: str
    description: str
    input_schema: dict[str, Any]  # JSON Schema
