from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """运行时配置。两套千帆/百度凭证分别覆盖 LLM 与语音服务。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 千帆大模型平台 (LLM, v2 OpenAI 兼容, Bearer 鉴权)
    qianfan_api_key: str = ""
    qianfan_base_url: str = "https://qianfan.baidubce.com/v2"
    qianfan_model: str = "ernie-4.5-turbo-128k"

    # 百度智能云语音 (ASR/TTS, API_KEY + SECRET_KEY -> access_token)
    baidu_speech_api_key: str = ""
    baidu_speech_secret_key: str = ""

    # 服务端
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def has_llm(self) -> bool:
        return bool(self.qianfan_api_key)

    @property
    def has_speech(self) -> bool:
        return bool(self.baidu_speech_api_key and self.baidu_speech_secret_key)


settings = Settings()
