"""Token Budget Gate for supervised pipeline Codex execution."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol

from .policy import TokenBudgetPolicy


PASS = "pass"
WARN = "warn"
FAIL = "fail"

CODE_PASS = "TOKEN_BUDGET_PASS"
CODE_PROMPT_MISSING = "TOKEN_BUDGET_PROMPT_MISSING"
CODE_TOKEN_COUNT_UNAVAILABLE = "TOKEN_BUDGET_COUNT_UNAVAILABLE"
CODE_PROMPT_TOO_LARGE = "TOKEN_BUDGET_PROMPT_TOO_LARGE"
CODE_LOW_REMAINING = "TOKEN_BUDGET_LOW_REMAINING"
CODE_CONTEXT_REQUIRES_COMPACT_SPLIT = "TOKEN_BUDGET_CONTEXT_REQUIRES_COMPACT_SPLIT"
CODE_WARN_TOKEN_COUNT_UNAVAILABLE = "TOKEN_BUDGET_WARN_COUNT_UNAVAILABLE"

CONTEXT_METADATA_RE = re.compile(r"<!--\s*Context:\s*(.*?)\s*-->", re.DOTALL)
CONTEXT_SECTION_LABEL = "Retrieved Context Pack Content:"
CONTEXT_SECTION_END_LABELS = (
    "\nAcceptance Criteria:",
    "\nVerification:",
    "\nResult Format:",
    "\nReview / Result Format Notes:",
)
COMPACT_SPLIT_LABEL_RE = re.compile(
    r"^\s*(?:[-*]\s*)?"
    r"(?:context\s+)?"
    r"(?:requires?|needs?|must)\s+"
    r"(?P<action>compact(?:ion)?|split|compact/split|compact\s+or\s+split)"
    r"\s*:\s*(?P<value>true|yes|1)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
TRUE_COMPACT_SPLIT_KEYS = {
    "compact_required",
    "compaction_required",
    "context_requires_compact",
    "context_requires_compaction",
    "context_requires_compact_or_split",
    "context_requires_split",
    "must_compact",
    "must_split",
    "needs_compact",
    "needs_compaction",
    "needs_split",
    "requires_compact",
    "requires_compaction",
    "requires_compact_or_split",
    "requires_split",
    "split_required",
}


class TokenCounter(Protocol):
    """Protocol for local or configured token-counting strategies."""

    def count(self, text: str) -> "TokenCount":
        ...


@dataclass(frozen=True)
class TokenCount:
    tokens: int | None
    strategy: str
    estimated: bool
    unavailable_reason: str = ""

    @property
    def unavailable(self) -> bool:
        return self.tokens is None


@dataclass(frozen=True)
class LocalTokenEstimator:
    """Deterministic local estimator used when no provider counter is configured."""

    strategy: str = "local_byte_estimate"

    def count(self, text: str) -> TokenCount:
        return TokenCount(
            tokens=estimate_tokens(text),
            strategy=self.strategy,
            estimated=True,
        )


@dataclass(frozen=True)
class TokenBudgetGateResult:
    status: str
    code: str
    reason: str
    prompt_path: str
    prompt_sha256: str
    prompt_bytes: int
    prompt_tokens: int | None
    context_bytes: int
    context_tokens: int | None
    token_count_strategy: str
    token_count_estimated: bool
    token_count_unavailable: bool
    token_count_unavailable_reason: str
    model_context_limit: int
    max_context_tokens: int
    reserved_output_tokens: int
    min_remaining_tokens: int
    remaining_tokens: int | None
    context_requires_compact_or_split: bool
    context_requirement_reasons: tuple[str, ...]
    context_pack: Mapping[str, Any]

    @property
    def ok(self) -> bool:
        return self.status == PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "reason": self.reason,
            "prompt_path": self.prompt_path,
            "prompt_sha256": self.prompt_sha256,
            "prompt_bytes": self.prompt_bytes,
            "prompt_tokens": self.prompt_tokens,
            "context_bytes": self.context_bytes,
            "context_tokens": self.context_tokens,
            "token_count_strategy": self.token_count_strategy,
            "token_count_estimated": self.token_count_estimated,
            "token_count_unavailable": self.token_count_unavailable,
            "token_count_unavailable_reason": self.token_count_unavailable_reason,
            "model_context_limit": self.model_context_limit,
            "max_context_tokens": self.max_context_tokens,
            "reserved_output_tokens": self.reserved_output_tokens,
            "min_remaining_tokens": self.min_remaining_tokens,
            "remaining_tokens": self.remaining_tokens,
            "context_requires_compact_or_split": self.context_requires_compact_or_split,
            "context_requirement_reasons": list(self.context_requirement_reasons),
            "context_pack": dict(self.context_pack),
        }


def evaluate_token_budget(
    *,
    root: str | Path = ".",
    policy: TokenBudgetPolicy,
    prompt_path: str | Path | None = None,
    token_counter: TokenCounter | None = None,
    strict: bool = True,
) -> TokenBudgetGateResult:
    """Evaluate the actual generated Codex prompt payload against policy."""

    root_path = Path(root).resolve()
    selected_prompt_path = (
        Path(prompt_path) if prompt_path is not None else _default_prompt_path(root_path)
    )
    if not selected_prompt_path.is_absolute():
        selected_prompt_path = root_path / selected_prompt_path
    selected_prompt_path = selected_prompt_path.resolve()

    if not selected_prompt_path.exists():
        return _result(
            status=FAIL,
            code=CODE_PROMPT_MISSING,
            reason="prompt_payload_missing",
            prompt_path=selected_prompt_path,
            policy=policy,
        )

    prompt_text = selected_prompt_path.read_text(encoding="utf-8")
    prompt_bytes = len(prompt_text.encode("utf-8"))
    prompt_sha = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
    context_text = _extract_context_payload(prompt_text)
    context_bytes = len(context_text.encode("utf-8"))
    context_pack = _context_pack_metadata(root_path, prompt_text)

    counter = token_counter or LocalTokenEstimator()
    prompt_count = counter.count(prompt_text)
    context_count = counter.count(context_text) if context_text else TokenCount(
        tokens=0,
        strategy=prompt_count.strategy,
        estimated=prompt_count.estimated,
    )

    token_count_unavailable = prompt_count.unavailable or context_count.unavailable
    unavailable_reason = (
        prompt_count.unavailable_reason
        or context_count.unavailable_reason
        or "token_count_unavailable"
    )
    if token_count_unavailable:
        status = FAIL if strict else WARN
        code = CODE_TOKEN_COUNT_UNAVAILABLE if strict else CODE_WARN_TOKEN_COUNT_UNAVAILABLE
        return _result(
            status=status,
            code=code,
            reason="token_count_unavailable",
            prompt_path=selected_prompt_path,
            policy=policy,
            prompt_sha256=prompt_sha,
            prompt_bytes=prompt_bytes,
            context_bytes=context_bytes,
            token_count_strategy=prompt_count.strategy or context_count.strategy,
            token_count_estimated=prompt_count.estimated or context_count.estimated,
            token_count_unavailable=True,
            token_count_unavailable_reason=unavailable_reason,
            context_pack=context_pack,
        )

    prompt_tokens = int(prompt_count.tokens or 0)
    context_tokens = int(context_count.tokens or 0)
    model_context_limit = policy.max_prompt_tokens
    reserved_output_tokens = policy.reserved_output_tokens
    remaining_tokens = model_context_limit - prompt_tokens - reserved_output_tokens
    context_required, context_reasons = _context_requires_compact_or_split(
        prompt_text,
        context_pack,
        context_tokens=context_tokens,
        max_context_tokens=policy.max_context_tokens,
    )

    base = {
        "prompt_sha256": prompt_sha,
        "prompt_bytes": prompt_bytes,
        "prompt_tokens": prompt_tokens,
        "context_bytes": context_bytes,
        "context_tokens": context_tokens,
        "token_count_strategy": prompt_count.strategy,
        "token_count_estimated": prompt_count.estimated,
        "remaining_tokens": remaining_tokens,
        "context_requires_compact_or_split": context_required,
        "context_requirement_reasons": tuple(context_reasons),
        "context_pack": context_pack,
    }

    if context_required:
        return _result(
            status=FAIL,
            code=CODE_CONTEXT_REQUIRES_COMPACT_SPLIT,
            reason="context_requires_compact_or_split",
            prompt_path=selected_prompt_path,
            policy=policy,
            **base,
        )

    if prompt_tokens + reserved_output_tokens > model_context_limit:
        return _result(
            status=FAIL,
            code=CODE_PROMPT_TOO_LARGE,
            reason="prompt_does_not_fit",
            prompt_path=selected_prompt_path,
            policy=policy,
            **base,
        )

    if remaining_tokens < policy.min_remaining_tokens:
        return _result(
            status=FAIL,
            code=CODE_LOW_REMAINING,
            reason="remaining_tokens_below_threshold",
            prompt_path=selected_prompt_path,
            policy=policy,
            **base,
        )

    return _result(
        status=PASS,
        code=CODE_PASS,
        reason="within_token_budget",
        prompt_path=selected_prompt_path,
        policy=policy,
        **base,
    )


def estimate_tokens(text: str) -> int:
    """Return a deterministic conservative token estimate for local gating."""

    if not text:
        return 0
    byte_count = len(text.encode("utf-8"))
    return max(1, math.ceil(byte_count / 4))


def _result(
    *,
    status: str,
    code: str,
    reason: str,
    prompt_path: Path,
    policy: TokenBudgetPolicy,
    prompt_sha256: str = "",
    prompt_bytes: int = 0,
    prompt_tokens: int | None = None,
    context_bytes: int = 0,
    context_tokens: int | None = None,
    token_count_strategy: str = "",
    token_count_estimated: bool = False,
    token_count_unavailable: bool = False,
    token_count_unavailable_reason: str = "",
    remaining_tokens: int | None = None,
    context_requires_compact_or_split: bool = False,
    context_requirement_reasons: tuple[str, ...] = (),
    context_pack: Mapping[str, Any] | None = None,
) -> TokenBudgetGateResult:
    return TokenBudgetGateResult(
        status=status,
        code=code,
        reason=reason,
        prompt_path=str(prompt_path),
        prompt_sha256=prompt_sha256,
        prompt_bytes=prompt_bytes,
        prompt_tokens=prompt_tokens,
        context_bytes=context_bytes,
        context_tokens=context_tokens,
        token_count_strategy=token_count_strategy,
        token_count_estimated=token_count_estimated,
        token_count_unavailable=token_count_unavailable,
        token_count_unavailable_reason=token_count_unavailable_reason,
        model_context_limit=policy.max_prompt_tokens,
        max_context_tokens=policy.max_context_tokens,
        reserved_output_tokens=policy.reserved_output_tokens,
        min_remaining_tokens=policy.min_remaining_tokens,
        remaining_tokens=remaining_tokens,
        context_requires_compact_or_split=context_requires_compact_or_split,
        context_requirement_reasons=context_requirement_reasons,
        context_pack=dict(context_pack or {}),
    )


def _default_prompt_path(root: Path) -> Path:
    return root / "AI_PROJECT" / "generated" / "CODEX_PROMPT.md"


def _extract_context_payload(prompt_text: str) -> str:
    start = prompt_text.find(CONTEXT_SECTION_LABEL)
    if start == -1:
        return ""
    payload_start = start + len(CONTEXT_SECTION_LABEL)
    payload_end = len(prompt_text)
    for label in CONTEXT_SECTION_END_LABELS:
        label_index = prompt_text.find(label, payload_start)
        if label_index != -1:
            payload_end = min(payload_end, label_index)
    return prompt_text[payload_start:payload_end].strip()


def _context_pack_metadata(root: Path, prompt_text: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    prompt_metadata = _first_context_metadata(prompt_text)
    if prompt_metadata:
        metadata["metadata"] = _safe_context_metadata(prompt_metadata)

    label_values = {
        "path": _label_value(prompt_text, "Context Pack path"),
        "sha256": _label_value(prompt_text, "Context Pack SHA-256"),
        "mode": _label_value(prompt_text, "Context mode"),
        "task_id": _label_value(prompt_text, "Context task ID"),
        "docs_revision": _label_value(prompt_text, "Docs revision"),
        "tasks_revision": _label_value(prompt_text, "Tasks revision"),
    }
    metadata.update({key: value for key, value in label_values.items() if value})

    raw_path = label_values["path"]
    if raw_path:
        path = Path(raw_path)
        resolved = path if path.is_absolute() else root / path
        metadata["resolved_path"] = str(resolved.resolve())
        if resolved.exists():
            content = resolved.read_bytes()
            metadata["file_sha256"] = hashlib.sha256(content).hexdigest()
            metadata["file_bytes"] = len(content)
    return metadata


def _first_context_metadata(text: str) -> dict[str, Any]:
    match = CONTEXT_METADATA_RE.search(text)
    if not match:
        return {}
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _safe_context_metadata(data: Mapping[str, Any]) -> dict[str, Any]:
    safe_keys = (
        "schema_version",
        "mode",
        "task_id",
        "limit",
        "docs_revision",
        "tasks_revision",
        "selected_chunks",
        "explicit_query",
    )
    return {key: data[key] for key in safe_keys if key in data}


def _label_value(text: str, label: str) -> str:
    pattern = re.compile(
        r"^\s*[-*]\s*" + re.escape(label) + r":\s*(?P<value>.+?)\s*$",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return ""
    return match.group("value").strip().strip("`").strip()


def _context_requires_compact_or_split(
    prompt_text: str,
    context_pack: Mapping[str, Any],
    *,
    context_tokens: int,
    max_context_tokens: int,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if max_context_tokens >= 0 and context_tokens > max_context_tokens:
        reasons.append("context_tokens_exceed_threshold")
    if COMPACT_SPLIT_LABEL_RE.search(prompt_text):
        reasons.append("prompt_declares_context_compact_or_split_required")
    if _metadata_requires_compact_or_split(context_pack):
        reasons.append("context_metadata_requires_compact_or_split")
    return bool(reasons), reasons


def _metadata_requires_compact_or_split(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).lower() in TRUE_COMPACT_SPLIT_KEYS and item is True:
                return True
            if _metadata_requires_compact_or_split(item):
                return True
    elif isinstance(value, list):
        return any(_metadata_requires_compact_or_split(item) for item in value)
    return False
