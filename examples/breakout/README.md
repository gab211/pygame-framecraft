# Breakout

A complete Breakout-style example built with **frameCraft**.

This standalone version is ported from the final CodeRoom solution and uses the public frameCraft API directly. The German CodeRoom DSL layer has been removed.

All example code, identifiers, comments, state variables and user-facing text are in English.

## What it demonstrates

- game and scene setup
- entities and rectangular colliders
- keyboard controls
- virtual buttons for touch and mouse input
- frame-rate-independent paddle movement with `ctx.dt`
- ball velocity and wall reflection
- paddle-dependent bounce direction
- minimum horizontal ball speed
- block collisions and scoring
- lives
- an invisible death zone
- a latch that prevents repeated life loss across multiple frames
- win and game-over states
- scene restart
- procedural graphics with `frameCraftGFX`
- HUD elements with `frameCraftUI`

## Controls

| Input | Action |
| --- | --- |
| `Left`, `A` | Move paddle left |
| `Right`, `D` | Move paddle right |
| `Space` | Launch ball / restart after game end |
| `Escape` | Stop the game |
| On-screen buttons | Move and launch |

## Goal

Destroy all blocks without losing all three lives.

Each destroyed block awards **10 points**. When the ball leaves the bottom of the playfield, one life is lost and the ball returns to the paddle.

The game is won when all blocks have been destroyed.

## Run

The example expects `frameCraft`, `frameCraftGFX` and `frameCraftUI` to be available in your Python environment.

From the repository root:

```bash
python examples/breakout/main.py
```

On Windows you can also use:

```bash
py examples/breakout/main.py
```

## Files

- `main.py` — complete standalone game
- `README.md` — example description and controls

No external images or assets are required. The paddle, ball and blocks are rendered entirely with frameCraft graphics primitives.
