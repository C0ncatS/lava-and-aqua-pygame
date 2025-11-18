from abc import ABC, abstractmethod

from pygame import Vector2

from items import Liquid


class Command(ABC):
    @abstractmethod
    def run(self):
        pass


class MoveCommand(Command):
    def __init__(self, state, player, move_vector):
        self.state = state
        self.player = player
        self.move_vector = move_vector

    def run(self):
        if self.player.status != "alive":
            return

        new_pos = self.player.position + (self.move_vector * self.player.speed)

        if not self.state.can_move(new_pos, check_blocks=False):
            return

        for block in self.state.blocks:
            if block.position == new_pos:
                new_block_pos = block.position + (self.move_vector * block.speed)
                if self.state.can_move(new_block_pos):
                    BlockMoveCommand(self.state, block, self.move_vector).run()
                    break
                else:
                    return

        self.player.position = new_pos

        if self.state.is_goal(self.player.position):
            self.state.notify_player_reached_goal(self.player)

        # notify observers that the player moved
        self.state.notify_player_moved(self.player, self.move_vector)

        AquaSpreadCommand(self.state, self.state.aquas).run()
        LavaSpreadCommand(self.state, self.state.lavas).run()
        TimerCommand(self.state, self.state.timers).run()


class BlockMoveCommand(Command):
    def __init__(self, state, block, move_vector):
        self.state = state
        self.block = block
        self.move_vector = move_vector

    def run(self):
        # in move command we already check that the block can move. no need to check here
        self.block.position += self.move_vector * self.block.speed
        self.state.notify_block_moved(self.block)


class SpreadCommand(Command):
    moves = [Vector2(0, 1), Vector2(1, 0), Vector2(0, -1), Vector2(-1, 0)]

    def __init__(self, state, liquids):
        self.state = state
        self.liquids = liquids

    def can_move(self, position):
        return self.state.can_move(position, check_containers=False)

    def add(self, position, liquid):
        new_liquid = Liquid(self.state, position, liquid.tile)
        self.liquids.append(new_liquid)


class AquaSpreadCommand(SpreadCommand):
    def run(self):
        current_aquas = self.liquids[:]
        for aqua in current_aquas:
            for move in self.moves:
                new_pos = aqua.position + (move * aqua.speed)

                if not self.can_move(new_pos):
                    continue

                if any(liquid.position == new_pos for liquid in self.liquids):
                    continue

                if any(lava.position == new_pos for lava in self.state.lavas):
                    self.state.notify_aqua_touched_lava(new_pos)
                    continue

                self.add(new_pos, aqua)


class LavaSpreadCommand(SpreadCommand):
    def run(self):
        current_lavas = self.liquids[:]
        for lava in current_lavas:
            for move in self.moves:
                new_pos = lava.position + (move * lava.speed)

                if not self.can_move(new_pos):
                    continue

                if any(liquid.position == new_pos for liquid in self.liquids):
                    continue

                if any(aqua.position == new_pos for aqua in self.state.aquas):
                    self.state.notify_lava_touched_aqua(new_pos)
                    continue

                self.add(new_pos, lava)

        for lava in self.liquids:
            for player in self.state.players:
                if player.position == lava.position:
                    self.state.notify_player_died(player)


class TimerCommand(Command):
    def __init__(self, state, timers):
        self.state = state
        self.timers = timers

    def decrement(self, value):
        for timer in self.timers:
            timer.duration -= value

    def filter(self):
        new_timers = [timer for timer in self.timers if timer.duration > 0]
        self.timers[:] = new_timers

    def run(self):
        self.decrement(1)
        self.filter()
