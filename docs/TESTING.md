# Testing Guide

## Overview

The esf-copilot-2026 project now includes a comprehensive test suite covering all core modules with 66 tests and 100% coverage for critical components.

## Running Tests

### Install Dependencies

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=core --cov-report=term-missing --cov-report=html
```

### Run Specific Test Files

```bash
pytest tests/test_kpi_calculator.py -v
pytest tests/test_red_flags.py -v
```

## Test Coverage

### Current Coverage: 24% overall, 100% for core business logic

**Fully Tested Modules (100% coverage):**
- `core/kpi_calculator.py` - All 10 KPI calculations tested
- `core/red_flags.py` - All 9 red flag detection rules tested

**High Coverage (>90%):**
- `core/mapping_engine.py` - 91% coverage
- `core/contracts.py` - 98% coverage
- `core/xml_loader.py` - 91% coverage
- `core/schema_detector.py` - 96% coverage

**Not Yet Tested:**
- Streamlit UI components (app/pages/)
- Export modules (excel_export.py, pdf_export.py)
- Visualization modules
- LLM integration
- Forecasting module

## Test Structure

```
tests/
├── __init__.py
├── test_xml_loader.py       (10 tests)
├── test_schema_detector.py  (11 tests)
├── test_mapping_engine.py   (10 tests)
├── test_kpi_calculator.py   (16 tests)
└── test_red_flags.py        (19 tests)
```

## Test Categories

### XML Parsing Tests
- Valid/invalid XML handling
- Namespace extraction
- Error handling for malformed input
- Special character handling

### Schema Detection Tests
- Schema ID extraction from namespaces
- Slug generation for Polish MF schemas
- Generic URL to slug conversion
- Special character sanitization

### Mapping Engine Tests
- XPath-based metric extraction
- Fallback XPath handling
- Sum transform aggregation
- Decimal separator conversion (comma to dot)
- Whitespace handling
- Coverage calculation

### KPI Calculator Tests
- All 10 KPI calculations verified:
  - Profitability: ROA, ROE, Net Profit Margin, EBIT Margin
  - Leverage: Debt-to-Equity, Equity Ratio, Debt Ratio
  - Efficiency: Asset Turnover
  - Cash Flow: OCF to Revenue, Quality of Earnings
- Division by zero handling
- Missing data handling
- Negative value calculations

### Red Flags Tests
- All 9 red flags tested:
  - High severity: Negative Net Income, Negative Equity, Negative OCF, Excessive Leverage, Negative Profit Margin
  - Medium severity: High Debt-to-Equity, Low Equity Ratio, Poor Earnings Quality
  - Low severity: Low ROE
- Detection thresholds verified
- Summary statistics tested

## Continuous Integration

Tests are configured to run automatically via pytest. To integrate with CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=core --cov-report=xml
```

## Writing New Tests

### Test File Template

```python
"""Tests for core.module_name."""
from __future__ import annotations

import pytest

from core.module_name import function_to_test


class TestFunctionName:
    """Tests for function_to_test."""

    def test_normal_case(self):
        """Test normal operation."""
        result = function_to_test(input_data)
        assert result == expected_value

    def test_edge_case(self):
        """Test edge case."""
        result = function_to_test(edge_case_data)
        assert result == expected_edge_value

    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ExpectedError):
            function_to_test(invalid_data)
```

### Best Practices

1. **Test one thing per test** - Keep tests focused and specific
2. **Use descriptive names** - Test names should explain what they verify
3. **Include docstrings** - Explain the purpose of each test
4. **Test edge cases** - Don't just test the happy path
5. **Test error conditions** - Verify proper error handling
6. **Use fixtures sparingly** - Keep tests self-contained when possible

## Coverage Goals

- **Core business logic**: Target 100% coverage ✅ ACHIEVED
- **Utility modules**: Target 90%+ coverage ✅ ACHIEVED
- **Integration points**: Target 80%+ coverage (pending)
- **UI components**: Target 60%+ coverage (pending)

## Known Gaps

1. **Integration tests** - Need tests that verify end-to-end analysis pipeline
2. **UI tests** - Streamlit pages not yet tested
3. **Export tests** - Excel/PDF generation not yet tested
4. **LLM tests** - Ollama integration not yet tested (requires mocking)
5. **Forecasting tests** - Forecasting module not yet tested

## Next Steps

- [ ] Add integration tests for complete analysis workflow
- [ ] Add tests for export modules (Excel, PDF)
- [ ] Add tests for forecasting module
- [ ] Mock LLM responses for chat testing
- [ ] Set up automated CI/CD pipeline
- [ ] Add performance/benchmark tests
