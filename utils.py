"""Shared utilities for the SalesAI pipeline."""

from __future__ import annotations

import json


def parse_json_response(text: str) -> dict | list:
    """
    Parse a JSON response from Claude, stripping markdown fences if present.

    Claude sometimes wraps JSON output in ```json ... ``` markdown fencing
    even when instructed not to. This function handles both cases.

    Returns the parsed JSON (dict or list).
    Raises json.JSONDecodeError if parsing fails after stripping.
    """
    cleaned = text.strip()

    # Remove markdown code fences if present
    if cleaned.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = cleaned.index("\n")
        cleaned = cleaned[first_newline + 1:]
        # Remove closing fence
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Some model responses include a sentence before/after the JSON despite
        # the prompt. Recover the first top-level object or array.
        object_start = cleaned.find("{")
        array_start = cleaned.find("[")
        starts = [idx for idx in (object_start, array_start) if idx != -1]
        if not starts:
            raise

        start = min(starts)
        opener = cleaned[start]
        closer = "}" if opener == "{" else "]"
        end = cleaned.rfind(closer)
        if end == -1 or end <= start:
            raise

        return json.loads(cleaned[start:end + 1])
