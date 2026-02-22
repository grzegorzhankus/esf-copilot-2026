from __future__ import annotations

import json
from typing import Dict, List, Optional

import requests

from core.contracts import AnalysisResult


class OllamaClient:
    """Client for interacting with Ollama LLM."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        self.chat_url = f"{base_url}/api/chat"

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception:
            return []

    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a response using Ollama."""
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                },
                timeout=60,
            )

            if response.status_code == 200:
                return response.json().get("response", "No response generated")
            else:
                return f"Error: {response.status_code} - {response.text}"
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The LLM is taking too long to respond."
        except Exception as e:
            return f"Error: {str(e)}"

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat with Ollama using conversation history."""
        try:
            response = requests.post(
                self.chat_url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                },
                timeout=60,
            )

            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "No response generated")
            else:
                return f"Error: {response.status_code} - {response.text}"
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The LLM is taking too long to respond."
        except Exception as e:
            return f"Error: {str(e)}"


def prepare_financial_context(result: AnalysisResult) -> str:
    """Prepare financial analysis context for the LLM."""
    context_parts = []

    # Metadata
    context_parts.append(f"Company Financial Analysis for: {result.metadata.filename}")
    context_parts.append(f"Analyzed on: {result.metadata.analyzed_at_utc}")
    context_parts.append("")

    # Base Metrics
    if result.metrics_base:
        context_parts.append("BASE FINANCIAL METRICS:")
        for metric in result.metrics_base:
            if metric.value is not None:
                context_parts.append(f"- {metric.key}: {metric.value:,.2f} {metric.unit}")
        context_parts.append("")

    # KPIs
    if result.kpis:
        context_parts.append("KEY PERFORMANCE INDICATORS:")
        for kpi in result.kpis:
            if kpi.value is not None:
                context_parts.append(f"- {kpi.name}: {kpi.value}{kpi.unit}")
                context_parts.append(f"  Category: {kpi.category}")
                context_parts.append(f"  Interpretation: {kpi.interpretation}")
        context_parts.append("")

    # Red Flags
    if result.red_flags:
        detected = [f for f in result.red_flags if f.detected]
        if detected:
            context_parts.append("DETECTED RED FLAGS:")
            for flag in detected:
                context_parts.append(f"- [{flag.severity.upper()}] {flag.title}")
                context_parts.append(f"  {flag.description}")
                context_parts.append(f"  Details: {flag.details}")
        else:
            context_parts.append("RED FLAGS: None detected - All checks passed")
        context_parts.append("")

    return "\n".join(context_parts)


def create_financial_advisor_system_prompt(language: str = "EN") -> str:
    """
    Create system prompt for financial advisor in specified language.

    Args:
        language: "EN" for English or "PL" for Polish
    """
    if language == "PL":
        return """Jesteś ekspertem CFO i doradcą finansowym specjalizującym się w polskich sprawozdaniach finansowych (e-Sprawozdania).
Twoja rola polega na:
1. Analizowaniu danych finansowych dostarczonych w kontekście
2. Odpowiadaniu na pytania dotyczące kondycji finansowej, wskaźników i wyników
3. Dostarczaniu praktycznych wniosków i rekomendacji
4. Wyjaśnianiu koncepcji finansowych w jasnym, zrozumiałym języku
5. Identyfikowaniu ryzyk i możliwości
6. Porównywaniu wskaźników ze standardami branżowymi, gdy jest to istotne

Podczas odpowiedzi:
- Bądź zwięzły, ale dokładny
- Używaj konkretnych liczb z danych
- Wyjaśniaj "dlaczego" stojące za wskaźnikami finansowymi
- Dostarczaj kontekst i porównania
- Sugeruj konkretne następne kroki, gdy jest to właściwe
- Używaj profesjonalnego, ale przystępnego języka

WAŻNE: Odpowiadaj ZAWSZE po POLSKU. Twoje odpowiedzi muszą być w języku polskim.

Jeśli zostaniesz zapytany o dane, których nie ma w kontekście, jasno powiedz, że informacja nie jest dostępna w obecnej analizie."""
    else:
        return """You are an expert CFO and financial advisor specializing in Polish financial statements (e-Sprawozdania).
Your role is to:
1. Analyze financial data provided in the context
2. Answer questions about financial health, ratios, and performance
3. Provide actionable insights and recommendations
4. Explain financial concepts in clear, understandable language
5. Identify risks and opportunities
6. Compare metrics against industry standards when relevant

When answering:
- Be concise but thorough
- Use specific numbers from the data
- Explain the "why" behind financial metrics
- Provide context and comparisons
- Suggest concrete next steps when appropriate
- Use professional but accessible language

IMPORTANT: Always respond in ENGLISH. Your responses must be in English.

If asked about data not in the context, clearly state that the information is not available in the current analysis."""


def ask_financial_question(
    question: str,
    result: AnalysisResult,
    ollama_client: OllamaClient,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Ask a financial question with context from analysis result.

    Args:
        question: User's question
        result: Analysis result containing financial data
        ollama_client: Ollama client instance
        conversation_history: Previous conversation messages (optional)

    Returns:
        LLM response
    """
    # Prepare context
    financial_context = prepare_financial_context(result)
    system_prompt = create_financial_advisor_system_prompt()

    # Build messages for chat
    messages = []

    # Add system message
    messages.append({
        "role": "system",
        "content": system_prompt
    })

    # Add financial context as a user message
    messages.append({
        "role": "user",
        "content": f"Here is the financial data for the company:\n\n{financial_context}"
    })

    # Add assistant acknowledgment
    messages.append({
        "role": "assistant",
        "content": "I have reviewed the financial data. I'm ready to answer your questions about this company's financial health and performance."
    })

    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)

    # Add current question
    messages.append({
        "role": "user",
        "content": question
    })

    # Get response from LLM
    return ollama_client.chat(messages)
