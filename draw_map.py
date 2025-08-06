import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json

# Constants for drawing
TILE_SIZE = 3
ZONE_SIZE = 1
BUILDING_COLOR = "#d2b48c"  # light brown
STREET_COLOR = "#eeeeee"   # light gray
WALL_COLOR = "black"
WALL_LINEWIDTH = 3
DOOR_COLOR = "blue"
DOOR_LINEWIDTH = 2

def draw_door(ax, x, y, direction, opened):
    """Draw a door on the wall in the given direction at (x, y)."""
    # Door size as fraction of wall length
    door_length = 0.3
    door_thickness = 0.12

    if opened:
        # Draw a 45º line (like a blueprint)
        if direction == "up":
            ax.plot([x + 0.35, x + 0.65], [y + 1, y + 0.7], color=DOOR_COLOR, linewidth=DOOR_LINEWIDTH)
        elif direction == "down":
            ax.plot([x + 0.35, x + 0.65], [y, y + 0.3], color=DOOR_COLOR, linewidth=DOOR_LINEWIDTH)
        elif direction == "left":
            ax.plot([x, x + 0.3], [y + 0.35, y + 0.65], color=DOOR_COLOR, linewidth=DOOR_LINEWIDTH)
        elif direction == "right":
            ax.plot([x + 1, x + 0.7], [y + 0.35, y + 0.65], color=DOOR_COLOR, linewidth=DOOR_LINEWIDTH)
    else:
        # Draw a small rectangle (closed door)
        if direction == "up":
            rect = patches.Rectangle(
                (x + 0.5 - door_length / 2, y + 1 - door_thickness / 2),
                door_length, door_thickness,
                linewidth=0, edgecolor=None, facecolor=DOOR_COLOR, zorder=10
            )
        elif direction == "down":
            rect = patches.Rectangle(
                (x + 0.5 - door_length / 2, y - door_thickness / 2),
                door_length, door_thickness,
                linewidth=0, edgecolor=None, facecolor=DOOR_COLOR, zorder=10
            )
        elif direction == "left":
            rect = patches.Rectangle(
                (x - door_thickness / 2, y + 0.5 - door_length / 2),
                door_thickness, door_length,
                linewidth=0, edgecolor=None, facecolor=DOOR_COLOR, zorder=10
            )
        elif direction == "right":
            rect = patches.Rectangle(
                (x + 1 - door_thickness / 2, y + 0.5 - door_length / 2),
                door_thickness, door_length,
                linewidth=0, edgecolor=None, facecolor=DOOR_COLOR, zorder=10
            )
        ax.add_patch(rect)

def draw_survivor_card(ax, survivor, x_pos, y_pos, card_width=3, card_height=4):
    """
    Draw a survivor card at the specified position with white border, 3px width.
    """
    # Draw card background with white border, 3 pixel width
    card_rect = patches.Rectangle((x_pos, y_pos), card_width, card_height, 
                                 linewidth=3, edgecolor='white', facecolor='lightgray')
    ax.add_patch(card_rect)
    
    # Add survivor name
    ax.text(x_pos + card_width/2, y_pos + card_height - 0.3, survivor['name'], 
            ha='center', va='center', fontsize=14, fontweight='bold', color='black')
    
    # Add level color indicator
    level_colors = {'blue': 'blue', 'yellow': 'gold', 'orange': 'orange', 'red': 'red'}
    level_color = level_colors.get(survivor['level'], 'gray')
    level_rect = patches.Rectangle((x_pos + 0.2, y_pos + card_height - 0.9), 
                                  card_width - 0.4, 0.3, 
                                  linewidth=1, edgecolor='black', facecolor=level_color)
    ax.add_patch(level_rect)
    ax.text(x_pos + card_width/2, y_pos + card_height - 0.75, survivor['level'].upper(), 
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # Add wounds and experience
    ax.text(x_pos + 0.2, y_pos + card_height - 1.4, f"Wounds: {survivor['wounds']}", 
            fontsize=10, va='center', color='black')
    ax.text(x_pos + 0.2, y_pos + card_height - 1.7, f"XP: {survivor['exp']}", 
            fontsize=10, va='center', color='black')
    
    # Add equipment (only non-empty items)
    y_offset = 2.2
    ax.text(x_pos + 0.2, y_pos + y_offset, "Equipment:", fontsize=10, fontweight='bold', color='black')
    y_offset -= 0.3
    for slot, item in survivor.get('equipment', {}).items():
        if item and item != "empty":
            ax.text(x_pos + 0.3, y_pos + y_offset, f"{slot}: {item}", fontsize=9, color='black')
            y_offset -= 0.3

def draw_map_from_json(json_path, map_index=0):
    """
    Reads map data from a JSON file and visualizes a single tile using matplotlib.
    Also loads and displays survivor cards from survivors_db.json.

    NOTE: This function is currently designed to display only the first tile (0,0) of a map.
    It is also a blocking call, and the program will not continue until the plot is closed.
    """
    # Load map data
    with open(json_path, 'r') as f:
        data = json.load(f)
    map_data = data["maps"][map_index]
    tile = map_data["tiles"][0][0]  # Only one tile for this map
    zones = tile["zones"]
    
    # Load survivor data
    try:
        with open('survivors_db.json', 'r') as f:
            survivors_data = json.load(f)
        survivors = survivors_data["survivors"]
    except FileNotFoundError:
        survivors = []
        print("Warning: survivors_db.json not found")

    fig, ax = plt.subplots(figsize=(12, 10))
    fig.canvas.manager.set_window_title('Zombicide - Map and Survivors')

    # Draw zones
    for zr in range(TILE_SIZE):
        for zc in range(TILE_SIZE):
            zone = zones[zr][zc]
            x = zc
            y = TILE_SIZE - 1 - zr  # invert y for display

            # Set color based on zone type
            color = BUILDING_COLOR if "building" in zone["features"] else STREET_COLOR

            rect = patches.Rectangle((x, y), ZONE_SIZE, ZONE_SIZE, linewidth=2, edgecolor='black', facecolor=color)
            ax.add_patch(rect)
            ax.text(x + 0.5, y + 0.5, ','.join(zone["features"]), ha='center', va='center', fontsize=10)

            # Draw walls and doors
            conns = zone.get("connections", {})
            for direction, conn in conns.items():
                if conn["type"] == "wall":
                    # Draw wall
                    if direction == "up":
                        ax.plot([x, x+1], [y+1, y+1], color=WALL_COLOR, linewidth=WALL_LINEWIDTH)
                    elif direction == "down":
                        ax.plot([x, x+1], [y, y], color=WALL_COLOR, linewidth=WALL_LINEWIDTH)
                    elif direction == "left":
                        ax.plot([x, x], [y, y+1], color=WALL_COLOR, linewidth=WALL_LINEWIDTH)
                    elif direction == "right":
                        ax.plot([x+1, x+1], [y, y+1], color=WALL_COLOR, linewidth=WALL_LINEWIDTH)
                    # Draw door if present
                    if "door" in conn:
                        opened = conn.get("opened", False)
                        draw_door(ax, x, y, direction, opened)

    # Draw survivor cards to the right of the map
    card_start_x = TILE_SIZE + 0.5
    for i, survivor in enumerate(survivors):  # Show all survivors
        card_y = TILE_SIZE - 1 - (i * 4.5)  # Stack cards vertically, one below the other
        draw_survivor_card(ax, survivor, card_start_x, card_y)
    
    # Set plot limits to accommodate both map and cards
    ax.set_xlim(0, TILE_SIZE + 4)
    ax.set_ylim(-5, TILE_SIZE + 1)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Drawing Zombicide Map from JSON database...")
    draw_map_from_json("maps_db.json", map_index=0)