from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Tuple
from xml.etree.ElementTree import Element

from core.contracts import AnalysisResult, Coverage, Metadata
from core.kpi_calculator import calculate_kpis
from core.mapping_engine import compute_metrics, load_mapping
from core.red_flags import detect_red_flags
from core.schema_detector import detect_schema_id, schema_id_to_slug
from core.xml_loader import parse_xml_bytes
from core.balance_sheet_extractor import extract_balance_sheet, balance_sheet_to_dict
from core.pl_extractor import extract_pl_statement, pl_to_dict
from core.cf_extractor import extract_cash_flow, cf_to_dict


def _extract_text_by_local_name(root: Element, local_name: str) -> Optional[str]:
    """Extract text from element by local name (ignoring namespace)."""
    for elem in root.iter():
        tag = elem.tag
        # Strip namespace: {http://...}LocalName -> LocalName
        if "}" in tag:
            tag = tag.split("}")[1]
        if tag == local_name and elem.text:
            return elem.text.strip()
    return None


def _extract_company_metadata(root: Element) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Extract company name, identifiers and reporting period from XML.

    Returns:
        Tuple of (company_name, krs, nip, period_from, period_to)
    """
    company_name = _extract_text_by_local_name(root, "NazwaFirmy")
    period_from = _extract_text_by_local_name(root, "OkresOd")
    period_to = _extract_text_by_local_name(root, "OkresDo")

    # Extract KRS (P_1E) and NIP (P_1D)
    krs = _extract_text_by_local_name(root, "P_1E")
    nip = _extract_text_by_local_name(root, "P_1D")

    return company_name, krs, nip, period_from, period_to


def analyze_xml_bytes(xml_bytes: bytes, filename: str) -> AnalysisResult:
    root = parse_xml_bytes(xml_bytes)
    schema_id = detect_schema_id(root)
    schema_id_slug = schema_id_to_slug(schema_id)
    analyzed_at_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Extract company metadata from XML
    company_name, krs, nip, period_from, period_to = _extract_company_metadata(root)

    # Extract detailed balance sheet
    balance_sheet_items = extract_balance_sheet(root)
    balance_sheet_data = balance_sheet_to_dict(balance_sheet_items)

    # Extract detailed P&L statement
    pl_items = extract_pl_statement(root)
    pl_statement_data = pl_to_dict(pl_items)

    # Extract detailed Cash Flow statement
    cf_items = extract_cash_flow(root)
    cf_statement_data = cf_to_dict(cf_items)

    mapping = load_mapping(schema_id_slug)
    metrics_base = []
    coverage = Coverage()
    kpis = []
    red_flags = []

    if mapping:
        metrics_base, coverage = compute_metrics(root, mapping)
        # Calculate KPIs from base metrics
        metrics_dict = {m.key: m.value for m in metrics_base}
        kpis = calculate_kpis(metrics_dict)
        # Detect red flags
        kpis_dict = {k.key: k.value for k in kpis}
        red_flags = detect_red_flags(metrics_dict, kpis_dict)

    metadata = Metadata(
        schema_id=schema_id,
        schema_id_slug=schema_id_slug,
        filename=filename,
        file_size_bytes=len(xml_bytes),
        analyzed_at_utc=analyzed_at_utc,
        company_name=company_name,
        krs=krs,
        nip=nip,
        period_from=period_from,
        period_to=period_to,
    )
    return AnalysisResult(
        metadata=metadata,
        metrics_base=metrics_base,
        coverage=coverage,
        kpis=kpis,
        red_flags=red_flags,
        balance_sheet=balance_sheet_data,
        pl_statement=pl_statement_data,
        cf_statement=cf_statement_data,
    )
