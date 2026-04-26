# Snake OG

Snake OG is a playable Snake project with two versions:

- A desktop game built with Python, pygame, pandas, and SQLite
- A shareable browser version in [play.html](play.html)
- file:///C:/Users/depic/snake%20game/play.html
  

## Features

- Start menu with player name entry
- Blinking typing cursor in the name input box
- Pixel-style snake movement on a square grid
- Pause screen, game-over screen, and leaderboard screen
- Local score and session saving in SQLite for the desktop version
- Local browser leaderboard storage for the web version

## Project Files

- `main.py` - desktop Snake game built with Python and pygame
- `play.html` - standalone browser version of the game
- `requirements.txt` - Python dependencies for the desktop version
- `assets/` - optional image assets
- `snake_data.db` - local desktop database created after running the Python game
- `PROJECT_REVIEW.md` - GitHub-ready project review summary

## Desktop Setup

1. Open a terminal in this project folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the desktop game:

```bash
python main.py
```

If `pygame` does not install on your Python version, install `pygame-ce` as a compatible drop-in package:

```bash
pip install pygame-ce pandas
```

## Web Version

To play the browser version, open [play.html](play.html) in a web browser.

You can also upload the project to GitHub and publish [play.html](play.html) with GitHub Pages for a shareable link.

## Desktop Controls

- `Arrow keys` or `W/A/S/D`: Move snake
- `Enter`: Start game from the menu
- `P`: Pause or resume
- `Tab`: Open leaderboard
- `Esc`: Return to menu
- `R`: Restart from game-over screen
- `Q`: Quit from the menu

## Web Controls

- `Arrow keys` or `W/A/S/D`: Move snake
- `Enter`: Start game
- `P`: Pause or resume
- `Tab`: Open leaderboard
- `Esc`: Return to menu
- `R`: Restart after game over

## Logo Asset

To show a logo in the desktop menu, place your image here:

- `assets/Snake_OG-logo.jpg.jfif`

If the file exists, the Python game loads it automatically.

## Data Storage

The desktop version creates and uses `snake_data.db` with these tables:

- `scores`
- `sessions`

The browser version stores leaderboard data in local browser storage and does not sync with the SQLite database.

## GitHub Sharing

For GitHub, the most useful files to include are:

- [README.md](README.md)
- [PROJECT_REVIEW.md](PROJECT_REVIEW.md)
- [play.html](play.html)

That gives people a project description, a review summary, and a browser-playable version they can open quickly.
