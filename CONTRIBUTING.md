# Contributing

## Source of truth

The GitHub repository is the development source of truth for frameCraft.

The copies shipped with CodeRoom are generated from released versions and should not be edited independently.

## Runtime source files

The runtime currently consists of:

```text
src/frameCraft.py
src/frameCraftGFX.py
src/frameCraftUI.py
```

Keep changes compatible with both:

- CodeRoom pygame-light hosted mode
- standard CPython + pygame standalone mode

## Compatibility rules

Do not introduce CodeRoom-specific imports into the shared runtime.

The hosted API must remain compatible:

```text
FC_BOOT(...)
FC_STEP(events, dt)
FC_DRAW(screen)
```

Existing educational code using:

```python
import frameCraft as fc
```

should remain compatible unless a future major version explicitly changes the API.
