"""
ConfigurationManager for the Zombicide game.
Centralized configuration management following domain-driven design principles.
"""
from dataclasses import dataclass, field
from typing import Dict, Tuple
import pygame


@dataclass
class DisplayConfig:
    """All display-related configuration in one place."""
    
    # Window properties
    window_width: int = 1200
    window_height: int = 900
    fps: int = 60
    
    # Colors (RGB tuples)
    colors: Dict[str, Tuple[int, int, int]] = field(default_factory=lambda: {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'gray': (128, 128, 128),
        'light_gray': (238, 238, 238),
        'building_color': (210, 180, 140),
        'street_color': (238, 238, 238),
        'blue': (0, 0, 255),
        'cyan': (0, 255, 255),
        'yellow': (255, 255, 0),
        'orange': (255, 165, 0),
        'red': (255, 0, 0),
        'dark_gray': (64, 64, 64)
    })
    
    # Layout constants
    tile_size: int = 3
    zone_pixel_size: int = 150
    map_start_x: int = 50
    map_start_y: int = 50
    wall_width: int = 4
    
    # Token properties
    token_diameter: int = 40
    token_border_width: int = 2
    
    # Card properties
    card_width: int = 280
    card_height: int = 380
    card_start_x: int = 550
    card_spacing: int = 20
    
    # Action menu properties
    menu_width: int = 300
    menu_height: int = 200
    
    # Fonts (initialized after pygame setup)
    fonts: Dict[str, pygame.font.Font] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize after creation."""
        self._fonts_initialized = False
    
    def initialize_fonts(self):
        """Initialize pygame fonts. Call after pygame.init()."""
        if not self._fonts_initialized:
            self.fonts = {
                'large': pygame.font.Font(None, 24),
                'medium': pygame.font.Font(None, 18),
                'small': pygame.font.Font(None, 14)
            }
            self._fonts_initialized = True
    
    @property
    def token_radius(self) -> int:
        """Get token radius from diameter."""
        return self.token_diameter // 2
    
    @property
    def level_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """Get mapping of survivor levels to colors."""
        return {
            'blue': self.colors['blue'],
            'yellow': self.colors['yellow'],
            'orange': self.colors['orange'],
            'red': self.colors['red']
        }


@dataclass
class GameConfig:
    """Game-specific configuration."""
    
    # Turn timing
    auto_advance_delay: int = 2000  # milliseconds
    
    # Gameplay constants
    max_survivor_actions: int = 3
    max_wounds: int = 2
    
    # Debug settings
    debug_mode: bool = False
    show_coordinates: bool = False


@dataclass
class InputConfig:
    """Input handling configuration."""
    
    # Key bindings
    key_bindings: Dict[str, int] = field(default_factory=lambda: {
        'quit': pygame.K_ESCAPE,
        'phase_advance': pygame.K_SPACE,
        'pause_toggle': pygame.K_p,
        'action_1': pygame.K_1,
        'action_2': pygame.K_2,
        'action_3': pygame.K_3
    })
    
    # Mouse settings
    mouse_enabled: bool = True
    double_click_threshold: int = 500  # milliseconds


class ConfigurationManager:
    """Centralized configuration management for all game systems."""
    
    def __init__(self):
        """Initialize with default configurations."""
        self.display = DisplayConfig()
        self.game = GameConfig()
        self.input = InputConfig()
    
    def initialize_pygame_dependent_configs(self):
        """Initialize configurations that depend on pygame being initialized."""
        self.display.initialize_fonts()
    
    def update_window_size(self, width: int, height: int):
        """Update window dimensions."""
        self.display.window_width = width
        self.display.window_height = height
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off."""
        self.game.debug_mode = not self.game.debug_mode
        return self.game.debug_mode
    
    def get_color(self, color_name: str) -> Tuple[int, int, int]:
        """Get color by name with fallback to white."""
        return self.display.colors.get(color_name, self.display.colors['white'])
    
    def get_font(self, font_name: str) -> pygame.font.Font:
        """Get font by name with fallback to medium."""
        return self.display.fonts.get(font_name, self.display.fonts.get('medium'))