import random
import sqlite3
import sys
import time
from pathlib import Path
import pandas as pd  # type: ignore
import pygame  # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "snake_data.db"
ASSET_LOGO = PROJECT_ROOT / "assets" / "Snake_OG-logo.jpg.jfif"

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
GRID_SIZE = 25
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = (WINDOW_HEIGHT - 100) // GRID_SIZE

FPS_BASE = 10
SNAKE_START_LENGTH = 3

BACKGROUND_TOP = (16, 24, 16)
BACKGROUND_BOTTOM = (28, 44, 28)
GRID_COLOR = (42, 64, 42)
SNAKE_HEAD_COLOR = (153, 224, 77)
SNAKE_BODY_COLOR = (103, 179, 61)
FOOD_COLOR = (255, 170, 51)
TEXT_COLOR = (238, 247, 214)
ACCENT_COLOR = (193, 242, 98)
DANGER_COLOR = (255, 98, 98)
PANEL_COLOR = (10, 15, 10)

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_LEADERBOARD = "leaderboard"
STATE_GAME_OVER = "game_over"


def init_database() -> None:
    """Create required SQLite tables if they do not exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                apples INTEGER NOT NULL,
                duration_sec REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                moves INTEGER NOT NULL,
                score INTEGER NOT NULL,
                apples INTEGER NOT NULL,
                duration_sec REAL NOT NULL,
                ended_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_game_result(player_name: str, score: int, apples: int, duration_sec: float, moves: int, ended_by: str) -> None:
    """Persist game result using pandas DataFrames into SQLite tables."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    score_df = pd.DataFrame(
        [
            {
                "player_name": player_name,
                "score": int(score),
                "apples": int(apples),
                "duration_sec": float(duration_sec),
                "created_at": timestamp,
            }
        ]
    )

    session_df = pd.DataFrame(
        [
            {
                "player_name": player_name,
                "moves": int(moves),
                "score": int(score),
                "apples": int(apples),
                "duration_sec": float(duration_sec),
                "ended_by": ended_by,
                "created_at": timestamp,
            }
        ]
    )

    with sqlite3.connect(DB_PATH) as conn:
        score_df.to_sql("scores", conn, if_exists="append", index=False)
        session_df.to_sql("sessions", conn, if_exists="append", index=False)


def load_leaderboard(limit: int = 10) -> pd.DataFrame:
    query = """
        SELECT player_name, score, apples, ROUND(duration_sec, 1) AS duration_sec, created_at
        FROM scores
        ORDER BY score DESC, apples DESC, duration_sec ASC
        LIMIT ?
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=(limit,))


class SnakeGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Snake OG")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_small = pygame.font.SysFont("consolas", 22)
        self.font_medium = pygame.font.SysFont("consolas", 30)
        self.font_large = pygame.font.SysFont("consolas", 48, bold=True)

        self.logo = self._load_logo()
        self.state = STATE_MENU
        self.running = True

        self.player_name = "PLAYER"
        self.name_input = "PLAYER"

        self.snake = []
        self.direction = (1, 0)
        self.pending_direction = (1, 0)
        self.food = (0, 0)

        self.score = 0
        self.apples_eaten = 0
        self.moves = 0
        self.speed = FPS_BASE

        self.session_start_time = 0.0
        self.saved_result = False

        self._reset_round()

    def _load_logo(self):
        if ASSET_LOGO.exists():
            try:
                image = pygame.image.load(str(ASSET_LOGO)).convert_alpha()
                return pygame.transform.smoothscale(image, (220, 110))
            except pygame.error:
                return None
        return None

    def _reset_round(self) -> None:
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2

        self.snake = [(center_x - i, center_y) for i in range(SNAKE_START_LENGTH)]
        self.direction = (1, 0)
        self.pending_direction = (1, 0)
        self.food = self._spawn_food()

        self.score = 0
        self.apples_eaten = 0
        self.moves = 0
        self.speed = FPS_BASE

        self.session_start_time = time.time()
        self.saved_result = False

    def _spawn_food(self):
        while True:
            position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if position not in self.snake:
                return position

    def _draw_gradient_background(self):
        for y in range(WINDOW_HEIGHT):
            t = y / WINDOW_HEIGHT
            color = (
                int(BACKGROUND_TOP[0] * (1 - t) + BACKGROUND_BOTTOM[0] * t),
                int(BACKGROUND_TOP[1] * (1 - t) + BACKGROUND_BOTTOM[1] * t),
                int(BACKGROUND_TOP[2] * (1 - t) + BACKGROUND_BOTTOM[2] * t),
            )
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))

    def _draw_grid(self):
        board_height = GRID_HEIGHT * GRID_SIZE
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, board_height), 1)
        for y in range(0, board_height + 1, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)

    def _draw_snake(self):
        for index, (x, y) in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_BODY_COLOR
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, color, rect)

    def _draw_food(self):
        fx, fy = self.food
        center = (fx * GRID_SIZE + GRID_SIZE // 2, fy * GRID_SIZE + GRID_SIZE // 2)
        pygame.draw.circle(self.screen, FOOD_COLOR, center, GRID_SIZE // 2 - 4)

    def _draw_hud(self):
        panel_y = GRID_HEIGHT * GRID_SIZE
        panel_rect = pygame.Rect(0, panel_y, WINDOW_WIDTH, WINDOW_HEIGHT - panel_y)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel_rect)

        info = f"Player: {self.player_name}    Score: {self.score}    Apples: {self.apples_eaten}    Speed: {self.speed}"
        controls = "Arrows/WASD: Move   P: Pause   Tab: Leaderboard   Esc: Menu"

        info_surface = self.font_small.render(info, True, TEXT_COLOR)
        controls_surface = self.font_small.render(controls, True, ACCENT_COLOR)

        self.screen.blit(info_surface, (20, panel_y + 16))
        self.screen.blit(controls_surface, (20, panel_y + 48))

    def _draw_menu(self):
        self._draw_gradient_background()

        title = self.font_large.render("SNAKE OG", True, ACCENT_COLOR)
        subtitle = self.font_small.render("Type your name and press Enter to start", True, TEXT_COLOR)

        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 120))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 190))

        if self.logo is not None:
            self.screen.blit(self.logo, (WINDOW_WIDTH // 2 - self.logo.get_width() // 2, 230))

        input_box = pygame.Rect(WINDOW_WIDTH // 2 - 180, 380, 360, 52)
        pygame.draw.rect(self.screen, (28, 44, 28), input_box, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT_COLOR, input_box, width=2, border_radius=8)

        name_text = self.font_medium.render(self.name_input, True, TEXT_COLOR)
        self.screen.blit(name_text, (input_box.x + 12, input_box.y + 10))

        cursor_visible = (pygame.time.get_ticks() // 450) % 2 == 0
        if cursor_visible:
            cursor_x = input_box.x + 12 + name_text.get_width() + 3
            cursor_top = input_box.y + 9
            cursor_bottom = input_box.y + input_box.height - 9
            pygame.draw.line(self.screen, ACCENT_COLOR, (cursor_x, cursor_top), (cursor_x, cursor_bottom), 2)

        lines = [
            "Enter: Start game",
            "Tab: Leaderboard",
            "Q: Quit",
        ]

        for idx, line in enumerate(lines):
            txt = self.font_small.render(line, True, TEXT_COLOR)
            self.screen.blit(txt, (WINDOW_WIDTH // 2 - txt.get_width() // 2, 470 + idx * 28))

    def _draw_pause(self):
        self._draw_board()
        pause_text = self.font_large.render("PAUSED", True, ACCENT_COLOR)
        hint_text = self.font_small.render("Press P to resume", True, TEXT_COLOR)
        self.screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, 220))
        self.screen.blit(hint_text, (WINDOW_WIDTH // 2 - hint_text.get_width() // 2, 280))

    def _draw_game_over(self):
        self._draw_board()
        over = self.font_large.render("GAME OVER", True, DANGER_COLOR)
        score = self.font_medium.render(f"Score: {self.score}", True, TEXT_COLOR)
        restart = self.font_small.render("Press R to play again, Esc for menu, Tab for leaderboard", True, ACCENT_COLOR)

        self.screen.blit(over, (WINDOW_WIDTH // 2 - over.get_width() // 2, 200))
        self.screen.blit(score, (WINDOW_WIDTH // 2 - score.get_width() // 2, 265))
        self.screen.blit(restart, (WINDOW_WIDTH // 2 - restart.get_width() // 2, 320))

    def _draw_leaderboard(self):
        self._draw_gradient_background()

        title = self.font_large.render("LEADERBOARD", True, ACCENT_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 70))

        table_header = self.font_small.render("Rank  Player        Score  Apples  Time(s)    Date", True, TEXT_COLOR)
        self.screen.blit(table_header, (135, 170))

        leaderboard_df = load_leaderboard(10)
        if leaderboard_df.empty:
            empty_text = self.font_medium.render("No scores yet. Play a game first.", True, TEXT_COLOR)
            self.screen.blit(empty_text, (WINDOW_WIDTH // 2 - empty_text.get_width() // 2, 260))
        else:
            for idx, row in leaderboard_df.iterrows():
                line = f"{idx + 1:<5} {row['player_name'][:12]:<12} {int(row['score']):<6} {int(row['apples']):<7} {float(row['duration_sec']):<9.1f} {row['created_at']}"
                row_surface = self.font_small.render(line, True, TEXT_COLOR)
                self.screen.blit(row_surface, (135, 210 + idx * 32))

        footer = self.font_small.render("Press Esc to return to menu", True, ACCENT_COLOR)
        self.screen.blit(footer, (WINDOW_WIDTH // 2 - footer.get_width() // 2, 640))

    def _draw_board(self):
        self._draw_gradient_background()
        self._draw_grid()
        self._draw_food()
        self._draw_snake()
        self._draw_hud()

    def _save_if_needed(self, ended_by: str) -> None:
        if self.saved_result:
            return
        duration = max(0.1, time.time() - self.session_start_time)
        save_game_result(
            player_name=self.player_name,
            score=self.score,
            apples=self.apples_eaten,
            duration_sec=duration,
            moves=self.moves,
            ended_by=ended_by,
        )
        self.saved_result = True

    def _handle_menu_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.player_name = self.name_input.strip() or "PLAYER"
                self._reset_round()
                self.state = STATE_PLAYING
            elif event.key == pygame.K_BACKSPACE:
                self.name_input = self.name_input[:-1]
            elif event.key == pygame.K_TAB:
                self.state = STATE_LEADERBOARD
            elif event.key == pygame.K_q:
                self.running = False
            else:
                char = event.unicode
                if char.isalnum() or char in "_-":
                    if len(self.name_input) < 14:
                        self.name_input += char.upper()

    def _handle_playing_events(self, event):
        if event.type != pygame.KEYDOWN:
            return

        key_to_direction = {
            pygame.K_UP: (0, -1),
            pygame.K_w: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_s: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_d: (1, 0),
        }

        if event.key in key_to_direction:
            new_direction = key_to_direction[event.key]
            if new_direction != (-self.direction[0], -self.direction[1]):
                self.pending_direction = new_direction
                self.moves += 1
        elif event.key == pygame.K_p:
            self.state = STATE_PAUSED
        elif event.key == pygame.K_TAB:
            self.state = STATE_LEADERBOARD
        elif event.key == pygame.K_ESCAPE:
            self.state = STATE_MENU

    def _handle_pause_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.state = STATE_PLAYING
            elif event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU

    def _handle_game_over_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._reset_round()
                self.state = STATE_PLAYING
            elif event.key == pygame.K_TAB:
                self.state = STATE_LEADERBOARD
            elif event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU

    def _handle_leaderboard_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = STATE_MENU

    def _update_game(self):
        self.direction = self.pending_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        new_head = (head_x + dx, head_y + dy)

        if (
            new_head[0] < 0
            or new_head[0] >= GRID_WIDTH
            or new_head[1] < 0
            or new_head[1] >= GRID_HEIGHT
            or new_head in self.snake
        ):
            self._save_if_needed("collision")
            self.state = STATE_GAME_OVER
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.apples_eaten += 1
            self.food = self._spawn_food()
            self.speed = min(20, FPS_BASE + self.apples_eaten // 3)
        else:
            self.snake.pop()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state in {STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER}:
                        self._save_if_needed("quit")
                    self.running = False
                    break

                if self.state == STATE_MENU:
                    self._handle_menu_events(event)
                elif self.state == STATE_PLAYING:
                    self._handle_playing_events(event)
                elif self.state == STATE_PAUSED:
                    self._handle_pause_events(event)
                elif self.state == STATE_GAME_OVER:
                    self._handle_game_over_events(event)
                elif self.state == STATE_LEADERBOARD:
                    self._handle_leaderboard_events(event)

            if self.state == STATE_MENU:
                self._draw_menu()
            elif self.state == STATE_PLAYING:
                self._update_game()
                self._draw_board()
            elif self.state == STATE_PAUSED:
                self._draw_pause()
            elif self.state == STATE_GAME_OVER:
                self._draw_game_over()
            elif self.state == STATE_LEADERBOARD:
                self._draw_leaderboard()

            pygame.display.flip()
            self.clock.tick(self.speed if self.state == STATE_PLAYING else 60)

        pygame.quit()
        sys.exit()


def main() -> None:
    init_database()
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()
