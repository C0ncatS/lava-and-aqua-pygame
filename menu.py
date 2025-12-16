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


class AlgorithmConfig:
    """Configuration for an algorithm button"""
    def __init__(self, label, algorithm, description, theme):
        self.label = label
        self.algorithm = algorithm
        self.description = description
        self.theme = theme


class ButtonTheme:
    """Color theme for a button"""
    GREEN = {"normal": (46, 125, 50), "hover": (76, 175, 80), "border": (27, 94, 32)}
    BLUE = {"normal": (25, 118, 210), "hover": (66, 165, 245), "border": (13, 71, 161)}
    PURPLE = {"normal": (123, 31, 162), "hover": (171, 71, 188), "border": (74, 20, 140)}
    ORANGE = {"normal": (230, 126, 34), "hover": (241, 156, 76), "border": (186, 101, 27)}
    TEAL = {"normal": (0, 137, 123), "hover": (38, 166, 154), "border": (0, 105, 92)}


# Add new algorithms here - just add a new AlgorithmConfig to this list
ALGORITHM_OPTIONS = [
    AlgorithmConfig("Manual Play", None, "Play the level yourself", ButtonTheme.GREEN),
    AlgorithmConfig("Auto: BFS", Algorithms.BFS, "Breadth-First Search (optimal)", ButtonTheme.BLUE),
    AlgorithmConfig("Auto: DFS", Algorithms.DFS, "Depth-First Search (fast)", ButtonTheme.PURPLE),
    AlgorithmConfig("Auto: UCS", Algorithms.UCS, "Uniform Cost Search", ButtonTheme.ORANGE),
]


class AlgorithmMenu:
    """Menu for selecting the solving algorithm"""

    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 90
    BUTTON_SPACING = 30
    MAX_COLUMNS = 4

    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_algorithm = None

        # Load fonts
        self.title_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 42)
        self.button_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 22)
        self.desc_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 14)

        # Colors
        self.bg_color = (25, 25, 35)
        self.title_color = (255, 200, 100)
        self.desc_color = (180, 180, 180)

        # Calculate window size based on number of algorithms
        self.window_size = self._calculate_window_size()
        self.window = pygame.display.set_mode(
            (int(self.window_size.x), int(self.window_size.y))
        )
        pygame.display.set_caption("Lava & Aqua - Choose Mode")

        # Create algorithm buttons
        self.buttons = self._create_buttons()

    def _calculate_window_size(self):
        """Calculate window size based on number of algorithm options"""
        num_options = len(ALGORITHM_OPTIONS)
        columns = min(num_options, self.MAX_COLUMNS)
        rows = (num_options + self.MAX_COLUMNS - 1) // self.MAX_COLUMNS

        width = columns * self.BUTTON_WIDTH + (columns + 1) * self.BUTTON_SPACING + 100
        height = 200 + rows * (self.BUTTON_HEIGHT + 60) + 50

        return Vector2(max(600, width), max(400, height))

    def _create_buttons(self):
        """Create buttons dynamically from ALGORITHM_OPTIONS"""
        buttons = []
        num_options = len(ALGORITHM_OPTIONS)
        columns = min(num_options, self.MAX_COLUMNS)

        total_width = columns * self.BUTTON_WIDTH + (columns - 1) * self.BUTTON_SPACING
        start_x = (self.window_size.x - total_width) / 2
        start_y = 180

        for index, config in enumerate(ALGORITHM_OPTIONS):
            col = index % self.MAX_COLUMNS
            row = index // self.MAX_COLUMNS

            position = Vector2(
                start_x + col * (self.BUTTON_WIDTH + self.BUTTON_SPACING),
                start_y + row * (self.BUTTON_HEIGHT + 60)
            )

            btn = MenuButton(
                config.label,
                position,
                Vector2(self.BUTTON_WIDTH, self.BUTTON_HEIGHT),
                color_normal=config.theme["normal"],
                color_hover=config.theme["hover"],
                color_border=config.theme["border"],
                color_text=(255, 255, 255)
            )
            btn.algorithm = config.algorithm
            btn.description = config.description
            buttons.append(btn)

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

