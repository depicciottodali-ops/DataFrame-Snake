# PROJECT_REVIEW.md — Snake OG

## Overview

**Snake OG** is a classic Snake game rebuilt as a data-analyst portfolio project.
It comes in two editions:

| Edition | Tech stack |
|---------|-----------|
| Desktop | Python · pygame · pandas · SQLite |
| Browser | HTML5 Canvas · Vanilla JavaScript · localStorage |

---

## Code Quality

### `main.py` (Desktop)
- Clean separation between **game logic**, **database helpers**, and **screen-drawing** functions.
- Uses **pandas** (`read_sql_query`) to aggregate the leaderboard, demonstrating DataFrame usage on real persistent data.
- SQLite schema is minimal and purposeful: a `scores` table records every game result, and a `sessions` table tracks play sessions (start time, end time, number of games).
- All rendering is handled through thin helper functions (`draw_cell`, `draw_text_centred`, etc.) keeping the main loop readable.
- Input is fully validated before acting (empty name guard, opposite-direction guard for the snake).

### `play.html` (Browser)
- Single self-contained file — no external dependencies, no build step.
- Game loop uses `requestAnimationFrame` with a fixed-timestep accumulator for consistent speed across different frame rates.
- `localStorage` is wrapped in safe `try/catch` for environments where it may be restricted.
- All keyboard navigation mirrors the desktop version for consistency.

---

## Features

| Feature | Desktop | Browser |
|---------|---------|---------|
| Start menu with name entry | ✅ | ✅ |
| Blinking typing cursor | ✅ | ✅ |
| Pixel-style grid movement | ✅ | ✅ |
| Pause / resume | ✅ | ✅ |
| Game-over screen | ✅ | ✅ |
| Leaderboard screen | ✅ | ✅ |
| Persistent score storage | SQLite | localStorage |
| Session tracking | ✅ | — |
| Optional logo asset | ✅ | — |

---

## Controls (Both Versions)

| Key | Action |
|-----|--------|
| Arrow keys / WASD | Move snake |
| Enter | Start game from menu |
| P | Pause / resume |
| Tab | Open leaderboard |
| Esc | Return to menu |
| R | Restart after game over |
| Q *(desktop only)* | Quit application |

---

## Data Model (Desktop)

```sql
CREATE TABLE scores (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    player    TEXT    NOT NULL,
    score     INTEGER NOT NULL,
    played_at TEXT    DEFAULT (datetime('now','localtime'))
);

CREATE TABLE sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    player     TEXT    NOT NULL,
    started_at TEXT    DEFAULT (datetime('now','localtime')),
    ended_at   TEXT,
    games      INTEGER DEFAULT 0
);
```

The leaderboard query uses a `GROUP BY player` with `MAX(score)` so each
player only appears once with their personal best.

---

## Areas for Future Improvement

- **Difficulty levels** — increase snake speed as score grows.
- **Online leaderboard** — replace localStorage with a lightweight backend (e.g. Flask + SQLite) so browser scores persist across devices.
- **Sound effects** — add eat / die audio for the browser version using the Web Audio API.
- **Mobile controls** — add swipe-gesture support or on-screen directional buttons.
- **Tests** — add pytest unit tests for game-logic helpers (`random_food`, collision detection) and database functions.

---

## GitHub Sharing

The three most useful files for GitHub visitors are:

1. **README.md** — project description and setup instructions
2. **PROJECT_REVIEW.md** — this review summary
3. **play.html** — browser-playable version (works with GitHub Pages)
