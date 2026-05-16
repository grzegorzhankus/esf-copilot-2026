"""P&L (Profit & Loss) page - Income Statement Analysis.

This page displays the Profit & Loss statement (RZiS) data extracted from
Polish e-Sprawozdanie XML files in a hierarchical table format.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from core.formatting import pl_number_str, unit_suffix, scale_for_display
from core.i18n import t
from core.analysis_file_selector import render_analysis_file_selector
from core.language_selector import render_language_selector
from core.modes import render_mode_header
from core.components import render_nvidia_badge

st.set_page_config(
    page_title="P&L - AI CFO Dashboard",
    page_icon="📈",
    layout="wide",
)


def _get_indent(level: int) -> str:
    """Get indentation string based on hierarchy level."""
    if level == 0:
        return ""
    return "    " * (level - 1)


def _format_change(current: float, prior: float) -> str:
    """Calculate and format percentage change."""
    if prior is None or prior == 0:
        return "—"
    change = ((current - prior) / abs(prior)) * 100
    if change > 0:
        return f"+{change:.1f}%"
    return f"{change:.1f}%"


def main():
    # Render language selector and get current language
    lang = render_language_selector()
    render_mode_header("DETECT", lang)

    st.title(f"📈 {t('pl_title', lang)}")
    st.markdown(f"**{t('pl_subtitle', lang)}**")

    # Render file selector and load analysis data
    analysis_data = render_analysis_file_selector(lang)

    if not analysis_data:
        st.info(f"👈 {t('load_analysis_instruction', lang)}")

        # Show instructions
        if lang == "PL":
            st.markdown("""
            ### Jak korzystać ze strony Rachunek Zysków i Strat:

            1. **Prześlij plik XML** - Użyj strony XML Analysis, aby przesłać plik e-Sprawozdanie
            2. **Załaduj analizę** - Wybierz plik z panelu bocznego
            3. **Przeglądaj dane** - Zobacz szczegóły rachunku zysków i strat
            """)
        else:
            st.markdown("""
            ### How to use the P&L page:

            1. **Upload XML file** - Use the XML Analysis page to upload an e-Sprawozdanie file
            2. **Load analysis** - Select a file from the sidebar
            3. **Review data** - See the profit & loss statement details
            """)

        render_nvidia_badge()
        return

    # Extract metadata
    metadata = analysis_data.get("metadata", {})
    company_name = metadata.get("company_name") or metadata.get("filename", "Unknown Company")
    period_from = metadata.get("period_from", "N/A")
    period_to = metadata.get("period_to", "N/A")

    # Get display unit from session state or default
    unit_mode = st.session_state.get("display_unit", "m PLN")

    st.markdown(f"""
    ### {company_name}
    **{t('period', lang)}:** {period_from} → {period_to} | **{t('currency', lang)}:** {unit_suffix(unit_mode)}
    """)

    st.divider()

    # Get P&L statement data
    pl_statement = analysis_data.get("pl_statement", [])

    # Check unit - if PLN_thousands, multiply by 1000
    metrics_base = analysis_data.get("metrics_base", [])
    unit_multiplier = 1
    if metrics_base:
        first_metric = metrics_base[0] if metrics_base else {}
        if first_metric.get("unit") == "PLN_thousands":
            unit_multiplier = 1000

    # If no pl_statement data, fall back to metrics_base
    if not pl_statement:
        st.info("📊 " + ("Using base metrics view. Re-analyze XML for detailed hierarchical P&L." if lang == "EN"
                        else "Używam widoku metryk bazowych. Przeanalizuj ponownie XML dla szczegółowego RZiS."))

        # Fall back to metrics_base display
        metrics_dict = {}
        for metric in metrics_base:
            key = metric.get("key", "")
            value = metric.get("value")
            unit = metric.get("unit", "PLN")
            if value is not None and key.startswith("pl_"):
                if unit == "PLN_thousands":
                    value = value * 1000
                metrics_dict[key] = value

        if metrics_dict:
            # Display key P&L metrics
            st.subheader("💰 " + ("Key P&L Data" if lang == "EN" else "Kluczowe Dane RZiS"))

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                revenue = metrics_dict.get("pl_revenue")
                if revenue is not None:
                    scaled = scale_for_display(revenue, unit_mode)
                    st.metric("Revenue" if lang == "EN" else "Przychody",
                             f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}")
                else:
                    st.metric("Revenue" if lang == "EN" else "Przychody", "N/A")

            with col2:
                gross_profit = metrics_dict.get("pl_gross_profit")
                if gross_profit is not None:
                    scaled = scale_for_display(gross_profit, unit_mode)
                    st.metric("Gross Profit" if lang == "EN" else "Zysk Brutto",
                             f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}")
                else:
                    st.metric("Gross Profit" if lang == "EN" else "Zysk Brutto", "N/A")

            with col3:
                ebit = metrics_dict.get("pl_ebit")
                if ebit is not None:
                    scaled = scale_for_display(ebit, unit_mode)
                    st.metric("EBIT", f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}")
                else:
                    st.metric("EBIT", "N/A")

            with col4:
                net_profit = metrics_dict.get("pl_net_income") or metrics_dict.get("pl_net_profit")
                if net_profit is not None:
                    scaled = scale_for_display(net_profit, unit_mode)
                    delta = "Profit" if net_profit >= 0 else "Loss"
                    delta_pl = "Zysk" if net_profit >= 0 else "Strata"
                    st.metric("Net Profit" if lang == "EN" else "Zysk Netto",
                             f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                             delta=delta if lang == "EN" else delta_pl)
                else:
                    st.metric("Net Profit" if lang == "EN" else "Zysk Netto", "N/A")

            # Show all P&L metrics
            with st.expander("📋 " + ("All P&L Metrics" if lang == "EN" else "Wszystkie Metryki RZiS")):
                pl_df = pd.DataFrame([
                    {
                        "Metric": k,
                        "Value": f"{v:,.0f}" if v is not None else "N/A",
                    }
                    for k, v in sorted(metrics_dict.items())
                ])
                st.dataframe(pl_df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ " + ("No P&L data available." if lang == "EN" else "Brak danych RZiS."))

        render_nvidia_badge()
        return

    # Build the hierarchical P&L table
    st.subheader("📊 " + ("Income Statement" if lang == "EN" else "Rachunek Zysków i Strat"))

    # Prepare data for the table
    rows = []
    summary_data = {}

    for item in pl_statement:
        key = item.get("key", "")
        label = item.get("label_pl" if lang == "PL" else "label_en", key)
        level = item.get("level", 0)
        current = item.get("current")
        prior = item.get("prior")

        # Skip if no data
        if current is None and prior is None:
            continue

        # Apply unit multiplier
        if current is not None:
            current = current * unit_multiplier
        if prior is not None:
            prior = prior * unit_multiplier

        # Store summary data for key items
        clean_key = key.replace("RZiSKalk_", "").replace("RZiS_", "")
        if clean_key == "A":
            summary_data["revenue"] = current
            summary_data["revenue_prior"] = prior
        elif clean_key == "C":
            summary_data["gross_profit"] = current
            summary_data["gross_profit_prior"] = prior
        elif clean_key in ("I", "G"):
            if "ebit" not in summary_data:
                summary_data["ebit"] = current
                summary_data["ebit_prior"] = prior
        elif clean_key == "L":
            summary_data["profit_before_tax"] = current
            summary_data["profit_before_tax_prior"] = prior
        elif clean_key == "O":
            summary_data["net_profit"] = current
            summary_data["net_profit_prior"] = prior

        # Format values
        indent = _get_indent(level)
        display_label = f"{indent}{label}"

        current_str = "—"
        prior_str = "—"
        change_str = "—"

        if current is not None:
            scaled = scale_for_display(current, unit_mode)
            current_str = pl_number_str(scaled, unit_mode)

        if prior is not None:
            scaled = scale_for_display(prior, unit_mode)
            prior_str = pl_number_str(scaled, unit_mode)

        if current is not None and prior is not None:
            change_str = _format_change(current, prior)

        # Style for level 0 and 1 (bold)
        if level <= 1:
            display_label = f"**{display_label}**"

        rows.append({
            "Item" if lang == "EN" else "Pozycja": display_label,
            f"Current ({period_to})" if lang == "EN" else f"Bieżący ({period_to})": current_str,
            f"Prior ({period_from})" if lang == "EN" else f"Poprzedni ({period_from})": prior_str,
            "Change" if lang == "EN" else "Zmiana": change_str,
        })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=min(len(rows) * 35 + 40, 600)
        )
    else:
        st.warning("⚠️ " + ("No P&L items found." if lang == "EN" else "Nie znaleziono pozycji RZiS."))

    # Key P&L metrics summary
    st.divider()
    st.subheader("💰 " + ("Key P&L Data" if lang == "EN" else "Kluczowe Dane RZiS"))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        revenue = summary_data.get("revenue")
        revenue_prior = summary_data.get("revenue_prior")
        if revenue is not None:
            scaled = scale_for_display(revenue, unit_mode)
            delta = None
            if revenue_prior and revenue_prior != 0:
                delta = f"{((revenue - revenue_prior) / abs(revenue_prior)) * 100:+.1f}%"
            st.metric("Revenue" if lang == "EN" else "Przychody",
                     f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                     delta=delta)
        else:
            st.metric("Revenue" if lang == "EN" else "Przychody", "N/A")

    with col2:
        gross_profit = summary_data.get("gross_profit")
        gross_profit_prior = summary_data.get("gross_profit_prior")
        if gross_profit is not None:
            scaled = scale_for_display(gross_profit, unit_mode)
            delta = None
            if gross_profit_prior and gross_profit_prior != 0:
                delta = f"{((gross_profit - gross_profit_prior) / abs(gross_profit_prior)) * 100:+.1f}%"
            st.metric("Gross Profit" if lang == "EN" else "Zysk Brutto",
                     f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                     delta=delta)
        else:
            st.metric("Gross Profit" if lang == "EN" else "Zysk Brutto", "N/A")

    with col3:
        ebit = summary_data.get("ebit")
        ebit_prior = summary_data.get("ebit_prior")
        if ebit is not None:
            scaled = scale_for_display(ebit, unit_mode)
            delta = None
            if ebit_prior and ebit_prior != 0:
                delta = f"{((ebit - ebit_prior) / abs(ebit_prior)) * 100:+.1f}%"
            st.metric("EBIT", f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                     delta=delta)
        else:
            st.metric("EBIT", "N/A")

    with col4:
        net_profit = summary_data.get("net_profit")
        net_profit_prior = summary_data.get("net_profit_prior")
        if net_profit is not None:
            scaled = scale_for_display(net_profit, unit_mode)
            status = "Profit" if net_profit >= 0 else "Loss"
            status_pl = "Zysk" if net_profit >= 0 else "Strata"
            delta = None
            if net_profit_prior and net_profit_prior != 0:
                delta = f"{((net_profit - net_profit_prior) / abs(net_profit_prior)) * 100:+.1f}%"
            st.metric("Net Profit" if lang == "EN" else "Zysk Netto",
                     f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                     delta=delta,
                     delta_color="normal" if net_profit >= 0 else "inverse")
        else:
            st.metric("Net Profit" if lang == "EN" else "Zysk Netto", "N/A")

    # KPIs related to P&L
    st.divider()
    st.subheader(f"📈 {t('profitability_kpis', lang)}")

    kpis = analysis_data.get("kpis", [])
    profitability_kpis = [k for k in kpis if k.get("category") == "Profitability" and k.get("value") is not None]

    if profitability_kpis:
        kpi_cols = st.columns(min(len(profitability_kpis), 4))
        for i, kpi in enumerate(profitability_kpis[:4]):
            with kpi_cols[i]:
                value = kpi.get("value")
                unit = kpi.get("unit", "")
                name = kpi.get("name", kpi.get("key", ""))

                # Color coding
                if value is not None:
                    if value > 10:
                        color = "🟢"
                    elif value > 0:
                        color = "🟡"
                    else:
                        color = "🔴"
                    st.metric(name, f"{color} {value:.1f}{unit}")
                else:
                    st.metric(name, "N/A")

        # Show interpretation
        with st.expander(f"📖 {t('kpi_interpretations', lang)}"):
            for kpi in profitability_kpis:
                kpi_name = kpi.get("name", kpi.get("key", ""))
                interpretation = kpi.get("interpretation", "N/A")
                st.write(f"**{kpi_name}**: {interpretation}")
    else:
        st.info(t("no_profitability_kpis", lang))

    st.divider()
    st.caption(t('data_source_rzis', lang))

    # Footer
    render_nvidia_badge()


if __name__ == "__main__":
    main()
