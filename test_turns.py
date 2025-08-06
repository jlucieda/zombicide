#!/usr/bin/env python3
"""
Test script to demonstrate the turn system functionality.
Press SPACE to advance through phases, P to pause/unpause, ESC to quit.
"""

import pygame
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.turn_manager import TurnManager, TurnPhase

def test_turn_system():
    pygame.init()
    
    # Create a simple test window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Turn System Test - Press SPACE to advance, P to pause, ESC to quit")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # Initialize turn manager
    turn_manager = TurnManager()
    
    # Test data
    survivors = [{'name': 'Eva'}, {'name': 'Josh'}]
    zombies = [{'id': 0}, {'id': 1}]
    
    last_time = pygame.time.get_ticks()
    running = True
    
    print("=== Turn System Test Started ===")
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
            turn_manager.process_survivor_turn(survivors)
        elif current_phase == TurnPhase.ZOMBIE_TURN:
            turn_manager.process_zombie_turn(zombies)
        elif current_phase == TurnPhase.ZOMBIE_SPAWN:
            turn_manager.process_zombie_spawn()
        elif current_phase == TurnPhase.TURN_END:
            turn_manager.process_turn_end()
        
        # Draw everything
        screen.fill((30, 30, 40))  # Dark blue background
        
        # Get turn info
        turn_info = turn_manager.get_turn_info()
        
        # Draw turn information
        y_pos = 50
        line_height = 50
        
        # Turn number
        turn_text = f"Turn: {turn_info['turn_number']}"
        turn_surface = font.render(turn_text, True, (255, 255, 255))
        screen.blit(turn_surface, (50, y_pos))
        y_pos += line_height
        
        # Current phase
        phase_color = (255, 255, 0) if not turn_info['phase_complete'] else (0, 255, 0)
        phase_text = f"Phase: {turn_info['phase_name']}"
        phase_surface = font.render(phase_text, True, phase_color)
        screen.blit(phase_surface, (50, y_pos))
        y_pos += line_height
        
        # Status
        status = "Complete" if turn_info['phase_complete'] else "In Progress"
        status_color = (0, 255, 0) if turn_info['phase_complete'] else (255, 255, 0)
        status_text = f"Status: {status}"
        status_surface = font.render(status_text, True, status_color)
        screen.blit(status_surface, (50, y_pos))
        y_pos += line_height
        
        # Pause indicator
        if turn_info['paused']:
            pause_text = "PAUSED"
            pause_surface = font.render(pause_text, True, (255, 0, 0))
            screen.blit(pause_surface, (50, y_pos))
            y_pos += line_height
        
        # Controls
        y_pos += 50
        controls = [
            "SPACE: Next Phase",
            "P: Pause/Unpause", 
            "ESC: Quit"
        ]
        
        for control in controls:
            control_surface = small_font.render(control, True, (180, 180, 180))
            screen.blit(control_surface, (50, y_pos))
            y_pos += 30
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\n=== Turn System Test Completed ===")

if __name__ == "__main__":
    test_turn_system()