"""Tests for core.red_flags module."""
from __future__ import annotations

import pytest

from core.red_flags import detect_red_flags, get_red_flag_summary


class TestDetectRedFlags:
    """Tests for detect_red_flags function."""

    def test_detect_all_flags_with_healthy_company(self):
        """Test red flag detection with healthy financial metrics."""
        metrics = {
            "pl_net_income": 100000.0,
            "pl_revenue": 500000.0,
            "bs_equity_total": 400000.0,
            "bs_total_liabilities": 300000.0,
            "bs_total_assets": 700000.0,
            "cf_net_cash_from_operations": 90000.0,
        }
        kpis = {
            "roe": 25.0,
            "debt_to_equity": 0.75,
            "net_profit_margin": 20.0,
            "equity_ratio": 57.14,
            "quality_of_earnings": 90.0,
        }

        flags = detect_red_flags(metrics, kpis)

        # Should have 9 flags total (8 implemented + excessive_leverage)
        assert len(flags) == 9

        # None should be detected for healthy company
        detected_flags = [f for f in flags if f.detected]
        assert len(detected_flags) == 0

    def test_negative_net_income_flag(self):
        """Test detection of negative net income."""
        metrics = {"pl_net_income": -50000.0}
        kpis = {}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "negative_net_income")

        assert flag.detected is True
        assert flag.severity == "high"
        assert "Net income: -50,000.00" in flag.details

    def test_positive_net_income_no_flag(self):
        """Test no flag for positive net income."""
        metrics = {"pl_net_income": 50000.0}
        kpis = {}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "negative_net_income")

        assert flag.detected is False

    def test_negative_equity_flag(self):
        """Test detection of negative equity (insolvency)."""
        metrics = {"bs_equity_total": -100000.0}
        kpis = {}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "negative_equity")

        assert flag.detected is True
        assert flag.severity == "high"
        assert "Equity: -100,000.00" in flag.details

    def test_high_debt_to_equity_flag(self):
        """Test detection of high debt-to-equity ratio."""
        metrics = {}
        kpis = {"debt_to_equity": 2.5}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "high_debt_to_equity")

        assert flag.detected is True
        assert flag.severity == "medium"
        assert "Debt-to-Equity: 2.50" in flag.details

    def test_acceptable_debt_to_equity_no_flag(self):
        """Test no flag for acceptable debt-to-equity ratio."""
        metrics = {}
        kpis = {"debt_to_equity": 1.5}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "high_debt_to_equity")

        assert flag.detected is False

    def test_low_equity_ratio_flag(self):
        """Test detection of low equity ratio."""
        metrics = {}
        kpis = {"equity_ratio": 15.0}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "low_equity_ratio")

        assert flag.detected is True
        assert flag.severity == "medium"
        assert "Equity Ratio: 15.00%" in flag.details

    def test_negative_operating_cash_flow_flag(self):
        """Test detection of negative operating cash flow."""
        metrics = {"cf_net_cash_from_operations": -20000.0}
        kpis = {}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "negative_operating_cash_flow")

        assert flag.detected is True
        assert flag.severity == "high"

    def test_poor_quality_of_earnings_flag(self):
        """Test detection of poor quality of earnings."""
        metrics = {"pl_net_income": 100000.0}  # Must be positive
        kpis = {"quality_of_earnings": 60.0}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "poor_quality_of_earnings")

        assert flag.detected is True
        assert flag.severity == "medium"
        assert "Quality of Earnings: 60.00%" in flag.details

    def test_quality_of_earnings_not_checked_for_losses(self):
        """Test that quality of earnings is not flagged when net income is negative."""
        metrics = {"pl_net_income": -10000.0}
        kpis = {"quality_of_earnings": 50.0}

        flags = detect_red_flags(metrics, kpis)

        # Flag should not be in the list when net income is not positive
        quality_flags = [f for f in flags if f.key == "poor_quality_of_earnings"]
        assert len(quality_flags) == 0

    def test_negative_profit_margin_flag(self):
        """Test detection of negative profit margin."""
        metrics = {}
        kpis = {"net_profit_margin": -5.0}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "negative_profit_margin")

        assert flag.detected is True
        assert flag.severity == "high"

    def test_low_roe_flag(self):
        """Test detection of low ROE."""
        metrics = {"bs_equity_total": 100000.0}  # Must be positive
        kpis = {"roe": 3.0}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "low_roe")

        assert flag.detected is True
        assert flag.severity == "low"
        assert "ROE: 3.00%" in flag.details

    def test_low_roe_not_flagged_for_negative_roe(self):
        """Test that negative ROE is not flagged as low ROE."""
        metrics = {"bs_equity_total": 100000.0}
        kpis = {"roe": -10.0}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "low_roe")

        assert flag.detected is False

    def test_excessive_leverage_flag(self):
        """Test detection of excessive leverage."""
        metrics = {
            "bs_total_liabilities": 850000.0,
            "bs_total_assets": 1000000.0,
        }
        kpis = {}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "excessive_leverage")

        assert flag.detected is True
        assert flag.severity == "high"
        assert "Debt Ratio: 85.00%" in flag.details

    def test_acceptable_leverage_no_flag(self):
        """Test no flag for acceptable leverage."""
        metrics = {
            "bs_total_liabilities": 600000.0,
            "bs_total_assets": 1000000.0,
        }
        kpis = {}

        flags = detect_red_flags(metrics, kpis)
        flag = next(f for f in flags if f.key == "excessive_leverage")

        assert flag.detected is False

    def test_multiple_flags_detected(self):
        """Test detection of multiple red flags simultaneously."""
        metrics = {
            "pl_net_income": -50000.0,
            "bs_equity_total": -20000.0,
            "cf_net_cash_from_operations": -10000.0,
            "bs_total_liabilities": 900000.0,
            "bs_total_assets": 1000000.0,
        }
        kpis = {
            "net_profit_margin": -10.0,
            "roe": -25.0,
        }

        flags = detect_red_flags(metrics, kpis)
        detected_flags = [f for f in flags if f.detected]

        # Should detect: negative_net_income, negative_equity, negative_operating_cash_flow,
        # negative_profit_margin, excessive_leverage
        assert len(detected_flags) >= 5


class TestGetRedFlagSummary:
    """Tests for get_red_flag_summary function."""

    def test_summary_with_no_flags_detected(self):
        """Test summary when no flags are detected."""
        metrics = {
            "pl_net_income": 100000.0,
            "bs_equity_total": 400000.0,
            "cf_net_cash_from_operations": 90000.0,
            "bs_total_liabilities": 300000.0,
            "bs_total_assets": 700000.0,
        }
        kpis = {
            "roe": 25.0,
            "debt_to_equity": 0.75,
            "net_profit_margin": 20.0,
            "equity_ratio": 57.14,
            "quality_of_earnings": 90.0,
        }

        flags = detect_red_flags(metrics, kpis)
        summary = get_red_flag_summary(flags)

        assert summary["total_flags"] == 9
        assert summary["detected"] == 0
        assert summary["high"] == 0
        assert summary["medium"] == 0
        assert summary["low"] == 0

    def test_summary_with_multiple_severity_levels(self):
        """Test summary with flags of different severity levels."""
        metrics = {
            "pl_net_income": -50000.0,  # high
            "bs_equity_total": 100000.0,
            "cf_net_cash_from_operations": 10000.0,
            "bs_total_liabilities": 150000.0,
            "bs_total_assets": 250000.0,
        }
        kpis = {
            "roe": 3.0,  # low
            "debt_to_equity": 1.5,
            "net_profit_margin": -10.0,  # high
            "equity_ratio": 40.0,
            "quality_of_earnings": 20.0,  # medium (but only if net_income > 0)
        }

        flags = detect_red_flags(metrics, kpis)
        summary = get_red_flag_summary(flags)

        assert summary["detected"] >= 2  # At least negative_net_income and negative_profit_margin
        assert summary["high"] >= 2
        assert summary["low"] >= 1  # low_roe

    def test_summary_structure(self):
        """Test that summary has expected structure."""
        metrics = {}
        kpis = {}

        flags = detect_red_flags(metrics, kpis)
        summary = get_red_flag_summary(flags)

        assert "total_flags" in summary
        assert "detected" in summary
        assert "high" in summary
        assert "medium" in summary
        assert "low" in summary
        assert isinstance(summary["total_flags"], int)
        assert isinstance(summary["detected"], int)
