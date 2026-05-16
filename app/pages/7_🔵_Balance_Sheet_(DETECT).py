"""Balance Sheet page - Assets, Liabilities, and Equity Analysis.

This page displays the complete Balance Sheet (Bilans) data extracted from
Polish e-Sprawozdanie XML files in a single hierarchical table.
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
from core.modes import apply_mode
from core.components import render_nvidia_badge

st.set_page_config(
    page_title="Balance Sheet - AI CFO Dashboard",
    page_icon="📙",
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
    apply_mode("DETECT", lang)

    st.title(f"📙 {t('balance_sheet_title', lang)}")
    st.markdown(f"**{t('balance_sheet_subtitle', lang)}**")

    # Render file selector and load analysis data
    analysis_data = render_analysis_file_selector(lang)

    if not analysis_data:
        st.info(f"👈 {t('load_analysis_instruction', lang)}")

        # Show instructions
        if lang == "PL":
            st.markdown("""
            ### Jak korzystać ze strony Bilans:

            1. **Prześlij plik XML** - Użyj strony XML Analysis, aby przesłać plik e-Sprawozdanie
            2. **Załaduj analizę** - Wybierz plik z panelu bocznego
            3. **Przeglądaj dane** - Zobacz szczegóły bilansu (aktywa, pasywa, kapitał)
            """)
        else:
            st.markdown("""
            ### How to use the Balance Sheet page:

            1. **Upload XML file** - Use the XML Analysis page to upload an e-Sprawozdanie file
            2. **Load analysis** - Select a file from the sidebar
            3. **Review data** - See balance sheet details (assets, liabilities, equity)
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
    **{t('as_of', lang)}:** {period_to} | **{t('currency', lang)}:** {unit_suffix(unit_mode)}
    """)

    st.divider()

    # Get balance sheet data
    balance_sheet = analysis_data.get("balance_sheet", [])

    if not balance_sheet:
        st.warning("⚠️ No balance sheet data available." if lang == "EN" else "⚠️ Brak danych bilansowych.")
        st.info(
            "Please re-upload the XML file to extract balance sheet details."
            if lang == "EN" else
            "Prześlij ponownie plik XML, aby wyodrębnić szczegóły bilansu."
        )
        render_nvidia_badge()
        return

    # Check unit - if PLN_thousands, multiply by 1000
    # Get unit from metrics_base if available
    metrics_base = analysis_data.get("metrics_base", [])
    unit_multiplier = 1
    if metrics_base:
        first_metric = metrics_base[0] if metrics_base else {}
        if first_metric.get("unit") == "PLN_thousands":
            unit_multiplier = 1000

    # Build the hierarchical table
    st.subheader("📊 " + ("Complete Balance Sheet" if lang == "EN" else "Pełny Bilans"))

    # Prepare data for the table
    rows = []
    summary_data = {}

    for item in balance_sheet:
        key = item.get("key", "")
        label = item.get("label_pl" if lang == "PL" else "label_en", key)
        level = item.get("level", 0)
        current = item.get("current")
        prior = item.get("prior")

        # Apply unit multiplier
        if current is not None:
            current = current * unit_multiplier
        if prior is not None:
            prior = prior * unit_multiplier

        # Store summary data
        if key == "Aktywa":
            summary_data["total_assets"] = current
            summary_data["total_assets_prior"] = prior
        elif key == "Pasywa_A":
            summary_data["total_equity"] = current
            summary_data["total_equity_prior"] = prior
        elif key == "Pasywa_B":
            summary_data["total_liabilities"] = current
            summary_data["total_liabilities_prior"] = prior
        elif key == "Aktywa_A":
            summary_data["fixed_assets"] = current
        elif key == "Aktywa_B":
            summary_data["current_assets"] = current
        elif key == "Pasywa_B_III":
            summary_data["current_liabilities"] = current

        # Skip zero values for detailed items (level > 2) to reduce clutter
        if level > 3 and (current == 0 or current is None) and (prior == 0 or prior is None):
            continue

        # Format values
        indent = _get_indent(level)
        display_label = f"{indent}{label}"

        current_scaled = scale_for_display(current, unit_mode) if current is not None else None
        prior_scaled = scale_for_display(prior, unit_mode) if prior is not None else None

        current_str = pl_number_str(current_scaled, unit_mode) if current_scaled is not None else "—"
        prior_str = pl_number_str(prior_scaled, unit_mode) if prior_scaled is not None else "—"
        change_str = _format_change(current, prior) if current is not None and prior is not None else "—"

        # Style totals differently
        is_total = level <= 1

        rows.append({
            "position": display_label,
            "current": current_str,
            "prior": prior_str,
            "change": change_str,
            "is_total": is_total,
            "level": level,
        })

    # Create DataFrame
    if rows:
        df = pd.DataFrame(rows)

        # Rename columns for display
        col_names = {
            "position": "Pozycja" if lang == "PL" else "Position",
            "current": f"Bieżący ({period_to[:4] if period_to != 'N/A' else 'Current'})" if lang == "PL" else f"Current ({period_to[:4] if period_to != 'N/A' else 'Current'})",
            "prior": "Poprzedni" if lang == "PL" else "Prior",
            "change": "Zmiana" if lang == "PL" else "Change",
        }

        display_df = df[["position", "current", "prior", "change"]].rename(columns=col_names)

        # Apply styling
        def style_rows(row):
            idx = row.name
            level = df.iloc[idx]["level"]
            if level == 0:
                return ["font-weight: bold; background-color: #e3f2fd; font-size: 1.1em"] * len(row)
            elif level == 1:
                return ["font-weight: bold; background-color: #f5f5f5"] * len(row)
            return [""] * len(row)

        styled_df = display_df.style.apply(style_rows, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)

    # Key metrics summary
    st.divider()
    st.subheader("💰 " + ("Key Balance Sheet Metrics" if lang == "EN" else "Kluczowe Dane Bilansowe"))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_assets = summary_data.get("total_assets")
        if total_assets is not None:
            assets_scaled = scale_for_display(total_assets, unit_mode)
            st.metric(
                "Total Assets" if lang == "EN" else "Aktywa razem",
                f"{pl_number_str(assets_scaled, unit_mode)} {unit_suffix(unit_mode)}"
            )
        else:
            st.metric("Total Assets" if lang == "EN" else "Aktywa razem", "N/A")

    with col2:
        total_equity = summary_data.get("total_equity")
        if total_equity is not None:
            equity_scaled = scale_for_display(total_equity, unit_mode)
            delta = "Positive" if total_equity >= 0 else "Negative"
            delta_pl = "Dodatni" if total_equity >= 0 else "Ujemny"
            st.metric(
                "Equity" if lang == "EN" else "Kapitał własny",
                f"{pl_number_str(equity_scaled, unit_mode)} {unit_suffix(unit_mode)}",
                delta=delta if lang == "EN" else delta_pl
            )
        else:
            st.metric("Equity" if lang == "EN" else "Kapitał własny", "N/A")

    with col3:
        total_liabilities = summary_data.get("total_liabilities")
        if total_liabilities is not None:
            liab_scaled = scale_for_display(total_liabilities, unit_mode)
            st.metric(
                "Liabilities" if lang == "EN" else "Zobowiązania razem",
                f"{pl_number_str(liab_scaled, unit_mode)} {unit_suffix(unit_mode)}"
            )
        else:
            st.metric("Liabilities" if lang == "EN" else "Zobowiązania razem", "N/A")

    with col4:
        # Net working capital = Current Assets - Current Liabilities
        current_assets = summary_data.get("current_assets")
        current_liabilities = summary_data.get("current_liabilities")

        if current_assets is not None and current_liabilities is not None:
            nwc = current_assets - current_liabilities
            nwc_scaled = scale_for_display(nwc, unit_mode)
            delta = "Healthy" if nwc >= 0 else "Warning"
            delta_pl = "Zdrowy" if nwc >= 0 else "Ostrzeżenie"
            st.metric(
                "Net Working Capital" if lang == "EN" else "Kapitał Obrotowy Netto",
                f"{pl_number_str(nwc_scaled, unit_mode)} {unit_suffix(unit_mode)}",
                delta=delta if lang == "EN" else delta_pl
            )
        else:
            st.metric("Net Working Capital" if lang == "EN" else "Kapitał Obrotowy Netto", "N/A")

    # Balance Sheet KPIs
    st.divider()
    st.subheader("📈 " + ("Balance Sheet Ratios" if lang == "EN" else "Wskaźniki Bilansowe"))

    kpis = analysis_data.get("kpis", [])
    leverage_kpis = [k for k in kpis if k.get("category") == "Leverage" and k.get("value") is not None]

    if leverage_kpis:
        cols = st.columns(min(len(leverage_kpis), 4))
        for i, kpi in enumerate(leverage_kpis[:4]):
            with cols[i]:
                value = kpi.get("value")
                unit = kpi.get("unit", "")
                name = kpi.get("name", kpi.get("key", ""))

                # Color coding for debt ratios
                if value is not None:
                    if "debt" in name.lower():
                        if value < 50:
                            color = "🟢"
                        elif value < 70:
                            color = "🟡"
                        else:
                            color = "🔴"
                    else:
                        if value > 40:
                            color = "🟢"
                        elif value > 25:
                            color = "🟡"
                        else:
                            color = "🔴"
                    st.metric(name, f"{color} {value:.1f}{unit}")
                else:
                    st.metric(name, "N/A")
    else:
        # Calculate basic ratios from summary data
        total_assets = summary_data.get("total_assets")
        total_equity = summary_data.get("total_equity")
        total_liabilities = summary_data.get("total_liabilities")

        if total_assets and total_assets > 0:
            col1, col2, col3 = st.columns(3)

            with col1:
                if total_equity is not None:
                    equity_ratio = (total_equity / total_assets) * 100
                    color = "🟢" if equity_ratio > 40 else ("🟡" if equity_ratio > 25 else "🔴")
                    st.metric(
                        "Equity Ratio" if lang == "EN" else "Wskaźnik Kapitału Własnego",
                        f"{color} {equity_ratio:.1f}%"
                    )

            with col2:
                if total_liabilities is not None:
                    debt_ratio = (total_liabilities / total_assets) * 100
                    color = "🟢" if debt_ratio < 50 else ("🟡" if debt_ratio < 70 else "🔴")
                    st.metric(
                        "Debt Ratio" if lang == "EN" else "Wskaźnik Zadłużenia",
                        f"{color} {debt_ratio:.1f}%"
                    )

            with col3:
                if total_equity is not None and total_equity > 0 and total_liabilities is not None:
                    dte = total_liabilities / total_equity
                    color = "🟢" if dte < 1.5 else ("🟡" if dte < 2.5 else "🔴")
                    st.metric(
                        "Debt-to-Equity" if lang == "EN" else "Dług do Kapitału",
                        f"{color} {dte:.2f}x"
                    )
        else:
            st.info("Brak dostępnych wskaźników" if lang == "PL" else "No ratios available")

    # Balance Verification
    st.divider()
    st.subheader(f"✅ {t('balance_sheet_verification', lang)}")

    total_assets = summary_data.get("total_assets")
    total_equity = summary_data.get("total_equity")
    total_liabilities = summary_data.get("total_liabilities")

    if total_assets is not None and total_equity is not None and total_liabilities is not None:
        equity_plus_liabilities = total_equity + total_liabilities
        difference = abs(total_assets - equity_plus_liabilities)

        if difference < 1:  # Allow for rounding errors
            st.success(f"✅ {t('balance_is_balanced', lang)}")
        else:
            st.warning(f"⚠️ {t('balance_discrepancy', lang)}: {difference:,.0f} PLN")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                t("total_assets", lang),
                f"{scale_for_display(total_assets, unit_mode):,.1f} {unit_suffix(unit_mode)}"
            )
        with col2:
            st.metric(
                t("equity_plus_liabilities", lang),
                f"{scale_for_display(equity_plus_liabilities, unit_mode):,.1f} {unit_suffix(unit_mode)}"
            )
        with col3:
            diff_scaled = scale_for_display(difference, unit_mode)
            st.metric(t("difference", lang), f"{diff_scaled:,.1f} {unit_suffix(unit_mode)}")
    else:
        st.info(t("cannot_verify_balance", lang))

    st.divider()
    st.caption(t("data_source_bilans", lang))

    # Footer
    render_nvidia_badge()


if __name__ == "__main__":
    main()
