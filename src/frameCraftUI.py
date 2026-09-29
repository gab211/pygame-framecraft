# frameCraftUI.py
# Compatible with CodeRoom pygame-light and standard pygame where supported.
# Text overlays + binding for frameCraft.
# Draw order: z (low->high). Supports screen-space and entity-space.

try:
    import pygame
except Exception:
    pygame = None

# ---------------- utils ----------------

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
    if c is None:
        return default
    if _is_list(c) and len(c) >= 3:
        return (_safe_int(c[0]), _safe_int(c[1]), _safe_int(c[2]))
    return default

def _clamp(v, a, b):
    if v < a: return a
    if v > b: return b
    return v

# ---------------- text object ----------------

class TextItem(object):
    __slots__ = (
        "name",
        "space",      # "screen" or "entity"
        "entity",     # entity name if space=="entity"
        "x", "y",     # position (screen px or local entity offset)
        "anchor",     # topleft, top, topright, left, center, right, bottomleft, bottom, bottomright
        "z",
        "text",       # static base text or template
        "bind",       # None or callable(ctx) or string key for ctx.vars
        "fmt",        # callable(value)->string OR format string with {v}
        "visible",
        # style
        "font",
        "size",
        "color",
        "bg",
        "border",
        "border_w",
        "pad",
        "alpha"
    )
    def __init__(self, name):
        self.name = name
        self.space = "screen"
        self.entity = None
        self.x = 0
        self.y = 0
        self.anchor = "topleft"
        self.z = 0
        self.text = ""
        self.bind = None
        self.fmt = None
        self.visible = True
        self.font = None   # None = default
        self.size = 18
        self.color = (255,255,255)
        self.bg = None
        self.border = None
        self.border_w = 1
        self.pad = 4
        self.alpha = 255

# ---------------- registry ----------------

_UI = {
    "items": {},     # name -> TextItem
    "order": []      # names in insertion order (used if z ties)
}

def UI_RESET():
    # call from scene build to clear UI, or from frameCraft reset hook
    _UI["items"] = {}
    _UI["order"] = []

def UI_TEXT(name, x, y, text="", anchor="topleft", z=0, space="screen", entity=None,
            bind=None, fmt=None,
            font=None, size=18, color=(255,255,255),
            bg=None, border=None, border_w=1, pad=4, alpha=255, visible=True):
    """
    Create or update a text item.
    bind:
      - None: uses text as-is
      - string: key in ctx.vars
      - callable(ctx)->value
      - tuple ("var", "punkte") or ("entity", "player", "x") (optional convenience)
    fmt:
      - None: value -> str(value)
      - string with "{v}" placeholder
      - callable(value)->string
    """
    it = _UI["items"].get(name)
    if it is None:
        it = TextItem(name)
        _UI["items"][name] = it
        _UI["order"].append(name)

    it.x = x; it.y = y
    it.text = text
    it.anchor = anchor
    it.z = z
    it.space = space
    it.entity = entity
    it.bind = bind
    it.fmt = fmt
    it.font = font
    it.size = size
    it.color = color
    it.bg = bg
    it.border = border
    it.border_w = border_w
    it.pad = pad
    it.alpha = _clamp(_safe_int(alpha, 255), 0, 255)
    it.visible = bool(visible)
    return it

def UI_HIDE(name, visible=False):
    it = _UI["items"].get(name)
    if it is not None:
        it.visible = bool(visible)

# ---------------- binding resolution ----------------

def _resolve_bind(ctx, bind):
    if bind is None:
        return None, False

    # bind = callable(ctx)
    try:
        if callable(bind):
            return bind(ctx), True
    except Exception:
        pass

    # bind = "punkte" -> ctx.vars["punkte"]
    if isinstance(bind, str) or (hasattr(__builtins__, "basestring") and isinstance(bind, basestring)):
        try:
            return ctx.vars.get(bind), True
        except Exception:
            return None, True

    # bind = ("var", "punkte") OR ("entity","player","x")
    if _is_list(bind) and len(bind) >= 2:
        kind = bind[0]
        if kind == "var":
            try:
                return ctx.vars.get(bind[1]), True
            except Exception:
                return None, True
        if kind == "entity" and len(bind) >= 3:
            try:
                e = ctx.E(bind[1])
                if e is None: return None, True
                return getattr(e, bind[2], None), True
            except Exception:
                return None, True

    return None, False

def _apply_fmt(value, fmt):
    if fmt is None:
        return str(value)
    # fmt = callable(value)
    try:
        if callable(fmt):
            return str(fmt(value))
    except Exception:
        pass
    # fmt = "Score: {v}"
    try:
        if isinstance(fmt, str) or (hasattr(__builtins__, "basestring") and isinstance(fmt, basestring)):
            return fmt.replace("{v}", str(value))
    except Exception:
        pass
    return str(value)

# ---------------- anchor helpers ----------------

def _anchor_pos(anchor, x, y, w, h):
    # returns top-left position for drawing
    if anchor == "topleft":
        return x, y
    if anchor == "top":
        return x - w//2, y
    if anchor == "topright":
        return x - w, y
    if anchor == "left":
        return x, y - h//2
    if anchor == "center":
        return x - w//2, y - h//2
    if anchor == "right":
        return x - w, y - h//2
    if anchor == "bottomleft":
        return x, y - h
    if anchor == "bottom":
        return x - w//2, y - h
    if anchor == "bottomright":
        return x - w, y - h
    return x, y

# ---------------- entity position helpers ----------------

def _entity_center_px(ctx, e):
    ex = _safe_float(getattr(e, "x", 0.0), 0.0)
    ey = _safe_float(getattr(e, "y", 0.0), 0.0)
    if getattr(e, "space", "px") == "tile":
        t = _safe_float(getattr(ctx, "tile", 32.0), 32.0)
        return (ex * t + t/2.0, ey * t + t/2.0)
    return (ex, ey)

# ---------------- draw ----------------

def UI_DRAW(screen, ctx):
    if pygame is None:
        return
    try:
        items = _UI["items"]
        if not items:
            return
    except Exception:
        return

    # sort by z, stable by insertion order
    order = _UI["order"]
    def _k(name):
        it = items.get(name)
        return (_safe_int(getattr(it, "z", 0), 0), order.index(name) if name in order else 999999)

    names = list(order)
    try:
        names.sort(key=_k)
    except Exception:
        pass

    for name in names:
        it = items.get(name)
        if it is None or not it.visible:
            continue

        # build text
        s = it.text
        val, has = _resolve_bind(ctx, it.bind)
        if has:
            s = _apply_fmt(val, it.fmt)

        if s is None:
            continue
        s = str(s)

        # skip empty text (do not draw anything, no bg/border either)
        try:
            if len(s.strip()) == 0:
                continue
        except Exception:
            if len(s) == 0:
                continue

        # load font
        try:
            font = pygame.font.Font(it.font, _safe_int(it.size, 18))
        except Exception:
            try:
                font = pygame.font.Font(None, _safe_int(it.size, 18))
            except Exception:
                continue

        # render text surface
        try:
            surf = font.render(s, 1, _col(it.color))
        except Exception:
            continue

        # apply alpha if supported
        try:
            if it.alpha < 255:
                surf.set_alpha(_safe_int(it.alpha, 255))
        except Exception:
            pass

        tw, th = surf.get_size()
        pad = _safe_int(it.pad, 4)
        box_w = tw + pad*2
        box_h = th + pad*2

        # compute base position
        x = _safe_int(it.x, 0)
        y = _safe_int(it.y, 0)

        if it.space == "entity":
            try:
                e = ctx.E(it.entity)
            except Exception:
                e = None
            if e is not None:
                cx, cy = _entity_center_px(ctx, e)
                x += _safe_int(cx, 0)
                y += _safe_int(cy, 0)

        # anchor box top-left
        bx, by = _anchor_pos(it.anchor, x, y, box_w, box_h)

        # background + border
        if it.bg is not None:
            try:
                r = pygame.Rect(_safe_int(bx), _safe_int(by), box_w, box_h)
                pygame.draw.rect(screen, _col(it.bg), r, 0)
                if it.border is not None:
                    pygame.draw.rect(screen, _col(it.border), r, _safe_int(it.border_w, 1))
            except Exception:
                pass

        # blit text inside box
        try:
            screen.blit(surf, (_safe_int(bx + pad), _safe_int(by + pad)))
        except Exception:
            pass