from __future__ import annotations

import json
from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.contracts import AnalysisResult
from core.i18n import t
from core.language_selector import render_language_selector
from core.llm_advanced import (
    AdvancedLLMClient,
    LLMBackend,
    LLMModel,
    create_financial_analyst_prompt,
)

st.set_page_config(page_title="CFO Chat (LLM) - AI CFO Dashboard", layout="wide", page_icon="💬")

# Render language selector and get current language
lang = render_language_selector()

st.title(f"💬 {t('cfo_chat_title', lang)}")

# LLM Badge
st.markdown(
    """
    <div style="display: inline-block; padding: 4px 12px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 16px; margin-bottom: 10px;">
        <span style="color: white; font-size: 12px; font-weight: 500;">🤖 Powered by LLM (NVIDIA NIM / Ollama)</span>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_analysis" not in st.session_state:
    st.session_state.selected_analysis = None
if "chat_input_key" not in st.session_state:
    st.session_state.chat_input_key = 0
if "llm_client" not in st.session_state:
    try:
        st.session_state.llm_client = AdvancedLLMClient()
        st.session_state.llm_available = True
    except RuntimeError:
        st.session_state.llm_client = None
        st.session_state.llm_available = False

# Model options for NVIDIA NIM
NIM_MODELS = {
    "Llama 3.3 70B (Recommended)": LLMModel.LLAMA_3_3_70B,
    "Llama 3.1 405B (Largest)": LLMModel.LLAMA_3_1_405B,
    "DeepSeek V3 (Financial Expert)": LLMModel.DEEPSEEK_V3,
    "DeepSeek R1 (Reasoning)": LLMModel.DEEPSEEK_R1,
    "Mistral Large 3 (675B)": LLMModel.MISTRAL_LARGE_3,
    "Qwen3 235B (Best Polish)": LLMModel.QWEN3_235B,
    "Nemotron 70B (NVIDIA Optimized)": LLMModel.NEMOTRON_70B,
    "Llama 3.1 8B (Fast)": LLMModel.LLAMA_3_1_8B,
    "Mistral Small 24B (Fast)": LLMModel.MISTRAL_SMALL,
}

# Sidebar for settings and analysis selection
with st.sidebar:
    st.markdown(f"### ⚙️ {t('settings_title', lang)}")

    # LLM status and model selection
    if st.session_state.llm_available and st.session_state.llm_client:
        client = st.session_state.llm_client
        backend = client.config.backend

        if backend == LLMBackend.NVIDIA_NIM:
            st.success("✅ NVIDIA NIM Connected")
            st.caption("🚀 Using cloud-based AI models")

            # Model selector for NIM
            current_model_name = None
            for name, model in NIM_MODELS.items():
                if model == client.config.model:
                    current_model_name = name
                    break

            selected_model_name = st.selectbox(
                t("select_model", lang),
                list(NIM_MODELS.keys()),
                index=list(NIM_MODELS.keys()).index(current_model_name) if current_model_name else 0
            )

            # Update model if changed
            new_model = NIM_MODELS[selected_model_name]
            if new_model != client.config.model:
                client.config.model = new_model
                st.rerun()

            # Show model info
            st.caption(f"📊 Model: `{client.config.model.value}`")

        elif backend == LLMBackend.OLLAMA:
            st.info("✅ Ollama Connected (Local)")
            st.caption("💡 Add NVIDIA_API_KEY to .env for cloud models")

            # For Ollama, show available local models
            from core.llm_integration import OllamaClient
            ollama = OllamaClient()
            if ollama.is_available():
                models = ollama.get_available_models()
                if models:
                    selected = st.selectbox(t("select_model", lang), models)
                    # Note: This doesn't change the advanced client's model
                    st.caption(f"Local model: {selected}")
    else:
        st.error(f"❌ {t('ollama_not_connected', lang)}")
        st.caption("No LLM backend available")

    st.markdown("---")

    # Analysis file selector
    st.markdown(f"### 📁 {t('load_analysis_title', lang)}")
    outputs_dir = Path("outputs")

    if outputs_dir.exists():
        analysis_files = sorted(
            [f for f in outputs_dir.glob("analysis_*.json")],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if analysis_files:
            file_options = [f.name for f in analysis_files]
            selected_file = st.selectbox(
                t("select_analysis_file", lang),
                file_options,
                index=0
            )

            if st.button(t("load_analysis_button", lang), use_container_width=True):
                try:
                    selected_path = outputs_dir / selected_file
                    with open(selected_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    st.session_state.selected_analysis = data
                    st.session_state.chat_history = []  # Reset chat history
                    st.success(f"{t('loaded_label', lang)}: {selected_file}")
                    st.rerun()
                except Exception as e:
                    st.error(f"{t('error_loading_file', lang)}: {e}")
        else:
            st.info(t("no_analysis_files", lang))
    else:
        st.info(t("no_outputs_dir", lang))

    # Clear chat button
    if st.button(f"🗑️ {t('clear_chat_button', lang)}", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Main chat interface
if not st.session_state.llm_available:
    st.error(f"⚠️ No LLM backend available")

    st.markdown("""
    ### Setup Options:

    **Option 1: NVIDIA NIM (Recommended for DGX Spark)**
    1. Get API key from [build.nvidia.com](https://build.nvidia.com/)
    2. Add to `.env` file: `NVIDIA_API_KEY=nvapi-your-key`
    3. Restart the app

    **Option 2: Ollama (Local)**
    1. Install from [ollama.ai](https://ollama.ai)
    2. Run: `ollama pull llama3.1:8b`
    3. Ensure Ollama is running

    Once configured, refresh this page.
    """)

elif not st.session_state.selected_analysis:
    st.info(f"👈 {t('load_analysis_instruction', lang)}")

    if lang == "EN":
        st.markdown("""
        ### How to use CFO Chat:

        1. **Run an Analysis**: Go to the XML Analysis page and analyze a financial statement
        2. **Load Analysis**: Use the sidebar to select and load an analysis file
        3. **Ask Questions**: Chat with the AI about the financial data
        4. **Get Insights**: Receive expert financial advice and recommendations

        ### Example Questions:

        - "What is the company's overall financial health?"
        - "Are there any concerning red flags I should address immediately?"
        - "How is the company's profitability compared to typical benchmarks?"
        - "What are the main risks based on this financial data?"
        - "Explain the debt-to-equity ratio and what it means for this company"
        - "What recommendations do you have to improve financial performance?"
        """)
    else:
        st.markdown("""
        ### Jak korzystać z CFO Chat:

        1. **Uruchom Analizę**: Przejdź do strony Analiza XML i przeanalizuj sprawozdanie finansowe
        2. **Wczytaj Analizę**: Użyj panelu bocznego, aby wybrać i wczytać plik analizy
        3. **Zadawaj Pytania**: Rozmawiaj z AI o danych finansowych
        4. **Uzyskaj Wnioski**: Otrzymuj eksperckie porady i rekomendacje finansowe

        ### Przykładowe Pytania:

        - "Jaka jest ogólna kondycja finansowa firmy?"
        - "Czy są jakieś niepokojące sygnały ostrzegawcze, którymi powinienem się zająć natychmiast?"
        - "Jak rentowność firmy wypada w porównaniu z typowymi wskaźnikami?"
        - "Jakie są główne ryzyka na podstawie tych danych finansowych?"
        - "Wyjaśnij wskaźnik zadłużenia do kapitału własnego i co to oznacza dla tej firmy"
        - "Jakie masz rekomendacje, aby poprawić wyniki finansowe?"
        """)
else:
    # Display loaded analysis info
    metadata = st.session_state.selected_analysis.get("metadata", {})
    chatting_label = t("chatting_about", lang) if lang == "EN" else "Rozmawiamy o"
    analyzed_label = t("analyzed_at", lang) if lang == "EN" else "przeanalizowano"
    st.info(f"📊 {chatting_label}: **{metadata.get('filename', 'Unknown')}** ({analyzed_label} {metadata.get('analyzed_at_utc', 'Unknown')})")

    # Show current model
    if st.session_state.llm_client:
        model_info = st.session_state.llm_client.get_model_info()
        backend_emoji = "🚀" if model_info["backend"] == "nvidia_nim" else "💻"
        st.caption(f"{backend_emoji} Using: **{model_info['model']}**")

    # Chat interface
    st.markdown(f"#### {t('chat_interface_title', lang)}")

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                you_label = t("you_label", lang)
                st.markdown(f"**🧑 {you_label}:** {msg['content']}")
            else:
                assistant_label = t("cfo_assistant_label", lang)
                st.markdown(f"**🤖 {assistant_label}:** {msg['content']}")
            st.markdown("---")

    # Chat input - use dynamic key to enable clearing after send
    user_question = st.text_area(
        t("your_question", lang),
        placeholder=t("ask_placeholder", lang),
        key=f"chat_input_{st.session_state.chat_input_key}",
        height=100
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button(t("send_button", lang), type="primary", use_container_width=True)

    if send_button and user_question:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })

        # Show thinking indicator
        thinking_label = t("thinking_label", lang)
        with st.spinner(f"🤔 {thinking_label}..."):
            try:
                analysis_data = st.session_state.selected_analysis

                # Build financial context
                context_parts = []
                context_parts.append("Company Financial Analysis")
                context_parts.append("")

                if "metrics_base" in analysis_data:
                    context_parts.append("BASE METRICS:")
                    for metric in analysis_data["metrics_base"]:
                        if metric.get("value") is not None:
                            context_parts.append(f"- {metric['key']}: {metric['value']} {metric['unit']}")
                    context_parts.append("")

                if "kpis" in analysis_data:
                    context_parts.append("KEY PERFORMANCE INDICATORS:")
                    for kpi in analysis_data["kpis"]:
                        if kpi.get("value") is not None:
                            context_parts.append(f"- {kpi['name']}: {kpi['value']}{kpi['unit']}")
                            context_parts.append(f"  Interpretation: {kpi['interpretation']}")
                    context_parts.append("")

                if "red_flags" in analysis_data:
                    detected = [f for f in analysis_data["red_flags"] if f.get("detected")]
                    if detected:
                        context_parts.append("DETECTED RED FLAGS:")
                        for flag in detected:
                            context_parts.append(f"- [{flag['severity'].upper()}] {flag['title']}")
                            context_parts.append(f"  {flag['description']}")
                    else:
                        context_parts.append("RED FLAGS: None detected")
                    context_parts.append("")

                financial_context = "\n".join(context_parts)
                system_prompt = create_financial_analyst_prompt(lang)

                # Build messages for chat
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the financial data:\n\n{financial_context}"},
                    {"role": "assistant", "content": "I have reviewed the financial data. I'm ready to answer your questions."}
                ]

                # Add conversation history (last 10 messages for context)
                recent_history = st.session_state.chat_history[-11:-1]
                messages.extend(recent_history)

                # Add current question
                messages.append({"role": "user", "content": user_question})

                # Get response using advanced LLM client
                client = st.session_state.llm_client
                response = client.chat(messages)

                # Add assistant response to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })

        # Increment key to clear input field on rerun
        st.session_state.chat_input_key += 1
        # Rerun to show updated chat
        st.rerun()

st.markdown("---")

# Show powered by info
if st.session_state.llm_available and st.session_state.llm_client:
    backend = st.session_state.llm_client.config.backend
    if backend == LLMBackend.NVIDIA_NIM:
        st.caption("🚀 Powered by NVIDIA NIM")
    else:
        st.caption("💻 Powered by Ollama LLM")
else:
    st.caption("⚠️ No LLM configured")

# NVIDIA Badge
from core.components import render_nvidia_badge
render_nvidia_badge()
