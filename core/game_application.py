"""
GameApplication coordinates all game components and manages the main game loop.
This class brings together rendering, input handling, game state, and turn management.
"""
import pygame
import sys
from typing import Dict, List, Any, Optional
from .turn_manager import TurnManager, TurnPhase
from .entities import GameState
from .game_setup import GameSetup, GameSetupError
from ui.rendering.game_renderer import GameRenderer
from ui.input.input_manager import InputManager, GameEvent, GameEventType
from config.display_config import DisplayConfig


class GameApplication:
    """Main game application coordinator."""
    
    def __init__(self, width: int = 1200, height: int = 900, title: str = "Zombicide Game"):
        """Initialize the game application."""
        # Initialize pygame
        pygame.init()
        
        # Configuration
        self.config = DisplayConfig()
        self.config.WINDOW_WIDTH = width
        self.config.WINDOW_HEIGHT = height
        
        # Pygame setup
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game components
        self.renderer = GameRenderer(self.screen, self.config)
        self.input_manager = InputManager()
        self.turn_manager = TurnManager()
        self.game_state = GameState()
        
        # Game data
        self.map_data: Optional[Dict[str, Any]] = None
        self.survivors_data: List[Dict[str, Any]] = []
        
        # Setup turn manager callbacks
        self.turn_manager.on_phase_change = self.on_phase_change
        self.turn_manager.on_turn_change = self.on_turn_change
        
        print("GameApplication initialized")
    
    def load_game_data(self, maps_json_path: str, survivors_json_path: str, map_index: int = 0):
        """
        Load game data from JSON files and initialize game state.
        
        Args:
            maps_json_path: Path to maps JSON file
            survivors_json_path: Path to survivors JSON file  
            map_index: Index of map to load
            
        Raises:
            GameSetupError: If loading fails
        """
        try:
            self.map_data, self.survivors_data, self.game_state = GameSetup.setup_complete_game(
                maps_json_path, survivors_json_path, map_index
            )
            print("Game data loaded successfully")
        except GameSetupError as e:
            print(f"Failed to load game data: {e}")
            raise
    
    def run(self):
        """Run the main game loop."""
        if not self.map_data or not self.survivors_data:
            raise RuntimeError("Game data not loaded. Call load_game_data() first.")
            
        print("Starting main game loop...")
        last_time = pygame.time.get_ticks()
        
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            dt = current_time - last_time
            last_time = current_time
            
            # Process input
            self.handle_input()
            
            # Update game state
            self.update(dt)
            
            # Render frame
            self.render()
            
            # Maintain target FPS
            self.clock.tick(self.config.FPS)
        
        print("Game loop ended")
    
    def handle_input(self):
        """Process input events."""
        events = self.input_manager.process_events()
        
        # Check for quit request
        if self.input_manager.is_quit_requested():
            self.running = False
            return
        
        # Process game events
        for event in events:
            self.handle_game_event(event)
    
    def handle_game_event(self, event: GameEvent):
        """Handle a specific game event."""
        if event.event_type == GameEventType.PHASE_ADVANCE:
            # Only advance if not waiting for survivor action
            if not self.turn_manager.is_waiting_for_action():
                print(f"Manual phase advance: {self.turn_manager.get_phase_name()}")
                self.turn_manager.advance_phase()
                
        elif event.event_type == GameEventType.PAUSE_TOGGLE:
            self.turn_manager.game_paused = not self.turn_manager.game_paused
            print(f"Game {'paused' if self.turn_manager.game_paused else 'unpaused'}")
            
        elif event.event_type == GameEventType.SURVIVOR_ACTION:
            # Handle survivor action selection during their turn
            if (self.turn_manager.is_waiting_for_action() and 
                self.turn_manager.get_current_phase() == TurnPhase.SURVIVOR_TURN):
                action_index = event.data.get("action_index", -1)
                if action_index >= 0:
                    success = self.turn_manager.select_action(action_index)
                    if not success:
                        print(f"Invalid action selection: {action_index}")
    
    def update(self, dt: int):
        """Update game state."""
        if not self.running:
            return
            
        # Update turn manager
        self.turn_manager.update(dt)
        
        # Process current turn phase
        current_phase = self.turn_manager.get_current_phase()
        
        if current_phase == TurnPhase.SURVIVOR_TURN:
            self.turn_manager.process_survivor_turn(self.game_state)
        elif current_phase == TurnPhase.ZOMBIE_TURN:
            self.turn_manager.process_zombie_turn(self.game_state)
        elif current_phase == TurnPhase.ZOMBIE_SPAWN:
            self.turn_manager.process_zombie_spawn()
        elif current_phase == TurnPhase.TURN_END:
            self.turn_manager.process_turn_end()
    
    def render(self):
        """Render the current frame."""
        # Get current state for rendering
        current_survivor = self.turn_manager.get_current_survivor()
        available_actions = None
        
        # Only show action menu if waiting for input
        if self.turn_manager.is_waiting_for_action():
            available_actions = self.turn_manager.get_available_actions()
        
        # Get turn information
        turn_info = self.turn_manager.get_turn_info()
        
        # Render complete frame
        self.renderer.render_frame(
            map_data=self.map_data,
            survivors=self.game_state.survivors,
            zombies=self.game_state.zombies,
            survivors_data=self.survivors_data,
            turn_info=turn_info,
            current_survivor=current_survivor,
            available_actions=available_actions
        )
    
    def on_phase_change(self, new_phase):
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
        return {
            "running": self.running,
            "turn_info": self.turn_manager.get_turn_info(),
            "survivors_count": len(self.game_state.survivors),
            "zombies_count": len(self.game_state.zombies),
            "map_loaded": self.map_data is not None,
            "survivors_loaded": len(self.survivors_data) > 0
        }