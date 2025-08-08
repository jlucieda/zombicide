import pygame
import sys
from enum import Enum, auto

# --- Game Data ---
SURVIVORS = [
    {"name": "Eva", "actions_left": 3},
    {"name": "Josh", "actions_left": 3}
]
ZOMBIES = []
MAP_SPAWN_ZONES = {(0, 0): (2, 2)}  # map_index: (zone_row, zone_col)
CURRENT_MAP_INDEX = 0

# --- FSM States ---
class GameState(Enum):
    SURVIVOR = auto()
    ZOMBIE = auto()
    SPAWN = auto()
    END = auto()

# --- Game State ---
turn_number = 1
current_state = GameState.SURVIVOR
survivor_index = 0

def draw_dashboard(screen):
    font = pygame.font.SysFont("Arial", 28)
    small_font = pygame.font.SysFont("Arial", 22)
    pygame.draw.rect(screen, (220, 220, 220), (0, 0, 1200, 120))
    turn_text = font.render(f"Turn: {turn_number}", True, (0, 0, 0))
    phase_text = font.render(f"Phase: {current_state.name}", True, (0, 0, 0))
    screen.blit(turn_text, (20, 20))
    screen.blit(phase_text, (220, 20))
    if current_state == GameState.SURVIVOR:
        s = SURVIVORS[survivor_index]
        pygame.draw.rect(screen, (255, 255, 180), (420, 10, 320, 100), 0)
        name_text = font.render(f"Survivor: {s['name']}", True, (0, 0, 0))
        actions_text = small_font.render(f"Actions left: {s['actions_left']}", True, (0, 0, 0))
        options_text = small_font.render("Options: Move (M), Attack (A)", True, (0, 0, 0))
        screen.blit(name_text, (440, 20))
        screen.blit(actions_text, (440, 55))
        screen.blit(options_text, (440, 80))
    elif current_state == GameState.ZOMBIE:
        zombie_text = font.render("Zombie Phase: Zombies move and attack!", True, (180, 0, 0))
        screen.blit(zombie_text, (420, 50))
    elif current_state == GameState.SPAWN:
        spawn_text = font.render("Spawn Phase: 1 Walker Zombie spawned!", True, (120, 0, 0))
        screen.blit(spawn_text, (420, 50))
    zombie_count_text = small_font.render(f"Zombies on board: {len(ZOMBIES)}", True, (60, 60, 60))
    screen.blit(zombie_count_text, (900, 20))

def survivor_action(action):
    s = SURVIVORS[survivor_index]
    if s["actions_left"] > 0:
        s["actions_left"] -= 1
        print(f"{s['name']} performed {action}. Actions left: {s['actions_left']}")

def next_survivor():
    global survivor_index, current_state
    survivor_index += 1
    if survivor_index >= len(SURVIVORS):
        survivor_index = 0
        current_state = GameState.ZOMBIE

def spawn_zombie():
    spawn_zone = MAP_SPAWN_ZONES.get(CURRENT_MAP_INDEX, (0, 0))
    ZOMBIES.append({"type": "walker", "zone": spawn_zone})
    print(f"Spawned 1 walker zombie at zone {spawn_zone}.")

def next_turn():
    global turn_number, current_state, survivor_index
    turn_number += 1
    current_state = GameState.SURVIVOR
    survivor_index = 0
    for s in SURVIVORS:
        s["actions_left"] = 3

def zombie_phase():
    # Simple placeholder logic: zombies move and attack
    for z in ZOMBIES:
        # You can expand this with real movement/attack logic
        print(f"Zombie at {z['zone']} moves/attacks!")
    print("Zombie phase complete.")

def run_turn_system(game_window):
    global current_state, survivor_index, turn_number
    screen = game_window.screen
    clock = game_window.clock

    while True:
        screen.fill((180, 180, 180))
        draw_dashboard(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if current_state == GameState.SURVIVOR:
                    if event.key == pygame.K_m:
                        survivor_action("Move")
                    elif event.key == pygame.K_a:
                        survivor_action("Attack")
                    if SURVIVORS[survivor_index]["actions_left"] == 0:
                        next_survivor()
                elif current_state == GameState.ZOMBIE:
                    # Press Z to resolve zombie phase
                    if event.key == pygame.K_z:
                        zombie_phase()
                        current_state = GameState.SPAWN
                elif current_state == GameState.SPAWN:
                    spawn_zombie()
                    current_state = GameState.END
                elif current_state == GameState.END:
                    next_turn()

        pygame.display.flip()
        clock.tick(30)