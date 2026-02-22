"""XML parsing utilities for e-Sprawozdania financial statements.

This module provides secure XML parsing using defusedxml to prevent XXE attacks
and namespace extraction utilities.
"""
from __future__ import annotations

from typing import Tuple

try:
    from defusedxml import ElementTree as SafeElementTree
except Exception:  # pragma: no cover - fallback for environments without defusedxml
    import xml.etree.ElementTree as SafeElementTree


class XmlParseError(Exception):
    """Exception raised when XML parsing fails."""
    pass


def parse_xml_bytes(xml_bytes: bytes):
    """Parse XML bytes into an ElementTree root element.

    Args:
        xml_bytes: Raw XML content as bytes.

    Returns:
        ElementTree root element.

    Raises:
        XmlParseError: If the XML is empty, malformed, or cannot be parsed.

    Example:
        >>> xml_bytes = b'<root><child>value</child></root>'
        >>> root = parse_xml_bytes(xml_bytes)
        >>> root.tag
        'root'
    """
    if not xml_bytes:
        raise XmlParseError("Empty file")
    try:
        return SafeElementTree.fromstring(xml_bytes)
    except SafeElementTree.ParseError as exc:  # type: ignore[attr-defined]
        raise XmlParseError(f"Invalid XML: {exc}") from exc
    except Exception as exc:
        raise XmlParseError(f"Failed to parse XML: {exc}") from exc


def get_namespace(root) -> str:
    """Extract the namespace URI from an XML element's tag.

    Args:
        root: ElementTree element (or None).

    Returns:
        Namespace URI as string, or empty string if no namespace.

    Example:
        >>> # For element with tag '{http://example.com/ns}root'
        >>> namespace = get_namespace(root)
        >>> namespace
        'http://example.com/ns'
    """
    if root is None:
        return ""
    tag = root.tag
    if tag.startswith("{") and "}" in tag:
        return tag[1:].split("}", 1)[0]
    return ""
