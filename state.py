from pygame.math import Vector2

from items import Item, Block, Liquid, Player, Timer


class State:
    def __init__(self, level_file="levels/level-1.txt"):
        level_data, world_size = self.read_level_file(level_file)
        self.world_size = world_size
        self.moves = [Vector2(0, 1), Vector2(1, 0), Vector2(0, -1), Vector2(-1, 0)]
        self.ground = []
        self.lavas = []
        self.aquas = []
        self.goals = []
        self.blocks = []
        self.players = []
        self.points = []
        self.timers = []
        self.containers = []
        self.walls = []
        self.deads = []
        self.stones = []
        self.parse_level(level_data)
        self.ground = [
            [Vector2(0, 0) for _ in range(int(self.world_size.x))]
            for _ in range(int(self.world_size.y))
        ]
        self.observers = []
        if not self.goals:
            raise ValueError("No goal found in level file")
        if not self.players:
            raise ValueError("No player found in level file")

    @property
    def world_width(self):
        return int(self.world_size.x)

    @property
    def world_height(self):
        return int(self.world_size.y)

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_player_moved(self, player, move_vector):
        for observer in self.observers:
            observer.player_moved(player, move_vector)

    def notify_player_died(self, player):
        for observer in self.observers:
            observer.player_died(player)

    def notify_aqua_touched_lava(self, position):
        for observer in self.observers:
            observer.aqua_touched_lava(position)

    def notify_lava_touched_aqua(self, position):
        for observer in self.observers:
            observer.lava_touched_aqua(position)

    def notify_block_moved(self, block):
        for observer in self.observers:
            observer.block_moved(block)

    def notify_player_reached_goal(self, player):
        for observer in self.observers:
            observer.player_reached_goal(player)

    def notify_player_won(self, player):
        for observer in self.observers:
            observer.player_won(player)

    def notify_state_restored(self):
        for observer in self.observers:
            observer.state_restored(self)

    def get_possible_moves(self, position: Vector2, **kwargs) -> list[Vector2]:
        possible_moves = []
        for move in self.moves:
            new_pos = position + move
            if self.can_move(new_pos, **kwargs):
                possible_moves.append(move)
        return possible_moves

    def can_move(self, position, **kwargs):
        for wall in self.walls:
            if wall.position == position:
                return False

        for stone in self.stones:
            if stone.position == position:
                return False

        for timer in self.timers:
            if timer.position == position:
                return False

        if kwargs.get("check_containers", True):
            for container in self.containers:
                if container.position == position:
                    return False

        if kwargs.get("check_blocks", True):
            for block in self.blocks:
                if block.position == position:
                    return False

        return self.is_inside(position)

    def is_inside(self, position):
        return (
            position.x >= 0
            and position.x < self.world_width
            and position.y >= 0
            and position.y < self.world_height
        )

    def is_points_empty(self):
        return len(self.points) == 0

    def is_goal(self, position):
        for goal in self.goals:
            if goal.position == position:
                return True
        return False

    def parse_level(self, level_data):
        for item in level_data:
            x = item["column"]
            y = item["row"]
            char = item["char"]
            if char == "L":
                self.lavas.append(Liquid(self, Vector2(x, y), Vector2(0, 0)))
            elif char == "A":
                self.aquas.append(Liquid(self, Vector2(x, y), Vector2(0, 0)))
            elif char == "B":
                self.blocks.append(Block(self, Vector2(x, y), Vector2(0, 0)))
            elif char == "G":
                self.goals.append(Item(self, Vector2(x, y), Vector2(0, 0)))
            elif char == "#":
                self.walls.append(Item(self, Vector2(x, y), Vector2(0, 0)))
            elif char == "U":
                self.players.append(Player(self, Vector2(x, y), Vector2(0, 0)))
            elif char == "*":
                self.points.append(Item(self, Vector2(x, y), Vector2(0, 0)))
            elif char.isdigit():
                self.timers.append(Timer(self, Vector2(x, y), Vector2(0, 0), int(char)))
            elif char == "I":
                self.containers.append(Item(self, Vector2(x, y), Vector2(0, 0)))

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
        new_state.world_size = self.world_size.copy()

        # Deep copy the ground array (2D list of Vector2)
        new_state.ground = [[tile.copy() for tile in row] for row in self.ground]

        # Copy item lists, but recreate items with new state reference
        new_state.lavas = [
            Liquid(new_state, liq.position.copy(), liq.tile.copy())
            for liq in self.lavas
        ]
        new_state.aquas = [
            Liquid(new_state, liq.position.copy(), liq.tile.copy())
            for liq in self.aquas
        ]
        new_state.blocks = [
            Block(new_state, block.position.copy(), block.tile.copy())
            for block in self.blocks
        ]
        new_state.goals = [
            Item(new_state, goal.position.copy(), goal.tile.copy())
            for goal in self.goals
        ]
        new_state.walls = [
            Item(new_state, wall.position.copy(), wall.tile.copy())
            for wall in self.walls
        ]
        new_state.players = [
            Player(new_state, player.position.copy(), player.tile.copy())
            for player in self.players
        ]
        new_state.points = [
            Item(new_state, point.position.copy(), point.tile.copy())
            for point in self.points
        ]
        new_state.containers = [
            Item(new_state, container.position.copy(), container.tile.copy())
            for container in self.containers
        ]
        new_state.deads = [
            Item(new_state, dead.position.copy(), dead.tile.copy())
            for dead in self.deads
        ]
        new_state.stones = [
            Item(new_state, stone.position.copy(), stone.tile.copy())
            for stone in self.stones
        ]
        # Copy timers with their duration
        new_state.timers = [
            Timer(new_state, timer.position.copy(), timer.tile.copy(), timer.duration)
            for timer in self.timers
        ]

        # Copy status for items that have it
        for i, player in enumerate(self.players):
            new_state.players[i].status = player.status

        new_state.observers = []

        return new_state
