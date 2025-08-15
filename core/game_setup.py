"""
GameSetup handles data loading and game state initialization for the Zombicide game.
This class is responsible for loading maps and survivors from JSON files and setting up the initial game state.
"""
import json
from typing import Dict, List, Any, Tuple, Optional
from .entities import GameState, Survivor, Zombie
from .actions import Position


class GameSetupError(Exception):
    """Custom exception for game setup errors."""
    pass


class GameSetup:
    """Handles data loading and game state initialization."""
    
    # Class variable to store weapons database
    _weapons_db = None
    
    @staticmethod
    def load_weapons_data(json_path: str = "weapons_db.json") -> Optional[Dict[str, Any]]:
        """
        Load weapons data from JSON file.
        
        Args:
            json_path: Path to the weapons JSON file (default: weapons_db.json)
            
        Returns:
            Dictionary containing weapons data, or None if loading fails
            
        Raises:
            GameSetupError: If file cannot be loaded or parsed
        """
        try:
            with open(json_path, 'r') as f:
                weapons_data = json.load(f)
            
            if 'weapons' not in weapons_data:
                raise GameSetupError(f"Invalid weapons file format: missing 'weapons' key in {json_path}")
            
            # Store in class variable for easy access
            GameSetup._weapons_db = weapons_data
            print(f"Loaded {len(weapons_data['weapons'])} weapons from database")
            return weapons_data
            
        except FileNotFoundError:
            raise GameSetupError(f"Weapons file not found: {json_path}")
        except json.JSONDecodeError as e:
            raise GameSetupError(f"Invalid JSON in weapons file {json_path}: {e}")
        except Exception as e:
            raise GameSetupError(f"Error loading weapons from {json_path}: {e}")
    
    @staticmethod
    def get_weapon_stats(weapon_name: str) -> Optional[Dict[str, Any]]:
        """
        Get weapon statistics by name.
        
        Args:
            weapon_name: Name of the weapon to look up
            
        Returns:
            Dictionary with weapon stats, or None if not found
        """
        if not GameSetup._weapons_db:
            return None
        
        for weapon in GameSetup._weapons_db['weapons']:
            if weapon['name'].lower() == weapon_name.lower():
                return weapon
        return None
    
    @staticmethod
    def load_map_data(json_path: str, map_index: int = 0) -> Optional[Dict[str, Any]]:
        """
        Load map data from JSON file.
        
        Args:
            json_path: Path to the maps JSON file
            map_index: Index of the map to load (default: 0)
            
        Returns:
            Dictionary containing map data, or None if loading fails
            
        Raises:
            GameSetupError: If there's an error loading or parsing the map data
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            if "maps" not in data:
                raise GameSetupError(f"Invalid map file format: missing 'maps' key")
                
            if map_index >= len(data["maps"]):
                raise GameSetupError(f"Map index {map_index} out of range (available: 0-{len(data['maps'])-1})")
                
            map_data = data["maps"][map_index]
            print(f"Loaded map: {map_data.get('name', 'Unnamed')}")
            return map_data
            
        except FileNotFoundError:
            raise GameSetupError(f"Map file not found: {json_path}")
        except json.JSONDecodeError as e:
            raise GameSetupError(f"Invalid JSON in map file: {e}")
        except Exception as e:
            raise GameSetupError(f"Error loading map data: {e}")
    
    @staticmethod
    def load_survivor_data(json_path: str) -> List[Dict[str, Any]]:
        """
        Load survivor data from JSON file.
        
        Args:
            json_path: Path to the survivors JSON file
            
        Returns:
            List of survivor data dictionaries
            
        Raises:
            GameSetupError: If there's an error loading or parsing the survivor data
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            if "survivors" not in data:
                raise GameSetupError(f"Invalid survivor file format: missing 'survivors' key")
                
            survivors_data = data["survivors"]
            print(f"Loaded {len(survivors_data)} survivors")
            return survivors_data
            
        except FileNotFoundError:
            raise GameSetupError(f"Survivor file not found: {json_path}")
        except json.JSONDecodeError as e:
            raise GameSetupError(f"Invalid JSON in survivor file: {e}")
        except Exception as e:
            raise GameSetupError(f"Error loading survivor data: {e}")
    
    @staticmethod
    def initialize_game_state(survivor_data: List[Dict[str, Any]], 
                             initial_survivor_position: Tuple[int, int] = (0, 2),
                             initial_zombie_position: Tuple[int, int] = (2, 2),
                             zombie_count: int = 2) -> GameState:
        """
        Initialize the game state with survivors and zombies.
        
        Args:
            survivor_data: List of survivor data from JSON
            initial_survivor_position: Starting position for survivors (row, col)
            initial_zombie_position: Starting position for zombies (row, col)  
            zombie_count: Number of zombies to create
            
        Returns:
            Initialized GameState object
            
        Raises:
            GameSetupError: If there's an error initializing the game state
        """
        try:
            game_state = GameState()
            
            # Initialize survivors
            survivor_pos = Position(initial_survivor_position[0], initial_survivor_position[1])
            for i, survivor_info in enumerate(survivor_data):
                survivor_id = f"survivor_{i}"
                survivor = Survivor(survivor_id, survivor_info['name'], survivor_pos, survivor_info)
                game_state.add_survivor(survivor)
                print(f"  Added survivor: {survivor.name} at position ({survivor_pos.row}, {survivor_pos.col})")
            
            # Initialize zombies
            zombie_pos = Position(initial_zombie_position[0], initial_zombie_position[1])
            for i in range(zombie_count):
                zombie_id = f"zombie_{i}"
                zombie = Zombie(zombie_id, zombie_pos)
                game_state.add_zombie(zombie)
                print(f"  Added {zombie.name} at position ({zombie_pos.row}, {zombie_pos.col})")
            
            print(f"Game state initialized with {len(game_state.survivors)} survivors and {len(game_state.zombies)} zombies")
            return game_state
            
        except Exception as e:
            raise GameSetupError(f"Error initializing game state: {e}")
    
    @staticmethod
    def setup_complete_game(maps_json_path: str, survivors_json_path: str, 
                           map_index: int = 0, weapons_json_path: str = "weapons_db.json") -> Tuple[Dict[str, Any], List[Dict[str, Any]], GameState]:
        """
        Complete game setup: load all data and initialize game state.
        
        Args:
            maps_json_path: Path to maps JSON file
            survivors_json_path: Path to survivors JSON file
            map_index: Index of map to load
            
        Returns:
            Tuple of (map_data, survivor_data, game_state)
            
        Raises:
            GameSetupError: If any part of setup fails
        """
        try:
            # Load weapons data first (needed for weapon stats)
            weapons_data = GameSetup.load_weapons_data(weapons_json_path)
            if not weapons_data:
                raise GameSetupError("Failed to load weapons data")
            
            # Load map data
            map_data = GameSetup.load_map_data(maps_json_path, map_index)
            if not map_data:
                raise GameSetupError("Failed to load map data")
            
            # Load survivor data
            survivor_data = GameSetup.load_survivor_data(survivors_json_path)
            if not survivor_data:
                raise GameSetupError("Failed to load survivor data")
            
            # Initialize game state
            game_state = GameSetup.initialize_game_state(survivor_data)
            
            print("=== Game Setup Complete ===")
            return map_data, survivor_data, game_state
            
        except GameSetupError:
            # Re-raise setup errors as-is
            raise
        except Exception as e:
            raise GameSetupError(f"Unexpected error during game setup: {e}")
    
    @staticmethod
    def validate_setup_files(maps_json_path: str, survivors_json_path: str) -> bool:
        """
        Validate that setup files exist and have basic required structure.
        
        Args:
            maps_json_path: Path to maps JSON file
            survivors_json_path: Path to survivors JSON file
            
        Returns:
            True if files are valid, False otherwise
        """
        try:
            # Quick validation - just check if we can load the data
            GameSetup.load_map_data(maps_json_path, 0)
            GameSetup.load_survivor_data(survivors_json_path)
            return True
        except GameSetupError:
            return False