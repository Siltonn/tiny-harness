import anthropic

MODEL = "claude-opus-5-5"
MAX_TOKENS = 16000


class RefusalError(Exception):
    """模型出于安全策略拒绝了请求（stop_reason == "refusal"）。"""


class AnthropicProvider:
    def __init__(self, model: str = MODEL) -> None:
        # 凭据从环境读取：ANTHROPIC_API_KEY，或 `ant auth login` 的 profile
        self.client = anthropic.AsyncAnthropic()
        self.model = model

    async def complete(self, prompt: str) -> str:
        response = await self.client.beta.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            output_config={"effort": "medium"},
            # 被安全分类器拒绝时，由服务端按拒绝类别自动换模型重试
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": prompt}],
        )

        if response.stop_reason == "refusal":
            details = response.stop_details
            category = details.category if details else None
            raise RefusalError(f"模型拒绝了请求（category={category}）")

        return "".join(block.text for block in response.content if block.type == "text")
