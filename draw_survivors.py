import pygame
import json

def draw_survivor_card(screen, survivor, x, y, width=280, height=380):
    """Draw a survivor card at the specified position using pygame."""
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    RED = (255, 0, 0)
    
    level_colors = {
        'blue': BLUE,
        'yellow': YELLOW, 
        'orange': ORANGE,
        'red': RED
    }
    
    # Fonts
    font_large = pygame.font.Font(None, 20)
    font_medium = pygame.font.Font(None, 16)
    font_small = pygame.font.Font(None, 14)
    
    # Draw card background with white border (3 pixel width)
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 3)
    pygame.draw.rect(screen, GRAY, (x+3, y+3, width-6, height-6))
    
    # Draw survivor name
    name_surface = font_large.render(survivor['name'], True, BLACK)
    name_rect = name_surface.get_rect(centerx=x + width//2, y=y + 10)
    screen.blit(name_surface, name_rect)
    
    # Draw level color indicator
    level_color = level_colors.get(survivor['level'], GRAY)
    level_rect = pygame.Rect(x + 20, y + 35, width - 40, 25)
    pygame.draw.rect(screen, level_color, level_rect)
    pygame.draw.rect(screen, BLACK, level_rect, 1)
    
    level_surface = font_medium.render(survivor['level'].upper(), True, WHITE)
    level_text_rect = level_surface.get_rect(center=level_rect.center)
    screen.blit(level_surface, level_text_rect)
    
    # Draw wounds and experience
    wounds_surface = font_medium.render(f"Wounds: {survivor['wounds']}", True, BLACK)
    screen.blit(wounds_surface, (x + 10, y + 70))
    
    exp_surface = font_medium.render(f"XP: {survivor['exp']}", True, BLACK)
    screen.blit(exp_surface, (x + 10, y + 90))
    
    # Draw equipment section
    equipment_title = font_medium.render("Equipment:", True, BLACK)
    screen.blit(equipment_title, (x + 10, y + 120))
    
    y_offset = 140
    for slot, item in survivor.get('equipment', {}).items():
        if item and item != "empty":
            equipment_text = f"{slot}: {item}"
            equipment_surface = font_small.render(equipment_text, True, BLACK)
            screen.blit(equipment_surface, (x + 15, y + y_offset))
            y_offset += 18
    
    # Draw skills section
    skills_title = font_medium.render("Skills:", True, BLACK)
    screen.blit(skills_title, (x + 10, y + y_offset + 10))
    y_offset += 30
    
    # Get active skills based on level
    levels = ['blue', 'yellow', 'orange1', 'orange2', 'red1', 'red2', 'red3']
    try:
        current_level_index = levels.index(survivor['level'])
        for level in levels[:current_level_index + 1]:
            skill_key = f'skill_{level}'
            if skill_key in survivor['skills']:
                skill = survivor['skills'][skill_key]
                if skill and skill != "empty":
                    skill_surface = font_small.render(f"• {skill}", True, BLACK)
                    screen.blit(skill_surface, (x + 15, y + y_offset))
                    y_offset += 16
    except ValueError:
        # If level not found in list, just show the blue skill
        if 'skill_blue' in survivor['skills']:
            skill = survivor['skills']['skill_blue']
            if skill and skill != "empty":
                skill_surface = font_small.render(f"• {skill}", True, BLACK)
                screen.blit(skill_surface, (x + 15, y + y_offset))

def draw_all_survivors(json_path, screen):
    """Draw all survivor cards on the screen."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        survivors = data['survivors']
        
        # Position cards to the right of the map
        card_width = 280
        card_height = 380
        card_start_x = 550  # Position to the right of the 450px wide map (50px margin + 450px map)
        spacing = 20
        
        for i, survivor in enumerate(survivors):
            card_y = 50 + (i * (card_height + spacing))
            draw_survivor_card(screen, survivor, card_start_x, card_y, card_width, card_height)
        
        # Remove print to avoid console spam during game loop
        
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"Error loading survivor data: {e}")

if __name__ == "__main__":
    # Test the survivor card drawing
    pygame.init()
    screen = pygame.display.set_mode((1200, 1000))
    pygame.display.set_caption("Survivor Cards Test")
    
    screen.fill((0, 0, 0))
    draw_all_survivors("survivors_db.json", screen)
    pygame.display.flip()
    
    # Keep window open
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(60)
    
    pygame.quit()