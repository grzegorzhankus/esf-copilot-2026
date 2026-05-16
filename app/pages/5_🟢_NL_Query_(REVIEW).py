"""Natural Language Query Interface for financial data.

This page allows users to query financial analysis data using natural language,
powered by NVIDIA NIM LLMs for query interpretation.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import streamlit as st
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.i18n import t
from core.language_selector import render_language_selector
from core.modes import render_mode_header
from core.nl_query_engine import NLQueryEngine, create_query_engine
from core.components import render_nvidia_badge, render_llm_badge

OUTPUTS_DIR = Path("outputs")

st.set_page_config(
    page_title="NL Query - AI CFO Dashboard",
    layout="wide",
    page_icon="🔍"
)

# Render language selector and get current language
lang = render_language_selector()
render_mode_header("REVIEW", lang)

# Page title
if lang == "PL":
    st.title("🔍 Zapytania w Języku Naturalnym")
    render_llm_badge("NVIDIA NIM / Ollama")
    st.write("Zadawaj pytania o dane finansowe w języku naturalnym - AI przekształci je w zapytania.")
else:
    st.title("🔍 Natural Language Query")
    render_llm_badge("NVIDIA NIM / Ollama")
    st.write("Ask questions about financial data in natural language - AI will convert them to queries.")

st.markdown("---")

# Initialize session state
if "nl_engine" not in st.session_state:
    st.session_state.nl_engine = create_query_engine()
    st.session_state.data_loaded = False

if "query_history" not in st.session_state:
    st.session_state.query_history = []

# Sidebar - Data loading and statistics
with st.sidebar:
    st.markdown("### 📊 Data Source")

    # Load data button
    if st.button("📂 Load Analysis Data", use_container_width=True):
        with st.spinner("Loading data..."):
            count = st.session_state.nl_engine.load_data(OUTPUTS_DIR)
            st.session_state.data_loaded = count > 0
            if count > 0:
                st.success(f"Loaded {count} analysis files")
            else:
                st.warning("No analysis files found in outputs/")

    # Show statistics
    stats = st.session_state.nl_engine.get_statistics()

    if stats.get("loaded"):
        st.success(f"✅ {stats['count']} analyses loaded")

        with st.expander("📈 Data Statistics"):
            # Key metrics
            metrics_to_show = [
                ("kpi_roe_mean", "Avg ROE", "%"),
                ("kpi_roa_mean", "Avg ROA", "%"),
                ("kpi_current_ratio_mean", "Avg Current Ratio", ""),
                ("red_flag_count_mean", "Avg Red Flags", ""),
            ]

            for key, label, unit in metrics_to_show:
                if key in stats:
                    value = stats[key]
                    if value is not None:
                        st.metric(label, f"{value:.2f}{unit}")

        with st.expander("📋 Available Columns"):
            columns = stats.get("columns", [])
            for col in columns[:20]:  # Show first 20
                st.caption(f"• {col}")
            if len(columns) > 20:
                st.caption(f"... and {len(columns) - 20} more")
    else:
        st.info("No data loaded. Click 'Load Analysis Data' to start.")

    st.markdown("---")

    # Sample queries
    st.markdown("### 💡 Sample Queries")

    sample_queries = st.session_state.nl_engine.get_sample_queries(lang)
    for i, sample in enumerate(sample_queries):
        if st.button(f"📝 {sample}", key=f"sample_{i}_{hash(sample) % 10000}", use_container_width=True):
            st.session_state.current_query = sample
            st.rerun()

# Main content
if not st.session_state.data_loaded:
    # No data loaded - show instructions
    if lang == "PL":
        st.info("👈 Wczytaj dane analizy używając przycisku w panelu bocznym.")

        st.markdown("""
        ### Jak używać Zapytań w Języku Naturalnym:

        1. **Wczytaj Dane**: Kliknij "Load Analysis Data" w panelu bocznym
        2. **Zadaj Pytanie**: Wpisz pytanie w języku naturalnym
        3. **Przejrzyj Wyniki**: AI przekształci pytanie i pokaże wyniki
        4. **Analizuj**: Przeglądaj dane, sortuj i filtruj

        ### Przykłady Pytań:

        - "Pokaż firmy z ROE większym niż 15%"
        - "Które firmy mają czerwone flagi?"
        - "Top 10 firm według sumy aktywów"
        - "Średnia rentowność wszystkich firm"
        - "Firmy z ujemnym wynikiem netto"
        """)
    else:
        st.info("👈 Load analysis data using the button in the sidebar.")

        st.markdown("""
        ### How to Use Natural Language Query:

        1. **Load Data**: Click "Load Analysis Data" in the sidebar
        2. **Ask a Question**: Type your question in natural language
        3. **Review Results**: AI will interpret your query and show results
        4. **Analyze**: Browse data, sort and filter

        ### Example Questions:

        - "Show companies with ROE greater than 15%"
        - "Which companies have red flags?"
        - "Top 10 companies by total assets"
        - "Average profitability of all companies"
        - "Companies with negative net income"
        """)
else:
    # Data loaded - show query interface
    col1, col2 = st.columns([4, 1])

    with col1:
        # Query input
        default_query = st.session_state.get("current_query", "")
        query = st.text_input(
            "🔍 Your Question" if lang == "EN" else "🔍 Twoje Pytanie",
            value=default_query,
            placeholder="e.g., Show companies with ROE > 15%" if lang == "EN" else "np. Pokaż firmy z ROE > 15%",
            key="query_input"
        )

    with col2:
        search_button = st.button(
            "🔎 Search" if lang == "EN" else "🔎 Szukaj",
            type="primary",
            use_container_width=True
        )

    # Execute query
    if search_button and query:
        with st.spinner("Processing query..." if lang == "EN" else "Przetwarzanie zapytania..."):
            result = st.session_state.nl_engine.query(query, language=lang)

            # Add to history
            st.session_state.query_history.insert(0, {
                "query": query,
                "result_count": result.result_count,
                "time_ms": result.execution_time_ms
            })

            # Keep only last 10 queries
            st.session_state.query_history = st.session_state.query_history[:10]

        # Display results
        st.markdown("---")

        # Query interpretation
        st.markdown("### 📝 Query Interpretation")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Results" if lang == "EN" else "Wyniki",
                result.result_count
            )
        with col2:
            st.metric(
                "Time" if lang == "EN" else "Czas",
                f"{result.execution_time_ms:.0f}ms"
            )
        with col3:
            st.info(f"**Interpretation:** {result.interpreted_query}")

        # SQL equivalent (expandable)
        if result.sql_equivalent:
            with st.expander("🔧 SQL Equivalent"):
                st.code(result.sql_equivalent, language="sql")

        # Explanation
        st.info(f"💡 {result.explanation}")

        # Results table
        if result.results:
            st.markdown("### 📊 Results")

            # Convert to DataFrame
            df = pd.DataFrame(result.results)

            # Format numeric columns
            for col in df.select_dtypes(include=["float64"]).columns:
                if "ratio" in col.lower() or "roe" in col.lower() or "roa" in col.lower():
                    df[col] = df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
                elif "assets" in col.lower() or "liabilities" in col.lower() or "equity" in col.lower():
                    df[col] = df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")

            # Display with data editor for interactivity
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV" if lang == "EN" else "📥 Pobierz CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv"
            )
        else:
            if lang == "PL":
                st.warning("Nie znaleziono wyników dla tego zapytania.")
            else:
                st.warning("No results found for this query.")

    # Query history
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("### 📜 Query History" if lang == "EN" else "### 📜 Historia Zapytań")

        for i, item in enumerate(st.session_state.query_history[:5]):
            col1, col2, col3 = st.columns([6, 1, 1])
            with col1:
                if st.button(f"🔄 {item['query']}", key=f"history_{i}", use_container_width=True):
                    st.session_state.current_query = item["query"]
                    st.rerun()
            with col2:
                st.caption(f"{item['result_count']} results")
            with col3:
                st.caption(f"{item['time_ms']:.0f}ms")

# Footer
render_nvidia_badge()
