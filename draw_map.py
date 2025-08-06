import pygame
import json
import sys

# Constants for drawing
TILE_SIZE = 3
ZONE_PIXEL_SIZE = 150
BUILDING_COLOR = (210, 180, 140)  # light brown
STREET_COLOR = (238, 238, 238)   # light gray
WALL_COLOR = (0, 0, 0)  # black
DOOR_COLOR = (0, 0, 255)  # blue
MAP_START_X = 50
MAP_START_Y = 50

def draw_door(screen, x, y, direction, opened):
    """Draw a door on the wall in the given direction at (x, y)."""
    door_size = 40
    
    if opened:
        # Draw a 45º line (like a blueprint)
        if direction == "up":
            pygame.draw.line(screen, DOOR_COLOR,
                           (x + ZONE_PIXEL_SIZE//2 - 20, y), 
                           (x + ZONE_PIXEL_SIZE//2, y - 20), 3)
        elif direction == "down":
            pygame.draw.line(screen, DOOR_COLOR,
                           (x + ZONE_PIXEL_SIZE//2 - 20, y + ZONE_PIXEL_SIZE), 
                           (x + ZONE_PIXEL_SIZE//2, y + ZONE_PIXEL_SIZE + 20), 3)
        elif direction == "left":
            pygame.draw.line(screen, DOOR_COLOR,
                           (x, y + ZONE_PIXEL_SIZE//2 - 20), 
                           (x - 20, y + ZONE_PIXEL_SIZE//2), 3)
        elif direction == "right":
            pygame.draw.line(screen, DOOR_COLOR,
                           (x + ZONE_PIXEL_SIZE, y + ZONE_PIXEL_SIZE//2 - 20), 
                           (x + ZONE_PIXEL_SIZE + 20, y + ZONE_PIXEL_SIZE//2), 3)
    else:
        # Draw a small rectangle (closed door)
        if direction == "up":
            door_x = x + (ZONE_PIXEL_SIZE - door_size) // 2
            pygame.draw.rect(screen, DOOR_COLOR, (door_x, y - 3, door_size, 6))
        elif direction == "down":
            door_x = x + (ZONE_PIXEL_SIZE - door_size) // 2
            pygame.draw.rect(screen, DOOR_COLOR, (door_x, y + ZONE_PIXEL_SIZE - 3, door_size, 6))
        elif direction == "left":
            door_y = y + (ZONE_PIXEL_SIZE - door_size) // 2
            pygame.draw.rect(screen, DOOR_COLOR, (x - 3, door_y, 6, door_size))
        elif direction == "right":
            door_y = y + (ZONE_PIXEL_SIZE - door_size) // 2
            pygame.draw.rect(screen, DOOR_COLOR, (x + ZONE_PIXEL_SIZE - 3, door_y, 6, door_size))

def draw_survivor_card(screen, survivor, x_pos, y_pos, card_width=280, card_height=380):
    """Draw a survivor card at the specified position with white border, 3px width."""
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LIGHT_GRAY = (200, 200, 200)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    RED = (255, 0, 0)
    
    level_colors = {'blue': BLUE, 'yellow': YELLOW, 'orange': ORANGE, 'red': RED}
    
    # Fonts
    font_large = pygame.font.Font(None, 24)
    font_medium = pygame.font.Font(None, 18)
    font_small = pygame.font.Font(None, 14)
    
    # Draw card background with white border, 3 pixel width
    pygame.draw.rect(screen, WHITE, (x_pos, y_pos, card_width, card_height), 3)
    pygame.draw.rect(screen, LIGHT_GRAY, (x_pos + 3, y_pos + 3, card_width - 6, card_height - 6))
    
    # Add survivor name
    name_surface = font_large.render(survivor['name'], True, BLACK)
    name_rect = name_surface.get_rect(centerx=x_pos + card_width//2, y=y_pos + 10)
    screen.blit(name_surface, name_rect)
    
    # Add level color indicator
    level_color = level_colors.get(survivor['level'], LIGHT_GRAY)
    level_rect = pygame.Rect(x_pos + 20, y_pos + 35, card_width - 40, 25)
    pygame.draw.rect(screen, level_color, level_rect)
    pygame.draw.rect(screen, BLACK, level_rect, 1)
    
    level_surface = font_medium.render(survivor['level'].upper(), True, WHITE)
    level_text_rect = level_surface.get_rect(center=level_rect.center)
    screen.blit(level_surface, level_text_rect)
    
    # Add wounds and experience
    wounds_surface = font_medium.render(f"Wounds: {survivor['wounds']}", True, BLACK)
    screen.blit(wounds_surface, (x_pos + 10, y_pos + 70))
    
    exp_surface = font_medium.render(f"XP: {survivor['exp']}", True, BLACK)
    screen.blit(exp_surface, (x_pos + 10, y_pos + 90))
    
    # Add equipment (only non-empty items)
    equipment_title = font_medium.render("Equipment:", True, BLACK)
    screen.blit(equipment_title, (x_pos + 10, y_pos + 120))
    
    y_offset = 140
    for slot, item in survivor.get('equipment', {}).items():
        if item and item != "empty":
            equipment_text = f"{slot}: {item}"
            equipment_surface = font_small.render(equipment_text, True, BLACK)
            screen.blit(equipment_surface, (x_pos + 15, y_pos + y_offset))
            y_offset += 18

def draw_survivor_tokens(screen, survivors):
    """Draw survivor tokens in zone (0,2) - white circles with black borders and names."""
    if not survivors:
        return
        
    # Zone (0,2) coordinates - zone at row 0, column 2
    zone_row = 0
    zone_col = 2
    zone_x = MAP_START_X + zone_col * ZONE_PIXEL_SIZE
    zone_y = MAP_START_Y + zone_row * ZONE_PIXEL_SIZE
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Token properties
    token_diameter = 40
    token_radius = token_diameter // 2
    border_width = 2
    
    # Position tokens within the zone
    tokens_per_row = 3
    spacing = 10
    start_x = zone_x + spacing
    start_y = zone_y + spacing
    
    # Font for names
    font_small = pygame.font.Font(None, 14)
    
    for i, survivor in enumerate(survivors):
        # Calculate position for each token
        row = i // tokens_per_row
        col = i % tokens_per_row
        
        token_x = start_x + col * (token_diameter + spacing) + token_radius
        token_y = start_y + row * (token_diameter + spacing) + token_radius
        
        # Make sure token stays within zone bounds
        if token_x + token_radius > zone_x + ZONE_PIXEL_SIZE or \
           token_y + token_radius > zone_y + ZONE_PIXEL_SIZE:
            continue
        
        # Draw white circle with black border
        pygame.draw.circle(screen, WHITE, (token_x, token_y), token_radius)
        pygame.draw.circle(screen, BLACK, (token_x, token_y), token_radius, border_width)
        
        # Draw survivor name in the middle
        name_surface = font_small.render(survivor['name'], True, BLACK)
        name_rect = name_surface.get_rect(center=(token_x, token_y))
        screen.blit(name_surface, name_rect)

def draw_zombie_tokens(screen):
    """Draw zombie tokens in zone (2,2) - dark grey circles with 'Z' in the middle."""
    # Zone (2,2) coordinates - zone at row 2, column 2 (bottom-right)
    zone_row = 2
    zone_col = 2
    zone_x = MAP_START_X + zone_col * ZONE_PIXEL_SIZE
    zone_y = MAP_START_Y + zone_row * ZONE_PIXEL_SIZE
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_GRAY = (64, 64, 64)
    
    # Token properties
    token_diameter = 40
    token_radius = token_diameter // 2
    border_width = 2
    
    # Position tokens within the zone
    tokens_per_row = 2
    spacing = 20
    start_x = zone_x + spacing
    start_y = zone_y + spacing
    
    # Font for 'Z'
    font_medium = pygame.font.Font(None, 18)
    
    # Draw only 2 zombie tokens
    num_zombies = 2
    
    for i in range(num_zombies):
        # Calculate position for each token
        row = i // tokens_per_row
        col = i % tokens_per_row
        
        token_x = start_x + col * (token_diameter + spacing) + token_radius
        token_y = start_y + row * (token_diameter + spacing) + token_radius
        
        # Make sure token stays within zone bounds
        if token_x + token_radius > zone_x + ZONE_PIXEL_SIZE or \
           token_y + token_radius > zone_y + ZONE_PIXEL_SIZE:
            continue
        
        # Draw dark grey circle with black border
        pygame.draw.circle(screen, DARK_GRAY, (token_x, token_y), token_radius)
        pygame.draw.circle(screen, BLACK, (token_x, token_y), token_radius, border_width)
        
        # Draw 'Z' in the middle
        z_surface = font_medium.render('Z', True, WHITE)
        z_rect = z_surface.get_rect(center=(token_x, token_y))
        screen.blit(z_surface, z_rect)

def draw_map_from_json(json_path, map_index=0):
    """
    Reads map data from a JSON file and visualizes it using pygame.
    Also loads and displays survivor cards from survivors_db.json.
    """
    pygame.init()
    
    # Create pygame window with exact 1200x1000 pixels
    screen = pygame.display.set_mode((1200, 1000))
    pygame.display.set_caption("Zombicide - Map and Survivors")
    clock = pygame.time.Clock()
    
    # Load map data
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        map_data = data["maps"][map_index]
        tile = map_data["tiles"][0][0]  # Only one tile for this map
        zones = tile["zones"]
    except (FileNotFoundError, KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error loading map data: {e}")
        pygame.quit()
        sys.exit(1)
    
    # Load survivor data
    try:
        with open('survivors_db.json', 'r') as f:
            survivors_data = json.load(f)
        survivors = survivors_data["survivors"]
    except FileNotFoundError:
        survivors = []
        print("Warning: survivors_db.json not found")

    # Fonts
    font_small = pygame.font.Font(None, 14)
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen with black background
        screen.fill((0, 0, 0))
        
        # Draw zones
        for zr in range(TILE_SIZE):
            for zc in range(TILE_SIZE):
                zone = zones[zr][zc]
                x = MAP_START_X + zc * ZONE_PIXEL_SIZE
                y = MAP_START_Y + zr * ZONE_PIXEL_SIZE

                # Set color based on zone type
                color = BUILDING_COLOR if "building" in zone["features"] else STREET_COLOR

                # Draw zone background
                pygame.draw.rect(screen, color, (x, y, ZONE_PIXEL_SIZE, ZONE_PIXEL_SIZE))
                
                # Draw zone border
                pygame.draw.rect(screen, WALL_COLOR, (x, y, ZONE_PIXEL_SIZE, ZONE_PIXEL_SIZE), 2)
                
                # Draw zone features text
                features_text = ','.join(zone["features"])
                text_surface = font_small.render(features_text, True, WALL_COLOR)
                text_rect = text_surface.get_rect(center=(x + ZONE_PIXEL_SIZE//2, y + ZONE_PIXEL_SIZE//2))
                screen.blit(text_surface, text_rect)

                # Draw walls and doors
                conns = zone.get("connections", {})
                for direction, conn in conns.items():
                    if conn["type"] == "wall":
                        # Draw wall
                        wall_width = 4
                        if direction == "up":
                            pygame.draw.line(screen, WALL_COLOR, 
                                           (x, y), (x + ZONE_PIXEL_SIZE, y), wall_width)
                        elif direction == "down":
                            pygame.draw.line(screen, WALL_COLOR,
                                           (x, y + ZONE_PIXEL_SIZE), (x + ZONE_PIXEL_SIZE, y + ZONE_PIXEL_SIZE), wall_width)
                        elif direction == "left":
                            pygame.draw.line(screen, WALL_COLOR,
                                           (x, y), (x, y + ZONE_PIXEL_SIZE), wall_width)
                        elif direction == "right":
                            pygame.draw.line(screen, WALL_COLOR,
                                           (x + ZONE_PIXEL_SIZE, y), (x + ZONE_PIXEL_SIZE, y + ZONE_PIXEL_SIZE), wall_width)
                        
                        # Draw door if present
                        if "door" in conn:
                            opened = conn.get("opened", False)
                            draw_door(screen, x, y, direction, opened)

        # Draw survivor cards to the right of the map
        card_start_x = MAP_START_X + (TILE_SIZE * ZONE_PIXEL_SIZE) + 50  # Position to the right of the map
        for i, survivor in enumerate(survivors):  # Show all survivors
            card_y = MAP_START_Y + (i * 400)  # Stack cards vertically, one below the other
            draw_survivor_card(screen, survivor, card_start_x, card_y)
        
        # Draw survivor tokens in zone (0,2)
        draw_survivor_tokens(screen, survivors)
        
        # Draw zombie tokens in zone (2,2)
        draw_zombie_tokens(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()
    print("Display closed")
    print(f"Loaded {len(survivors)} survivors from survivors_db.json")

if __name__ == "__main__":
    print("Drawing Zombicide Map from JSON database...")
    draw_map_from_json("maps_db.json", map_index=0)