import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json

def draw_survivor_card(ax, survivor, x, y, width=3, height=4):
    # Draw card border
    rect = patches.Rectangle((x, y), width, height, linewidth=3, edgecolor='black', facecolor='white')
    ax.add_patch(rect)
    
    # Add text content
    name_text = f"{survivor['name']} [{survivor['class']}]"
    stats_text = f"Wounds: {survivor['wounds']}; Exp: {survivor['exp']}; Level: {survivor['level']}"
    
    # Get active skills based on level
    active_skills = []
    levels = ['blue', 'yellow', 'orange1', 'orange2', 'red1', 'red2', 'red3']
    current_level_index = levels.index(survivor['level'])
    for level in levels[:current_level_index + 1]:
        skill = survivor['skills'][f'skill_{level}']
        if skill != "empty":
            active_skills.append(skill)
    skills_text = "Skills:\n" + "\n".join(f"- {skill}" for skill in active_skills)
    
    equipment_text = f"Equipment: {survivor['equipment']['hand_left']} | {survivor['equipment']['hand_right']}"
    
    inventory = [survivor['equipment'][f'inv_{i}'] for i in range(1, 5)]
    inventory = [item for item in inventory if item != "empty"]
    inventory_text = "Inventory: " + (", ".join(inventory) if inventory else "empty")

    # Position text elements
    ax.text(x + 0.1, y + height - 0.3, name_text, fontweight='bold')
    ax.text(x + 0.1, y + height - 0.6, stats_text)
    ax.text(x + 0.1, y + height - 1.2, skills_text)
    ax.text(x + 0.1, y + 0.6, equipment_text)
    ax.text(x + 0.1, y + 0.3, inventory_text)

def draw_all_survivors(json_path, ax=None, x_offset=0):
    """
    Draws survivor cards in the provided axes with an x offset
    """
    if ax is None:
        fig, ax = plt.subplots()
        
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Scale card dimensions and positions to pixels
    scale = 100
    card_width = 300 / scale  # 300 pixels wide
    card_height = 400 / scale  # 400 pixels high
    spacing = 50 / scale      # 50 pixels between cards
    
    for i, survivor in enumerate(data['survivors']):
        y_pos = (800 - (i * (card_height * scale + spacing))) / scale
        x_pos = x_offset / scale
        draw_survivor_card(ax, survivor, x_pos, y_pos, width=card_width, height=card_height)
    
    ax.set_xlim(-0.5, 20)
    ax.set_ylim(-0.5, 8)
    ax.axis('off')
    plt.show()

if __name__ == "__main__":
    draw_all_survivors("survivors_db.json")