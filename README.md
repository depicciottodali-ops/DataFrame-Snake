# Snake OG
DataFrame Snake is a GUI-based version of the classic Snake game built with Python. The project combines game development concepts with data-oriented programming by using pandas alongside pygame and SQLite. It was created as a portfolio project to demonstrate Python programming, event-driven logic, data handling, local database storage, and AI-assisted development using GitHub Copilot.
- A desktop game built with Python, pygame, pandas, and SQLite
- A shareable browser version in [play.html](play.html)  

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


## Data Storage

The desktop version creates and uses `snake_data.db` with these tables:



- `scores`
- `sessions`
- 
- <img width="2469" height="1670" alt="photo 1" src="https://github.com/user-attachments/assets/360683d5-7d93-43b2-b638-5ed0f0c6c011" />

- <img width="2321" height="1690" alt="photo 2" src="https://github.com/user-attachments/assets/a11c8b34-a4ab-4fa1-aa08-b5955ca2c353" />

-<img width="2232" height="1647" alt="photo 3" src="https://github.com/user-attachments/assets/43b225af-371b-4ede-906c-e95f3a313b6f" />




