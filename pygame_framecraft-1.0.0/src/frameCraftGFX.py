# frameCraftGFX.py
# Geometry rendering helper for frameCraft.
# Compatible with CodeRoom pygame-light and standard pygame where supported.
# Usage: attach specs to e.data["gfx"] = [ ... parts ... ]
# Then call draw_entity(screen, ctx, e) from frameCraft render loop.

try:
    import pygame
except Exception:
    pygame = None

# ---------- small utils ----------

def _is_list(x):
    return isinstance(x, (list, tuple))

def _safe_int(x, d=0):
    try:
        return int(x)
    except Exception:
        return d

def _safe_float(x, d=0.0):
    try:
        return float(x)
    except Exception:
        return float(d)

def _col(c, default=(255,255,255)):
    # Accept (r,g,b) or (r,g,b,a) -> use rgb
    if c is None:
        return default
    if _is_list(c) and len(c) >= 3:
        return (_safe_int(c[0]), _safe_int(c[1]), _safe_int(c[2]))
    return default

def _sort_z(parts):
    # parts: list of dicts with optional 'z'
    try:
        return sorted(parts, key=lambda p: _safe_int(p.get("z", 0)))
    except Exception:
        return parts

# ---------- coordinate model ----------
# Local coords are relative to entity center by default.
# If part has 'anchor': 'topleft', local coords are relative to entity top-left.

def _entity_center_px(ctx, e):
    # replicate frameCraft behavior: e.x/e.y are treated as center in px space.
    # (In frameCraft, sprite_center True uses center; rect fallback uses AABB based on center)
    ex = _safe_float(getattr(e, "x", 0.0), 0.0)
    ey = _safe_float(getattr(e, "y", 0.0), 0.0)
    # tile-space support (optional)
    if getattr(e, "space", "px") == "tile":
        t = _safe_float(getattr(ctx, "tile", 32.0), 32.0)
        return (ex * t + t/2.0, ey * t + t/2.0)
    return (ex, ey)

def _entity_topleft_px(ctx, e):
    cx, cy = _entity_center_px(ctx, e)
    w = _safe_float(getattr(e, "w", 0.0), 0.0)
    h = _safe_float(getattr(e, "h", 0.0), 0.0)
    return (cx - w/2.0, cy - h/2.0)

def _apply_anchor(ctx, e, part, cx, cy):
    anchor = part.get("anchor", "center")
    if anchor == "topleft":
        tx, ty = _entity_topleft_px(ctx, e)
        return (tx, ty)
    # default: center
    return (cx, cy)

# ---------- shape constructors (AI-friendly) ----------
# Each returns a dict part spec.

def P_RECT(x, y, w, h, fill=(255,255,255), outline=None, width=1, z=0, anchor="center"):
    return {"t":"rect","x":x,"y":y,"w":w,"h":h,"fill":fill,"outline":outline,"width":width,"z":z,"anchor":anchor}

def P_CIRCLE(x, y, r, fill=(255,255,255), outline=None, width=1, z=0, anchor="center"):
    return {"t":"circle","x":x,"y":y,"r":r,"fill":fill,"outline":outline,"width":width,"z":z,"anchor":anchor}

def P_POLY(points, fill=(255,255,255), outline=None, width=1, z=0, anchor="center"):
    # points: [(x,y), ...] local coords
    return {"t":"poly","pts":points,"fill":fill,"outline":outline,"width":width,"z":z,"anchor":anchor}

def P_LINE(x1, y1, x2, y2, color=(255,255,255), width=2, z=0, anchor="center"):
    return {"t":"line","x1":x1,"y1":y1,"x2":x2,"y2":y2,"color":color,"width":width,"z":z,"anchor":anchor}

def P_TEXT(x, y, text, size=18, color=(255,255,255), z=0, anchor="center"):
    return {"t":"text","x":x,"y":y,"text":text,"size":size,"color":color,"z":z,"anchor":anchor}

# ---------- attach helpers ----------

def set_gfx(e, parts):
    # parts: list of dict specs
    if not hasattr(e, "data") or e.data is None:
        try:
            e.data = {}
        except Exception:
            return
    e.data["gfx"] = parts

def add_gfx(e, part):
    if not hasattr(e, "data") or e.data is None:
        try:
            e.data = {}
        except Exception:
            return
    if "gfx" not in e.data or e.data["gfx"] is None:
        e.data["gfx"] = []
    e.data["gfx"].append(part)

# ---------- draw ----------

def draw_entity(screen, ctx, e):
    if pygame is None:
        return
    if not hasattr(e, "data") or not e.data:
        return
    parts = e.data.get("gfx")
    if not parts:
        return

    cx, cy = _entity_center_px(ctx, e)

    for p in _sort_z(parts):
        t = p.get("t")
        base_x, base_y = _apply_anchor(ctx, e, p, cx, cy)

        if t == "rect":
            x = _safe_float(p.get("x", 0.0), 0.0) + base_x
            y = _safe_float(p.get("y", 0.0), 0.0) + base_y
            w = _safe_float(p.get("w", 0.0), 0.0)
            h = _safe_float(p.get("h", 0.0), 0.0)
            r = pygame.Rect(_safe_int(x), _safe_int(y), _safe_int(w), _safe_int(h))
            fill = p.get("fill", None)
            outline = p.get("outline", None)
            width = _safe_int(p.get("width", 1), 1)
            if fill is not None:
                pygame.draw.rect(screen, _col(fill), r, 0)
            if outline is not None:
                pygame.draw.rect(screen, _col(outline), r, width)

        elif t == "circle":
            x = _safe_float(p.get("x", 0.0), 0.0) + base_x
            y = _safe_float(p.get("y", 0.0), 0.0) + base_y
            rr = _safe_int(p.get("r", 5), 5)
            fill = p.get("fill", None)
            outline = p.get("outline", None)
            width = _safe_int(p.get("width", 1), 1)
            if fill is not None:
                pygame.draw.circle(screen, _col(fill), (_safe_int(x), _safe_int(y)), rr, 0)
            if outline is not None:
                pygame.draw.circle(screen, _col(outline), (_safe_int(x), _safe_int(y)), rr, width)

        elif t == "poly":
            pts = p.get("pts", [])
            out = []
            for q in pts:
                if not _is_list(q) or len(q) < 2:
                    continue
                px = _safe_float(q[0], 0.0) + base_x
                py = _safe_float(q[1], 0.0) + base_y
                out.append((_safe_int(px), _safe_int(py)))
            if len(out) >= 3:
                fill = p.get("fill", None)
                outline = p.get("outline", None)
                width = _safe_int(p.get("width", 1), 1)
                if fill is not None:
                    pygame.draw.polygon(screen, _col(fill), out, 0)
                if outline is not None:
                    pygame.draw.polygon(screen, _col(outline), out, width)

        elif t == "line":
            x1 = _safe_float(p.get("x1", 0.0), 0.0) + base_x
            y1 = _safe_float(p.get("y1", 0.0), 0.0) + base_y
            x2 = _safe_float(p.get("x2", 0.0), 0.0) + base_x
            y2 = _safe_float(p.get("y2", 0.0), 0.0) + base_y
            color = _col(p.get("color", (255,255,255)))
            width = _safe_int(p.get("width", 2), 2)
            pygame.draw.line(screen, color, (_safe_int(x1), _safe_int(y1)), (_safe_int(x2), _safe_int(y2)), width)

        elif t == "text":
            # Text is optional; if font fails in Skulpt env it should silently no-op.
            try:
                x = _safe_float(p.get("x", 0.0), 0.0) + base_x
                y = _safe_float(p.get("y", 0.0), 0.0) + base_y
                txt = p.get("text", "")
                size = _safe_int(p.get("size", 18), 18)
                color = _col(p.get("color", (255,255,255)))
                font = pygame.font.Font(None, size)
                surf = font.render(str(txt), 1, color)
                screen.blit(surf, (_safe_int(x), _safe_int(y)))
            except Exception:
                pass