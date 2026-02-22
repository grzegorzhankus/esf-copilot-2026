"""
Shared analysis file selector component for Streamlit pages.

This module provides a reusable sidebar component for loading analysis files
from the outputs/ directory into session state.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple

import streamlit as st

from core.i18n import t


def render_analysis_file_selector(lang: str = "EN") -> Optional[dict]:
    """
    Render a file selector in the sidebar for loading analysis files.

    Args:
        lang: Language code ("EN" or "PL")

    Returns:
        The loaded analysis data dict if a file is selected and loaded, None otherwise
    """
    with st.sidebar:
        st.markdown(f"### 📁 {t('load_analysis_title', lang)}")

        outputs_dir = Path("outputs")

        if not outputs_dir.exists():
            st.info(t("no_outputs_dir", lang))
            return None

        analysis_files = sorted(
            [f for f in outputs_dir.glob("analysis_*.json")],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if not analysis_files:
            st.info(t("no_analysis_files", lang))
            return None

        file_options = [f.name for f in analysis_files]

        # Check if there's already a loaded file in session state
        current_file = st.session_state.get("loaded_analysis_file")
        default_index = 0
        if current_file and current_file in file_options:
            default_index = file_options.index(current_file)

        selected_file = st.selectbox(
            t("select_analysis_file", lang),
            file_options,
            index=default_index,
            key="analysis_file_selector"
        )

        if st.button(t("load_analysis_button", lang), use_container_width=True, type="primary"):
            try:
                selected_path = outputs_dir / selected_file
                with open(selected_path, "r", encoding="utf-8") as f:
                    analysis_data = json.load(f)

                # Store in session state
                st.session_state.loaded_analysis_data = analysis_data
                st.session_state.loaded_analysis_file = selected_file

                st.success(f"{t('loaded_label', lang)}: {selected_file}")
                st.rerun()

            except Exception as e:
                st.error(f"{t('error_loading_file', lang)}: {e}")
                return None

        st.markdown("---")

    # Return the loaded data if available
    return st.session_state.get("loaded_analysis_data")


def convert_v2026_to_v20_format(analysis_data: dict) -> Tuple[dict, dict]:
    """
    Convert v2026 analysis format to v2.0.0 format for backward compatibility.

    The v2.0.0 pages expect data in session_state.parsed_data and
    session_state.analysis_result with a specific structure.

    Args:
        analysis_data: Analysis data from JSON file (v2026 format)

    Returns:
        Tuple of (parsed_data, analysis_result) dicts
    """
    # Extract metadata
    metadata = analysis_data.get("metadata", {})

    # Build parsed_data dict (simplified financial data)
    parsed_data = {
        "company_name": metadata.get("company_name", "Unknown"),
        "period_start": metadata.get("period_from", "N/A"),
        "period_end": metadata.get("period_to", "N/A"),
        "_raw": {},
    }

    # Extract metrics_base for quick access
    metrics_dict = {}
    if "metrics_base" in analysis_data:
        for metric in analysis_data["metrics_base"]:
            key = metric.get("key", "")
            value = metric.get("value")
            if value is not None:
                metrics_dict[key] = value

    # Map common metrics to parsed_data
    parsed_data["assets_current"] = metrics_dict.get("bs_total_assets")
    parsed_data["assets_prior"] = metrics_dict.get("bs_total_assets_prior")
    parsed_data["equity_current"] = metrics_dict.get("bs_equity")
    parsed_data["equity_prior"] = metrics_dict.get("bs_equity_prior")
    parsed_data["liabilities_current"] = metrics_dict.get("bs_total_liabilities")
    parsed_data["liabilities_prior"] = metrics_dict.get("bs_total_liabilities_prior")
    parsed_data["revenue_current"] = metrics_dict.get("pl_revenue")
    parsed_data["revenue_prior"] = metrics_dict.get("pl_revenue_prior")
    parsed_data["gross_profit_current"] = metrics_dict.get("pl_gross_profit")
    parsed_data["ebit_current"] = metrics_dict.get("pl_ebit")
    parsed_data["net_profit_current"] = metrics_dict.get("pl_net_income")

    # Build P&L data structure
    pl_data = {}
    # This would require more detailed mapping - leaving minimal for now
    parsed_data["pl"] = pl_data
    parsed_data["pl_variant"] = "kalkulacyjny"  # Default

    # Build analysis_result dict (KPIs and red flags)
    analysis_result = {
        "metadata": metadata,
        "coverage": analysis_data.get("coverage", {}),
        "kpi": [],
        "red_flags": []
    }

    # Convert KPIs
    if "kpis" in analysis_data:
        for kpi in analysis_data["kpis"]:
            analysis_result["kpi"].append({
                "key": kpi.get("key", ""),
                "value": kpi.get("value"),
                "status": "OK" if kpi.get("value") is not None else "MISSING"
            })

    # Convert red flags
    if "red_flags" in analysis_data:
        for flag in analysis_data["red_flags"]:
            if flag.get("detected"):
                analysis_result["red_flags"].append({
                    "rule_id": flag.get("key", ""),
                    "severity": flag.get("severity", "MEDIUM").upper(),
                    "because": flag.get("description", ""),
                    "evidence": {"details": flag.get("details", "")}
                })

    return parsed_data, analysis_result
