from __future__ import annotations

import json
import os
import time
from pathlib import Path
import sys
import zipfile
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import streamlit as st
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.analysis_pipeline import analyze_xml_bytes
from core.excel_export import export_to_excel
from core.i18n import t
from core.language_selector import render_language_selector
from core.modes import apply_mode
from core.xml_loader import XmlParseError
from core.gpu_batch_processor import (
    GPUBatchProcessor,
    get_gpu_info,
    aggregate_batch_results,
    GPU_AVAILABLE
)
from core.components import render_nvidia_badge

OUTPUTS_DIR = Path("outputs")

st.set_page_config(page_title="Batch Processing - AI CFO Dashboard", layout="wide", page_icon="📦")

# Render language selector and get current language
lang = render_language_selector()
apply_mode("ORCHESTRATE", lang)

st.title(f"📦 {t('batch_processing_title', lang)}")
st.write(t("batch_upload_instruction", lang))

# Sidebar - Hardware Status
with st.sidebar:
    st.markdown("### 🖥️ Hardware Status")

    gpu_info = get_gpu_info()

    if gpu_info["gpu_available"]:
        st.success("✅ GPU Acceleration Available")
        if "device_name" in gpu_info:
            st.caption(f"🎮 {gpu_info['device_name']}")
        if "memory_total_gb" in gpu_info:
            st.caption(f"💾 Memory: {gpu_info['memory_free_gb']:.1f} / {gpu_info['memory_total_gb']:.1f} GB")
    else:
        st.info("💻 CPU Mode (Multi-threaded)")
        st.caption("RAPIDS not installed - using parallel CPU processing")

    st.markdown("---")

    # Processing settings
    st.markdown("### ⚙️ Processing Settings")

    # Get CPU count
    cpu_count = os.cpu_count() or 4

    max_workers = st.slider(
        "Parallel Workers",
        min_value=1,
        max_value=cpu_count * 2,
        value=min(8, cpu_count),
        help="Number of parallel threads for processing"
    )

    batch_size = st.selectbox(
        "Batch Size",
        options=[10, 25, 50, 100, 250, 500],
        index=2,  # Default to 50
        help="Files to process per batch"
    )

# File uploader for multiple files
uploaded_files = st.file_uploader(
    t("upload_xml_files", lang),
    type=["xml"],
    accept_multiple_files=True
)

if uploaded_files:
    files_selected = t("files_selected", lang)
    st.info(f"📁 {len(uploaded_files)} {files_selected}")

    # Display files
    with st.expander(f"📋 {t('selected_files', lang)}", expanded=False):
        file_df = pd.DataFrame({
            t("filename_col", lang): [f.name for f in uploaded_files],
            t("size_kb_col", lang): [f.size / 1024 for f in uploaded_files]
        })
        st.dataframe(file_df, use_container_width=True)

    # Processing options
    st.markdown(f"### ⚙️ {t('processing_options_title', lang)}")
    col1, col2 = st.columns(2)

    with col1:
        save_json = st.checkbox(t("save_json_outputs", lang), value=True)
        create_excel = st.checkbox(t("create_excel_reports", lang), value=True)

    with col2:
        create_summary = st.checkbox(t("create_summary_report", lang), value=True)
        create_batch_export = st.checkbox(t("create_batch_export", lang), value=True)

    # Analyze button
    if st.button(f"🚀 {t('analyze_all_files', lang)}", type="primary", use_container_width=True):

        # Performance tracking
        start_time = time.time()

        # Progress elements
        progress_container = st.container()
        with progress_container:
            col1, col2, col3, col4 = st.columns(4)
            progress_metric = col1.empty()
            speed_metric = col2.empty()
            eta_metric = col3.empty()
            status_metric = col4.empty()

            progress_bar = st.progress(0)
            status_text = st.empty()

        results = []
        errors = []

        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        # Process files in parallel using ThreadPoolExecutor
        total_files = len(uploaded_files)
        processed_count = 0

        def process_single_file(uploaded_file):
            """Process a single uploaded file."""
            try:
                xml_bytes = uploaded_file.read()
                uploaded_file.seek(0)  # Reset for potential re-read
                result = analyze_xml_bytes(xml_bytes, uploaded_file.name)
                return {"success": True, "result": result, "filename": uploaded_file.name}
            except XmlParseError as exc:
                return {"success": False, "error": f"{t('error_xml', lang)}: {exc}", "filename": uploaded_file.name}
            except Exception as exc:
                return {"success": False, "error": f"{t('error_unexpected', lang)}: {exc}", "filename": uploaded_file.name}

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(process_single_file, f): f
                for f in uploaded_files
            }

            # Process results as they complete
            for future in as_completed(future_to_file):
                processed_count += 1
                elapsed = time.time() - start_time

                try:
                    result = future.result()

                    if result["success"]:
                        analysis_result = result["result"]
                        results.append(analysis_result)

                        # Save JSON if requested
                        if save_json:
                            timestamp = analysis_result.metadata.analyzed_at_utc.replace(":", "").replace("Z", "")
                            output_path = OUTPUTS_DIR / f"analysis_{timestamp}.json"
                            with output_path.open("w", encoding="utf-8") as f:
                                json.dump(analysis_result.to_dict(), f, indent=2, ensure_ascii=False)
                    else:
                        errors.append({"file": result["filename"], "error": result["error"]})

                except Exception as exc:
                    errors.append({"file": "unknown", "error": str(exc)})

                # Update progress metrics
                progress = processed_count / total_files
                speed = processed_count / elapsed if elapsed > 0 else 0
                remaining = total_files - processed_count
                eta = remaining / speed if speed > 0 else 0

                progress_bar.progress(progress)
                progress_metric.metric("Processed", f"{processed_count}/{total_files}")
                speed_metric.metric("Speed", f"{speed:.1f} files/s")
                eta_metric.metric("ETA", f"{eta:.0f}s" if eta > 0 else "Done")
                status_metric.metric("Success Rate", f"{len(results)}/{processed_count}")

                processing_label = t("processing_label", lang)
                status_text.text(f"{processing_label} {processed_count}/{total_files}")

        # Clear progress elements
        status_text.empty()
        progress_bar.empty()

        # Calculate final metrics
        total_time = time.time() - start_time
        final_speed = len(results) / total_time if total_time > 0 else 0

        # Display results
        st.success(f"✅ {t('batch_completed', lang)}! {t('processed_label', lang)} {len(results)}/{len(uploaded_files)} {t('files_successfully', lang)}")

        # Performance metrics
        st.markdown("### 📊 Performance Metrics")
        perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)

        with perf_col1:
            st.metric("Total Time", f"{total_time:.1f}s")
        with perf_col2:
            st.metric("Files/Second", f"{final_speed:.2f}")
        with perf_col3:
            accel_mode = "GPU" if GPU_AVAILABLE else "CPU (Parallel)"
            st.metric("Mode", accel_mode)
        with perf_col4:
            st.metric("Workers", max_workers)

        if errors:
            st.error(f"⚠️ {len(errors)} {t('files_had_errors', lang)}")
            with st.expander(f"❌ {t('view_errors', lang)}"):
                for error in errors:
                    st.write(f"**{error['file']}**: {error['error']}")

        # Aggregate Statistics (using GPU if available)
        if results:
            st.markdown("---")
            st.markdown("### 📈 Aggregate Statistics")

            # Convert results to dict format for aggregation
            results_dict = [r.to_dict() for r in results]
            agg_stats = aggregate_batch_results(results_dict)

            if agg_stats and "metric_statistics" in agg_stats:
                # Display key metric statistics
                metric_stats = agg_stats["metric_statistics"]

                # Filter to important metrics
                important_metrics = [
                    "total_assets", "total_equity", "net_income",
                    "revenue", "operating_profit", "kpi_roe", "kpi_roa", "kpi_current_ratio"
                ]

                available_metrics = [m for m in important_metrics if m in metric_stats]

                if available_metrics:
                    stats_data = []
                    for metric in available_metrics[:8]:  # Limit to 8 metrics
                        stats = metric_stats[metric]
                        stats_data.append({
                            "Metric": metric.replace("kpi_", "").replace("_", " ").title(),
                            "Mean": f"{stats['mean']:,.2f}",
                            "Min": f"{stats['min']:,.2f}",
                            "Max": f"{stats['max']:,.2f}",
                            "Median": f"{stats['median']:,.2f}"
                        })

                    st.dataframe(pd.DataFrame(stats_data), use_container_width=True)

            # Red flag summary
            if "red_flag_summary" in agg_stats and agg_stats["red_flag_summary"]:
                st.markdown("#### 🚩 Red Flag Distribution")
                rf_df = pd.DataFrame([
                    {"Red Flag": k.replace("_", " ").title(), "Count": v}
                    for k, v in agg_stats["red_flag_summary"].items()
                ]).sort_values("Count", ascending=False)
                st.dataframe(rf_df, use_container_width=True)

        # Summary Report
        if create_summary and results:
            st.markdown("---")
            st.markdown(f"### 📊 {t('summary_report_title', lang)}")

            # Create summary dataframe
            summary_data = []
            for result in results:
                summary_data.append({
                    t("filename_col", lang): result.metadata.filename,
                    t("schema_col", lang): result.metadata.schema_id_slug,
                    t("coverage_col", lang): result.coverage.percent,
                    t("kpis_calculated_col", lang): len(result.kpis),
                    t("red_flags_col", lang): len([f for f in result.red_flags if f.detected]),
                })

            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)

            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(t("total_files_metric", lang), len(results))
            with col2:
                avg_coverage = summary_df[t("coverage_col", lang)].mean()
                st.metric(t("avg_coverage_metric", lang), f"{avg_coverage:.1f}%")
            with col3:
                total_red_flags = summary_df[t("red_flags_col", lang)].sum()
                st.metric(t("total_red_flags_metric", lang), int(total_red_flags))
            with col4:
                files_with_flags = len(summary_df[summary_df[t("red_flags_col", lang)] > 0])
                st.metric(t("files_with_flags_metric", lang), files_with_flags)

            # Export summary as CSV
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label=f"📥 {t('download_summary_csv', lang)}",
                data=csv,
                file_name="batch_summary.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Batch Export (ZIP)
        if create_batch_export and results:
            st.markdown("---")
            st.markdown(f"### 📦 {t('batch_export_title', lang)}")

            with st.spinner(f"{t('creating_batch_export', lang)}..."):
                zip_buffer = BytesIO()

                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for result in results:
                        timestamp = result.metadata.analyzed_at_utc.replace(":", "").replace("Z", "")
                        base_name = result.metadata.filename.replace(".xml", "")

                        # Add JSON
                        if save_json:
                            json_data = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
                            zip_file.writestr(f"{base_name}_{timestamp}.json", json_data)

                        # Add Excel
                        if create_excel:
                            excel_data = export_to_excel(result)
                            zip_file.writestr(f"{base_name}_{timestamp}.xlsx", excel_data)

                    # Add summary CSV
                    if create_summary:
                        zip_file.writestr("batch_summary.csv", csv)

                    # Add aggregate statistics
                    if results:
                        results_dict = [r.to_dict() for r in results]
                        agg_stats = aggregate_batch_results(results_dict)
                        zip_file.writestr(
                            "aggregate_statistics.json",
                            json.dumps(agg_stats, indent=2, ensure_ascii=False)
                        )

                zip_buffer.seek(0)

            st.download_button(
                label=f"📦 {t('download_batch_zip', lang)}",
                data=zip_buffer.getvalue(),
                file_name="batch_export.zip",
                mime="application/zip",
                use_container_width=True
            )

        # Individual Results
        if results:
            st.markdown("---")
            st.markdown(f"### 📄 {t('individual_results_title', lang)}")

            for result in results:
                with st.expander(f"📊 {result.metadata.filename}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(t("coverage_label", lang), f"{result.coverage.percent}%")
                    with col2:
                        st.metric(t("kpis_label", lang), len(result.kpis))
                    with col3:
                        red_flag_count = len([f for f in result.red_flags if f.detected])
                        st.metric(t("red_flags_label", lang), red_flag_count)

                    # Quick view of metrics
                    if result.metrics_base:
                        st.markdown(f"**{t('base_metrics_title', lang)}:**")
                        metrics_data = []
                        for m in result.metrics_base:
                            if m.value is not None:
                                metrics_data.append({
                                    t("metric_col", lang): m.key,
                                    t("value_col", lang): f"{m.value:,.2f}",
                                    t("unit_col", lang): m.unit
                                })
                        if metrics_data:
                            st.dataframe(pd.DataFrame(metrics_data), use_container_width=True)

                    # Red flags if any
                    if result.red_flags:
                        detected = [f for f in result.red_flags if f.detected]
                        if detected:
                            st.markdown(f"**{t('red_flags_label', lang)}:**")
                            for flag in detected:
                                severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                                st.write(f"{severity_color.get(flag.severity, '⚠️')} **{flag.title}** ({flag.severity}): {flag.details}")

else:
    st.info(f"👆 {t('upload_instruction_batch', lang)}")

    # Show hardware acceleration info
    st.markdown("### 🚀 Parallel Processing")

    gpu_info = get_gpu_info()
    if gpu_info["gpu_available"]:
        st.success("✅ **GPU Acceleration Active** - RAPIDS cuDF enabled for high-speed processing")
    else:
        st.info("💻 **CPU Parallel Mode** - Using multi-threaded processing for optimal performance")

    cpu_count = os.cpu_count() or 4
    st.caption(f"Available CPU cores: {cpu_count}")

    if lang == "EN":
        st.markdown("""
        ### How to use Batch Processing:

        1. **Upload Files**: Select multiple XML files using the file uploader above
        2. **Configure Options**: Choose which outputs to generate (JSON, Excel, Summary, ZIP)
        3. **Adjust Workers**: Use sidebar to set parallel processing workers
        4. **Analyze**: Click "Analyze All Files" to process all uploaded files
        5. **Review Results**: Check performance metrics, aggregate stats, and individual results
        6. **Download**: Export results individually or as a batch ZIP file

        ### Performance Features:

        - **Parallel Processing**: Analyze multiple files simultaneously
        - **Real-time Metrics**: Track speed, ETA, and success rate
        - **Aggregate Statistics**: Cross-company analysis of all metrics
        - **Red Flag Distribution**: See common issues across all files
        - **GPU Acceleration**: RAPIDS support for 100x faster aggregation (when available)
        """)
    else:
        st.markdown("""
        ### Jak korzystać z Przetwarzania Wsadowego:

        1. **Prześlij Pliki**: Wybierz wiele plików XML używając przycisku przesyłania powyżej
        2. **Skonfiguruj Opcje**: Wybierz, które wyniki wygenerować (JSON, Excel, Podsumowanie, ZIP)
        3. **Dostosuj Workers**: Użyj panelu bocznego, aby ustawić liczbę równoległych wątków
        4. **Analizuj**: Kliknij "Analizuj Wszystkie Pliki", aby przetworzyć wszystkie przesłane pliki
        5. **Przejrzyj Wyniki**: Sprawdź metryki wydajności, statystyki zbiorcze i wyniki indywidualne
        6. **Pobierz**: Eksportuj wyniki indywidualnie lub jako plik ZIP

        ### Funkcje Wydajności:

        - **Przetwarzanie Równoległe**: Analizuj wiele plików jednocześnie
        - **Metryki w Czasie Rzeczywistym**: Śledź prędkość, ETA i współczynnik sukcesu
        - **Statystyki Zbiorcze**: Analiza międzyfirmowa wszystkich metryk
        - **Rozkład Red Flags**: Zobacz typowe problemy we wszystkich plikach
        - **Akceleracja GPU**: Obsługa RAPIDS dla 100x szybszej agregacji (gdy dostępna)
        """)

st.markdown("---")

# Footer with processing mode info
gpu_info = get_gpu_info()
if gpu_info["gpu_available"]:
    st.caption("🚀 GPU-accelerated batch processing with RAPIDS cuDF")
else:
    cpu_count = os.cpu_count() or 4
    st.caption(f"💻 CPU parallel processing with {cpu_count} available cores")


# NVIDIA Badge
render_nvidia_badge()
