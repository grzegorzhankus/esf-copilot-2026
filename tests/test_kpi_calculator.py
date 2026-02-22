"""Tests for core.kpi_calculator module."""
from __future__ import annotations

import pytest

from core.kpi_calculator import calculate_kpis, get_kpi_category_summary


class TestCalculateKpis:
    """Tests for calculate_kpis function."""

    def test_calculate_all_kpis_with_complete_data(self):
        """Test calculating KPIs with all required metrics present."""
        metrics = {
            "bs_total_assets": 1000000.0,
            "bs_equity_total": 400000.0,
            "bs_total_liabilities": 600000.0,
            "pl_revenue": 500000.0,
            "pl_ebit": 100000.0,
            "pl_net_income": 80000.0,
            "cf_net_cash_from_operations": 90000.0,
        }

        kpis = calculate_kpis(metrics)

        # Should have 10 KPIs
        assert len(kpis) == 10

        # Check that all expected KPI keys are present
        kpi_keys = {kpi.key for kpi in kpis}
        expected_keys = {
            "roa", "roe", "net_profit_margin", "ebit_margin",
            "debt_to_equity", "equity_ratio", "debt_ratio",
            "asset_turnover", "ocf_to_revenue", "quality_of_earnings"
        }
        assert kpi_keys == expected_keys

    def test_roa_calculation(self):
        """Test Return on Assets calculation."""
        metrics = {
            "bs_total_assets": 1000000.0,
            "pl_net_income": 80000.0,
        }

        kpis = calculate_kpis(metrics)
        roa_kpi = next(k for k in kpis if k.key == "roa")

        assert roa_kpi.value == 8.0  # (80000 / 1000000) * 100
        assert roa_kpi.unit == "%"
        assert roa_kpi.category == "Profitability"

    def test_roe_calculation(self):
        """Test Return on Equity calculation."""
        metrics = {
            "bs_equity_total": 400000.0,
            "pl_net_income": 80000.0,
        }

        kpis = calculate_kpis(metrics)
        roe_kpi = next(k for k in kpis if k.key == "roe")

        assert roe_kpi.value == 20.0  # (80000 / 400000) * 100
        assert roe_kpi.unit == "%"
        assert roe_kpi.category == "Profitability"

    def test_net_profit_margin_calculation(self):
        """Test Net Profit Margin calculation."""
        metrics = {
            "pl_revenue": 500000.0,
            "pl_net_income": 50000.0,
        }

        kpis = calculate_kpis(metrics)
        npm_kpi = next(k for k in kpis if k.key == "net_profit_margin")

        assert npm_kpi.value == 10.0  # (50000 / 500000) * 100
        assert npm_kpi.unit == "%"

    def test_ebit_margin_calculation(self):
        """Test EBIT Margin calculation."""
        metrics = {
            "pl_revenue": 500000.0,
            "pl_ebit": 75000.0,
        }

        kpis = calculate_kpis(metrics)
        ebit_kpi = next(k for k in kpis if k.key == "ebit_margin")

        assert ebit_kpi.value == 15.0  # (75000 / 500000) * 100

    def test_debt_to_equity_calculation(self):
        """Test Debt-to-Equity ratio calculation."""
        metrics = {
            "bs_equity_total": 400000.0,
            "bs_total_liabilities": 600000.0,
        }

        kpis = calculate_kpis(metrics)
        dte_kpi = next(k for k in kpis if k.key == "debt_to_equity")

        assert dte_kpi.value == 1.5  # 600000 / 400000
        assert dte_kpi.unit == "ratio"
        assert dte_kpi.category == "Leverage"

    def test_equity_ratio_calculation(self):
        """Test Equity Ratio calculation."""
        metrics = {
            "bs_total_assets": 1000000.0,
            "bs_equity_total": 400000.0,
        }

        kpis = calculate_kpis(metrics)
        equity_kpi = next(k for k in kpis if k.key == "equity_ratio")

        assert equity_kpi.value == 40.0  # (400000 / 1000000) * 100
        assert equity_kpi.unit == "%"

    def test_debt_ratio_calculation(self):
        """Test Debt Ratio calculation."""
        metrics = {
            "bs_total_assets": 1000000.0,
            "bs_total_liabilities": 600000.0,
        }

        kpis = calculate_kpis(metrics)
        debt_kpi = next(k for k in kpis if k.key == "debt_ratio")

        assert debt_kpi.value == 60.0  # (600000 / 1000000) * 100

    def test_asset_turnover_calculation(self):
        """Test Asset Turnover calculation."""
        metrics = {
            "bs_total_assets": 1000000.0,
            "pl_revenue": 500000.0,
        }

        kpis = calculate_kpis(metrics)
        at_kpi = next(k for k in kpis if k.key == "asset_turnover")

        assert at_kpi.value == 0.5  # 500000 / 1000000
        assert at_kpi.unit == "times"
        assert at_kpi.category == "Efficiency"

    def test_ocf_to_revenue_calculation(self):
        """Test Operating Cash Flow to Revenue calculation."""
        metrics = {
            "pl_revenue": 500000.0,
            "cf_net_cash_from_operations": 100000.0,
        }

        kpis = calculate_kpis(metrics)
        ocf_kpi = next(k for k in kpis if k.key == "ocf_to_revenue")

        assert ocf_kpi.value == 20.0  # (100000 / 500000) * 100
        assert ocf_kpi.category == "Cash Flow"

    def test_quality_of_earnings_calculation(self):
        """Test Quality of Earnings calculation."""
        metrics = {
            "pl_net_income": 80000.0,
            "cf_net_cash_from_operations": 96000.0,
        }

        kpis = calculate_kpis(metrics)
        qoe_kpi = next(k for k in kpis if k.key == "quality_of_earnings")

        assert qoe_kpi.value == 120.0  # (96000 / 80000) * 100
        assert qoe_kpi.category == "Cash Flow"

    def test_division_by_zero_handling(self):
        """Test that division by zero is handled gracefully."""
        metrics = {
            "bs_total_assets": 0.0,
            "bs_equity_total": 0.0,
            "pl_revenue": 0.0,
            "pl_net_income": 100000.0,
        }

        kpis = calculate_kpis(metrics)

        # Should not crash, and should not include KPIs with zero denominators
        assert len(kpis) == 0

    def test_missing_metrics_handling(self):
        """Test that missing metrics result in fewer KPIs."""
        metrics = {
            "bs_total_assets": 1000000.0,
            "pl_revenue": 500000.0,
        }

        kpis = calculate_kpis(metrics)

        # Only asset_turnover should be calculated
        assert len(kpis) == 1
        assert kpis[0].key == "asset_turnover"

    def test_negative_values_in_calculations(self):
        """Test that negative values are handled correctly in calculations."""
        metrics = {
            "bs_total_assets": 1000000.0,
            "pl_net_income": -50000.0,
        }

        kpis = calculate_kpis(metrics)
        roa_kpi = next(k for k in kpis if k.key == "roa")

        assert roa_kpi.value == -5.0  # Negative ROA


class TestGetKpiCategorySummary:
    """Tests for get_kpi_category_summary function."""

    def test_summary_with_all_categories(self):
        """Test category summary with KPIs from all categories."""
        metrics = {
            "bs_total_assets": 1000000.0,
            "bs_equity_total": 400000.0,
            "bs_total_liabilities": 600000.0,
            "pl_revenue": 500000.0,
            "pl_ebit": 100000.0,
            "pl_net_income": 80000.0,
            "cf_net_cash_from_operations": 90000.0,
        }

        kpis = calculate_kpis(metrics)
        summary = get_kpi_category_summary(kpis)

        assert summary["Profitability"] == 4
        assert summary["Leverage"] == 3
        assert summary["Efficiency"] == 1
        assert summary["Cash Flow"] == 2

    def test_summary_with_empty_kpis(self):
        """Test category summary with no KPIs."""
        kpis = []
        summary = get_kpi_category_summary(kpis)

        assert len(summary) == 0
