from enum import Enum, auto
from collections import deque
from functools import cached_property

from state import State
from commands import MoveCommand
from position import Position


class Algo(Enum):
    DFS = auto()
    BFS = auto()


class DFS:
    def __init__(self, depth_limit: int = 200):
        self.depth_limit = depth_limit
        self.visited: dict(int, bool) = {}
        self.nodes = 0
        self.path: deque[Position] = deque()

    def mark_as_visited(self, state: State):
        state_key = hash(state)
        self.visited[state_key] = True

    def check(self, state: State):
        state_key = hash(state)
        return state_key not in self.visited and state.player.status in ["alive", "won"]

    def apply_move(self, state: State, move: Position):
        new_state = state.copy()
        MoveCommand(new_state, new_state.player, move).run()
        return new_state

    def __call__(self, state: State, depth: int = 0):
        if depth > self.depth_limit:
            return False

        self.mark_as_visited(state)
        self.nodes += 1
        if state.is_won():
            return True
        for move in state.get_possible_moves(state.player.position, check_blocks=False):
            new_state = self.apply_move(state, move)
            if self.check(new_state):
                result = self(new_state, depth + 1)
                if result:
                    self.path.appendleft(move)
                    return True

        return False


class BFS:
    def __init__(self):
        self.queue: deque[State] = deque()
        self.parent: dict[int, (int | None, Position | None)] = {}
        self.visited: dict[int, bool] = {}
        self.nodes = 0
        self.won_state = None

    def mark_as_visited(self, state: State):
        state_key = hash(state)
        self.visited[state_key] = True

    def set_parent(self, state: State, parent: State | None, move: Position | None):
        state_key = hash(state)
        parent_key = hash(parent) if parent else None
        self.parent[state_key] = (parent_key, move)

    def check(self, state: State):
        state_key = hash(state)
        return state_key not in self.visited and state.player.status in ["alive", "won"]

    def apply_move(self, state: State, move: Position):
        new_state = state.copy()
        MoveCommand(new_state, new_state.player, move).run()
        return new_state

    def __call__(self, state: State):
        self.queue.append(state)
        self.set_parent(state, None, None)
        self.mark_as_visited(state)
        while self.queue:
            current_state = self.queue.popleft()
            self.nodes += 1
            for move in current_state.get_possible_moves(
                current_state.player.position,
                check_blocks=False,
            ):
                new_state = self.apply_move(current_state, move)
                if self.check(new_state):
                    self.queue.append(new_state)
                    self.set_parent(new_state, current_state, move)
                    self.mark_as_visited(new_state)
                    if new_state.is_won():
                        self.won_state = hash(new_state)
                        return

    @cached_property
    def path(self) -> deque[Position] | None:
        if not self.won_state:
            return None
        path = deque()
        current_state = self.won_state
        while current_state:
            parent_key, move = self.parent[current_state]
            if move is not None:
                path.appendleft(move)
            current_state = parent_key
        return path
