from typing import TYPE_CHECKING

from pygame.math import Vector2

from items import Item, Block, Player
from position import Position

if TYPE_CHECKING:
    from state import State


class Observer:
    def player_moved(self, player: Player, move: Position):
        pass

    def player_died(self, player: Player):
        pass

    def aqua_touched_lava(self, position: Position):
        pass

    def lava_touched_aqua(self, position: Position):
        pass

    def block_moved(self, block: Block):
        pass

    def player_reached_goal(self, player: Player):
        pass

    def player_won(self, player: Player):
        pass

    def state_restored(self, new_state: "State"):
        pass


class StateObserver(Observer):
    def __init__(self, state: "State"):
        self.state = state

    def state_restored(self, new_state):
        self.state = new_state


class StoneObserver(StateObserver):
    def add(self, position: Position):
        new_stone = Item(self.state, position, Vector2(0, 0))
        self.state.stones[position] = new_stone
        if self.state.player.position == position:
            self.state.notify_player_died(self.state.player)

    def aqua_touched_lava(self, position):
        self.add(position)

    def lava_touched_aqua(self, position):
        self.add(position)


class GoalObserver(StateObserver):
    def player_reached_goal(self, player):
        if self.state.is_points_empty():
            player.status = "won"
            self.state.notify_player_won(player)


class AquaObserver(StateObserver):
    def reduce(self, position: Position):
        if position in self.state.aquas:
            self.state.aquas.pop(position)

    def block_moved(self, block):
        self.reduce(block.position)

    def lava_touched_aqua(self, position):
        self.reduce(position)


class LavaObserver(StateObserver):
    def reduce(self, position: Position):
        if position in self.state.lavas:
            self.state.lavas.pop(position)

    def block_moved(self, block):
        self.reduce(block.position)

    def aqua_touched_lava(self, position):
        self.reduce(position)


class PlayerObserver(StateObserver):
    def player_died(self, player):
        player.status = "dead"


class DeadObserver(StateObserver):
    def add(self, position: Position):
        dead = Item(self.state, position, Vector2(0, 0))
        self.state.deads[position] = dead

    def player_died(self, player):
        self.add(player.position)


class PointObserver(StateObserver):
    def update(self, position: Position):
        if position in self.state.points:
            self.state.points.pop(position)

    def player_moved(self, player, move):
        self.update(player.position)
