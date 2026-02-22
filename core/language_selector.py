"""Language selector component for sidebar - shared across all pages."""
from __future__ import annotations

import streamlit as st


def render_language_selector() -> str:
    """
    Render language selector in sidebar and return current language.

    Returns:
        str: Current language code ("EN" or "PL")
    """
    # Initialize session state if not exists
    if "language" not in st.session_state:
        st.session_state.language = "EN"

    # Create sidebar selector
    with st.sidebar:
        st.divider()
        language = st.selectbox(
            "🌐 Language / Język",
            options=["EN", "PL"],
            index=0 if st.session_state.language == "EN" else 1,
            key="language_selector"
        )

        # Update session state
        st.session_state.language = language

    return st.session_state.language


def get_current_language() -> str:
    """
    Get current language from session state.

    Returns:
        str: Current language code ("EN" or "PL"), defaults to "EN"
    """
    return st.session_state.get("language", "EN")
