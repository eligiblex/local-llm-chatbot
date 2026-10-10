"""Ollama client and conversation utilities."""

from __future__ import annotations

import os
from collections.abc import Iterable, Iterator

DEFAULT_SYSTEM_PROMPT = "你是一个友好、准确的中文助手。不确定时明确说明，不编造事实。"


def trim_history(messages: list[dict[str, str]], max_messages: int = 20) -> list[dict[str, str]]:
    """Keep the system prompt plus the most recent conversation messages."""
    if max_messages < 1:
        raise ValueError('max_messages 必须大于 0')
    system = [message.copy() for message in messages if message.get("role") == "system"][:1]
    dialogue = [message for message in messages if message.get("role") != "system"]
    dialogue = [message.copy() for message in dialogue[-max_messages:]]
    # Never send an orphaned assistant reply at the beginning of the window.
    while dialogue and dialogue[0]['role'] != 'user':
        dialogue.pop(0)
    return system + dialogue


class OllamaChatService:
    def __init__(self, host: str | None = None, model: str | None = None, *, client=None) -> None:
        import ollama

        self.host = host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")
        self.client = client if client is not None else ollama.Client(host=self.host, timeout=120)

    def stream_reply(self, messages: Iterable[dict[str, str]]) -> Iterator[str]:
        stream = self.client.chat(
            model=self.model,
            messages=list(messages),
            stream=True,
        )
        try:
            for chunk in stream:
                message = getattr(chunk, "message", None)
                content = getattr(message, "content", None)
                if content is None and isinstance(chunk, dict):
                    content = chunk.get("message", {}).get("content")
                if content:
                    yield content
        finally:
            close = getattr(stream, 'close', None)
            if close:
                close()
