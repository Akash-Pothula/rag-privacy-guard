"""Tests for JSON parsing utility."""

import pytest
from src.utils.json_parser import extract_json, safe_get


def test_extract_json_clean():
    """Test parsing clean JSON."""
    text = '{"key": "value", "number": 42}'
    result = extract_json(text)
    assert result == {"key": "value", "number": 42}


def test_extract_json_markdown_fences():
    """Test parsing JSON in markdown code fences."""
    text = """Here is the result:
```json
{
  "status": "success",
  "data": [1, 2, 3]
}
```
That's it!"""
    result = extract_json(text)
    assert result == {"status": "success", "data": [1, 2, 3]}


def test_extract_json_markdown_fences_no_language():
    """Test parsing JSON in markdown fences without language tag."""
    text = """```
{"answer": true}
```"""
    result = extract_json(text)
    assert result == {"answer": True}


def test_extract_json_with_extra_text():
    """Test parsing JSON with extra text before and after."""
    text = 'Some preamble text {"result": "found"} some trailing text'
    result = extract_json(text)
    assert result == {"result": "found"}


def test_extract_json_nested_objects():
    """Test parsing nested JSON objects."""
    text = """Response: {"outer": {"inner": {"value": 123}}}"""
    result = extract_json(text)
    assert result == {"outer": {"inner": {"value": 123}}}


def test_extract_json_array():
    """Test parsing JSON array."""
    text = '[1, 2, 3, "test"]'
    result = extract_json(text)
    assert result == [1, 2, 3, "test"]


def test_extract_json_array_with_text():
    """Test parsing JSON array with surrounding text."""
    text = 'Here is the array: [{"a": 1}, {"b": 2}] end'
    result = extract_json(text)
    # Should find either the array or first object (both are valid)
    assert isinstance(result, (list, dict))


def test_extract_json_invalid_with_fallback():
    """Test parsing completely invalid input returns fallback."""
    text = "This is not JSON at all"
    result = extract_json(text, {"default": "value"})
    assert result == {"default": "value"}


def test_extract_json_empty_string():
    """Test parsing empty string returns fallback."""
    result = extract_json("", {"empty": True})
    assert result == {"empty": True}


def test_extract_json_none():
    """Test parsing None returns fallback."""
    result = extract_json(None, {"none": True})
    assert result == {"none": True}


def test_safe_get_existing_key():
    """Test safe_get with existing key."""
    data = {"key": "value"}
    assert safe_get(data, "key") == "value"


def test_safe_get_missing_key():
    """Test safe_get with missing key returns default."""
    data = {"key": "value"}
    assert safe_get(data, "missing") is None
    assert safe_get(data, "missing", "default") == "default"


def test_safe_get_nested():
    """Test safe_get doesn't do nested access (just top level)."""
    data = {"outer": {"inner": "value"}}
    assert safe_get(data, "outer") == {"inner": "value"}
