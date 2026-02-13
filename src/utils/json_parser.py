"""Robust JSON extraction from LLM output."""

import json
import re
from typing import Any, Dict, Optional


def extract_json(text: str, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extract JSON from LLM output, handling various formats.
    
    Handles:
    - Clean JSON
    - JSON in markdown code fences
    - JSON with extra text before/after
    - Completely invalid input (returns fallback)
    
    Args:
        text: Raw LLM output text
        fallback: Default value to return if parsing fails
        
    Returns:
        Dict[str, Any]: Parsed JSON object or fallback
    """
    if fallback is None:
        fallback = {}
    
    if not text or not isinstance(text, str):
        return fallback
    
    # Try direct JSON parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code fences
    json_fence_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    matches = re.findall(json_fence_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue
    
    # Try to find JSON object in text (look for { ... })
    # Use simpler pattern to avoid ReDoS - just match balanced braces
    try:
        # Find all potential JSON objects by looking for opening braces
        start_positions = [i for i, c in enumerate(text) if c == '{']
        for start in start_positions:
            # Find matching closing brace by counting depth
            depth = 0
            for i in range(start, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i+1]
                        try:
                            return json.loads(candidate)
                        except json.JSONDecodeError:
                            break
    except Exception:
        pass
    
    # Try to find JSON array in text (look for [ ... ])
    try:
        # Find all potential JSON arrays by looking for opening brackets
        start_positions = [i for i, c in enumerate(text) if c == '[']
        for start in start_positions:
            # Find matching closing bracket by counting depth
            depth = 0
            for i in range(start, len(text)):
                if text[i] == '[':
                    depth += 1
                elif text[i] == ']':
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i+1]
                        try:
                            return json.loads(candidate)
                        except json.JSONDecodeError:
                            break
    except Exception:
        pass
    
    # All parsing attempts failed
    return fallback


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary with a default.
    
    Args:
        data: Dictionary to extract from
        key: Key to look up
        default: Default value if key not found
        
    Returns:
        Value from dict or default
    """
    return data.get(key, default)
