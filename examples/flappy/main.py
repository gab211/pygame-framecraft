import frameCraft as fc
import frameCraftGFX as gfx
import frameCraftUI as ui

# ------------------------------------------------------------
# Flappy Color Flight
# Standalone frameCraft example
# ------------------------------------------------------------

WINDOW_WIDTH = 360
WINDOW_HEIGHT = 240
GROUND_HEIGHT = 24

BIRD_X = 82
BIRD_START_Y = 112
BIRD_WIDTH = 20
BIRD_HEIGHT = 20

GRAVITY = 500
FLAP_FORCE = -175

START_SPEED = 82
SPEED_INCREASE_PER_POINT = 5
MAX_SPEED = 155

PIPE_COUNT = 4
PIPE_WIDTH = 34
PIPE_SPACING = 116
PIPE_GAP_START = 84
PIPE_GAP_MIN = 64
PIPE_START_X = 290

SKY_COLOR = (38, 64, 104)
GROUND_COLOR = (82, 146, 80)
GROUND_DARK_COLOR = (54, 98, 58)
CLOUD_COLOR = (215, 235, 255)

PIPE_COLORS = [
    (42, 205, 112),
    (60, 180, 235),
    (235, 170, 55),
    (205, 90, 150),
]

GAP_PATTERNS = [92, 112, 132, 104, 124]


def clamp(value, minimum, maximum):
    """Clamp a numeric value to the given range."""
    if value < minimum:
        return minimum

    if value > maximum:
        return maximum

    return value


def set_rectangle_gfx(entity, width, height, color, outline=None, z=0):
    """Draw a centered rectangle that matches an entity."""
    if entity is None:
        return

    gfx.set_gfx(entity, [
        gfx.P_RECT(
            -(width // 2),
            -(height // 2),
            width,
            height,
            fill=color,
            outline=outline,
            width=1,
            z=z,
        )
    ])


def set_pipe_gfx(entity, width, height, color):
    """Draw a pipe with a bright outline and end caps."""
    if entity is None:
        return

    edge_color = (245, 245, 245)

    gfx.set_gfx(entity, [
        gfx.P_RECT(
            -(width // 2),
            -(height // 2),
            width,
            height,
            fill=color,
            outline=edge_color,
            width=1,
            z=5,
        ),
        gfx.P_RECT(
            -(width // 2) - 3,
            -(height // 2),
            width + 6,
            10,
            fill=color,
            outline=edge_color,
            width=1,
            z=6,
        ),
        gfx.P_RECT(
            -(width // 2) - 3,
            (height // 2) - 10,
            width + 6,
            10,
            fill=color,
            outline=edge_color,
            width=1,
            z=6,
        ),
    ])


def set_bird_gfx(entity):
    """Draw the bird using simple graphics primitives."""
    if entity is None:
        return

    gfx.set_gfx(entity, [
        gfx.P_CIRCLE(
            0,
            0,
            10,
            fill=(255, 222, 70),
            outline=(255, 250, 180),
            width=1,
            z=20,
        ),
        gfx.P_CIRCLE(
            4,
            -3,
            3,
            fill=(255, 255, 255),
            outline=None,
            width=1,
            z=21,
        ),
        gfx.P_CIRCLE(
            5,
            -3,
            1,
            fill=(20, 20, 25),
            outline=None,
            width=1,
            z=22,
        ),
        gfx.P_POLY(
            [(9, -1), (17, 3), (9, 6)],
            fill=(255, 150, 40),
            outline=None,
            width=1,
            z=22,
        ),
        gfx.P_POLY(
            [(-8, 2), (-17, 8), (-6, 9)],
            fill=(255, 190, 50),
            outline=None,
            width=1,
            z=21,
        ),
    ])


fc.GAME(
    "Flappy Color Flight",
    window=(WINDOW_WIDTH, WINDOW_HEIGHT),
    fps=60,
    tile=16,
    background=SKY_COLOR,
    debug=False,
)

fc.SCENE(
    "main",
    game_state="running",
)


@fc.SCENE_BUILD("main")
def build_scene(ctx):
    ui.UI_RESET()

    width, height = ctx.window

    ctx.vars["game_state"] = "running"
    ctx.vars["score"] = 0
    ctx.vars["speed"] = START_SPEED
    ctx.vars["bird_vy"] = 0
    ctx.vars["flap_latch"] = False
    ctx.vars["restart_latch"] = False
    ctx.vars["pipe_scored"] = [False] * PIPE_COUNT
    ctx.vars["next_pattern"] = 0

    fc.BIND(
        "flap",
        ["space", "up", "w"],
    )

    fc.BIND(
        "restart",
        ["r", "return"],
    )

    button_style = {
        "bg": (0, 0, 0, 90),
        "border": (180, 220, 255, 180),
        "border_w": 1,
        "fg": (230, 240, 255),
        "font": 20,
    }

    fc.VBUTTON(
        "btn_flap",
        "flap",
        (width - 76, height - 64, 58, 48),
        label="J",
        visible=True,
        style=button_style,
    )

    fc.VBUTTON(
        "btn_restart",
        "restart",
        (18, height - 64, 58, 48),
        label="R",
        visible=True,
        style=button_style,
    )

    fc.ENTITY(
        "sky",
        pos=(width // 2, height // 2),
        tag="decoration",
    )

    set_rectangle_gfx(
        ctx.E("sky"),
        width,
        height,
        SKY_COLOR,
        None,
        -30,
    )

    fc.ENTITY(
        "sun",
        pos=(308, 42),
        tag="decoration",
    )

    sun = ctx.E("sun")

    if sun is not None:
        gfx.set_gfx(sun, [
            gfx.P_CIRCLE(
                0,
                0,
                18,
                fill=(255, 224, 110),
                outline=(255, 246, 180),
                width=2,
                z=-20,
            )
        ])

    for i in range(3):
        x = 55 + i * 110
        y = 38 + (i % 2) * 22

        cloud_name = "cloud_%d" % i

        fc.ENTITY(
            cloud_name,
            pos=(x, y),
            tag="decoration",
        )

        cloud = ctx.E(cloud_name)

        if cloud is not None:
            gfx.set_gfx(cloud, [
                gfx.P_CIRCLE(
                    -16,
                    3,
                    10,
                    fill=CLOUD_COLOR,
                    outline=None,
                    width=1,
                    z=-18,
                ),
                gfx.P_CIRCLE(
                    0,
                    -2,
                    13,
                    fill=CLOUD_COLOR,
                    outline=None,
                    width=1,
                    z=-18,
                ),
                gfx.P_CIRCLE(
                    17,
                    4,
                    9,
                    fill=CLOUD_COLOR,
                    outline=None,
                    width=1,
                    z=-18,
                ),
            ])

    fc.ENTITY(
        "ground",
        pos=(
            width // 2,
            height - GROUND_HEIGHT // 2,
        ),
        tag="hazard",
    )

    fc.RECT(
        "ground",
        width,
        GROUND_HEIGHT,
        solid=False,
        trigger=True,
    )

    ground = ctx.E("ground")

    if ground is not None:
        gfx.set_gfx(ground, [
            gfx.P_RECT(
                -(width // 2),
                -(GROUND_HEIGHT // 2),
                width,
                GROUND_HEIGHT,
                fill=GROUND_COLOR,
                outline=None,
                width=1,
                z=30,
            ),
            gfx.P_RECT(
                -(width // 2),
                -(GROUND_HEIGHT // 2),
                width,
                5,
                fill=GROUND_DARK_COLOR,
                outline=None,
                width=1,
                z=31,
            ),
        ])

    fc.ENTITY(
        "ceiling",
        pos=(width // 2, -6),
        tag="hazard",
    )

    fc.RECT(
        "ceiling",
        width,
        12,
        solid=False,
        trigger=True,
    )

    fc.ENTITY(
        "bird",
        pos=(BIRD_X, BIRD_START_Y),
        tag="bird",
    )

    fc.RECT(
        "bird",
        BIRD_WIDTH,
        BIRD_HEIGHT,
        solid=False,
        trigger=True,
    )

    bird = ctx.E("bird")

    if bird is not None:
        bird.vx = 0
        bird.vy = 0

    set_bird_gfx(bird)

    for i in range(PIPE_COUNT):
        x_pos = PIPE_START_X + i * PIPE_SPACING
        gap_y = GAP_PATTERNS[i % len(GAP_PATTERNS)]
        color = PIPE_COLORS[i % len(PIPE_COLORS)]

        top_height = max(
            20,
            int(gap_y - PIPE_GAP_START // 2),
        )

        bottom_start = int(
            gap_y + PIPE_GAP_START // 2
        )

        bottom_height = max(
            20,
            int(
                (height - GROUND_HEIGHT)
                - bottom_start
            ),
        )

        top_name = "pipe_top_%d" % i
        bottom_name = "pipe_bottom_%d" % i

        fc.ENTITY(
            top_name,
            pos=(x_pos, top_height // 2),
            tag="obstacle",
        )

        fc.RECT(
            top_name,
            PIPE_WIDTH,
            top_height,
            solid=False,
            trigger=True,
        )

        set_pipe_gfx(
            ctx.E(top_name),
            PIPE_WIDTH,
            top_height,
            color,
        )

        fc.ENTITY(
            bottom_name,
            pos=(
                x_pos,
                bottom_start + bottom_height // 2,
            ),
            tag="obstacle",
        )

        fc.RECT(
            bottom_name,
            PIPE_WIDTH,
            bottom_height,
            solid=False,
            trigger=True,
        )

        set_pipe_gfx(
            ctx.E(bottom_name),
            PIPE_WIDTH,
            bottom_height,
            color,
        )

    ui.UI_TEXT(
        "hud_score",
        8,
        7,
        text="",
        anchor="topleft",
        z=100,
        size=16,
        color=(255, 255, 255),
        bg=(0, 0, 0, 80),
        border=None,
        pad=4,
        bind=lambda ctx: "Score: %d"
        % ctx.vars.get("score", 0),
    )

    ui.UI_TEXT(
        "hud_speed",
        8,
        31,
        text="",
        anchor="topleft",
        z=100,
        size=13,
        color=(230, 240, 255),
        bg=(0, 0, 0, 60),
        border=None,
        pad=4,
        bind=lambda ctx: "Speed: %d"
        % int(ctx.vars.get("speed", START_SPEED)),
    )

    ui.UI_TEXT(
        "help",
        width // 2,
        8,
        text="Space / Tap: flap",
        anchor="midtop",
        z=100,
        size=13,
        color=(245, 250, 255),
        bg=(0, 0, 0, 45),
        border=None,
        pad=4,
    )

    ui.UI_TEXT(
        "game_over",
        width // 2,
        height // 2 - 18,
        text="",
        anchor="center",
        z=110,
        size=24,
        color=(255, 255, 255),
        bg=(0, 0, 0, 150),
        border=(255, 255, 255, 180),
        border_w=1,
        pad=8,
        visible=False,
        bind=lambda ctx: "Game Over  Score: %d"
        % ctx.vars.get("score", 0),
    )

    ui.UI_TEXT(
        "restart_hint",
        width // 2,
        height // 2 + 20,
        text="R or button R: Restart",
        anchor="center",
        z=110,
        size=15,
        color=(255, 235, 160),
        bg=(0, 0, 0, 120),
        border=None,
        pad=6,
        visible=False,
    )

    fc.RULE(game_rule)
    fc.RULE(restart_handler)

    fc.ON_COLLIDE(
        "bird",
        "hazard",
        bird_hit,
    )

    fc.ON_COLLIDE(
        "bird",
        "obstacle",
        bird_hit,
    )


def game_rule(ctx):
    if ctx.vars.get("game_state", "running") != "running":
        return

    control_bird(ctx)
    move_bird(ctx)
    move_pipes(ctx)
    check_score(ctx)


def control_bird(ctx):
    if not ctx.down("flap"):
        ctx.vars["flap_latch"] = False

    if (
        ctx.down("flap")
        and not ctx.vars.get("flap_latch", False)
    ):
        ctx.vars["flap_latch"] = True
        ctx.vars["bird_vy"] = FLAP_FORCE


def move_bird(ctx):
    bird = ctx.E("bird")

    if bird is None:
        return

    velocity_y = ctx.vars.get("bird_vy", 0)
    velocity_y = velocity_y + GRAVITY * ctx.dt

    ctx.vars["bird_vy"] = velocity_y

    bird.y = bird.y + velocity_y * ctx.dt


def move_pipes(ctx):
    speed = ctx.vars.get("speed", START_SPEED)

    for i in range(PIPE_COUNT):
        top = ctx.E("pipe_top_%d" % i)
        bottom = ctx.E("pipe_bottom_%d" % i)

        if top is None or bottom is None:
            continue

        top.x = top.x - speed * ctx.dt
        bottom.x = bottom.x - speed * ctx.dt

        if top.x < -PIPE_WIDTH:
            new_x = farthest_pipe_x(ctx) + PIPE_SPACING
            reset_pipe(ctx, i, new_x)


def farthest_pipe_x(ctx):
    farthest_x = 0

    for i in range(PIPE_COUNT):
        top = ctx.E("pipe_top_%d" % i)

        if top is not None and top.x > farthest_x:
            farthest_x = top.x

    return farthest_x


def reset_pipe(ctx, i, x_pos):
    _, height = ctx.window

    pattern_index = ctx.vars.get(
        "next_pattern",
        0,
    )

    gap_y = GAP_PATTERNS[
        pattern_index % len(GAP_PATTERNS)
    ]

    ctx.vars["next_pattern"] = pattern_index + 1

    score = ctx.vars.get("score", 0)

    gap = PIPE_GAP_START - score * 2

    gap = clamp(
        gap,
        PIPE_GAP_MIN,
        PIPE_GAP_START,
    )

    color_index = (
        pattern_index + score
    ) % len(PIPE_COLORS)

    color = PIPE_COLORS[color_index]

    top_height = max(
        20,
        int(gap_y - gap // 2),
    )

    bottom_start = int(
        gap_y + gap // 2
    )

    bottom_height = max(
        20,
        int(
            (height - GROUND_HEIGHT)
            - bottom_start
        ),
    )

    top = ctx.E("pipe_top_%d" % i)
    bottom = ctx.E("pipe_bottom_%d" % i)

    if top is not None:
        top.x = x_pos
        top.y = top_height // 2
        top.w = PIPE_WIDTH
        top.h = top_height

        set_pipe_gfx(
            top,
            PIPE_WIDTH,
            top_height,
            color,
        )

    if bottom is not None:
        bottom.x = x_pos
        bottom.y = (
            bottom_start
            + bottom_height // 2
        )
        bottom.w = PIPE_WIDTH
        bottom.h = bottom_height

        set_pipe_gfx(
            bottom,
            PIPE_WIDTH,
            bottom_height,
            color,
        )

    scored = ctx.vars.get(
        "pipe_scored",
        [False] * PIPE_COUNT,
    )

    if i < len(scored):
        scored[i] = False

    ctx.vars["pipe_scored"] = scored


def check_score(ctx):
    bird = ctx.E("bird")

    if bird is None:
        return

    scored = ctx.vars.get(
        "pipe_scored",
        [False] * PIPE_COUNT,
    )

    score = ctx.vars.get("score", 0)

    for i in range(PIPE_COUNT):
        top = ctx.E("pipe_top_%d" % i)

        if top is None:
            continue

        if (
            i < len(scored)
            and not scored[i]
            and top.x + PIPE_WIDTH // 2 < bird.x
        ):
            scored[i] = True
            score = score + 1

    ctx.vars["pipe_scored"] = scored
    ctx.vars["score"] = score

    new_speed = (
        START_SPEED
        + score * SPEED_INCREASE_PER_POINT
    )

    ctx.vars["speed"] = clamp(
        new_speed,
        START_SPEED,
        MAX_SPEED,
    )


def bird_hit(ctx, a, b):
    if ctx.vars.get("game_state", "running") != "running":
        return

    ctx.vars["game_state"] = "game_over"

    bird = ctx.E("bird")

    if bird is not None:
        bird.vx = 0
        bird.vy = 0

    ui.UI_HIDE(
        "game_over",
        visible=True,
    )

    ui.UI_HIDE(
        "restart_hint",
        visible=True,
    )


def restart_handler(ctx):
    state = ctx.vars.get(
        "game_state",
        "running",
    )

    if state == "running":
        ctx.vars["restart_latch"] = False
        return

    if not ctx.down("restart"):
        ctx.vars["restart_latch"] = False

    if (
        ctx.down("restart")
        and not ctx.vars.get("restart_latch", False)
    ):
        ctx.vars["restart_latch"] = True
        fc.RESET("main")


fc.START_STANDALONE("main")
