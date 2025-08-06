#!/usr/bin/env python3
"""
Test script to demonstrate the action system functionality.
Press SPACE to advance through phases and see actions in real time.
"""

import pygame
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.turn_manager import TurnManager, TurnPhase
from core.entities import GameState, Survivor, Zombie
from core.actions import Position

def test_action_system():
    pygame.init()
    
    # Create a simple test window
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Action System Test - Press SPACE to advance")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    # Initialize game state
    game_state = GameState()
    
    # Create test survivors
    survivor_data = {'name': 'Eva', 'wounds': 0, 'exp': 0, 'level': 'blue', 'equipment': {}}
    survivor1 = Survivor("survivor_0", "Eva", Position(0, 2), survivor_data)
    game_state.add_survivor(survivor1)
    
    survivor_data2 = {'name': 'Josh', 'wounds': 0, 'exp': 0, 'level': 'blue', 'equipment': {}}
    survivor2 = Survivor("survivor_1", "Josh", Position(0, 2), survivor_data2)
    game_state.add_survivor(survivor2)
    
    # Create test zombies
    zombie1 = Zombie("zombie_0", Position(2, 2))
    zombie2 = Zombie("zombie_1", Position(2, 2))
    game_state.add_zombie(zombie1)
    game_state.add_zombie(zombie2)
    
    # Initialize turn manager
    turn_manager = TurnManager()
    
    last_time = pygame.time.get_ticks()
    running = True
    
    print("=== Action System Test Started ===")
    print("Controls:")
    print("  SPACE: Advance to next phase")
    print("  P: Pause/Unpause")
    print("  ESC: Quit")
    print()
    
    while running:
        # Calculate delta time
        current_time = pygame.time.get_ticks()
        dt = current_time - last_time
        last_time = current_time
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    turn_manager.handle_event(event)
        
        # Update turn manager
        turn_manager.update(dt)
        
        # Process current turn phase
        current_phase = turn_manager.get_current_phase()
        
        if current_phase == TurnPhase.SURVIVOR_TURN:
            turn_manager.process_survivor_turn(game_state)
        elif current_phase == TurnPhase.ZOMBIE_TURN:
            turn_manager.process_zombie_turn(game_state)
        elif current_phase == TurnPhase.ZOMBIE_SPAWN:
            turn_manager.process_zombie_spawn()
        elif current_phase == TurnPhase.TURN_END:
            turn_manager.process_turn_end()
        
        # Draw everything
        screen.fill((30, 30, 40))  # Dark blue background
        
        # Draw 3x3 grid
        grid_size = 150
        start_x = 50
        start_y = 50
        
        for row in range(3):
            for col in range(3):
                x = start_x + col * grid_size
                y = start_y + row * grid_size
                
                # Draw zone
                pygame.draw.rect(screen, (200, 200, 200), (x, y, grid_size, grid_size), 2)
                
                # Draw zone coordinates
                coord_text = f"({row},{col})"
                coord_surface = small_font.render(coord_text, True, (150, 150, 150))
                screen.blit(coord_surface, (x + 5, y + 5))
        
        # Draw entities
        for survivor in game_state.survivors:
            if survivor.alive:
                x = start_x + survivor.position.col * grid_size + grid_size // 2
                y = start_y + survivor.position.row * grid_size + grid_size // 2
                
                # Draw survivor token
                pygame.draw.circle(screen, (255, 255, 255), (x, y), 20)
                pygame.draw.circle(screen, (0, 0, 0), (x, y), 20, 2)
                
                # Draw name
                name_surface = small_font.render(survivor.name[:3], True, (0, 0, 0))
                name_rect = name_surface.get_rect(center=(x, y))
                screen.blit(name_surface, name_rect)
                
                # Draw actions remaining
                actions_text = f"{survivor.actions_remaining}"
                actions_surface = small_font.render(actions_text, True, (255, 0, 0))
                screen.blit(actions_surface, (x - 10, y - 35))
        
        for zombie in game_state.zombies:
            if zombie.alive:
                x = start_x + zombie.position.col * grid_size + grid_size // 2 + 25
                y = start_y + zombie.position.row * grid_size + grid_size // 2
                
                # Draw zombie token
                pygame.draw.circle(screen, (100, 100, 100), (x, y), 20)
                pygame.draw.circle(screen, (0, 0, 0), (x, y), 20, 2)
                
                # Draw Z
                z_surface = font.render('Z', True, (255, 255, 255))
                z_rect = z_surface.get_rect(center=(x, y))
                screen.blit(z_surface, z_rect)
                
                # Draw actions remaining
                actions_text = f"{zombie.actions_remaining}"
                actions_surface = small_font.render(actions_text, True, (255, 0, 0))
                screen.blit(actions_surface, (x - 10, y - 35))
        
        # Get turn info
        turn_info = turn_manager.get_turn_info()
        
        # Draw turn information
        info_x = 550
        y_pos = 50
        line_height = 30
        
        # Turn number
        turn_text = f"Turn: {turn_info['turn_number']}"
        turn_surface = font.render(turn_text, True, (255, 255, 255))
        screen.blit(turn_surface, (info_x, y_pos))
        y_pos += line_height
        
        # Current phase
        phase_color = (255, 255, 0) if not turn_info['phase_complete'] else (0, 255, 0)
        phase_text = f"Phase: {turn_info['phase_name']}"
        phase_surface = font.render(phase_text, True, phase_color)
        screen.blit(phase_surface, (info_x, y_pos))
        y_pos += line_height
        
        # Status
        status = "Complete" if turn_info['phase_complete'] else "In Progress"
        status_color = (0, 255, 0) if turn_info['phase_complete'] else (255, 255, 0)
        status_text = f"Status: {status}"
        status_surface = font.render(status_text, True, status_color)
        screen.blit(status_surface, (info_x, y_pos))
        y_pos += line_height * 2
        
        # Entity status
        status_text = "Survivors:"
        status_surface = font.render(status_text, True, (255, 255, 255))
        screen.blit(status_surface, (info_x, y_pos))
        y_pos += line_height
        
        for survivor in game_state.survivors:
            if survivor.alive:
                pos_text = f"  {survivor.name}: ({survivor.position.row},{survivor.position.col}) - {survivor.actions_remaining} actions"
                pos_surface = small_font.render(pos_text, True, (200, 200, 200))
                screen.blit(pos_surface, (info_x, y_pos))
                y_pos += 20
        
        y_pos += 10
        status_text = "Zombies:"
        status_surface = font.render(status_text, True, (255, 255, 255))
        screen.blit(status_surface, (info_x, y_pos))
        y_pos += line_height
        
        for zombie in game_state.zombies:
            if zombie.alive:
                pos_text = f"  {zombie.name}: ({zombie.position.row},{zombie.position.col}) - {zombie.actions_remaining} actions"
                pos_surface = small_font.render(pos_text, True, (200, 200, 200))
                screen.blit(pos_surface, (info_x, y_pos))
                y_pos += 20
        
        # Controls
        y_pos += 50
        controls = [
            "SPACE: Next Phase",
            "P: Pause/Unpause", 
            "ESC: Quit"
        ]
        
        for control in controls:
            control_surface = small_font.render(control, True, (180, 180, 180))
            screen.blit(control_surface, (info_x, y_pos))
            y_pos += 25
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\n=== Action System Test Completed ===")

if __name__ == "__main__":
    test_action_system()