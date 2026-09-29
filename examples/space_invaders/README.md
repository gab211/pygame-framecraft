# Space Invaders

A complete Space-Invaders-style example built with **frameCraft**.

This standalone example is ported from the `SampleSolutionCode` of the final CodeRoom instruction task. The CodeRoom preprocessing wrappers have been removed; the example uses the public frameCraft API directly.

## What it demonstrates

- scenes and scene state
- keyboard input and virtual buttons
- entities, velocities and collision areas
- reusable projectile pool
- enemy formation movement
- collision handlers
- scoring and win/lose states
- reusable explosion effect pool
- frame-time-based animation with `ctx.dt`
- procedural pixel graphics with `frameCraftGFX`
- HUD elements with `frameCraftUI`
- scene restart

## Controls

| Input | Action |
| --- | --- |
| `Left`, `A` | Move left |
| `Right`, `D` | Move right |
| `Space`, `Up`, `W` | Fire |
| `R`, `Enter` | Restart after game over |
| `<`, `>` buttons | Move |
| `F` button | Fire |

## Run

The example expects `frameCraft`, `frameCraftGFX` and `frameCraftUI` to be available in your Python environment.

From the repository root:

```bash
python examples/space_invaders/main.py
```

On Windows you can also use:

```bash
py examples/space_invaders/main.py
```

## Files

- `main.py` — complete standalone game
- `README.md` — example description and controls

No external images or assets are required. The player ship, enemies, projectiles and explosions are drawn entirely with frameCraft graphics primitives.
