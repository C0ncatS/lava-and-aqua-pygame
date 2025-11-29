from abc import ABC, abstractmethod
from collections import deque
import time

from algorithms import Algorithm, DFS, BFS
from state import State
from position import Position


class AlgorithmFactory(ABC):
    @abstractmethod
    def create(self) -> Algorithm:
        pass

    def solve(self, state: State) -> deque[Position] | None:
        algorithm = self.create()
        start_time = time.time()
        algorithm(state)
        end_time = time.time()
        nodes = algorithm.get_nodes()
        visited_count = algorithm.get_visited_count()
        path = algorithm.get_path()
        print(f"Time taken: {end_time - start_time} seconds")
        print(f"Nodes: {nodes}")
        print(f"Visited count: {visited_count}")
        print(f"Path length: {len(path)}")
        return path


class DFSFactory(AlgorithmFactory):
    def __init__(self, depth_limit: int = 200):
        self.depth_limit = depth_limit

    def create(self) -> Algorithm:
        return DFS(self.depth_limit)


class BFSFactory(AlgorithmFactory):
    def create(self) -> Algorithm:
        return BFS()
