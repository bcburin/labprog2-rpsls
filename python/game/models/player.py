from dataclasses import dataclass


@dataclass(frozen=True)
class Player:
    name: str

    def __eq__(self, other):
        return isinstance(other, Player) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.name.__hash__()
