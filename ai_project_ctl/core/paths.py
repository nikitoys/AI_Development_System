"""Repository path helpers for project-control files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Resolved paths for the root AI_PROJECT control layer."""

    root: Path

    @classmethod
    def from_root(cls, root: str | Path = ".") -> "ProjectPaths":
        return cls(root=Path(root).resolve())

    @property
    def project_dir(self) -> Path:
        return self.root / "AI_PROJECT"

    @property
    def state_dir(self) -> Path:
        return self.project_dir / "state"

    @property
    def events_dir(self) -> Path:
        return self.project_dir / "events"

    @property
    def generated_dir(self) -> Path:
        return self.project_dir / "generated"

    @property
    def locks_dir(self) -> Path:
        return self.project_dir / ".locks"

    def ensure_project_dirs(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)

    def state_file(self, name: str) -> Path:
        return self.state_dir / name

    def event_file(self, name: str) -> Path:
        return self.events_dir / name

    def generated_file(self, name: str) -> Path:
        return self.generated_dir / name

    def lock_file(self, name: str) -> Path:
        return self.locks_dir / f"{name}.lock"

    def protected_kind(self, path: str | Path) -> str | None:
        resolved = Path(path).resolve()
        for kind, directory in (
            ("state", self.state_dir),
            ("events", self.events_dir),
            ("generated", self.generated_dir),
        ):
            try:
                resolved.relative_to(directory.resolve())
            except ValueError:
                continue
            return kind
        return None

    def is_protected(self, path: str | Path) -> bool:
        return self.protected_kind(path) is not None

