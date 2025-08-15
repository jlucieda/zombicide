"""
RenderingSystem for the Zombicide game.
Domain-focused rendering architecture with specialized renderers.
"""
import pygame
from typing import List, Optional, Dict, Any
from abc import ABC

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
    
    def render_turn_info(self, turn_info: Dict[str, Any], current_survivor=None, available_actions=None, survivors=None, combat_info=None):
        """Render revamped turn control window in upper right corner."""
        # Calculate dynamic height based on content (survivors + phases + controls)
        info_width = 220  # Narrower to avoid overlapping survivor cards
        base_height = 200  # Smaller height to be more compact
        info_x = self.config.display.window_width - info_width - 15  # More margin from right edge
        info_y = 10
        line_height = 16  # Smaller line height for compactness
        
        # Background
        info_rect = pygame.Rect(info_x - 5, info_y - 5, info_width, base_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), info_rect)
        pygame.draw.rect(self.screen, self.config.get_color('white'), info_rect, 2)
        
        current_y = info_y + 5
        
        # 1. Turn number at the top (smaller font for compact window)
        turn_text = f"Turn {turn_info['turn_number']}"
        turn_surface = self.config.get_font('large').render(turn_text, True, self.config.get_color('white'))
        turn_rect = turn_surface.get_rect(centerx=info_x + info_width//2, y=current_y)
        self.screen.blit(turn_surface, turn_rect)
        current_y += 28
        
        # 2. Phase list structure
        current_phase = turn_info.get('phase_name', '')
        
        # Helper function to draw arrow and text
        def draw_phase_item(text, is_current, y_pos, indent=0):
            arrow_x = info_x + 10 + indent
            text_x = arrow_x + 20
            
            # Draw yellow arrow if current phase
            if is_current:
                # Yellow arrow pointing right (triangle)
                arrow_points = [
                    (arrow_x, y_pos + 4),
                    (arrow_x + 12, y_pos + 9),
                    (arrow_x, y_pos + 14)
                ]
                pygame.draw.polygon(self.screen, self.config.get_color('yellow'), arrow_points)
            
            # Draw text (smaller font for compact window)
            color = self.config.get_color('white') if is_current else (180, 180, 180)
            text_surface = self.config.get_font('medium').render(text, True, color)
            self.screen.blit(text_surface, (text_x, y_pos))
            
            return y_pos + line_height + 1
        
        # a) Survivor Turn
        is_survivor_turn = 'Survivor' in current_phase
        current_y = draw_phase_item('Survivor Turn', is_survivor_turn, current_y)
        
        # List all survivors under Survivor Turn with action counts
        if survivors:
            # Check if we have turn order information
            turn_order_info = turn_info.get('turn_order_info')
            if turn_order_info and 'turn_order' in turn_order_info:
                # Display survivors in turn order with position indicators
                turn_order_names = turn_order_info['turn_order']
                for i, survivor_name in enumerate(turn_order_names):
                    # Find the survivor entity
                    survivor = next((s for s in survivors if s.name == survivor_name and s.alive), None)
                    if survivor:
                        # Format: "1. Eva (3/3)" showing position, name, and actions
                        position_marker = f"{i+1}. " if turn_order_info.get('first_player') == survivor_name else f"{i+1}. "
                        if turn_order_info.get('first_player') == survivor_name:
                            position_marker = f"👑{i+1}. "  # Crown for first player
                        
                        survivor_text = f"{position_marker}{survivor.name} ({survivor.actions_remaining}/3)"
                        is_current_survivor = (current_survivor and 
                                             current_survivor.name == survivor.name and 
                                             is_survivor_turn)
                        current_y = draw_phase_item(survivor_text, is_current_survivor, current_y, indent=15)
            else:
                # Fallback to original display
                for survivor in survivors:
                    if survivor.alive:
                        # Format: "Eva (3/3)" showing current/max actions
                        survivor_text = f"{survivor.name} ({survivor.actions_remaining}/3)"
                        is_current_survivor = (current_survivor and 
                                             current_survivor.name == survivor.name and 
                                             is_survivor_turn)
                        current_y = draw_phase_item(survivor_text, is_current_survivor, current_y, indent=15)
        
        # b) Zombie Turn
        is_zombie_turn = 'Zombie' in current_phase and 'Spawn' not in current_phase
        current_y = draw_phase_item('Zombie Turn', is_zombie_turn, current_y)
        
        # c) Zombie Spawn
        is_zombie_spawn = 'Spawn' in current_phase
        current_y = draw_phase_item('Zombie Spawn', is_zombie_spawn, current_y)
        
        # d) End Turn
        is_end_turn = 'End' in current_phase
        current_y = draw_phase_item('End Turn', is_end_turn, current_y)
        
        # Add spacing before bottom section
        current_y += 10
        
        # Show available actions for current survivor OR phase completion message
        if current_survivor and available_actions and is_survivor_turn:
            # Separator line
            pygame.draw.line(self.screen, self.config.get_color('white'), 
                           (info_x + 5, current_y), (info_x + info_width - 15, current_y), 1)
            current_y += 15
            
            # Actions header
            actions_text = "Available Actions:"
            actions_surface = self.config.get_font('small').render(actions_text, True, self.config.get_color('cyan'))
            self.screen.blit(actions_surface, (info_x + 10, current_y))
            current_y += 18
            
            # List actions
            for i, action in enumerate(available_actions):
                action_text = f"{i+1}. {action}"
                action_surface = self.config.get_font('small').render(action_text, True, self.config.get_color('white'))
                self.screen.blit(action_surface, (info_x + 15, current_y))
                current_y += 16
        
        elif combat_info and combat_info.get('waiting_for_selection', False):
            # Show combat survivor selection UI
            # Separator line
            pygame.draw.line(self.screen, self.config.get_color('white'), 
                           (info_x + 5, current_y), (info_x + info_width - 15, current_y), 1)
            current_y += 15
            
            # Combat message
            combat_message = combat_info.get('message', 'Combat!')
            combat_surface = self.config.get_font('small').render(combat_message, True, self.config.get_color('red'))
            self.screen.blit(combat_surface, (info_x + 10, current_y))
            current_y += 18
            
            # List target survivors
            target_survivors = combat_info.get('target_survivors', [])
            for i, survivor in enumerate(target_survivors):
                survivor_text = f"{i+1}. {survivor.name} ({survivor.wounds}/2)"
                survivor_color = self.config.get_color('white')
                if survivor.wounds >= 1:
                    survivor_color = self.config.get_color('yellow')  # Wounded survivors in yellow
                survivor_surface = self.config.get_font('small').render(survivor_text, True, survivor_color)
                self.screen.blit(survivor_surface, (info_x + 15, current_y))
                current_y += 16
        
        elif turn_info.get('phase_complete', False):
            # Show phase completion message when phase is done
            # Separator line
            pygame.draw.line(self.screen, self.config.get_color('white'), 
                           (info_x + 5, current_y), (info_x + info_width - 15, current_y), 1)
            current_y += 15
            
            # Phase completion message
            completion_text = "Press Space to move"
            completion_surface = self.config.get_font('small').render(completion_text, True, self.config.get_color('yellow'))
            self.screen.blit(completion_surface, (info_x + 10, current_y))
            current_y += 16
            
            next_phase_text = "to next phase"
            next_phase_surface = self.config.get_font('small').render(next_phase_text, True, self.config.get_color('yellow'))
            self.screen.blit(next_phase_surface, (info_x + 10, current_y))
            current_y += 16
    

    def render_survivor_cards(self, survivors_data: List[Dict[str, Any]], survivors: List[Survivor], 
                             current_survivor: Optional[Survivor] = None):
        """Render enhanced survivor information cards with skills, weapons, and inventory."""
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
            
            self._render_single_survivor_card(card_x, card_y, survivor_data, survivor_entity, is_active)
    
    def _render_single_survivor_card(self, card_x: int, card_y: int, survivor_data: Dict[str, Any], 
                                   survivor_entity: Optional[Survivor], is_active: bool):
        """Render a single survivor card with all details."""
        # Check if survivor is dead
        is_dead = (survivor_entity and not survivor_entity.alive) or survivor_data.get('wounds', 0) >= 2
        
        # Card background - dark gray for dead survivors
        if is_dead:
            border_color = self.config.get_color('dark_gray')
            border_width = 3
            card_bg_color = (80, 80, 80)  # Dark gray background for dead survivors
            text_color = (160, 160, 160)  # Lighter gray text for dead survivors
        else:
            border_color = self.config.get_color('cyan') if is_active else self.config.get_color('white')
            border_width = 5 if is_active else 3
            card_bg_color = (200, 200, 200)  # Normal background
            text_color = self.config.get_color('cyan') if is_active else self.config.get_color('black')
        
        pygame.draw.rect(self.screen, border_color, 
                       (card_x, card_y, self.config.display.card_width, self.config.display.card_height), border_width)
        pygame.draw.rect(self.screen, card_bg_color, 
                       (card_x+border_width, card_y+border_width, 
                        self.config.display.card_width-2*border_width, self.config.display.card_height-2*border_width))
        
        y_offset = 10
        line_height = 18
        
        # Name, level circle, XP, and wounds all on the same line
        name_color = text_color
        name_surface = self.config.get_font('xlarge').render(survivor_data['name'], True, name_color)
        self.screen.blit(name_surface, (card_x + 10, card_y + y_offset))
        
        # Level color indicator circle after name (sized to match font height)
        name_width = name_surface.get_width()
        name_height = name_surface.get_height()
        level_color = self.config.display.level_colors.get(survivor_data['level'], self.config.get_color('gray'))
        circle_radius = name_height // 2 - 2  # Slightly smaller than half font height
        circle_x = card_x + 10 + name_width + 15
        circle_y = card_y + y_offset + name_height // 2  # Center with name text
        pygame.draw.circle(self.screen, level_color, (circle_x, circle_y), circle_radius)
        pygame.draw.circle(self.screen, self.config.get_color('black'), (circle_x, circle_y), circle_radius, 2)
        
        # XP and Wounds on same line as name (right side)
        info_text = f"XP: {survivor_data['exp']} | Wounds: {survivor_data['wounds']}/2"
        wound_color = self.config.get_color('red') if survivor_data['wounds'] >= 2 else text_color
        info_surface = self.config.get_font('medium').render(info_text, True, wound_color)
        info_x = card_x + self.config.display.card_width - info_surface.get_width() - 10
        self.screen.blit(info_surface, (info_x, card_y + y_offset + 5))  # Slight vertical offset to align with name
        
        y_offset += 25
        
        # Actions remaining (if available) - don't show for dead survivors
        if survivor_entity and not is_dead:
            actions_text = f"Actions: {survivor_entity.actions_remaining}/3"
            actions_color = self.config.get_color('red') if survivor_entity.actions_remaining == 0 else text_color
            actions_surface = self.config.get_font('medium').render(actions_text, True, actions_color)
            self.screen.blit(actions_surface, (card_x + 10, card_y + y_offset))
        elif is_dead:
            # Show "DEAD" message for dead survivors
            dead_text = "DEAD - Cannot Act"
            dead_surface = self.config.get_font('medium').render(dead_text, True, self.config.get_color('red'))
            self.screen.blit(dead_surface, (card_x + 10, card_y + y_offset))
        
        y_offset += 30
        
        # Weapons in hands section with characteristics
        equipment = survivor_data.get('equipment', {})
        right_hand = equipment.get('hand_right', 'empty').replace('_', ' ').title()
        left_hand = equipment.get('hand_left', 'empty').replace('_', ' ').title()
        
        # Display weapons label
        weapons_label = "Weapons:"
        weapons_label_surface = self.config.get_font('medium').render(weapons_label, True, text_color)
        self.screen.blit(weapons_label_surface, (card_x + 10, card_y + y_offset))
        
        # Calculate positions for centered weapon names and stats
        weapons_start_x = card_x + 10 + weapons_label_surface.get_width() + 10
        weapons_width = self.config.display.card_width - (weapons_start_x - card_x) - 20
        
        # Display weapon names and characteristics with proper alignment
        self._render_aligned_weapons(weapons_start_x, card_y + y_offset, weapons_width, left_hand, right_hand, line_height, text_color, is_dead)
        y_offset += line_height * 2 + 5  # Space for weapon names and stats
        
        # Inventory section
        inv_title = self.config.get_font('medium').render("Inventory:", True, text_color)
        self.screen.blit(inv_title, (card_x + 10, card_y + y_offset))
        y_offset += line_height + 5
        
        # Inventory slots
        inventory_items = []
        for slot in ['inv_1', 'inv_2', 'inv_3', 'inv_4']:
            item = equipment.get(slot, 'empty')
            if item != 'empty':
                inventory_items.append(item.replace('_', ' ').title())
        
        if inventory_items:
            for item in inventory_items:
                item_surface = self.config.get_font('small').render(f"• {item}", True, text_color)
                self.screen.blit(item_surface, (card_x + 15, card_y + y_offset))
                y_offset += line_height
        else:
            empty_surface = self.config.get_font('small').render("• Empty", True, text_color)
            self.screen.blit(empty_surface, (card_x + 15, card_y + y_offset))
            y_offset += line_height
        
        y_offset += 15
        
        # Skills section
        skills_title = self.config.get_font('medium').render("Skills:", True, text_color)
        self.screen.blit(skills_title, (card_x + 10, card_y + y_offset))
        y_offset += line_height + 5
        
        skills = survivor_data.get('skills', {})
        current_level = survivor_data['level']
        
        # Show skills based on level (blue -> yellow -> orange -> red)
        level_order = ['blue', 'yellow', 'orange1', 'orange2', 'red1', 'red2', 'red3']
        current_level_index = {'blue': 0, 'yellow': 1, 'orange': 3, 'red': 6}.get(current_level, 0)
        
        skills_to_show = []
        for i, level in enumerate(level_order):
            if i <= current_level_index:
                skill_key = f"skill_{level}"
                if skill_key in skills:
                    skills_to_show.append(skills[skill_key])
        
        # Display current skills
        for skill in skills_to_show:
            # Wrap long skill text
            skill_lines = self._wrap_text(skill, self.config.display.card_width - 40)
            for line in skill_lines:
                if y_offset + line_height > card_y + self.config.display.card_height - 10:
                    break  # Don't draw outside card bounds
                skill_surface = self.config.get_font('small').render(f"• {line}", True, text_color)
                self.screen.blit(skill_surface, (card_x + 15, card_y + y_offset))
                y_offset += line_height
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within specified width."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_surface = self.config.get_font('small').render(test_line, True, self.config.get_color('black'))
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)  # Single word too long, add anyway
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _render_aligned_weapons(self, start_x: int, start_y: int, total_width: int, left_weapon: str, right_weapon: str, line_height: int, text_color=None, is_dead=False):
        """Render weapon names and stats with perfect alignment."""
        from core.game_setup import GameSetup
        
        # Use default colors if not provided
        if text_color is None:
            text_color = self.config.get_color('black')
        
        # Calculate two equal columns for left and right weapons
        column_width = total_width // 2
        left_column_x = start_x
        right_column_x = start_x + column_width
        
        # Render left weapon (name and stats)
        if left_weapon.lower() != "empty":
            # Left weapon name
            left_name = f"[{left_weapon}]"
            left_name_surface = self.config.get_font('medium').render(left_name, True, text_color)
            left_name_x = left_column_x + (column_width - left_name_surface.get_width()) // 2  # Center in column
            self.screen.blit(left_name_surface, (left_name_x, start_y))
            
            # Left weapon stats
            weapon_data = GameSetup.get_weapon_stats(left_weapon)
            if weapon_data:
                left_stats = f"[{weapon_data['range']}/{weapon_data['dice']}/{weapon_data['target']}/{weapon_data['damage']}]"
            else:
                left_stats = "[No stats]"
            
            left_stats_surface = self.config.get_font('small').render(left_stats, True, text_color)
            left_stats_x = left_column_x + (column_width - left_stats_surface.get_width()) // 2  # Center in column
            self.screen.blit(left_stats_surface, (left_stats_x, start_y + line_height))
        
        # Render right weapon (name and stats)
        if right_weapon.lower() != "empty":
            # Right weapon name
            right_name = f"[{right_weapon}]"
            right_name_surface = self.config.get_font('medium').render(right_name, True, text_color)
            right_name_x = right_column_x + (column_width - right_name_surface.get_width()) // 2  # Center in column
            self.screen.blit(right_name_surface, (right_name_x, start_y))
            
            # Right weapon stats
            weapon_data = GameSetup.get_weapon_stats(right_weapon)
            if weapon_data:
                right_stats = f"[{weapon_data['range']}/{weapon_data['dice']}/{weapon_data['target']}/{weapon_data['damage']}]"
            else:
                right_stats = "[No stats]"
            
            right_stats_surface = self.config.get_font('small').render(right_stats, True, text_color)
            right_stats_x = right_column_x + (column_width - right_stats_surface.get_width()) // 2  # Center in column
            self.screen.blit(right_stats_surface, (right_stats_x, start_y + line_height))

    def render_action_menu(self, _current_survivor: Optional[Survivor], _available_actions: List[str]):
        """Action menu is now integrated into turn info window - this method does nothing."""
        # Action menu functionality moved to render_turn_info
        pass


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
            self.ui_renderer.render_turn_info(
                ui_state['turn_info'],
                ui_state.get('current_survivor'),
                ui_state.get('available_actions') if ui_state.get('show_action_menu') else None,
                game_world.get('survivors', []),  # Pass survivor list
                ui_state.get('combat_info')  # Pass combat info
            )
        
        if 'survivors_data' in game_world and 'survivors' in game_world:
            self.ui_renderer.render_survivor_cards(
                game_world['survivors_data'],
                game_world['survivors'],
                ui_state.get('current_survivor')
            )
        
        # Action menu is now integrated into turn_info window - no separate rendering needed
        
        # Update display
        pygame.display.flip()