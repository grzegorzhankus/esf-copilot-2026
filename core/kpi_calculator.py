from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class KPI:
    key: str
    name: str
    value: Optional[float]
    unit: str
    category: str
    interpretation: str


def _get_metric(metrics: Dict[str, Optional[float]], *keys: str) -> Optional[float]:
    """Get metric value trying multiple key names (for backward compatibility)."""
    for key in keys:
        val = metrics.get(key)
        if val is not None:
            return val
    return None


def calculate_kpis(metrics: Dict[str, Optional[float]]) -> List[KPI]:
    """
    Calculate financial KPIs from base metrics.

    Categories:
    - Profitability: Measures how efficiently the company generates profit
    - Liquidity: Measures ability to meet short-term obligations
    - Leverage: Measures financial structure and debt levels
    - Efficiency: Measures how effectively assets are used
    """
    kpis: List[KPI] = []

    # Extract base metrics (with fallback key names for compatibility)
    total_assets = _get_metric(metrics, "bs_total_assets", "bs_assets_total")
    equity = _get_metric(metrics, "bs_equity_total", "bs_equity")
    liabilities = _get_metric(metrics, "bs_total_liabilities", "bs_liabilities_total")
    current_assets = _get_metric(metrics, "bs_current_assets")
    current_liabilities = _get_metric(metrics, "bs_current_liabilities")
    inventory = _get_metric(metrics, "bs_inventory")
    cash = _get_metric(metrics, "bs_cash")
    receivables = _get_metric(metrics, "bs_accounts_receivable")
    revenue = _get_metric(metrics, "pl_revenue")
    ebit = _get_metric(metrics, "pl_ebit")
    net_income = _get_metric(metrics, "pl_net_income", "pl_net_profit")
    cf_operations = _get_metric(metrics, "cf_net_cash_from_operations")

    # ===== PROFITABILITY RATIOS =====

    # Return on Assets (ROA)
    if net_income is not None and total_assets is not None and total_assets != 0:
        roa = (net_income / total_assets) * 100
        kpis.append(KPI(
            key="roa",
            name="Return on Assets (ROA)",
            value=round(roa, 2),
            unit="%",
            category="Profitability",
            interpretation="Higher is better. Shows profit generated per unit of assets."
        ))

    # Return on Equity (ROE)
    if net_income is not None and equity is not None and equity != 0:
        roe = (net_income / equity) * 100
        kpis.append(KPI(
            key="roe",
            name="Return on Equity (ROE)",
            value=round(roe, 2),
            unit="%",
            category="Profitability",
            interpretation="Higher is better. Shows profit generated per unit of shareholder equity."
        ))

    # Net Profit Margin
    if net_income is not None and revenue is not None and revenue != 0:
        npm = (net_income / revenue) * 100
        kpis.append(KPI(
            key="net_profit_margin",
            name="Net Profit Margin",
            value=round(npm, 2),
            unit="%",
            category="Profitability",
            interpretation="Higher is better. Shows percentage of revenue converted to profit."
        ))

    # EBIT Margin
    if ebit is not None and revenue is not None and revenue != 0:
        ebit_margin = (ebit / revenue) * 100
        kpis.append(KPI(
            key="ebit_margin",
            name="EBIT Margin",
            value=round(ebit_margin, 2),
            unit="%",
            category="Profitability",
            interpretation="Higher is better. Shows operating profitability before interest and tax."
        ))

    # ===== LIQUIDITY RATIOS =====

    # Current Ratio
    if current_assets is not None and current_liabilities is not None and current_liabilities != 0:
        current_ratio = current_assets / current_liabilities
        kpis.append(KPI(
            key="current_ratio",
            name="Current Ratio",
            value=round(current_ratio, 2),
            unit="ratio",
            category="Liquidity",
            interpretation="Higher is better (>1.5 ideal). Shows ability to pay short-term obligations."
        ))

    # Quick Ratio (Acid Test) - excludes inventory
    if current_assets is not None and inventory is not None and current_liabilities is not None and current_liabilities != 0:
        quick_assets = current_assets - inventory
        quick_ratio = quick_assets / current_liabilities
        kpis.append(KPI(
            key="quick_ratio",
            name="Quick Ratio (Acid Test)",
            value=round(quick_ratio, 2),
            unit="ratio",
            category="Liquidity",
            interpretation="Higher is better (>1.0 ideal). Shows ability to pay obligations without selling inventory."
        ))

    # Cash Ratio
    if cash is not None and current_liabilities is not None and current_liabilities != 0:
        cash_ratio = cash / current_liabilities
        kpis.append(KPI(
            key="cash_ratio",
            name="Cash Ratio",
            value=round(cash_ratio, 2),
            unit="ratio",
            category="Liquidity",
            interpretation="Shows immediate ability to pay current liabilities with cash."
        ))

    # ===== LEVERAGE RATIOS =====

    # Debt-to-Equity Ratio
    if liabilities is not None and equity is not None and equity != 0:
        debt_to_equity = liabilities / equity
        kpis.append(KPI(
            key="debt_to_equity",
            name="Debt-to-Equity Ratio",
            value=round(debt_to_equity, 2),
            unit="ratio",
            category="Leverage",
            interpretation="Lower is generally better. Shows debt relative to equity."
        ))

    # Equity Ratio
    if equity is not None and total_assets is not None and total_assets != 0:
        equity_ratio = (equity / total_assets) * 100
        kpis.append(KPI(
            key="equity_ratio",
            name="Equity Ratio",
            value=round(equity_ratio, 2),
            unit="%",
            category="Leverage",
            interpretation="Higher is better. Shows portion of assets financed by equity."
        ))

    # Debt Ratio
    if liabilities is not None and total_assets is not None and total_assets != 0:
        debt_ratio = (liabilities / total_assets) * 100
        kpis.append(KPI(
            key="debt_ratio",
            name="Debt Ratio",
            value=round(debt_ratio, 2),
            unit="%",
            category="Leverage",
            interpretation="Lower is generally better. Shows portion of assets financed by debt."
        ))

    # ===== EFFICIENCY RATIOS =====

    # Asset Turnover
    if revenue is not None and total_assets is not None and total_assets != 0:
        asset_turnover = revenue / total_assets
        kpis.append(KPI(
            key="asset_turnover",
            name="Asset Turnover",
            value=round(asset_turnover, 2),
            unit="times",
            category="Efficiency",
            interpretation="Higher is better. Shows revenue generated per unit of assets."
        ))

    # Inventory Turnover (using revenue as proxy for COGS)
    if revenue is not None and inventory is not None and inventory != 0:
        inventory_turnover = revenue / inventory
        kpis.append(KPI(
            key="inventory_turnover",
            name="Inventory Turnover",
            value=round(inventory_turnover, 2),
            unit="times",
            category="Efficiency",
            interpretation="Higher is better. Shows how quickly inventory is sold."
        ))

    # Receivables Turnover
    if revenue is not None and receivables is not None and receivables != 0:
        receivables_turnover = revenue / receivables
        kpis.append(KPI(
            key="receivables_turnover",
            name="Receivables Turnover",
            value=round(receivables_turnover, 2),
            unit="times",
            category="Efficiency",
            interpretation="Higher is better. Shows how quickly receivables are collected."
        ))

    # Days Sales Outstanding (DSO)
    if revenue is not None and receivables is not None and revenue != 0:
        dso = (receivables / revenue) * 365
        kpis.append(KPI(
            key="days_sales_outstanding",
            name="Days Sales Outstanding",
            value=round(dso, 1),
            unit="days",
            category="Efficiency",
            interpretation="Lower is better. Average days to collect payment."
        ))

    # ===== CASH FLOW RATIOS =====

    # Operating Cash Flow Ratio (vs Revenue)
    if cf_operations is not None and revenue is not None and revenue != 0:
        ocf_ratio = (cf_operations / revenue) * 100
        kpis.append(KPI(
            key="ocf_to_revenue",
            name="Operating Cash Flow to Revenue",
            value=round(ocf_ratio, 2),
            unit="%",
            category="Cash Flow",
            interpretation="Higher is better. Shows cash generation efficiency."
        ))

    # Cash Flow to Net Income Ratio (Quality of Earnings)
    if cf_operations is not None and net_income is not None and net_income != 0:
        quality_earnings = (cf_operations / net_income) * 100
        kpis.append(KPI(
            key="quality_of_earnings",
            name="Quality of Earnings",
            value=round(quality_earnings, 2),
            unit="%",
            category="Cash Flow",
            interpretation="Value > 100% indicates strong earnings quality backed by cash."
        ))

    return kpis


def get_kpi_category_summary(kpis: List[KPI]) -> Dict[str, int]:
    """Get count of KPIs by category."""
    summary: Dict[str, int] = {}
    for kpi in kpis:
        summary[kpi.category] = summary.get(kpi.category, 0) + 1
    return summary
