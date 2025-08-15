# Zombicide Game - Development Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Systems](#core-systems)
4. [Game Logic](#game-logic)
5. [Data Structures](#data-structures)
6. [Development Progress](#development-progress)
7. [Known Issues & TODOs](#known-issues--todos)
8. [Development Guidelines](#development-guidelines)

---

## Project Overview

### Goal
A digital implementation of the Zombicide board game using Python and Pygame, featuring:
- Turn-based gameplay with survivors and zombies
- Interactive map with zones, walls, and doors
- Comprehensive survivor management (skills, equipment, progression)
- Real-time rendering of game state
- Domain-driven architecture for maintainability and extensibility

### Key Features Implemented
- ✅ Domain-based architecture (vs technical layers)
- ✅ Turn management system with phase progression
- ✅ Interactive survivor cards with skills, weapons, inventory
- ✅ Map rendering with zones, walls, doors
- ✅ Entity system (survivors, zombies)
- ✅ Input handling and event system
- ✅ Configuration management
- ✅ Modular rendering system

---

## Architecture

### Domain-Based Design
The project follows game development best practices by organizing code around **game domains** rather than technical layers:

```
Technical Layers (OLD)     →     Game Domains (NEW)
├── ui/                          ├── systems/
│   ├── rendering/              │   ├── rendering_system.py
│   └── input/                  │   ├── input_system.py
├── core/                       │   ├── game_loop.py
│   ├── entities.py             │   └── configuration_manager.py
│   └── game_logic.py           ├── core/
└── config/                     │   ├── entities.py
    └── display_config.py       │   ├── turn_manager.py
                                │   └── game_setup.py
                                └── main.py
```

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        GameApplication                       │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    GameLoop                             ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    ││
│  │  │ InputSystem │  │RenderingSystem│ │TimingSystem │    ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘    ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    ││
│  │  │GameStateSystem│ │GameWorld    │ │ConfigManager│    ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘    ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## Core Systems

### 1. ConfigurationManager (`systems/configuration_manager.py`)

**Purpose**: Centralized configuration management
- `DisplayConfig`: Window, colors, fonts, layout constants
- `GameConfig`: Turn timing, gameplay constants
- `InputConfig`: Key bindings, mouse settings

**Key Features**:
- Dataclass-based configuration
- Pygame-dependent initialization
- Runtime configuration updates

### 2. RenderingSystem (`systems/rendering_system.py`)

**Purpose**: Domain-focused rendering with specialized renderers

**Components**:
- `MapRenderer`: Handles map, zones, walls, doors
- `EntityRenderer`: Handles survivors and zombies
- `UIRenderer`: Handles HUD, cards, menus
- `RenderingSystem`: Coordinates all renderers

**Survivor Cards Enhancement**:
- Skills based on level progression (blue → yellow → orange → red)
- Weapons in hands (right/left)
- Inventory display (4 slots)
- XP and wounds tracking
- Level color indicator
- Actions remaining

### 3. InputSystem (`systems/input_system.py`)

**Purpose**: Input processing and event generation

**Components**:
- `InputProcessor`: Converts pygame events to game events
- `GameEventHandler`: Processes game-specific events
- `UIEventHandler`: Processes UI-specific events

**Event Types**:
- `QUIT`: Application exit
- `PHASE_ADVANCE`: Manual phase progression
- `PAUSE_TOGGLE`: Game pause/unpause
- `SURVIVOR_ACTION`: Action selection (1, 2, 3)
- `DEBUG_TOGGLE`: Debug mode toggle

### 4. GameLoop (`systems/game_loop.py`)

**Purpose**: Core game loop with systems coordination

**Components**:
- `TimingSystem`: FPS management and delta time
- `GameStateSystem`: Game state updates via turn manager
- `GameActionProcessor`: Processes actions from input events
- `GameWorld`: Encapsulates complete game state
- `GameLoop`: Main coordinator

---

## Game Logic

### Turn Management (`core/turn_manager.py`)

**Turn Flow**:
1. **Survivor Turn**: Each survivor gets 3 actions
2. **Zombie Turn**: Each zombie gets 1 action  
3. **Zombie Spawn**: New zombies appear
4. **Turn End**: Cleanup and next turn

**Phase States**:
- `SURVIVOR_TURN`: Manual control, waiting for input
- `ZOMBIE_TURN`: AI-controlled zombie actions
- `ZOMBIE_SPAWN`: Spawn new zombies
- `TURN_END`: End turn processing

### Entity System (`core/entities.py`)

**Base Entity**:
- ID, name, position
- Actions remaining/max actions
- Alive status

**Survivor**:
- 3 actions per turn
- Wounds (0-2, dies at 2)
- Equipment (hands + 4 inventory slots)
- Skills based on level
- XP and level progression

**Zombie**:
- 1 action per turn
- AI-controlled movement and attack
- Dies in one hit

### Actions System (`core/actions.py`)

**Action Types**:
- `MOVE`: Move to adjacent zone
- `ATTACK`: Attack target in same zone
- `SEARCH`: Search for equipment (TODO)
- `OPEN_DOOR`: Open/close doors (TODO)

---

## Data Structures

### Map Data (`maps_db.json`)
```json
{
  "maps": [{
    "name": "Map 0",
    "tiles": [[{
      "zones": [
        [{
          "features": ["building"],
          "connections": {
            "down": {"type": "wall", "door": true, "opened": false}
          }
        }]
      ]
    }]]
  }]
}
```

### Survivor Data (`survivors_db.json`)
```json
{
  "survivors": [{
    "name": "Eva",
    "level": "blue",
    "wounds": 0,
    "exp": 0,
    "skills": {
      "skill_blue": "+1 to dice roll: ranged",
      "skill_yellow": "+1 action",
      "skill_orange1": "+1 free combat action"
    },
    "equipment": {
      "hand_right": "pistol",
      "hand_left": "iron bar",
      "inv_1": "empty",
      "inv_2": "empty"
    }
  }]
}
```

---

## Development Progress

### ✅ Completed Features

**Architecture Refactoring** (Major milestone):
- Migrated from technical layers to domain-based architecture
- Implemented ConfigurationManager with dataclasses
- Created specialized rendering system (Map, Entity, UI renderers)
- Built comprehensive input system with event handling
- Developed game loop with systems coordination

**Survivor Cards Enhancement**:
- Skills display based on level progression
- Weapons in hands (right/left) display
- Inventory management (4 slots)
- XP and wounds tracking
- Level color indicators
- Actions remaining highlighting
- Card size increased to 350x500px

**Core Game Systems**:
- Turn management with phase progression
- Entity system (survivors, zombies)
- Map rendering with zones, walls, doors
- Input handling (keyboard controls)
- Game state management

### 🔄 Current Status

**Working Systems**:
- Game initializes and runs successfully
- Turn-based gameplay functional
- Survivor cards display comprehensive information
- Map renders correctly with entities
- Input system responds to user actions

**Architecture Benefits Achieved**:
- Highly extensible (easy to add new renderers/systems)
- Domain separation (rendering, input, timing isolated)
- Follows game development best practices
- Maintainable codebase with clear responsibilities

---

## Known Issues & TODOs

### 🐛 Known Issues
1. **Diagnostic Warnings**:
   - Unused imports in `game_application.py` (List, Optional, GameState)
   - Parameter `new_phase` in callback not used

### 🎯 High Priority TODOs

**Gameplay Features**:
- [ ] Equipment system (search for weapons/items)
- [ ] Door opening/closing mechanics
- [ ] Zombie spawning rules
- [ ] Combat system with dice rolls
- [ ] Noise generation system
- [ ] Equipment cards and inventory management

**Map & Environment**:
- [ ] Multiple map support
- [ ] Dynamic door states
- [ ] Zone features (spawn points, objectives)
- [ ] Map editor tool

**UI/UX Improvements**:
- [ ] Mouse input support
- [ ] Sound effects and music
- [ ] Animation system
- [ ] Better visual feedback
- [ ] Settings menu

### 🔧 Technical TODOs

**Code Quality**:
- [ ] Fix diagnostic warnings
- [ ] Add comprehensive unit tests
- [ ] Add type hints everywhere
- [ ] Documentation improvements
- [ ] Error handling improvements

**Performance**:
- [ ] Optimize rendering for larger maps
- [ ] Implement sprite caching
- [ ] Profile and optimize bottlenecks

**Architecture Extensions**:
- [ ] Save/load game system
- [ ] Network multiplayer support
- [ ] Plugin system for custom rules
- [ ] AI difficulty levels

---

## Development Guidelines

### Adding New Features

1. **Follow Domain Architecture**:
   - Place rendering code in appropriate renderer
   - Handle input through InputSystem
   - Manage state through GameWorld
   - Configure through ConfigurationManager

2. **Testing Approach**:
   ```bash
   # Syntax check
   python -m py_compile <file>
   
   # Import test
   python -c "from module import Class; print('✓ Import success')"
   
   # Quick game test
   timeout 3 python main.py
   ```

3. **Code Style**:
   - Use type hints
   - Follow existing naming conventions
   - Add docstrings to public methods
   - Keep methods focused and small

### Working with the Codebase

**Entry Points**:
- `main.py`: Application entry point
- `GameApplication`: Main coordinator
- `GameLoop`: Core game loop
- `RenderingSystem`: All visual output
- `InputSystem`: All user input

**Key Files to Modify**:
- **New renderer**: Add to `UIRenderer`, `MapRenderer`, or `EntityRenderer`
- **New input**: Add to `InputSystem` event handlers
- **New game mechanic**: Extend `TurnManager` or entity classes
- **New configuration**: Add to `ConfigurationManager` dataclasses

### Debugging Tips

1. **Check game state**: Use `app.get_game_info()` for debugging
2. **Monitor events**: Check `InputSystem.get_last_events()`
3. **Verify rendering**: Test individual renderers in isolation
4. **Trace game flow**: Follow turn phase transitions

### Next Developer Onboarding

**To continue development**:
1. Read this document thoroughly
2. Run `python main.py` to see current state
3. Check `TODO` comments in codebase
4. Review recent commits for context
5. Start with small fixes before major features

**Recommended first tasks**:
- Fix diagnostic warnings
- Add equipment search functionality
- Implement door opening mechanics
- Add sound effects

---

## Project Stats

- **Lines of Code**: ~2000+ (estimated)
- **Files**: 15+ Python files
- **Architecture**: Domain-based (refactored from technical layers)
- **Dependencies**: pygame, Python 3.12+
- **Status**: Functional game with enhanced survivor cards
- **Last Major Update**: Domain architecture refactoring + survivor card enhancement

---

*This document is a living reference. Update it as the project evolves.*