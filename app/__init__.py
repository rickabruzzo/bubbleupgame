import sys, os, gc, time
sys.path.insert(0, "/system/apps/bubbleup")
os.chdir("/system/apps/bubbleup")
from badgeware import run
mode(HIRES)
large_font = rom_font.yesterday
small_font = rom_font.nope
IMG_LOGOMARK   = image.load("assets/hc_logomark.png")
IMG_LOGO_WHITE = image.load("assets/hc_logo_white.png")
IMG_SPLASH_BG  = image.load("assets/splash_bg.png")

# ---------------------------------------------------------------------------
# Honeycomb brand colors
# ---------------------------------------------------------------------------
COL_SLATE   = color.rgb(37,  48,  62)
COL_COBALT  = color.rgb(2,   120, 205)
COL_PACIFIC = color.rgb(2,   152, 236)
COL_LIME    = color.rgb(100, 186, 0)
COL_HONEY   = color.rgb(255, 176, 0)
COL_TANGO   = color.rgb(249, 110, 16)
COL_INDIGO  = color.rgb(81,  54,  141)
COL_DENIM   = color.rgb(1,   72,  123)
COL_WHITE   = color.rgb(220, 240, 255)
COL_DIM     = color.rgb(80,  80,  80)
COL_DARK    = color.rgb(8,   12,  20)
COL_NAVY    = color.rgb(20,  30,  50)

# ---------------------------------------------------------------------------
# Game states
# ---------------------------------------------------------------------------
class GS:
    HOME     = 0
    BUBBLEUP = 1
    TRACE    = 2
    GAMEOVER = 3
    SPLASH   = 4
    HEATMAP  = 5
    INTRO    = 6

# ---------------------------------------------------------------------------
# Board templates
# ---------------------------------------------------------------------------
BOARD_TEMPLATES = [
    {
        "label": "frontend",
        "heatmap":      [4, 7, 5, 8, 6, 38, 7, 4, 6, 8],
        "hmap_spike_idx": 5,
        "attributes": [
            {"name": "http.route",   "bars": [3, 5, 4, 6], "spike": True,  "spike_idx": 2},
            {"name": "browser.name", "bars": [4, 6, 3, 7], "spike": False, "spike_idx": -1},
            {"name": "user.region",  "bars": [5, 3, 6, 4], "spike": False, "spike_idx": -1},
            {"name": "app.version",  "bars": [6, 4, 5, 3], "spike": False, "spike_idx": -1},
        ],
        "trace_spans": [
            {"name": "frontend-web",  "service": "frontend", "duration_ms": 120,  "culprit": False},
            {"name": "api-gateway",   "service": "frontend", "duration_ms": 85,   "culprit": False},
            {"name": "render-svc",    "service": "frontend", "duration_ms": 4800, "culprit": True},
            {"name": "cache-lookup",  "service": "checkout", "duration_ms": 40,   "culprit": False},
            {"name": "db-query",      "service": "db",       "duration_ms": 95,   "culprit": False},
            {"name": "cdn-fetch",     "service": "frontend", "duration_ms": 60,   "culprit": False},
        ],
    },
    {
        "label": "checkout",
        "heatmap":      [5, 3, 39, 6, 4, 8, 5, 7, 6, 4],
        "hmap_spike_idx": 2,
        "attributes": [
            {"name": "payment.method",  "bars": [4, 7, 5, 6], "spike": False, "spike_idx": -1},
            {"name": "cart.item_count", "bars": [6, 4, 7, 3], "spike": True,  "spike_idx": 1},
            {"name": "geo.country",     "bars": [3, 6, 4, 7], "spike": False, "spike_idx": -1},
            {"name": "session.type",    "bars": [7, 5, 3, 6], "spike": False, "spike_idx": -1},
        ],
        "trace_spans": [
            {"name": "checkout-ui",  "service": "checkout", "duration_ms": 110,  "culprit": False},
            {"name": "pricing-svc",  "service": "checkout", "duration_ms": 75,   "culprit": False},
            {"name": "inventory-db", "service": "db",       "duration_ms": 4200, "culprit": True},
            {"name": "tax-calc",     "service": "checkout", "duration_ms": 55,   "culprit": False},
            {"name": "fraud-check",  "service": "frontend", "duration_ms": 130,  "culprit": False},
            {"name": "cart-persist", "service": "db",       "duration_ms": 90,   "culprit": False},
        ],
    },
    {
        "label": "payments",
        "heatmap":      [6, 4, 5, 7, 8, 4, 6, 5, 40, 4],
        "hmap_spike_idx": 8,
        "attributes": [
            {"name": "error.type",    "bars": [5, 3, 7, 4], "spike": False, "spike_idx": -1},
            {"name": "db.table",      "bars": [4, 6, 5, 7], "spike": False, "spike_idx": -1},
            {"name": "provider.name", "bars": [7, 4, 6, 3], "spike": False, "spike_idx": -1},
            {"name": "txn.currency",  "bars": [3, 7, 4, 6], "spike": True,  "spike_idx": 3},
        ],
        "trace_spans": [
            {"name": "pay-gateway",  "service": "checkout", "duration_ms": 95,   "culprit": False},
            {"name": "stripe-call",  "service": "frontend", "duration_ms": 150,  "culprit": False},
            {"name": "ledger-write", "service": "db",       "duration_ms": 80,   "culprit": False},
            {"name": "pay-auth-svc", "service": "checkout", "duration_ms": 4600, "culprit": True},
            {"name": "receipt-gen",  "service": "frontend", "duration_ms": 45,   "culprit": False},
            {"name": "notify-svc",   "service": "checkout", "duration_ms": 70,   "culprit": False},
        ],
    },
    {
        "label": "auth",
        "heatmap":      [3, 41, 4, 7, 5, 4, 6, 3, 5, 7],
        "hmap_spike_idx": 1,
        "attributes": [
            {"name": "auth.method", "bars": [6, 4, 5, 3], "spike": False, "spike_idx": -1},
            {"name": "user.tier",   "bars": [3, 5, 4, 6], "spike": False, "spike_idx": -1},
            {"name": "region.code", "bars": [5, 3, 6, 4], "spike": False, "spike_idx": -1},
            {"name": "token.type",  "bars": [4, 6, 3, 5], "spike": True,  "spike_idx": 0},
        ],
        "trace_spans": [
            {"name": "auth-gateway",  "service": "frontend", "duration_ms": 80,   "culprit": False},
            {"name": "token-verify",  "service": "checkout", "duration_ms": 55,   "culprit": False},
            {"name": "session-store", "service": "db",       "duration_ms": 70,   "culprit": False},
            {"name": "rate-limiter",  "service": "checkout", "duration_ms": 45,   "culprit": False},
            {"name": "jwt-decode",    "service": "frontend", "duration_ms": 4900, "culprit": True},
            {"name": "audit-log",     "service": "db",       "duration_ms": 60,   "culprit": False},
        ],
    },
]

# ---------------------------------------------------------------------------
# Active game state
# ---------------------------------------------------------------------------
boards         = []    # list of active board dicts: {template, start_ms, timer_ms}
score          = 0
timeouts       = 0
round_num      = 0
MAX_TIMEOUTS   = 5
BASE_TIMER     = 45000  # 45 s

selected_board    = [0]
selected_attr     = [0]
selected_span     = [0]
selected_hmap_bar = [0]
state             = [GS.HOME]
active_board   = [None]   # board dict currently being investigated

blink_timer      = [0]        # for GAMEOVER blink
flash_timer      = [0]        # flash on wrong selection
flash_type       = [0]        # 0 = error (red), 1 = neutral (no anomaly), 2 = success (green)
flash_next_state = [GS.HOME]  # state to go to after flash clears
success_board    = [None]     # board ref held during success flash
FLASH_DURATION   = 1200       # ms for error/neutral
SUCCESS_DURATION = 4000       # ms for success overlay
board_count      = [0]        # ever-incrementing counter for template rotation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _now():
    return time.ticks_ms()


def _board_timer_ms():
    """Return timer duration for the next board added."""
    if round_num < 8:
        return BASE_TIMER
    factor = max(0.4, 1.0 - (round_num - 8) * 0.05)
    return int(BASE_TIMER * factor)


def _add_board():
    idx = board_count[0] % len(BOARD_TEMPLATES)
    board_count[0] += 1
    tmpl = BOARD_TEMPLATES[idx]
    boards.append({
        "template": tmpl,
        "start_ms": _now(),
        "timer_ms": _board_timer_ms(),
    })


def _remove_board(board):
    if board in boards:
        boards.remove(board)


def _service_color(service_key):
    if service_key == "frontend":
        return COL_COBALT
    if service_key == "checkout":
        return COL_LIME
    return color.rgb(255, 100, 120)  # db — pinkish red


def _elapsed(board):
    return _now() - board["start_ms"]


def _remaining_frac(board):
    if "_paused_at" in board:
        elapsed = board["_paused_at"] - board["start_ms"]
    else:
        elapsed = _elapsed(board)
    return max(0.0, 1.0 - elapsed / board["timer_ms"])


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _pause_inactive_boards():
    """Freeze timers on ALL boards during investigation."""
    now = _now()
    for b in boards:
        b["_paused_at"] = now


def _resume_inactive_boards():
    """Unfreeze timers — extend start_ms by how long they were paused."""
    now = _now()
    for b in boards:
        if "_paused_at" in b:
            paused_duration = now - b["_paused_at"]
            b["start_ms"] += paused_duration
            del b["_paused_at"]


# Button guards ---------------------------------------------------------------
_prev_pressed = set()

def _update_prev_pressed():
    global _prev_pressed
    _prev_pressed = set(io.pressed)

def _just_pressed(name):
    btn = getattr(io, name, None)
    return btn is not None and btn in io.pressed and btn not in _prev_pressed

def _just_pressed_any(*names):
    return any(_just_pressed(n) for n in names)


# Screen dimensions
SW = 320
SH = 240
TOPBAR_H = 20

# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def _draw_topbar(label_left, label_right=None):
    """Draw the top status bar."""
    screen.pen = COL_SLATE
    screen.rectangle(0, 0, SW, TOPBAR_H)
    # Logomark left
    screen.blit(IMG_LOGOMARK, vec2(2, 2))
    # Screen label
    screen.pen = COL_WHITE
    screen.font = small_font
    screen.text(label_left, 22, 4)
    # Board label center
    if label_right:
        screen.pen = COL_PACIFIC
        screen.font = small_font
        screen.text(label_right, 110, 4)
    # Score
    score_str = "SCR:{}".format(score)
    screen.pen = COL_HONEY
    screen.font = small_font
    screen.text(score_str, 190, 4)
    # SLAs left label + pips
    screen.pen = COL_WHITE
    screen.font = small_font
    screen.text("SLAs:", 233, 4)
    remaining = MAX_TIMEOUTS - timeouts
    for i in range(MAX_TIMEOUTS):
        px = 270 + i * 9
        c = COL_PACIFIC if i < remaining else COL_TANGO
        screen.pen = c
        screen.rectangle(px, 7, 6, 6)


def _draw_timer_bar(board):
    """Draw a 10px countdown bar at the very bottom of the screen."""
    frac = _remaining_frac(board)
    bar_w = int(SW * frac)
    tc = _timer_color(frac)
    screen.pen = COL_DARK
    screen.rectangle(0, SH - 10, SW, 10)
    if bar_w > 0:
        screen.pen = tc
        screen.rectangle(0, SH - 10, bar_w, 10)
    secs_left = int(board["timer_ms"] * frac / 1000) + 1
    if secs_left <= 10:
        blink_on = frac > 0.1 or (((_now() // 250) % 2) == 0)
        if blink_on:
            screen.pen = COL_TANGO
            screen.font = small_font
            screen.text("{}s".format(secs_left), SW - 20, SH - 20)


def _draw_heatmap(hmap, x, y, w, h, spike_col=COL_HONEY):
    """
    Draw a heatmap of 20 columns inside rect (x, y, w, h).
    Baseline values 0–10, spike at 38–40.
    """
    n = len(hmap)
    col_w = max(1, w // n)
    max_val = 40
    for i, val in enumerate(hmap):
        col_h = int((val / max_val) * h)
        col_x = x + i * col_w
        col_y = y + h - col_h
        if val >= 30:
            c = spike_col
        else:
            # teal gradient: rgb(0, 180+v_scaled, 140)
            v = int((val / 10) * 60)
            c = color.rgb(0, _clamp(180 + v, 0, 255), 140)
        # draw as 2px-tall slices for the gradient feel
        for row in range(0, col_h, 2):
            screen.pen = c
            screen.rectangle(col_x, col_y + row, col_w - 1, min(2, col_h - row))


def _timer_color(frac):
    """Lime → Tango → Cobalt as frac drains 1→0."""
    if frac > 0.5:
        # Lime to Tango
        t = (1.0 - frac) * 2.0
        r = int(100 + t * (249 - 100))
        g = int(186 + t * (110 - 186))
        b = int(0   + t * (16  - 0))
        return color.rgb(r, g, b)
    else:
        # Tango to Cobalt
        t = (0.5 - frac) * 2.0
        r = int(249 + t * (2   - 249))
        g = int(110 + t * (120 - 110))
        b = int(16  + t * (205 - 16))
        return color.rgb(r, g, b)


# ---------------------------------------------------------------------------
# INTRO screen (BubbleUp explanation)
# ---------------------------------------------------------------------------
def _draw_intro():
    screen.pen = COL_SLATE
    screen.rectangle(0, 0, SW, SH)

    # Title bar
    screen.pen = COL_COBALT
    screen.rectangle(0, 0, SW, 28)
    screen.pen = COL_WHITE
    screen.font = large_font
    screen.text("BubbleUp", 88, 5)

    # Explanation box
    screen.pen = color.rgb(15, 22, 35)
    screen.rectangle(10, 38, 300, 140)
    screen.pen = COL_COBALT
    screen.rectangle(10, 38, 300, 2)
    screen.rectangle(10, 176, 300, 2)
    screen.rectangle(10, 38, 2, 140)
    screen.rectangle(308, 38, 2, 140)

    screen.pen = COL_WHITE
    screen.font = small_font
    screen.text("Anomaly alerts are firing.", 20, 50)
    screen.text("Use BubbleUp to find the root", 20, 66)
    screen.text("cause before your SLAs breach.", 20, 80)
    screen.pen = COL_HONEY
    screen.text("1. Select a spiking board", 20, 100)
    screen.text("2. Find the anomalous attribute", 20, 114)
    screen.text("3. Identify the culprit span", 20, 128)
    screen.pen = COL_TANGO
    screen.text("5 SLA breaches = game over.", 20, 152)

    # Prompt
    screen.pen = COL_LIME
    screen.font = small_font
    screen.text("Press B to begin", 100, 195)


def _handle_intro_input():
    if _just_pressed("BUTTON_B"):
        _maybe_add_boards()
        _prev_pressed.clear()
        state[0] = GS.HOME


# ---------------------------------------------------------------------------
# HOME screen
# ---------------------------------------------------------------------------
def _draw_home():
    screen.pen = COL_DARK
    screen.rectangle(0, 0, SW, SH)
    _draw_topbar("BUBBLEUP")

    n = len(boards)
    if n == 0:
        screen.pen = COL_DIM
        screen.font = small_font
        screen.text("Loading...", SW // 2 - 30, SH // 2)
        return

    avail_h = SH - TOPBAR_H
    strip_h = max(60, avail_h // n)

    for idx, board in enumerate(boards):
        tmpl = board["template"]
        sy = TOPBAR_H + idx * strip_h
        # Strip background
        bg = COL_NAVY if idx != selected_board[0] else color.rgb(30, 40, 60)
        screen.pen = bg
        screen.rectangle(0, sy, SW, strip_h)
        # Selection highlight border
        if idx == selected_board[0]:
            screen.pen = COL_TANGO
            screen.rectangle(0, sy, SW, 1)
            screen.pen = COL_TANGO
            screen.rectangle(0, sy + strip_h - 1, SW, 1)

        # Label
        screen.pen = COL_HONEY
        screen.font = small_font
        screen.text(tmpl["label"], 4, sy + 3)

        # Heatmap — leave 10px top margin for label, 8px bottom for timer bar
        hmap_y = sy + 14
        hmap_h = strip_h - 14 - 8
        if hmap_h > 4:
            _draw_heatmap(tmpl["heatmap"], 0, hmap_y, SW, hmap_h)

        # Countdown bar along the bottom of the strip
        frac = _remaining_frac(board)
        bar_w = int(SW * frac)
        tc = _timer_color(frac)
        screen.pen = COL_SLATE
        screen.rectangle(0, sy + strip_h - 10, SW, 10)
        if bar_w > 0:
            screen.pen = tc
            screen.rectangle(0, sy + strip_h - 10, bar_w, 10)
        # Seconds remaining label when under 10s
        secs_left = int(board["timer_ms"] * frac / 1000) + 1
        if secs_left <= 10:
            blink_on = frac > 0.1 or (((_now() // 250) % 2) == 0)
            if blink_on:
                screen.pen = COL_TANGO
                screen.font = small_font
                screen.text("{}s".format(secs_left), SW - 24, sy + strip_h - 20)


def _handle_home_input():
    global state

    n = len(boards)
    if n == 0:
        return

    if _just_pressed("BUTTON_UP"):
        selected_board[0] = (selected_board[0] - 1) % n
    if _just_pressed("BUTTON_DOWN"):
        selected_board[0] = (selected_board[0] + 1) % n

    if _just_pressed("BUTTON_B"):
        active_board[0] = boards[selected_board[0]]
        selected_hmap_bar[0] = 0
        flash_timer[0] = 0
        flash_type[0] = 0
        _pause_inactive_boards()
        _prev_pressed.clear()
        state[0] = GS.HEATMAP


# ---------------------------------------------------------------------------
# HEATMAP investigation screen
# ---------------------------------------------------------------------------
HMAP_N       = 10    # interactive bars
HMAP_BAR_W   = 22    # width of each interactive bar
HMAP_BAR_GAP = 4     # gap between bars
HMAP_X_START = (SW - HMAP_N * (HMAP_BAR_W + HMAP_BAR_GAP)) // 2
HMAP_DECOR   = [3, 5, 4]  # decorative flanking bar heights (dim)

def _draw_heatmap_screen():
    board = active_board[0]
    if board is None:
        state[0] = GS.HOME
        return

    tmpl = board["template"]
    screen.pen = COL_DARK
    screen.rectangle(0, 0, SW, SH)
    _draw_topbar("HEATMAP", tmpl["label"])

    hmap = tmpl["heatmap"]
    max_val = 42
    bar_area_top = TOPBAR_H + 20
    bar_area_h = SH - bar_area_top - 30

    # Prompt
    screen.pen = COL_WHITE
    screen.font = small_font
    screen.text("Find the anomaly  A/C:move  B:select", 10, TOPBAR_H + 6)

    # Decorative left bars
    for i, dh in enumerate(HMAP_DECOR):
        bh = max(4, int((dh / 10) * bar_area_h // 2))
        bx = HMAP_X_START - (len(HMAP_DECOR) - i) * (HMAP_BAR_W + HMAP_BAR_GAP)
        by = bar_area_top + bar_area_h - bh
        screen.pen = COL_DIM
        screen.rectangle(bx, by, HMAP_BAR_W, bh)

    # Decorative right bars
    right_x = HMAP_X_START + HMAP_N * (HMAP_BAR_W + HMAP_BAR_GAP)
    for i, dh in enumerate(HMAP_DECOR):
        bh = max(4, int((dh / 10) * bar_area_h // 2))
        bx = right_x + i * (HMAP_BAR_W + HMAP_BAR_GAP)
        by = bar_area_top + bar_area_h - bh
        screen.pen = COL_DIM
        screen.rectangle(bx, by, HMAP_BAR_W, bh)

    # Interactive bars
    for i, val in enumerate(hmap):
        bx = HMAP_X_START + i * (HMAP_BAR_W + HMAP_BAR_GAP)
        if val >= 30:
            bh = int((val / max_val) * bar_area_h)
            c = COL_HONEY
        else:
            bh = max(4, int((val / 10) * bar_area_h // 2))
            v = int((val / 10) * 60)
            c = color.rgb(0, _clamp(180 + v, 0, 255), 140)
        bh = min(bh, bar_area_h)
        by = bar_area_top + bar_area_h - bh
        screen.pen = c
        screen.rectangle(bx, by, HMAP_BAR_W, bh)

        # Cursor highlight — Tango border around selected bar
        if i == selected_hmap_bar[0]:
            screen.pen = COL_TANGO
            screen.rectangle(bx - 1, by - 1, HMAP_BAR_W + 2, 2)
            screen.rectangle(bx - 1, by + bh, HMAP_BAR_W + 2, 2)
            screen.rectangle(bx - 1, by - 1, 2, bh + 2)
            screen.rectangle(bx + HMAP_BAR_W, by - 1, 2, bh + 2)

    _draw_timer_bar(board)


def _handle_heatmap_input():
    board = active_board[0]
    if board is None:
        state[0] = GS.HOME
        return

    if _just_pressed("BUTTON_A"):
        if selected_hmap_bar[0] > 0:
            selected_hmap_bar[0] -= 1
    if _just_pressed("BUTTON_C"):
        if selected_hmap_bar[0] < HMAP_N - 1:
            selected_hmap_bar[0] += 1

    if _just_pressed("BUTTON_B"):
        spike_idx = board["template"]["hmap_spike_idx"]
        if selected_hmap_bar[0] == spike_idx:
            # Correct bar — go to BubbleUp
            selected_attr[0] = 0
            flash_timer[0] = 0
            flash_type[0] = 0
            _prev_pressed.clear()
            state[0] = GS.BUBBLEUP
        else:
            # Wrong bar — neutral flash
            flash_timer[0] = _now()
            flash_type[0] = 1


# ---------------------------------------------------------------------------
# BUBBLEUP screen (attribute cards)
# ---------------------------------------------------------------------------
CARD_COLS  = 2
CARD_ROWS  = 2
CARD_PAD   = 4
BAR_MAX_H  = 40   # max bar height in pixels for baseline (value 10)
SPIKE_H    = 70   # bar height in pixels for spike bar

def _draw_bubbleup():
    board = active_board[0]
    if board is None:
        state[0] = GS.HOME
        return

    tmpl = board["template"]
    screen.pen = COL_SLATE
    screen.rectangle(0, 0, SW, SH)
    _draw_topbar("BUBBLEUP", tmpl["label"])

    attrs = tmpl["attributes"]
    grid_y = TOPBAR_H + CARD_PAD
    grid_h = SH - TOPBAR_H - CARD_PAD * 2
    grid_w = SW - CARD_PAD * 2

    card_w = (grid_w - CARD_PAD) // CARD_COLS
    card_h = (grid_h - CARD_PAD) // CARD_ROWS

    for i, attr in enumerate(attrs):
        row = i // CARD_COLS
        col = i % CARD_COLS
        cx = CARD_PAD + col * (card_w + CARD_PAD)
        cy = grid_y + row * (card_h + CARD_PAD)

        # Card background
        screen.pen = COL_DARK
        screen.rectangle(cx, cy, card_w, card_h)

        # Border — Tango if selected, else Cobalt
        bc = COL_TANGO if i == selected_attr[0] else COL_COBALT
        screen.pen = bc
        screen.rectangle(cx, cy, card_w, 1)
        screen.pen = bc
        screen.rectangle(cx, cy + card_h - 1, card_w, 1)
        screen.pen = bc
        screen.rectangle(cx, cy, 1, card_h)
        screen.pen = bc
        screen.rectangle(cx + card_w - 1, cy, 1, card_h)

        # Card label
        screen.pen = COL_HONEY
        screen.font = small_font
        screen.text(attr["name"], cx + 3, cy + 3)

        # Bars
        n_bars = len(attr["bars"])
        bar_area_w = card_w - 8
        bar_area_h = card_h - 20
        bar_w = max(4, (bar_area_w - (n_bars - 1) * 2) // n_bars)
        bar_baseline = cy + card_h - 6

        for j, val in enumerate(attr["bars"]):
            bx = cx + 4 + j * (bar_w + 2)
            is_spike_bar = attr["spike"] and j == attr.get("spike_idx", -1)
            if is_spike_bar:
                bh = min(SPIKE_H, bar_area_h)
                bc2 = COL_HONEY
            else:
                bh = max(2, int((val / 10) * BAR_MAX_H))
                bh = min(bh, bar_area_h)
                bc2 = COL_DENIM
            by = bar_baseline - bh
            screen.pen = bc2
            screen.rectangle(bx, by, bar_w, bh)

    _draw_timer_bar(board)


def _handle_bubbleup_input():
    global state

    board = active_board[0]
    if board is None:
        state[0] = GS.HOME
        return

    # Navigate 2×2 grid
    if _just_pressed("BUTTON_UP"):
        if selected_attr[0] >= CARD_COLS:
            selected_attr[0] -= CARD_COLS
    if _just_pressed("BUTTON_DOWN"):
        if selected_attr[0] + CARD_COLS < 4:
            selected_attr[0] += CARD_COLS
    if _just_pressed("BUTTON_A"):
        if selected_attr[0] % CARD_COLS > 0:
            selected_attr[0] -= 1
    if _just_pressed("BUTTON_C"):
        if selected_attr[0] % CARD_COLS < CARD_COLS - 1:
            selected_attr[0] += 1

    if _just_pressed("BUTTON_B"):
        attr = board["template"]["attributes"][selected_attr[0]]
        if attr["spike"]:
            # Correct card — go to TRACE
            selected_span[0] = 0
            state[0] = GS.TRACE
        else:
            # No anomaly here — neutral overlay
            flash_timer[0] = _now()
            flash_type[0] = 1


# ---------------------------------------------------------------------------
# TRACE screen
# ---------------------------------------------------------------------------
SPAN_H     = 30   # height of each span row
TRACE_MAX  = 5000 # ms reference for bar width

def _draw_trace():
    board = active_board[0]
    if board is None and success_board[0] is None:
        state[0] = GS.HOME
        return
    if board is None:
        board = success_board[0]

    tmpl = board["template"]
    screen.pen = COL_SLATE
    screen.rectangle(0, 0, SW, SH)
    _draw_topbar("TRACE", tmpl["label"])

    spans = tmpl["trace_spans"]
    list_y = TOPBAR_H + 4

    for i, span in enumerate(spans):
        sy = list_y + i * SPAN_H
        is_sel = i == selected_span[0]

        # Row background
        bg = color.rgb(30, 40, 60) if is_sel else COL_DARK
        screen.pen = bg
        screen.rectangle(0, sy, SW, SPAN_H - 1)

        # Tango left border if selected
        if is_sel:
            screen.pen = COL_TANGO
            screen.rectangle(0, sy, 3, SPAN_H - 1)

        # Service color dot (6×6)
        sc = _service_color(span["service"])
        screen.pen = sc
        screen.rectangle(6, sy + 12, 6, 6)

        # Span name — left portion
        name = span["name"]
        screen.pen = COL_WHITE
        screen.font = small_font
        screen.text(name, 16, sy + 4)

        # Duration ms label
        dur_str = "{}ms".format(span["duration_ms"])
        screen.pen = COL_DIM
        screen.font = small_font
        screen.text(dur_str, 16, sy + 16)

        # Horizontal duration bar
        bar_x = 110
        bar_w_max = SW - bar_x - 4
        frac = min(1.0, span["duration_ms"] / TRACE_MAX)
        bw = max(2, int(frac * bar_w_max))
        bar_y = sy + 10
        bar_h = 10
        screen.pen = color.rgb(20, 25, 35)
        screen.rectangle(bar_x, bar_y, bar_w_max, bar_h)
        screen.pen = sc
        screen.rectangle(bar_x, bar_y, bw, bar_h)

    _draw_timer_bar(board)


def _handle_trace_input():
    global score, round_num, timeouts

    # Don't process input during success flash
    if flash_type[0] == 2 and flash_timer[0] > 0:
        return

    board = active_board[0]
    if board is None:
        state[0] = GS.HOME
        return

    spans = board["template"]["trace_spans"]
    n = len(spans)

    if _just_pressed("BUTTON_UP"):
        selected_span[0] = (selected_span[0] - 1) % n
    if _just_pressed("BUTTON_DOWN"):
        selected_span[0] = (selected_span[0] + 1) % n

    if _just_pressed("BUTTON_B"):
        span = spans[selected_span[0]]
        if span["culprit"]:
            # Correct! Show success overlay then go home
            score += 1
            round_num += 1
            _remove_board(board)
            success_board[0] = board
            active_board[0] = None
            _resume_inactive_boards()
            _maybe_add_boards()
            selected_board[0] = 0
            flash_timer[0] = _now()
            flash_type[0] = 2
            flash_next_state[0] = GS.HOME
            state[0] = GS.TRACE
        else:
            # Wrong span — neutral overlay, stay on TRACE
            flash_timer[0] = _now()
            flash_type[0] = 1


# ---------------------------------------------------------------------------
# Board management
# ---------------------------------------------------------------------------
def _maybe_add_boards():
    """Add boards based on current round_num."""
    target = 1
    if round_num >= 2:
        target = 2
    if round_num >= 4:
        target = 3
    while len(boards) < target:
        _add_board()


def _check_timeouts():
    global timeouts
    now = _now()
    # Don't expire boards while player is actively investigating
    if state[0] in (GS.HEATMAP, GS.BUBBLEUP, GS.TRACE):
        return
    expired = [b for b in boards if (now - b["start_ms"]) >= b["timer_ms"]]
    for b in expired:
        timeouts += 1
        _remove_board(b)
        if active_board[0] is b:
            active_board[0] = None
            _resume_inactive_boards()
            state[0] = GS.HOME
        if timeouts >= MAX_TIMEOUTS:
            state[0] = GS.GAMEOVER
            return
        _add_board()


# ---------------------------------------------------------------------------
# GAMEOVER screen
# ---------------------------------------------------------------------------
def _draw_gameover():
    screen.pen = COL_DARK
    screen.rectangle(0, 0, SW, SH)

    # GAME OVER — centered at x=97 (9 chars × 14px = 126, (320-126)//2 = 97)
    screen.pen = COL_TANGO
    screen.font = large_font
    screen.text("GAME OVER", 97, 25)

    # Congratulatory line
    if score >= 6:
        msg = "Outstanding work!"
    elif score >= 3:
        msg = "Good instincts!"
    else:
        msg = "Keep investigating."
    msg_x = (SW - len(msg) * 8) // 2
    screen.pen = COL_WHITE
    screen.font = small_font
    screen.text(msg, msg_x, 62)

    # Score — centered (8 chars base + digits, 14px large_font)
    score_line = "SCORE: {}".format(score)
    score_x = (SW - len(score_line) * 14) // 2
    screen.pen = COL_HONEY
    screen.font = large_font
    screen.text(score_line, score_x, 88)

    # Issues discovered — centered
    issues_line = "ISSUES DISCOVERED: {}".format(score)
    issues_x = (SW - len(issues_line) * 8) // 2
    screen.pen = COL_WHITE
    screen.font = small_font
    screen.text(issues_line, issues_x, 130)

    # Static prompt — centered, B only
    prompt = "Press B to try again."
    prompt_x = (SW - len(prompt) * 8) // 2
    screen.pen = COL_LIME
    screen.font = small_font
    screen.text(prompt, prompt_x, 185)


def _handle_gameover_input():
    global score, timeouts, round_num, boards, state

    if _just_pressed("BUTTON_B"):
        # Reset game
        score     = 0
        timeouts  = 0
        round_num = 0
        boards.clear()
        board_count[0]   = 0
        active_board[0]  = None
        success_board[0] = None
        selected_board[0]    = 0
        selected_attr[0]     = 0
        selected_span[0]     = 0
        selected_hmap_bar[0] = 0
        blink_timer[0] = _now()
        flash_timer[0] = 0
        state[0] = GS.SPLASH


# ---------------------------------------------------------------------------
# SPLASH screen
# ---------------------------------------------------------------------------
def _draw_splash():
    # Background image
    screen.blit(IMG_SPLASH_BG, vec2(0, 0))

    # Dark legibility strip behind text overlay
    screen.pen = color.rgb(8, 12, 20)
    screen.rectangle(0, 130, SW, 100)

    # Instructions
    screen.pen = COL_WHITE
    screen.font = small_font
    screen.text("Spike detected. Investigate fast.", 44, 140)
    screen.text("Find the bad attribute. Find span.", 44, 154)
    screen.text("5 SLA breaches = game over.", 65, 168)

    # Controls hint
    screen.pen = COL_HONEY
    screen.font = small_font
    screen.text("UP/DN:select  A/C:left/right  B:ok", 37, 184)

    # Blinking prompt
    blink_on = (((_now() - blink_timer[0]) // 500) % 2) == 0
    if blink_on:
        screen.pen = COL_LIME
        screen.font = small_font
        screen.text("[ ANY BUTTON ] START", 90, 212)


def _handle_splash_input():
    any_pressed = _just_pressed_any(
        "BUTTON_UP", "BUTTON_DOWN", "BUTTON_LEFT", "BUTTON_RIGHT",
        "BUTTON_A", "BUTTON_B", "BUTTON_C"
    )
    if any_pressed:
        boards.clear()
        state[0] = GS.INTRO


# ---------------------------------------------------------------------------
# Flash overlay (wrong selection)
# ---------------------------------------------------------------------------
def _draw_flash():
    if flash_timer[0] == 0:
        return
    elapsed = _now() - flash_timer[0]
    duration = SUCCESS_DURATION if flash_type[0] == 2 else FLASH_DURATION
    if elapsed >= duration:
        flash_timer[0] = 0
        if flash_type[0] == 2:
            active_board[0] = None
            success_board[0] = None
            state[0] = flash_next_state[0]
        return
    if flash_type[0] == 0:
        # Error — red fill
        screen.pen = color.rgb(180, 0, 0)
        screen.rectangle(0, 0, SW, SH)
    elif flash_type[0] == 1:
        # Neutral — "No anomaly detected" box
        box_x = SW // 2 - 90
        box_y = SH // 2 - 18
        screen.pen = color.rgb(20, 28, 40)
        screen.rectangle(box_x, box_y, 180, 36)
        screen.pen = COL_COBALT
        screen.rectangle(box_x, box_y, 180, 1)
        screen.rectangle(box_x, box_y + 35, 180, 1)
        screen.rectangle(box_x, box_y, 1, 36)
        screen.rectangle(box_x + 179, box_y, 1, 36)
        screen.pen = COL_WHITE
        screen.font = small_font
        screen.text("No anomaly detected", box_x + 12, box_y + 8)
        screen.pen = COL_DIM
        screen.font = small_font
        screen.text("Try another attribute", box_x + 10, box_y + 22)
    elif flash_type[0] == 2:
        # Success — full screen overlay
        screen.pen = color.rgb(5, 40, 10)
        screen.rectangle(0, 0, SW, SH)
        # Top and bottom accent bars
        screen.pen = COL_LIME
        screen.rectangle(0, 0, SW, 6)
        screen.rectangle(0, SH - 6, SW, 6)
        # Main message
        screen.pen = COL_LIME
        screen.font = large_font
        screen.text("Issue Discovered!", 52, 70)
        # Subtext
        screen.pen = COL_WHITE
        screen.font = small_font
        screen.text("Root cause identified.", 84, 110)
        screen.text("Returning to boards...", 84, 126)
        # Score so far
        screen.pen = COL_HONEY
        screen.font = large_font
        score_str = "Score: {}".format(score)
        score_x = (SW - len(score_str) * 14) // 2
        screen.text(score_str, score_x, 160)


# ---------------------------------------------------------------------------
# Main update loop
# ---------------------------------------------------------------------------
def update():
    cur_state = state[0]

    # Check timeouts except during GAMEOVER, SPLASH, INTRO, and active investigation
    if cur_state not in (GS.GAMEOVER, GS.SPLASH, GS.INTRO):
        _check_timeouts()
        cur_state = state[0]

    if cur_state == GS.SPLASH:
        _draw_splash()
        _handle_splash_input()

    elif cur_state == GS.INTRO:
        _draw_intro()
        _handle_intro_input()

    elif cur_state == GS.HOME:
        _draw_home()
        _handle_home_input()

    elif cur_state == GS.HEATMAP:
        _draw_heatmap_screen()
        if flash_timer[0] > 0:
            _draw_flash()
        _handle_heatmap_input()

    elif cur_state == GS.BUBBLEUP:
        _draw_bubbleup()
        if flash_timer[0] > 0:
            _draw_flash()
        _handle_bubbleup_input()

    elif cur_state == GS.TRACE:
        _draw_trace()
        if flash_timer[0] > 0:
            _draw_flash()
        _handle_trace_input()

    elif cur_state == GS.GAMEOVER:
        _draw_gameover()
        _handle_gameover_input()

    _update_prev_pressed()


# ---------------------------------------------------------------------------
# Boot
# ---------------------------------------------------------------------------
blink_timer[0] = _now()
state[0] = GS.SPLASH
run(update)
