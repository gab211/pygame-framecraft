# frameCraft

A lightweight educational game framework built on top of Pygame.

**frameCraft** is designed for teaching, learning, and beginner-friendly 2D game development. It provides a compact API for scenes, entities, input, collision handling, graphics, and UI while keeping the underlying game logic easy to understand.

The same frameCraft game code can run:

- locally with standard **CPython + Pygame**
- inside **CodeRoom** using its pygame-compatible host runtime

> frameCraft is an independent educational project. It is not affiliated with or maintained by the Pygame project.

## Website

For documentation, educational resources, and more information about frameCraft, visit the official CodeRoom website:

**[frameCraft on CodeRoom](https://www.coderoom.eu/en/framecraft/)**

## Installation

Install frameCraft from PyPI:

```bash
pip install pygame-framecraft
```

Pygame is installed as a package dependency.

Use frameCraft in Python with:

```python
import frameCraft as fc
```

The PyPI distribution is named `pygame-framecraft`, while the Python module intentionally remains `frameCraft`.

## Quick start

```python
import frameCraft as fc

fc.GAME(
    "frameCraft Test",
    window=(640, 400),
    fps=60
)

fc.SCENE("main")

@fc.SCENE_BUILD("main")
def build(ctx):
    fc.ENTITY("player", (320, 200), tag="player")
    fc.RECT("player", 40, 40)

fc.START()
```

Run the program normally:

```bash
python main.py
```

## How frameCraft works

frameCraft provides a small educational layer for structuring Pygame projects.

Typical frameCraft programs consist of:

1. a game configuration
2. one or more scenes
3. entities placed inside those scenes
4. graphics and UI elements
5. input bindings
6. update and game logic

The framework handles the surrounding runtime while the game itself remains regular Python code.

## Standalone and hosted execution

For normal local Python development, start the game with:

```python
fc.START()
```

frameCraft creates and manages the Pygame window and standalone game loop.

For hosted environments such as CodeRoom, the host can retain ownership of the outer game loop through:

```python
FC_BOOT(scene)
FC_STEP(events, dt)
FC_DRAW(screen)
```

Both execution modes use the same frameCraft implementation and game logic.

## Modules

frameCraft currently consists of three modules:

```text
frameCraft.py
frameCraftGFX.py
frameCraftUI.py
```

### `frameCraft`

The core framework, including game configuration, scenes, entities, input, collision handling, and runtime integration.

### `frameCraftGFX`

Additional graphics and geometry functionality.

### `frameCraftUI`

UI and text-related functionality.

## Examples

The repository contains complete example projects in the `examples/` directory.

Current examples include:

```text
examples/
├── breakout/
├── flappy/
├── frogger/
└── space_invaders/
```

Each example can be run with standard Python and Pygame.

For example:

```bash
python examples/breakout/main.py
```

## Educational focus

frameCraft is intentionally designed for educational use.

Its goal is not to replace Pygame or hide Python behind a large engine. Instead, it provides enough structure to let learners focus on game concepts while still working directly with Python.

Typical learning topics include:

- variables and constants
- conditions and loops
- functions
- coordinates and movement
- keyboard input
- scenes and game states
- entities and components
- collision detection
- simple physics
- UI and game feedback
- structuring larger Python projects

Learners can start with small games and gradually work with more of the underlying concepts.

## Compatibility

frameCraft 1.x keeps the established import:

```python
import frameCraft as fc
```

This is intentional and maintains compatibility with existing frameCraft and CodeRoom projects.

The package currently requires Python 3.9 or newer.

## Development

Clone the repository and install the project locally:

```bash
git clone https://github.com/gab211/pygame-framecraft.git
cd pygame-framecraft
python -m pip install -e .
```

You can then run the examples directly:

```bash
python examples/breakout/main.py
```

## Building the package

Install the Python build frontend:

```bash
python -m pip install build
```

Build the source distribution and wheel:

```bash
python -m build
```

The generated packages are written to:

```text
dist/
```

## Project structure

```text
pygame-framecraft/
├── .github/
│   └── workflows/
├── examples/
├── src/
│   ├── frameCraft.py
│   ├── frameCraftGFX.py
│   └── frameCraftUI.py
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── pyproject.toml
└── .gitignore
```

## Versioning

frameCraft uses semantic versioning.

Version numbers follow:

```text
MAJOR.MINOR.PATCH
```

For example:

```text
1.0.0
1.1.0
1.1.1
2.0.0
```

Breaking compatibility changes are reserved for major versions.

## Contributing

Bug reports, improvements, and contributions are welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

frameCraft is released under the MIT License.

See [LICENSE](LICENSE) for details.