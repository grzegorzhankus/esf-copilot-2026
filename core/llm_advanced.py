"""Advanced LLM integration for DGX Spark with support for SOTA models.

This module provides a unified interface for multiple LLM backends:
- NVIDIA NIM (recommended for DGX Spark)
- Ollama (local fallback)
- OpenAI-compatible APIs
- HuggingFace models

Optimized for NVIDIA Grace Blackwell architecture.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Find .env file in project root
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not installed, rely on system environment variables


class LLMBackend(Enum):
    """Supported LLM backends."""
    NVIDIA_NIM = "nvidia_nim"
    OLLAMA = "ollama"
    OPENAI_COMPATIBLE = "openai"
    HUGGINGFACE = "huggingface"


class LLMModel(Enum):
    """Available models optimized for financial analysis."""
    # NVIDIA NIM models (recommended for DGX Spark)
    # Large models for complex reasoning
    LLAMA_3_1_405B = "meta/llama-3.1-405b-instruct"
    LLAMA_3_3_70B = "meta/llama-3.3-70b-instruct"
    MISTRAL_LARGE_3 = "mistralai/mistral-large-3-675b-instruct-2512"
    DEEPSEEK_V3 = "deepseek-ai/deepseek-v3.2"
    DEEPSEEK_R1 = "deepseek-ai/deepseek-r1"
    QWEN3_235B = "qwen/qwen3-235b-a22b"

    # Medium models (good balance)
    LLAMA_3_1_70B = "meta/llama-3.1-70b-instruct"
    MISTRAL_LARGE_2 = "mistralai/mistral-large-2-instruct"
    NEMOTRON_70B = "nvidia/llama-3.1-nemotron-70b-instruct"

    # Smaller/faster models
    LLAMA_3_1_8B = "meta/llama-3.1-8b-instruct"
    MISTRAL_SMALL = "mistralai/mistral-small-24b-instruct"
    QWEN2_5_7B = "qwen/qwen2.5-7b-instruct"

    # Ollama models (local fallback)
    OLLAMA_LLAMA_3_1_8B = "llama3.1:8b"
    OLLAMA_DEEPSEEK_CODER = "deepseek-coder:6.7b"
    OLLAMA_MISTRAL_7B = "mistral:7b"


@dataclass
class LLMConfig:
    """LLM configuration."""
    backend: LLMBackend
    model: LLMModel
    base_url: str
    api_key: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4096
    timeout: int = 60


class AdvancedLLMClient:
    """Unified LLM client with support for multiple backends.

    Automatically detects available hardware and selects optimal configuration.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize LLM client.

        Args:
            config: Optional LLM configuration. If None, auto-detects best available.
        """
        self.config = config or self._auto_detect_config()
        self._validate_backend()

    def _auto_detect_config(self) -> LLMConfig:
        """Auto-detect best available LLM configuration for current hardware."""
        # Check for NVIDIA NIM (best for DGX Spark)
        if self._check_nvidia_nim():
            return LLMConfig(
                backend=LLMBackend.NVIDIA_NIM,
                model=LLMModel.LLAMA_3_3_70B,  # Best balance of speed and quality
                base_url=os.getenv("NVIDIA_NIM_URL", "https://integrate.api.nvidia.com/v1"),
                api_key=os.getenv("NVIDIA_API_KEY"),
                temperature=0.1,
                max_tokens=4096
            )

        # Fallback to Ollama
        if self._check_ollama():
            return LLMConfig(
                backend=LLMBackend.OLLAMA,
                model=LLMModel.OLLAMA_LLAMA_3_1_8B,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0.1
            )

        raise RuntimeError(
            "No LLM backend available. Please install Ollama or configure NVIDIA NIM."
        )

    def _check_nvidia_nim(self) -> bool:
        """Check if NVIDIA NIM is available."""
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            return False

        try:
            url = os.getenv("NVIDIA_NIM_URL", "https://integrate.api.nvidia.com/v1")
            response = requests.get(
                f"{url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            response = requests.get(f"{base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def _validate_backend(self):
        """Validate that selected backend is available."""
        if self.config.backend == LLMBackend.NVIDIA_NIM:
            if not self._check_nvidia_nim():
                raise RuntimeError(
                    "NVIDIA NIM not available. Set NVIDIA_API_KEY environment variable."
                )
        elif self.config.backend == LLMBackend.OLLAMA:
            if not self._check_ollama():
                raise RuntimeError(
                    "Ollama not available. Install from https://ollama.ai"
                )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text using configured LLM.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt for context.
            temperature: Override default temperature.
            max_tokens: Override default max tokens.
            **kwargs: Additional backend-specific parameters.

        Returns:
            Generated text response.
        """
        if self.config.backend == LLMBackend.NVIDIA_NIM:
            return self._generate_nvidia_nim(
                prompt, system_prompt, temperature, max_tokens, **kwargs
            )
        elif self.config.backend == LLMBackend.OLLAMA:
            return self._generate_ollama(
                prompt, system_prompt, temperature, max_tokens, **kwargs
            )
        else:
            raise NotImplementedError(f"Backend {self.config.backend} not implemented")

    def _generate_nvidia_nim(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        """Generate using NVIDIA NIM API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model.value,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            **kwargs
        }

        response = requests.post(
            f"{self.config.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        """Generate using Ollama API."""
        payload = {
            "model": self.config.model.value,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature or self.config.temperature,
                "num_predict": max_tokens or self.config.max_tokens
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        response = requests.post(
            f"{self.config.base_url}/api/generate",
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()

        result = response.json()
        return result["response"]

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Multi-turn chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            temperature: Override default temperature.
            max_tokens: Override default max tokens.
            **kwargs: Additional parameters.

        Returns:
            Assistant's response.
        """
        if self.config.backend == LLMBackend.NVIDIA_NIM:
            return self._chat_nvidia_nim(messages, temperature, max_tokens, **kwargs)
        elif self.config.backend == LLMBackend.OLLAMA:
            # Ollama doesn't have native chat API, convert to single prompt
            prompt = self._messages_to_prompt(messages)
            return self._generate_ollama(prompt, None, temperature, max_tokens, **kwargs)
        else:
            raise NotImplementedError(f"Backend {self.config.backend} not implemented")

    def _chat_nvidia_nim(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        """Chat using NVIDIA NIM API."""
        payload = {
            "model": self.config.model.value,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            **kwargs
        }

        response = requests.post(
            f"{self.config.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to single prompt for non-chat APIs."""
        prompt_parts = []
        for msg in messages:
            role = msg["role"].upper()
            content = msg["content"]
            prompt_parts.append(f"[{role}]: {content}")
        return "\n\n".join(prompt_parts)

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.

        Returns:
            Dictionary with model information.
        """
        return {
            "backend": self.config.backend.value,
            "model": self.config.model.value,
            "base_url": self.config.base_url,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }


def create_financial_analyst_prompt(
    language: str = "en",
    analysis_data: Optional[Dict[str, Any]] = None
) -> str:
    """Create system prompt for financial analysis.

    Args:
        language: Language code ('en' or 'pl').
        analysis_data: Optional analysis data to include in context.

    Returns:
        System prompt string.
    """
    if language == "pl":
        base_prompt = """Jesteś ekspertem ds. analizy finansowej specjalizującym się w polskich sprawozdaniach finansowych.

Twoje kompetencje:
- Analiza sprawozdań finansowych (bilans, rachunek zysków i strat, przepływy pieniężne)
- Obliczanie i interpretacja wskaźników finansowych (rentowność, płynność, zadłużenie)
- Identyfikacja sygnałów ostrzegawczych (red flags)
- Prognozowanie wyników finansowych
- Ocena kondycji finansowej przedsiębiorstw
- Znajomość polskich przepisów rachunkowości

Odpowiadaj precyzyjnie, profesjonalnie i w języku polskim. Podawaj konkretne liczby i wskaźniki.
Jeśli nie masz pewności, wyraźnie to zaznacz."""
    else:
        base_prompt = """You are a financial analysis expert specializing in Polish financial statements.

Your expertise:
- Financial statement analysis (balance sheet, P&L, cash flows)
- Calculation and interpretation of financial ratios (profitability, liquidity, leverage)
- Red flag identification
- Financial forecasting
- Corporate financial health assessment
- Knowledge of Polish accounting regulations

Respond precisely, professionally, and in English. Provide specific numbers and ratios.
If uncertain, clearly indicate this."""

    if analysis_data:
        context = f"\n\nCurrent Analysis Context:\n{_format_analysis_context(analysis_data)}"
        return base_prompt + context

    return base_prompt


def _format_analysis_context(data: Dict[str, Any]) -> str:
    """Format analysis data for prompt context."""
    parts = []

    if "metrics" in data:
        parts.append("Base Metrics:")
        for key, value in data["metrics"].items():
            parts.append(f"  - {key}: {value}")

    if "kpis" in data:
        parts.append("\nKPIs:")
        for kpi in data["kpis"]:
            parts.append(f"  - {kpi.get('name', kpi['key'])}: {kpi['value']} {kpi['unit']}")

    if "red_flags" in data:
        detected = [rf for rf in data["red_flags"] if rf.get("detected")]
        if detected:
            parts.append(f"\nRed Flags Detected: {len(detected)}")
            for rf in detected:
                parts.append(f"  - {rf['title']} ({rf['severity']})")

    return "\n".join(parts)


# Convenience function for easy migration from existing code
def get_llm_client(preferred_model: Optional[str] = None) -> AdvancedLLMClient:
    """Get configured LLM client.

    Args:
        preferred_model: Optional model name to use (e.g., "llama-4-maverick").

    Returns:
        Configured AdvancedLLMClient instance.
    """
    if preferred_model:
        # Map friendly names to enum
        model_map = {
            # Large models
            "llama-405b": LLMModel.LLAMA_3_1_405B,
            "llama-3.1-405b": LLMModel.LLAMA_3_1_405B,
            "llama-70b": LLMModel.LLAMA_3_3_70B,
            "llama-3.3-70b": LLMModel.LLAMA_3_3_70B,
            "deepseek": LLMModel.DEEPSEEK_V3,
            "deepseek-v3": LLMModel.DEEPSEEK_V3,
            "deepseek-r1": LLMModel.DEEPSEEK_R1,
            "mistral": LLMModel.MISTRAL_LARGE_3,
            "mistral-large": LLMModel.MISTRAL_LARGE_3,
            "qwen": LLMModel.QWEN3_235B,
            "qwen3": LLMModel.QWEN3_235B,
            # Medium models
            "nemotron": LLMModel.NEMOTRON_70B,
            "nemotron-70b": LLMModel.NEMOTRON_70B,
            # Small/fast models
            "llama-8b": LLMModel.LLAMA_3_1_8B,
            "mistral-small": LLMModel.MISTRAL_SMALL,
            "qwen-7b": LLMModel.QWEN2_5_7B,
        }

        model = model_map.get(preferred_model.lower())
        if model:
            # Check if NVIDIA NIM is available
            client = AdvancedLLMClient()
            if client.config.backend == LLMBackend.NVIDIA_NIM:
                client.config.model = model
            return client

    # Auto-detect best configuration
    return AdvancedLLMClient()
