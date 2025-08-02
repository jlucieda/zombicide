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

def draw_map_from_json(json_path, map_index=0):
    """
    Reads map data from a JSON file and visualizes a single tile using matplotlib.

    NOTE: This function is currently designed to display only the first tile (0,0) of a map.
    It is also a blocking call, and the program will not continue until the plot is closed.
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    map_data = data["maps"][map_index]
    tile = map_data["tiles"][0][0]  # Only one tile for this map
    zones = tile["zones"]

    fig, ax = plt.subplots(figsize=(5, 5))

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

    ax.set_xlim(0, TILE_SIZE)
    ax.set_ylim(0, TILE_SIZE)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.show()

if __name__ == "__main__":
    print("Drawing Zombicide Map from JSON database...")
    draw_map_from_json("maps_db.json", map_index=0)