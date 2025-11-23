from dataclasses import dataclass
from pygame.math import Vector2


@dataclass(frozen=True)
class Position:
    x: float
    y: float

    @staticmethod
    def from_vector(vector: Vector2):
        return Position(vector.x, vector.y)

    def to_vector(self):
        return Vector2(self.x, self.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other) -> bool:
        return isinstance(other, Position) and (self.x, self.y) == (other.x, other.y)
