import sys
import os
import random
import time
import sqlite3

import pandas as pd

try:
    import pygame
except ImportError:
    import pygame_ce as pygame  # type: ignore

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CELL = 20          # pixel size of one grid cell
COLS = 30          # grid columns
ROWS = 24          # grid rows
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
FPS = 10

# Colours
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GREEN   = (0,   200, 0)
DKGREEN = (0,   140, 0)
RED     = (200, 0,   0)
GRAY    = (40,  40,  40)
LGRAY   = (180, 180, 180)
YELLOW  = (230, 200, 0)
CYAN    = (0,   220, 220)

DB_PATH = "snake_data.db"


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            player    TEXT    NOT NULL,
            score     INTEGER NOT NULL,
            played_at TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            player     TEXT    NOT NULL,
            started_at TEXT    DEFAULT (datetime('now','localtime')),
            ended_at   TEXT,
            games      INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn


def save_score(conn: sqlite3.Connection, player: str, score: int) -> None:
    conn.execute(
        "INSERT INTO scores (player, score) VALUES (?, ?)", (player, score)
    )
    conn.commit()


def get_leaderboard(conn: sqlite3.Connection, limit: int = 10) -> pd.DataFrame:
    df = pd.read_sql_query(
        """
        SELECT player, MAX(score) AS best_score
        FROM   scores
        GROUP  BY player
        ORDER  BY best_score DESC
        LIMIT  ?
        """,
        conn,
        params=(limit,),
    )
    return df


def start_session(conn: sqlite3.Connection, player: str) -> int:
    cur = conn.execute(
        "INSERT INTO sessions (player) VALUES (?)", (player,)
    )
    conn.commit()
    return cur.lastrowid


def end_session(conn: sqlite3.Connection, session_id: int, games: int) -> None:
    conn.execute(
        "UPDATE sessions SET ended_at = datetime('now','localtime'), games = ? WHERE id = ?",
        (games, session_id),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Game state helpers
# ---------------------------------------------------------------------------
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)

OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


def random_food(snake: list) -> tuple:
    snake_set = set(map(tuple, snake))
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake_set:
            return pos


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def draw_cell(surface, col, row, colour, border=2):
    rect = pygame.Rect(col * CELL + border, row * CELL + border,
                       CELL - border * 2, CELL - border * 2)
    pygame.draw.rect(surface, colour, rect, border_radius=3)


def draw_text_centred(surface, text, font, colour, cy, shadow=True):
    if shadow:
        s = font.render(text, True, BLACK)
        r = s.get_rect(center=(WIDTH // 2 + 2, cy + 2))
        surface.blit(s, r)
    img = font.render(text, True, colour)
    rect = img.get_rect(center=(WIDTH // 2, cy))
    surface.blit(img, rect)
    return rect


def draw_text_left(surface, text, font, colour, x, y):
    img = font.render(text, True, colour)
    surface.blit(img, (x, y))


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------
def screen_menu(surface, fonts, logo_img, player_name: str,
                cursor_visible: bool) -> str:
    """Draw start-menu frame.  Returns 'menu' always (state unchanged here)."""
    surface.fill(GRAY)

    # Logo
    if logo_img:
        lw, lh = logo_img.get_size()
        surface.blit(logo_img, (WIDTH // 2 - lw // 2, 20))
        title_y = 20 + lh + 10
    else:
        draw_text_centred(surface, "SNAKE OG", fonts["title"], GREEN, 70)
        title_y = 120

    draw_text_centred(surface, "Enter your name:", fonts["med"], LGRAY, title_y + 30)

    # Name input box
    box_w, box_h = 260, 40
    box_x = WIDTH // 2 - box_w // 2
    box_y = title_y + 60
    pygame.draw.rect(surface, WHITE, (box_x, box_y, box_w, box_h), border_radius=4)
    pygame.draw.rect(surface, CYAN, (box_x, box_y, box_w, box_h), 2, border_radius=4)

    display_name = player_name + ("|" if cursor_visible else " ")
    name_img = fonts["input"].render(display_name, True, BLACK)
    surface.blit(name_img, (box_x + 8, box_y + 8))

    draw_text_centred(surface, "ENTER  to start", fonts["small"], LGRAY, box_y + 70)
    draw_text_centred(surface, "TAB  leaderboard    Q  quit", fonts["small"], LGRAY,
                      box_y + 95)
    return "menu"


def screen_game_over(surface, fonts, score: int, player: str) -> None:
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))
    draw_text_centred(surface, "GAME OVER", fonts["title"], RED, HEIGHT // 2 - 60)
    draw_text_centred(surface, f"{player}  scored  {score}", fonts["med"], YELLOW,
                      HEIGHT // 2)
    draw_text_centred(surface, "R  restart    ESC  menu", fonts["small"], LGRAY,
                      HEIGHT // 2 + 50)


def screen_pause(surface, fonts) -> None:
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surface.blit(overlay, (0, 0))
    draw_text_centred(surface, "PAUSED", fonts["title"], CYAN, HEIGHT // 2 - 30)
    draw_text_centred(surface, "P  resume    ESC  menu", fonts["small"], LGRAY,
                      HEIGHT // 2 + 30)


def screen_leaderboard(surface, fonts, df: pd.DataFrame) -> None:
    surface.fill(GRAY)
    draw_text_centred(surface, "LEADERBOARD", fonts["title"], YELLOW, 50)
    if df.empty:
        draw_text_centred(surface, "No scores yet!", fonts["med"], LGRAY, HEIGHT // 2)
    else:
        row_y = 110
        draw_text_left(surface, "#", fonts["med"], LGRAY, 60, row_y)
        draw_text_left(surface, "Player", fonts["med"], LGRAY, 100, row_y)
        draw_text_left(surface, "Best", fonts["med"], LGRAY, WIDTH - 110, row_y)
        row_y += 36
        for rank, (_, row) in enumerate(df.iterrows(), 1):
            colour = YELLOW if rank == 1 else WHITE
            draw_text_left(surface, str(rank), fonts["med"], colour, 60, row_y)
            draw_text_left(surface, str(row["player"]), fonts["med"], colour, 100,
                           row_y)
            draw_text_left(surface, str(row["best_score"]), fonts["med"], colour,
                           WIDTH - 110, row_y)
            row_y += 32
            if row_y > HEIGHT - 60:
                break
    draw_text_centred(surface, "TAB / ESC  back", fonts["small"], LGRAY, HEIGHT - 40)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    pygame.init()
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake OG")
    clock = pygame.time.Clock()

    # Fonts
    fonts = {
        "title": pygame.font.SysFont("monospace", 52, bold=True),
        "med":   pygame.font.SysFont("monospace", 28, bold=True),
        "small": pygame.font.SysFont("monospace", 20),
        "input": pygame.font.SysFont("monospace", 24),
        "hud":   pygame.font.SysFont("monospace", 18),
    }

    # Optional logo
    logo_img = None
    logo_path = os.path.join("assets", "Snake_OG-logo.jpg.jfif")
    if os.path.exists(logo_path):
        try:
            raw = pygame.image.load(logo_path).convert_alpha()
            max_h = 80
            ratio = max_h / raw.get_height()
            logo_img = pygame.transform.scale(
                raw, (int(raw.get_width() * ratio), max_h)
            )
        except Exception:
            pass

    conn = init_db()

    # --- state ---
    state = "menu"         # menu | game | pause | gameover | leaderboard
    player_name = ""
    snake = []
    direction = RIGHT
    next_dir = RIGHT
    food = (0, 0)
    score = 0
    session_id = None
    session_games = 0

    # blinking cursor
    cursor_timer = 0.0
    cursor_visible = True

    def reset_game():
        nonlocal snake, direction, next_dir, food, score
        cx, cy = COLS // 2, ROWS // 2
        snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        direction = RIGHT
        next_dir = RIGHT
        food = random_food(snake)
        score = 0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Blinking cursor (toggle every 0.5 s)
        cursor_timer += dt
        if cursor_timer >= 0.5:
            cursor_timer = 0.0
            cursor_visible = not cursor_visible

        # ---- Events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key == pygame.K_RETURN:
                        if player_name.strip():
                            reset_game()
                            if session_id is not None:
                                end_session(conn, session_id, session_games)
                            session_id = start_session(conn, player_name.strip())
                            session_games = 0
                            state = "game"
                    elif event.key == pygame.K_TAB:
                        state = "leaderboard"
                    elif event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        ch = event.unicode
                        if ch.isprintable() and len(player_name) < 16:
                            player_name += ch

                elif state == "game":
                    if event.key == pygame.K_p:
                        state = "pause"
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
                    elif event.key == pygame.K_TAB:
                        state = "leaderboard"
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        if direction != DOWN:
                            next_dir = UP
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if direction != UP:
                            next_dir = DOWN
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if direction != RIGHT:
                            next_dir = LEFT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if direction != LEFT:
                            next_dir = RIGHT

                elif state == "pause":
                    if event.key == pygame.K_p:
                        state = "game"
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"

                elif state == "gameover":
                    if event.key == pygame.K_r:
                        reset_game()
                        session_games += 1
                        state = "game"
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"

                elif state == "leaderboard":
                    if event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                        state = "menu"

        # ---- Update ----
        if state == "game":
            direction = next_dir
            head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            # Wall collision
            if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):
                save_score(conn, player_name.strip(), score)
                session_games += 1
                state = "gameover"
                continue

            # Self collision
            if head in snake:
                save_score(conn, player_name.strip(), score)
                session_games += 1
                state = "gameover"
                continue

            snake.insert(0, head)
            if head == food:
                score += 10
                food = random_food(snake)
            else:
                snake.pop()

        # ---- Draw ----
        if state == "menu":
            screen_menu(surface, fonts, logo_img, player_name, cursor_visible)

        elif state in ("game", "pause", "gameover"):
            # Draw grid background
            surface.fill(BLACK)
            for c in range(COLS):
                for r in range(ROWS):
                    pygame.draw.rect(surface, GRAY,
                                     (c * CELL, r * CELL, CELL, CELL), 1)

            # Draw food
            draw_cell(surface, food[0], food[1], RED)

            # Draw snake
            for i, seg in enumerate(snake):
                colour = GREEN if i > 0 else DKGREEN
                draw_cell(surface, seg[0], seg[1], colour)

            # HUD
            hud = fonts["hud"].render(
                f"  {player_name}   Score: {score}   P=pause  TAB=board  ESC=menu",
                True, LGRAY,
            )
            surface.blit(hud, (0, 0))

            if state == "pause":
                screen_pause(surface, fonts)
            elif state == "gameover":
                screen_game_over(surface, fonts, score, player_name)

        elif state == "leaderboard":
            df = get_leaderboard(conn)
            screen_leaderboard(surface, fonts, df)

        pygame.display.flip()

    # Cleanup
    if session_id is not None:
        end_session(conn, session_id, session_games)
    conn.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
