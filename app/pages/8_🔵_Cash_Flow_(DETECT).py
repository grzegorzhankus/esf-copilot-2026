"""Cash Flow page - Statement of Cash Flows Analysis.

This page displays the Cash Flow Statement (Rachunek Przepływów Pieniężnych) data
extracted from Polish e-Sprawozdanie XML files in a hierarchical table format.
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
    page_title="Cash Flow - AI CFO Dashboard",
    page_icon="💵",
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

    st.title(f"💵 {t('cash_flow_title', lang)}")
    st.markdown(f"**{t('analyze_cash_flows_subtitle', lang)}**")

    # Render file selector and load analysis data
    analysis_data = render_analysis_file_selector(lang)

    if not analysis_data:
        st.info(f"👈 {t('load_analysis_instruction', lang)}")

        # Show instructions
        if lang == "PL":
            st.markdown("""
            ### Jak korzystać ze strony Rachunek Przepływów Pieniężnych:

            1. **Prześlij plik XML** - Użyj strony XML Analysis, aby przesłać plik e-Sprawozdanie
            2. **Załaduj analizę** - Wybierz plik z panelu bocznego
            3. **Przeglądaj dane** - Zobacz przepływy z działalności operacyjnej, inwestycyjnej i finansowej

            ### Co zawiera Rachunek Przepływów Pieniężnych:

            - **Działalność operacyjna** - gotówka z podstawowej działalności firmy
            - **Działalność inwestycyjna** - wydatki na aktywa trwałe i inwestycje
            - **Działalność finansowa** - finansowanie zewnętrzne i dywidendy
            """)
        else:
            st.markdown("""
            ### How to use the Cash Flow page:

            1. **Upload XML file** - Use the XML Analysis page to upload an e-Sprawozdanie file
            2. **Load analysis** - Select a file from the sidebar
            3. **Review data** - See operating, investing, and financing cash flows

            ### What the Cash Flow Statement contains:

            - **Operating activities** - cash from the company's core business
            - **Investing activities** - spending on fixed assets and investments
            - **Financing activities** - external financing and dividends
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

    # Get Cash Flow statement data
    cf_statement = analysis_data.get("cf_statement", [])

    # Check unit - if PLN_thousands, multiply by 1000
    metrics_base = analysis_data.get("metrics_base", [])
    unit_multiplier = 1
    if metrics_base:
        first_metric = metrics_base[0] if metrics_base else {}
        if first_metric.get("unit") == "PLN_thousands":
            unit_multiplier = 1000

    # If no cf_statement data, fall back to metrics_base
    if not cf_statement:
        st.info("📊 " + ("Using base metrics view. Re-analyze XML for detailed hierarchical Cash Flow." if lang == "EN"
                        else "Używam widoku metryk bazowych. Przeanalizuj ponownie XML dla szczegółowego RPP."))

        # Build metrics dictionary for easy access
        metrics_dict = {}
        for metric in metrics_base:
            key = metric.get("key", "")
            value = metric.get("value")
            unit = metric.get("unit", "PLN")
            if value is not None and key.startswith("cf_"):
                if unit == "PLN_thousands":
                    value = value * 1000
                metrics_dict[key] = value

        if metrics_dict:
            # Display key CF metrics
            st.subheader("💰 " + ("Key Cash Flow Data" if lang == "EN" else "Kluczowe Dane RPP"))

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                ocf = metrics_dict.get("cf_operating_total")
                if ocf is not None:
                    scaled = scale_for_display(ocf, unit_mode)
                    delta = "Positive" if ocf >= 0 else "Negative"
                    delta_pl = "Dodatni" if ocf >= 0 else "Ujemny"
                    st.metric(t("operating_cash_flow", lang),
                             f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                             delta=delta if lang == "EN" else delta_pl)
                else:
                    st.metric(t("operating_cash_flow", lang), "N/A")

            with col2:
                icf = metrics_dict.get("cf_investing_total")
                if icf is not None:
                    scaled = scale_for_display(icf, unit_mode)
                    st.metric(t("investing_cash_flow", lang),
                             f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}")
                else:
                    st.metric(t("investing_cash_flow", lang), "N/A")

            with col3:
                fcf = metrics_dict.get("cf_financing_total")
                if fcf is not None:
                    scaled = scale_for_display(fcf, unit_mode)
                    st.metric(t("financing_cash_flow", lang),
                             f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}")
                else:
                    st.metric(t("financing_cash_flow", lang), "N/A")

            with col4:
                net_change = metrics_dict.get("cf_net_change")
                if net_change is not None:
                    scaled = scale_for_display(net_change, unit_mode)
                    delta = "Increased" if net_change >= 0 else "Decreased"
                    delta_pl = "Wzrost" if net_change >= 0 else "Spadek"
                    st.metric(t("net_change", lang),
                             f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                             delta=delta if lang == "EN" else delta_pl)
                else:
                    st.metric(t("net_change", lang), "N/A")

            # Show all CF metrics
            with st.expander("📋 " + ("All Cash Flow Metrics" if lang == "EN" else "Wszystkie Metryki RPP")):
                cf_df = pd.DataFrame([
                    {
                        "Metric": k,
                        "Value": f"{v:,.0f}" if v is not None else "N/A",
                    }
                    for k, v in sorted(metrics_dict.items())
                ])
                st.dataframe(cf_df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ " + ("No Cash Flow data available." if lang == "EN" else "Brak danych RPP."))

        render_nvidia_badge()
        return

    # Build the hierarchical Cash Flow table
    st.subheader("📊 " + ("Cash Flow Statement" if lang == "EN" else "Rachunek Przepływów Pieniężnych"))

    # Prepare data for the table
    rows = []
    summary_data = {}

    for item in cf_statement:
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
        clean_key = key.replace("RachPrzeplywow_", "").replace("PrzeplywyPosr_", "").replace("PrzeplywyBezposr_", "")
        # Remove doubled prefix (A_A_III -> A_III)
        parts = clean_key.split("_")
        if len(parts) >= 2 and parts[0] == parts[1]:
            clean_key = "_".join(parts[1:])

        if clean_key in ("A_III", "A_A_III"):
            summary_data["operating"] = current
            summary_data["operating_prior"] = prior
        elif clean_key in ("B_III", "B_B_III"):
            summary_data["investing"] = current
            summary_data["investing_prior"] = prior
        elif clean_key in ("C_III", "C_C_III"):
            summary_data["financing"] = current
            summary_data["financing_prior"] = prior
        elif clean_key == "D":
            summary_data["net_change"] = current
            summary_data["net_change_prior"] = prior
        elif clean_key == "F":
            summary_data["opening"] = current
        elif clean_key == "G":
            summary_data["closing"] = current

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
        st.warning("⚠️ " + ("No Cash Flow items found." if lang == "EN" else "Nie znaleziono pozycji RPP."))

    # Key Cash Flow metrics summary
    st.divider()
    st.subheader("💰 " + ("Key Cash Flow Data" if lang == "EN" else "Kluczowe Dane RPP"))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        operating = summary_data.get("operating")
        operating_prior = summary_data.get("operating_prior")
        if operating is not None:
            scaled = scale_for_display(operating, unit_mode)
            delta = None
            if operating_prior and operating_prior != 0:
                delta = f"{((operating - operating_prior) / abs(operating_prior)) * 100:+.1f}%"
            st.metric(t("operating_cash_flow", lang),
                     f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                     delta=delta)
        else:
            st.metric(t("operating_cash_flow", lang), "N/A")

    with col2:
        investing = summary_data.get("investing")
        investing_prior = summary_data.get("investing_prior")
        if investing is not None:
            scaled = scale_for_display(investing, unit_mode)
            delta = None
            if investing_prior and investing_prior != 0:
                delta = f"{((investing - investing_prior) / abs(investing_prior)) * 100:+.1f}%"
            st.metric(t("investing_cash_flow", lang),
                     f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                     delta=delta)
        else:
            st.metric(t("investing_cash_flow", lang), "N/A")

    with col3:
        financing = summary_data.get("financing")
        financing_prior = summary_data.get("financing_prior")
        if financing is not None:
            scaled = scale_for_display(financing, unit_mode)
            delta = None
            if financing_prior and financing_prior != 0:
                delta = f"{((financing - financing_prior) / abs(financing_prior)) * 100:+.1f}%"
            st.metric(t("financing_cash_flow", lang),
                     f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                     delta=delta)
        else:
            st.metric(t("financing_cash_flow", lang), "N/A")

    with col4:
        net_change = summary_data.get("net_change")
        net_change_prior = summary_data.get("net_change_prior")
        if net_change is not None:
            scaled = scale_for_display(net_change, unit_mode)
            delta = None
            if net_change_prior and net_change_prior != 0:
                delta = f"{((net_change - net_change_prior) / abs(net_change_prior)) * 100:+.1f}%"
            st.metric(t("net_change", lang),
                     f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}",
                     delta=delta,
                     delta_color="normal" if net_change >= 0 else "inverse")
        else:
            st.metric(t("net_change", lang), "N/A")

    # Cash position summary
    st.divider()
    st.subheader("🏦 " + ("Cash Position" if lang == "EN" else "Stan Środków Pieniężnych"))

    col1, col2, col3 = st.columns(3)

    with col1:
        opening = summary_data.get("opening")
        if opening is not None:
            scaled = scale_for_display(opening, unit_mode)
            st.metric("Opening Balance" if lang == "EN" else "Saldo początkowe",
                     f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}")
        else:
            st.metric("Opening Balance" if lang == "EN" else "Saldo początkowe", "N/A")

    with col2:
        net_change = summary_data.get("net_change")
        if net_change is not None:
            scaled = scale_for_display(net_change, unit_mode)
            indicator = "+" if net_change >= 0 else ""
            st.metric("Net Change" if lang == "EN" else "Zmiana netto",
                     f"{indicator}{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}")
        else:
            st.metric("Net Change" if lang == "EN" else "Zmiana netto", "N/A")

    with col3:
        closing = summary_data.get("closing")
        if closing is not None:
            scaled = scale_for_display(closing, unit_mode)
            st.metric("Closing Balance" if lang == "EN" else "Saldo końcowe",
                     f"{pl_number_str(scaled, unit_mode)} {unit_suffix(unit_mode)}")
        else:
            st.metric("Closing Balance" if lang == "EN" else "Saldo końcowe", "N/A")

    # Cash Flow KPIs
    st.divider()
    st.subheader(f"📈 {t('cash_flow_kpis', lang)}")

    kpis = analysis_data.get("kpis", [])
    cash_flow_kpis = [k for k in kpis if k.get("category") == "Cash Flow" and k.get("value") is not None]

    if cash_flow_kpis:
        kpi_cols = st.columns(min(len(cash_flow_kpis), 4))
        for i, kpi in enumerate(cash_flow_kpis[:4]):
            with kpi_cols[i]:
                value = kpi.get("value")
                unit = kpi.get("unit", "")
                name = kpi.get("name", kpi.get("key", ""))

                # Color coding
                if value is not None:
                    if value > 1:
                        color = "🟢"
                    elif value > 0:
                        color = "🟡"
                    else:
                        color = "🔴"
                    st.metric(name, f"{color} {value:.2f}{unit}")
                else:
                    st.metric(name, "N/A")

        # Show interpretation
        with st.expander(f"📖 {t('kpi_interpretations', lang)}"):
            for kpi in cash_flow_kpis:
                kpi_name = kpi.get("name", kpi.get("key", ""))
                interpretation = kpi.get("interpretation", "N/A")
                st.write(f"**{kpi_name}**: {interpretation}")
    else:
        st.info(t("no_cash_flow_kpis", lang))

    st.divider()
    st.caption(t('data_source_cashflow', lang))

    # Footer
    render_nvidia_badge()


if __name__ == "__main__":
    main()
