"""5 AI Modes Map — framework overview page.

Renders all five framework modes as tiles, mapping each to its corresponding
e-SF Copilot section(s). Used in Akt 4 of Demo #2 as the visual punchline that
shows the app IS the framework.

Pure-visual page: reads MODES from core.modes, no business logic.
"""
from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.language_selector import render_language_selector
from core.modes import MODES, NAVY

st.set_page_config(
    page_title="5 AI Modes Map - AI CFO Dashboard",
    page_icon="📊",
    layout="wide",
)

lang = render_language_selector()
PL = lang.upper() == "PL"

# Title + intro
if PL:
    st.markdown("# 📊 5 AI Modes — Mapa Frameworka")
    st.markdown(
        "**Architektura aplikacji e-SF Analyzer w autorskiej taksonomii 5 AI Modes.** "
        "Każda sekcja aplikacji to konkretne pytanie biznesowe rozwiązywane przez konkretny tryb AI."
    )
else:
    st.markdown("# 📊 5 AI Modes — Framework Map")
    st.markdown(
        "**The e-SF Analyzer application architecture mapped onto my 5 AI Modes taxonomy.** "
        "Each section of the app answers a specific business question through a specific AI mode."
    )

st.markdown("---")


def _tile_html(mode_key: str, *, width_label: str) -> str:
    m = MODES[mode_key]
    name = m["name_pl"] if PL else m["name_en"]
    question = m["question_pl"] if PL else m["question_en"]
    framework_label = "Tryb" if PL else "Mode"
    sections_label = "Sekcje aplikacji:" if PL else "App sections:"
    sections = " · ".join(m["sections"])
    color = m["color"]
    return f"""
    <div style="
        background: white;
        border-top: 6px solid {color};
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        height: 100%;
        min-height: {width_label};
    ">
        <div style="color: {color}; font-size: 11px; font-weight: 700;
                    letter-spacing: 2px; text-transform: uppercase;">
            {framework_label} {m['id']}
        </div>
        <div style="color: {NAVY}; font-size: 22px; font-weight: 700; margin-top: 4px;">
            {name}
        </div>
        <div style="color: #1F2937; font-size: 12px; font-style: italic; margin-top: 8px;
                    line-height: 1.4;">
            "{question}"
        </div>
        <div style="margin-top: 16px;">
            <div style="color: #94A3B8; font-size: 10px; text-transform: uppercase;
                        letter-spacing: 1px;">
                {sections_label}
            </div>
            <div style="color: {color}; font-size: 13px; font-weight: 600; margin-top: 4px;">
                {sections}
            </div>
        </div>
    </div>
    """


# Top row: 4 tiles (DETECT, FORECAST, REVIEW, DRAFT)
cols = st.columns(4)
top_row = ["DETECT", "FORECAST", "REVIEW", "DRAFT"]
for col, key in zip(cols, top_row):
    with col:
        st.markdown(_tile_html(key, width_label="220px"), unsafe_allow_html=True)

st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

# Bottom: ORCHESTRATE full-width (it's the meta / coordinator mode)
m = MODES["ORCHESTRATE"]
name = m["name_pl"] if PL else m["name_en"]
question = m["question_pl"] if PL else m["question_en"]
framework_label = "Tryb" if PL else "Mode"
sections_label = "Sekcja aplikacji:" if PL else "App section:"
subtitle = "— Pies pasterski stada" if PL else "— Shepherd of the pack"
color = m["color"]
st.markdown(
    f"""
    <div style="
        background: white;
        border-top: 6px solid {color};
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    ">
        <div style="color: {color}; font-size: 11px; font-weight: 700;
                    letter-spacing: 2px; text-transform: uppercase;">
            {framework_label} {m['id']} · {'KOORDYNATOR' if PL else 'COORDINATOR'}
        </div>
        <div style="color: {NAVY}; font-size: 24px; font-weight: 700; margin-top: 4px;">
            {name}
            <span style="font-size: 14px; color: #94A3B8; font-weight: 400;">{subtitle}</span>
        </div>
        <div style="color: #1F2937; font-size: 13px; font-style: italic; margin-top: 8px;">
            "{question}"
        </div>
        <div style="margin-top: 12px; color: {color}; font-size: 14px; font-weight: 600;">
            {sections_label} {' · '.join(m['sections'])}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

# Footer note
if PL:
    st.caption(
        "Każdy z 5 trybów odpowiada na jedno konkretne pytanie biznesowe. "
        "Aplikacja e-SF Analyzer jest dowodem koncepcji, że framework działa "
        "na rzeczywistym kontekście polskich sprawozdań finansowych."
    )
else:
    st.caption(
        "Each of the 5 modes answers one specific business question. "
        "The e-SF Analyzer app is the proof-of-concept that the framework "
        "holds up against real-world Polish financial statement workflows."
    )
