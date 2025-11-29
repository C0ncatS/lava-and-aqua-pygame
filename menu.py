import os
import pygame
from pygame import Vector2

from algorithms import Algorithms


class MenuButton:
    """Generic button class for menus"""
    def __init__(self, text, position, size, color_normal, color_hover, color_border, color_text):
        self.text = text
        self.rect = pygame.Rect(position.x, position.y, size.x, size.y)
        self.hovered = False
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_border = color_border
        self.color_text = color_text

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def render(self, surface, font):
        color = self.color_hover if self.hovered else self.color_normal
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.color_border, self.rect, 3, border_radius=8)

        text_surface = font.render(self.text, True, self.color_text)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class LevelButton:
    def __init__(self, level_name, level_path, position, size):
        self.level_name = level_name
        self.level_path = level_path
        self.rect = pygame.Rect(position.x, position.y, size.x, size.y)
        self.hovered = False
        self.color_normal = (70, 130, 180)  # Steel blue
        self.color_hover = (100, 160, 210)  # Lighter blue
        self.color_border = (40, 90, 140)   # Dark blue
        self.color_text = (255, 255, 255)   # White

    def check_hover(self, mouse_pos):
        """Check if mouse is hovering over this button"""
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def render(self, surface, font):
        """Render the button"""
        color = self.color_hover if self.hovered else self.color_normal

        # Draw button background
        pygame.draw.rect(surface, color, self.rect)

        # Draw border
        pygame.draw.rect(surface, self.color_border, self.rect, 3)

        # Draw text
        text_surface = font.render(self.level_name, True, self.color_text)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class MenuUI:
    def __init__(self, levels_directory="levels"):
        pygame.init()

        self.levels_directory = levels_directory
        self.window_size = Vector2(800, 600)
        self.window = pygame.display.set_mode(
            (int(self.window_size.x), int(self.window_size.y))
        )
        pygame.display.set_caption("Lava & Aqua - Level Selection")

        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_level = None

        # Load font
        self.title_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 48)
        self.button_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 24)
        self.instruction_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 18)

        # Colors
        self.bg_color = (30, 30, 40)
        self.title_color = (255, 200, 100)
        self.instruction_color = (200, 200, 200)

        # Load available levels
        self.level_buttons = self._load_levels()

    def _load_levels(self):
        """Scan the levels directory and create buttons for each level"""
        buttons = []

        # Get all level files
        level_files = []
        for filename in os.listdir(self.levels_directory):
            # Exclude test.txt and only include .txt files
            if filename.endswith('.txt') and filename != 'test.txt':
                level_files.append(filename)

        def get_level_number(filename):
            # Extract number from filename like "level1.txt" -> 1
            try:
                return int(filename.replace('level', '').replace('.txt', ''))
            except:
                return 999

        level_files.sort(key=get_level_number)

        # Create buttons in a grid layout
        button_size = Vector2(150, 80)
        spacing = 20
        start_x = 100
        start_y = 150
        columns = 4

        for index, filename in enumerate(level_files):
            col = index % columns
            row = index // columns

            position = Vector2(
                start_x + col * (button_size.x + spacing),
                start_y + row * (button_size.y + spacing)
            )

            # Create display name (e.g., "Level 1")
            level_number = get_level_number(filename)
            display_name = f"Level {level_number}"

            level_path = os.path.join(self.levels_directory, filename)

            button = LevelButton(display_name, level_path, position, button_size)
            buttons.append(button)

        return buttons

    def process_input(self):
        """Handle user input"""
        mouse_pos = pygame.mouse.get_pos()

        # Update hover states
        for button in self.level_buttons:
            button.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for button in self.level_buttons:
                        if button.check_click(mouse_pos):
                            self.selected_level = button.level_path
                            self.running = False
                            return

    def render(self):
        self.window.fill(self.bg_color)

        # Draw title
        title_text = self.title_font.render("Lava & Aqua", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.window_size.x / 2, 60))
        self.window.blit(title_text, title_rect)

        # Draw instruction
        instruction_text = self.instruction_font.render(
            "Select a level to play (ESC to exit)",
            True,
            self.instruction_color
        )
        instruction_rect = instruction_text.get_rect(
            center=(self.window_size.x / 2, 110)
        )
        self.window.blit(instruction_text, instruction_rect)

        # Draw all level buttons
        for button in self.level_buttons:
            button.render(self.window, self.button_font)

        pygame.display.update()

    def run(self):
        while self.running:
            self.process_input()
            self.render()
            self.clock.tick(60)

        return self.selected_level


class AlgorithmMenu:
    """Menu for selecting the solving algorithm"""
    def __init__(self):
        pygame.init()

        self.window_size = Vector2(800, 600)
        self.window = pygame.display.set_mode(
            (int(self.window_size.x), int(self.window_size.y))
        )
        pygame.display.set_caption("Lava & Aqua - Choose Mode")

        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_algorithm = None

        # Load fonts
        self.title_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 42)
        self.button_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 26)
        self.desc_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 16)

        # Colors
        self.bg_color = (25, 25, 35)
        self.title_color = (255, 200, 100)
        self.desc_color = (180, 180, 180)

        # Create algorithm buttons
        self.buttons = self._create_buttons()

    def _create_buttons(self):
        buttons = []
        button_width = 220
        button_height = 100
        spacing = 40
        total_width = 3 * button_width + 2 * spacing
        start_x = (self.window_size.x - total_width) / 2
        center_y = self.window_size.y / 2

        # Manual play button - green theme
        manual_btn = MenuButton(
            "Manual Play",
            Vector2(start_x, center_y - button_height / 2),
            Vector2(button_width, button_height),
            color_normal=(46, 125, 50),
            color_hover=(76, 175, 80),
            color_border=(27, 94, 32),
            color_text=(255, 255, 255)
        )
        manual_btn.algorithm = None
        manual_btn.description = "Play the level yourself"
        buttons.append(manual_btn)

        # BFS button - blue theme
        bfs_btn = MenuButton(
            "Auto: BFS",
            Vector2(start_x + button_width + spacing, center_y - button_height / 2),
            Vector2(button_width, button_height),
            color_normal=(25, 118, 210),
            color_hover=(66, 165, 245),
            color_border=(13, 71, 161),
            color_text=(255, 255, 255)
        )
        bfs_btn.algorithm = Algorithms.BFS
        bfs_btn.description = "Breadth-First Search (optimal)"
        buttons.append(bfs_btn)

        # DFS button - purple theme
        dfs_btn = MenuButton(
            "Auto: DFS",
            Vector2(start_x + 2 * (button_width + spacing), center_y - button_height / 2),
            Vector2(button_width, button_height),
            color_normal=(123, 31, 162),
            color_hover=(171, 71, 188),
            color_border=(74, 20, 140),
            color_text=(255, 255, 255)
        )
        dfs_btn.algorithm = Algorithms.DFS
        dfs_btn.description = "Depth-First Search (fast)"
        buttons.append(dfs_btn)

        return buttons

    def process_input(self):
        mouse_pos = pygame.mouse.get_pos()

        for button in self.buttons:
            button.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_algorithm = "back"
                return

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.selected_algorithm = "back"
                    return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in self.buttons:
                        if button.check_click(mouse_pos):
                            self.selected_algorithm = button.algorithm
                            self.running = False
                            return

    def render(self):
        self.window.fill(self.bg_color)

        # Draw title
        title_text = self.title_font.render("Choose Play Mode", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.window_size.x / 2, 100))
        self.window.blit(title_text, title_rect)

        # Draw subtitle
        subtitle_text = self.desc_font.render(
            "Press ESC to go back to level selection",
            True,
            self.desc_color
        )
        subtitle_rect = subtitle_text.get_rect(center=(self.window_size.x / 2, 150))
        self.window.blit(subtitle_text, subtitle_rect)

        # Draw buttons and their descriptions
        for button in self.buttons:
            button.render(self.window, self.button_font)

            # Draw description below button
            desc_text = self.desc_font.render(button.description, True, self.desc_color)
            desc_rect = desc_text.get_rect(
                center=(button.rect.centerx, button.rect.bottom + 25)
            )
            self.window.blit(desc_text, desc_rect)

        pygame.display.update()

    def run(self):
        while self.running:
            self.process_input()
            self.render()
            self.clock.tick(60)

        return self.selected_algorithm

