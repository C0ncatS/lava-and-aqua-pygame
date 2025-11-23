from items import Block, Player
from position import Position
from state import State


class StateObserver:
    def player_moved(self, player: Player, direction: Position):
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

    def state_restored(self, new_state: State):
        pass
