from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from .actions import Action, ActionType, ActionResult, Direction, Position, ActionValidator
import random

class Entity(ABC):
    """Base class for all game entities (survivors, zombies)."""
    
    def __init__(self, entity_id: str, name: str, position: Position):
        self.id = entity_id
        self.name = name
        self.position = position
        self.alive = True
        self.actions_remaining = 0
        self.max_actions = 1  # Default to 1 action per turn
    
    @abstractmethod
    def decide_action(self, game_state: 'GameState') -> Optional[Action]:
        """Decide what action this entity should take."""
        pass
    
    def can_act(self) -> bool:
        """Check if this entity can still take actions this turn."""
        return self.alive and self.actions_remaining > 0
    
    def start_turn(self):
        """Initialize the entity for a new turn."""
        self.actions_remaining = self.max_actions
    
    def consume_action(self):
        """Consume one action point."""
        if self.actions_remaining > 0:
            self.actions_remaining -= 1

class Survivor(Entity):
    """Survivor entity with 3 actions per turn."""
    
    def __init__(self, entity_id: str, name: str, position: Position, survivor_data: dict):
        super().__init__(entity_id, name, position)
        self.max_actions = 3  # Survivors get 3 actions per turn
        self.survivor_data = survivor_data
        self.wounds = survivor_data.get('wounds', 0)
        self.exp = survivor_data.get('exp', 0)
        self.level = survivor_data.get('level', 'blue')
        self.equipment = survivor_data.get('equipment', {})
        
    def decide_action(self, game_state: 'GameState') -> Optional[Action]:
        """AI decision making for survivor (for demo purposes)."""
        if not self.can_act():
            return None
        
        # Find zombies in the same zone
        zombies_in_zone = [z for z in game_state.zombies if z.position == self.position and z.alive]
        
        # If there are zombies in the same zone, attack one
        if zombies_in_zone:
            target_zombie = zombies_in_zone[0]
            return Action(
                action_type=ActionType.ATTACK,
                actor_id=self.id,
                target_position=target_zombie.position,
                target_id=target_zombie.id
            )
        
        # Otherwise, try to move towards zombies or randomly
        possible_moves = []
        for direction in Direction:
            if ActionValidator.validate_move(self.position, direction):
                possible_moves.append(direction)
        
        if possible_moves:
            chosen_direction = random.choice(possible_moves)
            new_position = self.position + chosen_direction
            return Action(
                action_type=ActionType.MOVE,
                actor_id=self.id,
                target_position=new_position,
                direction=chosen_direction
            )
        
        return None
    
    def take_damage(self):
        """Survivor takes damage (gains wounds)."""
        self.wounds += 1
        if self.wounds >= 2:  # Survivors die at 2 wounds
            self.alive = False
            return True  # Died
        return False  # Survived

class Zombie(Entity):
    """Zombie entity with 1 action per turn."""
    
    def __init__(self, entity_id: str, position: Position):
        super().__init__(entity_id, f"Zombie_{entity_id}", position)
        self.max_actions = 1  # Zombies get 1 action per turn
        
    def decide_action(self, game_state: 'GameState') -> Optional[Action]:
        """AI decision making for zombie."""
        if not self.can_act():
            return None
        
        # Find survivors in the same zone
        survivors_in_zone = [s for s in game_state.survivors if s.position == self.position and s.alive]
        
        # If there are survivors in the same zone, attack one
        if survivors_in_zone:
            target_survivor = survivors_in_zone[0]
            return Action(
                action_type=ActionType.ATTACK,
                actor_id=self.id,
                target_position=target_survivor.position,
                target_id=target_survivor.id
            )
        
        # Otherwise, move towards the closest survivor
        closest_survivor = None
        min_distance = float('inf')
        
        for survivor in game_state.survivors:
            if survivor.alive:
                distance = self.position.distance_to(survivor.position)
                if distance < min_distance:
                    min_distance = distance
                    closest_survivor = survivor
        
        if closest_survivor:
            # Move towards the closest survivor
            best_direction = None
            best_distance = min_distance
            
            for direction in Direction:
                if ActionValidator.validate_move(self.position, direction):
                    new_position = self.position + direction
                    distance = new_position.distance_to(closest_survivor.position)
                    if distance < best_distance:
                        best_distance = distance
                        best_direction = direction
            
            if best_direction:
                new_position = self.position + best_direction
                return Action(
                    action_type=ActionType.MOVE,
                    actor_id=self.id,
                    target_position=new_position,
                    direction=best_direction
                )
        
        return None

class GameState:
    """Manages the current state of all entities in the game."""
    
    def __init__(self):
        self.survivors: List[Survivor] = []
        self.zombies: List[Zombie] = []
        self.grid_size = 3
        
    def add_survivor(self, survivor: Survivor):
        """Add a survivor to the game state."""
        self.survivors.append(survivor)
    
    def add_zombie(self, zombie: Zombie):
        """Add a zombie to the game state."""
        self.zombies.append(zombie)
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Find an entity by ID."""
        for survivor in self.survivors:
            if survivor.id == entity_id:
                return survivor
        for zombie in self.zombies:
            if zombie.id == entity_id:
                return zombie
        return None
    
    def get_entities_at_position(self, position: Position) -> List[Entity]:
        """Get all entities at a specific position."""
        entities = []
        for survivor in self.survivors:
            if survivor.position == position and survivor.alive:
                entities.append(survivor)
        for zombie in self.zombies:
            if zombie.position == position and zombie.alive:
                entities.append(zombie)
        return entities
    
    def execute_action(self, action: Action) -> ActionResult:
        """Execute an action and return the result."""
        actor = self.get_entity_by_id(action.actor_id)
        if not actor or not actor.can_act():
            return ActionResult(False, f"Actor {action.actor_id} cannot act")
        
        if action.action_type == ActionType.MOVE:
            return self._execute_move(actor, action)
        elif action.action_type == ActionType.ATTACK:
            return self._execute_attack(actor, action)
        
        return ActionResult(False, "Unknown action type")
    
    def _execute_move(self, actor: Entity, action: Action) -> ActionResult:
        """Execute a move action."""
        if not ActionValidator.validate_move(actor.position, action.direction, self.grid_size):
            return ActionResult(False, f"Invalid move for {actor.name}")
        
        old_position = actor.position
        actor.position = action.target_position
        actor.consume_action()
        
        return ActionResult(
            True, 
            f"{actor.name} moved from ({old_position.row},{old_position.col}) to ({actor.position.row},{actor.position.col})",
            [f"position_changed:{actor.id}:{actor.position.row},{actor.position.col}"]
        )
    
    def _execute_attack(self, actor: Entity, action: Action) -> ActionResult:
        """Execute an attack action."""
        target = self.get_entity_by_id(action.target_id)
        if not target:
            return ActionResult(False, f"Target {action.target_id} not found")
        
        if not ActionValidator.validate_attack(actor.position, target.position):
            return ActionResult(False, f"{actor.name} cannot attack {target.name} - not in same zone")
        
        # Execute the attack
        actor.consume_action()
        effects = []
        
        if isinstance(target, Survivor):
            died = target.take_damage()
            message = f"{actor.name} attacks {target.name} - {target.name} takes 1 wound"
            if died:
                message += f" and dies!"
                effects.append(f"entity_died:{target.id}")
            effects.append(f"damage_taken:{target.id}:1")
            
        elif isinstance(target, Zombie):
            target.alive = False
            message = f"{actor.name} attacks {target.name} - {target.name} is eliminated!"
            effects.append(f"entity_died:{target.id}")
        
        return ActionResult(True, message, effects)
    
    def start_entity_turns(self, entity_type: type):
        """Initialize all entities of a given type for their turn."""
        entities = self.survivors if entity_type == Survivor else self.zombies
        for entity in entities:
            if entity.alive:
                entity.start_turn()