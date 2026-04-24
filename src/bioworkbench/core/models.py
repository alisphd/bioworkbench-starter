from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    id: str
    name: str
    category: str
    description: str
    status: str = "planned"
    external_tools: tuple[str, ...] = ()
    next_steps: tuple[str, ...] = ()

    @property
    def is_ready(self) -> bool:
        return self.status.lower() == "ready"

