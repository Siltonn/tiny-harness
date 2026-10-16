import logging

from tiny_harness.config import Settings
from tiny_harness.provider.anthropic import AnthropicProvider
from tiny_harness.provider.base import LLMProvider, ProviderError

log = logging.getLogger(__name__)


def create_provider(settings: Settings) -> LLMProvider:
    """配置里有哪家的 API key，就创建哪家的 provider。"""
    if settings.anthropic_api_key:
        log.info("使用 provider: anthropic")
        return AnthropicProvider(api_key=settings.anthropic_api_key.get_secret_value())

    raise ProviderError("没有找到可用的 provider，请在 .env 中设置: ANTHROPIC_API_KEY")
