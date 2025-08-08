"""
Display configuration for the Zombicide game.
Centralizes all UI-related constants and settings.
"""
from dataclasses import dataclass
from typing import Tuple
import pygame


@dataclass
class DisplayConfig:
    """Configuration for display settings, colors, fonts, and layout."""
    
    # Window properties
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 900
    FPS: int = 60
    
    # Colors (RGB tuples)
    BLACK: Tuple[int, int, int] = (0, 0, 0)
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    GRAY: Tuple[int, int, int] = (128, 128, 128)
    LIGHT_GRAY: Tuple[int, int, int] = (238, 238, 238)
    BUILDING_COLOR: Tuple[int, int, int] = (210, 180, 140)  # light brown
    STREET_COLOR: Tuple[int, int, int] = (238, 238, 238)   # light gray
    BLUE: Tuple[int, int, int] = (0, 0, 255)
    CYAN: Tuple[int, int, int] = (0, 255, 255)
    YELLOW: Tuple[int, int, int] = (255, 255, 0)
    ORANGE: Tuple[int, int, int] = (255, 165, 0)
    RED: Tuple[int, int, int] = (255, 0, 0)
    DARK_GRAY: Tuple[int, int, int] = (64, 64, 64)
    
    # Layout constants
    TILE_SIZE: int = 3
    ZONE_PIXEL_SIZE: int = 150  # Each zone is 150x150 pixels
    MAP_START_X: int = 50
    MAP_START_Y: int = 50
    WALL_WIDTH: int = 4
    
    # Token properties
    TOKEN_DIAMETER: int = 40
    TOKEN_BORDER_WIDTH: int = 2
    
    # Card properties
    CARD_WIDTH: int = 280
    CARD_HEIGHT: int = 380
    CARD_START_X: int = 550
    CARD_SPACING: int = 20
    
    # Action menu properties
    MENU_WIDTH: int = 300
    MENU_HEIGHT: int = 200
    
    def __post_init__(self):
        """Initialize pygame fonts after pygame is initialized."""
        # Note: Fonts will be created by the renderer when pygame is ready
        self._fonts_initialized = False
        self.font_large = None
        self.font_medium = None
        self.font_small = None
    
    def initialize_fonts(self):
        """Initialize pygame fonts. Call this after pygame.init()."""
        if not self._fonts_initialized:
            self.font_large = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 14)
            self._fonts_initialized = True
    
    @property
    def token_radius(self) -> int:
        """Get token radius from diameter."""
        return self.TOKEN_DIAMETER // 2
    
    @property
    def level_colors(self) -> dict:
        """Get mapping of survivor levels to colors."""
        return {
            'blue': self.BLUE,
            'yellow': self.YELLOW, 
            'orange': self.ORANGE,
            'red': self.RED
        }