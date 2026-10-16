from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """所有环境变量配置的唯一入口。从进程环境变量和 .env 读取，进程环境变量优先。"""

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    # Provider 凭据：配置了哪家，就使用哪家
    anthropic_api_key: SecretStr | None = None
