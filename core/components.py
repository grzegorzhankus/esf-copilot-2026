"""Shared UI components for AI CFO Dashboard.

This module provides reusable Streamlit components used across multiple pages.
"""
from __future__ import annotations

import streamlit as st


def render_nvidia_badge():
    """Render the NVIDIA DGX Spark badge in the footer."""
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align: center; padding: 8px 16px; background: linear-gradient(90deg, #76b900 0%, #1a1a1a 100%); border-radius: 8px; margin: 10px 0;">
                <span style="color: white; font-weight: bold; font-size: 14px;">⚡ Powered by NVIDIA DGX Spark</span>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_llm_badge(provider: str = "NVIDIA NIM"):
    """Render an LLM-powered badge.

    Args:
        provider: The LLM provider name to display.
    """
    st.markdown(
        f"""
        <div style="display: inline-block; padding: 4px 12px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 16px; margin: 5px 0;">
            <span style="color: white; font-size: 12px; font-weight: 500;">🤖 Powered by {provider}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_page_header(title: str, subtitle: str = None, show_llm_badge: bool = False):
    """Render a consistent page header.

    Args:
        title: Main page title.
        subtitle: Optional subtitle/description.
        show_llm_badge: Whether to show the LLM-powered badge.
    """
    st.title(title)
    if subtitle:
        st.markdown(subtitle)
    if show_llm_badge:
        render_llm_badge()
    st.markdown("---")
