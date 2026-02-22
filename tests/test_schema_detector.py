"""Tests for core.schema_detector module."""
from __future__ import annotations

import pytest
from defusedxml import ElementTree as SafeElementTree

from core.schema_detector import detect_schema_id, schema_id_to_slug


class TestDetectSchemaId:
    """Tests for detect_schema_id function."""

    def test_detect_schema_id_with_namespace(self):
        """Test detecting schema ID from element with namespace."""
        xml_bytes = b'<?xml version="1.0"?><root xmlns="http://example.com/schema/2025"></root>'
        root = SafeElementTree.fromstring(xml_bytes)
        schema_id = detect_schema_id(root)
        assert schema_id == "http://example.com/schema/2025"

    def test_detect_schema_id_without_namespace(self):
        """Test detecting schema ID from element without namespace returns unknown."""
        xml_bytes = b'<?xml version="1.0"?><root></root>'
        root = SafeElementTree.fromstring(xml_bytes)
        schema_id = detect_schema_id(root)
        assert schema_id == "unknown"

    def test_detect_schema_id_polish_mf_schema(self):
        """Test detecting Polish Ministry of Finance schema."""
        xml_bytes = b'<?xml version="1.0"?><root xmlns="http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2025/JednostkaInna"></root>'
        root = SafeElementTree.fromstring(xml_bytes)
        schema_id = detect_schema_id(root)
        assert "mf.gov.pl" in schema_id
        assert "2025" in schema_id


class TestSchemaIdToSlug:
    """Tests for schema_id_to_slug function."""

    def test_convert_empty_string_to_slug(self):
        """Test converting empty string returns unknown."""
        slug = schema_id_to_slug("")
        assert slug == "unknown"

    def test_convert_unknown_to_slug(self):
        """Test converting 'unknown' returns unknown."""
        slug = schema_id_to_slug("unknown")
        assert slug == "unknown"

    def test_convert_mf_schema_jednostka_inna(self):
        """Test converting Polish MF JednostkaInna schema to slug."""
        schema_id = "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2025/01/01/JednostkaInnaWZlotych"
        slug = schema_id_to_slug(schema_id)
        assert slug == "http_www.mf.gov.pl_schematy_sf_definicjetypysprawozdaniafinansowe_2025_01_01_jednostkainnawzlotych"

    def test_convert_mf_schema_jednostka_mala(self):
        """Test converting Polish MF JednostkaMala schema to slug."""
        schema_id = "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2025/01/01/JednostkaMalaWZlotych"
        slug = schema_id_to_slug(schema_id)
        assert slug == "http_www.mf.gov.pl_schematy_sf_definicjetypysprawozdaniafinansowe_2025_01_01_jednostkamalawzlotych"

    def test_convert_mf_schema_wtysiacach(self):
        """Test converting Polish MF schema with 'WTysiacach' suffix."""
        schema_id = "http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2025/01/01/JednostkaInnaWTysiacach"
        slug = schema_id_to_slug(schema_id)
        assert slug == "http_www.mf.gov.pl_schematy_sf_definicjetypysprawozdaniafinansowe_2025_01_01_jednostkainnawtysiacach"

    def test_convert_generic_url_to_slug(self):
        """Test converting generic URL to slug."""
        schema_id = "https://example.com/schema/2025/MySchema"
        slug = schema_id_to_slug(schema_id)
        # https is normalized to http prefix
        assert slug.startswith("http_example.com")
        assert "myschema" in slug.lower()

    def test_convert_slug_removes_special_characters(self):
        """Test that slug removes special characters."""
        schema_id = "http://example.com/my-schema!@#$%test"
        slug = schema_id_to_slug(schema_id)
        assert "!" not in slug
        assert "@" not in slug
        assert "#" not in slug
        # Slug contains alphanumeric, underscores, and dots
        assert all(c.isalnum() or c in "_." for c in slug)

    def test_convert_preserves_domain_dots(self):
        """Test that domain dots are preserved in slug."""
        schema_id = "http://www.mf.gov.pl/schematy/SF/Test"
        slug = schema_id_to_slug(schema_id)
        assert "www.mf.gov.pl" in slug

    def test_convert_urn_format(self):
        """Test converting URN-style identifier to slug."""
        schema_id = "urn:esf:demo:v1"
        slug = schema_id_to_slug(schema_id)
        assert slug == "urn_esf_demo_v1"
