import pygame
import json
import sys

class GameWindow:
    def __init__(self, width=1200, height=1000, title="Zombicide Game"):
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
        
        # Map data
        self.map_data = None

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
                
                # Draw zone features text
                features_text = ','.join(zone["features"])
                text_surface = self.font_small.render(features_text, True, self.BLACK)
                text_rect = text_surface.get_rect(center=(x + self.ZONE_PIXEL_SIZE//2, y + self.ZONE_PIXEL_SIZE//2))
                self.screen.blit(text_surface, text_rect)

                # Draw connections (walls and doors)
                conns = zone.get("connections", {})
                for direction, conn in conns.items():
                    if conn["type"] == "wall":
                        self.draw_wall(x, y, direction)
                        if "door" in conn:
                            opened = conn.get("opened", False)
                            self.draw_door(x, y, direction, opened)

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        """Update game state."""
        pass

    def draw(self):
        """Update the display only."""
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        print("Starting game window...")
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS

    def cleanup(self):
        """Clean up pygame resources."""
        pygame.quit()
        sys.exit()