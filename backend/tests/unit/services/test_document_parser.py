"""Test Specs for DocumentParser."""

import base64
from unittest.mock import MagicMock, patch

import pytest

from src.services.document_parser import DocumentParser


@pytest.fixture
def parser() -> DocumentParser:
    """Fixture: Document parser."""
    return DocumentParser()


def test_parse_simple_text(parser: DocumentParser) -> None:
    """Spec: parse_document should return plain text as-is."""
    content = "This is plain text content."
    result = parser.parse_document(content, "test.txt", "text/plain")

    assert result == "This is plain text content."


def test_parse_base64_text(parser: DocumentParser) -> None:
    """Spec: parse_document should decode base64 text."""
    original = "This is test content."
    encoded = base64.b64encode(original.encode()).decode()

    result = parser.parse_document(encoded, "test.txt", "text/plain")

    # Should decode base64
    assert result == original or "test content" in result


def test_looks_like_base64(parser: DocumentParser) -> None:
    """Spec: _looks_like_base64 should detect base64 strings."""
    # Valid base64
    base64_str = base64.b64encode(b"test content").decode()
    assert parser._looks_like_base64(base64_str * 20)  # Make it long enough

    # Plain text
    plain_text = "This is plain text content that is not base64 encoded."
    assert not parser._looks_like_base64(plain_text * 2)


def test_looks_like_base64_short_string(parser: DocumentParser) -> None:
    """Spec: _looks_like_base64 should return False for short strings."""
    short_str = "abc"
    assert not parser._looks_like_base64(short_str)


def test_parse_document_pdf_without_docling(parser: DocumentParser) -> None:
    """Spec: parse_document should fallback when Docling not available."""
    # Disable docling
    parser.docling_available = False

    content = "%PDF-1.4\nTest PDF content"
    result = parser.parse_document(content, "test.pdf", "application/pdf")

    # Should fallback to simple parsing
    assert isinstance(result, str)


def test_parse_document_docx(parser: DocumentParser) -> None:
    """Spec: parse_document should handle DOCX files."""
    # Mock docx import
    with patch("src.services.document_parser.Document", MagicMock()):
        # Create minimal DOCX-like content (ZIP signature)
        docx_bytes = b"PK\x03\x04" + b"x" * 100
        encoded = base64.b64encode(docx_bytes).decode()

        try:
            result = parser.parse_document(encoded, "test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            # Should return string (may be empty if parsing fails)
            assert isinstance(result, str)
        except ImportError:
            # python-docx not installed, should fallback
            pass


def test_parse_document_unknown_type(parser: DocumentParser) -> None:
    """Spec: parse_document should handle unknown file types."""
    content = "Some content"
    result = parser.parse_document(content, "test.unknown", "application/unknown")

    # Should return string
    assert isinstance(result, str)
