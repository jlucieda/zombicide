"""
RenderingSystem for the Zombicide game.
Domain-focused rendering architecture with specialized renderers.
"""
import pygame
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

from core.entities import Survivor, Zombie
from .configuration_manager import ConfigurationManager


class BaseRenderer(ABC):
    """Base class for all specialized renderers."""
    
    def __init__(self, screen: pygame.Surface, config_manager: ConfigurationManager):
        self.screen = screen
        self.config = config_manager


class MapRenderer(BaseRenderer):
    """Handles all map-related rendering."""
    
    def draw_door(self, x: int, y: int, direction: str, opened: bool = False):
        """Draw a door on the wall."""
        door_size = 40
        door_color = self.config.get_color('blue')
        
        if direction == "up":
            door_x = x + (self.config.display.zone_pixel_size - door_size) // 2
            door_y = y
            if opened:
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x + door_size//2, door_y - 20), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x, door_y - 3, door_size, 6))
        elif direction == "down":
            door_x = x + (self.config.display.zone_pixel_size - door_size) // 2
            door_y = y + self.config.display.zone_pixel_size
            if opened:
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x + door_size//2, door_y + 20), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x, door_y - 3, door_size, 6))
        elif direction == "left":
            door_x = x
            door_y = y + (self.config.display.zone_pixel_size - door_size) // 2
            if opened:
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x - 20, door_y + door_size//2), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x - 3, door_y, 6, door_size))
        elif direction == "right":
            door_x = x + self.config.display.zone_pixel_size
            door_y = y + (self.config.display.zone_pixel_size - door_size) // 2
            if opened:
                pygame.draw.line(self.screen, door_color,
                               (door_x, door_y), (door_x + 20, door_y + door_size//2), 3)
            else:
                pygame.draw.rect(self.screen, door_color,
                               (door_x - 3, door_y, 6, door_size))

    def draw_wall(self, x: int, y: int, direction: str):
        """Draw a wall in the specified direction."""
        wall_color = self.config.get_color('black')
        wall_width = self.config.display.wall_width
        zone_size = self.config.display.zone_pixel_size
        
        if direction == "up":
            pygame.draw.line(self.screen, wall_color,
                           (x, y), (x + zone_size, y), wall_width)
        elif direction == "down":
            pygame.draw.line(self.screen, wall_color,
                           (x, y + zone_size), (x + zone_size, y + zone_size), wall_width)
        elif direction == "left":
            pygame.draw.line(self.screen, wall_color,
                           (x, y), (x, y + zone_size), wall_width)
        elif direction == "right":
            pygame.draw.line(self.screen, wall_color,
                           (x + zone_size, y), (x + zone_size, y + zone_size), wall_width)

    def render(self, map_data: Dict[str, Any]):
        """Render the game map."""
        if not map_data:
            return
            
        tile = map_data["tiles"][0][0]
        zones = tile["zones"]

        for zr in range(self.config.display.tile_size):
            for zc in range(self.config.display.tile_size):
                zone = zones[zr][zc]
                
                x = self.config.display.map_start_x + zc * self.config.display.zone_pixel_size
                y = self.config.display.map_start_y + zr * self.config.display.zone_pixel_size

                color = (self.config.get_color('building_color') if "building" in zone["features"] 
                        else self.config.get_color('street_color'))

                pygame.draw.rect(self.screen, color, 
                               (x, y, self.config.display.zone_pixel_size, self.config.display.zone_pixel_size))
                
                pygame.draw.rect(self.screen, self.config.get_color('black'),
                               (x, y, self.config.display.zone_pixel_size, self.config.display.zone_pixel_size), 2)
                
                conns = zone.get("connections", {})
                for direction, conn in conns.items():
                    if conn["type"] == "wall":
                        self.draw_wall(x, y, direction)
                        if "door" in conn:
                            opened = conn.get("opened", False)
                            self.draw_door(x, y, direction, opened)


class EntityRenderer(BaseRenderer):
    """Handles rendering of game entities (survivors, zombies)."""
    
    def render_survivors(self, survivors: List[Survivor], current_survivor: Optional[Survivor] = None):
        """Render survivor tokens."""
        if not survivors:
            return
        
        survivors_by_position = {}
        for survivor in survivors:
            if survivor.alive:
                pos_key = (survivor.position.row, survivor.position.col)
                if pos_key not in survivors_by_position:
                    survivors_by_position[pos_key] = []
                survivors_by_position[pos_key].append(survivor)
        
        for (row, col), survivor_group in survivors_by_position.items():
            zone_x = self.config.display.map_start_x + col * self.config.display.zone_pixel_size
            zone_y = self.config.display.map_start_y + row * self.config.display.zone_pixel_size
            
            tokens_per_row = min(3, len(survivor_group))
            spacing = 10
            start_x = zone_x + spacing
            start_y = zone_y + spacing
            
            for i, survivor in enumerate(survivor_group):
                token_row = i // tokens_per_row
                token_col = i % tokens_per_row
                
                token_x = start_x + token_col * (self.config.display.token_diameter + spacing) + self.config.display.token_radius
                token_y = start_y + token_row * (self.config.display.token_diameter + spacing) + self.config.display.token_radius
                
                if (token_x + self.config.display.token_radius > zone_x + self.config.display.zone_pixel_size or 
                    token_y + self.config.display.token_radius > zone_y + self.config.display.zone_pixel_size):
                    continue
                
                color = (self.config.get_color('cyan') if current_survivor and survivor.id == current_survivor.id 
                        else self.config.get_color('white') if survivor.alive else self.config.get_color('gray'))
                
                pygame.draw.circle(self.screen, color, (token_x, token_y), self.config.display.token_radius)
                pygame.draw.circle(self.screen, self.config.get_color('black'), (token_x, token_y), 
                                 self.config.display.token_radius, self.config.display.token_border_width)
                
                name_surface = self.config.get_font('small').render(survivor.name, True, self.config.get_color('black'))
                name_rect = name_surface.get_rect(center=(token_x, token_y))
                self.screen.blit(name_surface, name_rect)
    
    def render_zombies(self, zombies: List[Zombie]):
        """Render zombie tokens."""
        if not zombies:
            return
        
        zombies_by_position = {}
        for zombie in zombies:
            if zombie.alive:
                pos_key = (zombie.position.row, zombie.position.col)
                if pos_key not in zombies_by_position:
                    zombies_by_position[pos_key] = []
                zombies_by_position[pos_key].append(zombie)
        
        for (row, col), zombie_group in zombies_by_position.items():
            zone_x = self.config.display.map_start_x + col * self.config.display.zone_pixel_size
            zone_y = self.config.display.map_start_y + row * self.config.display.zone_pixel_size
            
            tokens_per_row = min(3, len(zombie_group))
            spacing = 20
            start_x = zone_x + spacing
            start_y = zone_y + spacing
            
            for i, zombie in enumerate(zombie_group):
                token_row = i // tokens_per_row
                token_col = i % tokens_per_row
                
                token_x = start_x + token_col * (self.config.display.token_diameter + spacing) + self.config.display.token_radius
                token_y = start_y + token_row * (self.config.display.token_diameter + spacing) + self.config.display.token_radius
                
                if (token_x + self.config.display.token_radius > zone_x + self.config.display.zone_pixel_size or 
                    token_y + self.config.display.token_radius > zone_y + self.config.display.zone_pixel_size):
                    continue
                
                pygame.draw.circle(self.screen, self.config.get_color('dark_gray'), (token_x, token_y), self.config.display.token_radius)
                pygame.draw.circle(self.screen, self.config.get_color('black'), (token_x, token_y), 
                                 self.config.display.token_radius, self.config.display.token_border_width)
                
                z_surface = self.config.get_font('medium').render('Z', True, self.config.get_color('white'))
                z_rect = z_surface.get_rect(center=(token_x, token_y))
                self.screen.blit(z_surface, z_rect)


class UIRenderer(BaseRenderer):
    """Handles UI elements rendering (menus, HUD, cards)."""
    
    def render_turn_info(self, turn_info: Dict[str, Any]):
        """Render turn information HUD."""
        info_x = 10
        info_y = 10
        line_height = 25
        
        info_rect = pygame.Rect(info_x - 5, info_y - 5, 300, 120)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), info_rect)
        pygame.draw.rect(self.screen, self.config.get_color('white'), info_rect, 2)
        
        turn_text = f"Turn: {turn_info['turn_number']}"
        turn_surface = self.config.get_font('large').render(turn_text, True, self.config.get_color('white'))
        self.screen.blit(turn_surface, (info_x, info_y))
        
        phase_text = f"Phase: {turn_info['phase_name']}"
        phase_surface = self.config.get_font('medium').render(phase_text, True, self.config.get_color('white'))
        self.screen.blit(phase_surface, (info_x, info_y + line_height))
        
        status = "Complete" if turn_info['phase_complete'] else "In Progress"
        status_color = self.config.get_color('white') if turn_info['phase_complete'] else self.config.get_color('yellow')
        status_text = f"Status: {status}"
        status_surface = self.config.get_font('small').render(status_text, True, status_color)
        self.screen.blit(status_surface, (info_x, info_y + line_height * 2))
        
        controls_text = "SPACE: Next Phase | P: Pause | ESC: Quit"
        controls_surface = self.config.get_font('small').render(controls_text, True, (200, 200, 200))
        self.screen.blit(controls_surface, (info_x, info_y + line_height * 3))

    def render_survivor_cards(self, survivors_data: List[Dict[str, Any]], survivors: List[Survivor], 
                             current_survivor: Optional[Survivor] = None):
        """Render survivor information cards."""
        if not survivors_data:
            return
        
        for i, survivor_data in enumerate(survivors_data):
            survivor_entity = None
            for survivor in survivors:
                if survivor.name == survivor_data['name']:
                    survivor_entity = survivor
                    break
            
            card_x = self.config.display.card_start_x
            card_y = 50 + (i * (self.config.display.card_height + self.config.display.card_spacing))
            
            is_active = (current_survivor and survivor_entity and 
                        current_survivor.id == survivor_entity.id)
            
            border_color = self.config.get_color('cyan') if is_active else self.config.get_color('white')
            border_width = 5 if is_active else 3
            
            pygame.draw.rect(self.screen, border_color, 
                           (card_x, card_y, self.config.display.card_width, self.config.display.card_height), border_width)
            pygame.draw.rect(self.screen, (200, 200, 200), 
                           (card_x+border_width, card_y+border_width, 
                            self.config.display.card_width-2*border_width, self.config.display.card_height-2*border_width))
            
            name_color = self.config.get_color('cyan') if is_active else self.config.get_color('black')
            name_surface = self.config.get_font('large').render(survivor_data['name'], True, name_color)
            name_rect = name_surface.get_rect(centerx=card_x + self.config.display.card_width//2, y=card_y + 10)
            self.screen.blit(name_surface, name_rect)
            
            if survivor_entity:
                actions_text = f"Actions: {survivor_entity.actions_remaining}/3"
                actions_color = self.config.get_color('cyan') if is_active else self.config.get_color('black')
                actions_surface = self.config.get_font('medium').render(actions_text, True, actions_color)
                self.screen.blit(actions_surface, (card_x + 10, card_y + 35))
            
            level_color = self.config.display.level_colors.get(survivor_data['level'], self.config.get_color('gray'))
            level_rect = pygame.Rect(card_x + 20, card_y + 60, self.config.display.card_width - 40, 25)
            pygame.draw.rect(self.screen, level_color, level_rect)
            pygame.draw.rect(self.screen, self.config.get_color('black'), level_rect, 1)
            
            level_surface = self.config.get_font('medium').render(survivor_data['level'].upper(), True, self.config.get_color('white'))
            level_text_rect = level_surface.get_rect(center=level_rect.center)
            self.screen.blit(level_surface, level_text_rect)
            
            wounds_surface = self.config.get_font('medium').render(f"Wounds: {survivor_data['wounds']}", True, self.config.get_color('black'))
            self.screen.blit(wounds_surface, (card_x + 10, card_y + 95))
            
            exp_surface = self.config.get_font('medium').render(f"XP: {survivor_data['exp']}", True, self.config.get_color('black'))
            self.screen.blit(exp_surface, (card_x + 10, card_y + 115))

    def render_action_menu(self, current_survivor: Optional[Survivor], available_actions: List[str]):
        """Render action selection menu."""
        if not current_survivor or not available_actions:
            return
        
        menu_x = (self.config.display.window_width - self.config.display.menu_width) // 2
        menu_y = (self.config.display.window_height - self.config.display.menu_height) // 2
        
        menu_rect = pygame.Rect(menu_x, menu_y, self.config.display.menu_width, self.config.display.menu_height)
        pygame.draw.rect(self.screen, (50, 50, 50), menu_rect)
        pygame.draw.rect(self.screen, self.config.get_color('white'), menu_rect, 3)
        
        title_text = f"{current_survivor.name}'s Turn"
        title_surface = self.config.get_font('large').render(title_text, True, self.config.get_color('white'))
        title_rect = title_surface.get_rect(centerx=menu_x + self.config.display.menu_width//2, y=menu_y + 10)
        self.screen.blit(title_surface, title_rect)
        
        actions_start_y = menu_y + 50
        line_height = 25
        
        for i, action in enumerate(available_actions):
            action_text = f"{i+1}. {action}"
            action_surface = self.config.get_font('medium').render(action_text, True, self.config.get_color('white'))
            self.screen.blit(action_surface, (menu_x + 20, actions_start_y + i * line_height))
        
        instruction_text = "Press 1, 2, or 3 to select action"
        instruction_surface = self.config.get_font('small').render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(centerx=menu_x + self.config.display.menu_width//2, 
                                                       y=menu_y + self.config.display.menu_height - 30)
        self.screen.blit(instruction_surface, instruction_rect)


class RenderingSystem:
    """Main rendering coordinator that orchestrates all rendering operations."""
    
    def __init__(self, screen: pygame.Surface, config_manager: ConfigurationManager):
        """Initialize the rendering system with specialized renderers."""
        self.screen = screen
        self.config = config_manager
        
        self.map_renderer = MapRenderer(screen, config_manager)
        self.entity_renderer = EntityRenderer(screen, config_manager)
        self.ui_renderer = UIRenderer(screen, config_manager)
    
    def render(self, game_world: Dict[str, Any], ui_state: Dict[str, Any]):
        """Render complete frame using all specialized renderers."""
        # Clear screen
        self.screen.fill(self.config.get_color('black'))
        
        # Render game world
        if 'map_data' in game_world:
            self.map_renderer.render(game_world['map_data'])
        
        if 'survivors' in game_world:
            self.entity_renderer.render_survivors(
                game_world['survivors'], 
                ui_state.get('current_survivor')
            )
        
        if 'zombies' in game_world:
            self.entity_renderer.render_zombies(game_world['zombies'])
        
        # Render UI elements
        if 'turn_info' in ui_state:
            self.ui_renderer.render_turn_info(ui_state['turn_info'])
        
        if 'survivors_data' in game_world and 'survivors' in game_world:
            self.ui_renderer.render_survivor_cards(
                game_world['survivors_data'],
                game_world['survivors'],
                ui_state.get('current_survivor')
            )
        
        if ui_state.get('show_action_menu') and ui_state.get('available_actions'):
            self.ui_renderer.render_action_menu(
                ui_state.get('current_survivor'),
                ui_state['available_actions']
            )
        
        # Update display
        pygame.display.flip()