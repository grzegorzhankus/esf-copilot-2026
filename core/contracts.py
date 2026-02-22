"""Data contracts and models for financial statement analysis.

This module defines immutable dataclasses used throughout the analysis pipeline
to ensure type safety and consistent data structures.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, Any, List, Optional


@dataclass(frozen=True)
class Metadata:
    """Analysis metadata.

    Attributes:
        schema_id: Full XML namespace URI.
        schema_id_slug: Filesystem-safe slug derived from schema_id.
        filename: Original uploaded filename.
        file_size_bytes: Size of the XML file in bytes.
        analyzed_at_utc: ISO 8601 timestamp of analysis.
        company_name: Name of the company from XML.
        period_from: Start of reporting period (YYYY-MM-DD).
        period_to: End of reporting period (YYYY-MM-DD).
    """
    schema_id: str
    schema_id_slug: str
    filename: str
    file_size_bytes: int
    analyzed_at_utc: str
    company_name: Optional[str] = None
    krs: Optional[str] = None
    nip: Optional[str] = None
    period_from: Optional[str] = None
    period_to: Optional[str] = None


@dataclass(frozen=True)
class MetricValue:
    """A single extracted financial metric.

    Attributes:
        key: Metric identifier (e.g., "bs_total_assets").
        value: Extracted numeric value, or None if not found.
        unit: Currency unit (e.g., "PLN", "PLN_thousands").
        source_ref: XPath expression used to extract this value.
    """
    key: str
    value: Optional[float]
    unit: str
    source_ref: str


@dataclass(frozen=True)
class Coverage:
    """Metric extraction coverage statistics.

    Attributes:
        percent: Percentage of metrics successfully extracted (0-100).
        present: List of metric keys that were found.
        missing: List of metric keys that could not be extracted.
    """
    percent: float = 0.0
    present: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class KPI:
    """Calculated financial Key Performance Indicator.

    Attributes:
        key: KPI identifier (e.g., "roa", "debt_to_equity").
        name: Human-readable KPI name.
        value: Calculated value, or None if cannot be calculated.
        unit: Unit of measurement (%, ratio, times).
        category: KPI category (Profitability, Leverage, Efficiency, Cash Flow).
        interpretation: Brief explanation of what the KPI means.
    """
    key: str
    name: str
    value: Optional[float]
    unit: str
    category: str
    interpretation: str


@dataclass(frozen=True)
class RedFlag:
    """Detected financial red flag warning.

    Attributes:
        key: Red flag identifier (e.g., "negative_net_income").
        title: Human-readable title.
        severity: Severity level ("high", "medium", "low").
        description: What this red flag indicates.
        detected: Whether this flag was triggered (True) or not (False).
        details: Specific details about the flag detection.
    """
    key: str
    title: str
    severity: str
    description: str
    detected: bool
    details: str


@dataclass(frozen=True)
class AnalysisResult:
    """Complete financial statement analysis result.

    This is the top-level container for all analysis outputs.

    Attributes:
        metadata: Analysis metadata and file information.
        metrics_base: List of extracted base metrics from XML.
        coverage: Extraction coverage statistics.
        kpis: List of calculated financial KPIs.
        red_flags: List of detected red flags.
        balance_sheet: Detailed balance sheet items with hierarchical structure.
        pl_statement: Detailed P&L items with hierarchical structure.
        cf_statement: Detailed Cash Flow items with hierarchical structure.
    """
    metadata: Metadata
    metrics_base: List[MetricValue] = field(default_factory=list)
    coverage: Coverage = field(default_factory=Coverage)
    kpis: List[KPI] = field(default_factory=list)
    red_flags: List[RedFlag] = field(default_factory=list)
    balance_sheet: List[Dict[str, Any]] = field(default_factory=list)
    pl_statement: List[Dict[str, Any]] = field(default_factory=list)
    cf_statement: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire analysis result to a dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """Reconstruct AnalysisResult from a dictionary (JSON).

        Args:
            data: Dictionary with analysis data (from JSON file).

        Returns:
            AnalysisResult object with all nested dataclasses reconstructed.
        """
        # Reconstruct Metadata
        metadata_data = data.get("metadata", {})
        metadata = Metadata(
            schema_id=metadata_data.get("schema_id", ""),
            schema_id_slug=metadata_data.get("schema_id_slug", ""),
            filename=metadata_data.get("filename", ""),
            file_size_bytes=metadata_data.get("file_size_bytes", 0),
            analyzed_at_utc=metadata_data.get("analyzed_at_utc", ""),
            company_name=metadata_data.get("company_name"),
            krs=metadata_data.get("krs"),
            nip=metadata_data.get("nip"),
            period_from=metadata_data.get("period_from"),
            period_to=metadata_data.get("period_to"),
        )

        # Reconstruct MetricValue list
        metrics_base = [
            MetricValue(
                key=m.get("key", ""),
                value=m.get("value"),
                unit=m.get("unit", "PLN"),
                source_ref=m.get("source_ref", "")
            )
            for m in data.get("metrics_base", [])
        ]

        # Reconstruct Coverage
        coverage_data = data.get("coverage", {})
        coverage = Coverage(
            percent=coverage_data.get("percent", 0.0),
            present=coverage_data.get("present", []),
            missing=coverage_data.get("missing", [])
        )

        # Reconstruct KPI list
        kpis = [
            KPI(
                key=k.get("key", ""),
                name=k.get("name", ""),
                value=k.get("value"),
                unit=k.get("unit", ""),
                category=k.get("category", ""),
                interpretation=k.get("interpretation", "")
            )
            for k in data.get("kpis", [])
        ]

        # Reconstruct RedFlag list
        red_flags = [
            RedFlag(
                key=r.get("key", ""),
                title=r.get("title", ""),
                severity=r.get("severity", ""),
                description=r.get("description", ""),
                detected=r.get("detected", False),
                details=r.get("details", "")
            )
            for r in data.get("red_flags", [])
        ]

        # Balance sheet, P&L, CF are already lists of dicts - no reconstruction needed
        balance_sheet = data.get("balance_sheet", [])
        pl_statement = data.get("pl_statement", [])
        cf_statement = data.get("cf_statement", [])

        return cls(
            metadata=metadata,
            metrics_base=metrics_base,
            coverage=coverage,
            kpis=kpis,
            red_flags=red_flags,
            balance_sheet=balance_sheet,
            pl_statement=pl_statement,
            cf_statement=cf_statement,
        )
