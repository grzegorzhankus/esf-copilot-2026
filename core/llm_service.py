"""
LLM service module for cfo-copilot.

Handles all interactions with Ollama LLM including:
- Chat completions with timeout and error handling
- Context building from parsed financial statements
- Prompt engineering for board memos and financial analysis
"""

import json
import logging
import os
from typing import Any, Dict, Iterator, List, Optional

import requests

# Set up logger using Python's built-in logging
logger = logging.getLogger(__name__)


# Default configuration
DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
DEFAULT_OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
DEFAULT_OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "4096"))
DEFAULT_OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "2048"))
DEFAULT_TIMEOUT = 120  # seconds


class OllamaError(Exception):
    """Base exception for Ollama service errors."""
    pass


class OllamaTimeoutError(OllamaError):
    """Raised when Ollama request times out."""
    pass


class OllamaConnectionError(OllamaError):
    """Raised when cannot connect to Ollama service."""
    pass


def list_ollama_models(base_url: str = DEFAULT_OLLAMA_URL) -> List[str]:
    """
    List available models from Ollama.

    Args:
        base_url: Ollama API base URL

    Returns:
        List of model names available in Ollama

    Raises:
        OllamaConnectionError: If cannot connect to service
        OllamaError: For other API errors
    """
    url = base_url.rstrip("/") + "/api/tags"

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        models = [m["name"] for m in data.get("models", [])]
        logger.info(f"Found {len(models)} models in Ollama")
        return models
    except requests.exceptions.ConnectionError as e:
        logger.warning(f"Cannot connect to Ollama at {base_url}")
        raise OllamaConnectionError(f"Cannot connect to Ollama at {base_url}") from e
    except requests.exceptions.RequestException as e:
        logger.error(f"Error listing Ollama models: {e}")
        raise OllamaError(f"Error listing Ollama models: {e}") from e
    except (ValueError, KeyError) as e:
        logger.error(f"Invalid response format from Ollama: {e}")
        raise OllamaError(f"Invalid response format: {e}") from e


def ollama_chat(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_OLLAMA_MODEL,
    temperature: float = DEFAULT_OLLAMA_TEMPERATURE,
    num_predict: int = DEFAULT_OLLAMA_NUM_PREDICT,
    num_ctx: int = DEFAULT_OLLAMA_NUM_CTX,
    base_url: str = DEFAULT_OLLAMA_URL,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """
    Send chat completion request to Ollama.

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name (e.g., 'llama3.1:8b')
        temperature: Sampling temperature (0.0-1.0)
        num_predict: Max tokens to generate
        num_ctx: Context window size
        base_url: Ollama API base URL
        timeout: Request timeout in seconds

    Returns:
        LLM response content string

    Raises:
        OllamaTimeoutError: If request times out
        OllamaConnectionError: If cannot connect to service
        OllamaError: For other API errors
    """
    logger.info(f"Sending chat request to Ollama (model={model}, messages={len(messages)})")
    logger.debug(f"Request params: temp={temperature}, num_predict={num_predict}, timeout={timeout}s")

    url = base_url.rstrip("/") + "/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.Timeout as e:
        logger.error(f"Ollama request timed out after {timeout}s")
        raise OllamaTimeoutError(f"Ollama request timed out after {timeout}s") from e
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Cannot connect to Ollama at {base_url}")
        raise OllamaConnectionError(f"Cannot connect to Ollama at {base_url}") from e
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API error: {e}")
        raise OllamaError(f"Ollama API error: {e}") from e

    try:
        data = resp.json()
        msg = (data.get("message") or {}).get("content")
        if not msg:
            logger.error("LLM response missing content")
            raise OllamaError("LLM response did not include message content")

        logger.info(f"Ollama response received ({len(msg)} chars)")
        return msg
    except (ValueError, KeyError) as e:
        logger.error(f"Invalid response format from Ollama: {e}")
        raise OllamaError(f"Invalid response format from Ollama: {e}") from e


def ollama_chat_stream(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_OLLAMA_MODEL,
    temperature: float = DEFAULT_OLLAMA_TEMPERATURE,
    num_predict: int = DEFAULT_OLLAMA_NUM_PREDICT,
    num_ctx: int = DEFAULT_OLLAMA_NUM_CTX,
    base_url: str = DEFAULT_OLLAMA_URL,
    timeout: int = DEFAULT_TIMEOUT,
) -> Iterator[str]:
    """
    Stream chat completion from Ollama for real-time display.

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name (e.g., 'llama3.1:8b')
        temperature: Sampling temperature (0.0-1.0)
        num_predict: Max tokens to generate
        num_ctx: Context window size
        base_url: Ollama API base URL
        timeout: Request timeout in seconds

    Yields:
        String chunks of the response as they're generated

    Raises:
        OllamaTimeoutError: If request times out
        OllamaConnectionError: If cannot connect to service
        OllamaError: For other API errors

    Example:
        >>> for chunk in ollama_chat_stream(messages, model="llama3.1:8b"):
        ...     print(chunk, end='', flush=True)
    """
    logger.info(f"Starting streaming chat (model={model}, messages={len(messages)})")
    logger.debug(f"Stream params: temp={temperature}, num_predict={num_predict}, timeout={timeout}s")

    url = base_url.rstrip("/") + "/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,  # Enable streaming
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
        },
    }

    try:
        resp = requests.post(url, json=payload, stream=True, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.Timeout as e:
        logger.error(f"Ollama streaming request timed out after {timeout}s")
        raise OllamaTimeoutError(f"Ollama request timed out after {timeout}s") from e
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Cannot connect to Ollama at {base_url}")
        raise OllamaConnectionError(f"Cannot connect to Ollama at {base_url}") from e
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama streaming API error: {e}")
        raise OllamaError(f"Ollama API error: {e}") from e

    try:
        total_chars = 0
        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if chunk := data.get("message", {}).get("content"):
                        total_chars += len(chunk)
                        yield chunk

                    # Check if stream is done
                    if data.get("done", False):
                        logger.info(f"Streaming completed ({total_chars} chars)")
                        break

                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to decode streaming chunk: {e}")
                    continue

    except Exception as e:
        logger.error(f"Error during streaming: {e}")
        raise OllamaError(f"Streaming error: {e}") from e


def build_llm_context(parsed: Dict[str, Any], cf_labels: Optional[Dict[str, str]] = None) -> str:
    """
    Build compact numeric context for LLM from parsed financial statement.

    Creates a text summary of key financial figures suitable for LLM prompt.
    Used by both board memo generation and interactive chat.

    Args:
        parsed: Parsed financial statement dict from fs_parser
        cf_labels: Optional dict mapping cash flow keys to labels

    Returns:
        Multi-line text context string with company info, figures, and ratios
    """
    meta = parsed["meta"]
    n = parsed["numbers"]
    r = parsed["ratios"]

    rzis_variant = meta.get("rzis_variant")
    rzis_kalk = parsed.get("rzis_kalk", {})
    rzis_por = parsed.get("rzis_por", {})

    if rzis_variant == "porownawczy":
        pl = rzis_por or rzis_kalk
        keys_for_summary = ["A", "C", "F", "N"]  # revenue, profit on sales, EBIT, net profit
    else:
        pl = rzis_kalk or rzis_por
        keys_for_summary = ["A", "C", "I", "O"]  # revenue, GP, EBIT, net profit

    cf = parsed.get("cashflow", {})

    lines = []
    lines.append(f"Company: {meta.get('company')}")
    lines.append(f"Period: {meta.get('okres_od')} to {meta.get('okres_do')}")
    lines.append(f"Units in XML: {meta.get('units')} (multiplier={meta.get('multiplier')})")
    lines.append("")
    lines.append("Key figures (A=current, B=prior) in PLN (raw):")
    for k in [
        "assets_total_A",
        "assets_total_B",
        "equity_A",
        "equity_B",
        "liabilities_total_A",
        "liabilities_total_B",
        "current_assets_A",
        "current_liabilities_A",
    ]:
        lines.append(f"- {k}: {n.get(k)}")

    for k in keys_for_summary:
        if k in pl:
            lines.append(
                f"- P&L {k} {pl[k].get('label')}: "
                f"A={pl[k].get('A')} B={pl[k].get('B')}"
            )

    if cf and cf_labels:
        lines.append("")
        lines.append("Cash flow (A/B/C):")
        for key, label in cf_labels.items():
            rec = cf.get(key) or {}
            lines.append(f"- {label}: A={rec.get('A')} B={rec.get('B')}")

    lines.append("")
    lines.append("Key ratios (A):")
    for k, v in r.items():
        lines.append(f"- {k}: {v}")

    return "\n".join(lines)


def build_board_memo_prompt(parsed: Dict[str, Any], ctx: Optional[str] = None, cf_labels: Optional[Dict[str, str]] = None, language: str = "EN") -> str:
    """
    Build prompt for generating executive board memo.

    Args:
        parsed: Parsed financial statement dict
        ctx: Optional pre-built context (if None, will build it)
        cf_labels: Optional cash flow labels dict
        language: Language code ("EN" or "PL") for response

    Returns:
        Complete prompt string for LLM
    """
    ctx = ctx or build_llm_context(parsed, cf_labels)

    if language.upper() == "PL":
        return f"""
Jesteś doświadczonym CFO i kontrolerem finansowym. Stwórz gotowe dla zarządu jednostronicowe Board Memo bazując WYŁĄCZNIE na dostarczonych danych.

DANE:
{ctx}

Memo musi być:
• ~200 słów, zwięzłe i profesjonalne
• Napisane w pierwszej osobie („Rekomenduj ę…")
• Skupione na kluczowych insightach: rentowność, płynność, zadłużenie
• Podkreślić materialne zmiany r/r jeśli dane dostępne
• Zakończyć jasną, praktyczną rekomendacją

Format: Markdown (użyj ## nagłówków). Bez halucynacji. Jeśli brakuje danych, powiedz to.

WAŻNE: Odpowiadaj TYLKO PO POLSKU.
"""
    else:
        return f"""
You are a seasoned CFO and financial controller. Create an executive-ready one-page Board Memo based ONLY on the data provided.

DATA:
{ctx}

The memo must be:
• ~200 words, concise and professional
• Written in the first person ("I recommend…")
• Focused on key insights: profitability, liquidity, leverage
• Highlight material changes year-over-year if data is available
• End with a clear, actionable recommendation or call-out

Format: Markdown (use ## headings). No hallucination. If data is missing, say so.

IMPORTANT: Respond ONLY IN ENGLISH.
"""


def build_variance_analysis_prompt(parsed: Dict[str, Any], ctx: Optional[str] = None, cf_labels: Optional[Dict[str, str]] = None, language: str = "EN") -> str:
    """
    Build prompt for generating variance analysis.

    Args:
        parsed: Parsed financial statement dict
        ctx: Optional pre-built context
        cf_labels: Optional cash flow labels dict
        language: Language code ("EN" or "PL") for response

    Returns:
        Complete prompt string for variance analysis
    """
    ctx = ctx or build_llm_context(parsed, cf_labels)

    if language.upper() == "PL":
        return f"""
Jesteś analitykiem finansowym. Przeanalizuj zmiany rok-do-roku w tym sprawozdaniu finansowym.

DANE:
{ctx}

Skup się na:
• Materjalnych zmianach w przychodach, marżach i kosztach
• Zmianach w strukturze aktywów i zobowiązań
• Ruchach kapitału obrotowego
• Kluczowych zmianach wskaźników i ich konsekwencjach

Utrzymaj analityczny, oparty na danych styl. Użyj wypunktowań. ~150-200 słów.

WAŻNE: Odpowiadaj TYLKO PO POLSKU.
"""
    else:
        return f"""
You are a financial analyst. Analyze the year-over-year variances in this financial statement.

DATA:
{ctx}

Focus on:
• Material changes in revenue, profit margins, and expenses
• Changes in asset and liability composition
• Working capital movements
• Key ratio changes and their implications

Keep it analytical and data-driven. Use bullet points. ~150-200 words.

IMPORTANT: Respond ONLY IN ENGLISH.
"""


def build_story_prompt(parsed: Dict[str, Any], ctx: Optional[str] = None, cf_labels: Optional[Dict[str, str]] = None, language: str = "EN") -> str:
    """
    Build prompt for generating business narrative.

    Args:
        parsed: Parsed financial statement dict
        ctx: Optional pre-built context
        cf_labels: Optional cash flow labels dict
        language: Language code ("EN" or "PL") for response

    Returns:
        Complete prompt string for business story
    """
    ctx = ctx or build_llm_context(parsed, cf_labels)

    if language.upper() == "PL":
        return f"""
Jesteś storytellerem biznesowym. Opowiedz finansową historię tej firmy bazując na liczbach.

DANE:
{ctx}

Stwórz narrację która:
• Wyjaśnia co się wydarzyło w okresie
• Łączy operacje, rentowność i przepływy pieniężne
• Identyfikuje charakterystykę modelu biznesowego
• Podkreśla mocne strony i ryzyka

Pisz w angażującym, przystępnym stylu. ~200-250 słów.

WAŻNE: Odpowiadaj TYLKO PO POLSKU.
"""
    else:
        return f"""
You are a business storyteller. Tell the financial story of this company based on the numbers.

DATA:
{ctx}

Craft a narrative that:
• Explains what happened during the period
• Connects the dots between operations, profitability, and cash flow
• Identifies the business model characteristics
• Highlights strengths and risks

Write in an engaging, accessible style. ~200-250 words.

IMPORTANT: Respond ONLY IN ENGLISH.
"""
