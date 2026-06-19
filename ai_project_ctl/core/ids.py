"""ID allocation and identity resolution helpers."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .result import CommandError


class IdentityError(CommandError):
    """Identity allocation or resolution error."""


@dataclass(frozen=True)
class IdentityRecord:
    token: str
    entity_id: str
    field: str


class IdentityIndex:
    """Unique token-to-entity resolver."""

    def __init__(self) -> None:
        self._records: dict[str, IdentityRecord] = {}

    def add(self, token: object, entity_id: object, field: str) -> None:
        if token is None or token == "":
            return
        token_text = str(token)
        entity_text = str(entity_id)
        existing = self._records.get(token_text)
        if existing is not None and existing.entity_id != entity_text:
            raise IdentityError(
                "DUPLICATE_IDENTITY_TOKEN",
                f"{token_text} resolves to both {existing.entity_id} and {entity_text}",
                path=field,
            )
        self._records[token_text] = IdentityRecord(
            token=token_text,
            entity_id=entity_text,
            field=field,
        )

    def resolve(self, token: str) -> str:
        record = self._records.get(token)
        if record is None:
            raise IdentityError("IDENTITY_NOT_FOUND", f"No entity resolves from {token}")
        return record.entity_id

    def to_dict(self) -> dict[str, str]:
        return {token: record.entity_id for token, record in sorted(self._records.items())}


def allocate_numeric_id(existing_ids: Iterable[str], prefix: str, *, width: int = 3) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    highest = 0
    for value in existing_ids:
        match = pattern.match(str(value))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{prefix}-{highest + 1:0{width}d}"


def allocate_uid(prefix: str, *, suffix: str | None = None, width: int = 12) -> str:
    token = suffix or uuid.uuid4().hex[:width]
    return f"{prefix}{token}"


def format_scoped_ref(epic_key: str, local_seq: int, *, width: int = 2) -> str:
    if local_seq < 1:
        raise IdentityError("INVALID_LOCAL_SEQUENCE", "local_seq must be positive")
    return f"{epic_key}-{local_seq:0{width}d}"


def build_identity_index(
    entities: Iterable[Mapping[str, object]],
    *,
    entity_id_field: str = "id",
    token_fields: Sequence[str] = ("id", "uid", "ref", "legacy_id"),
    aliases_field: str = "aliases",
) -> IdentityIndex:
    index = IdentityIndex()
    for entity in entities:
        entity_id = entity.get(entity_id_field)
        if not entity_id:
            raise IdentityError("MISSING_ENTITY_ID", f"Missing {entity_id_field}")

        for field in token_fields:
            index.add(entity.get(field), entity_id, field)

        aliases = entity.get(aliases_field, [])
        if aliases is None:
            aliases = []
        if not isinstance(aliases, list):
            raise IdentityError("INVALID_ALIASES", f"{aliases_field} must be a list")
        for alias in aliases:
            index.add(alias, entity_id, aliases_field)
    return index

