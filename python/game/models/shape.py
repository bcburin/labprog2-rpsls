from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Shape:
    name: str

    def __eq__(self, other):
        return isinstance(other, Shape) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)
