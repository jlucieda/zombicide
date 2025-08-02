import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json

# Map structure constants
MAP_SIZE = 4  # 4x4 matrix of tiles
TILE_SIZE = 3  # Each tile has 3x3 zones
ZONES_PER_TILE = TILE_SIZE * TILE_SIZE

# Connection types between adjacent zones
CONNECTION_WALL = 0    # No connection - wall blocks movement
CONNECTION_OPEN = 1    # Open connection - free movement
CONNECTION_GATE = 2    # Gate connection - movement through gate in building
CONNECTION_DOOR = 3    # Door connection - movement when door is open

# Connection type mapping for JSON compatibility
CONNECTION_TYPE_MAP = {
    "wall": CONNECTION_WALL,
    "open": CONNECTION_OPEN, 
    "gate": CONNECTION_GATE,
    "door": CONNECTION_DOOR
}

# Zone features
ZONE_FEATURES = {
    "street": {"color": "#eeeeee", "actions": ["move", "search_noise"]},
    "building": {"color": "#d2b48c", "actions": ["move", "search_quiet", "barricade"]},
    "shop": {"color": "#ffcc99", "actions": ["move", "search_equipment"]},
    "spawn": {"color": "#ff9999", "actions": ["zombie_spawn"]}
}

def get_zone_color(features):
    """Get zone color based on features, with priority order."""
    if "spawn" in features:
        return ZONE_FEATURES["spawn"]["color"]
    elif "shop" in features:
        return ZONE_FEATURES["shop"]["color"] 
    elif "building" in features:
        return ZONE_FEATURES["building"]["color"]
    else:
        return ZONE_FEATURES["street"]["color"]

def _draw_wall(ax, x, y, direction):
    """Draw a wall in the specified direction."""
    if direction == "up":
        ax.plot([x, x+1], [y+1, y+1], color='black', linewidth=3)
    elif direction == "down":
        ax.plot([x, x+1], [y, y], color='black', linewidth=3)
    elif direction == "left":
        ax.plot([x, x], [y, y+1], color='black', linewidth=3)
    elif direction == "right":
        ax.plot([x+1, x+1], [y, y+1], color='black', linewidth=3)

def _draw_door(ax, x, y, direction):
    """Draw a door opening in the wall."""
    if direction == "up":
        ax.plot([x+0.4, x+0.6], [y+1, y+1], color='blue', linewidth=5)
    elif direction == "down":
        ax.plot([x+0.4, x+0.6], [y, y], color='blue', linewidth=5)
    elif direction == "left":
        ax.plot([x, x], [y+0.4, y+0.6], color='blue', linewidth=5)
    elif direction == "right":
        ax.plot([x+1, x+1], [y+0.4, y+0.6], color='blue', linewidth=5)

def _draw_gate(ax, x, y, direction):
    """Draw a gate opening in the wall."""
    if direction == "up":
        ax.plot([x+0.3, x+0.7], [y+1, y+1], color='green', linewidth=4)
    elif direction == "down":
        ax.plot([x+0.3, x+0.7], [y, y], color='green', linewidth=4)
    elif direction == "left":
        ax.plot([x, x], [y+0.3, y+0.7], color='green', linewidth=4)
    elif direction == "right":
        ax.plot([x+1, x+1], [y+0.3, y+0.7], color='green', linewidth=4)

def draw_map_from_json(json_path, map_index=0):
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        map_data = data["maps"][map_index]
        tile = map_data["tiles"][0][0]  # Only one tile for this map
        zones = tile["zones"]
    except (FileNotFoundError, KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error loading map data: {e}")
        return

    ZONE_SIZE = 1
    fig, ax = plt.subplots(figsize=(TILE_SIZE * 2, TILE_SIZE * 2))

    # Draw zones
    for zr in range(TILE_SIZE):
        for zc in range(TILE_SIZE):
            zone = zones[zr][zc]
            x = zc
            y = TILE_SIZE - 1 - zr  # invert y for display

            # Set color based on zone features
            color = get_zone_color(zone["features"])

            rect = patches.Rectangle((x, y), ZONE_SIZE, ZONE_SIZE, linewidth=2, edgecolor='black', facecolor=color)
            ax.add_patch(rect)
            ax.text(x + 0.5, y + 0.5, ','.join(zone["features"]), ha='center', va='center', fontsize=8)

            # Draw connections between zones
            conns = zone.get("connections", {})
            for direction, conn in conns.items():
                connection_type = CONNECTION_TYPE_MAP.get(conn["type"], CONNECTION_WALL)
                
                if connection_type == CONNECTION_WALL:
                    _draw_wall(ax, x, y, direction)
                elif connection_type == CONNECTION_DOOR:
                    _draw_wall(ax, x, y, direction)
                    _draw_door(ax, x, y, direction)
                elif connection_type == CONNECTION_GATE:
                    _draw_wall(ax, x, y, direction)
                    _draw_gate(ax, x, y, direction)
                # CONNECTION_OPEN doesn't draw anything (open passage)

    ax.set_xlim(0, TILE_SIZE)
    ax.set_ylim(0, TILE_SIZE)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.show()

if __name__ == "__main__":
    print("Drawing Zombicide Map from JSON database...")