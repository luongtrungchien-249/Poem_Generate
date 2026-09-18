
from adapters.llm.openai import OpenAIClient


class VLLMClient(OpenAIClient):
    """vLLM self-hosted inference client using OpenAI-compatible endpoints."""

    def __init__(self, base_url: str, api_key: str = "EMPTY") -> None:
        # Endpoint do composition root truyền vào; adapter không đọc môi trường.
        super().__init__(api_key=api_key, base_url=base_url)
