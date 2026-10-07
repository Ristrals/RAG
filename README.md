*This project has been created as part of the 42 curriculum by juruan, kmalfois*

<div align="center">

![TITLE](assets/readme/TITLE.png)

</div>

# DESCRIPTION

This project is a remake of the classic arcade game **Pac-Man**, written in
Python with the [arcade](https://api.arcade.academy/) library.

The player moves Pac-Man through a maze to eat every pacgum while avoiding the
four ghosts (Blinky, Pinky, Inky and Clyde). Eating a super pacgum makes the
ghosts frightened for a short time, so Pac-Man can eat them for extra points.
A level is cleared when every pacgum is eaten. The game ends when the player
loses all their lives or when the level timer runs out.

Main features:
- **Generated mazes**: mazes are built with the `mazegenerator` package. The
  first level uses the seed from the configuration, so it is always the same;
  the next levels are generated randomly.
- **10 levels**: the game has 10 levels and the maze grows with each one.
  The player wins the game after clearing all 10 levels.
- **JSON configuration**: lives, scores, timer, seed and level sizes are read
  from a configuration file and checked with pydantic.
- **Highscores**: the top 10 scores are saved in a JSON file.
- **Main menu**: start the game, show the highscores, or quit the game.
- **Pause menu** (`P`): resume the game or go back to the main menu.
- **Cheat mode** (`C`): makes the game easier:
  - `I`: invincibility (toggle)
  - `F`: freeze the ghosts (toggle)
  - `N`: skip to the next level
  - `L`: get an extra life

-------------------------------------------------------------------------------
# INSTRUCTIONS

## REQUIREMENTS
- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) (Python package manager)

Dependencies (installed automatically by uv, see `pyproject.toml`):
- `arcade`: game window, drawing and keyboard input
- `pydantic`: configuration validation
- `mazegenerator`: maze generation. This package is provided with the
  project as the local wheel `mazegenerator-2.1.0-py3-none-any.whl`. If
  needed, it can be downloaded again from the project page.

## INSTALLATION
```bash
make install
```
This runs `uv sync`, which creates the `.venv` virtual environment
and installs all the dependencies.

## EXECUTION
```bash
make run
```
or, with any configuration file:
```bash
uv run python3 pac-man.py <config.json>
```
The configuration file is required. The default one is
`data/configuration.json`.

## STANDALONE EXECUTABLE
```bash
make package
```
This step is optional: it is only needed to share the game as a program
that runs on its own. It builds the game with
[PyInstaller](https://pyinstaller.org/) in `dist/pacman/` and creates
`dist/pacman.zip`. The executable can be launched without Python or uv
installed, on the same operating system it was built on. It uses `data/configuration.json` by default.

## CONTROLS
| Key | Action |
|-----|--------|
| Arrow keys | Move Pac-Man / navigate menus |
| `Enter` | Confirm a menu choice |
| `P` | Pause / resume |
| `C` | Toggle cheat mode |
| `Esc` | Quit (from the main menu) |

## MAKEFILE
Makefile commands:
- **make install**: Creates the virtual environment and installs the
  dependencies with `uv sync`.
- **make run**: Runs the game with `data/configuration.json`.
- **make debug**: Runs the game with Python's debugger (`pdb`).
- **make clean**: Removes `__pycache__` and `.mypy_cache` directories.
- **make fclean**: Runs `make clean`, then removes the virtual environment
  (`.venv`).
- **make lint**: Runs flake8 and mypy.
- **make lint-strict**: Runs flake8 and mypy with the `--strict` flag.
- **make f8**: Runs flake8 only.
- **make mp**: Runs mypy only.
- **make package**: Builds a standalone executable with PyInstaller in
  `dist/pacman/` (with `assets` and `data`), and zips it into
  `dist/pacman.zip`.

To launch the game without the Makefile:
```bash
uv run python3 pac-man.py data/configuration.json
```

-------------------------------------------------------------------------------
# RESOURCES
- [Arcade documentation](https://api.arcade.academy/): windows, views,
  drawing, sprites and keyboard input.
- [Pydantic documentation](https://docs.pydantic.dev/): models and
  validators used for the configuration file.

-------------------------------------------------------------------------------
# CONFIGURATION
The game is configured with a JSON file given as the first argument of the
program. The default one is `data/configuration.json`:

```json
{
    "lives": 3,
    "seed": 42,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "level_max_time": 90,
    "highscore_filename": "highscores.json",
    "levels": [
        {"width": 15, "height": 15},
        {"width": 15, "height": 16},
        ...
        {"width": 20, "height": 20}
    ]
}
```

## KEYS AND DEFAULT VALUES
| Key | Type | Default | Valid values | Description |
|-----|------|---------|--------------|-------------|
| `lives` | int | `3` | ≥ 1 | Number of lives at the start of the game. |
| `seed` | int | `42` | ≥ 1 | Seed used to generate the maze of the first level. |
| `pacgum` | int | `42` | ≥ 1 | Number of pacgums placed in each maze. |
| `points_per_pacgum` | int | `10` | ≥ 1 | Points for eating a pacgum. |
| `points_per_super_pacgum` | int | `50` | ≥ 1 | Points for eating a super pacgum. |
| `points_per_ghost` | int | `200` | ≥ 1 | Points for eating a ghost. |
| `level_max_time` | int | `90` | ≥ 1 | Time limit of each level, in seconds. |
| `highscore_filename` | string | `"highscores.json"` | any string | Name of the highscore file, saved in the `data/` directory. |
| `levels` | list | one 15 × 15 level | list of levels | Maze size of each level, in order. |

Each element of `levels` is an object with:

| Key | Type | Default | Valid values | Description |
|-----|------|---------|--------------|-------------|
| `width` | int | `15` | 5 to 25 | Number of columns of the maze. |
| `height` | int | `15` | 5 to 25 | Number of rows of the maze. |

The number of levels of the game is the length of `levels`. The provided
configuration file has 10 levels, from 15 × 15 to 20 × 20.

## ERROR HANDLING
The configuration is loaded with pydantic. The game tries to start whenever
possible:
- **Missing key**: a warning is printed and the default value is used.
- **Invalid value** (wrong type or out of range): a warning is printed and
  the default value is used.
- **Empty or missing `levels`**: one default 15 × 15 level is used.
- **JSON root not an object**: all default values are used.
- **Unknown keys** are ignored.

The program stops with an error message only when the configuration file
cannot be read:
- no file path is given, or the file does not exist;
- the content is not valid JSON.

## COMMENTS
The configuration file may contain comments, which are removed before
parsing:
```
# comment until the end of the line
// comment until the end of the line
/* block comment,
   on several lines */
```
A block comment that is never closed is an error.

-------------------------------------------------------------------------------
# HIGHSCORE

Highscores regroup the entire list of scores performed in the game, they are stored in `data/highscores.json`.\
Note that this file does not exist until a player has registered a score for the first time.

This JSON string respects the following schema:
```json
[
    {
        "name": "Iwatani",
        "score": 1337
    },
    {
        "name": "Pacman",
        "score": 1980
    }
]
```
In case of corrupted JSON string or incorrect entries, the current `highscores.json` will be renamed `highscores-temp.json` and a fresh score file will be created.\
This acts as error mitigation for the program to continue while preventing potential data loss from the original highscores file.

A `highscores_default.json` file is also available. It can be duplicated and renamed `highscores.json` in case the user wants to reinitialize his game's scoreboard.

-------------------------------------------------------------------------------
# MAZE GENERATION
Mazes are generated with the `mazegenerator` package from the A-Maze-ing
project, provided as the local wheel `mazegenerator-2.1.0-py3-none-any.whl`.
It is used in `src/grid/grid_loader.py`.

## USING THE PACKAGE
For each level, the `Grid` class creates a `MazeGenerator` with the level
size from the configuration:

```python
m = MazeGenerator(size=(width, height), perfect=False)
if isinstance(seed, int):
    m.generate(seed=seed)
```

- **`perfect=False`**: a perfect maze has exactly one path between two cells,
  so it is full of dead ends where Pac-Man would be trapped by the ghosts.
  With `perfect=False`, the generator opens extra walls to create loops and
  removes every dead end, which gives a maze that is playable as Pac-Man.
- **Seed**: creating a `MazeGenerator` already generates a random maze. For
  the first level, the maze is generated again with `generate(seed=...)`
  using the `seed` of the configuration, so level 1 is always the same maze.
  The other levels keep the random maze.
- **"42" pattern**: when the maze is big enough (at least 14 × 10), the
  generator draws a "42" in the middle with fully closed cells. These cells
  are drawn in blue and cannot be entered.

## FROM THE GENERATOR TO THE GRID
`m.maze` is a 2D list of integers. Each integer is a 4-bit mask of the walls
around one cell (a set bit means a wall):

| Bit | Value | Wall |
|-----|-------|------|
| 0 | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

For example, `9` (`1 + 8`) is a cell with walls on the north and west sides,
and `15` is a fully closed cell. Each value is converted into a `Cell` object
(`src/grid/cell.py`) with four booleans (`north`, `east`, `south`, `west`)
telling whether Pac-Man and the ghosts can leave the cell in that direction.

## PLACING THE PACGUMS
Once the grid is built, `Grid.place_items()` fills it:
- a **super pacgum** in each of the four corners;
- **pacgums** (`pacgum` in the configuration) on random cells that are
  empty, not closed and not Pac-Man's start cell in the center. If there
  are not enough free cells, the number is reduced and a warning is printed.

-------------------------------------------------------------------------------
# IMPLEMENTATION

## CONFIGURATION LOADING (`src/config.py`)
- The configuration is described by two pydantic models: `GameConfig` for
  the global settings and `LevelConfig` for the size of one level.
- Each field has a `field_validator` in `mode="before"`. It checks the raw
  value before pydantic converts it, and replaces an invalid value by the
  field's default with a warning, instead of raising an error. This way a
  single bad value does not stop the game.
- Before `json.loads`, `strip_comments()` removes `#`, `//` and `/* */`
  comments by reading the text character by character. It keeps track of
  whether it is inside a string, so a `#` inside a string is kept. Newlines
  inside block comments are kept, so JSON error line numbers still match the
  original file.
- Errors that make the file unreadable raise a custom `ParsingError`, which
  is caught in `__main__.py` to print the message and exit.

## GRID (`src/grid/`)
- `Grid` (`grid_loader.py`) wraps the `mazegenerator` package: it generates
  the maze and converts each wall value into a `Cell` (see
  [MAZE GENERATION](#maze-generation)).
- `Cell` (`cell.py`) is a dataclass with its position, four booleans for the
  open sides and its content (`EMPTY`, `PACGUM` or `SUPER_PACGUM`).
  `can_exit(direction)` tells whether an entity can leave the cell in a
  direction; it is the only wall check the entities need.
- `Grid` also provides:
  - `get_cell(y, x)`: returns a cell, with coordinates clamped to the grid
    so it never goes out of range;
  - `place_items()`: places the super pacgums and pacgums;
  - `get_center_position()`: the start cell of Pac-Man, in the gap between the "4" and the "2";
  - `is_all_empty()`: used by the game loop to know when a level is cleared.

## MENUS AND INTERFACE (`src/main_menu.py`, `src/end_view.py`, `src/game_view.py`)
Each screen is an arcade `View`, and screens are changed with
`window.show_view()`:

```
MainMenuView ──Start──> GameView ──win / game over──> EndView ──Enter──> MainMenuView
                           │
                           └──pause menu: Main menu──> MainMenuView
```

The window is created in `__main__.py` at 85% of the screen size. In every
menu, the selected option is stored as an index, highlighted in blue with a
`>` in front, and confirmed with Enter.

**Main menu (`MainMenuView`)**
- Shows the title, the top 10 highscores in two columns of five (empty
  slots show `---`), the `Start` / `Exit` options (chosen with Left / Right)
  and a bottom bar with the controls.
- The highscores are read with the `ScoreManager`. If the highscore file
  cannot be opened, the error is printed and the menu is shown without
  highscores.
- `Start` creates a new `GameView`. If the game cannot start, the error is
  printed and the menu stays open.

**End screen (`EndView`)**
- Shown after a victory (`YOU WIN!!`, in green) or a game over
  (`GAME OVER...`, in orange), with the final score.
- The player types a name in an input box: letters, digits and spaces, up
  to 10 characters, uppercase with Shift, Backspace to delete.
- Enter saves the name and score in the highscore file (only if the name
  has at least 3 characters) and goes back to the main menu.

**HUD** (`GameView.draw_hud`, `GameView.draw_page`)
- At the top: the lives (one heart per life), the level, the score and the
  timer (rounded down to whole seconds).
- At the bottom: an orange bar recalling the controls (arrows, `P`, `C`).

**Pause menu and cheat panel**
- They are not separate views: `GameView` draws them over the game as a
  semi-transparent black layer, controlled by the `pause` and `cheat_mode`
  flags. While one of them is open, `on_update()` does nothing, so the game
  is frozen.
- **Pause** (`P`): `RESUME` / `MAIN MENU`, chosen with Up / Down.
- **Cheat panel** (`C`): shows each cheat with its key and its current
  state (`ON` / `OFF`, number of lives):
  - `I` invincibility: sets `is_invincible` on Pac-Man, so the ghosts
    cannot catch him;
  - `F` freeze: sets `ghost_freeze` in the `EntityManager`, so the ghosts
    stop moving;
  - `N` skip level: calls `next_level()` (not available on the last level);
  - `L` extra life: adds one life.
- The invincibility and freeze states are kept when a new level is loaded.

## GAME LOOP (`src/game_view.py`)
arcade calls `on_key_press()`, `on_update()` and `on_draw()` on the current
view.

**Input (`on_key_press`)** is handled by priority: first the pause menu,
then the cheat panel, then the movement. A key used by a menu is not
passed to Pac-Man. An arrow key stores the next direction in Pac-Man's
`buffered_direction` and starts the game.

**Update (`on_update`)**, once per frame:
1. Nothing happens while the game is paused, the cheat panel is open, or
   the player has not pressed an arrow key yet.
2. The frame time is capped at 1/30 s, so a lag spike cannot move an entity
   through a wall or past a collision.
3. The timer goes down and the entities are updated by the `EntityManager`,
   which returns a summary of the frame (pacgum eaten, ghosts eaten, Pac-Man
   caught).
4. The game view adds the points from the summary and handles the result: a
   lost life (positions reset, wait for a key), game over, level cleared
   (next level or victory), or time out.

**Drawing (`on_draw`)** draws the maze, the pacgums, the sprites, the HUD
and the bottom bar, then the pause menu or cheat panel on top.
- The maze takes at most 60% of the window, with square cells, and is
  centered. The cell size and offsets are computed in
  `calculate_render_params()` and recomputed in `on_resize()`, so the game
  follows the window size.
- The grid counts rows from the top, but arcade counts y from the bottom,
  so the row index is flipped when converting a cell to screen coordinates.
- Walls are drawn as lines on the closed sides of each cell, and the cells
  of the "42" are filled in blue.

**Levels**: `load_level()` builds a new `Grid` and a new `EntityManager` for
the current level and resets the timer. The score, lives and cheat states
are kept from one level to the next.

-------------------------------------------------------------------------------
# GENERAL SOFTWARE ARCHITECTURE

## FILE TREE
```
pacman/
├── pac-man.py                  # Launcher: python3 pac-man.py <config.json>
├── Makefile                    # install, run, lint, package...
├── pyproject.toml              # Dependencies for uv
├── uv.lock                     # Locked dependency versions
├── mazegenerator-2.1.0-...whl  # A-Maze-ing maze generator package
├── mypy.ini / .flake8          # Lint settings
│
├── assets/                         
│   ├── sprites/                # Sprite images    
│   │   ├── pacman/             #   Pac-Man: 3 frames per direction
│   │   ├── blinky/ pinky/      #   Ghosts: 2 frames per direction,
│   │   ├── inky/ clyde/        #   frightened, sleep and wake frames
│   │   └── eyes/               #   Eaten ghost (eyes only)
│   │
│   └── readme/                 # README.md assets            
│
├── data/
│   ├── configuration.json      # Default game configuration
│   ├── highscores.json         # Saved highscores (created at runtime)
│   └── highscores_default.json # Default highscore list
│
└── src/
    ├── __main__.py             # Entry point: loads the config, opens the window
    ├── config.py               # Config models (pydantic) and loader
    ├── error.py                # Custom exceptions
    ├── data_lib.py             # Shared enums (Movements, colors)
    │
    ├── main_menu.py            # View: main menu + highscores
    ├── game_view.py            # View: game loop, HUD, pause, cheat mode
    ├── end_view.py             # View: victory / game over, name input
    │
    ├── grid/
    │   ├── grid_loader.py      # Grid: maze generation, pacgum placement
    │   └── cell.py             # Cell: walls and content of one cell
    │
    ├── entity_manager.py       # Updates all entities, collisions, score events
    ├── entity/
    │   ├── token.py            # Base class of every moving entity
    │   ├── pacman.py           # Pac-Man
    │   ├── ghost.py            # Base ghost: states and movement
    │   └── blinky.py pinky.py  # The four ghosts and their targets
    │       inky.py clyde.py
    │
    ├── sprite_manager.py       # Loads textures for each entity and state
    └── score.py                # Highscore file: read, sort, save
```

## HOW THE MODULES WORK TOGETHER
```
                         pac-man.py
                             │
                             ▼
                        __main__.py ─────────► config.py ──► data/configuration.json
                             │
                             ▼
   ┌───────────────► main_menu.py ─────────────► score.py ──► data/highscores.json
   │                         │ Start                 ▲
   │                         ▼                       │
   │                   game_view.py                  │
   │          ┌──────────┬───┴───────┬──────────┐    │
   │          ▼          ▼           ▼          ▼    │
   │     grid_loader  entity_     sprite_   end_view.py
   │          │       manager     manager      │
   │          ▼          │                     │ Enter
   │   mazegenerator     ▼                     │
   │      + cell.py   entity/                  │
   │                (Pac-Man, ghosts)          │
   └───────────────────────────────────────────┘
```

- **Views** (`main_menu`, `game_view`, `end_view`) are the arcade screens.
  Only one is shown at a time.
- **`game_view`** is the center of the game. Each level, it creates a `Grid`
  and an `EntityManager`, then on each frame it updates them and draws the
  result with the textures of the `SpriteManager`.
- **`grid`** knows the maze (walls and pacgums), **`entity`** knows how
  Pac-Man and the ghosts move in it, and **`entity_manager`** connects them
  (movements, collisions, points).
- **`score`** is used by the main menu (to show the highscores) and by the
  end screen (to save a new score).

-------------------------------------------------------------------------------
# TOKENS


Tokens are the entity that represents Pacman and the Ghosts.

This class manages tools and attributes required by all tokens for pacman and ghosts to inherit. This includes the reset position method, cell center detection and various info recovery properties for coordinates and states.

## PACMAN
Unlike ghosts, pacman’s movements are managed by the player.\
To do so, the Game Loop will listen for user inputs and pass them to Pacman's entity, which will then respond if the situation allows it.

Pacman also possesses a specific *is_invincible* attribute in case the respective cheat mode is activated.\
If turned on, collision detection between Pacman and ghosts will not result in defeat, yet he will still be able to feast on enemies if they're frightened.

## GHOSTS

### MOVEMENT
Ghosts possess a different movement system, following a distance based algorithm.

Regarding their current position, they will always choose a direction that brings them closer to their targeted location, except if eaten.\
This allows the player to toy around with their behavior if they can figure it out, but be careful not to take our little wraiths lightly either.

During the EATEN state, Ghosts will instead refer to a classic BFS model, to ensure they'll reach their spawn tile no matter the distance and maze layout.

### STATES
Ghosts refers to their behavior by using a state system:
- **SCATTER**: Returns them toward their spawn point
- **CHASE**: Chase their target tile
- **FRIGHTENED**: Immediate 180% then follow random directions
- **EATEN**: Use BFS to return to spawn, then wait 5s before switching to chase or scatter

In a regular game loop, respectively to the old Arcade Game, ghosts will alternate between 5s of SCATTER and 20s to CHASE states.\
This allows the player to have some breathing room instead of being chased relentlessly the whole game.

-------------------------------------------------------------------------------
# GHOST BEHAVIOR

## Algorithms
Ghost behavior defines their targeted tile regarding their current state.\
As mentioned, all states use the classic distance based method except the EATEN state (BFS)

## Ghosts
The true difference between ghosts comes from their CHASE tile targeting. Each one has a different way to calculate their destination to challenge the player during a party.

### Blinky
Blinky, the red ghost, is the most simple and direct.\
He will aim straight for Pacman's immediate location, being an active threat for the player no matter where they are.

![Blinky_behavior](assets/readme/Blinky_behavior.png)

### Inky
Inky, the cyan ghost, is goofy and cunning.\
His role is the flanker, he calculates his destination by referring to Blinky's position relative to Pacman's, and then offsetting it by 2 tiles relative to Pacman's direction. This way he's always around the corner for a pincer attack with his red leader.

![Inky_behavior](assets/readme/Inky_behavior.png)

### Pinky
Pinky, the fuchsia ghost, is adorably mischievous.\
Her favourite job his to anticipate Pacman's path to cut him out. To do so she will always target 4 tiles ahead of pacman's current direction.

![Pinky_behavior](assets/readme/Pinky_behavior.png)

### Clyde
Clyde, the orange ghost, is lazy and brainless... or is he?\
He refers to a specific behavior, chase Pacman if he is more than 8 tiles away, or flee from him and return to his spawn point if he's closer than 8 tiles.\
Following this guideline, Clyde will gravitate around Pacman, and, in some cases, become wildly unpredictible when he decides to flee the player from certain angles.

![Clyde_behavior](assets/readme/Clyde_behavior.png)

-------------------------------------------------------------------------------
# PROJECT MANAGEMENT
### Project organization:

Project hosted on GitHub central repository: https://github.com/Ristrals/PAC-MAN \
Project organization was managed using a Kanban setup.

### Task distribution:

**Jun Ruan**:
- Configuration parsing and error handling
- Arcade Game View development
- Arcade Game Loop development
- Cheat modes and graphic interface integration
- Maze generator integration

**Malfois Kevin**:
- Highscore parsing and error handling
- Token movement system and collision detection
- Ghosts Behavior algorithms
- Graphic assets

-------------------------------------------------------------------------------
# CONCLUSION
LOL

