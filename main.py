from ui.game_window import GameWindow

def main():
    # Create game window with specified dimensions
    game_window = GameWindow(width=1200, height=1000, title="Zombicide Game")
    
    try:
        # Load the map data into the game window
        game_window.load_map("maps_db.json", map_index=0)
        
        # Run the game loop
        game_window.run()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Ensure proper cleanup
        game_window.cleanup()

if __name__ == "__main__":
    main()