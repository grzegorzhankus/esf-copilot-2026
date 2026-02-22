"""Configuration management for esf-copilot-2026.

Loads settings from environment variables and .env file.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    # Load .env file if it exists
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, use environment variables only
    pass

# Streamlit Cloud: load secrets into environment variables
try:
    import streamlit as st
    for key, value in st.secrets.items():
        if isinstance(value, str) and key not in os.environ:
            os.environ[key] = value
except Exception:
    pass


class Config:
    """Application configuration."""

    # LLM Settings
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_NIM_URL: str = os.getenv("NVIDIA_NIM_URL", "https://integrate.api.nvidia.com/v1")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL: Optional[str] = os.getenv("LLM_MODEL")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))

    # Application Settings
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    CONFIGS_DIR: Path = BASE_DIR / "configs"
    DATA_DIR: Path = BASE_DIR / "data"

    @classmethod
    def is_nvidia_nim_configured(cls) -> bool:
        """Check if NVIDIA NIM is properly configured."""
        return bool(cls.NVIDIA_API_KEY)

    @classmethod
    def get_model_display_name(cls, model_value: str) -> str:
        """Get user-friendly model name."""
        model_names = {
            "meta/llama-4-maverick-instruct": "Llama 4 Maverick (405B)",
            "deepseek/deepseek-v3": "DeepSeek V3 (685B)",
            "mistralai/mistral-large-3-instruct": "Mistral Large 3 (123B)",
            "qwen/qwen3-72b-instruct": "Qwen3 (72B)",
            "llama3.1:8b": "Llama 3.1 (8B - Local)",
            "deepseek-coder:6.7b": "DeepSeek Coder (6.7B - Local)",
            "mistral:7b": "Mistral (7B - Local)",
        }
        return model_names.get(model_value, model_value)


# Global config instance
config = Config()
