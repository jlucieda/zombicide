from ui.game_window import GameWindow
from draw_survivors import draw_all_survivors

def main():
    # Create game window with exact pixel dimensions (1200x1000)
    game_window = GameWindow(width=1200, height=900, title="Zombicide Game")
    
    try:
        # Load the map data into the game window
        game_window.load_map("maps_db.json", map_index=0)
        
        # Load survivor data
        game_window.load_survivors("survivors_db.json")
        
        # Main game loop
        while game_window.running:
            # Handle events
            game_window.handle_events()
            
            # Update game state
            game_window.update()
            
            # Draw everything
            game_window.screen.fill(game_window.BLACK)
            game_window.draw_map()
            
            # Draw survivor cards
            draw_all_survivors("survivors_db.json", game_window.screen)
            
            # Draw survivor tokens in zone (0,2)
            game_window.draw_survivor_tokens()
            
            # Draw zombie tokens in zone (2,2)
            game_window.draw_zombie_tokens()
            
            # Update display
            game_window.draw()
            game_window.clock.tick(60)  # 60 FPS
            
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Ensure proper cleanup
        game_window.cleanup()

if __name__ == "__main__":
    main()