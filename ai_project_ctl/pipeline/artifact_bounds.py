"""Bounds for pipeline phase artifacts before they enter session state."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any

from .state import MAX_STORED_STRING_LENGTH


MAX_ARTIFACT_SNIPPET_LENGTH = 1200
TRUNCATED_TEXT_REASON = "oversized_string_truncated"


def bound_pipeline_artifact(
    value: Any,
    *,
    string_limit: int = MAX_STORED_STRING_LENGTH,
    snippet_length: int = MAX_ARTIFACT_SNIPPET_LENGTH,
) -> Any:
    """Return a JSON-compatible artifact with oversized strings summarized."""

    return _bound_value(
        value,
        path="artifact",
        string_limit=string_limit,
        snippet_length=snippet_length,
    )


def _bound_value(
    value: Any,
    *,
    path: str,
    string_limit: int,
    snippet_length: int,
) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _bound_value(
                nested,
                path="{}.{}".format(path, key),
                string_limit=string_limit,
                snippet_length=snippet_length,
            )
            for key, nested in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [
            _bound_value(
                nested,
                path="{}[{}]".format(path, index),
                string_limit=string_limit,
                snippet_length=snippet_length,
            )
            for index, nested in enumerate(value)
        ]
    if isinstance(value, str) and len(value) > string_limit:
        return _truncated_text(
            value,
            path=path,
            string_limit=string_limit,
            snippet_length=snippet_length,
        )
    return value


def _truncated_text(
    value: str,
    *,
    path: str,
    string_limit: int,
    snippet_length: int,
) -> dict[str, Any]:
    snippet_limit = max(0, min(snippet_length, string_limit - 1))
    snippet = value[:snippet_limit]
    return {
        "truncated": True,
        "reason": TRUNCATED_TEXT_REASON,
        "field": _field_name(path),
        "path": path,
        "original_size": len(value),
        "original_bytes": len(value.encode("utf-8")),
        "stored_size": len(snippet),
        "stored_bytes": len(snippet.encode("utf-8")),
        "limit": string_limit,
        "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "snippet": snippet,
    }


def _field_name(path: str) -> str:
    selected = path.rsplit(".", 1)[-1]
    if "[" in selected:
        return ""
    return selected
