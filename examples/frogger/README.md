# Frogger

A complete Frogger-style example built with **frameCraft**.

This standalone example is ported from the `SampleSolutionCode` of the final CodeRoom instruction task. The CodeRoom-specific German DSL and helper layer have been removed, and the example uses the public frameCraft API directly.

All example code, identifiers, comments and user-facing text are in English.

## What it demonstrates

- scene setup and scene state
- keyboard input with `pressed()` and `down()`
- virtual buttons for touch and mouse input
- entities and collision areas
- velocity-based movement
- frame-rate-independent movement with `ctx.dt`
- reusable scene construction helpers
- procedural graphics with `frameCraftGFX`
- HUD elements with `frameCraftUI`
- collision handling
- lives and score
- win and game-over states
- scene restart with an input latch

## Controls

| Input | Action |
| --- | --- |
| `Up`, `W` | Move up |
| `Down`, `S` | Move down |
| `Left`, `A` | Move left |
| `Right`, `D` | Move right |
| `R`, `Enter` | Restart after the game ends |
| On-screen buttons | Movement and restart |

## Goal

Guide the frog from the bottom of the screen to the goal strip at the top.

Cars move across four traffic lanes. A collision costs one life and returns the frog to its starting position. Reaching the goal awards 100 points.

## Run

The example expects `frameCraft`, `frameCraftGFX` and `frameCraftUI` to be available in your Python environment.

From the repository root:

```bash
python examples/frogger/main.py
```

On Windows you can also use:

```bash
py examples/frogger/main.py
```

## Files

- `main.py` — complete standalone game
- `README.md` — example description and controls

No external images or assets are required. The frog, cars, roads and lane markings are created entirely with frameCraft graphics primitives.
