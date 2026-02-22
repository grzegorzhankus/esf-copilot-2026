"""Schema detection and slug generation for Polish financial statements.

This module provides utilities to detect the XML schema namespace from
e-Sprawozdania files and convert schema IDs into filesystem-safe slugs
for mapping file lookup.
"""
from __future__ import annotations

import re

from core.xml_loader import get_namespace


def detect_schema_id(root) -> str:
    """Detect the schema ID (namespace URI) from an XML root element.

    Args:
        root: ElementTree root element.

    Returns:
        Schema ID as string, or "unknown" if no namespace found.

    Example:
        >>> root = parse_xml_bytes(xml_bytes)
        >>> schema_id = detect_schema_id(root)
        >>> schema_id
        'http://www.mf.gov.pl/schematy/SF/.../2025/JednostkaInna'
    """
    namespace = get_namespace(root)
    if not namespace:
        return "unknown"
    return namespace


def schema_id_to_slug(schema_id: str) -> str:
    """Convert a schema ID (namespace URI) into a filesystem-safe slug.

    This function generates slug names used for mapping file lookup in the
    configs/mappings/ directory. The slug format is:
    mf_YYYY_jednostka_type (e.g., mf_2025_jednostka_inna_wtysiacach)

    Args:
        schema_id: Full schema namespace URI.

    Returns:
        Slug string suitable for directory names.

    Example:
        >>> schema_id = "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2025/01/01/JednostkaInnaWTysiacach"
        >>> slug = schema_id_to_slug(schema_id)
        >>> slug
        'mf_2025_jednostka_inna_wtysiacach'
    """
    if not schema_id or schema_id == "unknown":
        return "unknown"

    # Extract year from schema_id (e.g., /2025/)
    year_match = re.search(r"/(20\d{2})/", schema_id)
    year = year_match.group(1) if year_match else "unknown"

    # Extract the last segment (entity type, e.g., JednostkaInnaWTysiacach)
    last_segment = schema_id.rstrip("/").split("/")[-1]

    # Convert CamelCase to lowercase with underscores
    # e.g., JednostkaInnaWTysiacach -> jednostka_inna_wtysiacach
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", last_segment).lower()

    # Build slug: mf_YYYY_type
    slug = f"mf_{year}_{words}"

    # Clean up any double underscores
    slug = re.sub(r"_+", "_", slug).strip("_")

    return slug
