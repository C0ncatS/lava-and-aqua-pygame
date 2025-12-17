from abc import ABC, abstractmethod
from enum import Enum
from collections import deque
import heapq

from state import State
from commands import MoveCommand
from position import Position


INF = 1_000_000_000


class Algorithms(Enum):
    DFS = "dfs"
    BFS = "bfs"
    UCS = "ucs"
    HILL_CLIMB = "hill_climb"
    A_STAR = "a_star"


class Algorithm(ABC):
    @abstractmethod
    def get_nodes(self) -> int:
        pass

    @abstractmethod
    def get_visited_count(self) -> int:
        pass

    @abstractmethod
    def get_path(self) -> deque[Position]:
        pass

    @abstractmethod
    def __call__(self, state: State):
        pass


class DFS(Algorithm):
    def __init__(self):
        self.visited: dict[State, bool] = {}
        self.nodes: int = 0
        self.visited_count: int = 0
        self.path: deque[Position] = deque()

    def mark_as_visited(self, state: State):
        self.visited[state] = True

    def check(self, state: State):
        return state not in self.visited and state.player.status in ["alive", "won"]

    def apply_move(self, state: State, move: Position):
        new_state = state.copy()
        MoveCommand(new_state, new_state.player, move).run()
        return new_state

    def __call__(self, state: State):
        self.nodes += 1
        self.visited_count += 1
        self.mark_as_visited(state)

        if state.is_won():
            return True

        for move in state.get_possible_moves(state.player.position, check_blocks=False):
            new_state = self.apply_move(state, move)
            if self.check(new_state):
                result = self(new_state)
                if result:
                    self.path.appendleft(move)
                    return True

        return False

    def get_nodes(self) -> int:
        return self.nodes

    def get_visited_count(self) -> int:
        return self.visited_count

    def get_path(self) -> deque[Position]:
        return self.path


class BFS(Algorithm):
    def __init__(self):
        self.parent: dict[State, tuple[State | None, Position | None]] = {}
        self.visited: dict[State, bool] = {}
        self.nodes: int = 0
        self.visited_count: int = 0
        self.won_state: State | None = None

    def mark_as_visited(self, state: State):
        self.visited[state] = True

    def set_parent(self, state: State, parent: State | None, move: Position | None):
        self.parent[state] = (parent, move)

    def check(self, state: State):
        return state not in self.visited and state.player.status in ["alive", "won"]

    def apply_move(self, state: State, move: Position):
        new_state = state.copy()
        MoveCommand(new_state, new_state.player, move).run()
        return new_state

    def __call__(self, state: State):
        queue: deque[State] = deque()
        queue.append(state)
        self.set_parent(state, None, None)
        self.nodes += 1
        self.visited_count += 1
        self.mark_as_visited(state)
        while queue:
            current_state = queue.popleft()
            self.visited_count += 1
            pos = current_state.player.position
            for move in current_state.get_possible_moves(pos, check_blocks=False):
                new_state = self.apply_move(current_state, move)
                if self.check(new_state):
                    queue.append(new_state)
                    self.set_parent(new_state, current_state, move)
                    self.nodes += 1
                    self.mark_as_visited(new_state)
                    if new_state.is_won():
                        self.won_state = new_state
                        return

    def get_nodes(self) -> int:
        return self.nodes

    def get_visited_count(self) -> int:
        return self.visited_count

    def get_path(self) -> deque[Position]:
        path: deque[Position] = deque()
        current_state = self.won_state
        while current_state is not None:
            parent, move = self.parent[current_state]
            if move is not None:
                path.appendleft(move)
            current_state = parent
        return path


class UCS(Algorithm):
    def __init__(self):
        self.parent: dict[State, tuple[State | None, Position | None]] = {}
        self.visited: dict[State, bool] = {}
        self.distance: dict[State, int] = {}
        self.nodes: int = 0
        self.visited_count: int = 0
        self.won_state: State | None = None

    def is_visited(self, state: State):
        return state in self.visited

    def mark_as_visited(self, state: State):
        self.visited[state] = True

    def update_cost(self, state: State, cost: int):
        self.distance[state] = cost

    def check_cost(self, state: State, cost: int):
        return self.distance.get(state, INF) > cost and state.player.status != "dead"

    def set_parent(self, state: State, parent: State | None, move: Position | None):
        self.parent[state] = (parent, move)

    def apply_move(self, state: State, move: Position):
        new_state = state.copy()
        MoveCommand(new_state, new_state.player, move).run()
        return new_state

    def __call__(self, state: State):
        heap: list[tuple[int, State]] = []
        heapq.heappush(heap, (0, state))
        self.set_parent(state, None, None)
        self.update_cost(state, 0)
        self.nodes += 1
        while heap:
            cost, current_state = heapq.heappop(heap)
            self.visited_count += 1

            if current_state.is_won():
                self.won_state = current_state
                return

            if self.is_visited(current_state):
                continue

            self.mark_as_visited(current_state)
            self.update_cost(current_state, cost)

            pos = current_state.player.position
            for move in current_state.get_possible_moves(pos, check_blocks=False):
                new_state = self.apply_move(current_state, move)
                new_cost = cost + len(new_state.lavas)
                self.nodes += 1
                if self.check_cost(new_state, new_cost):
                    heapq.heappush(heap, (new_cost, new_state))
                    self.update_cost(new_state, new_cost)
                    self.set_parent(new_state, current_state, move)

    def get_nodes(self) -> int:
        return self.nodes

    def get_visited_count(self) -> int:
        return self.visited_count

    def get_path(self) -> deque[Position]:
        path: deque[Position] = deque()
        current_state = self.won_state
        while current_state is not None:
            parent, move = self.parent[current_state]
            if move is not None:
                path.appendleft(move)
            current_state = parent
        return path


class HillClimb(Algorithm):
    def __init__(self):
        self.visited: dict[State, bool] = {}
        self.parent: dict[State, tuple[State | None, Position | None]] = {}
        self.nodes: int = 0
        self.visited_count: int = 0
        self.won_state: State | None = None

    def set_parent(self, state: State, parent: State | None, move: Position | None):
        self.parent[state] = (parent, move)

    def is_visited(self, state: State):
        return state in self.visited

    def mark_as_visited(self, state: State):
        self.visited[state] = True

    def apply_move(self, state: State, move: Position):
        new_state = state.copy()
        MoveCommand(new_state, new_state.player, move).run()
        return new_state

    def __call__(self, state: State):
        self.run(state)

    def run(
        self,
        state: State,
        parent: State | None = None,
        move: Position | None = None,
    ):
        self.mark_as_visited(state)
        self.set_parent(state, parent, move)

        if state.is_won():
            return True, state

        heap: list[tuple[int, State, Position]] = []
        pos = state.player.position
        for move in state.get_possible_moves(pos, check_blocks=False, check_lavas=True):
            new_state = self.apply_move(state, move)
            c = new_state.manhattan_distance(
                new_state.player.position,
                new_state.goal.position,
            )
            heapq.heappush(heap, (c, new_state, move))

        while heap:
            c, new_state, move = heapq.heappop(heap)
            if not self.is_visited(new_state):
                is_won, won_state = self.run(new_state, state, move)
                if is_won:
                    self.won_state = won_state
                    return is_won, won_state

        return False, None

    def get_nodes(self) -> int:
        return self.nodes

    def get_visited_count(self) -> int:
        return self.visited_count

    def get_path(self) -> deque[Position]:
        path: deque[Position] = deque()
        current_state = self.won_state
        while current_state is not None:
            parent, move = self.parent[current_state]
            if move is not None:
                path.appendleft(move)
            current_state = parent
        return path


class AStar(Algorithm):
    def __init__(self):
        self.visited: dict[State, bool] = {}
        self.parent: dict[State, tuple[State | None, Position | None]] = {}
        self.best_cost: dict[State, int] = {}
        self.nodes: int = 0
        self.visited_count: int = 0
        self.won_state: State | None = None

    def set_parent(self, state: State, parent: State | None, move: Position | None):
        self.parent[state] = (parent, move)

    def is_visited(self, state: State):
        return state in self.visited

    def mark_as_visited(self, state: State):
        self.visited[state] = True

    def apply_move(self, state: State, move: Position):
        new_state = state.copy()
        MoveCommand(new_state, new_state.player, move).run()
        return new_state

    def check(self, state: State, cost: int):
        return state not in self.best_cost or cost < self.best_cost[state]

    def __call__(self, state: State):
        heap: list[tuple[int, State]] = []
        heapq.heappush(heap, (0, state))
        self.set_parent(state, None, None)
        self.best_cost[state] = 0
        self.nodes += 1

        while heap:
            _, curr_state = heapq.heappop(heap)
            self.visited_count += 1

            if curr_state.is_won():
                self.won_state = curr_state
                return

            if self.is_visited(curr_state):
                continue

            pos = curr_state.player.position
            for move in curr_state.get_possible_moves(pos, check_blocks=False):
                new_state = self.apply_move(curr_state, move)
                cost = new_state.manhattan_distance(
                    new_state.player.position,
                    new_state.goal.position,
                )

                if self.is_visited(new_state):
                    continue

                new_cost = self.best_cost[curr_state] + cost
                if self.check(new_state, new_cost):
                    self.best_cost[new_state] = new_cost
                    self.set_parent(new_state, curr_state, move)
                    heapq.heappush(heap, (new_cost, new_state))
                    self.nodes += 1

    def get_nodes(self) -> int:
        return self.nodes

    def get_visited_count(self) -> int:
        return self.visited_count

    def get_path(self) -> deque[Position]:
        path: deque[Position] = deque()
        current_state = self.won_state
        while current_state is not None:
            parent, move = self.parent[current_state]
            if move is not None:
                path.appendleft(move)
            current_state = parent
        return path
