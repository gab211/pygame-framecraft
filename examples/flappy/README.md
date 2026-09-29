# Flappy Farbenflug

A complete Flappy-style example built with **frameCraft**.

This example is a standalone port of a CodeRoom learning project. It uses the public frameCraft API directly and does not depend on CodeRoom-specific preprocessing or wrapper functions.

## What it demonstrates

- scenes and scene state
- entities and rectangle colliders
- keyboard input and virtual buttons
- frame-based movement
- collision handlers
- procedural graphics with `frameCraftGFX`
- HUD and game-over UI with `frameCraftUI`
- scoring and increasing difficulty
- scene restart

## Controls

| Input | Action |
| --- | --- |
| `Space`, `Up`, `W` | Flap |
| `R`, `Enter` | Restart after Game Over |
| `J` button | Flap |
| `R` button | Restart |

## Run

The example expects `frameCraft`, `frameCraftGFX` and `frameCraftUI` to be available in your Python environment.

From the repository root, run:

```bash
python examples/flappy/main.py
```

On Windows you can also use:

```bash
py examples/flappy/main.py
```

## Files

- `main.py` — complete standalone game
- `README.md` — this description

No external images or other assets are required. The bird, pipes, clouds, sun and background are drawn with frameCraft graphics primitives.
