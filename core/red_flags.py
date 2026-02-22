from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class RedFlag:
    key: str
    title: str
    severity: str  # "high", "medium", "low"
    description: str
    detected: bool
    details: str


def detect_red_flags(
    metrics: Dict[str, Optional[float]],
    kpis: Dict[str, Optional[float]]
) -> List[RedFlag]:
    """
    Detect financial red flags based on metrics and KPIs.

    Severity levels:
    - high: Critical issues requiring immediate attention
    - medium: Concerning trends that should be monitored
    - low: Minor issues or areas for improvement
    """
    flags: List[RedFlag] = []

    # Extract values
    net_income = metrics.get("pl_net_income")
    revenue = metrics.get("pl_revenue")
    equity = metrics.get("bs_equity_total")
    liabilities = metrics.get("bs_total_liabilities")
    total_assets = metrics.get("bs_total_assets")
    cf_operations = metrics.get("cf_net_cash_from_operations")

    # KPI values
    roe = kpis.get("roe")
    debt_to_equity = kpis.get("debt_to_equity")
    net_profit_margin = kpis.get("net_profit_margin")
    equity_ratio = kpis.get("equity_ratio")
    quality_of_earnings = kpis.get("quality_of_earnings")

    # ===== RED FLAG 1: Negative Net Income =====
    if net_income is not None:
        detected = net_income < 0
        flags.append(RedFlag(
            key="negative_net_income",
            title="Negative Net Income",
            severity="high",
            description="Company is operating at a loss",
            detected=detected,
            details=f"Net income: {net_income:,.2f}" if detected else "Net income is positive"
        ))

    # ===== RED FLAG 2: Negative Equity (Insolvency Risk) =====
    if equity is not None:
        detected = equity < 0
        flags.append(RedFlag(
            key="negative_equity",
            title="Negative Equity",
            severity="high",
            description="Liabilities exceed assets - technical insolvency",
            detected=detected,
            details=f"Equity: {equity:,.2f}" if detected else "Equity is positive"
        ))

    # ===== RED FLAG 3: High Debt-to-Equity Ratio =====
    if debt_to_equity is not None:
        detected = debt_to_equity > 2.0
        flags.append(RedFlag(
            key="high_debt_to_equity",
            title="High Debt-to-Equity Ratio",
            severity="medium",
            description="Debt is more than 2x equity - high financial leverage",
            detected=detected,
            details=f"Debt-to-Equity: {debt_to_equity:.2f} (threshold: 2.0)" if detected else f"Debt-to-Equity: {debt_to_equity:.2f} - within acceptable range"
        ))

    # ===== RED FLAG 4: Low Equity Ratio =====
    if equity_ratio is not None:
        detected = equity_ratio < 20.0
        flags.append(RedFlag(
            key="low_equity_ratio",
            title="Low Equity Ratio",
            severity="medium",
            description="Less than 20% of assets financed by equity",
            detected=detected,
            details=f"Equity Ratio: {equity_ratio:.2f}% (threshold: 20%)" if detected else f"Equity Ratio: {equity_ratio:.2f}% - adequate"
        ))

    # ===== RED FLAG 5: Negative Operating Cash Flow =====
    if cf_operations is not None:
        detected = cf_operations < 0
        flags.append(RedFlag(
            key="negative_operating_cash_flow",
            title="Negative Operating Cash Flow",
            severity="high",
            description="Operations are consuming cash rather than generating it",
            detected=detected,
            details=f"Operating Cash Flow: {cf_operations:,.2f}" if detected else "Operating cash flow is positive"
        ))

    # ===== RED FLAG 6: Poor Quality of Earnings =====
    if quality_of_earnings is not None and net_income is not None and net_income > 0:
        detected = quality_of_earnings < 80.0
        flags.append(RedFlag(
            key="poor_quality_of_earnings",
            title="Poor Quality of Earnings",
            severity="medium",
            description="Operating cash flow is less than 80% of net income - earnings may not be sustainable",
            detected=detected,
            details=f"Quality of Earnings: {quality_of_earnings:.2f}% (threshold: 80%)" if detected else f"Quality of Earnings: {quality_of_earnings:.2f}% - good"
        ))

    # ===== RED FLAG 7: Negative Profit Margin =====
    if net_profit_margin is not None:
        detected = net_profit_margin < 0
        flags.append(RedFlag(
            key="negative_profit_margin",
            title="Negative Profit Margin",
            severity="high",
            description="Company loses money on each unit of revenue",
            detected=detected,
            details=f"Net Profit Margin: {net_profit_margin:.2f}%" if detected else f"Net Profit Margin: {net_profit_margin:.2f}% - profitable"
        ))

    # ===== RED FLAG 8: Low Profitability (ROE) =====
    if roe is not None and equity is not None and equity > 0:
        detected = roe < 5.0 and roe >= 0
        flags.append(RedFlag(
            key="low_roe",
            title="Low Return on Equity",
            severity="low",
            description="ROE below 5% indicates poor profitability",
            detected=detected,
            details=f"ROE: {roe:.2f}% (threshold: 5%)" if detected else f"ROE: {roe:.2f}% - acceptable"
        ))

    # ===== RED FLAG 9: Revenue Decline =====
    # Note: This would require historical data, so we'll mark it as not applicable for now
    # In future, when we have multi-period analysis, we can implement this

    # ===== RED FLAG 10: Excessive Leverage (Debt > 80% of Assets) =====
    if liabilities is not None and total_assets is not None and total_assets > 0:
        debt_ratio_pct = (liabilities / total_assets) * 100
        detected = debt_ratio_pct > 80.0
        flags.append(RedFlag(
            key="excessive_leverage",
            title="Excessive Leverage",
            severity="high",
            description="Debt exceeds 80% of total assets",
            detected=detected,
            details=f"Debt Ratio: {debt_ratio_pct:.2f}% (threshold: 80%)" if detected else f"Debt Ratio: {debt_ratio_pct:.2f}% - acceptable"
        ))

    return flags


def get_red_flag_summary(flags: List[RedFlag]) -> Dict[str, int]:
    """Get summary of detected red flags by severity."""
    detected = [f for f in flags if f.detected]
    summary = {
        "total_flags": len(flags),
        "detected": len(detected),
        "high": len([f for f in detected if f.severity == "high"]),
        "medium": len([f for f in detected if f.severity == "medium"]),
        "low": len([f for f in detected if f.severity == "low"]),
    }
    return summary
