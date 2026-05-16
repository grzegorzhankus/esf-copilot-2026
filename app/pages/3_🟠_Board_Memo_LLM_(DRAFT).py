"""Board Memo page - AI-generated executive summary using LLM.

This page generates an AI-powered executive summary for board presentations,
utilizing NVIDIA NIM or Ollama for intelligent analysis.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from core.i18n import t
from core.language_selector import render_language_selector
from core.modes import render_mode_header
from core.components import render_nvidia_badge, render_llm_badge

# Try to import advanced LLM client first, fall back to basic Ollama
try:
    from core.llm_advanced import AdvancedLLMClient, LLMBackend
    HAS_ADVANCED_LLM = True
except ImportError:
    HAS_ADVANCED_LLM = False

from core.llm_service import (
    list_ollama_models,
    ollama_chat,
    OllamaConnectionError,
    OllamaError,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
)
from core.analysis_file_selector import render_analysis_file_selector, convert_v2026_to_v20_format

st.set_page_config(
    page_title="Board Memo (LLM) - AI CFO Dashboard",
    page_icon="🧾",
    layout="wide",
)


def get_llm_backend_info():
    """Get information about the current LLM backend."""
    if HAS_ADVANCED_LLM:
        try:
            client = AdvancedLLMClient()
            backend = client.config.backend
            if backend == LLMBackend.NVIDIA_NIM:
                return "NVIDIA NIM", True, client
            else:
                return "Ollama", True, client
        except Exception:
            pass
    return "Ollama", False, None


def main():
    # Render language selector and get current language
    lang = render_language_selector()
    render_mode_header("DRAFT", lang)

    st.title(f"🧾 {t('board_memo_title', lang)}")

    # Add LLM badge
    render_llm_badge("NVIDIA NIM / Ollama")

    st.markdown(f"**{t('board_memo_subtitle', lang)}**")

    # Render file selector and load analysis data
    analysis_data = render_analysis_file_selector(lang)

    if not analysis_data:
        st.info(f"👈 {t('load_analysis_instruction', lang)}")
        render_nvidia_badge()
        return

    # Convert v2026 format to v2.0.0 format for compatibility
    parsed, result = convert_v2026_to_v20_format(analysis_data)
    parsed_raw = analysis_data  # Keep full structure for LLM

    # Company header
    company_name = parsed.get("company_name", "Unknown Company")
    period_end = parsed.get("period_end", "N/A")

    st.markdown(f"""
    ### Board Memo: {company_name}
    **{t('period_end', lang)}:** {period_end}
    """)

    st.divider()

    # Get LLM backend info
    backend_name, has_advanced, advanced_client = get_llm_backend_info()

    # Check Ollama availability as fallback
    try:
        models = list_ollama_models(DEFAULT_OLLAMA_URL)
        ollama_available = len(models) > 0
    except OllamaConnectionError:
        ollama_available = False
        models = []

    # Determine if any LLM is available
    llm_available = has_advanced or ollama_available

    if not llm_available:
        # Show placeholder info if no LLM available
        st.info(f"""
        🤖 **{t('board_memo_coming_soon', lang)}**

        This page will generate an AI-powered executive summary using LLM.

        **{t('planned_features', lang)}**
        - {t('feature_exec_summary', lang)}
        - {t('feature_highlights', lang)}
        - {t('feature_recommendations', lang)}
        - {t('feature_llm_powered', lang)}

        **{t('to_enable_feature', lang)}**

        Option 1: NVIDIA NIM (Recommended)
        - Set NVIDIA_API_KEY in your .env file
        - Set LLM_BACKEND=nvidia_nim

        Option 2: Local Ollama
        1. {t('step_1_install', lang)}
        2. {t('step_2_pull_model', lang)}
        3. {t('step_4_restart', lang)}

        {t('for_now_explore', lang)}
        - 📄 **XML Analysis** - Financial statements and KPIs
        - 💬 **CFO Chat** - Interactive AI assistant
        """)

        st.divider()

        # Show deterministic summary
        st.subheader(f"📊 {t('financial_summary', lang)} (Deterministic)")

        if result:
            kpi_list = result.get("kpi", [])
            red_flags = result.get("red_flags", [])

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**{t('kpis_calculated', lang)}:**")
                st.write(f"• Total KPIs: {len(kpi_list)}")
                ok_kpis = sum(1 for kpi in kpi_list if kpi.get("status") == "OK")
                st.write(f"• Available: {ok_kpis}/{len(kpi_list)}")

            with col2:
                st.markdown(f"**{t('red_flags_metric', lang)}:**")
                if red_flags:
                    st.write(f"• Total Flags: {len(red_flags)}")
                    high_flags = sum(1 for flag in red_flags if flag.get("severity") == "HIGH")
                    st.write(f"• High Severity: {high_flags}")
                else:
                    st.write(f"• {t('no_red_flags', lang)} ✅")

        caption_text = t('note_full_llm', lang)
        st.caption(caption_text)
        render_nvidia_badge()
        return

    # LLM is available - show LLM-powered interface
    st.success(f"✅ Connected to {backend_name}" + (f" • {len(models)} models available" if ollama_available else ""))

    # Model selector in sidebar
    with st.sidebar:
        st.divider()
        st.subheader(f"🤖 {t('llm_settings', lang)}")

        # Backend selector (if advanced client available)
        if HAS_ADVANCED_LLM:
            backend_options = ["NVIDIA NIM (Recommended)", "Ollama (Local)"]
            selected_backend_idx = st.selectbox(
                "LLM Backend:",
                options=range(len(backend_options)),
                format_func=lambda x: backend_options[x],
                index=0 if backend_name == "NVIDIA NIM" else 1,
                key="backend_selector"
            )
            use_nvidia = selected_backend_idx == 0
        else:
            use_nvidia = False
            st.info("Using Ollama backend")

        # Model selector for Ollama
        if not use_nvidia and ollama_available:
            model_options = models
            default_idx = 0
            if DEFAULT_OLLAMA_MODEL in models:
                default_idx = models.index(DEFAULT_OLLAMA_MODEL)

            selected_model = st.selectbox(
                f"{t('model', lang)}:",
                options=model_options,
                index=default_idx,
            )
        else:
            selected_model = "nvidia-nim"

        # Temperature slider
        temperature = st.slider(
            "Temperature:",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Lower = more focused, Higher = more creative"
        )

    # Generate button
    if st.button(f"🚀 {t('generate_board_memo', lang)}", type="primary", use_container_width=True):
        with st.spinner(t('generating_board_memo', lang)):
            try:
                # Build simplified context from v2026 format
                context_parts = []
                context_parts.append(f"Company: {company_name}")
                context_parts.append(f"Period: {parsed.get('period_start', 'N/A')} to {parsed.get('period_end', 'N/A')}")
                context_parts.append("")

                # Add base metrics
                if "metrics_base" in analysis_data and analysis_data["metrics_base"]:
                    context_parts.append("BASE FINANCIAL METRICS:")
                    for metric in analysis_data["metrics_base"]:
                        if metric.get("value") is not None:
                            context_parts.append(f"- {metric['key']}: {metric['value']:,.0f} {metric['unit']}")
                    context_parts.append("")

                # Add KPIs
                if "kpis" in analysis_data and analysis_data["kpis"]:
                    context_parts.append("KEY PERFORMANCE INDICATORS:")
                    for kpi in analysis_data["kpis"]:
                        if kpi.get("value") is not None:
                            context_parts.append(f"- {kpi['name']}: {kpi['value']}{kpi['unit']}")
                            context_parts.append(f"  Interpretation: {kpi['interpretation']}")
                    context_parts.append("")

                # Add red flags
                if "red_flags" in analysis_data:
                    detected_flags = [f for f in analysis_data["red_flags"] if f.get("detected")]
                    if detected_flags:
                        context_parts.append("DETECTED RED FLAGS:")
                        for flag in detected_flags:
                            context_parts.append(f"- [{flag['severity'].upper()}] {flag['title']}")
                            context_parts.append(f"  {flag['description']}")
                    else:
                        context_parts.append("RED FLAGS: None detected - All checks passed")
                    context_parts.append("")

                financial_context = "\n".join(context_parts)

                # Build prompt manually with language support
                if lang == "PL":
                    system_prompt = """Jesteś doświadczonym CFO i kontrolerem finansowym. Stwórz gotowe dla zarządu jednostronicowe Board Memo bazując WYŁĄCZNIE na dostarczonych danych.

Memo musi być:
• ~200 słów, zwięzłe i profesjonalne
• Napisane w pierwszej osobie („Rekomenduję…")
• Skupione na kluczowych insightach: rentowność, płynność, zadłużenie
• Podkreślić materialne zmiany r/r jeśli dane dostępne
• Zakończyć jasną, praktyczną rekomendacją

Format: Markdown (użyj ## nagłówków). Bez halucynacji. Jeśli brakuje danych, powiedz to.

WAŻNE: Odpowiadaj TYLKO PO POLSKU."""
                else:
                    system_prompt = """You are a seasoned CFO and financial controller. Create an executive-ready one-page Board Memo based ONLY on the data provided.

The memo must be:
• ~200 words, concise and professional
• Written in the first person ("I recommend…")
• Focused on key insights: profitability, liquidity, leverage
• Highlight material changes year-over-year if data is available
• End with a clear, actionable recommendation or call-out

Format: Markdown (use ## headings). No hallucination. If data is missing, say so.

IMPORTANT: Respond ONLY IN ENGLISH."""

                prompt = f"{system_prompt}\n\nDATA:\n{financial_context}"

                # Call LLM based on selected backend
                if use_nvidia and HAS_ADVANCED_LLM:
                    # Use NVIDIA NIM via advanced client
                    client = AdvancedLLMClient()
                    response = client.chat(
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                    )
                    backend_used = "NVIDIA NIM"
                else:
                    # Use Ollama
                    messages = [{"role": "user", "content": prompt}]
                    response = ollama_chat(
                        messages=messages,
                        model=selected_model,
                        temperature=temperature,
                        num_predict=1000,
                    )
                    backend_used = f"Ollama ({selected_model})"

                # Store in session state
                st.session_state.board_memo_text = response
                st.session_state.board_memo_backend = backend_used

            except OllamaError as e:
                st.error(f"❌ LLM Error: {e}")
                return
            except Exception as e:
                st.error(f"❌ Error generating memo: {e}")
                return

    # Display generated memo
    if "board_memo_text" in st.session_state:
        st.divider()
        st.subheader(f"📄 {t('generated_board_memo', lang)}")

        st.markdown(st.session_state.board_memo_text)

        st.caption(f"Generated by: {st.session_state.get('board_memo_backend', 'unknown')} • Language: {lang}")

        # Download button
        col1, col2 = st.columns([3, 1])
        with col2:
            st.download_button(
                label=f"💾 {t('download', lang)}",
                data=st.session_state.board_memo_text,
                file_name=f"board_memo_{company_name.replace(' ', '_')}.md",
                mime="text/markdown",
            )

    st.divider()

    # Show deterministic summary as reference
    st.subheader(f"📊 {t('financial_summary', lang)} (Reference)")

    if result:
        kpi_list = result.get("kpi", [])
        red_flags = result.get("red_flags", [])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{t('kpis_calculated', lang)}:**")
            st.write(f"• Total KPIs: {len(kpi_list)}")
            ok_kpis = sum(1 for kpi in kpi_list if kpi.get("status") == "OK")
            st.write(f"• Available: {ok_kpis}/{len(kpi_list)}")

        with col2:
            st.markdown(f"**{t('red_flags_metric', lang)}:**")
            if red_flags:
                st.write(f"• Total Flags: {len(red_flags)}")
                high_flags = sum(1 for flag in red_flags if flag.get("severity") == "HIGH")
                st.write(f"• High Severity: {high_flags}")
            else:
                st.write(f"• {t('no_red_flags', lang)} ✅")

    # Footer
    render_nvidia_badge()


if __name__ == "__main__":
    main()
