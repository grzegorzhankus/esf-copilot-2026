"""Tests for core.xml_loader module."""
from __future__ import annotations

import pytest
from defusedxml import ElementTree as SafeElementTree

from core.xml_loader import XmlParseError, get_namespace, parse_xml_bytes


class TestParseXmlBytes:
    """Tests for parse_xml_bytes function."""

    def test_parse_valid_xml(self):
        """Test parsing valid XML bytes."""
        xml_bytes = b'<?xml version="1.0"?><root><child>value</child></root>'
        root = parse_xml_bytes(xml_bytes)
        assert root is not None
        assert root.tag == "root"
        assert root.find("child").text == "value"

    def test_parse_xml_with_namespace(self):
        """Test parsing XML with namespace."""
        xml_bytes = b'<?xml version="1.0"?><ns:root xmlns:ns="http://example.com"><ns:child>value</ns:child></ns:root>'
        root = parse_xml_bytes(xml_bytes)
        assert root is not None
        assert "http://example.com" in root.tag

    def test_parse_empty_bytes_raises_error(self):
        """Test that empty bytes raises XmlParseError."""
        with pytest.raises(XmlParseError, match="Empty file"):
            parse_xml_bytes(b"")

    def test_parse_invalid_xml_raises_error(self):
        """Test that invalid XML raises XmlParseError."""
        xml_bytes = b"<root><unclosed>"
        with pytest.raises(XmlParseError, match="Invalid XML"):
            parse_xml_bytes(xml_bytes)

    def test_parse_non_xml_bytes_raises_error(self):
        """Test that non-XML content raises XmlParseError."""
        xml_bytes = b"This is not XML at all"
        with pytest.raises(XmlParseError, match="Invalid XML"):
            parse_xml_bytes(xml_bytes)

    def test_parse_xml_with_special_characters(self):
        """Test parsing XML with special characters."""
        xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?><root><child>Test &amp; &lt;special&gt;</child></root>'
        root = parse_xml_bytes(xml_bytes)
        assert root is not None
        assert root.find("child").text == "Test & <special>"


class TestGetNamespace:
    """Tests for get_namespace function."""

    def test_get_namespace_from_namespaced_element(self):
        """Test extracting namespace from element with namespace."""
        xml_bytes = b'<?xml version="1.0"?><ns:root xmlns:ns="http://example.com/ns"></ns:root>'
        root = SafeElementTree.fromstring(xml_bytes)
        namespace = get_namespace(root)
        assert namespace == "http://example.com/ns"

    def test_get_namespace_from_element_without_namespace(self):
        """Test extracting namespace from element without namespace."""
        xml_bytes = b'<?xml version="1.0"?><root></root>'
        root = SafeElementTree.fromstring(xml_bytes)
        namespace = get_namespace(root)
        assert namespace == ""

    def test_get_namespace_from_none_returns_empty(self):
        """Test that None element returns empty string."""
        namespace = get_namespace(None)
        assert namespace == ""

    def test_get_namespace_complex_uri(self):
        """Test extracting complex namespace URI."""
        xml_bytes = b'<?xml version="1.0"?><root xmlns="http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2025/JednostkaInna"></root>'
        root = SafeElementTree.fromstring(xml_bytes)
        namespace = get_namespace(root)
        assert namespace == "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2025/JednostkaInna"
