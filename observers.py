class StateObserver:
    def player_moved(self, player, move_vector):
        pass

    def player_died(self, player):
        pass

    def aqua_touched_lava(self, position):
        pass

    def lava_touched_aqua(self, position):
        pass

    def block_moved(self, block):
        pass

    def player_reached_goal(self, player):
        pass

    def player_won(self, player):
        pass

    def state_restored(self, new_state):
        pass