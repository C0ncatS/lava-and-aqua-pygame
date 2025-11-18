import pygame
from pygame import Vector2


class PopupButton:
    def __init__(self, text, action, position, size):
        self.text = text
        self.action = action  # Action to return when clicked (e.g., 'retry', 'menu', 'next')
        self.rect = pygame.Rect(position.x, position.y, size.x, size.y)
        self.hovered = False
        self.color_normal = (70, 130, 180)
        self.color_hover = (100, 160, 210)
        self.color_border = (40, 90, 140)
        self.color_text = (255, 255, 255)
        
    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered
    
    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def render(self, surface, font):
        color = self.color_hover if self.hovered else self.color_normal
        
        # Draw button background
        pygame.draw.rect(surface, color, self.rect)
        
        # Draw border
        pygame.draw.rect(surface, self.color_border, self.rect, 3)
        
        # Draw text
        text_surface = font.render(self.text, True, self.color_text)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class GameOverPopup:
    def __init__(self, window_size):
        self.window_size = window_size
        self.visible = False
        self.selected_action = None
        
        # Load fonts
        self.title_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 48)
        self.button_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 24)
        
        # Colors
        self.overlay_color = (0, 0, 0, 180)  # Semi-transparent black
        self.title_color = (255, 100, 100)  # Red for death
        
        # Create buttons
        button_size = Vector2(150, 60)
        button_spacing = 20
        center_x = window_size.x / 2
        center_y = window_size.y / 2 + 50
        
        self.buttons = [
            PopupButton(
                "Retry",
                "retry",
                Vector2(center_x - button_size.x - button_spacing / 2, center_y),
                button_size
            ),
            PopupButton(
                "Menu",
                "menu",
                Vector2(center_x + button_spacing / 2, center_y),
                button_size
            )
        ]
    
    def show(self):
        """Show the popup"""
        self.visible = True
        self.selected_action = None
    
    def hide(self):
        """Hide the popup"""
        self.visible = False
    
    def process_input(self, events, mouse_pos):
        if not self.visible:
            return None
        
        # Update hover states
        for button in self.buttons:
            button.check_hover(mouse_pos)
        
        # Check for clicks
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for button in self.buttons:
                        if button.check_click(mouse_pos):
                            self.selected_action = button.action
                            return self.selected_action
        
        return None
    
    def render(self, surface):
        if not self.visible:
            return
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.window_size.x, self.window_size.y))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self.title_font.render("You Died!", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.window_size.x / 2, self.window_size.y / 2 - 80))
        surface.blit(title_text, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.render(surface, self.button_font)


class VictoryPopup:
    def __init__(self, window_size):
        self.window_size = window_size
        self.visible = False
        self.selected_action = None
        
        # Load fonts
        self.title_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 48)
        self.subtitle_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 24)
        self.button_font = pygame.font.Font("fonts/NotoSans-Bold.ttf", 24)
        
        # Colors
        self.title_color = (100, 255, 100)  # Green for victory
        self.subtitle_color = (200, 200, 200)
        
        # Create buttons
        button_size = Vector2(150, 60)
        button_spacing = 20
        center_x = window_size.x / 2
        center_y = window_size.y / 2 + 80
        
        self.buttons = [
            PopupButton(
                "Retry",
                "retry",
                Vector2(center_x - button_size.x - button_spacing / 2, center_y),
                button_size
            ),
            PopupButton(
                "Menu",
                "menu",
                Vector2(center_x + button_spacing / 2, center_y),
                button_size
            )
        ]
    
    def show(self):
        """Show the popup"""
        self.visible = True
        self.selected_action = None
    
    def hide(self):
        """Hide the popup"""
        self.visible = False
    
    def process_input(self, events, mouse_pos):
        if not self.visible:
            return None
        
        # Update hover states
        for button in self.buttons:
            button.check_hover(mouse_pos)
        
        # Check for clicks
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for button in self.buttons:
                        if button.check_click(mouse_pos):
                            self.selected_action = button.action
                            return self.selected_action
        
        return None
    
    def render(self, surface):
        if not self.visible:
            return
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.window_size.x, self.window_size.y))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self.title_font.render("Victory!", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.window_size.x / 2, self.window_size.y / 2 - 100))
        surface.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.subtitle_font.render("Level Complete!", True, self.subtitle_color)
        subtitle_rect = subtitle_text.get_rect(center=(self.window_size.x / 2, self.window_size.y / 2 - 50))
        surface.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.render(surface, self.button_font)

