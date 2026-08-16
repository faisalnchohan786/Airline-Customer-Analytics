"""Small Ollama client wrapper used by the analytics assistant."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class OllamaUnavailableError(RuntimeError):
    """Raised when the local Ollama service or Python package is unavailable."""


@dataclass(frozen=True)
class OllamaModel:
    """A locally available Ollama model."""

    name: str


def _load_ollama():
    try:
        import ollama  # type: ignore
    except ImportError as exc:
        raise OllamaUnavailableError(
            "The Python 'ollama' package is not installed. Run `pip install -r requirements.txt`."
        ) from exc
    return ollama


def _model_name(item: object) -> str | None:
    """Extract a model name across Ollama client response versions."""
    if isinstance(item, dict):
        return item.get("model") or item.get("name")
    return getattr(item, "model", None) or getattr(item, "name", None)


def list_models() -> list[str]:
    """Return locally installed Ollama model names."""
    ollama = _load_ollama()
    try:
        response = ollama.list()
    except Exception as exc:
        raise OllamaUnavailableError(
            "Ollama is not reachable. Start Ollama locally, then refresh this page."
        ) from exc

    items: Iterable[object]
    if isinstance(response, dict):
        items = response.get("models", [])
    else:
        items = getattr(response, "models", [])

    return sorted({name for item in items if (name := _model_name(item))})


def chat(model: str, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
    """Send a grounded chat request to a local Ollama model."""
    if not model:
        raise ValueError("An Ollama model name is required.")
    ollama = _load_ollama()
    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            options={"temperature": temperature},
        )
    except Exception as exc:
        raise OllamaUnavailableError(
            f"Could not query Ollama model '{model}'. Confirm Ollama is running and the model is installed."
        ) from exc

    if isinstance(response, dict):
        content = response.get("message", {}).get("content")
    else:
        message = getattr(response, "message", None)
        content = getattr(message, "content", None)
    if not content:
        raise RuntimeError("Ollama returned an empty response.")
    return str(content).strip()
