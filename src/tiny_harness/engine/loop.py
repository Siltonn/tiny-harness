from tiny_harness.provider.base import Provider


async def run(provider: Provider, prompt: str) -> str:
    """MainLoop 入口。目前只调用一次模型；加入工具后会变成 tool_use 循环。"""
    return await provider.complete(prompt)
