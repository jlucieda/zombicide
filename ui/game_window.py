import pygame
import json
import sys
from core.turn_manager import TurnManager, TurnPhase
from core.entities import GameState, Survivor, Zombie
from core.actions import Position

class GameWindow:
    def __init__(self, width=1200, height=900, title="Zombicide Game"):
        """Initialize game window with pygame"""
        pygame.init()
        
        # Window properties
        self.width = width
        self.height = height
        self.title = title
        self.running = True
        
        # Create pygame window
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (238, 238, 238)
        self.BUILDING_COLOR = (210, 180, 140)  # light brown
        self.STREET_COLOR = (238, 238, 238)   # light gray
        self.BLUE = (0, 0, 255)
        
        # Drawing constants
        self.TILE_SIZE = 3
        self.ZONE_PIXEL_SIZE = 150  # Each zone is 150x150 pixels
        self.MAP_START_X = 50
        self.MAP_START_Y = 50
        self.WALL_WIDTH = 4
        
        # Fonts
        self.font_large = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 14)
        
        # Game data
        self.map_data = None
        self.survivors_data = None
        self.game_state = GameState()
        
        # Turn management
        self.turn_manager = TurnManager()
        self.turn_manager.on_phase_change = self.on_phase_change
        self.turn_manager.on_turn_change = self.on_turn_change

    def load_map(self, json_path, map_index=0):
        """Load map data from JSON file."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            self.map_data = data["maps"][map_index]
            print(f"Loaded map: {self.map_data.get('name', 'Unnamed')}")
        except (FileNotFoundError, KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error loading map data: {e}")
            self.map_data = None
    
    def load_survivors(self, json_path):
        """Load survivor data from JSON file."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            self.survivors_data = data["survivors"]
            print(f"Loaded {len(self.survivors_data)} survivors")
            
            # Initialize survivors in game state
            self.game_state.survivors.clear()
            for i, survivor_data in enumerate(self.survivors_data):
                survivor_id = f"survivor_{i}"
                # Start survivors in zone (0,2) - top right
                position = Position(0, 2)
                survivor = Survivor(survivor_id, survivor_data['name'], position, survivor_data)
                self.game_state.add_survivor(survivor)
            
            # Initialize zombies list (zombies will spawn during gameplay)
            self.game_state.zombies.clear()
            
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"Error loading survivor data: {e}")
            self.survivors_data = []

    def draw_door(self, x, y, direction, opened=False):
        """Draw a door on the wall."""
        door_size = 40
        door_color = self.BLUE
        
        if direction == "up":
            door_x = x + (self.ZONE_PIXEL_SIZE - door_size) // 2
            door_y = y
            if opened:
                # Draw opened door as angled line
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x + door_size//2, door_y - 20), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x, door_y - 3, door_size, 6))
        elif direction == "down":
            door_x = x + (self.ZONE_PIXEL_SIZE - door_size) // 2
            door_y = y + self.ZONE_PIXEL_SIZE
            if opened:
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x + door_size//2, door_y + 20), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x, door_y - 3, door_size, 6))
        elif direction == "left":
            door_x = x
            door_y = y + (self.ZONE_PIXEL_SIZE - door_size) // 2
            if opened:
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x - 20, door_y + door_size//2), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x - 3, door_y, 6, door_size))
        elif direction == "right":
            door_x = x + self.ZONE_PIXEL_SIZE
            door_y = y + (self.ZONE_PIXEL_SIZE - door_size) // 2
            if opened:
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x + 20, door_y + door_size//2), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x - 3, door_y, 6, door_size))

    def draw_wall(self, x, y, direction):
        """Draw a wall in the specified direction."""
        wall_color = self.BLACK
        
        if direction == "up":
            pygame.draw.line(self.screen, wall_color,
                           (x, y), (x + self.ZONE_PIXEL_SIZE, y), self.WALL_WIDTH)
        elif direction == "down":
            pygame.draw.line(self.screen, wall_color,
                           (x, y + self.ZONE_PIXEL_SIZE), (x + self.ZONE_PIXEL_SIZE, y + self.ZONE_PIXEL_SIZE), self.WALL_WIDTH)
        elif direction == "left":
            pygame.draw.line(self.screen, wall_color,
                           (x, y), (x, y + self.ZONE_PIXEL_SIZE), self.WALL_WIDTH)
        elif direction == "right":
            pygame.draw.line(self.screen, wall_color,
                           (x + self.ZONE_PIXEL_SIZE, y), (x + self.ZONE_PIXEL_SIZE, y + self.ZONE_PIXEL_SIZE), self.WALL_WIDTH)

    def draw_map(self):
        """Draw the map using pygame."""
        if not self.map_data:
            return
            
        tile = self.map_data["tiles"][0][0]  # Only one tile for this map
        zones = tile["zones"]

        # Draw zones
        for zr in range(self.TILE_SIZE):
            for zc in range(self.TILE_SIZE):
                zone = zones[zr][zc]
                
                # Calculate zone position
                x = self.MAP_START_X + zc * self.ZONE_PIXEL_SIZE
                y = self.MAP_START_Y + zr * self.ZONE_PIXEL_SIZE

                # Set color based on zone type
                color = self.BUILDING_COLOR if "building" in zone["features"] else self.STREET_COLOR

                # Draw zone background
                pygame.draw.rect(self.screen, color, 
                               (x, y, self.ZONE_PIXEL_SIZE, self.ZONE_PIXEL_SIZE))
                
                # Draw zone border
                pygame.draw.rect(self.screen, self.BLACK,
                               (x, y, self.ZONE_PIXEL_SIZE, self.ZONE_PIXEL_SIZE), 2)
                
                # Draw connections (walls and doors)
                conns = zone.get("connections", {})
                for direction, conn in conns.items():
                    if conn["type"] == "wall":
                        self.draw_wall(x, y, direction)
                        if "door" in conn:
                            opened = conn.get("opened", False)
                            self.draw_door(x, y, direction, opened)
    
    def draw_survivor_tokens(self):
        """Draw survivor tokens at their current positions - white circles with black borders and names."""
        if not self.game_state.survivors:
            return
            
        # Token properties
        token_diameter = 40
        token_radius = token_diameter // 2
        border_width = 2
        CYAN = (0, 255, 255)
        
        # Get current active survivor from turn manager
        current_survivor = self.turn_manager.get_current_survivor()
        
        # Group survivors by position
        survivors_by_position = {}
        for survivor in self.game_state.survivors:
            if survivor.alive:
                pos_key = (survivor.position.row, survivor.position.col)
                if pos_key not in survivors_by_position:
                    survivors_by_position[pos_key] = []
                survivors_by_position[pos_key].append(survivor)
        
        # Draw survivors at each position
        for (row, col), survivors in survivors_by_position.items():
            zone_x = self.MAP_START_X + col * self.ZONE_PIXEL_SIZE
            zone_y = self.MAP_START_Y + row * self.ZONE_PIXEL_SIZE
            
            # Position tokens within the zone
            tokens_per_row = min(3, len(survivors))
            spacing = 10
            start_x = zone_x + spacing
            start_y = zone_y + spacing
            
            for i, survivor in enumerate(survivors):
                # Calculate position for each token
                token_row = i // tokens_per_row
                token_col = i % tokens_per_row
                
                token_x = start_x + token_col * (token_diameter + spacing) + token_radius
                token_y = start_y + token_row * (token_diameter + spacing) + token_radius
                
                # Make sure token stays within zone bounds
                if token_x + token_radius > zone_x + self.ZONE_PIXEL_SIZE or \
                   token_y + token_radius > zone_y + self.ZONE_PIXEL_SIZE:
                    continue
                
                # Color based on survivor status - cyan if active, white otherwise
                if current_survivor and survivor.id == current_survivor.id:
                    color = CYAN  # Active survivor gets cyan color
                else:
                    color = self.WHITE if survivor.alive else self.GRAY
                
                # Draw circle with black border
                pygame.draw.circle(self.screen, color, (token_x, token_y), token_radius)
                pygame.draw.circle(self.screen, self.BLACK, (token_x, token_y), token_radius, border_width)
                
                # Draw survivor name in the middle
                name_surface = self.font_small.render(survivor.name, True, self.BLACK)
                name_rect = name_surface.get_rect(center=(token_x, token_y))
                self.screen.blit(name_surface, name_rect)
    
    def draw_zombie_tokens(self):
        """Draw zombie tokens at their current positions - dark grey circles with 'Z' in the middle."""
        if not self.game_state.zombies:
            return
            
        # Token properties
        token_diameter = 40
        token_radius = token_diameter // 2
        border_width = 2
        DARK_GRAY = (64, 64, 64)
        
        # Group zombies by position
        zombies_by_position = {}
        for zombie in self.game_state.zombies:
            if zombie.alive:
                pos_key = (zombie.position.row, zombie.position.col)
                if pos_key not in zombies_by_position:
                    zombies_by_position[pos_key] = []
                zombies_by_position[pos_key].append(zombie)
        
        # Draw zombies at each position
        for (row, col), zombies in zombies_by_position.items():
            zone_x = self.MAP_START_X + col * self.ZONE_PIXEL_SIZE
            zone_y = self.MAP_START_Y + row * self.ZONE_PIXEL_SIZE
            
            # Position tokens within the zone
            tokens_per_row = min(3, len(zombies))
            spacing = 20
            start_x = zone_x + spacing
            start_y = zone_y + spacing
            
            for i, zombie in enumerate(zombies):
                # Calculate position for each token
                token_row = i // tokens_per_row
                token_col = i % tokens_per_row
                
                token_x = start_x + token_col * (token_diameter + spacing) + token_radius
                token_y = start_y + token_row * (token_diameter + spacing) + token_radius
                
                # Make sure token stays within zone bounds
                if token_x + token_radius > zone_x + self.ZONE_PIXEL_SIZE or \
                   token_y + token_radius > zone_y + self.ZONE_PIXEL_SIZE:
                    continue
                
                # Draw dark grey circle with black border
                pygame.draw.circle(self.screen, DARK_GRAY, (token_x, token_y), token_radius)
                pygame.draw.circle(self.screen, self.BLACK, (token_x, token_y), token_radius, border_width)
                
                # Draw 'Z' in the middle
                z_surface = self.font_medium.render('Z', True, self.WHITE)
                z_rect = z_surface.get_rect(center=(token_x, token_y))
                self.screen.blit(z_surface, z_rect)
    
    def draw_turn_info(self):
        """Draw turn information on the screen."""
        turn_info = self.turn_manager.get_turn_info()
        
        # Position in top-left corner
        info_x = 10
        info_y = 10
        line_height = 25
        
        # Background rectangle for better readability
        info_rect = pygame.Rect(info_x - 5, info_y - 5, 300, 120)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), info_rect)
        pygame.draw.rect(self.screen, self.WHITE, info_rect, 2)
        
        # Turn number
        turn_text = f"Turn: {turn_info['turn_number']}"
        turn_surface = self.font_large.render(turn_text, True, self.WHITE)
        self.screen.blit(turn_surface, (info_x, info_y))
        
        # Current phase
        phase_text = f"Phase: {turn_info['phase_name']}"
        phase_surface = self.font_medium.render(phase_text, True, self.WHITE)
        self.screen.blit(phase_surface, (info_x, info_y + line_height))
        
        # Phase status
        status = "Complete" if turn_info['phase_complete'] else "In Progress"
        status_color = self.WHITE if turn_info['phase_complete'] else (255, 255, 0)  # Yellow for in progress
        status_text = f"Status: {status}"
        status_surface = self.font_small.render(status_text, True, status_color)
        self.screen.blit(status_surface, (info_x, info_y + line_height * 2))
        
        # Controls info
        controls_text = "SPACE: Next Phase | P: Pause | ESC: Quit"
        controls_surface = self.font_small.render(controls_text, True, (200, 200, 200))
        self.screen.blit(controls_surface, (info_x, info_y + line_height * 3))

    def on_phase_change(self, new_phase):
        """Callback when turn phase changes."""
        print(f"Phase changed to: {self.turn_manager.get_phase_name()}")
    
    def on_turn_change(self, new_turn):
        """Callback when turn number changes."""
        print(f"Starting turn {new_turn}")

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    # Let turn manager handle other key events
                    self.turn_manager.handle_event(event)

    def update(self, dt):
        """Update game state."""
        # Update turn manager
        self.turn_manager.update(dt)
        
        # Process current turn phase
        current_phase = self.turn_manager.get_current_phase()
        
        if current_phase == TurnPhase.SURVIVOR_TURN:
            self.turn_manager.process_survivor_turn(self.game_state)
        elif current_phase == TurnPhase.ZOMBIE_TURN:
            self.turn_manager.process_zombie_turn(self.game_state)
        elif current_phase == TurnPhase.ZOMBIE_SPAWN:
            self.turn_manager.process_zombie_spawn()
        elif current_phase == TurnPhase.TURN_END:
            self.turn_manager.process_turn_end()

    def draw_survivor_cards(self):
        """Draw survivor cards with highlighting and actions display."""
        if not self.survivors_data:
            return
            
        # Colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GRAY = (200, 200, 200)
        BLUE = (0, 0, 255)
        YELLOW = (255, 255, 0)
        ORANGE = (255, 165, 0)
        RED = (255, 0, 0)
        CYAN = (0, 255, 255)
        
        level_colors = {
            'blue': BLUE,
            'yellow': YELLOW, 
            'orange': ORANGE,
            'red': RED
        }
        
        # Get current active survivor
        current_survivor = self.turn_manager.get_current_survivor()
        
        # Position cards to the right of the map
        card_width = 280
        card_height = 380
        card_start_x = 550
        spacing = 20
        
        for i, survivor_data in enumerate(self.survivors_data):
            # Find corresponding survivor entity for actions
            survivor_entity = None
            for survivor in self.game_state.survivors:
                if survivor.name == survivor_data['name']:
                    survivor_entity = survivor
                    break
            
            card_x = card_start_x
            card_y = 50 + (i * (card_height + spacing))
            
            # Determine if this survivor is active
            is_active = (current_survivor and survivor_entity and 
                        current_survivor.id == survivor_entity.id)
            
            # Draw card background with highlighting
            border_color = CYAN if is_active else WHITE
            border_width = 5 if is_active else 3
            
            pygame.draw.rect(self.screen, border_color, (card_x, card_y, card_width, card_height), border_width)
            pygame.draw.rect(self.screen, GRAY, (card_x+border_width, card_y+border_width, 
                           card_width-2*border_width, card_height-2*border_width))
            
            # Draw survivor name with highlighting
            name_color = CYAN if is_active else BLACK
            name_surface = self.font_large.render(survivor_data['name'], True, name_color)
            name_rect = name_surface.get_rect(centerx=card_x + card_width//2, y=card_y + 10)
            self.screen.blit(name_surface, name_rect)
            
            # Draw actions remaining if survivor entity exists
            if survivor_entity:
                actions_text = f"Actions: {survivor_entity.actions_remaining}/3"
                actions_color = CYAN if is_active else BLACK
                actions_surface = self.font_medium.render(actions_text, True, actions_color)
                self.screen.blit(actions_surface, (card_x + 10, card_y + 35))
            
            # Draw level color indicator
            level_color = level_colors.get(survivor_data['level'], GRAY)
            level_rect = pygame.Rect(card_x + 20, card_y + 60, card_width - 40, 25)
            pygame.draw.rect(self.screen, level_color, level_rect)
            pygame.draw.rect(self.screen, BLACK, level_rect, 1)
            
            level_surface = self.font_medium.render(survivor_data['level'].upper(), True, WHITE)
            level_text_rect = level_surface.get_rect(center=level_rect.center)
            self.screen.blit(level_surface, level_text_rect)
            
            # Draw wounds and experience
            wounds_surface = self.font_medium.render(f"Wounds: {survivor_data['wounds']}", True, BLACK)
            self.screen.blit(wounds_surface, (card_x + 10, card_y + 95))
            
            exp_surface = self.font_medium.render(f"XP: {survivor_data['exp']}", True, BLACK)
            self.screen.blit(exp_surface, (card_x + 10, card_y + 115))
    
    def draw_action_menu(self):
        """Draw the action selection menu when waiting for user input."""
        if not self.turn_manager.is_waiting_for_action():
            return
            
        # Get available actions
        available_actions = self.turn_manager.get_available_actions()
        if not available_actions:
            return
        
        # Menu properties
        menu_width = 300
        menu_height = 200
        menu_x = (self.width - menu_width) // 2
        menu_y = (self.height - menu_height) // 2
        
        # Draw menu background
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, (50, 50, 50), menu_rect)
        pygame.draw.rect(self.screen, self.WHITE, menu_rect, 3)
        
        # Draw title
        current_survivor = self.turn_manager.get_current_survivor()
        if current_survivor:
            title_text = f"{current_survivor.name}'s Turn"
            title_surface = self.font_large.render(title_text, True, self.WHITE)
            title_rect = title_surface.get_rect(centerx=menu_x + menu_width//2, y=menu_y + 10)
            self.screen.blit(title_surface, title_rect)
        
        # Draw available actions
        actions_start_y = menu_y + 50
        line_height = 25
        
        for i, action in enumerate(available_actions):
            action_text = f"{i+1}. {action}"
            action_surface = self.font_medium.render(action_text, True, self.WHITE)
            self.screen.blit(action_surface, (menu_x + 20, actions_start_y + i * line_height))
        
        # Draw instructions
        instruction_text = "Press 1, 2, or 3 to select action"
        instruction_surface = self.font_small.render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(centerx=menu_x + menu_width//2, 
                                                       y=menu_y + menu_height - 30)
        self.screen.blit(instruction_surface, instruction_rect)
    
    def draw(self):
        """Render the complete game screen."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Draw game components
        self.draw_map()
        self.draw_survivor_tokens()
        self.draw_zombie_tokens()
        self.draw_survivor_cards()
        self.draw_turn_info()
        self.draw_action_menu()
        
        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        print("Starting game window...")
        last_time = pygame.time.get_ticks()
        
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            dt = current_time - last_time
            last_time = current_time
            
            self.handle_events()
            self.update(dt)
            self.draw()
            self.clock.tick(60)  # 60 FPS

    def cleanup(self):
        """Clean up pygame resources."""
        pygame.quit()
        sys.exit()