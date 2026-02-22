"""
UI components module for cfo-copilot.

Provides reusable Streamlit UI components including:
- Traffic light pills (OK/Watch/Risk indicators)
- Classification functions for financial metrics
- Pill badge HTML generators
"""

from typing import Optional, Tuple
from core.i18n import t


# ---------- Traffic Light Classification ----------

def classify_higher_better(value: Optional[float], good: float, warn: float, language: str = "EN") -> Tuple[str, str]:
    """
    Classify a metric where higher values are better.

    Args:
        value: Metric value to classify
        good: Threshold for "OK" status (value >= good)
        warn: Threshold for "Watch" status (value >= warn)
        language: Language code for label translation ("EN" or "PL")

    Returns:
        Tuple of (label, css_class) where:
        - label: Translated "OK", "Watch", "Risk", or "n/a"
        - css_class: "pill-green", "pill-yellow", or "pill-red"

    Example:
        >>> classify_higher_better(2.5, 2.0, 1.0, "EN")
        ("OK", "pill-green")
        >>> classify_higher_better(1.5, 2.0, 1.0, "PL")
        ("Obserwuj", "pill-yellow")
    """
    if value is None:
        return t("traffic_light_na", language), "pill-yellow"
    if value >= good:
        return t("traffic_light_ok", language), "pill-green"
    if value >= warn:
        return t("traffic_light_watch", language), "pill-yellow"
    return t("traffic_light_risk", language), "pill-red"


def classify_lower_better(value: Optional[float], good: float, warn: float, language: str = "EN") -> Tuple[str, str]:
    """
    Classify a metric where lower values are better.

    Args:
        value: Metric value to classify
        good: Threshold for "OK" status (value <= good)
        warn: Threshold for "Watch" status (value <= warn)
        language: Language code for label translation ("EN" or "PL")

    Returns:
        Tuple of (label, css_class) where:
        - label: Translated "OK", "Watch", "Risk", or "n/a"
        - css_class: "pill-green", "pill-yellow", or "pill-red"

    Example:
        >>> classify_lower_better(0.3, 0.5, 0.7, "EN")
        ("OK", "pill-green")
        >>> classify_lower_better(0.8, 0.5, 0.7, "PL")
        ("Ryzyko", "pill-red")
    """
    if value is None:
        return t("traffic_light_na", language), "pill-yellow"
    if value <= good:
        return t("traffic_light_ok", language), "pill-green"
    if value <= warn:
        return t("traffic_light_watch", language), "pill-yellow"
    return t("traffic_light_risk", language), "pill-red"


# ---------- Pill Badge Generators ----------

def pill_badge(label: str, css_class: str) -> str:
    """
    Generate HTML for a pill badge.

    Args:
        label: Text to display in the pill
        css_class: CSS class for styling (pill-green, pill-yellow, pill-red)

    Returns:
        HTML string for the pill badge

    Example:
        >>> pill_badge("OK", "pill-green")
        '<span class="pill pill-green">OK</span>'
    """
    return f'<span class="pill {css_class}">{label}</span>'


def metric_with_pill(
    pill_label: str,
    pill_class: str,
    metric_name: str,
    metric_value: str,
    unsafe_allow_html: bool = True
) -> str:
    """
    Generate HTML for a metric display with traffic light pill.

    Args:
        pill_label: Label for the pill (e.g., "OK", "Watch", "Risk")
        pill_class: CSS class for the pill
        metric_name: Name of the metric
        metric_value: Formatted value of the metric
        unsafe_allow_html: Whether to mark as unsafe HTML (for st.markdown)

    Returns:
        Formatted HTML string

    Example:
        >>> metric_with_pill("OK", "pill-green", "Current Ratio", "2.5")
        '<span class="pill pill-green">OK</span> Current Ratio = 2.5'
    """
    return f'{pill_badge(pill_label, pill_class)} {metric_name} = {metric_value}'


def traffic_light_metric_html(
    value: Optional[float],
    good_threshold: float,
    warn_threshold: float,
    higher_is_better: bool,
    metric_name: str,
    format_fn=None
) -> str:
    """
    Generate complete HTML for a metric with automatic traffic light classification.

    Args:
        value: Metric value
        good_threshold: Threshold for "OK" classification
        warn_threshold: Threshold for "Watch" classification
        higher_is_better: If True, higher values get "OK"; if False, lower values get "OK"
        metric_name: Display name for the metric
        format_fn: Optional function to format the value (default: f"{value:.2f}")

    Returns:
        Complete HTML string with pill and metric

    Example:
        >>> traffic_light_metric_html(2.5, 2.0, 1.0, True, "Current Ratio")
        '<span class="pill pill-green">OK</span> Current Ratio = 2.50'
    """
    if higher_is_better:
        label, css_class = classify_higher_better(value, good_threshold, warn_threshold)
    else:
        label, css_class = classify_lower_better(value, good_threshold, warn_threshold)

    if value is None:
        formatted_value = "—"
    elif format_fn:
        formatted_value = format_fn(value)
    else:
        formatted_value = f"{value:.2f}"

    return metric_with_pill(label, css_class, metric_name, formatted_value)


# ---------- Card Components ----------

def hero_card(content: str) -> str:
    """
    Generate HTML for a hero card (gradient background).

    Args:
        content: HTML content to display in the card

    Returns:
        HTML string for hero card
    """
    return f'<div class="hero">{content}</div>'


def card(content: str) -> str:
    """
    Generate HTML for a standard card.

    Args:
        content: HTML content to display in the card

    Returns:
        HTML string for card
    """
    return f'<div class="card">{content}</div>'


# ---------- CSS Styles ----------

def get_pill_css() -> str:
    """
    Get CSS styles for pill badges.

    Returns:
        CSS string with pill styles
    """
    return """
.pill {
  display:inline-block;
  padding:4px 10px;
  border-radius:999px;
  font-size:0.85rem;
  font-weight:600;
  margin-right:6px;
}
.pill-green  { background:rgba(46,125,50,0.10);  color:#1B5E20; }
.pill-yellow { background:rgba(237,108,2,0.10);  color:#E65100; }
.pill-red    { background:rgba(198,40,40,0.10);  color:#B71C1C; }
"""


def get_card_css() -> str:
    """
    Get CSS styles for card components.

    Returns:
        CSS string with card styles
    """
    return """
/* hero card */
.hero {
  padding: 18px 18px 14px 18px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(40,60,255,0.28), rgba(0,245,255,0.10));
  border: 1px solid rgba(0,0,0,0.10);
  color: rgba(0,0,0,0.92) !important;
}
.hero * {
  color: rgba(0,0,0,0.92) !important;
}
.smallmuted {
  color: rgba(0,0,0,0.65) !important;
  font-size: 0.9rem;
}

/* generic card */
.card {
  border-radius: 18px;
  padding: 14px 14px 10px 14px;
  border: 1px solid rgba(0,0,0,0.06);
  background: rgba(255,255,255,0.6);
}
"""


def get_all_component_css() -> str:
    """
    Get all CSS styles for UI components.

    Returns:
        Complete CSS string
    """
    return f"""<style>
{get_card_css()}
{get_pill_css()}
hr {{
  border: none;
  height: 1px;
  background: rgba(0,0,0,0.08);
  margin: 14px 0;
}}
</style>"""
