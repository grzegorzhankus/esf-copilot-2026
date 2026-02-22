from __future__ import annotations

from typing import List

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from core.contracts import AnalysisResult, KPI, MetricValue


def create_base_metrics_chart(metrics: List[MetricValue]) -> go.Figure:
    """Create bar chart for base financial metrics."""
    # Filter out None values
    valid_metrics = [m for m in metrics if m.value is not None]

    if not valid_metrics:
        return None

    keys = [m.key for m in valid_metrics]
    values = [m.value for m in valid_metrics]

    fig = go.Figure(data=[
        go.Bar(
            x=keys,
            y=values,
            marker_color='lightblue',
            text=values,
            texttemplate='%{text:,.0f}',
            textposition='outside',
        )
    ])

    fig.update_layout(
        title="Base Financial Metrics",
        xaxis_title="Metric",
        yaxis_title="Value (PLN thousands)",
        height=400,
        showlegend=False,
        template="plotly_white"
    )

    return fig


def create_balance_sheet_structure_chart(metrics: List[MetricValue]) -> go.Figure:
    """Create pie chart showing balance sheet structure (Assets vs Equity vs Liabilities)."""
    # Extract relevant metrics
    equity = None
    liabilities = None

    for m in metrics:
        if m.key == "bs_equity_total" and m.value is not None:
            equity = m.value
        elif m.key == "bs_total_liabilities" and m.value is not None:
            liabilities = m.value

    if equity is None or liabilities is None:
        return None

    # Create pie chart
    labels = ['Equity', 'Liabilities']
    values = [equity, liabilities]
    colors = ['#70AD47', '#E74C3C']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.3,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{value:,.0f}<br>(%{percent})',
    )])

    fig.update_layout(
        title="Balance Sheet Structure",
        height=400,
        showlegend=True,
        template="plotly_white"
    )

    return fig


def create_kpi_radar_chart(kpis: List[KPI]) -> go.Figure:
    """Create radar chart for profitability KPIs."""
    # Filter profitability KPIs with valid values
    profitability_kpis = [
        k for k in kpis
        if k.category == "Profitability" and k.value is not None
    ]

    if not profitability_kpis:
        return None

    # Normalize values to 0-100 scale for radar chart
    names = [k.name.replace(" (ROA)", "").replace(" (ROE)", "") for k in profitability_kpis]
    values = [abs(k.value) for k in profitability_kpis]  # Use absolute values for display

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=names,
        fill='toself',
        name='Profitability Metrics',
        line_color='#4472C4'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.2] if values else [0, 100]
            )
        ),
        title="Profitability KPIs",
        height=450,
        showlegend=False,
        template="plotly_white"
    )

    return fig


def create_kpi_gauge_charts(kpis: List[KPI]) -> List[go.Figure]:
    """Create gauge charts for key KPIs."""
    gauges = []

    # Define KPIs to create gauges for
    gauge_kpis = ["roe", "roa", "net_profit_margin", "debt_to_equity"]

    for kpi in kpis:
        if kpi.key not in gauge_kpis or kpi.value is None:
            continue

        # Determine gauge ranges and colors based on KPI type
        if kpi.key in ["roe", "roa", "net_profit_margin"]:
            # Higher is better
            max_val = 30 if kpi.key in ["roe", "roa"] else 20
            ranges = [
                {"range": [0, 5], "color": "red"},
                {"range": [5, 10], "color": "yellow"},
                {"range": [10, max_val], "color": "green"}
            ]
        else:  # debt_to_equity
            # Lower is better
            max_val = 4
            ranges = [
                {"range": [0, 1], "color": "green"},
                {"range": [1, 2], "color": "yellow"},
                {"range": [2, max_val], "color": "red"}
            ]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=kpi.value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': kpi.name, 'font': {'size': 16}},
            number={'suffix': kpi.unit},
            gauge={
                'axis': {'range': [None, max_val]},
                'bar': {'color': "darkblue"},
                'steps': ranges,
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': kpi.value
                }
            }
        ))

        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            template="plotly_white"
        )

        gauges.append(fig)

    return gauges


def create_red_flags_summary_chart(result: AnalysisResult) -> go.Figure:
    """Create bar chart summarizing red flags by severity."""
    if not result.red_flags:
        return None

    detected = [f for f in result.red_flags if f.detected]

    high = len([f for f in detected if f.severity == "high"])
    medium = len([f for f in detected if f.severity == "medium"])
    low = len([f for f in detected if f.severity == "low"])
    passed = len(result.red_flags) - len(detected)

    fig = go.Figure(data=[
        go.Bar(
            x=['High', 'Medium', 'Low', 'Passed'],
            y=[high, medium, low, passed],
            marker_color=['#E74C3C', '#F39C12', '#F1C40F', '#70AD47'],
            text=[high, medium, low, passed],
            textposition='outside',
        )
    ])

    fig.update_layout(
        title="Red Flags Summary",
        xaxis_title="Severity",
        yaxis_title="Count",
        height=350,
        showlegend=False,
        template="plotly_white"
    )

    return fig


def create_financial_health_score_chart(result: AnalysisResult) -> go.Figure:
    """Create a simple financial health score visualization."""
    if not result.red_flags:
        return None

    detected = [f for f in result.red_flags if f.detected]
    total_checks = len(result.red_flags)

    # Calculate score (0-100)
    # Deduct more points for high severity flags
    deductions = 0
    for flag in detected:
        if flag.severity == "high":
            deductions += 15
        elif flag.severity == "medium":
            deductions += 8
        else:  # low
            deductions += 3

    score = max(0, 100 - deductions)

    # Determine color
    if score >= 80:
        color = "green"
        health_status = "Excellent"
    elif score >= 60:
        color = "lightgreen"
        health_status = "Good"
    elif score >= 40:
        color = "yellow"
        health_status = "Fair"
    elif score >= 20:
        color = "orange"
        health_status = "Poor"
    else:
        color = "red"
        health_status = "Critical"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Financial Health Score<br><span style='font-size:0.8em;color:gray'>{health_status}</span>", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 20], 'color': '#ffcccc'},
                {'range': [20, 40], 'color': '#ffe6cc'},
                {'range': [40, 60], 'color': '#ffffcc'},
                {'range': [60, 80], 'color': '#e6ffcc'},
                {'range': [80, 100], 'color': '#ccffcc'}
            ],
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=80, b=20),
        template="plotly_white"
    )

    return fig
