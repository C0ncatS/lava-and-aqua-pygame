from pygame.math import Vector2


class Position:
    @staticmethod
    def from_vector(vector: Vector2):
        return Position(vector.x, vector.y)

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def to_vector(self):
        return Vector2(self.x, self.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other) -> bool:
        return isinstance(other, Position) and (self.x, self.y) == (other.x, other.y)
