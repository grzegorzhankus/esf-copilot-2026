"""Anomaly Detection Page for Financial Statements.

This page provides GPU-accelerated anomaly detection using autoencoders
and other ML methods to identify unusual financial patterns.
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
from core.components import render_nvidia_badge

# Try to import anomaly detector with graceful fallback
ANOMALY_DETECTION_AVAILABLE = False
MISSING_DEPENDENCIES = []

try:
    from core.anomaly_detector import (
        AnomalyDetector,
        create_anomaly_detector,
        load_data_for_detection,
        get_gpu_status
    )
    ANOMALY_DETECTION_AVAILABLE = True
except ImportError as e:
    if "sklearn" in str(e).lower():
        MISSING_DEPENDENCIES.append("scikit-learn")
    if "torch" in str(e).lower():
        MISSING_DEPENDENCIES.append("PyTorch")
    if "numpy" in str(e).lower():
        MISSING_DEPENDENCIES.append("NumPy")

    # Provide dummy functions for graceful degradation
    def get_gpu_status():
        return {"pytorch_installed": False, "cuda_available": False, "cuml_available": False}

    def load_data_for_detection(directory):
        return pd.DataFrame()

    def create_anomaly_detector(**kwargs):
        return None


OUTPUTS_DIR = Path("outputs")

st.set_page_config(
    page_title="Anomaly Detection - AI CFO Dashboard",
    layout="wide",
    page_icon="🔴"
)

# Render language selector and get current language
lang = render_language_selector()
render_mode_header("DETECT", lang)

# Page title
if lang == "PL":
    st.title("🔴 Wykrywanie Anomalii")
    st.write("Wykrywaj nietypowe wzorce finansowe używając uczenia maszynowego i autokoderów.")
else:
    st.title("🔴 Anomaly Detection")
    st.write("Detect unusual financial patterns using machine learning and autoencoders.")

st.markdown("---")

# Check if dependencies are available
if not ANOMALY_DETECTION_AVAILABLE:
    st.warning("⚠️ Anomaly Detection requires additional dependencies")

    if MISSING_DEPENDENCIES:
        st.error(f"Missing dependencies: {', '.join(MISSING_DEPENDENCIES)}")

    if lang == "PL":
        st.markdown("""
        ### Wymagane Zależności

        Aby korzystać z wykrywania anomalii, zainstaluj następujące pakiety:

        ```bash
        pip install scikit-learn torch numpy pandas
        ```

        **Opcjonalnie dla akceleracji GPU:**
        ```bash
        pip install torch --index-url https://download.pytorch.org/whl/cu121
        ```

        Po instalacji uruchom ponownie aplikację.
        """)
    else:
        st.markdown("""
        ### Required Dependencies

        To use anomaly detection, install the following packages:

        ```bash
        pip install scikit-learn torch numpy pandas
        ```

        **Optional for GPU acceleration:**
        ```bash
        pip install torch --index-url https://download.pytorch.org/whl/cu121
        ```

        Restart the application after installation.
        """)

    st.info("👉 The application works without anomaly detection. Other features are fully available.")
    render_nvidia_badge()
    st.stop()

# Sidebar - Configuration
with st.sidebar:
    st.markdown("### 🖥️ Hardware Status")

    gpu_status = get_gpu_status()

    if gpu_status.get("cuda_available"):
        st.success("✅ GPU Acceleration Available")
        if "device_name" in gpu_status:
            st.caption(f"🎮 {gpu_status['device_name']}")
        if "device_memory_gb" in gpu_status:
            st.caption(f"💾 {gpu_status['device_memory_gb']:.1f} GB VRAM")
    elif gpu_status.get("pytorch_installed"):
        st.info("💻 CPU Mode (PyTorch)")
        st.caption("CUDA not available")
    else:
        st.warning("⚠️ PyTorch not installed")
        st.caption("Using statistical methods only")

    st.markdown("---")

    # Detection settings
    st.markdown("### ⚙️ Detection Settings")

    # Filter methods based on available libraries
    available_methods = ["statistical"]  # Always available
    if gpu_status.get("pytorch_installed"):
        available_methods = ["ensemble", "autoencoder", "isolation_forest", "statistical"]
    else:
        # Check if sklearn is available
        try:
            import sklearn
            available_methods = ["isolation_forest", "statistical"]
        except ImportError:
            pass

    method = st.selectbox(
        "Detection Method",
        options=available_methods,
        index=0,
        help="Algorithm to use for anomaly detection"
    )

    threshold = st.slider(
        "Anomaly Threshold (percentile)",
        min_value=0.80,
        max_value=0.99,
        value=0.95,
        step=0.01,
        help="Higher = fewer anomalies detected"
    )

    st.markdown("---")

    # Method descriptions
    with st.expander("ℹ️ Method Descriptions"):
        st.markdown("""
        **Ensemble** (Recommended)
        - Combines all methods
        - Most robust detection

        **Autoencoder**
        - Neural network approach
        - Best for complex patterns

        **Isolation Forest**
        - Tree-based outlier detection
        - Fast and interpretable

        **Statistical**
        - Z-score based
        - Simple but effective
        """)

# Main content
st.markdown("### 📊 Data Analysis")

# Load data
if st.button("📂 Load & Analyze Data", type="primary", use_container_width=True):
    with st.spinner("Loading data..." if lang == "EN" else "Ładowanie danych..."):
        data = load_data_for_detection(OUTPUTS_DIR)

    if data.empty:
        st.error("No analysis files found in outputs/ directory." if lang == "EN" else "Nie znaleziono plików analizy w katalogu outputs/.")
    else:
        st.success(f"Loaded {len(data)} analysis files" if lang == "EN" else f"Wczytano {len(data)} plików analizy")

        # Show data preview
        with st.expander("📋 Data Preview"):
            st.dataframe(data.head(10), use_container_width=True)

        # Create detector and run analysis
        st.markdown("---")
        st.markdown("### 🔍 Running Anomaly Detection")

        with st.spinner("Detecting anomalies..." if lang == "EN" else "Wykrywanie anomalii..."):
            try:
                detector = create_anomaly_detector(method=method, use_gpu=True)
                detector.threshold = threshold
                report = detector.detect(data)

                # Store in session state for later use
                st.session_state.anomaly_report = report
                st.session_state.anomaly_data = data

            except Exception as e:
                st.error(f"Error during detection: {e}")
                st.info("Try using a simpler detection method (e.g., 'statistical') or check your data.")
                st.stop()

        # Display results
        st.markdown("---")
        st.markdown("### 📈 Detection Results")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Companies" if lang == "EN" else "Liczba Firm",
                report.total_companies
            )
        with col2:
            st.metric(
                "Anomalies Detected" if lang == "EN" else "Wykryte Anomalie",
                report.anomalies_detected,
                delta=f"{report.anomaly_rate*100:.1f}%"
            )
        with col3:
            st.metric(
                "Method" if lang == "EN" else "Metoda",
                report.method_used.replace("_", " ").title()
            )
        with col4:
            st.metric(
                "Processing Time" if lang == "EN" else "Czas",
                f"{report.execution_time_ms:.0f}ms"
            )

        # GPU status indicator
        if report.gpu_accelerated:
            st.caption("🚀 GPU-accelerated processing")
        else:
            st.caption("💻 CPU processing")

        # Anomalies table
        st.markdown("---")
        st.markdown("### 🚨 Detected Anomalies" if lang == "EN" else "### 🚨 Wykryte Anomalie")

        anomaly_results = [r for r in report.results if r.is_anomaly]

        if anomaly_results:
            anomaly_df = pd.DataFrame([
                {
                    "Company" if lang == "EN" else "Firma": r.filename,
                    "Score" if lang == "EN" else "Wynik": f"{r.anomaly_score:.3f}",
                    "Type" if lang == "EN" else "Typ": r.anomaly_type,
                    "Factors" if lang == "EN" else "Czynniki": ", ".join(r.contributing_factors[:3]) if r.contributing_factors else "-"
                }
                for r in anomaly_results
            ])

            st.dataframe(
                anomaly_df,
                use_container_width=True,
                hide_index=True
            )

            # Detailed view for each anomaly
            st.markdown("#### 🔎 Anomaly Details")

            for result in anomaly_results:
                with st.expander(f"⚠️ {result.filename} (Score: {result.anomaly_score:.3f})"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**Type:** {result.anomaly_type}")
                        st.markdown("**Contributing Factors:**")
                        for factor in result.contributing_factors:
                            st.write(f"  • {factor}")

                    with col2:
                        if result.z_scores:
                            st.markdown("**Z-Scores (Top Deviations):**")
                            sorted_z = sorted(
                                result.z_scores.items(),
                                key=lambda x: abs(x[1]),
                                reverse=True
                            )[:5]
                            for metric, z in sorted_z:
                                color = "🔴" if abs(z) > 2 else "🟡" if abs(z) > 1 else "🟢"
                                st.write(f"  {color} {metric}: {z:.2f}")
        else:
            st.success("No anomalies detected!" if lang == "EN" else "Nie wykryto anomalii!")

        # Feature importance
        st.markdown("---")
        st.markdown("### 📊 Feature Importance" if lang == "EN" else "### 📊 Ważność Cech")

        if report.feature_importance:
            importance_df = pd.DataFrame([
                {
                    "Feature" if lang == "EN" else "Cecha": k.replace("kpi_", "").replace("_", " ").title(),
                    "Importance" if lang == "EN" else "Ważność": v
                }
                for k, v in sorted(
                    report.feature_importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            ])

            st.bar_chart(
                importance_df.set_index("Feature" if lang == "EN" else "Cecha"),
                use_container_width=True
            )

        # All companies scores
        st.markdown("---")
        st.markdown("### 📋 All Companies Scores" if lang == "EN" else "### 📋 Wyniki Wszystkich Firm")

        all_scores_df = pd.DataFrame([
            {
                "Company" if lang == "EN" else "Firma": r.filename,
                "Score" if lang == "EN" else "Wynik": r.anomaly_score,
                "Status": "⚠️ Anomaly" if r.is_anomaly else "✅ Normal"
            }
            for r in sorted(report.results, key=lambda x: x.anomaly_score, reverse=True)
        ])

        st.dataframe(
            all_scores_df,
            use_container_width=True,
            hide_index=True
        )

        # Export results
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            # Export as CSV
            export_df = pd.DataFrame([
                {
                    "filename": r.filename,
                    "anomaly_score": r.anomaly_score,
                    "is_anomaly": r.is_anomaly,
                    "anomaly_type": r.anomaly_type,
                    "contributing_factors": "; ".join(r.contributing_factors)
                }
                for r in report.results
            ])
            csv = export_df.to_csv(index=False)

            st.download_button(
                "📥 Download CSV" if lang == "EN" else "📥 Pobierz CSV",
                data=csv,
                file_name="anomaly_detection_results.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # Export as JSON
            export_json = {
                "summary": {
                    "total_companies": report.total_companies,
                    "anomalies_detected": report.anomalies_detected,
                    "anomaly_rate": report.anomaly_rate,
                    "method": report.method_used,
                    "gpu_accelerated": report.gpu_accelerated
                },
                "feature_importance": report.feature_importance,
                "results": [
                    {
                        "filename": r.filename,
                        "anomaly_score": r.anomaly_score,
                        "is_anomaly": r.is_anomaly,
                        "anomaly_type": r.anomaly_type,
                        "contributing_factors": r.contributing_factors,
                        "z_scores": r.z_scores
                    }
                    for r in report.results
                ]
            }

            st.download_button(
                "📥 Download JSON" if lang == "EN" else "📥 Pobierz JSON",
                data=json.dumps(export_json, indent=2),
                file_name="anomaly_detection_results.json",
                mime="application/json",
                use_container_width=True
            )

else:
    # Show instructions when no data is loaded
    if lang == "PL":
        st.info("👆 Kliknij 'Load & Analyze Data' aby rozpocząć wykrywanie anomalii.")

        st.markdown("""
        ### Jak działa Wykrywanie Anomalii:

        1. **Wczytaj Dane**: Kliknij przycisk powyżej, aby wczytać pliki analizy
        2. **Automatyczna Analiza**: System przeanalizuje wszystkie firmy
        3. **Wykrywanie Wzorców**: Algorytmy ML identyfikują nietypowe wzorce
        4. **Przejrzyj Wyniki**: Zobacz wykryte anomalie i ich przyczyny

        ### Metody Wykrywania:

        - **Ensemble**: Łączy wszystkie metody dla najlepszych wyników
        - **Autoencoder**: Sieć neuronowa ucząca się normalnych wzorców
        - **Isolation Forest**: Algorytm drzew dla wykrywania outlierów
        - **Statistical**: Metody statystyczne (Z-score)

        ### Co jest anomalią?

        - Nietypowo wysokie lub niskie wskaźniki finansowe
        - Nietypowe kombinacje metryk
        - Wzorce odbiegające od innych firm
        """)
    else:
        st.info("👆 Click 'Load & Analyze Data' to start anomaly detection.")

        st.markdown("""
        ### How Anomaly Detection Works:

        1. **Load Data**: Click the button above to load analysis files
        2. **Automatic Analysis**: System analyzes all companies
        3. **Pattern Detection**: ML algorithms identify unusual patterns
        4. **Review Results**: See detected anomalies and their causes

        ### Detection Methods:

        - **Ensemble**: Combines all methods for best results
        - **Autoencoder**: Neural network learning normal patterns
        - **Isolation Forest**: Tree-based outlier detection
        - **Statistical**: Statistical methods (Z-score)

        ### What counts as an anomaly?

        - Unusually high or low financial ratios
        - Unusual combinations of metrics
        - Patterns deviating from other companies
        """)

# Footer
render_nvidia_badge()
