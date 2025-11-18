from abc import ABC, abstractmethod

import pygame
from pygame.math import Vector2

from items import Item
from observers import StateObserver


class Layer(ABC, StateObserver):
    def __init__(self, cell_size, image_file, font_file=None):
        self.cell_size = cell_size
        self.texture = pygame.image.load(image_file)
        self.font = pygame.font.Font(font_file, 24) if font_file else None

    @property
    def cell_width(self):
        return int(self.cell_size.x)

    @property
    def cell_height(self):
        return int(self.cell_size.y)

    def render_font(self, surface, position, text):
        if self.font is None:
            return

        # Convert grid position to screen coordinates
        sprite_point = position.elementwise() * self.cell_size

        text_surface = self.font.render(text, True, (0, 0, 0))
        text_x = int(sprite_point.x + (self.cell_width - text_surface.get_width()) / 2)
        text_y = int(
            sprite_point.y + (self.cell_height - text_surface.get_height()) / 2
        )

        surface.blit(text_surface, (text_x, text_y))

    def render_tile(self, surface, position, tile):
        # Location on the screen
        sprite_point = position.elementwise() * self.cell_size

        # Texture
        texture_point = tile.elementwise() * self.cell_size
        texture_rect = pygame.Rect(
            int(texture_point.x),
            int(texture_point.y),
            self.cell_width,
            self.cell_height,
        )

        # Get the actual size of the texture portion being used
        # Clamp to texture bounds to get actual size
        actual_texture_rect = texture_rect.clip(self.texture.get_rect())
        actual_width = actual_texture_rect.width
        actual_height = actual_texture_rect.height

        # Extract the texture portion
        texture_surface = pygame.Surface(
            (actual_width, actual_height), flags=pygame.SRCALPHA
        )
        texture_surface.blit(self.texture, (0, 0), actual_texture_rect)

        # Scale the texture to fit the cell size (stretch if smaller, shrink if bigger)
        scaled_texture = pygame.transform.scale(
            texture_surface, (self.cell_width, self.cell_height)
        )

        # Render the scaled tile at the sprite point
        surface.blit(scaled_texture, (int(sprite_point.x), int(sprite_point.y)))

    @abstractmethod
    def render(self, surface):
        pass


class ArrayLayer(Layer):
    def __init__(
        self,
        cell_size,
        image_file,
        state,
        array,
        surface_flags=pygame.SRCALPHA,
    ):
        super().__init__(cell_size, image_file)
        self.state = state
        self.array = array
        self.surface = None
        self.surface_flags = surface_flags

    def render(self, surface):
        if self.surface is None:
            self.surface = pygame.Surface(surface.get_size(), flags=self.surface_flags)
            for y in range(self.state.world_height):
                for x in range(self.state.world_width):
                    tile = self.array[y][x]
                    if not tile is None:
                        self.render_tile(self.surface, Vector2(x, y), tile)

        surface.blit(self.surface, (0, 0))

    def state_restored(self, new_state):
        self.state = new_state


class GroundLayer(ArrayLayer):
    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.array = new_state.ground


class UnitLayer(Layer):
    def __init__(self, cell_size, image_file, state, units):
        super().__init__(cell_size, image_file)
        self.state = state
        self.units = units

    def render(self, surface):
        for unit in self.units:
            self.render_tile(surface, unit.position, unit.tile)

    def state_restored(self, new_state):
        self.state = new_state


class WallLayer(UnitLayer):
    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.units = new_state.walls


class ContainerLayer(UnitLayer):
    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.units = new_state.containers


class StoneLayer(UnitLayer):
    def add(self, position):
        new_stone = Item(self.state, position, Vector2(0, 0))
        self.units.append(new_stone)
        for player in self.state.players:
            if player.position == position:
                self.state.notify_player_died(player)

    def aqua_touched_lava(self, position):
        self.add(position)

    def lava_touched_aqua(self, position):
        self.add(position)

    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.units = new_state.stones


class GoalLayer(UnitLayer):
    def player_reached_goal(self, player):
        if self.state.is_points_empty():
            player.status = "won"
            self.state.notify_player_won(player)

    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.units = new_state.goals


class LiquidLayer(UnitLayer):
    def block_moved(self, block):
        new_liquids = [
            liquid for liquid in self.units if liquid.position != block.position
        ]
        self.units[:] = new_liquids

    def reduce(self, position):
        new_liquids = [liquid for liquid in self.units if liquid.position != position]
        self.units[:] = new_liquids


class AquaLayer(LiquidLayer):
    def lava_touched_aqua(self, position):
        self.reduce(position)

    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.units = new_state.aquas


class LavaLayer(LiquidLayer):
    def aqua_touched_lava(self, position):
        self.reduce(position)

    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.units = new_state.lavas


class PlayerLayer(UnitLayer):
    def player_died(self, player):
        for p in self.units:
            if p.position == player.position:
                p.status = "dead"

    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.units = new_state.players


class DeadLayer(UnitLayer):
    def add(self, player):
        dead = Item(self.state, player.position, player.tile)
        self.units.append(dead)

    def player_died(self, player):
        self.add(player)

    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.units = new_state.deads


class BlockLayer(UnitLayer):
    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.units = new_state.blocks


class PointLayer(UnitLayer):
    def update(self, player):
        new_points = [
            point for point in self.units if point.position != player.position
        ]
        self.units[:] = new_points

    def player_moved(self, player, move_vector):
        self.update(player)

    def state_restored(self, new_state):
        super().state_restored(new_state)
        self.units = new_state.points


class TimerLayer(Layer):
    def __init__(self, cell_size, image_file, font_file, state, timers):
        super().__init__(cell_size, image_file, font_file)
        self.state = state
        self.timers = timers

    def render(self, surface):
        for timer in self.timers:
            self.render_tile(surface, timer.position, timer.tile)
            self.render_font(surface, timer.position, str(int(timer.duration)))

    def state_restored(self, new_state):
        self.state = new_state
        self.timers = new_state.timers
