from __future__ import annotations

import json
from pathlib import Path
import sys

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.forecasting import simple_linear_forecast, scenario_analysis, get_forecast_summary
from core.i18n import t
from core.language_selector import render_language_selector
from core.components import render_nvidia_badge

st.set_page_config(page_title="Forecasting - AI CFO Dashboard", layout="wide", page_icon="📈")

# Render language selector and get current language
lang = render_language_selector()

st.title(f"📈 {t('forecasting_title', lang)}")
st.write(t("forecasting_subtitle", lang))

# Sidebar for analysis selection
with st.sidebar:
    st.markdown(f"### 📁 {t('load_analysis_title', lang)}")
    outputs_dir = Path("outputs")

    selected_analysis = None

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
                        selected_analysis = json.load(f)
                    st.success(f"{t('loaded_label', lang)}: {selected_file}")
                except Exception as e:
                    st.error(f"{t('error_loading_file', lang)}: {e}")
        else:
            st.info(t("no_analysis_files", lang))
    else:
        st.info(t("no_outputs_dir", lang))

    st.markdown("---")

    # Forecasting parameters
    st.markdown(f"### ⚙️ {t('parameters_title', lang)}")
    growth_rate = st.slider(
        t("expected_growth_rate", lang),
        min_value=-10.0,
        max_value=30.0,
        value=5.0,
        step=0.5
    ) / 100.0

if selected_analysis:
    metadata = selected_analysis.get("metadata", {})
    forecasting_for = t("forecasting_for", lang) if lang == "EN" else "Prognozowanie dla"
    st.info(f"📊 {forecasting_for}: **{metadata.get('filename', 'Unknown')}**")

    # Extract metrics
    metrics_dict = {}
    if "metrics_base" in selected_analysis:
        for metric in selected_analysis["metrics_base"]:
            if metric.get("value") is not None:
                metrics_dict[metric["key"]] = metric["value"]

    if not metrics_dict:
        st.warning(t("no_metrics_available", lang))
    else:
        # Generate forecasts
        forecasts = simple_linear_forecast(metrics_dict, growth_rate)

        if forecasts:
            # Summary metrics
            st.markdown(f"### 📊 {t('forecast_summary_title', lang)}")
            summary = get_forecast_summary(forecasts)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(t("forecasts_generated", lang), summary.total_forecasts)
            with col2:
                st.metric(t("avg_growth_rate_metric", lang), f"{summary.avg_growth_rate:.1f}%")
            with col3:
                st.metric(t("high_confidence_metric", lang), summary.high_confidence)
            with col4:
                st.metric(t("medium_confidence_metric", lang), summary.medium_confidence)

            st.markdown("---")

            # Forecast visualizations
            st.markdown(f"### 📈 {t('forecast_charts_title', lang)}")

            # Translate time periods
            current_label = t("current_label", lang)
            year1_label = t("year1_label", lang)
            year2_label = t("year2_label", lang)
            year3_label = t("year3_label", lang)

            for forecast in forecasts:
                st.markdown(f"#### {forecast.metric_name}")

                # Create forecast chart
                years = [current_label, year1_label, year2_label, year3_label]
                values = [
                    forecast.current_value,
                    forecast.forecast_1y,
                    forecast.forecast_2y,
                    forecast.forecast_3y
                ]

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=years,
                    y=values,
                    mode='lines+markers',
                    name=forecast.metric_name,
                    line=dict(color='#4472C4', width=3),
                    marker=dict(size=10)
                ))

                forecast_label = t("forecast_label", lang)
                time_period_label = t("time_period_label", lang)
                value_label = t("value_label", lang)

                fig.update_layout(
                    title=f"{forecast.metric_name} {forecast_label}",
                    xaxis_title=time_period_label,
                    yaxis_title=value_label,
                    height=400,
                    showlegend=True,
                    template="plotly_white"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Forecast details
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(current_label, f"{forecast.current_value:,.0f}" if forecast.current_value else "N/A")
                with col2:
                    st.metric(year1_label, f"{forecast.forecast_1y:,.0f}" if forecast.forecast_1y else "N/A")
                with col3:
                    st.metric(year2_label, f"{forecast.forecast_2y:,.0f}" if forecast.forecast_2y else "N/A")
                with col4:
                    st.metric(year3_label, f"{forecast.forecast_3y:,.0f}" if forecast.forecast_3y else "N/A")

                method_label = t("method_label", lang)
                confidence_label = t("confidence_label", lang)
                growth_rate_label = t("growth_rate_label", lang)
                st.caption(f"**{method_label}:** {forecast.method} | **{confidence_label}:** {forecast.confidence.upper()} | **{growth_rate_label}:** {forecast.growth_rate:.2f}%")
                st.divider()

            # Scenario Analysis
            st.markdown("---")
            st.markdown(f"### 🎯 {t('scenario_analysis_title', lang)}")

            scenarios = scenario_analysis(metrics_dict)

            # Select metric for scenario comparison
            metric_names = [f.metric_name for f in forecasts]
            selected_metric_name = st.selectbox(t("select_metric_scenario", lang), metric_names)

            # Find the selected metric in each scenario
            selected_metric_idx = metric_names.index(selected_metric_name)

            best_case = scenarios["best_case"][selected_metric_idx]
            base_case = scenarios["base_case"][selected_metric_idx]
            worst_case = scenarios["worst_case"][selected_metric_idx]

            # Create scenario comparison chart
            years = [current_label, year1_label, year2_label, year3_label]

            fig = go.Figure()

            # Translate scenario names
            best_case_label = t("best_case_label", lang)
            base_case_label = t("base_case_label", lang)
            worst_case_label = t("worst_case_label", lang)

            # Best case
            fig.add_trace(go.Scatter(
                x=years,
                y=[best_case.current_value, best_case.forecast_1y, best_case.forecast_2y, best_case.forecast_3y],
                mode='lines+markers',
                name=f'{best_case_label} (+15%)',
                line=dict(color='#70AD47', width=2),
                marker=dict(size=8)
            ))

            # Base case
            fig.add_trace(go.Scatter(
                x=years,
                y=[base_case.current_value, base_case.forecast_1y, base_case.forecast_2y, base_case.forecast_3y],
                mode='lines+markers',
                name=f'{base_case_label} (+5%)',
                line=dict(color='#4472C4', width=3),
                marker=dict(size=10)
            ))

            # Worst case
            fig.add_trace(go.Scatter(
                x=years,
                y=[worst_case.current_value, worst_case.forecast_1y, worst_case.forecast_2y, worst_case.forecast_3y],
                mode='lines+markers',
                name=f'{worst_case_label} (-2%)',
                line=dict(color='#E74C3C', width=2),
                marker=dict(size=8)
            ))

            fig.update_layout(
                title=f"{t('scenario_analysis_title', lang)}: {selected_metric_name}",
                xaxis_title=time_period_label,
                yaxis_title=value_label,
                height=500,
                showlegend=True,
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Scenario comparison table
            scenario_col = t("scenario_col", lang)
            growth_rate_col = t("growth_rate_col", lang)

            scenario_df = pd.DataFrame({
                scenario_col: [best_case_label, base_case_label, worst_case_label],
                growth_rate_col: ["+15%", "+5%", "-2%"],
                year1_label: [
                    f"{best_case.forecast_1y:,.0f}" if best_case.forecast_1y else "N/A",
                    f"{base_case.forecast_1y:,.0f}" if base_case.forecast_1y else "N/A",
                    f"{worst_case.forecast_1y:,.0f}" if worst_case.forecast_1y else "N/A"
                ],
                year2_label: [
                    f"{best_case.forecast_2y:,.0f}" if best_case.forecast_2y else "N/A",
                    f"{base_case.forecast_2y:,.0f}" if base_case.forecast_2y else "N/A",
                    f"{worst_case.forecast_2y:,.0f}" if worst_case.forecast_2y else "N/A"
                ],
                year3_label: [
                    f"{best_case.forecast_3y:,.0f}" if best_case.forecast_3y else "N/A",
                    f"{base_case.forecast_3y:,.0f}" if base_case.forecast_3y else "N/A",
                    f"{worst_case.forecast_3y:,.0f}" if worst_case.forecast_3y else "N/A"
                ],
            })

            st.dataframe(scenario_df, use_container_width=True)

            # Export forecasts
            st.markdown("---")
            st.markdown(f"### 📥 {t('export_forecasts_title', lang)}")

            # Create export dataframe
            export_data = []
            metric_export_col = t("metric_col", lang)
            current_value_col = t("current_value_col", lang)
            year1_forecast_col = t("year1_forecast_col", lang)
            year2_forecast_col = t("year2_forecast_col", lang)
            year3_forecast_col = t("year3_forecast_col", lang)

            for forecast in forecasts:
                export_data.append({
                    metric_export_col: forecast.metric_name,
                    current_value_col: forecast.current_value,
                    year1_forecast_col: forecast.forecast_1y,
                    year2_forecast_col: forecast.forecast_2y,
                    year3_forecast_col: forecast.forecast_3y,
                    growth_rate_col: forecast.growth_rate,
                    method_label: forecast.method,
                    confidence_label: forecast.confidence
                })

            export_df = pd.DataFrame(export_data)
            csv = export_df.to_csv(index=False)

            st.download_button(
                label=f"📥 {t('download_forecasts_csv', lang)}",
                data=csv,
                file_name=f"forecasts_{metadata.get('filename', 'analysis')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        else:
            st.warning(t("unable_generate_forecasts", lang))

else:
    st.info(f"👈 {t('load_analysis_instruction_forecast', lang)}")

    if lang == "EN":
        st.markdown("""
        ### How to use Forecasting:

        1. **Load Analysis**: Select an analysis file from the sidebar
        2. **Set Parameters**: Adjust the expected growth rate
        3. **View Forecasts**: Review projected values for key metrics
        4. **Scenario Analysis**: Compare best case, base case, and worst case scenarios
        5. **Export**: Download forecasts as CSV for further analysis

        ### Forecasting Methods:

        - **Linear Growth**: Simple projection based on growth rate assumptions
        - **Conservative Model**: More cautious forecasts for net income
        - **Asset Accumulation**: Models asset growth based on reinvestment
        - **Scenario Analysis**: Best case (+15%), base case (+5%), worst case (-2%)

        ### Important Notes:

        - Forecasts are based on simple assumptions and historical data
        - Real forecasting requires multi-period historical data
        - Consider external factors (market conditions, competition, regulations)
        - Use forecasts as guidance, not guarantees
        - Low confidence indicates limited historical data or high uncertainty
        """)
    else:
        st.markdown("""
        ### Jak korzystać z Prognozowania:

        1. **Wczytaj Analizę**: Wybierz plik analizy z panelu bocznego
        2. **Ustaw Parametry**: Dostosuj oczekiwaną stopę wzrostu
        3. **Przeglądaj Prognozy**: Sprawdź prognozowane wartości kluczowych wskaźników
        4. **Analiza Scenariuszy**: Porównaj najlepszy, bazowy i najgorszy scenariusz
        5. **Eksportuj**: Pobierz prognozy jako CSV do dalszej analizy

        ### Metody Prognozowania:

        - **Wzrost Liniowy**: Prosta projekcja oparta na założeniach dotyczących tempa wzrostu
        - **Model Konserwatywny**: Bardziej ostrożne prognozy dla dochodu netto
        - **Akumulacja Aktywów**: Modeluje wzrost aktywów na podstawie reinwestycji
        - **Analiza Scenariuszy**: Najlepszy (+15%), bazowy (+5%), najgorszy (-2%)

        ### Ważne Uwagi:

        - Prognozy opierają się na prostych założeniach i danych historycznych
        - Rzeczywiste prognozowanie wymaga wielookresowych danych historycznych
        - Uwzględnij czynniki zewnętrzne (warunki rynkowe, konkurencja, regulacje)
        - Używaj prognoz jako wskazówek, a nie gwarancji
        - Niska pewność wskazuje na ograniczone dane historyczne lub wysoką niepewność
        """)

st.markdown("---")
disclaimer = t("forecast_disclaimer", lang) if lang == "EN" else "⚠️ Zastrzeżenie: Prognozy są oszacowaniami i nie powinny być jedyną podstawą decyzji finansowych"
st.caption(disclaimer)


# Footer
render_nvidia_badge()
