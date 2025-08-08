"""
GameRenderer handles all rendering operations for the Zombicide game.
This class is responsible for drawing the map, entities, UI elements, and menus.
"""
import pygame
from typing import List, Optional, Dict, Any
from config.display_config import DisplayConfig
from core.entities import Survivor, Zombie


class GameRenderer:
    """Pure rendering operations - no game logic or state management."""
    
    def __init__(self, screen: pygame.Surface, config: DisplayConfig):
        """Initialize the renderer with screen and configuration."""
        self.screen = screen
        self.config = config
        
        # Initialize fonts
        config.initialize_fonts()
    
    def draw_door(self, x: int, y: int, direction: str, opened: bool = False):
        """Draw a door on the wall."""
        door_size = 40
        door_color = self.config.BLUE
        
        if direction == "up":
            door_x = x + (self.config.ZONE_PIXEL_SIZE - door_size) // 2
            door_y = y
            if opened:
                # Draw opened door as angled line
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x + door_size//2, door_y - 20), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x, door_y - 3, door_size, 6))
        elif direction == "down":
            door_x = x + (self.config.ZONE_PIXEL_SIZE - door_size) // 2
            door_y = y + self.config.ZONE_PIXEL_SIZE
            if opened:
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x + door_size//2, door_y + 20), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x, door_y - 3, door_size, 6))
        elif direction == "left":
            door_x = x
            door_y = y + (self.config.ZONE_PIXEL_SIZE - door_size) // 2
            if opened:
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x - 20, door_y + door_size//2), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x - 3, door_y, 6, door_size))
        elif direction == "right":
            door_x = x + self.config.ZONE_PIXEL_SIZE
            door_y = y + (self.config.ZONE_PIXEL_SIZE - door_size) // 2
            if opened:
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x + 20, door_y + door_size//2), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x - 3, door_y, 6, door_size))

    def draw_wall(self, x: int, y: int, direction: str):
        """Draw a wall in the specified direction."""
        wall_color = self.config.BLACK
        
        if direction == "up":
            pygame.draw.line(self.screen, wall_color,
                           (x, y), (x + self.config.ZONE_PIXEL_SIZE, y), self.config.WALL_WIDTH)
        elif direction == "down":
            pygame.draw.line(self.screen, wall_color,
                           (x, y + self.config.ZONE_PIXEL_SIZE), (x + self.config.ZONE_PIXEL_SIZE, y + self.config.ZONE_PIXEL_SIZE), self.config.WALL_WIDTH)
        elif direction == "left":
            pygame.draw.line(self.screen, wall_color,
                           (x, y), (x, y + self.config.ZONE_PIXEL_SIZE), self.config.WALL_WIDTH)
        elif direction == "right":
            pygame.draw.line(self.screen, wall_color,
                           (x + self.config.ZONE_PIXEL_SIZE, y), (x + self.config.ZONE_PIXEL_SIZE, y + self.config.ZONE_PIXEL_SIZE), self.config.WALL_WIDTH)

    def draw_map(self, map_data: Dict[str, Any]):
        """Draw the map using the provided map data."""
        if not map_data:
            return
            
        tile = map_data["tiles"][0][0]  # Only one tile for this map
        zones = tile["zones"]

        # Draw zones
        for zr in range(self.config.TILE_SIZE):
            for zc in range(self.config.TILE_SIZE):
                zone = zones[zr][zc]
                
                # Calculate zone position
                x = self.config.MAP_START_X + zc * self.config.ZONE_PIXEL_SIZE
                y = self.config.MAP_START_Y + zr * self.config.ZONE_PIXEL_SIZE

                # Set color based on zone type
                color = self.config.BUILDING_COLOR if "building" in zone["features"] else self.config.STREET_COLOR

                # Draw zone background
                pygame.draw.rect(self.screen, color, 
                               (x, y, self.config.ZONE_PIXEL_SIZE, self.config.ZONE_PIXEL_SIZE))
                
                # Draw zone border
                pygame.draw.rect(self.screen, self.config.BLACK,
                               (x, y, self.config.ZONE_PIXEL_SIZE, self.config.ZONE_PIXEL_SIZE), 2)
                
                # Draw connections (walls and doors)
                conns = zone.get("connections", {})
                for direction, conn in conns.items():
                    if conn["type"] == "wall":
                        self.draw_wall(x, y, direction)
                        if "door" in conn:
                            opened = conn.get("opened", False)
                            self.draw_door(x, y, direction, opened)
    
    def draw_survivor_tokens(self, survivors: List[Survivor], current_survivor: Optional[Survivor] = None):
        """Draw survivor tokens at their current positions - white circles with black borders and names."""
        if not survivors:
            return
        
        # Group survivors by position
        survivors_by_position = {}
        for survivor in survivors:
            if survivor.alive:
                pos_key = (survivor.position.row, survivor.position.col)
                if pos_key not in survivors_by_position:
                    survivors_by_position[pos_key] = []
                survivors_by_position[pos_key].append(survivor)
        
        # Draw survivors at each position
        for (row, col), survivor_group in survivors_by_position.items():
            zone_x = self.config.MAP_START_X + col * self.config.ZONE_PIXEL_SIZE
            zone_y = self.config.MAP_START_Y + row * self.config.ZONE_PIXEL_SIZE
            
            # Position tokens within the zone
            tokens_per_row = min(3, len(survivor_group))
            spacing = 10
            start_x = zone_x + spacing
            start_y = zone_y + spacing
            
            for i, survivor in enumerate(survivor_group):
                # Calculate position for each token
                token_row = i // tokens_per_row
                token_col = i % tokens_per_row
                
                token_x = start_x + token_col * (self.config.TOKEN_DIAMETER + spacing) + self.config.token_radius
                token_y = start_y + token_row * (self.config.TOKEN_DIAMETER + spacing) + self.config.token_radius
                
                # Make sure token stays within zone bounds
                if token_x + self.config.token_radius > zone_x + self.config.ZONE_PIXEL_SIZE or \
                   token_y + self.config.token_radius > zone_y + self.config.ZONE_PIXEL_SIZE:
                    continue
                
                # Color based on survivor status - cyan if active, white otherwise
                if current_survivor and survivor.id == current_survivor.id:
                    color = self.config.CYAN  # Active survivor gets cyan color
                else:
                    color = self.config.WHITE if survivor.alive else self.config.GRAY
                
                # Draw circle with black border
                pygame.draw.circle(self.screen, color, (token_x, token_y), self.config.token_radius)
                pygame.draw.circle(self.screen, self.config.BLACK, (token_x, token_y), self.config.token_radius, self.config.TOKEN_BORDER_WIDTH)
                
                # Draw survivor name in the middle
                name_surface = self.config.font_small.render(survivor.name, True, self.config.BLACK)
                name_rect = name_surface.get_rect(center=(token_x, token_y))
                self.screen.blit(name_surface, name_rect)
    
    def draw_zombie_tokens(self, zombies: List[Zombie]):
        """Draw zombie tokens at their current positions - dark grey circles with 'Z' in the middle."""
        if not zombies:
            return
        
        # Group zombies by position
        zombies_by_position = {}
        for zombie in zombies:
            if zombie.alive:
                pos_key = (zombie.position.row, zombie.position.col)
                if pos_key not in zombies_by_position:
                    zombies_by_position[pos_key] = []
                zombies_by_position[pos_key].append(zombie)
        
        # Draw zombies at each position
        for (row, col), zombie_group in zombies_by_position.items():
            zone_x = self.config.MAP_START_X + col * self.config.ZONE_PIXEL_SIZE
            zone_y = self.config.MAP_START_Y + row * self.config.ZONE_PIXEL_SIZE
            
            # Position tokens within the zone
            tokens_per_row = min(3, len(zombie_group))
            spacing = 20
            start_x = zone_x + spacing
            start_y = zone_y + spacing
            
            for i, zombie in enumerate(zombie_group):
                # Calculate position for each token
                token_row = i // tokens_per_row
                token_col = i % tokens_per_row
                
                token_x = start_x + token_col * (self.config.TOKEN_DIAMETER + spacing) + self.config.token_radius
                token_y = start_y + token_row * (self.config.TOKEN_DIAMETER + spacing) + self.config.token_radius
                
                # Make sure token stays within zone bounds
                if token_x + self.config.token_radius > zone_x + self.config.ZONE_PIXEL_SIZE or \
                   token_y + self.config.token_radius > zone_y + self.config.ZONE_PIXEL_SIZE:
                    continue
                
                # Draw dark grey circle with black border
                pygame.draw.circle(self.screen, self.config.DARK_GRAY, (token_x, token_y), self.config.token_radius)
                pygame.draw.circle(self.screen, self.config.BLACK, (token_x, token_y), self.config.token_radius, self.config.TOKEN_BORDER_WIDTH)
                
                # Draw 'Z' in the middle
                z_surface = self.config.font_medium.render('Z', True, self.config.WHITE)
                z_rect = z_surface.get_rect(center=(token_x, token_y))
                self.screen.blit(z_surface, z_rect)
    
    def draw_turn_info(self, turn_info: Dict[str, Any]):
        """Draw turn information on the screen."""
        # Position in top-left corner
        info_x = 10
        info_y = 10
        line_height = 25
        
        # Background rectangle for better readability
        info_rect = pygame.Rect(info_x - 5, info_y - 5, 300, 120)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), info_rect)
        pygame.draw.rect(self.screen, self.config.WHITE, info_rect, 2)
        
        # Turn number
        turn_text = f"Turn: {turn_info['turn_number']}"
        turn_surface = self.config.font_large.render(turn_text, True, self.config.WHITE)
        self.screen.blit(turn_surface, (info_x, info_y))
        
        # Current phase
        phase_text = f"Phase: {turn_info['phase_name']}"
        phase_surface = self.config.font_medium.render(phase_text, True, self.config.WHITE)
        self.screen.blit(phase_surface, (info_x, info_y + line_height))
        
        # Phase status
        status = "Complete" if turn_info['phase_complete'] else "In Progress"
        status_color = self.config.WHITE if turn_info['phase_complete'] else self.config.YELLOW  # Yellow for in progress
        status_text = f"Status: {status}"
        status_surface = self.config.font_small.render(status_text, True, status_color)
        self.screen.blit(status_surface, (info_x, info_y + line_height * 2))
        
        # Controls info
        controls_text = "SPACE: Next Phase | P: Pause | ESC: Quit"
        controls_surface = self.config.font_small.render(controls_text, True, (200, 200, 200))
        self.screen.blit(controls_surface, (info_x, info_y + line_height * 3))

    def draw_survivor_cards(self, survivors_data: List[Dict[str, Any]], survivors: List[Survivor], current_survivor: Optional[Survivor] = None):
        """Draw survivor cards with highlighting and actions display."""
        if not survivors_data:
            return
        
        for i, survivor_data in enumerate(survivors_data):
            # Find corresponding survivor entity for actions
            survivor_entity = None
            for survivor in survivors:
                if survivor.name == survivor_data['name']:
                    survivor_entity = survivor
                    break
            
            card_x = self.config.CARD_START_X
            card_y = 50 + (i * (self.config.CARD_HEIGHT + self.config.CARD_SPACING))
            
            # Determine if this survivor is active
            is_active = (current_survivor and survivor_entity and 
                        current_survivor.id == survivor_entity.id)
            
            # Draw card background with highlighting
            border_color = self.config.CYAN if is_active else self.config.WHITE
            border_width = 5 if is_active else 3
            
            pygame.draw.rect(self.screen, border_color, (card_x, card_y, self.config.CARD_WIDTH, self.config.CARD_HEIGHT), border_width)
            pygame.draw.rect(self.screen, (200, 200, 200), (card_x+border_width, card_y+border_width, 
                           self.config.CARD_WIDTH-2*border_width, self.config.CARD_HEIGHT-2*border_width))
            
            # Draw survivor name with highlighting
            name_color = self.config.CYAN if is_active else self.config.BLACK
            name_surface = self.config.font_large.render(survivor_data['name'], True, name_color)
            name_rect = name_surface.get_rect(centerx=card_x + self.config.CARD_WIDTH//2, y=card_y + 10)
            self.screen.blit(name_surface, name_rect)
            
            # Draw actions remaining if survivor entity exists
            if survivor_entity:
                actions_text = f"Actions: {survivor_entity.actions_remaining}/3"
                actions_color = self.config.CYAN if is_active else self.config.BLACK
                actions_surface = self.config.font_medium.render(actions_text, True, actions_color)
                self.screen.blit(actions_surface, (card_x + 10, card_y + 35))
            
            # Draw level color indicator
            level_color = self.config.level_colors.get(survivor_data['level'], self.config.GRAY)
            level_rect = pygame.Rect(card_x + 20, card_y + 60, self.config.CARD_WIDTH - 40, 25)
            pygame.draw.rect(self.screen, level_color, level_rect)
            pygame.draw.rect(self.screen, self.config.BLACK, level_rect, 1)
            
            level_surface = self.config.font_medium.render(survivor_data['level'].upper(), True, self.config.WHITE)
            level_text_rect = level_surface.get_rect(center=level_rect.center)
            self.screen.blit(level_surface, level_text_rect)
            
            # Draw wounds and experience
            wounds_surface = self.config.font_medium.render(f"Wounds: {survivor_data['wounds']}", True, self.config.BLACK)
            self.screen.blit(wounds_surface, (card_x + 10, card_y + 95))
            
            exp_surface = self.config.font_medium.render(f"XP: {survivor_data['exp']}", True, self.config.BLACK)
            self.screen.blit(exp_surface, (card_x + 10, card_y + 115))
    
    def draw_action_menu(self, current_survivor: Optional[Survivor], available_actions: List[str]):
        """Draw the action selection menu when waiting for user input."""
        if not current_survivor or not available_actions:
            return
        
        # Menu position
        menu_x = (self.config.WINDOW_WIDTH - self.config.MENU_WIDTH) // 2
        menu_y = (self.config.WINDOW_HEIGHT - self.config.MENU_HEIGHT) // 2
        
        # Draw menu background
        menu_rect = pygame.Rect(menu_x, menu_y, self.config.MENU_WIDTH, self.config.MENU_HEIGHT)
        pygame.draw.rect(self.screen, (50, 50, 50), menu_rect)
        pygame.draw.rect(self.screen, self.config.WHITE, menu_rect, 3)
        
        # Draw title
        title_text = f"{current_survivor.name}'s Turn"
        title_surface = self.config.font_large.render(title_text, True, self.config.WHITE)
        title_rect = title_surface.get_rect(centerx=menu_x + self.config.MENU_WIDTH//2, y=menu_y + 10)
        self.screen.blit(title_surface, title_rect)
        
        # Draw available actions
        actions_start_y = menu_y + 50
        line_height = 25
        
        for i, action in enumerate(available_actions):
            action_text = f"{i+1}. {action}"
            action_surface = self.config.font_medium.render(action_text, True, self.config.WHITE)
            self.screen.blit(action_surface, (menu_x + 20, actions_start_y + i * line_height))
        
        # Draw instructions
        instruction_text = "Press 1, 2, or 3 to select action"
        instruction_surface = self.config.font_small.render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(centerx=menu_x + self.config.MENU_WIDTH//2, 
                                                       y=menu_y + self.config.MENU_HEIGHT - 30)
        self.screen.blit(instruction_surface, instruction_rect)
    
    def render_frame(self, map_data: Dict[str, Any], survivors: List[Survivor], zombies: List[Zombie], 
                     survivors_data: List[Dict[str, Any]], turn_info: Dict[str, Any], 
                     current_survivor: Optional[Survivor] = None, available_actions: Optional[List[str]] = None):
        """Render a complete frame with all game elements."""
        # Clear screen
        self.screen.fill(self.config.BLACK)
        
        # Draw game components
        self.draw_map(map_data)
        self.draw_survivor_tokens(survivors, current_survivor)
        self.draw_zombie_tokens(zombies)
        self.draw_survivor_cards(survivors_data, survivors, current_survivor)
        self.draw_turn_info(turn_info)
        
        # Draw action menu if waiting for input
        if current_survivor and available_actions:
            self.draw_action_menu(current_survivor, available_actions)
        
        # Update display
        pygame.display.flip()