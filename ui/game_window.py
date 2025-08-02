import pygame
import json

class GameWindow:
    def __init__(self, width=1200, height=1000, title="Zombicide Simulation"):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True

        # Color scheme (greyscale)
        self.bg_color = (45, 45, 50)          # Dark grey background
        self.map_border_color = (200, 200, 200)  # Light grey border
        self.grid_line_color = (120, 120, 120)   # Medium grey grid lines
        self.map_bg_color = (70, 70, 75)         # Slightly lighter map background

        # Map properties - 900x900 square centered in window
        self.map_size = 900
        self.map_x = (width - self.map_size) // 2  # Center horizontally
        self.map_y = (height - self.map_size) // 2  # Center vertically
        self.tile_size = 3  # 3x3 zones per tile
        self.zone_size = self.map_size // self.tile_size  # Size of each zone
        
        # Zone colors
        self.zone_colors = {
            "street": (238, 238, 238),    # Light gray
            "building": (210, 180, 140),  # Light brown
            "shop": (255, 204, 153),      # Orange
            "spawn": (255, 153, 153)      # Red
        }
        
        # Map data
        self.map_data = None

    def load_map(self, json_path, map_index=0):
        """Load map data from JSON file."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            self.map_data = data["maps"][map_index]
        except (FileNotFoundError, KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error loading map data: {e}")
            self.map_data = None

    def get_zone_color(self, features):
        """Get zone color based on features, with priority order."""
        if "spawn" in features:
            return self.zone_colors["spawn"]
        elif "shop" in features:
            return self.zone_colors["shop"]
        elif "building" in features:
            return self.zone_colors["building"]
        else:
            return self.zone_colors["street"]

    def draw_wall(self, x, y, direction, thickness=4):
        """Draw a wall in the specified direction."""
        if direction == "up":
            pygame.draw.line(self.screen, (0, 0, 0), 
                           (x, y), (x + self.zone_size, y), thickness)
        elif direction == "down":
            pygame.draw.line(self.screen, (0, 0, 0),
                           (x, y + self.zone_size), (x + self.zone_size, y + self.zone_size), thickness)
        elif direction == "left":
            pygame.draw.line(self.screen, (0, 0, 0),
                           (x, y), (x, y + self.zone_size), thickness)
        elif direction == "right":
            pygame.draw.line(self.screen, (0, 0, 0),
                           (x + self.zone_size, y), (x + self.zone_size, y + self.zone_size), thickness)

    def draw_door(self, x, y, direction):
        """Draw a door opening in the wall."""
        door_size = self.zone_size // 3
        if direction == "up":
            door_x = x + (self.zone_size - door_size) // 2
            pygame.draw.line(self.screen, (0, 0, 255),
                           (door_x, y), (door_x + door_size, y), 6)
        elif direction == "down":
            door_x = x + (self.zone_size - door_size) // 2
            pygame.draw.line(self.screen, (0, 0, 255),
                           (door_x, y + self.zone_size), (door_x + door_size, y + self.zone_size), 6)
        elif direction == "left":
            door_y = y + (self.zone_size - door_size) // 2
            pygame.draw.line(self.screen, (0, 0, 255),
                           (x, door_y), (x, door_y + door_size), 6)
        elif direction == "right":
            door_y = y + (self.zone_size - door_size) // 2
            pygame.draw.line(self.screen, (0, 0, 255),
                           (x + self.zone_size, door_y), (x + self.zone_size, door_y + door_size), 6)

    def draw_map(self):
        if not self.map_data:
            return
            
        # Fill map background
        pygame.draw.rect(self.screen, self.map_bg_color,
                        (self.map_x, self.map_y, self.map_size, self.map_size))
        
        # Draw main map border
        pygame.draw.rect(self.screen, self.map_border_color, 
                        (self.map_x, self.map_y, self.map_size, self.map_size), 3)

        # Get tile data (assuming single tile for now)
        tile = self.map_data["tiles"][0][0]
        zones = tile["zones"]
        
        # Draw zones
        for zr in range(self.tile_size):
            for zc in range(self.tile_size):
                zone = zones[zr][zc]
                
                # Calculate zone position
                x = self.map_x + zc * self.zone_size
                y = self.map_y + zr * self.zone_size
                
                # Draw zone background
                color = self.get_zone_color(zone["features"])
                pygame.draw.rect(self.screen, color, 
                               (x, y, self.zone_size, self.zone_size))
                
                # Draw zone border
                pygame.draw.rect(self.screen, (0, 0, 0),
                               (x, y, self.zone_size, self.zone_size), 2)
                
                # Draw connections (walls)
                conns = zone.get("connections", {})
                for direction, conn in conns.items():
                    if conn["type"] == "wall":
                        self.draw_wall(x, y, direction)
                        if conn.get("door"):
                            self.draw_door(x, y, direction)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Add more event handling here

    def update(self):
        # Add game state updates here
        pass

    def draw(self):
        # Fill the screen with background color
        self.screen.fill(self.bg_color)
        
        # Draw the map
        self.draw_map()
        
        # Update the display
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS

    def cleanup(self):
        pygame.quit()