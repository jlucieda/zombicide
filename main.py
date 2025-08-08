from ui.game_window import GameWindow

def main():
    # Create game window with exact pixel dimensions (1200x900)
    game_window = GameWindow(width=1200, height=900, title="Zombicide Game")
    
    try:
        # Load the map data into the game window
        game_window.load_map("maps_db.json", map_index=0)
        
        # Load survivor data
        game_window.load_survivors("survivors_db.json")
        
        # Run the proper turn system integrated with GameWindow
        game_window.run()
            
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Ensure proper cleanup
        game_window.cleanup()

if __name__ == "__main__":
    main()