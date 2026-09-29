"""
frameCraft 

A lightweight educational game framework using a pygame-compatible API.

frameCraft can run in two modes:

1. Hosted mode:
   A host such as CodeRoom pygame-light owns the main loop and calls
   FC_BOOT(), FC_STEP(events, dt), and FC_DRAW(screen).

2. Standalone mode:
   Standard CPython + pygame can run the same game code through START().

The public game DSL is shared between both environments. Support for individual
pygame features and asset formats may vary by host.
"""

# Python 2 / 3 compatibility
try:
    basestring
except NameError:
    basestring = str

try:
    import pygame
except Exception:
    pygame = None

try:
    import frameCraftGFX as gfx
except Exception:
    gfx = None

try:
    import frameCraftUI as ui
except Exception:
    ui = None

# ------------------------
# Utilities
# ------------------------

def _clamp(v, a, b):
    if v < a: return a
    if v > b: return b
    return v

def _is_list(x):
    return isinstance(x, (list, tuple))

def _lower(s):
    try:
        return s.lower()
    except Exception:
        return s

def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default

def _safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return float(default)

def _dbg(msg):
    # möglichst harmlos: print nur kurz
    try:
        print("[frameCraft][DBG] " + str(msg))
    except Exception:
        pass

# ------------------------
# Data Structures
# ------------------------

class Entity(object):
    __slots__ = (
        "name","tag",
        "x","y","vx","vy",
        "w","h",
        "alive",
        "solid","trigger",
        "sprite","sprite_center",
        "space",      # "px" or "tile"
        "grid_cd","grid_t",
        "data"
    )

    def __init__(self, name, x=0, y=0, tag=""):
        self.name = name
        self.tag = tag
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.w = 0
        self.h = 0
        self.alive = True
        self.solid = False
        self.trigger = False
        self.sprite = None
        self.sprite_center = True
        self.space = "px"
        self.grid_cd = 0.12
        self.grid_t = 0.0
        self.data = {}


class Zone(object):
    __slots__ = ("name","rect","tag","trigger")
    def __init__(self, name, rect, tag, trigger):
        self.name = name
        self.rect = rect
        self.tag = tag
        self.trigger = trigger


class VirtualButton(object):
    __slots__ = ("name","action","rect","label","style","visible","is_down")
    def __init__(self, name, action, rect, label, style=None, visible=True):
        self.name = name
        self.action = action
        self.rect = rect
        self.label = label
        self.style = style or {}
        self.visible = visible
        self.is_down = False


class TimerEvent(object):
    __slots__ = ("every","t","fn")
    def __init__(self, every, fn):
        self.every = float(every)
        self.t = 0.0
        self.fn = fn


class GridBoard(object):
    def __init__(self, w, h, default=0):
        self.w = int(w)
        self.h = int(h)
        self.default = default
        self.cells = [[default for _ in range(self.w)] for __ in range(self.h)]

    def in_bounds(self, x, y):
        return (0 <= x < self.w) and (0 <= y < self.h)

    def get(self, x, y, default=None):
        if default is None: default = self.default
        if not self.in_bounds(x,y): return default
        return self.cells[y][x]

    def set(self, x, y, v):
        if self.in_bounds(x,y):
            self.cells[y][x] = v

    def fill(self, v):
        for y in range(self.h):
            row = self.cells[y]
            for x in range(self.w):
                row[x] = v


# ------------------------
# Context (runtime state)
# ------------------------

class FrameCraftContext(object):
    def __init__(self):
        # config
        self.title = "frameCraft"
        self.window = (800,600)
        self.fps = 60
        self.tile = 32
        self.bg = (16,16,16)
        self.debug = False
        self.asset_resolver = None

        # runtime
        self.scene = "main"
        self.vars = {}      # arbitrary user state variables
        self.time = 0.0
        self.dt = 0.016
        self.running = True

        # world
        self.entities = {}  # name -> Entity
        self.tags = {}      # tag -> set(names)
        self.zones = {}     # name -> Zone
        self.rules = []     # fn(ctx)
        self.collisions = []# (tagA, tagB, handler)
        self.timers = []    # TimerEvent
        self.boards = {}    # name -> GridBoard
        self.vbuttons = []  # VirtualButton
        self.fn = {}        # name->callable

        # input bindings
        self.bindings = {}      # action -> [keynames]
        self._keys_down = set() # keyname strings down
        self._actions_down = set()
        self._actions_edge = set()

        # pointer state (touch/mouse)
        self.pointer_down = False
        self.pointer_pos = (0,0)

        # internal asset cache
        self._img = {}

    # ---- entity access ----
    def E(self, name):
        return self.entities.get(name)

    def all_tag(self, tag):
        out = []
        names = self.tags.get(tag, set())
        for n in names:
            e = self.entities.get(n)
            if e and e.alive:
                out.append(e)
        return out

    def _add_entity(self, e):
        self.entities[e.name] = e
        if e.tag:
            if e.tag not in self.tags:
                self.tags[e.tag] = set()
            self.tags[e.tag].add(e.name)

    def _remove_entity(self, name):
        e = self.entities.get(name)
        if not e: return
        e.alive = False
        if e.tag and e.tag in self.tags and name in self.tags[e.tag]:
            self.tags[e.tag].remove(name)
        if name in self.entities:
            del self.entities[name]

    # ---- input API (for game code) ----
    def down(self, action):
        return action in self._actions_down

    def pressed(self, action):
        return action in self._actions_edge

    # ---- coords/collisions ----
    def _to_px_center(self, e):
        # Defensive: x/y müssen Zahlen sein
        ex = _safe_float(getattr(e, "x", 0.0), 0.0)
        ey = _safe_float(getattr(e, "y", 0.0), 0.0)

        if e.space == "tile":
            t = _safe_float(self.tile, 32.0)
            return (ex * t + t/2.0, ey * t + t/2.0)

        return (ex, ey)

    def _aabb_px(self, e):
        cx, cy = self._to_px_center(e)

        ew = _safe_float(getattr(e, "w", 0.0), 0.0)
        eh = _safe_float(getattr(e, "h", 0.0), 0.0)

        ## Wenn das hier auffällig ist, loggen wir EINMAL pro Call
        #if ew <= 0 or eh <= 0:
        #    _dbg("AABB warn: entity=%s tag=%s w=%s h=%s x=%s y=%s space=%s" % (
        #        getattr(e, "name", "?"),
        #        getattr(e, "tag", ""),
        #        str(getattr(e, "w", None)),
        #        str(getattr(e, "h", None)),
        #        str(getattr(e, "x", None)),
        #        str(getattr(e, "y", None)),
        #        str(getattr(e, "space", None))
        #    ))

        try:
            return pygame.Rect(int(cx - ew/2.0), int(cy - eh/2.0), int(ew), int(eh))
        except Exception as ex:
            _dbg("AABB ERROR: %s entity=%s x=%s y=%s w=%s h=%s cx=%s cy=%s space=%s" % (
                str(ex),
                getattr(e, "name", "?"),
                str(getattr(e, "x", None)),
                str(getattr(e, "y", None)),
                str(getattr(e, "w", None)),
                str(getattr(e, "h", None)),
                str(cx), str(cy),
                str(getattr(e, "space", None))
            ))
            # super safe fallback rect
            return pygame.Rect(0, 0, 1, 1)

    def _collide(self, a, b):
        return self._aabb_px(a).colliderect(self._aabb_px(b))

    def in_zone(self, ent_name, zone_name):
        e = self.E(ent_name)
        z = self.zones.get(zone_name)
        if not e or not z: return False
        px, py = self._to_px_center(e)
        return z.rect.collidepoint(int(px), int(py))

    # ---- helpers exposed to game code ----
    def grid_step(self, ent_name, dx, dy):
        e = self.E(ent_name)
        if not e: return
        if e.grid_t > 0.0: return
        e.x += dx
        e.y += dy
        e.grid_t = e.grid_cd

    def bounce(self, a, b):
        ax, ay = self._to_px_center(a)
        bx, by = self._to_px_center(b)
        dx = ax - bx
        dy = ay - by
        if abs(dx) > abs(dy):
            a.vx = -a.vx
        else:
            a.vy = -a.vy

    def bounce_walls(self, e, top=True, left=True, right=True, bottom=False):
        # px space only, common for Pong/Breakout
        if e.space != "px":
            return
        halfw = e.w/2.0
        halfh = e.h/2.0
        if left and e.x < halfw:
            e.x = halfw
            e.vx = abs(e.vx)
        if right and e.x > self.window[0] - halfw:
            e.x = self.window[0] - halfw
            e.vx = -abs(e.vx)
        if top and e.y < halfh:
            e.y = halfh
            e.vy = abs(e.vy)
        if bottom and e.y > self.window[1] - halfh:
            e.y = self.window[1] - halfh
            e.vy = -abs(e.vy)

    # ---- assets / draw ----
    def _resolve_asset(self, spec):
        if self.asset_resolver is not None:
            try:
                return self.asset_resolver(spec)
            except Exception:
                return spec
        return spec

    def _load_image(self, spec):
        if spec is None:
            return None

        if _is_list(spec):
            try:
                cache_key = str(spec)
            except Exception:
                cache_key = spec[0]

            if cache_key in self._img:
                return self._img[cache_key]

            try:
                image_spec = spec[0]
                rect_spec = spec[1] if len(spec) > 1 else None
                size_spec = spec[2] if len(spec) > 2 else None
                flip_spec = spec[3] if len(spec) > 3 else None

                img = pygame.image.load(self._resolve_asset(image_spec))

                if rect_spec is not None:
                    img = img.subsurface(rect_spec)

                if size_spec is not None:
                    try:
                        if hasattr(pygame, "transform") and hasattr(pygame.transform, "scale"):
                            img = pygame.transform.scale(img, (int(size_spec[0]), int(size_spec[1])))
                    except Exception:
                        pass

                if flip_spec is not None:
                    try:
                        flip_x = bool(flip_spec[0])
                        flip_y = bool(flip_spec[1])
                        if (flip_x or flip_y) and hasattr(pygame, "transform") and hasattr(pygame.transform, "flip"):
                            flipped = pygame.transform.flip(img, flip_x, flip_y)
                            if flipped is not None:
                                img = flipped
                    except Exception:
                        pass

            except Exception:
                img = None

            # Wichtig: fehlgeschlagene URL-/Atlas-Ladevorgänge nicht dauerhaft cachen.
            if img is not None:
                self._img[cache_key] = img

            return img

        if spec in self._img:
            return self._img[spec]

        try:
            img = pygame.image.load(self._resolve_asset(spec))
        except Exception:
            img = None

        # Wichtig: None nicht cachen, damit ein späterer Versuch möglich bleibt.
        if img is not None:
            self._img[spec] = img

        return img

    def _draw_text(self, screen, text, x, y, size=18, color=(235,235,235)):
        try:
            font = pygame.font.Font(None, int(size))
            surf = font.render(str(text), 1, color)
            screen.blit(surf, (int(x), int(y)))
        except Exception:
            pass


# ------------------------
# Module-level singleton state
# ------------------------

_CTX = FrameCraftContext()
_SCENES = {}          # scene_name -> build_fn
_ACTIVE_SCENE = None  # name currently built


def _fc_reset_runtime(ctx):
    # Keep config; reset runtime containers
    ctx.time = 0.0
    ctx.dt = 0.016
    ctx.running = True

    ctx.entities = {}
    ctx.tags = {}
    ctx.zones = {}
    ctx.rules = []
    ctx.collisions = []
    ctx.timers = []
    ctx.boards = {}
    ctx.vbuttons = []
    ctx.fn = {}

    ctx.bindings = {}
    ctx._keys_down = set()
    ctx._actions_down = set()
    ctx._actions_edge = set()

    ctx.pointer_down = False
    ctx.pointer_pos = (0,0)

    if ui is not None:
        try: ui.UI_RESET()
        except Exception: pass


def _fc_build(scene_name):
    global _ACTIVE_SCENE
    build = _SCENES.get(scene_name)
    if not build:
        raise Exception("frameCraft: scene not found: %s" % scene_name)
    _fc_reset_runtime(_CTX)
    _CTX.scene = scene_name
    _ACTIVE_SCENE = scene_name
    # copy default vars from last SCENE(...) call into ctx.vars
    # NOTE: SCENE sets _CTX.vars template; we clone it here
    _CTX.vars = dict(_CTX.vars)
    build(_CTX)


# ============================================================
#  Hooks for CodeRoom pygame engine loop
# ============================================================

def FC_BOOT(scene_name=None):
    """Call once before first frame (or after reset) to build the scene."""
    if pygame is None:
        raise Exception("frameCraft: pygame not available")
    if scene_name is None:
        scene_name = _CTX.scene
    _fc_build(scene_name)

def FC_STEP(events, dt):
    """
    Called each frame by CodeRoom's existing engine.
    - events: list of pygame events (already collected by host) OR None
    - dt: delta time seconds
    """
    if not _CTX.running:
        return
    _CTX.dt = float(dt)
    _CTX.time += _CTX.dt

    _fc_update_input(events)
    _fc_tick_timers()
    _fc_tick_entities()
    _fc_run_rules()
    _fc_run_collisions()

def FC_DRAW(screen):
    """Called each frame by host to draw onto the existing screen/canvas."""
    # sync actual window size from host screen
    try:
        _CTX.window = screen.get_size()
    except Exception:
        pass
    _fc_render(screen)

def FC_RESET(scene_name=None):
    """Rebuild current scene (or a new one)."""
    if scene_name is None:
        scene_name = _CTX.scene
    _fc_build(scene_name)

def FC_STOP():
    _CTX.running = False


# ============================================================
# Internal engine steps
# ============================================================

def _fc_update_input(events):
    # edge = pressed this frame
    prev = set(_CTX._actions_down)
    _CTX._actions_edge = set()

    # If host passes events, we update from them.
    # If host passes None, we do not consume pygame.event.get().
    if events is None:
        events = []

    for ev in events:
        if ev.type == pygame.QUIT:
            _CTX.running = False

        elif ev.type == pygame.KEYDOWN:
            try:
                name = pygame.key.name(ev.key)
                name = _lower(name)
                # normalize common arrow names across pygame/Skulpt builds
                if "up" in name and "page" not in name:
                    name = "up"
                elif "down" in name and "page" not in name:
                    name = "down"
                elif "left" in name:
                    name = "left"
                elif "right" in name:
                    name = "right"
            except Exception:
                name = None
            if name:
                _CTX._keys_down.add(_lower(name))

        elif ev.type == pygame.KEYUP:
            try:
                name = pygame.key.name(ev.key)
            except Exception:
                name = None
            if name:
                n = _lower(name)
                if n in _CTX._keys_down:
                    _CTX._keys_down.remove(n)

        elif ev.type == pygame.MOUSEMOTION:
            _CTX.pointer_pos = ev.pos

        elif ev.type == pygame.MOUSEBUTTONDOWN:
            _CTX.pointer_down = True
            _CTX.pointer_pos = ev.pos

        elif ev.type == pygame.MOUSEBUTTONUP:
            _CTX.pointer_down = False
            _CTX.pointer_pos = ev.pos

    # virtual buttons update
    for b in _CTX.vbuttons:
        if not b.visible:
            b.is_down = False
            continue
        if _CTX.pointer_down and b.rect.collidepoint(_CTX.pointer_pos[0], _CTX.pointer_pos[1]):
            b.is_down = True
        else:
            b.is_down = False

    # actions down from keyboard
    down = set()
    for action, keys in _CTX.bindings.items():
        for k in keys:
            if _lower(k) in _CTX._keys_down:
                down.add(action)
                break

    # actions down from virtual buttons
    for b in _CTX.vbuttons:
        if b.visible and b.is_down:
            down.add(b.action)

    _CTX._actions_down = down
    _CTX._actions_edge = down.difference(prev)

def _fc_tick_timers():
    for te in _CTX.timers:
        te.t += _CTX.dt
        while te.t >= te.every:
            te.t -= te.every
            te.fn(_CTX)

def _fc_tick_entities():
    # grid cooldown timers
    for e in _CTX.entities.values():
        if not e.alive:
            continue
        if e.grid_t > 0.0:
            e.grid_t = max(0.0, e.grid_t - _CTX.dt)

    # integrate px velocities
    for e in _CTX.entities.values():
        if not e.alive:
            continue
        if e.space == "px":
            e.x += e.vx * _CTX.dt
            e.y += e.vy * _CTX.dt

def _fc_run_rules():
    for fn in _CTX.rules:
        fn(_CTX)

def _fc_run_collisions():
    for (ta, tb, handler) in _CTX.collisions:
        A = _CTX.all_tag(ta)
        B = _CTX.all_tag(tb)
        if not A or not B:
            continue
        for a in A:
            for b in B:
                if a is b:
                    continue
                if _CTX._collide(a, b):
                    h = handler
                    if isinstance(handler, basestring):
                        h = _CTX.fn.get(handler)
                    if h:
                        h(_CTX, a, b)

def _fc_render(screen):
    # clear
    try:
        screen.fill(_CTX.bg)
    except Exception:
        pass

    # zones (debug)
    if _CTX.debug:
        for z in _CTX.zones.values():
            try:
                pygame.draw.rect(screen, (50,90,50), z.rect, 1)
            except Exception:
                pass

    # entities
    for e in _CTX.entities.values():
        if not e.alive:
            continue
        cx, cy = _CTX._to_px_center(e)

        if gfx is not None and hasattr(e, "data") and e.data and e.data.get("gfx"):
            try:
                gfx.draw_entity(screen, _CTX, e)
            except Exception:
                pass
        elif e.sprite:
            try:
                r = e.sprite.get_rect()
                if e.sprite_center:
                    r.center = (int(cx), int(cy))
                else:
                    r.topleft = (int(cx), int(cy))
                screen.blit(e.sprite, r)
            except Exception:
                pass
        else:
            # fallback collider rect
            try:
                rr = _CTX._aabb_px(e)
                pygame.draw.rect(screen, (200,200,200), rr, 1)
            except Exception:
                pass

        if _CTX.debug:
            try:
                rr = _CTX._aabb_px(e)
                pygame.draw.rect(screen, (120,120,255), rr, 1)
            except Exception:
                pass

    # virtual buttons UI  (WICHTIG: ausserhalb der entities-loop!)
    for b in _CTX.vbuttons:
        if not b.visible:
            continue

        st = b.style or {}

        # Defaults: white border/text like before, but with semi-transparent background
        # NOTE: pygame in some envs may ignore alpha on draw.rect; we still keep RGBA for compatibility.
        bg = st.get("bg", (0, 0, 0, 120))                 # semi-transparent black
        border = st.get("border", (255, 255, 255, 255))   # white
        fg = st.get("fg", st.get("color", (255, 255, 255, 255)))

        border_w = _safe_int(st.get("border_w", 2), 2)
        font_size = _safe_int(st.get("font", 20), 20)

        # background
        try:
            if bg is not None:
                pygame.draw.rect(screen, bg, b.rect, 0)  # fill
        except Exception:
            pass

        # outline
        try:
            if border is not None and border_w > 0:
                pygame.draw.rect(screen, border, b.rect, border_w)  # outline
        except Exception:
            pass

        # label
        if b.label:
            try:
                _CTX._draw_text(screen, b.label, b.rect.x + 8, b.rect.y + 6, size=font_size, color=fg)
            except Exception:
                _CTX._draw_text(screen, b.label, b.rect.x + 8, b.rect.y + 6, size=font_size)

    # debug HUD
    if _CTX.debug:
        _CTX._draw_text(screen, "frameCraft  scene=%s  dt=%.3f  ents=%d" %
                        (_CTX.scene, _CTX.dt, len(_CTX.entities)), 8, 8, 18)

    # UI on top
    if ui is not None:
        try:
            ui.UI_DRAW(screen, _CTX)
        except Exception:
            pass
# ============================================================
# Public English DSL
# ============================================================

def GAME(title, window=(800,600), fps=60, tile=32, background=(16,16,16), debug=False):
    _CTX.title = title
    _CTX.window = window
    _CTX.fps = fps
    _CTX.tile = tile
    _CTX.bg = background
    _CTX.debug = bool(debug)

def ASSET_RESOLVER(fn):
    _CTX.asset_resolver = fn
    return fn

def SCENE(name, **vars_):
    # Set current scene name & default vars template (cloned on build)
    _CTX.scene = name
    _CTX.vars = dict(vars_)

def SCENE_BUILD(name):
    # decorator
    def deco(fn):
        _SCENES[name] = fn
        return fn
    return deco

def REGISTER(name, fn):
    _CTX.fn[name] = fn

def BIND(action, keys):
    if not _is_list(keys):
        keys = [keys]
    _CTX.bindings[action] = [_lower(k) for k in keys]

def VBUTTON(name, action, rect, label="", visible=True, style=None):
    # rect in px (x,y,w,h)
    r = pygame.Rect(_safe_int(rect[0]), _safe_int(rect[1]), _safe_int(rect[2]), _safe_int(rect[3]))
    b = VirtualButton(name, action, r, label, style=style, visible=visible)
    _CTX.vbuttons.append(b)
    return b

def VBUTTON_SHOW(name, visible=True):
    for b in _CTX.vbuttons:
        if b.name == name:
            b.visible = bool(visible)
            return b
    return None

def ENTITY(name, pos=(0,0), tag="", space="px"):
    e = Entity(name, pos[0], pos[1], tag)
    e.space = space
    _CTX._add_entity(e)
    return e

def SPRITE(name, image, center=True):
    e = _CTX.E(name)
    if not e:
        return None
    e.sprite = _CTX._load_image(image)
    e.sprite_center = bool(center)
    return e

def RECT(name, w, h, solid=False, trigger=False):
    e = _CTX.E(name)
    if not e:
        return None
    e.w = int(w); e.h = int(h)
    e.solid = bool(solid); e.trigger = bool(trigger)
    return e

def TILE_RECT(name, w_tiles, h_tiles, solid=False, trigger=False):
    e = _CTX.E(name)
    if not e:
        return None
    e.w = int(w_tiles) * _CTX.tile
    e.h = int(h_tiles) * _CTX.tile
    e.solid = bool(solid); e.trigger = bool(trigger)
    return e

def VEL(name, vx, vy):
    e = _CTX.E(name)
    if not e:
        return None
    e.vx = float(vx); e.vy = float(vy)
    return e

def GRID_COOLDOWN(name, seconds):
    e = _CTX.E(name)
    if not e:
        return None
    e.grid_cd = float(seconds)
    return e

def GRID_STEP(name, dx, dy):
    _CTX.grid_step(name, dx, dy)

def RULE(handler):
    if isinstance(handler, basestring):
        fn = _CTX.fn.get(handler)
        if fn:
            _CTX.rules.append(fn)
            return fn
        return None
    else:
        _CTX.rules.append(handler)
        return handler

def EVERY(seconds, handler):
    if isinstance(handler, basestring):
        fn = _CTX.fn.get(handler)
    else:
        fn = handler
    if fn:
        te = TimerEvent(seconds, fn)
        _CTX.timers.append(te)
        return te
    return None

def ON_COLLIDE(tagA, tagB, handler):
    c = (tagA, tagB, handler)
    _CTX.collisions.append(c)
    return c

def ZONE(name, rect, tag="", trigger=True):
    r = pygame.Rect(_safe_int(rect[0]), _safe_int(rect[1]), _safe_int(rect[2]), _safe_int(rect[3]))
    z = Zone(name, r, tag, bool(trigger))
    _CTX.zones[name] = z
    return z

def BOARD(name, w, h, default=0):
    b = GridBoard(w, h, default)
    _CTX.boards[name] = b
    return b

def BOARD_GET(name, x, y, default=None):
    b = _CTX.boards.get(name)
    if not b: return default
    return b.get(x,y,default)

def BOARD_SET(name, x, y, value):
    b = _CTX.boards.get(name)
    if not b: return
    b.set(x,y,value)

def BOARD_FILL(name, value):
    b = _CTX.boards.get(name)
    if not b: return
    b.fill(value)

def RESET(scene_name=None):
    FC_RESET(scene_name)

def STOP():
    FC_STOP()


# Optional convenience: standalone runner (only if you want it for local dev)
def START_STANDALONE(scene_name=None):
    """
    For local testing outside CodeRoom. In CodeRoom you likely won't use this.
    """
    if pygame is None:
        raise Exception("pygame not available")
    pygame.init()
    screen = pygame.display.set_mode(_CTX.window)
    try:
        pygame.display.set_caption(_CTX.title)
    except Exception:
        pass
    clock = pygame.time.Clock()
    if scene_name is None:
        scene_name = _CTX.scene
    FC_BOOT(scene_name)
    running = True
    while running and _CTX.running:
        dt = clock.tick(_CTX.fps) / 1000.0
        events = pygame.event.get()
        FC_STEP(events, dt)
        FC_DRAW(screen)
        pygame.display.flip()
        # allow quit
        for ev in events:
            if ev.type == pygame.QUIT:
                running = False
    pygame.quit()

def START(scene_name=None):
    return START_STANDALONE(scene_name)
