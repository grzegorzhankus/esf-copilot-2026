"""Tests for core.mapping_engine module."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from defusedxml import ElementTree as SafeElementTree

from core.mapping_engine import (
    MappingSpec,
    compute_metrics,
    load_mapping,
)


class TestLoadMapping:
    """Tests for load_mapping function."""

    def test_load_existing_mapping(self):
        """Test loading an existing mapping configuration."""
        # Use actual mapping file from project
        mapping = load_mapping("mf_2025_jednostka_inna", base_dir="configs/mappings")
        assert mapping is not None
        assert isinstance(mapping, MappingSpec)
        assert mapping.unit == "PLN"
        assert len(mapping.metrics) > 0

    def test_load_nonexistent_mapping_returns_none(self):
        """Test that loading non-existent mapping returns None."""
        mapping = load_mapping("nonexistent_schema", base_dir="configs/mappings")
        assert mapping is None

    def test_load_mapping_with_custom_base_dir(self, tmp_path):
        """Test loading mapping from custom base directory."""
        # Create temporary mapping file
        mapping_dir = tmp_path / "test_schema"
        mapping_dir.mkdir()
        mapping_file = mapping_dir / "mapping_v1.yaml"
        mapping_file.write_text("""
version: v1
schema_id: http://test.com/schema
unit: EUR
metrics:
  test_metric:
    xpaths:
      - /Root/Value
    transform: first
""")

        mapping = load_mapping("test_schema", base_dir=tmp_path)
        assert mapping is not None
        assert mapping.unit == "EUR"
        assert "test_metric" in mapping.metrics


class TestComputeMetrics:
    """Tests for compute_metrics function."""

    def test_compute_metrics_with_simple_xpath(self):
        """Test computing metrics with simple XPath."""
        xml_str = """
        <Root>
            <TotalAssets>100000</TotalAssets>
            <Revenue>50000</Revenue>
        </Root>
        """
        root = SafeElementTree.fromstring(xml_str)

        mapping = MappingSpec(
            schema_id="test",
            unit="PLN",
            metrics={
                "bs_total_assets": {
                    "xpaths": ["TotalAssets"],
                    "transform": "first"
                },
                "pl_revenue": {
                    "xpaths": ["Revenue"],
                    "transform": "first"
                }
            }
        )

        metrics, coverage = compute_metrics(root, mapping)

        assert len(metrics) == 2
        assert metrics[0].key == "bs_total_assets"
        assert metrics[0].value == 100000.0
        assert metrics[1].key == "pl_revenue"
        assert metrics[1].value == 50000.0
        assert coverage.percent == 100.0

    def test_compute_metrics_with_missing_values(self):
        """Test computing metrics when some values are missing."""
        xml_str = """
        <Root>
            <TotalAssets>100000</TotalAssets>
        </Root>
        """
        root = SafeElementTree.fromstring(xml_str)

        mapping = MappingSpec(
            schema_id="test",
            unit="PLN",
            metrics={
                "bs_total_assets": {
                    "xpaths": ["TotalAssets"],
                    "transform": "first"
                },
                "pl_revenue": {
                    "xpaths": ["Revenue"],
                    "transform": "first"
                }
            }
        )

        metrics, coverage = compute_metrics(root, mapping)

        assert len(metrics) == 2
        assert metrics[0].value == 100000.0
        assert metrics[1].value is None
        assert coverage.percent == 50.0
        assert "bs_total_assets" in coverage.present
        assert "pl_revenue" in coverage.missing

    def test_compute_metrics_with_sum_transform(self):
        """Test computing metrics using sum transform."""
        xml_str = """
        <Root>
            <Item1>1000</Item1>
            <Item2>2000</Item2>
            <Item3>3000</Item3>
        </Root>
        """
        root = SafeElementTree.fromstring(xml_str)

        mapping = MappingSpec(
            schema_id="test",
            unit="PLN",
            metrics={
                "total": {
                    "xpaths": ["Item1", "Item2", "Item3"],
                    "transform": "sum"
                }
            }
        )

        metrics, coverage = compute_metrics(root, mapping)

        assert len(metrics) == 1
        assert metrics[0].value == 6000.0
        assert coverage.percent == 100.0

    def test_compute_metrics_with_nested_xpath(self):
        """Test computing metrics with nested XPath."""
        xml_str = """
        <Root>
            <Bilans>
                <Aktywa>
                    <SumaAktywow>150000</SumaAktywow>
                </Aktywa>
            </Bilans>
        </Root>
        """
        root = SafeElementTree.fromstring(xml_str)

        mapping = MappingSpec(
            schema_id="test",
            unit="PLN",
            metrics={
                "bs_total_assets": {
                    "xpaths": ["Bilans/Aktywa/SumaAktywow"],
                    "transform": "first"
                }
            }
        )

        metrics, coverage = compute_metrics(root, mapping)

        assert len(metrics) == 1
        assert metrics[0].value == 150000.0

    def test_compute_metrics_with_decimal_separator(self):
        """Test that values with comma decimal separator are parsed correctly."""
        xml_str = """
        <Root>
            <Value>1234,56</Value>
        </Root>
        """
        root = SafeElementTree.fromstring(xml_str)

        mapping = MappingSpec(
            schema_id="test",
            unit="PLN",
            metrics={
                "test_value": {
                    "xpaths": ["Value"],
                    "transform": "first"
                }
            }
        )

        metrics, coverage = compute_metrics(root, mapping)

        assert len(metrics) == 1
        assert metrics[0].value == 1234.56

    def test_compute_metrics_with_whitespace_in_values(self):
        """Test that values with whitespace are parsed correctly."""
        xml_str = """
        <Root>
            <Value>  100 000.50  </Value>
        </Root>
        """
        root = SafeElementTree.fromstring(xml_str)

        mapping = MappingSpec(
            schema_id="test",
            unit="PLN",
            metrics={
                "test_value": {
                    "xpaths": ["Value"],
                    "transform": "first"
                }
            }
        )

        metrics, coverage = compute_metrics(root, mapping)

        assert len(metrics) == 1
        assert metrics[0].value == 100000.50

    def test_compute_metrics_with_fallback_xpaths(self):
        """Test that fallback XPaths are used when first one fails."""
        xml_str = """
        <Root>
            <AlternativeValue>99999</AlternativeValue>
        </Root>
        """
        root = SafeElementTree.fromstring(xml_str)

        mapping = MappingSpec(
            schema_id="test",
            unit="PLN",
            metrics={
                "test_value": {
                    "xpaths": ["PreferredValue", "AlternativeValue"],
                    "transform": "first"
                }
            }
        )

        metrics, coverage = compute_metrics(root, mapping)

        assert len(metrics) == 1
        assert metrics[0].value == 99999.0
        assert metrics[0].source_ref == "AlternativeValue"
