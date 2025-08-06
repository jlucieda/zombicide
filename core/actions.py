from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, List

class ActionType(Enum):
    MOVE = "move"
    ATTACK = "attack"
    
class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0) 
    LEFT = (0, -1)
    RIGHT = (0, 1)
    
    def get_offset(self):
        return self.value

@dataclass
class Position:
    row: int
    col: int
    
    def __add__(self, direction: Direction):
        dr, dc = direction.get_offset()
        return Position(self.row + dr, self.col + dc)
    
    def __eq__(self, other):
        return isinstance(other, Position) and self.row == other.row and self.col == other.col
    
    def is_valid(self, grid_size: int = 3):
        """Check if position is within the grid bounds."""
        return 0 <= self.row < grid_size and 0 <= self.col < grid_size
    
    def distance_to(self, other: 'Position') -> int:
        """Calculate Manhattan distance to another position."""
        return abs(self.row - other.row) + abs(self.col - other.col)
    
    def is_adjacent(self, other: 'Position') -> bool:
        """Check if this position is adjacent to another position."""
        return self.distance_to(other) == 1

@dataclass
class Action:
    action_type: ActionType
    actor_id: str
    target_position: Optional[Position] = None
    target_id: Optional[str] = None
    direction: Optional[Direction] = None
    
    def __str__(self):
        if self.action_type == ActionType.MOVE:
            return f"{self.actor_id} moves {self.direction.name} to {self.target_position}"
        elif self.action_type == ActionType.ATTACK:
            return f"{self.actor_id} attacks {self.target_id} at {self.target_position}"
        return f"{self.actor_id} performs {self.action_type.value}"

class ActionValidator:
    """Validates whether actions are legal in the current game state."""
    
    @staticmethod
    def validate_move(actor_pos: Position, direction: Direction, grid_size: int = 3) -> bool:
        """Validate if a move action is legal."""
        new_position = actor_pos + direction
        return new_position.is_valid(grid_size)
    
    @staticmethod
    def validate_attack(actor_pos: Position, target_pos: Position) -> bool:
        """Validate if an attack action is legal (target must be in same zone)."""
        return actor_pos == target_pos

class ActionResult:
    """Result of executing an action."""
    def __init__(self, success: bool, message: str = "", effects: List[str] = None):
        self.success = success
        self.message = message
        self.effects = effects or []
    
    def __str__(self):
        return f"{'Success' if self.success else 'Failed'}: {self.message}"