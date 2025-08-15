"""
Turn Order Management for Zombicide.
Handles the rotating first player system as per Zombicide rules.
"""
from typing import List, Optional
from .entities import Survivor


class TurnOrderManager:
    """
    Manages the turn order for survivors in Zombicide.
    
    In Zombicide, survivors take turns in a rotating order where the player who went 
    first in the previous turn goes last in the next turn. This manager handles that logic.
    """
    
    def __init__(self, survivors: List[Survivor]):
        """
        Initialize the turn order manager.
        
        Args:
            survivors: List of all survivors in the game
        """
        self.survivors = survivors.copy()  # Create a copy to avoid external modifications
        self.first_player_index = 0  # Index of the current first player
        self.current_turn_order: List[Survivor] = []
        self.current_survivor_index = 0
        self.turn_number = 1
        
        # Initialize the first turn order
        self._update_turn_order()
    
    def _update_turn_order(self):
        """Update the current turn order based on the first player index."""
        if not self.survivors:
            self.current_turn_order = []
            return
        
        # Create turn order starting from first player
        self.current_turn_order = (
            self.survivors[self.first_player_index:] + 
            self.survivors[:self.first_player_index]
        )
        
        # Filter out dead survivors
        self.current_turn_order = [s for s in self.current_turn_order if s.alive]
        
        # Reset current survivor index
        self.current_survivor_index = 0
    
    def get_current_turn_order(self) -> List[Survivor]:
        """
        Get the current turn order for this turn.
        
        Returns:
            List of survivors in turn order for current turn
        """
        return self.current_turn_order.copy()
    
    def get_current_survivor(self) -> Optional[Survivor]:
        """
        Get the survivor whose turn it currently is.
        
        Returns:
            Current survivor or None if no survivors left
        """
        if not self.current_turn_order or self.current_survivor_index >= len(self.current_turn_order):
            return None
        return self.current_turn_order[self.current_survivor_index]
    
    def get_next_survivor(self) -> Optional[Survivor]:
        """
        Advance to the next survivor in the turn order.
        
        Returns:
            Next survivor or None if all survivors have finished their turns
        """
        self.current_survivor_index += 1
        return self.get_current_survivor()
    
    def has_more_survivors(self) -> bool:
        """
        Check if there are more survivors to take their turns this round.
        
        Returns:
            True if more survivors need to take their turns
        """
        return (self.current_turn_order and 
                self.current_survivor_index < len(self.current_turn_order))
    
    def advance_turn(self):
        """
        Advance to the next turn, rotating the first player.
        
        This should be called when all survivors have completed their turns.
        The survivor who went first this turn will go last next turn.
        """
        # Rotate first player (previous first player goes to the back)
        self.first_player_index = (self.first_player_index + 1) % len(self.survivors)
        
        # Increment turn number
        self.turn_number += 1
        
        # Update turn order for new turn
        self._update_turn_order()
        
        print(f"=== Turn {self.turn_number} ===")
        if self.current_turn_order:
            first_player = self.current_turn_order[0]
            print(f"First player this turn: {first_player.name}")
            print(f"Turn order: {' → '.join(s.name for s in self.current_turn_order)}")
    
    def get_first_player(self) -> Optional[Survivor]:
        """
        Get the first player for the current turn.
        
        Returns:
            First player survivor or None if no survivors
        """
        if self.current_turn_order:
            return self.current_turn_order[0]
        return None
    
    def get_turn_info(self) -> dict:
        """
        Get comprehensive turn order information.
        
        Returns:
            Dictionary with turn order details
        """
        current_survivor = self.get_current_survivor()
        
        return {
            'turn_number': self.turn_number,
            'first_player': self.get_first_player().name if self.get_first_player() else None,
            'current_survivor': current_survivor.name if current_survivor else None,
            'current_survivor_index': self.current_survivor_index,
            'turn_order': [s.name for s in self.current_turn_order],
            'survivors_remaining': len(self.current_turn_order) - self.current_survivor_index,
            'has_more_survivors': self.has_more_survivors()
        }
    
    def reset_for_new_game(self, survivors: List[Survivor]):
        """
        Reset the turn order manager for a new game.
        
        Args:
            survivors: New list of survivors
        """
        self.survivors = survivors.copy()
        self.first_player_index = 0
        self.current_survivor_index = 0
        self.turn_number = 1
        self._update_turn_order()
    
    def remove_dead_survivor(self, survivor: Survivor):
        """
        Remove a dead survivor from the game.
        
        Args:
            survivor: The survivor who died
        """
        # Remove from main survivors list
        if survivor in self.survivors:
            dead_index = self.survivors.index(survivor)
            self.survivors.remove(survivor)
            
            # Adjust first player index if necessary
            if dead_index < self.first_player_index:
                self.first_player_index -= 1
            elif dead_index == self.first_player_index and self.first_player_index >= len(self.survivors):
                self.first_player_index = 0
        
        # Update current turn order
        self._update_turn_order()
        
        # Adjust current survivor index if necessary
        if self.current_survivor_index >= len(self.current_turn_order):
            self.current_survivor_index = len(self.current_turn_order)
    
    def get_position_in_turn(self, survivor: Survivor) -> Optional[int]:
        """
        Get the position of a survivor in the current turn order.
        
        Args:
            survivor: The survivor to check
            
        Returns:
            Position in turn order (0-based) or None if not found
        """
        try:
            return self.current_turn_order.index(survivor)
        except ValueError:
            return None
    
    def is_last_survivor_in_turn(self) -> bool:
        """
        Check if the current survivor is the last one in this turn.
        
        Returns:
            True if this is the last survivor's turn
        """
        return (self.current_survivor_index == len(self.current_turn_order) - 1)