import frameCraft as fc
import frameCraftGFX as gfx
import frameCraftUI as ui

# ============================================================
# Game constants
# ============================================================

# Frog starting position
FROG_START_X = 160
FROG_START_Y = 220

# Car dimensions in pixels
CAR_WIDTH = 46
CAR_HEIGHT = 20

# Number of cars per traffic lane
CARS_PER_LANE = 3


# ============================================================
# Graphics helpers
#
# GFX parts use the entity center as (0, 0):
#   P_RECT(x, y, w, h) -> x, y is the top-left corner
#   P_CIRCLE(x, y, r)  -> x, y is the circle center
#
# A centered rectangle starts at:
#   x = -(width // 2)
#   y = -(height // 2)
# ============================================================

def make_car_gfx(width, height, body_color, facing_right):
    """Create the graphics primitives for a car."""
    base_r, base_g, base_b = body_color

    # Use a brighter version of the body color for the center panel.
    highlight_color = (
        min(base_r + 70, 255),
        min(base_g + 70, 255),
        min(base_b + 70, 255),
    )

    origin_x = -(width // 2)
    origin_y = -(height // 2)

    panel_width = width - 12
    panel_height = height - 8
    panel_x = -(panel_width // 2)
    panel_y = -(panel_height // 2)

    light_width = 4
    light_height = height - 4
    light_y = -(light_height // 2)

    if facing_right:
        front_light_x = (width // 2) - light_width
        rear_light_x = origin_x
    else:
        front_light_x = origin_x
        rear_light_x = (width // 2) - light_width

    wheel_width = 5
    wheel_height = 5

    return [
        gfx.P_RECT(
            origin_x,
            origin_y,
            width,
            height,
            fill=body_color,
        ),
        gfx.P_RECT(
            panel_x,
            panel_y,
            panel_width,
            panel_height,
            fill=highlight_color,
        ),
        gfx.P_RECT(
            front_light_x,
            light_y,
            light_width,
            light_height,
            fill=(255, 245, 140),
        ),
        gfx.P_RECT(
            rear_light_x,
            light_y,
            light_width,
            light_height,
            fill=(210, 40, 40),
        ),
        gfx.P_RECT(
            origin_x,
            origin_y,
            wheel_width,
            wheel_height,
            fill=(30, 30, 30),
        ),
        gfx.P_RECT(
            (width // 2) - wheel_width,
            origin_y,
            wheel_width,
            wheel_height,
            fill=(30, 30, 30),
        ),
        gfx.P_RECT(
            origin_x,
            (height // 2) - wheel_height,
            wheel_width,
            wheel_height,
            fill=(30, 30, 30),
        ),
        gfx.P_RECT(
            (width // 2) - wheel_width,
            (height // 2) - wheel_height,
            wheel_width,
            wheel_height,
            fill=(30, 30, 30),
        ),
    ]


def make_frog_gfx():
    """Create the graphics primitives for the frog."""
    green_mid = (65, 210, 65)
    green_light = (48, 185, 48)
    green_dark = (32, 150, 32)
    eye_white = (220, 255, 210)
    pupil_dark = (20, 20, 20)

    return [
        # Body
        gfx.P_RECT(
            -7,
            -3,
            14,
            9,
            fill=green_light,
        ),
        # Head
        gfx.P_RECT(
            -5,
            -9,
            10,
            6,
            fill=green_mid,
        ),
        # Left eye
        gfx.P_CIRCLE(
            -4,
            -10,
            4,
            fill=eye_white,
        ),
        gfx.P_CIRCLE(
            -4,
            -10,
            2,
            fill=pupil_dark,
        ),
        # Right eye
        gfx.P_CIRCLE(
            4,
            -10,
            4,
            fill=eye_white,
        ),
        gfx.P_CIRCLE(
            4,
            -10,
            2,
            fill=pupil_dark,
        ),
        # Front legs
        gfx.P_RECT(
            -11,
            -5,
            5,
            3,
            fill=green_dark,
        ),
        gfx.P_RECT(
            6,
            -5,
            5,
            3,
            fill=green_dark,
        ),
        # Back legs
        gfx.P_RECT(
            -12,
            4,
            5,
            5,
            fill=green_dark,
        ),
        gfx.P_RECT(
            7,
            4,
            5,
            5,
            fill=green_dark,
        ),
    ]


# ============================================================
# Game and scene setup
# ============================================================

fc.GAME(
    "Frogger",
    window=(320, 200),
    fps=30,
    background=(50, 130, 50),
)

fc.SCENE(
    "main",
    lives=5,
    score=0,
    step_size=32,
    game_over=False,
    won=False,
    restart_latch=False,
    end_screen_shown=False,
)


# ============================================================
# Scene construction helpers
# ============================================================

def create_background_strip(
    ctx,
    name,
    center_y,
    strip_height,
    color,
):
    """Create a colored background strip such as a road."""
    window_width, _window_height = ctx.window

    fc.ENTITY(
        name,
        pos=(0, center_y),
    )

    fc.RECT(
        name,
        window_width,
        strip_height,
    )

    entity = ctx.E(name)

    if entity is not None:
        gfx.set_gfx(
            entity,
            [
                gfx.P_RECT(
                    0,
                    0,
                    window_width,
                    strip_height,
                    fill=color,
                )
            ],
        )


def create_lane_markings(
    ctx,
    window_width,
    lane_y,
    name_prefix,
):
    """Create dashed lane markings across the screen."""
    for x in range(0, window_width, 32):
        marking_name = name_prefix + str(x)

        fc.ENTITY(
            marking_name,
            pos=(x + 4, lane_y),
        )

        fc.RECT(
            marking_name,
            16,
            3,
        )

        entity = ctx.E(marking_name)

        if entity is not None:
            gfx.set_gfx(
                entity,
                [
                    gfx.P_RECT(
                        0,
                        0,
                        16,
                        3,
                        fill=(255, 255, 180),
                    )
                ],
            )


def create_cars_for_lane(
    ctx,
    lane_index,
    lane_y,
    velocity_x,
    body_color,
    window_width,
):
    """Create all cars for one traffic lane."""
    car_spacing = window_width // CARS_PER_LANE

    for car_index in range(CARS_PER_LANE):
        car_name = (
            "car_"
            + str(lane_index)
            + "_"
            + str(car_index)
        )

        # Offset each lane so cars do not start directly above each other.
        start_x = (
            car_index * car_spacing
            + lane_index * 28
            + 20
        ) % window_width

        fc.ENTITY(
            car_name,
            pos=(start_x, lane_y),
            tag="car",
        )

        fc.RECT(
            car_name,
            CAR_WIDTH,
            CAR_HEIGHT,
            trigger=True,
        )

        fc.VEL(
            car_name,
            velocity_x,
            0,
        )

        entity = ctx.E(car_name)

        if entity is not None:
            gfx.set_gfx(
                entity,
                make_car_gfx(
                    CAR_WIDTH,
                    CAR_HEIGHT,
                    body_color,
                    velocity_x > 0,
                ),
            )


# ============================================================
# Scene build
# ============================================================

@fc.SCENE_BUILD("main")
def build_scene(ctx):
    # RESET rebuilds the scene, so explicitly restore the game state here.
    ctx.vars["lives"] = 5
    ctx.vars["score"] = 0
    ctx.vars["step_size"] = 32
    ctx.vars["game_over"] = False
    ctx.vars["won"] = False
    ctx.vars["restart_latch"] = False
    ctx.vars["end_screen_shown"] = False

    window_width, window_height = ctx.window

    # Keyboard controls
    fc.BIND(
        "up",
        ["up", "w"],
    )
    fc.BIND(
        "down",
        ["down", "s"],
    )
    fc.BIND(
        "left",
        ["left", "a"],
    )
    fc.BIND(
        "right",
        ["right", "d"],
    )
    fc.BIND(
        "restart",
        ["r", "return"],
    )

    # Virtual controls for touch and mouse input
    fc.VBUTTON(
        "btn_up",
        "up",
        (4, window_height - 68, 36, 28),
        label="^",
    )

    fc.VBUTTON(
        "btn_down",
        "down",
        (4, window_height - 36, 36, 28),
        label="v",
    )

    fc.VBUTTON(
        "btn_left",
        "left",
        (window_width - 80, window_height - 36, 36, 28),
        label="<",
    )

    fc.VBUTTON(
        "btn_right",
        "right",
        (window_width - 40, window_height - 36, 36, 28),
        label=">",
    )

    fc.VBUTTON(
        "btn_restart",
        "restart",
        (
            window_width // 2 - 52,
            window_height // 2 + 18,
            104,
            30,
        ),
        label="Restart [R]",
        visible=False,
    )

    # Roads and goal strip
    create_background_strip(
        ctx,
        "road_1",
        115,
        64,
        (68, 68, 78),
    )

    create_background_strip(
        ctx,
        "road_2",
        20,
        64,
        (68, 68, 78),
    )

    create_background_strip(
        ctx,
        "goal_strip",
        4,
        8,
        (235, 205, 0),
    )

    # Lane markings
    create_lane_markings(
        ctx,
        window_width,
        146,
        "lane_marking_1_",
    )

    create_lane_markings(
        ctx,
        window_width,
        50,
        "lane_marking_2_",
    )

    # Player frog
    fc.ENTITY(
        "frog",
        pos=(FROG_START_X, FROG_START_Y),
        tag="frog",
    )

    fc.RECT(
        "frog",
        24,
        24,
        trigger=True,
    )

    frog = ctx.E("frog")

    if frog is not None:
        gfx.set_gfx(
            frog,
            make_frog_gfx(),
        )

    # Each tuple contains:
    # (y position, horizontal velocity, car color)
    lane_data = [
        (160, 88, (200, 45, 45)),
        (130, -75, (210, 140, 25)),
        (68, 105, (40, 100, 210)),
        (35, -65, (155, 40, 195)),
    ]

    for lane_index, (
        lane_y,
        velocity_x,
        body_color,
    ) in enumerate(lane_data):
        create_cars_for_lane(
            ctx,
            lane_index,
            lane_y,
            velocity_x,
            body_color,
            window_width,
        )

    # HUD: lives
    ui.UI_TEXT(
        "hud_lives",
        6,
        5,
        bind=lambda c: (
            "Lives: "
            + str(c.vars["lives"])
        ),
        size=12,
        color=(255, 255, 255),
        bg=(20, 20, 45),
        border=(80, 100, 200),
        border_w=1,
        pad=3,
        anchor="topleft",
        z=15,
    )

    # HUD: score
    ui.UI_TEXT(
        "hud_score",
        window_width - 6,
        5,
        bind=lambda c: (
            "Score: "
            + str(c.vars["score"])
        ),
        size=12,
        color=(255, 255, 255),
        bg=(20, 20, 45),
        border=(80, 100, 200),
        border_w=1,
        pad=3,
        anchor="topright",
        z=15,
    )

    # End screen
    ui.UI_TEXT(
        "end_message",
        window_width // 2,
        window_height // 2 - 22,
        bind=lambda c: (
            "Game Over!"
            if c.vars["game_over"]
            else (
                "Goal reached!"
                if c.vars["won"]
                else ""
            )
        ),
        size=18,
        color=(255, 240, 60),
        bg=(40, 10, 10),
        border=(200, 50, 50),
        border_w=2,
        pad=6,
        anchor="center",
        z=20,
    )

    ui.UI_TEXT(
        "bonus_message",
        window_width // 2,
        window_height // 2 - 2,
        bind=lambda c: (
            "+100 points!"
            if c.vars["won"]
            else ""
        ),
        size=11,
        color=(80, 255, 80),
        bg=(10, 40, 10),
        border=(50, 200, 50),
        border_w=1,
        pad=4,
        anchor="center",
        z=20,
    )

    ui.UI_TEXT(
        "restart_hint",
        window_width // 2,
        window_height // 2 + 14,
        bind=lambda c: (
            "Press R or use the Restart button"
            if (
                c.vars["game_over"]
                or c.vars["won"]
            )
            else ""
        ),
        size=9,
        color=(220, 220, 220),
        bg=(35, 35, 35),
        border=(130, 130, 130),
        border_w=1,
        pad=3,
        anchor="center",
        z=20,
    )

    # ========================================================
    # Game rules
    # ========================================================

    def move_frog(ctx):
        if ctx.vars["game_over"] or ctx.vars["won"]:
            return

        frog_entity = ctx.E("frog")

        if frog_entity is None:
            return

        step_size = ctx.vars.get(
            "step_size",
            32,
        )

        if ctx.pressed("up"):
            frog_entity.y -= step_size

        elif ctx.pressed("down"):
            frog_entity.y += step_size

        elif ctx.pressed("left"):
            frog_entity.x -= step_size

        elif ctx.pressed("right"):
            frog_entity.x += step_size

        # Keep the frog inside the visible play area.
        if frog_entity.x < 14:
            frog_entity.x = 14

        if frog_entity.x > window_width - 14:
            frog_entity.x = window_width - 14

        if frog_entity.y < 6:
            frog_entity.y = 6

        if frog_entity.y > window_height - 14:
            frog_entity.y = window_height - 14

    fc.RULE(move_frog)

    def move_cars(ctx):
        # dt-based movement keeps car speed independent of frame rate.
        for lane_index in range(4):
            for car_index in range(CARS_PER_LANE):
                car = ctx.E(
                    "car_"
                    + str(lane_index)
                    + "_"
                    + str(car_index)
                )

                if car is None:
                    continue

                car.x += car.vx * ctx.dt

                # Wrap cars around when they leave the screen.
                if (
                    car.vx > 0
                    and car.x > window_width + CAR_WIDTH
                ):
                    car.x = -CAR_WIDTH

                elif (
                    car.vx < 0
                    and car.x < -CAR_WIDTH
                ):
                    car.x = window_width + CAR_WIDTH

    fc.RULE(move_cars)

    def check_goal(ctx):
        if ctx.vars["game_over"] or ctx.vars["won"]:
            return

        frog_entity = ctx.E("frog")

        if frog_entity is None:
            return

        if frog_entity.y <= 14:
            ctx.vars["won"] = True
            ctx.vars["score"] += 100

    fc.RULE(check_goal)

    def show_end_ui(ctx):
        # Show the restart button only once after the game ends.
        if ctx.vars["end_screen_shown"]:
            return

        if not (
            ctx.vars["game_over"]
            or ctx.vars["won"]
        ):
            return

        ctx.vars["end_screen_shown"] = True

        fc.VBUTTON(
            "btn_restart",
            "restart",
            (
                window_width // 2 - 52,
                window_height // 2 + 18,
                104,
                30,
            ),
            label="Restart [R]",
            visible=True,
        )

    fc.RULE(show_end_ui)

    def check_restart(ctx):
        # The latch prevents a held restart input from triggering every frame.
        if not (
            ctx.vars["game_over"]
            or ctx.vars["won"]
        ):
            ctx.vars["restart_latch"] = False
            return

        if not ctx.down("restart"):
            ctx.vars["restart_latch"] = False
            return

        if not ctx.vars["restart_latch"]:
            ctx.vars["restart_latch"] = True
            fc.RESET("main")

    fc.RULE(check_restart)

    def car_collision(ctx, frog_entity, car_entity):
        if ctx.vars["game_over"] or ctx.vars["won"]:
            return

        ctx.vars["lives"] -= 1

        frog = ctx.E("frog")

        if ctx.vars["lives"] <= 0:
            ctx.vars["game_over"] = True

            if frog is not None:
                frog.alive = False

        else:
            if frog is not None:
                frog.x = FROG_START_X
                frog.y = FROG_START_Y

    fc.ON_COLLIDE(
        "frog",
        "car",
        car_collision,
    )


fc.START_STANDALONE("main")
