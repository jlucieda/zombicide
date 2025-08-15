"""
GameApplication using domain-based architecture.
Coordinates all game systems and manages the application lifecycle.
"""
import pygame
import sys
from typing import Dict, Any
from .turn_manager import TurnManager
from .game_setup import GameSetup, GameSetupError
from systems.configuration_manager import ConfigurationManager
from systems.rendering_system import RenderingSystem
from systems.input_system import InputSystem
from systems.game_loop import GameLoop, GameWorld


class GameApplication:
    """Main game application using domain-based architecture."""
    
    def __init__(self, width: int = 1200, height: int = 900, title: str = "Zombicide Game"):
        """Initialize the game application with new systems architecture."""
        # Initialize pygame
        pygame.init()
        
        # Configuration management
        self.config_manager = ConfigurationManager()
        self.config_manager.update_window_size(width, height)
        self.config_manager.initialize_pygame_dependent_configs()
        
        # Pygame setup
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        # Game systems
        self.rendering_system = RenderingSystem(self.screen, self.config_manager)
        self.input_system = InputSystem(self.config_manager)
        
        # Game world state
        self.game_world = GameWorld()
        
        # Game components (will be initialized in load_game_data)
        self.turn_manager = None
        self.game_state = None
        self.game_loop = None
        
        print("GameApplication initialized with domain-based architecture")
    
    def load_game_data(self, maps_json_path: str, survivors_json_path: str, map_index: int = 0):
        """
        Load game data and initialize game systems.
        
        Args:
            maps_json_path: Path to maps JSON file
            survivors_json_path: Path to survivors JSON file  
            map_index: Index of map to load
            
        Raises:
            GameSetupError: If loading fails
        """
        try:
            map_data, survivors_data, game_state = GameSetup.setup_complete_game(
                maps_json_path, survivors_json_path, map_index
            )
            
            # Initialize game components
            self.turn_manager = TurnManager()
            self.game_state = game_state
            
            # Setup turn manager callbacks
            self.turn_manager.on_phase_change = self.on_phase_change
            self.turn_manager.on_turn_change = self.on_turn_change
            
            # Update game world
            self.game_world.map_data = map_data
            self.game_world.survivors_data = survivors_data
            self.game_world.survivors = game_state.survivors
            self.game_world.zombies = game_state.zombies
            self.game_world.game_state = game_state
            
            # Initialize game loop with systems
            self.game_loop = GameLoop(
                self.config_manager,
                self.rendering_system,
                self.input_system,
                self.game_world
            )
            self.game_loop.set_game_components(self.turn_manager, self.game_state)
            
            print("Game data loaded and systems initialized successfully")
        except GameSetupError as e:
            print(f"Failed to load game data: {e}")
            raise
    
    def run(self):
        """Run the main game loop using the new systems architecture."""
        if not self.game_loop:
            raise RuntimeError("Game data not loaded. Call load_game_data() first.")
        
        try:
            self.game_loop.run()
        except KeyboardInterrupt:
            print("\nGame interrupted by user")
        except Exception as e:
            print(f"Game loop error: {e}")
            raise
    
    
    def on_phase_change(self, _new_phase):
        """Callback when turn phase changes."""
        print(f"Phase changed to: {self.turn_manager.get_phase_name()}")
    
    def on_turn_change(self, new_turn):
        """Callback when turn number changes.""" 
        print(f"Starting turn {new_turn}")
    
    def cleanup(self):
        """Clean up pygame resources and exit."""
        pygame.quit()
        sys.exit()
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get information about the current game state (for debugging)."""
        if not self.game_loop or not self.turn_manager:
            return {"status": "not_initialized"}
        
        return {
            "running": self.game_loop.running,
            "turn_info": self.turn_manager.get_turn_info() if self.turn_manager else {},
            "survivors_count": len(self.game_state.survivors) if self.game_state else 0,
            "zombies_count": len(self.game_state.zombies) if self.game_state else 0,
            "map_loaded": self.game_world.map_data is not None,
            "survivors_loaded": len(self.game_world.survivors_data) > 0
        }