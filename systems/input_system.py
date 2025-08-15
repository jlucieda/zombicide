"""
InputSystem for the Zombicide game.
Handles input processing and event generation in a domain-focused manner.
"""
import pygame
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .configuration_manager import ConfigurationManager


class InputEventType(Enum):
    """Types of input events that can be generated."""
    QUIT = "quit"
    PHASE_ADVANCE = "phase_advance"
    PAUSE_TOGGLE = "pause_toggle"
    SURVIVOR_ACTION = "survivor_action"
    DEBUG_TOGGLE = "debug_toggle"
    MOVE = "move"
    ATTACK = "attack"
    SKIP_TURN = "skip_turn"
    UNKNOWN = "unknown"


@dataclass
class InputEvent:
    """Represents an input event generated from user input."""
    event_type: InputEventType
    data: Optional[Dict[str, Any]] = None
    timestamp: int = 0


class InputProcessor:
    """Core input processing logic."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config = config_manager
        self._quit_requested = False
    
    def process_pygame_events(self) -> List[InputEvent]:
        """Process pygame events and convert to game input events."""
        events = []
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            input_event = self._convert_pygame_event(event, current_time)
            if input_event:
                events.append(input_event)
        
        return events
    
    def _convert_pygame_event(self, event: pygame.event.Event, timestamp: int) -> Optional[InputEvent]:
        """Convert a pygame event to an input event."""
        if event.type == pygame.QUIT:
            self._quit_requested = True
            return InputEvent(InputEventType.QUIT, timestamp=timestamp)
        
        elif event.type == pygame.KEYDOWN:
            return self._handle_keydown(event, timestamp)
        
        # TODO: Add mouse event handling here
        
        return None
    
    def _handle_keydown(self, event: pygame.event.Event, timestamp: int) -> Optional[InputEvent]:
        """Handle keyboard input events."""
        key = event.key
        key_bindings = self.config.input.key_bindings
        
        if key == key_bindings['quit']:
            self._quit_requested = True
            return InputEvent(InputEventType.QUIT, timestamp=timestamp)
        
        elif key == key_bindings['phase_advance']:
            return InputEvent(InputEventType.PHASE_ADVANCE, timestamp=timestamp)
        
        elif key == key_bindings['pause_toggle']:
            return InputEvent(InputEventType.PAUSE_TOGGLE, timestamp=timestamp)
        
        elif key == key_bindings['action_1']:
            return InputEvent(InputEventType.SURVIVOR_ACTION, 
                            {"action_index": 0}, timestamp)
        
        elif key == key_bindings['action_2']:
            return InputEvent(InputEventType.SURVIVOR_ACTION, 
                            {"action_index": 1}, timestamp)
        
        elif key == key_bindings['action_3']:
            return InputEvent(InputEventType.SURVIVOR_ACTION, 
                            {"action_index": 2}, timestamp)
        
        elif key == pygame.K_F1:  # Debug toggle
            return InputEvent(InputEventType.DEBUG_TOGGLE, timestamp=timestamp)
        
        # Movement with cursor keys
        elif key == pygame.K_UP:
            return InputEvent(InputEventType.MOVE, {"direction": "UP"}, timestamp)
        
        elif key == pygame.K_DOWN:
            return InputEvent(InputEventType.MOVE, {"direction": "DOWN"}, timestamp)
        
        elif key == pygame.K_LEFT:
            return InputEvent(InputEventType.MOVE, {"direction": "LEFT"}, timestamp)
        
        elif key == pygame.K_RIGHT:
            return InputEvent(InputEventType.MOVE, {"direction": "RIGHT"}, timestamp)
        
        # Attack with 'a' key
        elif key == pygame.K_a:
            return InputEvent(InputEventType.ATTACK, timestamp=timestamp)
        
        # Space key - context sensitive (phase advance OR skip turn)
        elif key == key_bindings['phase_advance']:  # This is space key
            return InputEvent(InputEventType.PHASE_ADVANCE, timestamp=timestamp)
        
        return InputEvent(InputEventType.UNKNOWN, {"key": key}, timestamp)
    
    def is_quit_requested(self) -> bool:
        """Check if quit was requested."""
        return self._quit_requested
    
    def reset_quit_flag(self):
        """Reset quit flag."""
        self._quit_requested = False


class GameEventHandler:
    """Handles game-specific event processing."""
    
    def __init__(self):
        self.event_handlers = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default event handlers."""
        self.event_handlers[InputEventType.PHASE_ADVANCE] = self._handle_phase_advance
        self.event_handlers[InputEventType.PAUSE_TOGGLE] = self._handle_pause_toggle
        self.event_handlers[InputEventType.SURVIVOR_ACTION] = self._handle_survivor_action
        self.event_handlers[InputEventType.DEBUG_TOGGLE] = self._handle_debug_toggle
        self.event_handlers[InputEventType.MOVE] = self._handle_move
        self.event_handlers[InputEventType.ATTACK] = self._handle_attack
        self.event_handlers[InputEventType.SKIP_TURN] = self._handle_skip_turn
    
    def handle_event(self, event: InputEvent, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an input event and return resulting game state changes."""
        handler = self.event_handlers.get(event.event_type)
        if handler:
            return handler(event, game_state)
        return {}
    
    def _handle_phase_advance(self, event: InputEvent, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle phase advance request or skip turn during survivor turn."""
        # During survivor turn, space should skip turn instead of advance phase
        if game_state.get("waiting_for_action", False):
            return {"action": "skip_turn"}
        else:
            # This could be phase advance or waiting for phase advance
            return {"action": "advance_phase"}
    
    def _handle_pause_toggle(self, event: InputEvent, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pause toggle."""
        return {"action": "toggle_pause"}
    
    def _handle_survivor_action(self, event: InputEvent, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle survivor action selection."""
        action_index = event.data.get("action_index", -1) if event.data else -1
        return {
            "action": "survivor_action",
            "action_index": action_index
        }
    
    def _handle_debug_toggle(self, event: InputEvent, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle debug mode toggle."""
        return {"action": "toggle_debug"}
    
    def _handle_move(self, event: InputEvent, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle movement input."""
        direction = event.data.get("direction") if event.data else None
        return {
            "action": "move",
            "direction": direction
        }
    
    def _handle_attack(self, event: InputEvent, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle attack input."""
        return {
            "action": "attack"
        }
    
    def _handle_skip_turn(self, event: InputEvent, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle skip turn input."""
        return {
            "action": "skip_turn"
        }


class UIEventHandler:
    """Handles UI-specific event processing."""
    
    def handle_ui_events(self, events: List[InputEvent]) -> Dict[str, Any]:
        """Process UI-related events."""
        ui_changes = {}
        
        for event in events:
            if event.event_type == InputEventType.DEBUG_TOGGLE:
                ui_changes["toggle_debug_overlay"] = True
        
        return ui_changes


class InputSystem:
    """Main input system that coordinates input processing and event generation."""
    
    def __init__(self, config_manager: ConfigurationManager):
        """Initialize the input system."""
        self.config = config_manager
        self.processor = InputProcessor(config_manager)
        self.game_event_handler = GameEventHandler()
        self.ui_event_handler = UIEventHandler()
        
        self.events_this_frame: List[InputEvent] = []
    
    def process_input(self) -> List[InputEvent]:
        """Process all input and return events generated this frame."""
        self.events_this_frame = self.processor.process_pygame_events()
        return self.events_this_frame.copy()
    
    def handle_ui_events(self, events: List[InputEvent]) -> Dict[str, Any]:
        """Handle UI-specific events."""
        return self.ui_event_handler.handle_ui_events(events)
    
    def handle_game_events(self, events: List[InputEvent], game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle game-specific events."""
        game_actions = []
        
        for event in events:
            action = self.game_event_handler.handle_event(event, game_state)
            if action:
                game_actions.append(action)
        
        return game_actions
    
    def is_quit_requested(self) -> bool:
        """Check if application quit was requested."""
        return self.processor.is_quit_requested()
    
    def reset_quit_flag(self):
        """Reset the quit flag."""
        self.processor.reset_quit_flag()
    
    def get_last_events(self) -> List[InputEvent]:
        """Get events from the last frame (for debugging)."""
        return self.events_this_frame.copy()
    
    def register_game_event_handler(self, event_type: InputEventType, handler_func):
        """Register a custom game event handler."""
        self.game_event_handler.event_handlers[event_type] = handler_func
    
    def update_key_binding(self, action: str, new_key: int):
        """Update a key binding."""
        if action in self.config.input.key_bindings:
            self.config.input.key_bindings[action] = new_key