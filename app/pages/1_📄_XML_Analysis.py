"""XML Analysis Page - Upload and Executive Dashboard.

This page provides:
- XML file upload in sidebar
- Automatic analysis on upload
- Executive Dashboard with KPIs and red flags
- Export options (Excel, PDF, JSON)
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

from core.analysis_pipeline import analyze_xml_bytes
from core.excel_export import export_to_excel
from core.formatting import money_fmt
from core.i18n import t
from core.language_selector import render_language_selector
from core.pdf_export import export_to_pdf
from core.xml_loader import XmlParseError
from core.components import render_nvidia_badge

OUTPUTS_DIR = Path("outputs")

st.set_page_config(page_title="XML Analysis - AI CFO Dashboard", layout="wide", page_icon="📄")

# Render language selector and get current language
lang = render_language_selector()

# ============== SIDEBAR - File Upload ==============
with st.sidebar:
    st.markdown("### 📤 Upload XML File")

    uploaded = st.file_uploader(
        "e-Sprawozdanie XML" if lang == "EN" else "Plik XML e-Sprawozdanie",
        type=["xml"],
        help="Upload Polish e-Sprawozdanie XML file (JednostkaInna or JednostkaMała)"
    )

    analyze_clicked = st.button(
        "🔍 Analyze" if lang == "EN" else "🔍 Analizuj",
        type="primary",
        use_container_width=True,
        disabled=uploaded is None
    )

    st.markdown("---")

    # Show recent analyses
    st.markdown("### 📂 Recent Analyses")
    if OUTPUTS_DIR.exists():
        analysis_files = sorted(
            [f for f in OUTPUTS_DIR.glob("analysis_*.json")],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:5]  # Show last 5

        if analysis_files:
            selected_file = st.selectbox(
                "Load previous:" if lang == "EN" else "Wczytaj poprzednią:",
                options=["-- Select --"] + [f.name for f in analysis_files],
                index=0
            )

            if selected_file != "-- Select --":
                try:
                    with open(OUTPUTS_DIR / selected_file, "r", encoding="utf-8") as f:
                        st.session_state["analysis_result"] = json.load(f)
                        st.session_state["analysis_source"] = "loaded"
                except Exception as e:
                    st.error(f"Error loading: {e}")
        else:
            st.caption("No previous analyses found")
    else:
        st.caption("No outputs directory")

# ============== MAIN CONTENT ==============
st.title("📄 XML Analysis & Executive Dashboard")

if lang == "EN":
    st.markdown("Upload e-Sprawozdanie XML file to analyze financial statements with KPIs and red flags.")
else:
    st.markdown("Prześlij plik XML e-Sprawozdanie, aby przeanalizować sprawozdania finansowe z KPI i czerwonymi flagami.")

# Process uploaded file
if analyze_clicked and uploaded is not None:
    try:
        with st.spinner("Analyzing financial statement..." if lang == "EN" else "Analizuję sprawozdanie finansowe..."):
            xml_bytes = uploaded.read()
            result = analyze_xml_bytes(xml_bytes, uploaded.name)

            # Save to outputs
            OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = result.metadata.analyzed_at_utc.replace(":", "").replace("Z", "")
            output_path = OUTPUTS_DIR / f"analysis_{timestamp}.json"
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

            # Store in session state
            st.session_state["analysis_result"] = result.to_dict()
            st.session_state["analysis_source"] = "uploaded"
            st.session_state["analysis_timestamp"] = timestamp
            st.session_state["output_path"] = str(output_path)

        st.success(f"✅ Analysis complete! Saved to: {output_path.name}")
        st.rerun()

    except XmlParseError as exc:
        st.error(f"❌ XML Error: {exc}")
    except Exception as exc:
        st.error(f"❌ Unexpected error: {exc}")

# Display analysis results if available
if "analysis_result" in st.session_state:
    result_data = st.session_state["analysis_result"]

    # Extract data
    metadata = result_data.get("metadata", {})
    metrics_base = result_data.get("metrics_base", [])
    kpis = result_data.get("kpis", [])
    red_flags = result_data.get("red_flags", [])
    coverage = result_data.get("coverage", {})

    # Convert to dicts for easy access
    metrics_dict = {m["key"]: m["value"] for m in metrics_base if m.get("value") is not None}
    kpis_dict = {k["key"]: k for k in kpis if k.get("value") is not None}

    st.markdown("---")

    # ============== EXECUTIVE DASHBOARD ==============
    st.markdown("## 📊 Executive Dashboard")

    # Company info header - prominent display
    company_name = metadata.get("company_name", "Unknown Company")
    krs = metadata.get("krs", "")
    nip = metadata.get("nip", "")
    period_from = metadata.get("period_from", "")
    period_to = metadata.get("period_to", "")

    st.markdown(f"### 🏢 {company_name}")
    company_info = []
    if krs:
        company_info.append(f"**KRS:** {krs}")
    if nip:
        company_info.append(f"**NIP:** {nip}")
    if period_from and period_to:
        company_info.append(f"**Okres:** {period_from} → {period_to}")
    if company_info:
        st.markdown(" | ".join(company_info))

    st.markdown("")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**File:** `{metadata.get('filename', 'Unknown')}`")
        st.markdown(f"**Schema:** `{metadata.get('schema_id_slug', 'Unknown')}`")
    with col2:
        st.metric("Coverage", f"{coverage.get('percent', 0):.0f}%")
    with col3:
        detected_flags = len([f for f in red_flags if f.get("detected")])
        st.metric("Red Flags", detected_flags, delta=None if detected_flags == 0 else "warning")

    st.markdown("---")

    # ============== KEY METRICS ==============
    st.markdown("### 💰 Key Financial Metrics")

    # Check for unit - if PLN_thousands, multiply by 1000
    unit_multiplier = 1
    if metrics_base and metrics_base[0].get("unit") == "PLN_thousands":
        unit_multiplier = 1000

    # Helper to get value with fallback key names
    def get_metric(*keys):
        for key in keys:
            val = metrics_dict.get(key)
            if val is not None:
                return val * unit_multiplier
        return None

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        revenue = get_metric("pl_revenue")
        if revenue:
            st.metric("Revenue" if lang == "EN" else "Przychody", f"{revenue / 1_000_000:,.1f} m PLN")
        else:
            st.metric("Revenue" if lang == "EN" else "Przychody", "N/A")

    with col2:
        net_income = get_metric("pl_net_income", "pl_net_profit")
        if net_income is not None:
            st.metric("Net Income" if lang == "EN" else "Zysk Netto", f"{net_income / 1_000_000:,.1f} m PLN")
        else:
            st.metric("Net Income" if lang == "EN" else "Zysk Netto", "N/A")

    with col3:
        total_assets = get_metric("bs_total_assets", "bs_assets_total")
        if total_assets:
            st.metric("Total Assets" if lang == "EN" else "Aktywa", f"{total_assets / 1_000_000:,.1f} m PLN")
        else:
            st.metric("Total Assets" if lang == "EN" else "Aktywa", "N/A")

    with col4:
        equity = get_metric("bs_equity_total", "bs_equity")
        if equity is not None:
            st.metric("Equity" if lang == "EN" else "Kapitał Własny", f"{equity / 1_000_000:,.1f} m PLN")
        else:
            st.metric("Equity" if lang == "EN" else "Kapitał Własny", "N/A")

    st.markdown("---")

    # ============== KPI SUMMARY ==============
    st.markdown("### 📈 Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**💧 Liquidity**" if lang == "EN" else "**💧 Płynność**")
        current_ratio = kpis_dict.get("current_ratio", {}).get("value")
        if current_ratio:
            color = "🟢" if current_ratio >= 1.5 else "🟡" if current_ratio >= 1.0 else "🔴"
            st.write(f"{color} Current Ratio: **{current_ratio:.2f}**")
        else:
            st.write("Current Ratio: N/A")

    with col2:
        st.markdown("**📊 Profitability**" if lang == "EN" else "**📊 Rentowność**")
        roe = kpis_dict.get("roe", {}).get("value")
        roa = kpis_dict.get("roa", {}).get("value")
        net_margin = kpis_dict.get("net_profit_margin", {}).get("value")

        if roe is not None:
            color = "🟢" if roe > 10 else "🟡" if roe > 0 else "🔴"
            st.write(f"{color} ROE: **{roe:.1f}%**")
        if roa is not None:
            color = "🟢" if roa > 5 else "🟡" if roa > 0 else "🔴"
            st.write(f"{color} ROA: **{roa:.1f}%**")
        if net_margin is not None:
            color = "🟢" if net_margin > 5 else "🟡" if net_margin > 0 else "🔴"
            st.write(f"{color} Net Margin: **{net_margin:.1f}%**")

    with col3:
        st.markdown("**⚖️ Capital Structure**" if lang == "EN" else "**⚖️ Struktura Kapitału**")
        debt_ratio = kpis_dict.get("debt_ratio", {}).get("value")
        equity_ratio = kpis_dict.get("equity_ratio", {}).get("value")

        if debt_ratio is not None:
            color = "🟢" if debt_ratio < 50 else "🟡" if debt_ratio < 70 else "🔴"
            st.write(f"{color} Debt Ratio: **{debt_ratio:.1f}%**")
        if equity_ratio is not None:
            color = "🟢" if equity_ratio > 40 else "🟡" if equity_ratio > 25 else "🔴"
            st.write(f"{color} Equity Ratio: **{equity_ratio:.1f}%**")

    # All KPIs in expander
    with st.expander("📋 View All KPIs" if lang == "EN" else "📋 Zobacz Wszystkie KPI"):
        if kpis:
            kpi_df = pd.DataFrame([
                {
                    "KPI": k.get("name", k.get("key", "")),
                    "Value": f"{k.get('value'):.2f}{k.get('unit', '')}" if k.get("value") is not None else "N/A",
                    "Category": k.get("category", "Other"),
                    "Interpretation": k.get("interpretation", "")[:50] + "..." if len(k.get("interpretation", "")) > 50 else k.get("interpretation", "")
                }
                for k in kpis
            ])
            st.dataframe(kpi_df, use_container_width=True, hide_index=True)
        else:
            st.info("No KPIs calculated")

    st.markdown("---")

    # ============== RED FLAGS ==============
    st.markdown("### 🚩 Red Flags Analysis")

    detected_flags = [f for f in red_flags if f.get("detected")]

    if detected_flags:
        # Count by severity
        high = len([f for f in detected_flags if f.get("severity") == "high"])
        medium = len([f for f in detected_flags if f.get("severity") == "medium"])
        low = len([f for f in detected_flags if f.get("severity") == "low"])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔴 High", high)
        with col2:
            st.metric("🟡 Medium", medium)
        with col3:
            st.metric("🟢 Low", low)

        st.markdown("---")

        # Display each flag
        for flag in sorted(detected_flags, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("severity", "low"), 3)):
            severity = flag.get("severity", "low")
            color_map = {"high": "🔴", "medium": "🟡", "low": "🟢"}

            with st.container():
                st.markdown(f"**{color_map.get(severity, '⚪')} {flag.get('title', 'Unknown')}** ({severity.upper()})")
                st.write(flag.get("description", ""))
                st.caption(f"Details: {flag.get('details', 'N/A')}")
                st.divider()
    else:
        st.success("✅ No red flags detected! All financial indicators look healthy." if lang == "EN" else "✅ Nie wykryto czerwonych flag! Wszystkie wskaźniki finansowe wyglądają zdrowo.")

    # View all checks
    with st.expander("📋 View All Checks" if lang == "EN" else "📋 Zobacz Wszystkie Testy"):
        for flag in red_flags:
            status = "⚠️" if flag.get("detected") else "✅"
            st.write(f"{status} **{flag.get('title', 'Unknown')}**: {flag.get('details', 'N/A')}")

    st.markdown("---")

    # ============== EXPORT OPTIONS ==============
    st.markdown("### 📥 Export Options")

    col1, col2, col3 = st.columns(3)

    timestamp = st.session_state.get("analysis_timestamp", "export")

    with col1:
        # Recreate result object for export
        from core.contracts import AnalysisResult
        try:
            result_obj = AnalysisResult.from_dict(result_data)
            excel_data = export_to_excel(result_obj)
            st.download_button(
                "📊 Download Excel" if lang == "EN" else "📊 Pobierz Excel",
                data=excel_data,
                file_name=f"analysis_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception:
            st.button("📊 Excel (Error)", disabled=True, use_container_width=True)

    with col2:
        try:
            result_obj = AnalysisResult.from_dict(result_data)
            pdf_data = export_to_pdf(result_obj)
            st.download_button(
                "📑 Download PDF" if lang == "EN" else "📑 Pobierz PDF",
                data=pdf_data,
                file_name=f"analysis_{timestamp}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception:
            st.button("📑 PDF (Error)", disabled=True, use_container_width=True)

    with col3:
        json_data = json.dumps(result_data, indent=2, ensure_ascii=False)
        st.download_button(
            "📄 Download JSON" if lang == "EN" else "📄 Pobierz JSON",
            data=json_data,
            file_name=f"analysis_{timestamp}.json",
            mime="application/json",
            use_container_width=True
        )

    # Base metrics in expander
    with st.expander("📊 View Base Metrics" if lang == "EN" else "📊 Zobacz Metryki Bazowe"):
        if metrics_base:
            metrics_df = pd.DataFrame([
                {
                    "Metric": m.get("key", ""),
                    "Value": f"{m.get('value'):,.2f}" if m.get("value") is not None else "N/A",
                    "Unit": m.get("unit", "PLN"),
                    "Source": m.get("source_ref", "")[:30] if m.get("source_ref") else ""
                }
                for m in metrics_base
            ])
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        else:
            st.info("No base metrics available")

else:
    # No analysis loaded - show instructions
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        if lang == "EN":
            st.markdown("""
            ### How to Get Started

            1. **Upload XML File** - Use the sidebar to upload your e-Sprawozdanie XML file
            2. **Click Analyze** - The system will automatically detect the schema and extract data
            3. **Review Dashboard** - See KPIs, red flags, and financial metrics at a glance
            4. **Export Results** - Download reports in Excel, PDF, or JSON format

            ### Supported File Types

            - **JednostkaInna** - Standard company financial statements
            - **JednostkaMała** - Small entity financial statements
            - Values in PLN or thousands PLN (auto-detected)
            """)
        else:
            st.markdown("""
            ### Jak Rozpocząć

            1. **Prześlij Plik XML** - Użyj panelu bocznego, aby przesłać plik XML e-Sprawozdanie
            2. **Kliknij Analizuj** - System automatycznie wykryje schemat i wyodręmni dane
            3. **Przejrzyj Dashboard** - Zobacz KPI, czerwone flagi i metryki finansowe
            4. **Eksportuj Wyniki** - Pobierz raporty w formacie Excel, PDF lub JSON

            ### Obsługiwane Typy Plików

            - **JednostkaInna** - Standardowe sprawozdania finansowe firm
            - **JednostkaMała** - Sprawozdania finansowe małych podmiotów
            - Wartości w PLN lub tysiącach PLN (automatyczne wykrywanie)
            """)

    with col2:
        st.info("👈 Upload an XML file in the sidebar to begin" if lang == "EN" else "👈 Prześlij plik XML w panelu bocznym, aby rozpocząć")

# Footer
render_nvidia_badge()
