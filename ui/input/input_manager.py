"""
InputManager handles all input processing and event management for the Zombicide game.
This class is responsible for capturing pygame events and converting them into game actions.
"""
import pygame
from typing import List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class GameEventType(Enum):
    """Types of game events that can be generated from input."""
    QUIT = "quit"
    PHASE_ADVANCE = "phase_advance"
    PAUSE_TOGGLE = "pause_toggle"
    SURVIVOR_ACTION = "survivor_action"
    UNKNOWN = "unknown"


@dataclass
class GameEvent:
    """Represents a game event generated from user input."""
    event_type: GameEventType
    data: Optional[dict] = None


class InputManager:
    """Handles event processing and input management."""
    
    def __init__(self):
        """Initialize the input manager."""
        self.quit_requested = False
        self.events_this_frame: List[GameEvent] = []
        
    def process_events(self) -> List[GameEvent]:
        """Process all pygame events and return corresponding game events."""
        self.events_this_frame.clear()
        
        for event in pygame.event.get():
            game_event = self._convert_pygame_event(event)
            if game_event:
                self.events_this_frame.append(game_event)
                
        return self.events_this_frame.copy()
    
    def _convert_pygame_event(self, event: pygame.event.Event) -> Optional[GameEvent]:
        """Convert a pygame event to a game event."""
        if event.type == pygame.QUIT:
            self.quit_requested = True
            return GameEvent(GameEventType.QUIT)
            
        elif event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)
            
        return None
    
    def _handle_keydown(self, event: pygame.event.Event) -> Optional[GameEvent]:
        """Handle keyboard input events."""
        key = event.key
        
        # System controls
        if key == pygame.K_ESCAPE:
            self.quit_requested = True
            return GameEvent(GameEventType.QUIT)
            
        elif key == pygame.K_SPACE:
            return GameEvent(GameEventType.PHASE_ADVANCE)
            
        elif key == pygame.K_p:
            return GameEvent(GameEventType.PAUSE_TOGGLE)
            
        # Survivor action selection
        elif key == pygame.K_1:
            return GameEvent(GameEventType.SURVIVOR_ACTION, {"action_index": 0})
            
        elif key == pygame.K_2:
            return GameEvent(GameEventType.SURVIVOR_ACTION, {"action_index": 1})
            
        elif key == pygame.K_3:
            return GameEvent(GameEventType.SURVIVOR_ACTION, {"action_index": 2})
            
        return GameEvent(GameEventType.UNKNOWN, {"key": key})
    
    def is_quit_requested(self) -> bool:
        """Check if the user has requested to quit the application."""
        return self.quit_requested
    
    def reset_quit_flag(self):
        """Reset the quit flag (useful for testing or dialog handling)."""
        self.quit_requested = False
    
    def get_last_events(self) -> List[GameEvent]:
        """Get the events from the last frame (for debugging)."""
        return self.events_this_frame.copy()