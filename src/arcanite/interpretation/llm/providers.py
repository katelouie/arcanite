"""
Arcanite LLM Providers

Implementations for different LLM backends: Anthropic, OpenAI, and local (Ollama).
"""

import os
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Literal

# Lazy imports for optional dependencies
_anthropic = None
_openai = None
_httpx = None


def _get_anthropic():
    global _anthropic
    if _anthropic is None:
        try:
            import anthropic
            _anthropic = anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install arcanite[llm]"
            )
    return _anthropic


def _get_openai():
    global _openai
    if _openai is None:
        try:
            import openai
            _openai = openai
        except ImportError:
            raise ImportError(
                "openai package not installed. Install with: pip install arcanite[llm]"
            )
    return _openai


def _get_httpx():
    global _httpx
    if _httpx is None:
        try:
            import httpx
            _httpx = httpx
        except ImportError:
            raise ImportError(
                "httpx package not installed. Install with: pip install arcanite[llm]"
            )
    return _httpx


@dataclass
class LLMResponse:
    """Response from an LLM completion."""

    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = ""

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """
        Get a completion from the LLM.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            LLMResponse with content and metadata
        """
        ...

    async def complete_stream(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """
        Get a streaming completion from the LLM.

        Default implementation falls back to non-streaming.
        Override in subclasses for true streaming support.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Yields:
            Chunks of the response as they arrive
        """
        response = await self.complete(prompt, system, temperature, max_tokens)
        yield response.content

    @property
    @abstractmethod
    def model_name(self) -> str:
        """The model name/identifier."""
        ...


@dataclass
class BaseLLMProvider(LLMProvider):
    """Base class with common configuration."""

    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4000
    api_key: str | None = None

    @property
    def model_name(self) -> str:
        return self.model


@dataclass
class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    model: str = "claude-sonnet-4-20250514"
    api_key: str | None = field(default=None)

    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY env var or pass api_key."
            )

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        anthropic = _get_anthropic()
        client = anthropic.AsyncAnthropic(api_key=self.api_key)

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system:
            kwargs["system"] = system

        response = await client.messages.create(**kwargs)

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason or "",
        )

    async def complete_stream(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        anthropic = _get_anthropic()
        client = anthropic.AsyncAnthropic(api_key=self.api_key)

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system:
            kwargs["system"] = system

        async with client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text


@dataclass
class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider (GPT-4, etc.)."""

    model: str = "gpt-4o"
    api_key: str | None = field(default=None)
    base_url: str | None = None

    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key."
            )

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        openai = _get_openai()

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        client = openai.AsyncOpenAI(**client_kwargs)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )

        choice = response.choices[0]
        usage = response.usage

        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            stop_reason=choice.finish_reason or "",
        )

    async def complete_stream(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        openai = _get_openai()

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        client = openai.AsyncOpenAI(**client_kwargs)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


@dataclass
class LocalProvider(BaseLLMProvider):
    """
    Local LLM provider via OpenAI-compatible API (Ollama, llama.cpp, etc.).

    Uses the OpenAI client with a custom base_url.
    """

    model: str = "llama3.2"
    base_url: str = "http://localhost:11434/v1"  # Ollama default
    api_key: str = "ollama"  # Ollama doesn't need a real key

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        openai = _get_openai()

        client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )

        choice = response.choices[0]
        usage = response.usage

        return LLMResponse(
            content=choice.message.content or "",
            model=self.model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            stop_reason=choice.finish_reason or "",
        )

    async def complete_stream(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        openai = _get_openai()

        client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def get_provider(
    provider: Literal["anthropic", "openai", "local"] = "anthropic",
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4000,
) -> LLMProvider:
    """
    Factory function to create an LLM provider.

    Args:
        provider: Which provider to use
        model: Model name (uses provider default if not specified)
        api_key: API key (uses env var if not specified)
        base_url: Base URL for API (mainly for local providers)
        temperature: Default temperature
        max_tokens: Default max tokens

    Returns:
        Configured LLMProvider instance
    """
    if provider == "anthropic":
        kwargs = {"temperature": temperature, "max_tokens": max_tokens}
        if model:
            kwargs["model"] = model
        if api_key:
            kwargs["api_key"] = api_key
        return AnthropicProvider(**kwargs)

    elif provider == "openai":
        kwargs = {"temperature": temperature, "max_tokens": max_tokens}
        if model:
            kwargs["model"] = model
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            kwargs["base_url"] = base_url
        return OpenAIProvider(**kwargs)

    elif provider == "local":
        kwargs = {"temperature": temperature, "max_tokens": max_tokens}
        if model:
            kwargs["model"] = model
        if base_url:
            kwargs["base_url"] = base_url
        if api_key:
            kwargs["api_key"] = api_key
        return LocalProvider(**kwargs)

    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'anthropic', 'openai', or 'local'.")
