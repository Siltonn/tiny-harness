from typing import Any

import anthropic
from anthropic.types.beta import BetaMessage, BetaMessageParam, BetaToolParam

from tiny_harness.provider.base import ProviderError, RefusalError
from tiny_harness.schema.message import Message, Role, ToolCall, ToolDefinition

MODEL = "claude-opus-5-5"
MAX_TOKENS = 16000


class AnthropicProvider:
    def __init__(self, api_key: str, model: str = MODEL) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate(
        self, messages: list[Message], available_tools: list[ToolDefinition]
    ) -> Message:
        system, params = _to_anthropic_messages(messages)
        tools = [_to_anthropic_tool(tool) for tool in available_tools]

        try:
            response = await self.client.beta.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                output_config={"effort": "medium"},
                # 被安全分类器拒绝时，由服务端按拒绝类别自动换模型重试
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                system=system or anthropic.omit,
                tools=tools or anthropic.omit,
                messages=params,
            )
        except anthropic.APIError as e:
            raise ProviderError(f"Anthropic API 调用失败: {e}") from e

        if response.stop_reason == "refusal":
            details = response.stop_details
            category = details.category if details else None
            raise RefusalError(f"模型拒绝了请求（category={category}）")

        return _from_anthropic_response(response)


def _to_anthropic_messages(messages: list[Message]) -> tuple[str, list[BetaMessageParam]]:
    """标准消息 -> Anthropic 消息。开头的 system 消息放进顶层的 system 参数。"""
    system_parts: list[str] = []
    params: list[Any] = []

    for msg in messages:
        if msg.role == Role.SYSTEM and not params:
            system_parts.append(msg.content)
        elif msg.role == Role.ASSISTANT:
            # 自己产生的消息原样回传：thinking 块必须一字不改地送回去
            content = msg.raw if msg.raw is not None else _assistant_blocks(msg)
            params.append({"role": "assistant", "content": content})
        elif msg.tool_call_id is not None:
            block = {"type": "tool_result", "tool_use_id": msg.tool_call_id, "content": msg.content}
            # 并行调用的多个结果必须合并进同一条 user 消息
            last = params[-1] if params else None
            if last and last["role"] == "user" and isinstance(last["content"], list):
                last["content"].append(block)
            else:
                params.append({"role": "user", "content": [block]})
        else:
            params.append({"role": msg.role.value, "content": msg.content})

    return "\n\n".join(system_parts), params


def _assistant_blocks(msg: Message) -> list[dict[str, Any]]:
    """没有 raw（比如历史来自别的 provider）时，用标准字段重建 assistant 内容。"""
    blocks: list[dict[str, Any]] = []
    if msg.content:
        blocks.append({"type": "text", "text": msg.content})
    for call in msg.tool_calls:
        blocks.append(
            {"type": "tool_use", "id": call.id, "name": call.name, "input": call.arguments}
        )
    return blocks


def _to_anthropic_tool(tool: ToolDefinition) -> BetaToolParam:
    return {"name": tool.name, "description": tool.description, "input_schema": tool.input_schema}


def _from_anthropic_response(response: BetaMessage) -> Message:
    """Anthropic 响应 -> 标准消息。完整的 content 保存在 raw 里，供下一轮原样回传。"""
    text = "".join(block.text for block in response.content if block.type == "text")
    tool_calls = [
        ToolCall(id=block.id, name=block.name, arguments=block.input)
        for block in response.content
        if block.type == "tool_use"
    ]
    return Message(role=Role.ASSISTANT, content=text, tool_calls=tool_calls, raw=response.content)
