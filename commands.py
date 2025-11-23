from abc import ABC, abstractmethod

from items import Block, Liquid, Player, Timer
from position import Position
from state import State


class Command(ABC):
    @abstractmethod
    def run(self):
        pass


class MoveCommand(Command):
    def __init__(self, state: State, player: Player, direction: Position):
        self.state = state
        self.player = player
        self.direction = direction

    def run(self):
        if self.player.status != "alive":
            return

        new_pos = Position.from_vector(
            self.player.position.to_vector()
            + (self.direction.to_vector() * self.player.speed)
        )

        if not self.state.can_move(new_pos, check_blocks=False):
            return

        if new_pos in self.state.blocks:
            block = self.state.blocks[new_pos]
            new_block_pos = Position.from_vector(
                block.position.to_vector() + self.direction.to_vector() * block.speed
            )
            if self.state.can_move(new_block_pos):
                BlockMoveCommand(self.state, block, self.direction).run()
            else:
                return

        self.player.position = new_pos

        if self.state.is_goal(self.player.position):
            self.state.notify_player_reached_goal(self.player)

        # notify observers that the player moved
        self.state.notify_player_moved(self.player, self.direction)

        AquaSpreadCommand(self.state, self.state.aquas).run()
        LavaSpreadCommand(self.state, self.state.lavas).run()
        TimerCommand(self.state, self.state.timers).run()


class BlockMoveCommand(Command):
    def __init__(self, state: State, block: Block, direction: Position):
        self.state = state
        self.block = block
        self.direction = direction

    def run(self):
        # in move command we already check that the block can move. no need to check here
        new_pos = Position.from_vector(
            self.block.position.to_vector()
            + self.direction.to_vector() * self.block.speed
        )
        self.state.blocks.pop(self.block.position)
        new_block = Block(self.state, new_pos, self.block.tile)
        self.state.blocks[new_pos] = new_block
        self.state.notify_block_moved(new_block)


class SpreadCommand(Command):
    moves = [Position(0, 1), Position(1, 0), Position(0, -1), Position(-1, 0)]

    def __init__(self, state: State, liquids: dict[Position, Liquid]):
        self.state = state
        self.liquids = liquids

    def can_move(self, position: Position):
        return self.state.can_move(position, check_containers=False)

    def add(self, position: Position, liquid: Liquid):
        new_liquid = Liquid(self.state, position, liquid.tile)
        self.liquids[position] = new_liquid


class AquaSpreadCommand(SpreadCommand):
    def run(self):
        current_aquas = list(self.liquids.values())
        for aqua in current_aquas:
            for move in self.moves:
                new_pos = Position.from_vector(
                    aqua.position.to_vector() + move.to_vector() * aqua.speed
                )

                if not self.can_move(new_pos):
                    continue

                if new_pos in self.liquids:
                    continue

                if new_pos in self.state.lavas:
                    self.state.notify_aqua_touched_lava(new_pos)
                    continue

                self.add(new_pos, aqua)


class LavaSpreadCommand(SpreadCommand):
    def run(self):
        current_lavas = list(self.liquids.values())
        for lava in current_lavas:
            for move in self.moves:
                new_pos = Position.from_vector(
                    lava.position.to_vector() + move.to_vector() * lava.speed
                )

                if not self.can_move(new_pos):
                    continue

                if new_pos in self.liquids:
                    continue

                if new_pos in self.state.aquas:
                    self.state.notify_lava_touched_aqua(new_pos)
                    continue

                self.add(new_pos, lava)

        if self.state.player.position in self.state.lavas:
            self.state.notify_player_died(self.state.player)


class TimerCommand(Command):
    def __init__(self, state: State, timers: dict[Position, Timer]):
        self.state = state
        self.timers = timers

    def decrement(self, value: int):
        for timer in self.timers.values():
            timer.duration -= value

    def filter(self):
        new_timers = {
            pos: timer for pos, timer in self.timers.items() if timer.duration > 0
        }
        self.timers.clear()
        self.timers.update(new_timers)

    def run(self):
        self.decrement(1)
        self.filter()
