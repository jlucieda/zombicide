from ui import GameWindow
from draw_map import draw_map_from_json

def main():
    # Create game window with specified dimensions
    game_window = GameWindow(width=1200, height=1000, title="Zombicide Game")
    
    try:
        # Draw the map from the JSON database using the new draw_map module
        draw_map_from_json("maps_db.json", map_index=0)
        
        # Run the game loop
        game_window.run()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Ensure proper cleanup
        game_window.cleanup()

if __name__ == "__main__":
    main()