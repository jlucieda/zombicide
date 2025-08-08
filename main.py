from core.game_application import GameApplication
from core.game_setup import GameSetupError

def main():
    """Main entry point for the Zombicide game."""
    # Create the game application
    app = GameApplication(width=1200, height=900, title="Zombicide Game")
    
    try:
        # Load game data
        app.load_game_data("maps_db.json", "survivors_db.json", map_index=0)
        
        # Run the game
        app.run()
        
    except GameSetupError as e:
        print(f"Game setup failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure proper cleanup
        app.cleanup()

if __name__ == "__main__":
    main()