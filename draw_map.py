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
DOOR_LINEWIDTH = 5

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
    
    # NOTE: Assuming a single tile map for now.
    # To support multi-tile maps, this would need to iterate through all tiles.
    tile = map_data["tiles"][0][0]
    zones = tile["zones"]

    TILE_SIZE = 3
    ZONE_SIZE = 1
    fig, ax = plt.subplots(figsize=(5, 5))

    # Draw zones
    for zr in range(TILE_SIZE):
        for zc in range(TILE_SIZE):
            zone = zones[zr][zc]
            x = zc
            y = TILE_SIZE - 1 - zr  # invert y for display

            # Set color based on zone type
            if "building" in zone["features"]:
                color = "#d2b48c"  # light brown
            else:
                color = "#eeeeee"  # light gray for street

            rect = patches.Rectangle((x, y), ZONE_SIZE, ZONE_SIZE, linewidth=2, edgecolor='black', facecolor=color)
            ax.add_patch(rect)
            ax.text(x + 0.5, y + 0.5, ','.join(zone["features"]), ha='center', va='center', fontsize=10)

            # Draw walls and doors
            conns = zone.get("connections", {})
            for direction, conn in conns.items():
                if conn["type"] == "wall":
                    if direction == "up":
                        ax.plot([x, x+1], [y+1, y+1], color='black', linewidth=3)
                        if conn.get("door"):
                            ax.plot([x+0.4, x+0.6], [y+1, y+1], color='blue', linewidth=5)
                    if direction == "down":
                        ax.plot([x, x+1], [y, y], color='black', linewidth=3)
                        if conn.get("door"):
                            ax.plot([x+0.4, x+0.6], [y, y], color='blue', linewidth=5)
                    if direction == "left":
                        ax.plot([x, x], [y, y+1], color='black', linewidth=3)
                        if conn.get("door"):
                            ax.plot([x, x], [y+0.4, y+0.6], color='blue', linewidth=5)
                    if direction == "right":
                        ax.plot([x+1, x+1], [y, y+1], color='black', linewidth=3)
                        if conn.get("door"):
                            ax.plot([x+1, x+1], [y+0.4, y+0.6], color='blue', linewidth=5)

    ax.set_xlim(0, TILE_SIZE)
    ax.set_ylim(0, TILE_SIZE)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.show()

if __name__ == "__main__":
    print("Drawing Zombicide Map from JSON database...")