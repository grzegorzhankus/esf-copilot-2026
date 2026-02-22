from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Forecast:
    metric_key: str
    metric_name: str
    current_value: Optional[float]
    forecast_1y: Optional[float]
    forecast_2y: Optional[float]
    forecast_3y: Optional[float]
    growth_rate: Optional[float]
    confidence: str  # "high", "medium", "low"
    method: str


def simple_linear_forecast(
    metrics: Dict[str, Optional[float]],
    growth_rate: float = 0.05  # Default 5% growth
) -> List[Forecast]:
    """
    Create simple linear forecasts based on current metrics and assumed growth rate.

    This is a simplified forecasting method. In production, you would:
    - Use historical data to calculate actual growth trends
    - Apply more sophisticated forecasting methods (ARIMA, exponential smoothing, etc.)
    - Consider seasonality and external factors
    - Use machine learning models for better accuracy
    """
    forecasts: List[Forecast] = []

    # Revenue forecast
    revenue = metrics.get("pl_revenue")
    if revenue is not None and revenue > 0:
        forecasts.append(Forecast(
            metric_key="pl_revenue",
            metric_name="Revenue",
            current_value=revenue,
            forecast_1y=revenue * (1 + growth_rate),
            forecast_2y=revenue * (1 + growth_rate) ** 2,
            forecast_3y=revenue * (1 + growth_rate) ** 3,
            growth_rate=growth_rate * 100,
            confidence="low",
            method="Linear growth assumption"
        ))

    # Net income forecast
    net_income = metrics.get("pl_net_income")
    if net_income is not None:
        # More conservative growth for net income
        ni_growth = growth_rate * 0.8 if net_income > 0 else growth_rate * 0.5
        forecasts.append(Forecast(
            metric_key="pl_net_income",
            metric_name="Net Income",
            current_value=net_income,
            forecast_1y=net_income * (1 + ni_growth) if net_income > 0 else net_income,
            forecast_2y=net_income * (1 + ni_growth) ** 2 if net_income > 0 else net_income,
            forecast_3y=net_income * (1 + ni_growth) ** 3 if net_income > 0 else net_income,
            growth_rate=ni_growth * 100 if net_income > 0 else 0,
            confidence="low",
            method="Conservative linear growth"
        ))

    # Total assets forecast
    total_assets = metrics.get("bs_total_assets")
    if total_assets is not None and total_assets > 0:
        # Assets typically grow slower than revenue
        asset_growth = growth_rate * 0.6
        forecasts.append(Forecast(
            metric_key="bs_total_assets",
            metric_name="Total Assets",
            current_value=total_assets,
            forecast_1y=total_assets * (1 + asset_growth),
            forecast_2y=total_assets * (1 + asset_growth) ** 2,
            forecast_3y=total_assets * (1 + asset_growth) ** 3,
            growth_rate=asset_growth * 100,
            confidence="low",
            method="Asset accumulation model"
        ))

    # Equity forecast (based on retained earnings)
    equity = metrics.get("bs_equity_total")
    if equity is not None and net_income is not None and equity > 0:
        # Assume 50% of net income is retained
        retention_rate = 0.5
        forecasts.append(Forecast(
            metric_key="bs_equity_total",
            metric_name="Equity",
            current_value=equity,
            forecast_1y=equity + (net_income * retention_rate) if net_income > 0 else equity,
            forecast_2y=equity + (net_income * retention_rate * 2) if net_income > 0 else equity,
            forecast_3y=equity + (net_income * retention_rate * 3) if net_income > 0 else equity,
            growth_rate=((net_income * retention_rate) / equity * 100) if net_income > 0 and equity > 0 else 0,
            confidence="medium",
            method="Retained earnings accumulation"
        ))

    return forecasts


def scenario_analysis(
    metrics: Dict[str, Optional[float]]
) -> Dict[str, List[Forecast]]:
    """
    Generate forecasts for best case, base case, and worst case scenarios.
    """
    scenarios = {
        "best_case": simple_linear_forecast(metrics, growth_rate=0.15),  # 15% growth
        "base_case": simple_linear_forecast(metrics, growth_rate=0.05),  # 5% growth
        "worst_case": simple_linear_forecast(metrics, growth_rate=-0.02),  # -2% decline
    }

    return scenarios


def calculate_breakeven_point(
    revenue: Optional[float],
    variable_costs: Optional[float],
    fixed_costs: Optional[float]
) -> Optional[float]:
    """
    Calculate breakeven point in revenue.

    Formula: Breakeven = Fixed Costs / (1 - (Variable Costs / Revenue))
    """
    if revenue is None or variable_costs is None or fixed_costs is None:
        return None

    if revenue == 0:
        return None

    contribution_margin_ratio = 1 - (variable_costs / revenue)

    if contribution_margin_ratio <= 0:
        return None

    return fixed_costs / contribution_margin_ratio


@dataclass(frozen=True)
class ForecastSummary:
    total_forecasts: int
    high_confidence: int
    medium_confidence: int
    low_confidence: int
    avg_growth_rate: float
    scenarios_available: bool


def get_forecast_summary(forecasts: List[Forecast]) -> ForecastSummary:
    """Get summary statistics for forecasts."""
    if not forecasts:
        return ForecastSummary(
            total_forecasts=0,
            high_confidence=0,
            medium_confidence=0,
            low_confidence=0,
            avg_growth_rate=0.0,
            scenarios_available=False
        )

    high = len([f for f in forecasts if f.confidence == "high"])
    medium = len([f for f in forecasts if f.confidence == "medium"])
    low = len([f for f in forecasts if f.confidence == "low"])

    # Calculate average growth rate (excluding None values)
    growth_rates = [f.growth_rate for f in forecasts if f.growth_rate is not None]
    avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0.0

    return ForecastSummary(
        total_forecasts=len(forecasts),
        high_confidence=high,
        medium_confidence=medium,
        low_confidence=low,
        avg_growth_rate=avg_growth,
        scenarios_available=True
    )
