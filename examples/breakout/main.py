import frameCraft as fc

try:
    import frameCraftGFX as gfx
except ImportError:
    gfx = None

try:
    import frameCraftUI as ui
except ImportError:
    ui = None


# ============================================================
# Game constants
# ============================================================

BORDER = 4
BALL_SPEED = 140.0

ROW_COLORS = [
    (220, 60, 60),
    (220, 140, 40),
    (200, 200, 40),
    (60, 200, 60),
    (60, 160, 220),
]

BLOCK_WIDTH = 36
BLOCK_HEIGHT = 10
BLOCK_COLUMNS = 7
BLOCK_ROWS = 5
BLOCK_SPACING_X = 40
BLOCK_SPACING_Y = 14
BLOCK_START_X = 22
BLOCK_START_Y = 24

PADDLE_WIDTH = 56
PADDLE_HEIGHT = 8
PADDLE_SPEED = 220.0

BALL_SIZE = 7
BALL_RADIUS = 4
BALL_OFFSET_Y = 14
BALL_MIN_X_SPEED = 25

TOUCH_BUTTON_WIDTH = 60
TOUCH_BUTTON_HEIGHT = 28
START_BUTTON_WIDTH = 70
START_BUTTON_HEIGHT = 18

HUD_FONT_SIZE = 11
MESSAGE_FONT_SIZE = 14


# ============================================================
# General helpers
# ============================================================

def clamp(value, minimum, maximum):
    """Clamp a value to the inclusive range minimum..maximum."""
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def set_rectangle_gfx(
    entity,
    width,
    height,
    fill=(80, 180, 255),
    outline=(200, 240, 255),
):
    """Assign a centered rectangle graphic to an entity."""
    if gfx is None or entity is None:
        return

    gfx.set_gfx(
        entity,
        [
            gfx.P_RECT(
                -(width // 2),
                -(height // 2),
                width,
                height,
                fill=fill,
                outline=outline,
                width=1,
            )
        ],
    )


def set_circle_gfx(
    entity,
    radius,
    fill=(255, 220, 80),
    outline=(255, 255, 180),
):
    """Assign a circle graphic to an entity."""
    if gfx is None or entity is None:
        return

    gfx.set_gfx(
        entity,
        [
            gfx.P_CIRCLE(
                0,
                0,
                radius,
                fill=fill,
                outline=outline,
                width=1,
            )
        ],
    )


def setup_controls(ctx):
    """Configure keyboard actions and virtual buttons."""
    window_width, window_height = ctx.window

    fc.BIND("left", ["left", "a"])
    fc.BIND("right", ["right", "d"])
    fc.BIND("start", ["space"])
    fc.BIND("stop", ["escape"])

    fc.VBUTTON(
        "btn_left",
        "left",
        (
            0,
            window_height - TOUCH_BUTTON_HEIGHT,
            TOUCH_BUTTON_WIDTH,
            TOUCH_BUTTON_HEIGHT,
        ),
        label="<",
        style={"font": 18},
    )

    fc.VBUTTON(
        "btn_right",
        "right",
        (
            window_width - TOUCH_BUTTON_WIDTH,
            window_height - TOUCH_BUTTON_HEIGHT,
            TOUCH_BUTTON_WIDTH,
            TOUCH_BUTTON_HEIGHT,
        ),
        label=">",
        style={"font": 18},
    )

    fc.VBUTTON(
        "btn_start",
        "start",
        (
            window_width // 2 - START_BUTTON_WIDTH // 2,
            6,
            START_BUTTON_WIDTH,
            START_BUTTON_HEIGHT,
        ),
        label="START",
        style={"font": 14},
    )


# ============================================================
# Game and scene setup
# ============================================================

fc.GAME(
    "Breakout",
    window=(320, 200),
    fps=60,
    background=(15, 15, 25),
)

fc.SCENE(
    "main",
    score=0,
    lives=3,
    blocks_remaining=0,
    active=False,
    game_over=False,
    won=False,
    message_text="Press SPACE!",
    death_latch=False,
    restart_latch=False,
)


# ============================================================
# Scene build
# ============================================================

@fc.SCENE_BUILD("main")
def build_scene(ctx):
    window_width, window_height = ctx.window

    # RESET rebuilds the scene, so explicitly restore the game state.
    ctx.vars["score"] = 0
    ctx.vars["lives"] = 3
    ctx.vars["blocks_remaining"] = 0
    ctx.vars["active"] = False
    ctx.vars["game_over"] = False
    ctx.vars["won"] = False
    ctx.vars["message_text"] = "Press SPACE!"
    ctx.vars["death_latch"] = False
    ctx.vars["restart_latch"] = False

    setup_controls(ctx)

    # --------------------------------------------------------
    # Paddle
    # --------------------------------------------------------

    fc.ENTITY(
        "paddle",
        pos=(
            window_width // 2,
            window_height - 22,
        ),
        tag="paddle",
    )

    fc.RECT(
        "paddle",
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
        solid=True,
    )

    set_rectangle_gfx(
        ctx.E("paddle"),
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
        fill=(80, 180, 255),
        outline=(200, 240, 255),
    )

    # --------------------------------------------------------
    # Ball
    # --------------------------------------------------------

    fc.ENTITY(
        "ball",
        pos=(
            window_width // 2,
            window_height - 35,
        ),
        tag="ball",
    )

    fc.RECT(
        "ball",
        BALL_SIZE,
        BALL_SIZE,
    )

    fc.VEL(
        "ball",
        0,
        0,
    )

    set_circle_gfx(
        ctx.E("ball"),
        BALL_RADIUS,
        fill=(255, 220, 80),
        outline=(255, 255, 180),
    )

    # --------------------------------------------------------
    # Blocks
    # --------------------------------------------------------

    block_count = 0

    for row in range(BLOCK_ROWS):
        for column in range(BLOCK_COLUMNS):
            block_name = (
                "block_"
                + str(row)
                + "_"
                + str(column)
            )

            block_x = (
                BLOCK_START_X
                + column * BLOCK_SPACING_X
            )

            block_y = (
                BLOCK_START_Y
                + row * BLOCK_SPACING_Y
            )

            fc.ENTITY(
                block_name,
                pos=(block_x, block_y),
                tag="block",
            )

            fc.RECT(
                block_name,
                BLOCK_WIDTH,
                BLOCK_HEIGHT,
                solid=True,
            )

            block_color = ROW_COLORS[
                row % len(ROW_COLORS)
            ]

            set_rectangle_gfx(
                ctx.E(block_name),
                BLOCK_WIDTH,
                BLOCK_HEIGHT,
                fill=block_color,
                outline=(0, 0, 0),
            )

            block_count += 1

    ctx.vars["blocks_remaining"] = block_count

    # Invisible trigger area below the visible playfield.
    fc.ZONE(
        "death_zone",
        (
            0,
            window_height + 2,
            window_width,
            14,
        ),
        tag="death",
    )

    # --------------------------------------------------------
    # HUD
    # --------------------------------------------------------

    if ui is not None:
        ui.UI_TEXT(
            "hud_score",
            4,
            2,
            bind=lambda c: (
                "Score: "
                + str(c.vars.get("score", 0))
            ),
            size=HUD_FONT_SIZE,
            color=(200, 220, 255),
            anchor="topleft",
            z=10,
        )

        ui.UI_TEXT(
            "hud_lives",
            window_width - 4,
            2,
            bind=lambda c: (
                "Lives: "
                + str(c.vars.get("lives", 0))
            ),
            size=HUD_FONT_SIZE,
            color=(200, 220, 255),
            anchor="topright",
            z=10,
        )

        ui.UI_TEXT(
            "message",
            window_width // 2,
            window_height // 2,
            bind="message_text",
            size=MESSAGE_FONT_SIZE,
            color=(255, 255, 120),
            anchor="center",
            z=20,
        )

    # ========================================================
    # Game rules
    # ========================================================

    def global_stop(ctx):
        if ctx.pressed("stop"):
            fc.STOP()

    fc.RULE(global_stop)

    def move_paddle(ctx):
        if (
            ctx.vars.get("game_over")
            or ctx.vars.get("won")
        ):
            return

        paddle = ctx.E("paddle")

        if paddle is None:
            return

        move_step = PADDLE_SPEED * ctx.dt

        if ctx.down("left"):
            paddle.x -= move_step

        if ctx.down("right"):
            paddle.x += move_step

        paddle.x = clamp(
            paddle.x,
            BORDER + paddle.w / 2.0,
            window_width - BORDER - paddle.w / 2.0,
        )

    fc.RULE(move_paddle)

    def attach_ball_to_paddle(ctx):
        if ctx.vars.get("active"):
            return

        paddle = ctx.E("paddle")
        ball = ctx.E("ball")

        if paddle is None or ball is None:
            return

        ball.x = paddle.x
        ball.y = paddle.y - BALL_OFFSET_Y
        ball.vx = 0
        ball.vy = 0

        # Allow the next ball loss to be counted.
        ctx.vars["death_latch"] = False

    fc.RULE(attach_ball_to_paddle)

    def start_ball(ctx):
        if (
            ctx.vars.get("game_over")
            or ctx.vars.get("won")
        ):
            return

        if (
            not ctx.vars.get("active")
            and ctx.pressed("start")
        ):
            ctx.vars["active"] = True
            ctx.vars["message_text"] = ""

            ball = ctx.E("ball")

            if ball is not None:
                ball.vx = BALL_SPEED
                ball.vy = -BALL_SPEED

    fc.RULE(start_ball)

    def reflect_ball_at_walls(ctx):
        if not ctx.vars.get("active"):
            return

        ball = ctx.E("ball")

        if ball is None:
            return

        if ball.x - ball.w / 2.0 <= BORDER:
            ball.x = BORDER + ball.w / 2.0
            ball.vx = abs(ball.vx)

        if (
            ball.x + ball.w / 2.0
            >= window_width - BORDER
        ):
            ball.x = (
                window_width
                - BORDER
                - ball.w / 2.0
            )
            ball.vx = -abs(ball.vx)

        if ball.y - ball.h / 2.0 <= BORDER:
            ball.y = BORDER + ball.h / 2.0
            ball.vy = abs(ball.vy)

    fc.RULE(reflect_ball_at_walls)

    def check_ball_lost(ctx):
        if not ctx.vars.get("active", False):
            return

        # The zone can remain active for several frames.
        # The latch guarantees that one lost ball costs exactly one life.
        if ctx.vars.get("death_latch", False):
            return

        if ctx.in_zone(
            "ball",
            "death_zone",
        ):
            ctx.vars["death_latch"] = True
            ctx.vars["lives"] -= 1
            ctx.vars["active"] = False

            if ctx.vars.get("lives", 0) <= 0:
                ctx.vars["game_over"] = True
                ctx.vars["message_text"] = (
                    "GAME OVER! "
                    + str(ctx.vars.get("score", 0))
                    + " points!"
                )
            else:
                ctx.vars["message_text"] = (
                    "Press SPACE!"
                )

    fc.RULE(check_ball_lost)

    def check_restart(ctx):
        if not (
            ctx.vars.get("game_over")
            or ctx.vars.get("won")
        ):
            return

        if ctx.pressed("start"):
            fc.RESET("main")
            return

        if (
            ctx.down("start")
            and not ctx.vars.get("restart_latch")
        ):
            ctx.vars["restart_latch"] = True
            fc.RESET("main")
            return

        if not ctx.down("start"):
            ctx.vars["restart_latch"] = False

    fc.RULE(check_restart)

    # ========================================================
    # Collisions
    # ========================================================

    def ball_paddle_collision(
        ctx,
        ball,
        paddle,
    ):
        if not ctx.vars.get("active"):
            return

        # Always send the ball upward after a paddle hit.
        ball.vy = -abs(ball.vy)

        denominator = paddle.w / 2.0

        if denominator <= 0:
            return

        # The horizontal bounce angle depends on where the
        # ball hits the paddle.
        offset = (
            ball.x - paddle.x
        ) / denominator

        offset = clamp(
            offset,
            -1,
            1,
        )

        ball.vx = BALL_SPEED * offset

        # Prevent almost vertical trajectories.
        if abs(ball.vx) < BALL_MIN_X_SPEED:
            if ball.vx >= 0:
                ball.vx = BALL_MIN_X_SPEED
            else:
                ball.vx = -BALL_MIN_X_SPEED

    fc.ON_COLLIDE(
        "ball",
        "paddle",
        ball_paddle_collision,
    )

    def ball_block_collision(
        ctx,
        ball,
        block,
    ):
        if not ctx.vars.get("active"):
            return

        if not block.alive:
            return

        block.alive = False

        ctx.vars["score"] += 10
        ctx.vars["blocks_remaining"] -= 1

        ball.vy = -ball.vy

        if ctx.vars["blocks_remaining"] <= 0:
            ctx.vars["won"] = True
            ctx.vars["active"] = False
            ctx.vars["message_text"] = (
                "YOU WIN! "
                + str(ctx.vars["score"])
                + " points!"
            )

    fc.ON_COLLIDE(
        "ball",
        "block",
        ball_block_collision,
    )


fc.START_STANDALONE("main")
