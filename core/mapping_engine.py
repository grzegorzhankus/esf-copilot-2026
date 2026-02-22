"""XPath-based metric extraction engine for Polish financial statements.

This module handles loading of schema-specific mapping configurations and
extracting financial metrics from XML documents using XPath expressions.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import yaml

from core.contracts import Coverage, MetricValue


@dataclass(frozen=True)
class MappingSpec:
    """Schema mapping specification.

    Attributes:
        schema_id: Full namespace URI of the XML schema.
        unit: Currency unit (e.g., "PLN", "PLN_thousands").
        metrics: Dictionary mapping metric keys to extraction specs.
    """
    schema_id: str
    unit: str
    metrics: Dict[str, Dict[str, object]]


def load_mapping(schema_slug: str, base_dir: Path | str = "configs_mappings") -> Optional[MappingSpec]:
    """Load a mapping configuration file for a given schema slug.

    Supports two formats:
    - List-based: metrics is a list of dicts with 'key' field (new format)
    - Dict-based: metrics is a dict keyed by metric name (legacy format)

    Args:
        schema_slug: Schema slug identifier.
        base_dir: Base directory containing mapping subdirectories.

    Returns:
        MappingSpec object if mapping file exists, None otherwise.

    Example:
        >>> mapping = load_mapping("mf_2025_jednostka_inna_wtysiacach")
        >>> mapping.unit
        'PLN_thousands'
    """
    base_path = Path(base_dir)

    # Try multiple directories for mapping lookup
    search_paths = [
        base_path / schema_slug / "mapping_v1.yaml",
        Path("configs/mappings") / schema_slug / "mapping_v1.yaml",
        base_path / "_default" / "mapping_v1.yaml",
    ]

    mapping_path = None
    for path in search_paths:
        if path.exists():
            mapping_path = path
            break

    if mapping_path is None:
        return None

    data = yaml.safe_load(mapping_path.read_text(encoding="utf-8")) or {}

    # Handle both list-based and dict-based metrics formats
    raw_metrics = data.get("metrics", {})
    if isinstance(raw_metrics, list):
        # Convert list format to dict format for internal use
        metrics_dict = {}
        for item in raw_metrics:
            key = item.get("key")
            if key:
                metrics_dict[key] = {
                    "xpaths": item.get("xpaths", []),
                    "transform": item.get("transform", "first"),
                    "required": item.get("required", False),
                }
        raw_metrics = metrics_dict

    # Determine unit: from mapping file, or auto-detect from schema_slug
    unit = data.get("unit", "")
    if unit in ("", "PLN") and "wtysiacach" in schema_slug.lower():
        # Schema indicates values are in thousands (e.g., JednostkaInnaWTysiacach)
        unit = "PLN_thousands"

    return MappingSpec(
        schema_id=data.get("schema_id", ""),
        unit=unit,
        metrics=raw_metrics,
    )


def compute_metrics(root, mapping: MappingSpec) -> Tuple[List[MetricValue], Coverage]:
    """Extract all metrics from XML root using the provided mapping specification.

    Args:
        root: ElementTree root element.
        mapping: MappingSpec containing XPath expressions for each metric.

    Returns:
        Tuple of (metrics_list, coverage_info) where metrics_list contains
        MetricValue objects and coverage_info tracks extraction success rate.

    Example:
        >>> metrics, coverage = compute_metrics(root, mapping)
        >>> coverage.percent
        87.5
    """
    metrics_base: List[MetricValue] = []
    for metric_key in sorted(mapping.metrics.keys()):
        spec = mapping.metrics.get(metric_key, {})
        xpaths = spec.get("xpaths", []) or []
        transform = spec.get("transform", "first")
        value, source_ref = _extract_metric(root, xpaths, transform)
        metrics_base.append(
            MetricValue(
                key=metric_key,
                value=value,
                unit=mapping.unit,
                source_ref=source_ref,
            )
        )

    present = [m.key for m in metrics_base if m.value is not None]
    missing = [m.key for m in metrics_base if m.value is None]
    total = len(metrics_base)
    percent = round((len(present) / total) * 100.0, 2) if total else 0.0
    coverage = Coverage(percent=percent, present=present, missing=missing)
    return metrics_base, coverage


def _extract_metric(root, xpaths: Iterable[str], transform: str) -> Tuple[Optional[float], str]:
    if transform == "sum":
        values: List[float] = []
        used_paths: List[str] = []
        for xpath in xpaths:
            extracted = _extract_values(root, xpath)
            if extracted:
                values.extend(extracted)
                used_paths.append(xpath)
        if not values:
            return None, ""
        return sum(values), ";".join(used_paths)

    for xpath in xpaths:
        extracted = _extract_values(root, xpath)
        if extracted:
            return extracted[0], xpath
    return None, ""


def _extract_values(root, xpath: str) -> List[float]:
    nodes = _find_nodes_by_path(root, xpath)
    values: List[float] = []
    for node in nodes:
        if node.text is None:
            continue
        raw = node.text.strip().replace(" ", "").replace(",", ".")
        if not raw:
            continue
        try:
            values.append(float(raw))
        except ValueError:
            continue
    return values


def _find_nodes_by_path(root, path: str):
    segments = [seg for seg in path.strip("/").split("/") if seg]
    if not segments:
        return []
    current = [root]
    for segment in segments:
        next_nodes = []
        for node in current:
            for child in list(node):
                if _localname(child.tag) == segment:
                    next_nodes.append(child)
        current = next_nodes
        if not current:
            break
    return current


def _localname(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag
