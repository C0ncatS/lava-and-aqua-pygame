from pygame.math import Vector2

from items import Item, Block, Liquid, Player, Timer
from observers import (
    StoneObserver,
    PointObserver,
    DeadObserver,
    PlayerObserver,
    GoalObserver,
    AquaObserver,
    LavaObserver,
)
from position import Position


class State:
    def __init__(self, level_file="levels/level1.txt"):
        level_data, world_size = self.read_level_file(level_file)
        self.world_size = world_size
        self.moves = [Position(0, 1), Position(0, -1), Position(1, 0), Position(-1, 0)]
        self.ground = []
        self.lavas: dict[Position, Liquid] = {}
        self.aquas: dict[Position, Liquid] = {}
        self.goal = None
        self.blocks: dict[Position, Block] = {}
        self.player = None
        self.points: dict[Position, Item] = {}
        self.timers: dict[Position, Timer] = {}
        self.containers: dict[Position, Item] = {}
        self.walls: dict[Position, Item] = {}
        self.deads: dict[Position, Item] = {}
        self.stones: dict[Position, Item] = {}
        self.parse_level(level_data)
        self.ground = [
            [Vector2(0, 0) for _ in range(int(self.world_size.x))]
            for _ in range(int(self.world_size.y))
        ]
        self.observers = [
            StoneObserver(self),
            PointObserver(self),
            DeadObserver(self),
            PlayerObserver(self),
            GoalObserver(self),
            AquaObserver(self),
            LavaObserver(self),
        ]
        if not self.goal:
            raise ValueError("No goal found in level file")
        if not self.player:
            raise ValueError("No player found in level file")

    @property
    def world_width(self):
        return int(self.world_size.x)

    @property
    def world_height(self):
        return int(self.world_size.y)

    def add_observer(self, observer):
        self.observers.append(observer)

    def clear_observers(self):
        self.observers.clear()

    def notify_player_moved(self, player: Player, move: Position):
        for observer in self.observers:
            observer.player_moved(player, move)

    def notify_player_died(self, player: Player):
        for observer in self.observers:
            observer.player_died(player)

    def notify_aqua_touched_lava(self, position: Position):
        for observer in self.observers:
            observer.aqua_touched_lava(position)

    def notify_lava_touched_aqua(self, position: Position):
        for observer in self.observers:
            observer.lava_touched_aqua(position)

    def notify_block_moved(self, block: Block):
        for observer in self.observers:
            observer.block_moved(block)

    def notify_player_reached_goal(self, player: Player):
        for observer in self.observers:
            observer.player_reached_goal(player)

    def notify_player_won(self, player: Player):
        for observer in self.observers:
            observer.player_won(player)

    def notify_state_restored(self):
        for observer in self.observers:
            observer.state_restored(self)

    def get_possible_moves(self, position: Position, **kwargs) -> list[Position]:
        possible_moves = []
        for move in self.moves:
            new_pos = Position.from_vector(position.to_vector() + move.to_vector())
            if self.can_move(new_pos, **kwargs):
                possible_moves.append(move)
        return possible_moves

    def can_move(self, position: Position, **kwargs):
        if position in self.walls:
            return False

        if position in self.stones:
            return False

        if position in self.timers:
            return False

        if kwargs.get("check_containers", True):
            if position in self.containers:
                return False

        if kwargs.get("check_blocks", True):
            if position in self.blocks:
                return False

        return self.is_inside(position)

    def is_inside(self, position: Position):
        return (
            position.x >= 0
            and position.x < self.world_width
            and position.y >= 0
            and position.y < self.world_height
        )

    def is_points_empty(self):
        return len(self.points) == 0

    def is_goal(self, position: Position):
        return position == self.goal.position

    def is_won(self):
        return self.is_points_empty() and self.is_goal(self.player.position)

    def parse_level(self, level_data):
        for item in level_data:
            x = item["column"]
            y = item["row"]
            char = item["char"]
            if char == "L":
                self.lavas[Position(x, y)] = Liquid(self, Position(x, y), Vector2(0, 0))
            elif char == "A":
                self.aquas[Position(x, y)] = Liquid(self, Position(x, y), Vector2(0, 0))
            elif char == "B":
                self.blocks[Position(x, y)] = Block(self, Position(x, y), Vector2(0, 0))
            elif char == "G":
                self.goal = Item(self, Position(x, y), Vector2(0, 0))
            elif char == "#":
                self.walls[Position(x, y)] = Item(self, Position(x, y), Vector2(0, 0))
            elif char == "U":
                self.player = Player(self, Position(x, y), Vector2(0, 0))
            elif char == "*":
                self.points[Position(x, y)] = Item(self, Position(x, y), Vector2(0, 0))
            elif char.isdigit():
                self.timers[Position(x, y)] = Timer(
                    self,
                    Position(x, y),
                    Vector2(0, 0),
                    int(char),
                )
            elif char == "I":
                self.containers[Position(x, y)] = Item(
                    self,
                    Position(x, y),
                    Vector2(0, 0),
                )

    def read_level_file(self, filename):
        level_data = []
        world_size = Vector2(0, 0)

        with open(filename, "r") as file:
            for row_index, line in enumerate(file):
                line = line.rstrip("\n").split()
                world_size.x = len(line)
                world_size.y += 1
                for col_index, char in enumerate(line):
                    level_data.append(
                        {"row": row_index, "column": col_index, "char": char}
                    )

        return level_data, world_size

    def copy(self):
        # Create a new State instance without calling __init__
        cls = self.__class__
        new_state = cls.__new__(cls)

        # Copy simple attributes
        new_state.moves = self.moves
        new_state.world_size = self.world_size.copy()
        new_state.ground = self.ground
        new_state.walls = self.walls
        new_state.containers = self.containers

        # Copy item lists, but recreate items with new state reference
        new_state.lavas = {
            pos: Liquid(new_state, liq.position, liq.tile.copy())
            for pos, liq in self.lavas.items()
        }
        new_state.aquas = {
            pos: Liquid(new_state, liq.position, liq.tile.copy())
            for pos, liq in self.aquas.items()
        }
        new_state.blocks = {
            pos: Block(new_state, block.position, block.tile.copy())
            for pos, block in self.blocks.items()
        }

        new_state.goal = Item(
            new_state,
            self.goal.position,
            self.goal.tile.copy(),
        )
        new_state.player = Player(
            new_state,
            self.player.position,
            self.player.tile.copy(),
        )
        # Copy status for items that have it
        new_state.player.status = self.player.status

        new_state.points = {
            pos: Item(new_state, point.position, point.tile.copy())
            for pos, point in self.points.items()
        }
        new_state.deads = {
            pos: Item(new_state, dead.position, dead.tile.copy())
            for pos, dead in self.deads.items()
        }
        new_state.stones = {
            pos: Item(new_state, stone.position, stone.tile.copy())
            for pos, stone in self.stones.items()
        }
        # Copy timers with their duration
        new_state.timers = {
            pos: Timer(new_state, timer.position, timer.tile.copy(), timer.duration)
            for pos, timer in self.timers.items()
        }

        new_state.observers = [
            StoneObserver(new_state),
            PointObserver(new_state),
            DeadObserver(new_state),
            PlayerObserver(new_state),
            GoalObserver(new_state),
            AquaObserver(new_state),
            LavaObserver(new_state),
        ]

        return new_state

    def __hash__(self) -> int:
        # lavas, aquas, blocks, player, points, timers, deads, and stones
        return hash(
            (
                frozenset(self.lavas.keys()),
                frozenset(self.aquas.keys()),
                frozenset(self.blocks.keys()),
                (self.player.position, self.player.status),
                frozenset(self.points.keys()),
                frozenset((pos, timer.duration) for pos, timer in self.timers.items()),
                frozenset(self.deads.keys()),
                frozenset(self.stones.keys()),
            )
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, State):
            return False
        return (
            self.lavas.keys() == other.lavas.keys()
            and self.aquas.keys() == other.aquas.keys()
            and self.blocks.keys() == other.blocks.keys()
            and self.player.position == other.player.position
            and self.player.status == other.player.status
            and self.points.keys() == other.points.keys()
            and all(
                self.timers[pos].duration == other.timers[pos].duration
                for pos in self.timers.keys()
                if pos in other.timers.keys()
            )
            and self.timers.keys() == other.timers.keys()
            and self.deads.keys() == other.deads.keys()
            and self.stones.keys() == other.stones.keys()
        )
