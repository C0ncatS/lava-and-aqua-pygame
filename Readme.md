# Lava & Aqua – Guide

## 1. Top-Level Flow (`main.py`)
- Sets `SDL_VIDEO_CENTERED` and keeps running while the player wants to play.
- Repeatedly shows the level-selection menu (`MenuUI`). When a level path is returned, it launches the in-game UI (`UserInterface`) for that level.
- After each play session the action from in-game popups decides whether to retry the level, go back to the menu, or exit entirely.

## 2. Levels & Tile Legend (`levels/*.txt`)
- Levels are plain-text grids where each token is separated by spaces. Each row must be equal length so `state.read_level_file` can compute `world_size`.
- Symbols that matter to gameplay:

| Token | Meaning / Asset | Stored In State |
|-------|-----------------|-----------------|
| `.`   | Ground tile     | `ground` backing array |
| `#`   | Wall            | `walls` |
| `I`   | Container/obstacle | `containers` |
| `B`   | Movable block   | `blocks` |
| `U`   | Player spawn    | `players` |
| `A`   | Aqua (water)    | `aquas` |
| `L`   | Lava            | `lavas` |
| `G`   | Goal portal     | `goals` |
| `*`   | Collectible point | `points` |
| `0-9` | Countdown timer (value is duration) | `timers` |

The game enforces “at least one player and one goal per level” during state construction.

## 3. Core State Model (`state.py`)
- `State` owns the parsed level, world dimensions, and every gameplay list (players, liquids, blocks, etc.).
- Movement helpers:
  - `moves` holds the four cardinal `Vector2` directions.
  - `get_possible_moves` filters moves through `can_move`, which checks walls, stones, timers, containers, blocks, and world bounds depending on flags.
- Observer broadcasting:
  - Methods such as `notify_player_moved`, `notify_block_moved`, `notify_lava_touched_aqua`, etc., fan out events to any registered observer (rendering layers, UI).
- Additional logic:
  - `is_goal`, `is_points_empty`, `is_inside` provide quick queries.
  - `copy()` creates a deep copy of the current state for potential rewind/undo features.

## 4. Game Entities (`items.py`)
- `Item` is the shared base (holds `state`, `position`, `tile` sprite offset).
- Specialized subclasses add minimal behavior:
  - `Liquid` and `Block` provide a `speed`.
  - `Player` tracks `status` (`alive`, `dead`, `won`).
  - `Timer` adds a `duration` counter drawn above its tile.

## 5. Command & Simulation Layer (`commands.py`)
- `MoveCommand` executes one player move:
  - Aborts if the player is not alive or target cell is blocked.
  - Pushes a block via `BlockMoveCommand` if the block’s next cell is free.
  - Notifies observers of movement and checks if the goal was reached.
  - Triggers environment updates each turn: `AquaSpreadCommand`, `LavaSpreadCommand`, `TimerCommand`.
- Spreading commands step every liquid outward orthogonally, skipping blocked tiles. When lava and aqua meet they notify the state, allowing other layers to react (e.g., turning into stone).
- `TimerCommand` decrements every timer and removes expired ones.

## 6. Rendering & Observer System (`layers.py`, `observers.py`)
- `StateObserver` defines the callback surface that both UI and rendering layers implement.
- `Layer` hierarchy:
  - `Layer` loads textures/fonts and renders tiles scaled to `cell_size`.
  - `ArrayLayer` pre-renders immutable backgrounds like ground.
  - `UnitLayer` renders dynamic entities each frame.
  - Specialized layers listen for events:
    - `PointLayer` removes collected stars when it hears `player_moved`.
    - `GoalLayer` calls `state.notify_player_won` once all points are picked up and a player steps on the goal.
    - `LiquidLayer` derivatives (`AquaLayer`, `LavaLayer`) remove liquids that evaporate after mixing.
    - `StoneLayer` converts aqua/lava collisions into permanent blocking stones and kills any player occupying that tile.
    - `PlayerLayer`, `DeadLayer`, `TimerLayer`, `BlockLayer`, `ContainerLayer`, `WallLayer`, `GroundLayer` render their corresponding entity lists.
- Because every layer registers itself as an observer (see `UserInterface.__init__`), visual updates automatically track gameplay events without tight coupling.

## 7. In-Game UI Loop (`ui.py`)
- Initializes Pygame, builds the `State`, and creates all layers, popups, and the resizable window sized to `world_size * cell_size`.
- Input handling:
  - Arrow keys / WASD create `MoveCommand`s queued in `self.commands`.
  - **`Z` key triggers undo** to revert the last move.
  - **`U` key triggers redo** to restore a previously undone move.
  - ESC or window close requests exit back to the menu.
  - When a popup is visible, mouse clicks are redirected to its buttons before gameplay resumes.
- Update & render:
  - Before executing commands, the current state is saved to the history manager for undo functionality.
  - Each frame runs the queued commands, clears them, draws every layer, then overlays popups if needed.
  - Observes the state itself to pause the loop and show `GameOverPopup` or `VictoryPopup`.
- Returns `"retry"`, `"menu"`, or `None` to the caller so `main.py` knows what to do next.

## 8. Menu & Popups (`menu.py`, `popup.py`)
- `MenuUI` scans the `levels` directory, sorts files numerically, and lays out `LevelButton`s in a grid. Hover/click states are entirely mouse-driven.
- `GameOverPopup` & `VictoryPopup` share the `PopupButton` component:
  - Draw a translucent overlay, a title, and two buttons (`Retry`, `Menu`).
  - Handle hover via mouse position and return an action when clicked.
  - The victory popup also displays a celebratory subtitle.

## 9. Undo/Redo System (`history.py`)
- Implements the **Memento Pattern** to enable undo/redo functionality without exposing state internals.
- `HistoryManager` maintains two stacks:
  - **Undo stack:** stores previous game states (up to 100 moves)
  - **Redo stack:** stores undone states that can be restored
- Before each move command executes, the current state is saved via `state.copy()`.
- When undoing, the previous state is restored and all layers are updated to reflect it.
- When a new move is made after undo, the redo stack is cleared (standard behavior).
- See `UNDO_REDO_DESIGN.md` for comprehensive design documentation, patterns, and extension guidelines.

## 10. Assets & Dependencies
- Sprites live under `assets/` (ground, timer, lava, aqua, etc.) and fonts under `fonts/` (currently `NotoSans-Bold.ttf` is used everywhere).

## 11. Extending
- **Adding levels:** drop another `.txt` grid into `levels/` and it will appear automatically in the menu.
