"""5 AI Modes Framework — visual rebrand metadata.

Pure-visual mapping of e-SF Copilot sections to the "5 AI Modes" framework.
Used by each Streamlit page to render its section-header banner, and by the
overview page (`12_📊_5_AI_Modes_Map.py`) to draw the framework grid.

NO business logic, NO parsing, NO LLM calls — visual layer only.
Safe to import from any page.
"""
from __future__ import annotations

import streamlit as st

NAVY = "#1A2B47"

# Order matters: this is the rendering order in the overview map.
MODES: dict[str, dict] = {
    "DETECT": {
        "color": "#42D7F5",         # cyan
        "emoji": "🔵",
        "id": "01",
        "name_en": "DETECT",
        "name_pl": "DETECT",
        "question_en": "Is there anything strange in our numbers?",
        "question_pl": "Czy w naszych liczbach jest coś dziwnego?",
        "sections": ["XML Analysis", "Anomaly Detection", "P&L", "Balance Sheet", "Cash Flow"],
    },
    "FORECAST": {
        "color": "#9D6BD0",         # violet
        "emoji": "🟣",
        "id": "02",
        "name_en": "FORECAST",
        "name_pl": "FORECAST",
        "question_en": "What if rates rise by 200 bp?",
        "question_pl": "Co się stanie, jeśli stopy wzrosną o 200 bp?",
        "sections": ["Forecasting"],
    },
    "REVIEW": {
        "color": "#069F8C",         # teal
        "emoji": "🟢",
        "id": "03",
        "name_en": "REVIEW",
        "name_pl": "REVIEW",
        "question_en": "Is this document consistent and complete?",
        "question_pl": "Czy ten dokument jest spójny i kompletny?",
        "sections": ["CFO Chat", "NL Query"],
    },
    "DRAFT": {
        "color": "#FFA94D",         # orange
        "emoji": "🟠",
        "id": "04",
        "name_en": "DRAFT",
        "name_pl": "DRAFT",
        "question_en": "Help me write the first draft…",
        "question_pl": "Pomóż mi napisać pierwszą wersję…",
        "sections": ["Board Memo LLM"],
    },
    "ORCHESTRATE": {
        "color": "#76B900",         # NVIDIA green
        "emoji": "🟡",
        "id": "05",
        "name_en": "ORCHESTRATE",
        "name_pl": "ORCHESTRATE",
        "question_en": "I do this every quarter — can it be automated?",
        "question_pl": "Powtarzam to co kwartał — można zautomatyzować?",
        "sections": ["Batch Processing"],
    },
}


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def render_mode_header(mode_key: str, lang: str = "PL") -> None:
    """Render the section-top banner for *mode_key*. Visual only.

    Drops a dark navy strip at the top of the page with a colored left + top
    border, the framework label, the mode name, and the canonical question.
    Call once near the top of each page, after st.set_page_config.
    """
    m = MODES[mode_key]
    name = m["name_pl"] if lang.upper() == "PL" else m["name_en"]
    question = m["question_pl"] if lang.upper() == "PL" else m["question_en"]
    framework_label = "Tryb" if lang.upper() == "PL" else "Mode"
    color = m["color"]
    html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(26,43,71,0.97) 0%, rgba(26,43,71,0.88) 100%);
        border-left: 6px solid {color};
        border-top: 3px solid {color};
        padding: 16px 24px;
        border-radius: 8px;
        margin-bottom: 24px;
    ">
        <div style="color: {color}; font-size: 11px; font-weight: 700;
                    letter-spacing: 2px; text-transform: uppercase;">
            {framework_label} {m['id']} · 5 AI MODES FRAMEWORK
        </div>
        <div style="color: white; font-size: 28px; font-weight: 700; margin-top: 4px;">
            {name} MODE
        </div>
        <div style="color: #E2E8F0; font-size: 14px; font-style: italic; margin-top: 8px;">
            "{question}"
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def inject_mode_styles(mode_key: str) -> None:
    """Inject CSS for subtle background tint + KPI border-left in the page.

    Tints the main block container with the mode color at ~5% opacity, and
    adds a 4 px left border (full mode color) to every st.metric on the page.
    Call once near the top of each page, after st.set_page_config.
    """
    m = MODES[mode_key]
    r, g, b = _hex_to_rgb(m["color"])
    css = f"""
    <style>
        section.main > div.block-container {{
            background: rgba({r},{g},{b},0.05);
            border-radius: 12px;
            padding: 1rem 1.5rem !important;
        }}
        [data-testid="stMetric"] {{
            border-left: 4px solid {m['color']};
            padding-left: 12px;
            background: white;
            border-radius: 4px;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def apply_mode(mode_key: str, lang: str = "PL") -> None:
    """Convenience: inject styles + render banner in one call."""
    inject_mode_styles(mode_key)
    render_mode_header(mode_key, lang=lang)
