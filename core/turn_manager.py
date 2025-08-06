import pygame
from enum import Enum

class TurnPhase(Enum):
    SURVIVOR_TURN = 1
    ZOMBIE_TURN = 2
    ZOMBIE_SPAWN = 3
    TURN_END = 4

class TurnManager:
    def __init__(self):
        """Initialize the turn management system."""
        self.current_phase = TurnPhase.SURVIVOR_TURN
        self.turn_number = 1
        self.current_survivor_index = 0
        self.survivors_acted = []
        self.phase_complete = False
        self.game_paused = False
        
        # Phase timers (for automatic progression if needed)
        self.phase_timer = 0
        self.auto_advance_delay = 2000  # milliseconds
        
        # Event callbacks
        self.on_phase_change = None
        self.on_turn_change = None
        
        # Survivor turn management
        self.current_survivor = None
        self.waiting_for_action = False
        self.available_actions = []
        
    def get_current_phase(self):
        """Get the current turn phase."""
        return self.current_phase
    
    def get_turn_number(self):
        """Get the current turn number."""
        return self.turn_number
    
    def get_phase_name(self):
        """Get the human-readable name of the current phase."""
        phase_names = {
            TurnPhase.SURVIVOR_TURN: "Survivor Turn",
            TurnPhase.ZOMBIE_TURN: "Zombie Turn", 
            TurnPhase.ZOMBIE_SPAWN: "Zombie Spawn",
            TurnPhase.TURN_END: "Turn End"
        }
        return phase_names[self.current_phase]
    
    def advance_phase(self):
        """Advance to the next phase of the turn."""
        if self.game_paused:
            return
            
        # Reset phase completion flag
        self.phase_complete = False
        self.phase_timer = 0
        
        # Advance to next phase
        if self.current_phase == TurnPhase.SURVIVOR_TURN:
            self.current_phase = TurnPhase.ZOMBIE_TURN
            print(f"Turn {self.turn_number}: Advancing to Zombie Turn")
            
        elif self.current_phase == TurnPhase.ZOMBIE_TURN:
            self.current_phase = TurnPhase.ZOMBIE_SPAWN
            print(f"Turn {self.turn_number}: Advancing to Zombie Spawn")
            
        elif self.current_phase == TurnPhase.ZOMBIE_SPAWN:
            self.current_phase = TurnPhase.TURN_END
            print(f"Turn {self.turn_number}: Advancing to Turn End")
            
        elif self.current_phase == TurnPhase.TURN_END:
            self.end_turn()
            
        # Trigger phase change callback
        if self.on_phase_change:
            self.on_phase_change(self.current_phase)
    
    def end_turn(self):
        """Complete the current turn and start a new one."""
        self.turn_number += 1
        self.current_phase = TurnPhase.SURVIVOR_TURN
        self.current_survivor_index = 0
        self.survivors_acted.clear()
        self.phase_complete = False
        self.phase_timer = 0
        
        print(f"=== Starting Turn {self.turn_number} ===")
        
        # Trigger turn change callback
        if self.on_turn_change:
            self.on_turn_change(self.turn_number)
    
    def update(self, dt):
        """Update the turn manager (called each frame)."""
        if self.game_paused:
            return
            
        # Update phase timer
        self.phase_timer += dt
        
        # Handle automatic phase progression for certain phases
        if self.phase_complete and self.phase_timer >= self.auto_advance_delay:
            self.advance_phase()
    
    def handle_event(self, event):
        """Handle input events for turn management."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Space bar advances to next phase (only if not waiting for survivor action)
                if not self.waiting_for_action:
                    print(f"Manual phase advance: {self.get_phase_name()}")
                    self.advance_phase()
                    return True
            elif event.key == pygame.K_p:
                # P pauses/unpauses the game
                self.game_paused = not self.game_paused
                print(f"Game {'paused' if self.game_paused else 'unpaused'}")
                return True
            elif self.waiting_for_action and self.current_phase == TurnPhase.SURVIVOR_TURN:
                # Handle survivor action selection
                if event.key == pygame.K_1:
                    return self.select_action(0)  # Move
                elif event.key == pygame.K_2:
                    return self.select_action(1)  # Attack
                elif event.key == pygame.K_3:
                    return self.select_action(2)  # Skip turn
        return False
    
    def select_action(self, action_index):
        """Select and execute a survivor action."""
        if action_index >= len(self.available_actions):
            return False
            
        selected_action_text = self.available_actions[action_index]
        print(f"Selected action: {selected_action_text}")
        
        # Execute the selected action
        success = self._execute_selected_action(selected_action_text)
        
        if success:
            self.waiting_for_action = False
            # Move to next survivor or complete phase if this survivor is done
            if not self.current_survivor.can_act():
                self.current_survivor_index += 1
        
        return success
    
    def get_current_survivor(self):
        """Get the currently active survivor."""
        return self.current_survivor
    
    def is_waiting_for_action(self):
        """Check if the game is waiting for a survivor action."""
        return self.waiting_for_action
    
    def get_available_actions(self):
        """Get the list of available actions for the current survivor."""
        return self.available_actions
    
    # Phase-specific methods
    def process_survivor_turn(self, game_state):
        """Process the survivor turn phase with manual control."""
        if not hasattr(game_state, 'survivors') or len(game_state.survivors) == 0:
            self.mark_phase_complete()
            return
        
        # Store game state reference for action execution
        self._current_game_state = game_state
        
        # Initialize survivor turns if not done yet
        if not hasattr(self, '_survivor_turn_initialized'):
            game_state.start_entity_turns(type(game_state.survivors[0]))
            self._survivor_turn_initialized = True
            self.current_survivor_index = 0
            print("=== Survivor Turn Started (Manual Control) ===")
            for survivor in game_state.survivors:
                if survivor.alive:
                    print(f"  {survivor.name}: {survivor.actions_remaining} actions remaining")
        
        # If not waiting for action, find next survivor who can act
        if not self.waiting_for_action:
            # Find next active survivor
            active_survivor = None
            while self.current_survivor_index < len(game_state.survivors):
                survivor = game_state.survivors[self.current_survivor_index]
                if survivor.alive and survivor.can_act():
                    active_survivor = survivor
                    break
                else:
                    self.current_survivor_index += 1
            
            if active_survivor:
                self.current_survivor = active_survivor
                # Generate available actions
                self.available_actions = self._get_available_actions(active_survivor, game_state)
                self.waiting_for_action = True
                print(f"\n=== {active_survivor.name}'s Turn ===")
                print(f"Actions remaining: {active_survivor.actions_remaining}")
                print("Available actions:")
                for i, action in enumerate(self.available_actions):
                    print(f"  {i+1}. {action}")
            else:
                # All survivors have completed their actions
                if not self.phase_complete:
                    print("All survivors have completed their actions")
                self._survivor_turn_initialized = False
                self.mark_phase_complete()
    
    def _get_available_actions(self, survivor, game_state):
        """Get available actions for a survivor."""
        from .actions import Direction, ActionValidator
        
        actions = []
        
        # Add move actions
        for direction in Direction:
            if ActionValidator.validate_move(survivor.position, direction):
                actions.append(f"Move {direction.name}")
        
        # Add attack actions
        targets_in_zone = []
        for zombie in game_state.zombies:
            if zombie.alive and zombie.position == survivor.position:
                targets_in_zone.append(zombie)
        
        if targets_in_zone:
            actions.append("Attack zombie")
        
        # Always allow skipping turn
        actions.append("Skip remaining actions")
        
        return actions
    
    def _execute_selected_action(self, action_text):
        """Execute the selected action based on the action text."""
        from .actions import Action, ActionType, Direction, Position
        
        if not self.current_survivor:
            return False
            
        # Parse action text and create appropriate action
        if action_text.startswith("Move "):
            direction_name = action_text.replace("Move ", "")
            try:
                direction = Direction[direction_name]
                new_position = self.current_survivor.position + direction
                action = Action(
                    action_type=ActionType.MOVE,
                    actor_id=self.current_survivor.id,
                    target_position=new_position,
                    direction=direction
                )
                # Execute through game state (this will be set during process_survivor_turn)
                result = self._current_game_state.execute_action(action)
                print(f"  {result.message}")
                return result.success
            except (KeyError, ValueError):
                print(f"  Invalid direction: {direction_name}")
                return False
                
        elif action_text == "Attack zombie":
            # Find a zombie in the same zone
            for zombie in self._current_game_state.zombies:
                if zombie.alive and zombie.position == self.current_survivor.position:
                    action = Action(
                        action_type=ActionType.ATTACK,
                        actor_id=self.current_survivor.id,
                        target_position=zombie.position,
                        target_id=zombie.id
                    )
                    result = self._current_game_state.execute_action(action)
                    print(f"  {result.message}")
                    return result.success
            print("  No zombie found to attack")
            return False
            
        elif action_text == "Skip remaining actions":
            # Skip all remaining actions for this survivor
            self.current_survivor.actions_remaining = 0
            print(f"  {self.current_survivor.name} skips remaining actions")
            return True
        
        return False
    
    def process_zombie_turn(self, game_state):
        """Process the zombie turn phase."""
        if not hasattr(game_state, 'zombies') or len(game_state.zombies) == 0:
            self.mark_phase_complete()
            return
        
        # Initialize zombie turns if not done yet
        if not hasattr(self, '_zombie_turn_initialized'):
            game_state.start_entity_turns(type(game_state.zombies[0]))
            self._zombie_turn_initialized = True
            print("=== Zombie Turn Started ===")
            
        # Process zombie actions
        all_done = True
        for zombie in game_state.zombies:
            if zombie.alive and zombie.can_act():
                all_done = False
                
                # Let zombie decide and execute their action
                action = zombie.decide_action(game_state)
                if action:
                    result = game_state.execute_action(action)
                    print(f"    {result.message}")
                    if not result.success:
                        # If action failed, consume the action anyway
                        zombie.consume_action()
                else:
                    # No valid action available, skip this zombie's remaining actions
                    zombie.actions_remaining = 0
        
        if all_done:
            if not self.phase_complete:  # Only print once
                print("All zombies have completed their actions")
            self._zombie_turn_initialized = False
            self.mark_phase_complete()
    
    def process_zombie_spawn(self):
        """Process the zombie spawn phase."""
        if not self.phase_complete:
            # Calculate spawn points based on turn number and game state
            spawn_count = min(self.turn_number, 4)  # Max 4 zombies per turn
            print(f"  Spawning {spawn_count} new zombies")
            
            # In a full game, this would actually spawn zombies on the map
            self.mark_phase_complete()
    
    def process_turn_end(self):
        """Process the turn end phase."""
        if not self.phase_complete:
            print("  Turn cleanup and end-of-turn effects")
            # Handle any end-of-turn cleanup or effects
            self.mark_phase_complete()
    
    def mark_phase_complete(self):
        """Mark the current phase as complete."""
        self.phase_complete = True
        self.phase_timer = 0
    
    def get_turn_info(self):
        """Get comprehensive turn information for display."""
        return {
            'turn_number': self.turn_number,
            'phase': self.current_phase,
            'phase_name': self.get_phase_name(),
            'phase_complete': self.phase_complete,
            'survivors_acted': len(self.survivors_acted),
            'paused': self.game_paused
        }
    
    def reset(self):
        """Reset the turn manager to initial state."""
        self.current_phase = TurnPhase.SURVIVOR_TURN
        self.turn_number = 1
        self.current_survivor_index = 0
        self.survivors_acted.clear()
        self.phase_complete = False
        self.game_paused = False
        self.phase_timer = 0
        print("Turn manager reset to initial state")