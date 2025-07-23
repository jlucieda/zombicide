import pygame

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

        # Map properties
        self.map_size = 800
        self.map_x = 0  # Align to left
        self.map_y = 0  # Align to top
        self.grid_cells = 3  # 3x3 grid
        self.cell_size = self.map_size // self.grid_cells

    def draw_map(self):
        # Fill map background
        pygame.draw.rect(self.screen, self.map_bg_color,
                        (self.map_x, self.map_y, self.map_size, self.map_size))
        
        # Draw main map border
        pygame.draw.rect(self.screen, self.map_border_color, 
                        (self.map_x, self.map_y, self.map_size, self.map_size), 
                        3)  # Border thickness of 3 pixels
        
        # Draw grid lines
        for i in range(1, self.grid_cells):
            # Vertical lines
            pygame.draw.line(self.screen, self.grid_line_color,
                           (self.map_x + i * self.cell_size, self.map_y),
                           (self.map_x + i * self.cell_size, self.map_y + self.map_size),
                           1)  # Line thickness of 1 pixel
            # Horizontal lines
            pygame.draw.line(self.screen, self.grid_line_color,
                           (self.map_x, self.map_y + i * self.cell_size),
                           (self.map_x + self.map_size, self.map_y + i * self.cell_size),
                           1)  # Line thickness of 1 pixel

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