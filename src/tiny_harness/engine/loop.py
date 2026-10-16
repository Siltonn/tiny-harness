import json
import logging
from pathlib import Path

from tiny_harness.provider.base import LLMProvider
from tiny_harness.schema.message import Message, Role
from tiny_harness.tools.registry import Registry

log = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are tiny-harness, an expert coding assistant. "
    "You have full access to tools in the workspace."
)


class AgentEngine:
    """微型 OS 的核心驱动。"""

    def __init__(self, provider: LLMProvider, registry: Registry, work_dir: Path) -> None:
        self.provider = provider
        self.registry = registry
        # 工作区：Agent 必须有一个明确的物理边界
        self.work_dir = work_dir

    async def run(self, user_prompt: str) -> None:
        """启动 Agent 的生命周期。"""
        log.info("[Engine] 引擎启动，锁定工作区: %s", self.work_dir)

        # 1. 初始化会话的上下文。以后由动态 Prompt 组装器加载 AGENTS.md，目前先硬编码
        history = [
            Message(role=Role.SYSTEM, content=SYSTEM_PROMPT),
            Message(role=Role.USER, content=user_prompt),
        ]

        # 2. Main Loop：心跳开始（标准的 ReAct 循环）
        turn = 0
        while True:
            turn += 1
            log.info("========== [Turn %d] 开始 ==========", turn)

            available_tools = self.registry.get_available_tools()

            log.info("[Engine] 正在思考 (Reasoning)...")
            reply = await self.provider.generate(history, available_tools)

            # 模型的响应完整追加到历史中（raw 里的 thinking 块也一并保留）
            history.append(reply)

            # 纯文本通常是模型的思考过程，或是最终结果
            if reply.content:
                print(f"🤖 模型: {reply.content}", flush=True)

            # 3. 退出条件：模型没有请求任何工具调用，说明它认为任务已经完成
            if not reply.tool_calls:
                log.info("[Engine] 任务完成，退出循环。")
                break

            # 4. 执行行动（Action），获取观察结果（Observation）
            log.info("[Engine] 模型请求调用 %d 个工具...", len(reply.tool_calls))
            for call in reply.tool_calls:
                arguments = json.dumps(call.arguments, ensure_ascii=False)
                log.info("  -> 🛠️ 执行工具: %s, 参数: %s", call.name, arguments)

                # 通过 Registry 路由并执行底层工具
                result = await self.registry.execute(call)

                if result.is_error:
                    log.warning("  -> ❌ 工具执行报错: %s", result.output)
                else:
                    log.info("  -> ✅ 工具执行成功（返回 %d 个字符）", len(result.output))

                # 观察结果封装为 user 消息追加到历史中。
                # 注意：tool_call_id 必须携带！这是维系大模型推理链条的关键
                history.append(Message(role=Role.USER, content=result.output, tool_call_id=call.id))

            # 回到循环开头，模型带着新加入的 Observation 继续下一轮思考
