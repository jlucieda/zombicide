"""
GameLoop for the Zombicide game.
Core game loop with timing and systems coordination.
"""
import pygame
from typing import Dict, Any, List
from abc import ABC, abstractmethod

from .configuration_manager import ConfigurationManager
from .rendering_system import RenderingSystem
from .input_system import InputSystem, InputEvent


class GameSystem(ABC):
    """Base class for all game systems."""
    
    @abstractmethod
    def update(self, dt: int, game_world: Dict[str, Any]) -> Dict[str, Any]:
        """Update the system and return any state changes."""
        pass


class TimingSystem(GameSystem):
    """Handles game timing and frame rate management."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config = config_manager
        self.clock = pygame.time.Clock()
        self.last_time = pygame.time.get_ticks()
    
    def update(self, dt: int, game_world: Dict[str, Any]) -> Dict[str, Any]:
        """Update timing information."""
        current_time = pygame.time.get_ticks()
        actual_dt = current_time - self.last_time
        self.last_time = current_time
        
        return {
            "timing": {
                "delta_time": actual_dt,
                "fps": self.clock.get_fps(),
                "target_fps": self.config.display.fps
            }
        }
    
    def tick(self) -> int:
        """Maintain target FPS and return delta time."""
        return self.clock.tick(self.config.display.fps)


class GameStateSystem(GameSystem):
    """Manages core game state updates."""
    
    def __init__(self, turn_manager, game_state):
        self.turn_manager = turn_manager
        self.game_state = game_state
    
    def update(self, dt: int, game_world: Dict[str, Any]) -> Dict[str, Any]:
        """Update game state through turn manager."""
        if not game_world.get("running", True):
            return {}
        
        # Update turn manager
        self.turn_manager.update(dt)
        
        # Process current turn phase
        current_phase = self.turn_manager.get_current_phase()
        
        # Import here to avoid circular imports
        from core.turn_manager import TurnPhase
        
        if current_phase == TurnPhase.SURVIVOR_TURN:
            self.turn_manager.process_survivor_turn(self.game_state)
        elif current_phase == TurnPhase.ZOMBIE_TURN:
            self.turn_manager.process_zombie_turn(self.game_state)
        elif current_phase == TurnPhase.ZOMBIE_SPAWN:
            self.turn_manager.process_zombie_spawn()
        elif current_phase == TurnPhase.TURN_END:
            self.turn_manager.process_turn_end()
        
        # Build combat info if zombie combat is active
        combat_info = None
        if hasattr(self.turn_manager, 'waiting_for_survivor_selection') and self.turn_manager.waiting_for_survivor_selection:
            combat_info = {
                'waiting_for_selection': True,
                'message': getattr(self.turn_manager, 'combat_message', 'Combat!'),
                'target_survivors': getattr(self.turn_manager, 'available_target_survivors', [])
            }
        
        return {
            "turn_info": self.turn_manager.get_turn_info(),
            "current_survivor": self.turn_manager.get_current_survivor(),
            "available_actions": (self.turn_manager.get_available_actions() 
                                if self.turn_manager.is_waiting_for_action() else None),
            "combat_info": combat_info
        }


class GameActionProcessor:
    """Processes game actions generated from input events."""
    
    def __init__(self, turn_manager):
        self.turn_manager = turn_manager
    
    def process_actions(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a list of game actions."""
        state_changes = {}
        
        for action in actions:
            action_type = action.get("action")
            
            if action_type == "advance_phase":
                if not self.turn_manager.is_waiting_for_action():
                    self.turn_manager.advance_phase()
                    state_changes["phase_advanced"] = True
            
            elif action_type == "toggle_pause":
                self.turn_manager.game_paused = not self.turn_manager.game_paused
                state_changes["game_paused"] = self.turn_manager.game_paused
            
            elif action_type == "survivor_action":
                if self.turn_manager.is_waiting_for_action():
                    action_index = action.get("action_index", -1)
                    if action_index >= 0:
                        success = self.turn_manager.select_action(action_index)
                        state_changes["action_selected"] = success
                        if not success:
                            state_changes["invalid_action"] = action_index
            
            elif action_type == "survivor_target_selection":
                if hasattr(self.turn_manager, 'waiting_for_survivor_selection') and self.turn_manager.waiting_for_survivor_selection:
                    target_index = action.get("target_index", -1)
                    if target_index >= 0:
                        success = self.turn_manager.select_survivor_target(target_index)
                        state_changes["target_selected"] = success
                        if not success:
                            state_changes["invalid_target"] = target_index
            
            elif action_type == "toggle_debug":
                # This would be handled by the configuration manager
                state_changes["debug_toggled"] = True
        
        return state_changes


class GameWorld:
    """Encapsulates the complete game world state."""
    
    def __init__(self):
        self.running = True
        self.map_data = None
        self.survivors = []
        self.zombies = []
        self.survivors_data = []
        self.game_state = None
        
        # UI state
        self.turn_info = {}
        self.current_survivor = None
        self.available_actions = None
        self.show_action_menu = False
    
    def update_from_changes(self, changes: Dict[str, Any]):
        """Update world state from system changes."""
        for key, value in changes.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_render_data(self) -> tuple:
        """Get data needed for rendering."""
        game_world = {
            "map_data": self.map_data,
            "survivors": self.survivors,
            "zombies": self.zombies,
            "survivors_data": self.survivors_data
        }
        
        ui_state = {
            "turn_info": self.turn_info,
            "current_survivor": self.current_survivor,
            "available_actions": self.available_actions,
            "show_action_menu": self.available_actions is not None
        }
        
        return game_world, ui_state


class GameLoop:
    """Core game loop with timing and systems coordination."""
    
    def __init__(self, config_manager: ConfigurationManager, rendering_system: RenderingSystem, 
                 input_system: InputSystem, game_world: GameWorld):
        """Initialize the game loop with all required systems."""
        self.config = config_manager
        self.rendering_system = rendering_system
        self.input_system = input_system
        self.world = game_world
        
        # Core systems
        self.timing_system = TimingSystem(config_manager)
        self.game_state_system = None  # Will be set when game is loaded
        self.action_processor = None   # Will be set when game is loaded
        
        # State
        self.running = True
    
    def set_game_components(self, turn_manager, game_state):
        """Set game-specific components after game data is loaded."""
        self.turn_manager = turn_manager  # Store reference for event handling
        self.game_state_system = GameStateSystem(turn_manager, game_state)
        self.action_processor = GameActionProcessor(turn_manager)
        
        # Update world with initial game data
        self.world.game_state = game_state
    
    def run(self):
        """Run the main game loop."""
        if not self.game_state_system or not self.action_processor:
            raise RuntimeError("Game components not set. Call set_game_components() first.")
        
        print("Starting domain-based game loop...")
        
        while self.running:
            # Calculate delta time
            dt = self.timing_system.tick()
            
            # Process input
            self.handle_input()
            
            # Update systems
            self.update_systems(dt)
            
            # Render frame
            self.render_systems()
            
            # Check if we should continue running
            if self.input_system.is_quit_requested() or not self.world.running:
                self.running = False
        
        print("Game loop ended")
    
    def handle_input(self):
        """Process input through the input system."""
        # Get raw pygame events for turn manager before they're consumed
        import pygame
        raw_events = pygame.event.get()
        
        # Pass raw events to turn manager
        if hasattr(self, 'turn_manager') and self.turn_manager:
            for pygame_event in raw_events:
                if pygame_event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.turn_manager.handle_event(pygame_event)
        
        # Put events back for input system processing
        for event in raw_events:
            pygame.event.post(event)
        
        events = self.input_system.process_input()
        
        if self.input_system.is_quit_requested():
            self.running = False
            return
        
        # Handle UI events
        ui_changes = self.input_system.handle_ui_events(events)
        if ui_changes:
            self.world.update_from_changes(ui_changes)
        
        # Handle game events
        game_actions = self.input_system.handle_game_events(events, self._get_game_state_dict())
        if game_actions:
            action_results = self.action_processor.process_actions(game_actions)
            self.world.update_from_changes(action_results)
    
    def update_systems(self, dt: int):
        """Update all game systems."""
        # Update timing
        timing_changes = self.timing_system.update(dt, self._get_world_dict())
        self.world.update_from_changes(timing_changes)
        
        # Update game state
        if self.game_state_system:
            game_changes = self.game_state_system.update(dt, self._get_world_dict())
            self.world.update_from_changes(game_changes)
    
    def render_systems(self):
        """Render the current frame using the rendering system."""
        game_world, ui_state = self.world.get_render_data()
        self.rendering_system.render(game_world, ui_state)
    
    def _get_world_dict(self) -> Dict[str, Any]:
        """Get world state as dictionary."""
        return {
            "running": self.running,
            "map_data": self.world.map_data,
            "survivors": self.world.survivors,
            "zombies": self.world.zombies,
            "game_state": self.world.game_state
        }
    
    def _get_game_state_dict(self) -> Dict[str, Any]:
        """Get current game state for event processing."""
        return {
            "turn_info": self.world.turn_info,
            "current_survivor": self.world.current_survivor,
            "waiting_for_action": self.world.available_actions is not None
        }
    
    def stop(self):
        """Stop the game loop."""
        self.running = False