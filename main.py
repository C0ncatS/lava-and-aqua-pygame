import os

import pygame

import algorithms
from menu import MenuUI
from ui import UserInterface
from algorithms import Algorithms


os.environ["SDL_VIDEO_CENTERED"] = "1"

running = True
while running:
    menu = MenuUI()
    selected_level = menu.run()

    if selected_level:
        playing_level = True
        current_level = selected_level

        while playing_level:
            user_interface = UserInterface(current_level, Algorithms.BFS)
            action = user_interface.run()

            if action == "retry":
                continue
            elif action == "menu" or action is None:
                playing_level = False
            else:
                playing_level = False
    else:
        running = False

pygame.quit()


#! player -> block -> aqua -> lava -> timer

# '.' -> 'ground'
# '#' -> 'wall'
# 'I' -> 'container'
# 'B' -> 'block'
# 'U' -> 'player'
# 'A' -> 'aqua'
# 'L' -> 'lava'
# 'G' -> 'goal'
# '*' -> 'point'
# 'digit' -> 'timer'
