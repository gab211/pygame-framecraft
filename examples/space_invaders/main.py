import frameCraft as fc
import frameCraftGFX as gfx
import frameCraftUI as ui

# ------------------------------------------------------------
# Space Invaders
# Standalone frameCraft example
# ------------------------------------------------------------

ENEMY_COLUMNS = 8
ENEMY_ROWS = 3
ENEMY_SPACING_X = 34
ENEMY_SPACING_Y = 22
ENEMY_START_X = 28
ENEMY_START_Y = 22
ENEMY_WIDTH = 14
ENEMY_HEIGHT = 10

PLAYER_SPEED = 120
SHOT_SPEED = 220
SHOT_COUNT = 100
EXPLOSION_COUNT = 12
EXPLOSION_DURATION = 0.28


def mix_color(color_a, color_b, amount):
    r = int(color_a[0] + (color_b[0] - color_a[0]) * amount)
    g = int(color_a[1] + (color_b[1] - color_a[1]) * amount)
    b = int(color_a[2] + (color_b[2] - color_a[2]) * amount)
    return (r, g, b)


def enemy_color(row, column):
    if ENEMY_ROWS <= 1:
        y_amount = 0
    else:
        y_amount = float(row) / float(ENEMY_ROWS - 1)

    if ENEMY_COLUMNS <= 1:
        x_amount = 0
    else:
        x_amount = float(column) / float(ENEMY_COLUMNS - 1)

    top_left = (80, 200, 255)
    top_right = (220, 80, 255)
    bottom_left = (80, 255, 120)
    bottom_right = (255, 90, 60)

    top_color = mix_color(top_left, top_right, x_amount)
    bottom_color = mix_color(bottom_left, bottom_right, x_amount)

    return mix_color(top_color, bottom_color, y_amount)


def enemy_pixel_gfx(row, color):
    dark = (10, 10, 14)

    if row == 0:
        return [
            gfx.P_RECT(-2, -7, 4, 2, fill=color),
            gfx.P_RECT(-6, -5, 12, 2, fill=color),
            gfx.P_RECT(-8, -3, 16, 4, fill=color),
            gfx.P_RECT(-6, 1, 3, 2, fill=dark),
            gfx.P_RECT(3, 1, 3, 2, fill=dark),
            gfx.P_RECT(-8, 3, 4, 2, fill=color),
            gfx.P_RECT(4, 3, 4, 2, fill=color),
            gfx.P_RECT(-6, 5, 3, 2, fill=color),
            gfx.P_RECT(3, 5, 3, 2, fill=color),
        ]

    if row == 1:
        return [
            gfx.P_RECT(-6, -7, 12, 2, fill=color),
            gfx.P_RECT(-8, -5, 16, 4, fill=color),
            gfx.P_RECT(-10, -1, 20, 4, fill=color),
            gfx.P_RECT(-6, 0, 3, 2, fill=dark),
            gfx.P_RECT(3, 0, 3, 2, fill=dark),
            gfx.P_RECT(-10, 3, 4, 2, fill=color),
            gfx.P_RECT(6, 3, 4, 2, fill=color),
            gfx.P_RECT(-8, 5, 3, 2, fill=color),
            gfx.P_RECT(5, 5, 3, 2, fill=color),
        ]

    return [
        gfx.P_RECT(-8, -7, 16, 2, fill=color),
        gfx.P_RECT(-10, -5, 20, 4, fill=color),
        gfx.P_RECT(-8, -1, 16, 4, fill=color),
        gfx.P_RECT(-5, 0, 3, 2, fill=dark),
        gfx.P_RECT(2, 0, 3, 2, fill=dark),
        gfx.P_RECT(-10, 3, 4, 2, fill=color),
        gfx.P_RECT(-2, 3, 4, 2, fill=color),
        gfx.P_RECT(6, 3, 4, 2, fill=color),
        gfx.P_RECT(-8, 5, 3, 2, fill=color),
        gfx.P_RECT(5, 5, 3, 2, fill=color),
    ]


fc.GAME(
    "Space Invaders",
    window=(320, 200),
    fps=60,
    tile=8,
    background=(10, 10, 14),
)

fc.SCENE(
    "main",
    score=0,
    game_state="running",
    restart_latch=False,
    fire_latch=False,
    enemy_direction=1,
    status_text="",
)


@fc.SCENE_BUILD("main")
def build_scene(ctx):
    width, height = ctx.window

    ctx.vars["score"] = 0
    ctx.vars["game_state"] = "running"
    ctx.vars["restart_latch"] = False
    ctx.vars["fire_latch"] = False
    ctx.vars["enemy_direction"] = 1
    ctx.vars["status_text"] = ""

    fc.BIND("left", ["left", "a"])
    fc.BIND("right", ["right", "d"])
    fc.BIND("fire", ["space", "up", "w"])
    fc.BIND("restart", ["r", "return"])

    button_height = 34
    button_width = 44
    margin = 6
    spacing = 6
    button_y = height - button_height - margin

    button_style = {
        "bg": (0, 0, 0, 90),
        "border": (180, 220, 255, 180),
        "border_w": 1,
        "fg": (230, 240, 255),
        "font": 20,
    }

    fc.VBUTTON(
        "btn_left",
        "left",
        (margin, button_y, button_width, button_height),
        label="<",
        style=button_style,
    )

    fc.VBUTTON(
        "btn_right",
        "right",
        (margin + button_width + spacing, button_y, button_width, button_height),
        label=">",
        style=button_style,
    )

    fc.VBUTTON(
        "btn_fire",
        "fire",
        (width - button_width - margin, button_y, button_width, button_height),
        label="F",
        style=button_style,
    )

    fc.ENTITY(
        "player",
        pos=(width // 2, height - 34),
        tag="player",
    )
    fc.RECT(
        "player",
        20,
        10,
        solid=False,
    )
    fc.VEL(
        "player",
        0,
        0,
    )

    player = ctx.E("player")

    if player is not None:
        player.alive = True
        player.x = width // 2
        player.y = height - 34
        player.vx = 0
        player.vy = 0

        gfx.set_gfx(player, [
            gfx.P_POLY(
                [(0, -16), (-7, 8), (7, 8)],
                fill=(0, 230, 90),
            ),
            gfx.P_POLY(
                [(-7, 2), (-18, 10), (-5, 10)],
                fill=(0, 170, 80),
            ),
            gfx.P_POLY(
                [(7, 2), (18, 10), (5, 10)],
                fill=(0, 170, 80),
            ),
            gfx.P_RECT(
                -3, 2, 6, 9,
                fill=(120, 255, 180),
            ),
            gfx.P_RECT(
                -2, 9, 4, 5,
                fill=(255, 120, 40),
            ),
        ])

    for i in range(SHOT_COUNT):
        shot_name = "shot_%d" % i

        fc.ENTITY(
            shot_name,
            pos=(-50, -50),
            tag="shot",
        )
        fc.RECT(
            shot_name,
            4,
            10,
            solid=False,
            trigger=True,
        )
        fc.VEL(
            shot_name,
            0,
            0,
        )

        shot = ctx.E(shot_name)

        if shot is not None:
            shot.alive = False
            shot.vx = 0
            shot.vy = 0

            gfx.set_gfx(
                shot,
                [
                    gfx.P_RECT(
                        -2,
                        -5,
                        4,
                        10,
                        fill=(255, 240, 80),
                    )
                ],
            )

    for i in range(EXPLOSION_COUNT):
        explosion_name = "explosion_%d" % i

        fc.ENTITY(
            explosion_name,
            pos=(-50, -50),
            tag="explosion",
        )
        fc.RECT(
            explosion_name,
            1,
            1,
            solid=False,
            trigger=False,
        )
        fc.VEL(
            explosion_name,
            0,
            0,
        )

        explosion = ctx.E(explosion_name)
        ctx.vars["explosion_time_%d" % i] = 0

        if explosion is not None:
            explosion.alive = False
            gfx.set_gfx(explosion, [])

    for row in range(ENEMY_ROWS):
        for column in range(ENEMY_COLUMNS):
            color = enemy_color(row, column)
            enemy_name = "enemy_%d_%d" % (row, column)

            enemy_x = ENEMY_START_X + column * ENEMY_SPACING_X
            enemy_y = ENEMY_START_Y + row * ENEMY_SPACING_Y

            fc.ENTITY(
                enemy_name,
                pos=(enemy_x, enemy_y),
                tag="enemy",
            )
            fc.RECT(
                enemy_name,
                ENEMY_WIDTH,
                ENEMY_HEIGHT,
                solid=False,
                trigger=True,
            )

            enemy = ctx.E(enemy_name)

            if enemy is not None:
                enemy.alive = True
                enemy.x = enemy_x
                enemy.y = enemy_y
                enemy.vx = 0
                enemy.vy = 0

                gfx.set_gfx(
                    enemy,
                    enemy_pixel_gfx(row, color),
                )

    ui.UI_RESET()

    ui.UI_TEXT(
        "hud_score",
        8,
        6,
        bind=lambda ctx: "%d" % ctx.vars.get("score", 0),
        size=10,
        color=(220, 220, 220),
        anchor="topleft",
        z=10,
    )

    ui.UI_TEXT(
        "hud_status",
        width // 2,
        height // 2 - 10,
        text="",
        bind=lambda ctx: ctx.vars.get("status_text", ""),
        size=18,
        color=(255, 240, 80),
        anchor="center",
        z=20,
        visible=False,
    )

    ui.UI_TEXT(
        "hud_restart",
        width // 2,
        height // 2 + 14,
        text="",
        bind=lambda ctx: (
            "[R] Restart"
            if ctx.vars.get("game_state", "running") != "running"
            else ""
        ),
        size=11,
        color=(180, 180, 180),
        anchor="center",
        z=20,
        visible=False,
    )

    fc.RULE(player_controls)
    fc.RULE(update_shots)
    fc.RULE(update_explosions)

    fc.ON_COLLIDE(
        "shot",
        "enemy",
        hit_handler,
    )

    fc.EVERY(
        0.3,
        move_enemies,
    )

    fc.RULE(check_game_end)
    fc.RULE(restart_handler)


def update_shots(ctx):
    for i in range(SHOT_COUNT):
        shot = ctx.E("shot_%d" % i)

        if shot is not None and shot.alive:
            if shot.y < -20:
                shot.alive = False
                shot.vy = 0


def move_enemies(ctx):
    if ctx.vars.get("game_state", "running") != "running":
        return

    direction = ctx.vars.get("enemy_direction", 1)

    left_edge = 999
    right_edge = 0

    for row in range(ENEMY_ROWS):
        for column in range(ENEMY_COLUMNS):
            enemy = ctx.E(
                "enemy_%d_%d" % (row, column)
            )

            if enemy is not None and enemy.alive:
                if enemy.x < left_edge:
                    left_edge = enemy.x

                if enemy.x > right_edge:
                    right_edge = enemy.x

    step = 10 * direction
    reverse = False

    if (
        direction > 0
        and right_edge + step > ctx.window[0] - 14
    ):
        reverse = True

    if (
        direction < 0
        and left_edge + step < 14
    ):
        reverse = True

    if reverse:
        ctx.vars["enemy_direction"] = -direction

        for row in range(ENEMY_ROWS):
            for column in range(ENEMY_COLUMNS):
                enemy = ctx.E(
                    "enemy_%d_%d" % (row, column)
                )

                if enemy is not None and enemy.alive:
                    enemy.y = enemy.y + 10

    else:
        for row in range(ENEMY_ROWS):
            for column in range(ENEMY_COLUMNS):
                enemy = ctx.E(
                    "enemy_%d_%d" % (row, column)
                )

                if enemy is not None and enemy.alive:
                    enemy.x = enemy.x + step


def player_controls(ctx):
    if ctx.vars.get("game_state", "running") != "running":
        return

    player = ctx.E("player")

    if player is None:
        return

    if ctx.down("left"):
        player.vx = -PLAYER_SPEED

    elif ctx.down("right"):
        player.vx = PLAYER_SPEED

    else:
        player.vx = 0

    width = ctx.window[0]

    if player.x < 10:
        player.x = 10

    if player.x > width - 10:
        player.x = width - 10

    if not ctx.down("fire"):
        ctx.vars["fire_latch"] = False

    if (
        ctx.down("fire")
        and not ctx.vars.get("fire_latch", False)
    ):
        ctx.vars["fire_latch"] = True
        fire_shot(ctx)


def fire_shot(ctx):
    player = ctx.E("player")

    if player is None:
        return

    for i in range(SHOT_COUNT):
        shot = ctx.E("shot_%d" % i)

        if shot is not None and not shot.alive:
            shot.alive = True
            shot.x = player.x
            shot.y = player.y - 10
            shot.vx = 0
            shot.vy = -SHOT_SPEED
            return


def start_explosion(ctx, x, y):
    for i in range(EXPLOSION_COUNT):
        explosion = ctx.E("explosion_%d" % i)

        if explosion is not None and not explosion.alive:
            explosion.alive = True
            explosion.x = x
            explosion.y = y

            ctx.vars[
                "explosion_time_%d" % i
            ] = EXPLOSION_DURATION

            return


def update_explosions(ctx):
    for i in range(EXPLOSION_COUNT):
        explosion = ctx.E("explosion_%d" % i)

        if explosion is None or not explosion.alive:
            continue

        time_name = "explosion_time_%d" % i
        time_left = ctx.vars.get(time_name, 0)

        time_left = time_left - ctx.dt
        ctx.vars[time_name] = time_left

        if time_left <= 0:
            explosion.alive = False
            gfx.set_gfx(explosion, [])

        else:
            remaining = time_left / EXPLOSION_DURATION
            radius = int(
                10 + (1 - remaining) * 10
            )

            gfx.set_gfx(explosion, [
                gfx.P_LINE(
                    -radius,
                    0,
                    radius,
                    0,
                    color=(255, 240, 80),
                    width=2,
                ),
                gfx.P_LINE(
                    0,
                    -radius,
                    0,
                    radius,
                    color=(255, 120, 40),
                    width=2,
                ),
                gfx.P_LINE(
                    -radius // 2,
                    -radius // 2,
                    radius // 2,
                    radius // 2,
                    color=(255, 80, 80),
                    width=2,
                ),
                gfx.P_LINE(
                    -radius // 2,
                    radius // 2,
                    radius // 2,
                    -radius // 2,
                    color=(255, 180, 80),
                    width=2,
                ),
                gfx.P_CIRCLE(
                    0,
                    0,
                    max(2, radius // 4),
                    fill=(255, 240, 120),
                ),
            ])


def hit_handler(ctx, shot, enemy):
    shot.alive = False
    shot.vy = 0

    start_explosion(
        ctx,
        enemy.x,
        enemy.y,
    )

    enemy.alive = False

    ctx.vars["score"] = (
        ctx.vars.get("score", 0) + 10
    )


def hide_playfield(ctx):
    player = ctx.E("player")

    if player is not None:
        player.alive = False

    for i in range(SHOT_COUNT):
        shot = ctx.E("shot_%d" % i)

        if shot is not None:
            shot.alive = False
            shot.vy = 0

    for i in range(EXPLOSION_COUNT):
        explosion = ctx.E("explosion_%d" % i)

        if explosion is not None:
            explosion.alive = False
            gfx.set_gfx(explosion, [])

    for row in range(ENEMY_ROWS):
        for column in range(ENEMY_COLUMNS):
            enemy = ctx.E(
                "enemy_%d_%d" % (row, column)
            )

            if enemy is not None:
                enemy.alive = False


def check_game_end(ctx):
    if ctx.vars.get("game_state", "running") != "running":
        return

    enemies_alive = False
    enemies_landed = False

    for row in range(ENEMY_ROWS):
        for column in range(ENEMY_COLUMNS):
            enemy = ctx.E(
                "enemy_%d_%d" % (row, column)
            )

            if enemy is not None and enemy.alive:
                enemies_alive = True

                if enemy.y > 135:
                    enemies_landed = True

    if not enemies_alive:
        ctx.vars["game_state"] = "won"
        ctx.vars["status_text"] = "You win!"

        hide_playfield(ctx)

        ui.UI_HIDE(
            "hud_status",
            visible=True,
        )
        ui.UI_HIDE(
            "hud_restart",
            visible=True,
        )

    elif enemies_landed:
        ctx.vars["game_state"] = "lost"
        ctx.vars["status_text"] = "Game Over! The invaders have landed."

        hide_playfield(ctx)

        ui.UI_HIDE(
            "hud_status",
            visible=True,
        )
        ui.UI_HIDE(
            "hud_restart",
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
