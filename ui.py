import os

import pygame
from pygame import Vector2

from state import State
from observers import Observer
from layers import (
    GroundLayer,
    BlockLayer,
    DeadLayer,
    PlayerLayer,
    TimerLayer,
    PointLayer,
    AquaLayer,
    LavaLayer,
    StoneLayer,
    GoalLayer,
    ContainerLayer,
    WallLayer,
)
from commands import MoveCommand
from popup import GameOverPopup, VictoryPopup
from history import HistoryManager
from position import Position
from algorithms import Algorithms
from factories import DFSFactory, BFSFactory, UCSFactory, HillClimbFactory


class UserInterface(Observer):
    def __init__(
        self,
        level_file="levels/level1.txt",
        solve_algo: Algorithms | None = None,
    ):
        pygame.init()

        self.level_file = level_file
        self.solve_algo = solve_algo
        self.state = State(self.level_file)

        self.cell_size = Vector2(48, 48)
        self.layers = [
            GroundLayer(
                self.cell_size,
                "assets/ground.png",
                self.state,
                self.state.ground,
                0,
            ),
            TimerLayer(
                self.cell_size,
                "assets/timer.png",
                "fonts/NotoSans-Bold.ttf",
                self.state,
                self.state.timers,
            ),
            LavaLayer(
                self.cell_size,
                "assets/lava.png",
                self.state,
                self.state.lavas,
            ),
            AquaLayer(
                self.cell_size,
                "assets/aqua.png",
                self.state,
                self.state.aquas,
            ),
            GoalLayer(
                self.cell_size,
                "assets/goal.png",
                self.state,
                self.state.goal,
            ),
            BlockLayer(
                self.cell_size,
                "assets/block.png",
                self.state,
                self.state.blocks,
            ),
            PlayerLayer(
                self.cell_size,
                "assets/player.png",
                self.state,
                self.state.player,
            ),
            DeadLayer(
                self.cell_size,
                "assets/dead.png",
                self.state,
                self.state.deads,
            ),
            PointLayer(
                self.cell_size,
                "assets/point.png",
                self.state,
                self.state.points,
            ),
            ContainerLayer(
                self.cell_size,
                "assets/container.png",
                self.state,
                self.state.containers,
            ),
            StoneLayer(
                self.cell_size,
                "assets/wall.png",
                self.state,
                self.state.stones,
            ),
            WallLayer(
                self.cell_size,
                "assets/wall.png",
                self.state,
                self.state.walls,
            ),
        ]

        self.commands = []
        self.player = self.state.player
        self.goal = self.state.goal

        self.history = HistoryManager(max_history_size=100, state=self.state)

        self.state.clear_observers()
        for layer in reversed(self.layers):
            self.state.add_observer(layer)

        self.state.add_observer(self)

        window_size = self.state.world_size.elementwise() * self.cell_size
        self.window_size = window_size
        self.window = pygame.display.set_mode(
            (int(window_size.x), int(window_size.y)),
            pygame.RESIZABLE,
        )

        # Set window caption to show the current level
        level_name = os.path.basename(self.level_file).replace(".txt", "").replace("level", "Level ")
        pygame.display.set_caption(f"Lava & Aqua - {level_name} - {self.solve_algo.value}")

        # Create popups
        self.game_over_popup = GameOverPopup(window_size)
        self.victory_popup = VictoryPopup(window_size)
        self.paused = False
        self.popup_action = None

        self.clock = pygame.time.Clock()
        self.running = True

    def process_input(self):
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        # Handle popup input first
        if self.paused:
            action = None
            if self.game_over_popup.visible:
                action = self.game_over_popup.process_input(events, mouse_pos)
            elif self.victory_popup.visible:
                action = self.victory_popup.process_input(events, mouse_pos)

            if action:
                self.popup_action = action
                self.running = False

            for event in events:
                if event.type == pygame.QUIT:
                    self.popup_action = "menu"
                    self.running = False

            return

        move = Vector2(0, 0)
        undo_requested = False
        redo_requested = False

        for event in events:
            if event.type == pygame.QUIT:
                self.popup_action = "menu"
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.popup_action = "menu"
                    self.running = False
                    break
                elif event.key == pygame.K_z:
                    undo_requested = True
                elif event.key == pygame.K_u:
                    redo_requested = True
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    move.x = 1
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    move.x = -1
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    move.y = 1
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    move.y = -1

        # Handle undo
        if undo_requested:
            self.perform_undo()
        # Handle redo
        elif redo_requested:
            self.perform_redo()
        # Handle movement
        elif move.x != 0 or move.y != 0:
            command = MoveCommand(self.state, self.player, Position.from_vector(move))
            self.commands.append(command)

    def update(self):
        if self.commands:
            self.history.save_state(self.state)

        for command in self.commands:
            command.run()
        self.commands.clear()

    def render(self):
        self.window.fill((0, 0, 0))

        for layer in self.layers:
            layer.render(self.window)

        # Draw popups on top
        self.game_over_popup.render(self.window)
        self.victory_popup.render(self.window)

        pygame.display.update()

    def perform_undo(self):
        if not self.history.can_undo():
            return

        restored_state = self.history.undo()
        if restored_state:
            self.restore_state(restored_state)

    def perform_redo(self):
        if not self.history.can_redo():
            return

        restored_state = self.history.redo()
        if restored_state:
            self.restore_state(restored_state)

    def restore_state(self, new_state):
        self.state = new_state

        self.player = self.state.player if self.state.player else self.player
        self.goal = self.state.goal if self.state.goal else self.goal

        self.state.clear_observers()
        for layer in reversed(self.layers):
            self.state.add_observer(layer)

        self.state.add_observer(self)

        self.state.notify_state_restored()

    def player_died(self, player):
        self.paused = True
        self.game_over_popup.show()

    def player_won(self, player):
        self.paused = True
        self.victory_popup.show()

    def solve(self):
        path = None
        if self.solve_algo == Algorithms.DFS:
            dfs = DFSFactory()
            path = dfs.solve(self.state)
        elif self.solve_algo == Algorithms.BFS:
            bfs = BFSFactory()
            path = bfs.solve(self.state)
        elif self.solve_algo == Algorithms.UCS:
            ucs = UCSFactory()
            path = ucs.solve(self.state)
        elif self.solve_algo == Algorithms.HILL_CLIMB:
            hill_climb = HillClimbFactory()
            path = hill_climb.solve(self.state)
        return path

    def run(self):
        path = self.solve()
        timer = 0
        while self.running:
            self.process_input()
            if path and timer == 0:
                self.commands.append(
                    MoveCommand(self.state, self.player, path.popleft())
                )
                timer += 10
            self.update()
            self.render()
            self.clock.tick(60)
            timer -= 1

        return self.popup_action
