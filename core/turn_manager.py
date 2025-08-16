
import pygame
from enum import Enum
from .turn_order import TurnOrderManager

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
        
        # Combat system
        self.waiting_for_survivor_selection = False
        self.attacking_zombie = None
        self.available_target_survivors = []
        self.combat_message = ""
        
        # Turn transition system
        self.waiting_for_phase_advance = False
        self.phase_advance_message = ""
        
        # New turn order management
        self.turn_order_manager: TurnOrderManager = None
        
    def get_current_phase(self):
        """Get the current turn phase."""
        return self.current_phase
    
    def get_turn_number(self):
        """Get the current turn number."""
        return self.turn_order_manager.turn_number if self.turn_order_manager else self.turn_number
    
    def initialize_turn_order(self, survivors):
        """Initialize the turn order manager with survivors."""
        self.turn_order_manager = TurnOrderManager(survivors)
        print(f"Turn order initialized for {len(survivors)} survivors")
        turn_info = self.turn_order_manager.get_turn_info()
        print(f"First player: {turn_info['first_player']}")
    
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
        # Use turn order manager if available
        if self.turn_order_manager:
            self.turn_order_manager.advance_turn()
            self.turn_number = self.turn_order_manager.turn_number
        else:
            # Fallback to old behavior
            self.turn_number += 1
        
        self.current_phase = TurnPhase.SURVIVOR_TURN
        self.current_survivor_index = 0
        self.survivors_acted.clear()
        self.phase_complete = False
        self.phase_timer = 0
        
        # Reset survivor actions for new turn
        if hasattr(self, '_current_game_state') and self._current_game_state:
            for survivor in self._current_game_state.survivors:
                if survivor.alive:
                    survivor.actions_remaining = survivor.max_actions
        
        # Reset initialization flags
        if hasattr(self, '_survivor_turn_initialized'):
            self._survivor_turn_initialized = False
        if hasattr(self, '_zombie_turn_initialized'):
            self._zombie_turn_initialized = False
        if hasattr(self, '_zombie_index'):
            self._zombie_index = 0
        
        if not self.turn_order_manager:
            print(f"=== Starting Turn {self.turn_number} ===")
            print("All survivors have 3 actions restored")
        
        # Trigger turn change callback
        if self.on_turn_change:
            self.on_turn_change(self.turn_number)
    
    def update(self, dt):
        """Update the turn manager (called each frame)."""
        if self.game_paused:
            return
            
        # Update phase timer (but no automatic progression)
        self.phase_timer += dt
        
        # All phase progression now requires user input (Space or Enter)
    
    def handle_event(self, event):
        """Handle input events for turn management."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                # Space or Enter advances to next phase (only if not waiting for survivor action or selection)
                if not self.waiting_for_action and not self.waiting_for_survivor_selection and self.phase_complete:
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
            elif self.waiting_for_survivor_selection and self.current_phase == TurnPhase.ZOMBIE_TURN:
                # Handle survivor target selection for zombie combat
                if event.key == pygame.K_1 and len(self.available_target_survivors) >= 1:
                    return self.select_survivor_target(0)
                elif event.key == pygame.K_2 and len(self.available_target_survivors) >= 2:
                    return self.select_survivor_target(1)
                elif event.key == pygame.K_3 and len(self.available_target_survivors) >= 3:
                    return self.select_survivor_target(2)
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
                if self.turn_order_manager:
                    # Advance to next survivor in turn order
                    self.turn_order_manager.get_next_survivor()
                else:
                    # Fallback to old behavior
                    self.current_survivor_index += 1
                # Immediately find next survivor
                self._find_next_survivor()
        
        return success
    
    def execute_move(self, direction):
        """Execute a move action directly using cursor keys."""
        from .actions import Action, ActionType, ActionValidator
        
        if not self.current_survivor or not hasattr(self, '_current_game_state'):
            return False
        
        # Validate the move
        if not ActionValidator.validate_move(self.current_survivor.position, direction):
            print(f"Invalid move {direction.name}")
            return False
        
        # Create and execute the move action
        new_position = self.current_survivor.position + direction
        action = Action(
            action_type=ActionType.MOVE,
            actor_id=self.current_survivor.id,
            target_position=new_position,
            direction=direction
        )
        
        result = self._current_game_state.execute_action(action)
        print(f"  {result.message}")
        
        if result.success:
            # Check if survivor is done with actions
            if not self.current_survivor.can_act():
                if self.turn_order_manager:
                    self.turn_order_manager.get_next_survivor()
                else:
                    self.current_survivor_index += 1
                # Find next survivor
                self._find_next_survivor()
        
        return result.success
    
    def execute_attack(self):
        """Execute an attack action directly using 'a' key."""
        from .actions import Action, ActionType
        
        if not self.current_survivor or not hasattr(self, '_current_game_state'):
            return False
        
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
                
                if result.success:
                    # Check if survivor is done with actions
                    if not self.current_survivor.can_act():
                        if self.turn_order_manager:
                            self.turn_order_manager.get_next_survivor()
                        else:
                            self.current_survivor_index += 1
                        # Find next survivor
                        self._find_next_survivor()
                
                return result.success
        
        print("  No zombie found to attack")
        return False
    
    def execute_skip_turn(self):
        """Skip remaining actions for current survivor."""
        if not self.current_survivor:
            return False
        
        # Skip all remaining actions
        self.current_survivor.actions_remaining = 0
        print(f"  {self.current_survivor.name} skipped remaining actions")
        
        # Move to next survivor
        if self.turn_order_manager:
            self.turn_order_manager.get_next_survivor()
        else:
            self.current_survivor_index += 1
        
        # Find next survivor
        self._find_next_survivor()
        
        return True
    
    def get_current_survivor(self):
        """Get the currently active survivor."""
        return self.current_survivor
    
    def is_waiting_for_action(self):
        """Check if the game is waiting for a survivor action."""
        return self.waiting_for_action
    
    def is_waiting_for_phase_advance(self):
        """Check if the game is waiting for user to advance to next phase."""
        return self.waiting_for_phase_advance
    
    def get_phase_advance_message(self):
        """Get the phase advance message to display."""
        return self.phase_advance_message
    
    def advance_to_next_phase(self):
        """Advance from waiting state to next phase."""
        if self.waiting_for_phase_advance:
            print(f"Advancing from {self.get_phase_name()} to next phase...")
            self.waiting_for_phase_advance = False
            self.phase_advance_message = ""
            # Actually advance the phase, don't just mark it complete
            self.advance_phase()
            print(f"Phase advanced to: {self.get_phase_name()}")
            return True
        return False
    
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
            
            # Initialize turn order manager if not already done
            if not self.turn_order_manager:
                self.initialize_turn_order(game_state.survivors)
            
            self.current_survivor_index = 0
            print("=== Survivor Turn Started (Manual Control) ===")
            
            # Show turn order information
            if self.turn_order_manager:
                turn_info = self.turn_order_manager.get_turn_info()
                print(f"Turn order: {' → '.join(turn_info['turn_order'])}")
            
            for survivor in game_state.survivors:
                if survivor.alive:
                    print(f"  {survivor.name}: {survivor.actions_remaining} actions remaining")
        
        # If not waiting for action, find next survivor who can act
        if not self.waiting_for_action:
            self._find_next_survivor()
    
    def _get_available_actions(self, survivor, game_state):
        """Get available actions for a survivor."""
        actions = []
        
        # Show cursor key instructions instead of individual move actions
        actions.append("Use cursor keys to move")
        
        # Add attack actions
        targets_in_zone = []
        for zombie in game_state.zombies:
            if zombie.alive and zombie.position == survivor.position:
                targets_in_zone.append(zombie)
        
        if targets_in_zone:
            actions.append("Press 'a' to attack")
        
        # Show skip instruction
        actions.append("Press 'space' to skip turn")
        
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
    
    def select_survivor_target(self, target_index):
        """Select a survivor target for zombie combat."""
        if not self.waiting_for_survivor_selection or target_index >= len(self.available_target_survivors):
            return False
        
        target_survivor = self.available_target_survivors[target_index]
        self._inflict_wound(target_survivor, self.attacking_zombie, self._current_game_state)
        
        # Reset combat state
        self.attacking_zombie.consume_action()
        self._zombie_index += 1
        self.waiting_for_survivor_selection = False
        self.attacking_zombie = None
        self.available_target_survivors = []
        self.combat_message = ""
        
        return True
    
    def _find_next_survivor(self):
        """Find the next survivor who can act."""
        if not hasattr(self, '_current_game_state') or not self._current_game_state:
            return
        
        game_state = self._current_game_state
        
        # Use turn order manager if available
        if self.turn_order_manager:
            active_survivor = self.turn_order_manager.get_current_survivor()
            
            # If current survivor can't act, find next one
            while active_survivor and not active_survivor.can_act():
                active_survivor = self.turn_order_manager.get_next_survivor()
            
            if active_survivor:
                self.current_survivor = active_survivor
                # Generate available actions
                self.available_actions = self._get_available_actions(active_survivor, game_state)
                self.waiting_for_action = True
                
                turn_info = self.turn_order_manager.get_turn_info()
                position = self.turn_order_manager.get_position_in_turn(active_survivor) + 1
                print(f"\n=== {active_survivor.name}'s Turn ({position}/{len(turn_info['turn_order'])}) ===")
                print(f"Actions remaining: {active_survivor.actions_remaining}")
                print("Available actions:")
                for i, action in enumerate(self.available_actions):
                    print(f"  {i+1}. {action}")
            else:
                # All survivors have completed their actions - wait for user to advance
                print("All survivors have completed their actions")
                self._survivor_turn_initialized = False
                self.waiting_for_action = False
                self.waiting_for_phase_advance = True
                self.phase_advance_message = "Press 'space' for zombie's turn"
                print(self.phase_advance_message)
        else:
            # Fallback to old behavior
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
                print("All survivors have completed their actions")
                self._survivor_turn_initialized = False
                self.mark_phase_complete()
    
    def _inflict_wound(self, survivor, zombie, game_state):
        """Inflict a wound on a survivor."""
        old_wounds = survivor.wounds
        died = survivor.take_damage()
        
        message = f"{zombie.name} attacks {survivor.name} - {survivor.name} takes 1 wound ({old_wounds + 1}/2)"
        if died:
            message += f" and dies!"
            print(f"    {message}")
            # Update survivor data to reflect death
            if hasattr(survivor, 'survivor_data'):
                survivor.survivor_data['wounds'] = survivor.wounds
        else:
            print(f"    {message}")
            # Update survivor data
            if hasattr(survivor, 'survivor_data'):
                survivor.survivor_data['wounds'] = survivor.wounds
    
    def process_zombie_turn(self, game_state):
        """Process the zombie turn phase with automatic combat."""
        if not hasattr(game_state, 'zombies') or len(game_state.zombies) == 0:
            self.mark_phase_complete()
            return
        
        # Store game state reference
        self._current_game_state = game_state
        
        # Initialize zombie turns if not done yet
        if not hasattr(self, '_zombie_turn_initialized') or not self._zombie_turn_initialized:
            game_state.start_entity_turns(type(game_state.zombies[0]))
            self._zombie_turn_initialized = True
            self._zombie_index = 0
            print("=== Zombie Turn Started (Combat Phase) ===")
            print(f"  Restoring actions for {len([z for z in game_state.zombies if z.alive])} alive zombies")
        
        # If waiting for survivor selection, don't process other zombies
        if self.waiting_for_survivor_selection:
            return
        
        # Process zombies one by one (one per game loop iteration)
        if self._zombie_index < len(game_state.zombies):
            zombie = game_state.zombies[self._zombie_index]
            
            if zombie.alive and zombie.can_act():
                print(f"  Processing {zombie.name} (ID: {zombie.id}) at position ({zombie.position.row}, {zombie.position.col}) - Actions: {zombie.actions_remaining}/{zombie.max_actions}")
                
                # Ensure zombie has actions remaining, otherwise move to next zombie
                if zombie.actions_remaining == 0:
                    print(f"    {zombie.name} has already acted this turn, skipping")
                    self._zombie_index += 1
                    return
                # Check for survivors in same zone
                survivors_in_zone = [s for s in game_state.survivors 
                                   if s.position == zombie.position and s.alive]
                
                if survivors_in_zone:
                    # Zombie automatically attacks - inflict wound
                    if len(survivors_in_zone) == 1:
                        # Only one survivor - direct attack
                        target = survivors_in_zone[0]
                        self._inflict_wound(target, zombie, game_state)
                        zombie.actions_remaining -= 1
                        self._zombie_index += 1
                    else:
                        # Multiple survivors - player must choose target
                        self.attacking_zombie = zombie
                        self.available_target_survivors = survivors_in_zone
                        self.waiting_for_survivor_selection = True
                        self.combat_message = f"{zombie.name} attacks! Choose target survivor:"
                        print(f"\n{self.combat_message}")
                        for i, survivor in enumerate(survivors_in_zone):
                            print(f"  {i+1}. {survivor.name} (Wounds: {survivor.wounds}/2)")
                        return  # Wait for player input
                else:
                    # No survivors in zone - move toward closest survivor
                    action = zombie.decide_action(game_state)
                    if action:
                        result = game_state.execute_action(action)
                        print(f"    {result.message}")
                    else:
                        zombie.actions_remaining -= 1
                    self._zombie_index += 1
            else:
                self._zombie_index += 1
        
        # All zombies processed
        if self._zombie_index >= len(game_state.zombies):
            if not self.phase_complete:
                print("All zombies have completed their actions")
                self._zombie_turn_initialized = False
                self.mark_phase_complete()
    
    def process_zombie_spawn(self):
        """Process the zombie spawn phase."""
        # Soon, loop for each spawn zone and spawn zombies
        if not self.phase_complete:
            # For now, just spawn 1 zombie per turn
            spawn_count = 1
            print(f"  Spawning {spawn_count} new zombies")
            
            # Spawn zombies at (2,2) spawn zone
            if hasattr(self, '_current_game_state') and self._current_game_state:
                from .actions import Position
                spawn_pos = Position(2, 2)
                
                for i in range(spawn_count):
                    zombie = self._current_game_state.spawn_zombie(spawn_pos)
                    print(f"    Spawned {zombie.name} (ID: {zombie.id}) at ({spawn_pos.row}, {spawn_pos.col})")
            
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
        base_info = {
            'turn_number': self.turn_number,
            'phase': self.current_phase,
            'phase_name': self.get_phase_name(),
            'phase_complete': self.phase_complete,
            'survivors_acted': len(self.survivors_acted),
            'paused': self.game_paused
        }
        
        # Add turn order information if available
        if self.turn_order_manager:
            base_info['turn_order_info'] = self.turn_order_manager.get_turn_info()
        
        return base_info
    
    # def reset(self):
    #    """Reset the turn manager to initial state."""
    #    self.current_phase = TurnPhase.SURVIVOR_TURN
    #    self.turn_number = 1
    #    self.current_survivor_index = 0
    #    self.survivors_acted.clear()
    #    self.phase_complete = False
    #    self.game_paused = False
    #    self.phase_timer = 0
    #    print("Turn manager reset to initial state")