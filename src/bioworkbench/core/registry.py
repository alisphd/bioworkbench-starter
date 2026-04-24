from __future__ import annotations

from collections import OrderedDict
from typing import Iterable

from bioworkbench.core.models import ToolSpec


class ToolRegistry:
    def __init__(self, tools: Iterable[ToolSpec]) -> None:
        self._tools = list(tools)
        self._by_id = {tool.id: tool for tool in self._tools}

        categories: OrderedDict[str, list[ToolSpec]] = OrderedDict()
        for tool in self._tools:
            categories.setdefault(tool.category, []).append(tool)
        self._by_category = categories

    def all(self) -> list[ToolSpec]:
        return list(self._tools)

    def get(self, tool_id: str) -> ToolSpec:
        return self._by_id[tool_id]

    def categories(self) -> list[str]:
        return list(self._by_category.keys())

    def by_category(self, category: str) -> list[ToolSpec]:
        return list(self._by_category.get(category, []))

    def ready_tools(self) -> list[ToolSpec]:
        return [tool for tool in self._tools if tool.is_ready]

