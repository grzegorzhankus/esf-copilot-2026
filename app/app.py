from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.language_selector import render_language_selector
from core.i18n import t

st.set_page_config(page_title="AI CFO Dashboard", layout="wide", page_icon="📊")

# Render language selector and get current language
lang = render_language_selector()

st.title("📊 AI CFO Dashboard")

# Subtitle based on language
if lang == "EN":
    st.markdown("**Intelligent Financial Statement Analysis for Polish e-Sprawozdania**")
else:
    st.markdown("**Inteligentna Analiza Sprawozdań Finansowych dla Polskich e-Sprawozdań**")

st.markdown("---")

# Main content - App description and navigation guide
col1, col2 = st.columns([2, 1])

with col1:
    if lang == "EN":
        st.markdown("""
        ## What is AI CFO Dashboard?

        AI CFO Dashboard is an **AI-powered financial analysis tool** designed for Polish financial statements (e-Sprawozdania).
        Upload your XML files and get instant insights powered by advanced AI models.

        ### Key Features

        | Feature | Description |
        |---------|-------------|
        | **XML Analysis** | Parse e-Sprawozdania XML files, extract KPIs and detect red flags |
        | **CFO Chat (LLM)** | Ask questions about your financials in natural language |
        | **Board Memo (LLM)** | Generate executive summaries automatically |
        | **Anomaly Detection** | AI-powered detection of unusual financial patterns |
        | **Natural Language Query** | Query your data using plain English or Polish |
        | **Forecasting** | Project future performance with scenario analysis |

        ### How to Use

        1. **Start with XML Analysis** - Upload your e-Sprawozdanie XML file in the sidebar
        2. **Review Executive Dashboard** - See KPIs, red flags, and financial health at a glance
        3. **Explore Details** - Navigate to P&L, Balance Sheet, or Cash Flow for deep dives
        4. **Ask AI** - Use CFO Chat to get answers about your financials
        5. **Generate Reports** - Create Board Memos and export data

        ### Supported Schemas

        - JednostkaInna (standard companies)
        - JednostkaMała (small entities)
        - Values in PLN or thousands PLN
        """)
    else:
        st.markdown("""
        ## Czym jest AI CFO Dashboard?

        AI CFO Dashboard to **narzędzie do analizy finansowej wspomagane AI** zaprojektowane dla polskich sprawozdań finansowych (e-Sprawozdania).
        Prześlij pliki XML i uzyskaj natychmiastowe wnioski wspierane przez zaawansowane modele AI.

        ### Główne Funkcje

        | Funkcja | Opis |
        |---------|------|
        | **Analiza XML** | Parsuj pliki XML e-Sprawozdań, wyodrębnij KPI i wykryj czerwone flagi |
        | **Chat CFO (LLM)** | Zadawaj pytania o finanse w języku naturalnym |
        | **Board Memo (LLM)** | Generuj automatycznie podsumowania wykonawcze |
        | **Wykrywanie Anomalii** | Wykrywanie nietypowych wzorców finansowych przez AI |
        | **Zapytania Naturalne** | Odpytuj dane używając języka polskiego lub angielskiego |
        | **Prognozowanie** | Przewiduj przyszłe wyniki z analizą scenariuszy |

        ### Jak Używać

        1. **Zacznij od Analizy XML** - Prześlij plik XML e-Sprawozdania w panelu bocznym
        2. **Przejrzyj Dashboard** - Zobacz KPI, czerwone flagi i zdrowie finansowe na pierwszy rzut oka
        3. **Eksploruj Szczegóły** - Przejdź do RZiS, Bilansu lub Przepływów Pieniężnych
        4. **Zapytaj AI** - Użyj Chat CFO, aby uzyskać odpowiedzi o finansach
        5. **Generuj Raporty** - Twórz Board Memo i eksportuj dane

        ### Obsługiwane Schematy

        - JednostkaInna (standardowe firmy)
        - JednostkaMała (małe podmioty)
        - Wartości w PLN lub tysiącach PLN
        """)

with col2:
    # Quick navigation panel
    if lang == "EN":
        st.markdown("### Quick Start")
        st.markdown("""
        **📄 XML Analysis**
        Upload & analyze files

        **💬 CFO Chat**
        AI-powered Q&A

        **🧾 Board Memo**
        Executive summaries

        **🔴 Anomaly Detection**
        Find unusual patterns

        **📈 Forecasting**
        Future projections
        """)
    else:
        st.markdown("### Szybki Start")
        st.markdown("""
        **📄 Analiza XML**
        Prześlij i analizuj pliki

        **💬 Chat CFO**
        Q&A wspomagane AI

        **🧾 Board Memo**
        Podsumowania wykonawcze

        **🔴 Wykrywanie Anomalii**
        Znajdź nietypowe wzorce

        **📈 Prognozowanie**
        Projekcje przyszłości
        """)

st.markdown("---")

# Navigation hint
if lang == "EN":
    st.info("👈 **Select a page from the sidebar to get started**")
else:
    st.info("👈 **Wybierz stronę z panelu bocznego, aby rozpocząć**")

# Footer with NVIDIA badge
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        """
        <div style="text-align: center; padding: 10px; background: linear-gradient(90deg, #76b900 0%, #1a1a1a 100%); border-radius: 8px; margin: 10px 0;">
            <span style="color: white; font-weight: bold;">⚡ Powered by NVIDIA DGX Spark</span>
        </div>
        """,
        unsafe_allow_html=True
    )
st.caption("AI CFO Dashboard v2.0 | Built with Streamlit and NVIDIA NIM")
