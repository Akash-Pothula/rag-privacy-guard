"""Tests for severity computation utilities."""

import pytest
from src.agents.models.evaluation import Severity
from src.utils.severity import (
    max_severity, severity_from_string, compute_overall_severity
)


def test_max_severity_single():
    """Test max_severity with single severity."""
    result = max_severity([Severity.HIGH])
    assert result == Severity.HIGH


def test_max_severity_multiple():
    """Test max_severity with multiple severities."""
    severities = [Severity.LOW, Severity.HIGH, Severity.MEDIUM]
    result = max_severity(severities)
    assert result == Severity.HIGH


def test_max_severity_with_critical():
    """Test max_severity returns CRITICAL when present."""
    severities = [Severity.MEDIUM, Severity.CRITICAL, Severity.HIGH]
    result = max_severity(severities)
    assert result == Severity.CRITICAL


def test_max_severity_empty_list():
    """Test max_severity with empty list returns PASS."""
    result = max_severity([])
    assert result == Severity.PASS


def test_severity_from_string_valid():
    """Test severity_from_string with valid strings."""
    assert severity_from_string("PASS") == Severity.PASS
    assert severity_from_string("LOW") == Severity.LOW
    assert severity_from_string("MEDIUM") == Severity.MEDIUM
    assert severity_from_string("HIGH") == Severity.HIGH
    assert severity_from_string("CRITICAL") == Severity.CRITICAL


def test_severity_from_string_case_insensitive():
    """Test severity_from_string is case insensitive."""
    assert severity_from_string("high") == Severity.HIGH
    assert severity_from_string("CrItIcAl") == Severity.CRITICAL


def test_severity_from_string_invalid():
    """Test severity_from_string with invalid string returns PASS."""
    assert severity_from_string("INVALID") == Severity.PASS
    assert severity_from_string("") == Severity.PASS


def test_severity_from_string_none():
    """Test severity_from_string with None returns PASS."""
    assert severity_from_string(None) == Severity.PASS


def test_compute_overall_severity_all_pass():
    """Test compute_overall_severity with all PASS."""
    result = compute_overall_severity(
        principle_severities=["PASS", "PASS"],
        pii_severities=[],
        jailbreak_severity="PASS"
    )
    assert result == Severity.PASS


def test_compute_overall_severity_mixed():
    """Test compute_overall_severity with mixed severities."""
    result = compute_overall_severity(
        principle_severities=["LOW", "MEDIUM"],
        pii_severities=["HIGH"],
        jailbreak_severity="PASS"
    )
    assert result == Severity.HIGH


def test_compute_overall_severity_critical():
    """Test compute_overall_severity with CRITICAL."""
    result = compute_overall_severity(
        principle_severities=["MEDIUM"],
        pii_severities=["CRITICAL"],
        jailbreak_severity="LOW"
    )
    assert result == Severity.CRITICAL


def test_compute_overall_severity_jailbreak():
    """Test compute_overall_severity with jailbreak severity."""
    result = compute_overall_severity(
        principle_severities=["PASS"],
        pii_severities=[],
        jailbreak_severity="CRITICAL"
    )
    assert result == Severity.CRITICAL


def test_severity_comparison():
    """Test Severity enum comparison operators."""
    assert Severity.PASS < Severity.LOW
    assert Severity.LOW < Severity.MEDIUM
    assert Severity.MEDIUM < Severity.HIGH
    assert Severity.HIGH < Severity.CRITICAL
    
    assert Severity.CRITICAL > Severity.HIGH
    assert Severity.HIGH > Severity.MEDIUM
    
    assert Severity.PASS <= Severity.PASS
    assert Severity.HIGH >= Severity.HIGH
