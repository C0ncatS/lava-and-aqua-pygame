import os
import pygame
from pygame import Vector2


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

