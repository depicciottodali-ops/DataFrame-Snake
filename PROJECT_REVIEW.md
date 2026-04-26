# Snake OG Project Review

## Overview

Snake OG is a desktop Snake game built with Python, pygame, pandas, and SQLite. The project takes a familiar arcade game and adds persistence, a start menu, a leaderboard, and session tracking so it feels more like a complete game project than a single gameplay loop.

## What Works Well

- Clean game loop structure with clear menu, playing, paused, leaderboard, and game-over states.
- Persistent score tracking using SQLite, with pandas used to write and read score data.
- Simple controls that make the game easy to pick up quickly.
- A distinct pixel-style presentation with a custom HUD and menu flow.
- Easy local setup with a small number of dependencies.

## Technical Highlights

- `pygame` handles rendering, input, and the main loop.
- `sqlite3` stores score and session history locally.
- `pandas` writes structured score and session data into the database.
- The game keeps gameplay logic, rendering, and data storage organized in one main application file for a straightforward small-project structure.

## Features

- Player name entry before starting.
- Score, apples eaten, and speed tracking.
- Pause screen and game-over screen.
- Leaderboard view.
- Automatic local database creation.

## Good Fit For

- A beginner-to-intermediate Python game portfolio project.
- A school or personal programming showcase.
- A foundation for adding more mechanics such as obstacles, sound, skins, or difficulty modes.

## Suggested Future Improvements

- Split the code into separate modules for gameplay, rendering, and data access.
- Add sound effects and music.
- Add difficulty settings and alternate maps.
- Improve the leaderboard UI formatting.
- Add unit tests for database and score-handling logic.
- Publish the browser version with GitHub Pages for one-click sharing.

## Share Summary

Snake OG is a polished Python Snake project that goes beyond the basic tutorial version by including saved scores, session history, a leaderboard, and a stronger menu flow. It works well as a portfolio project because it demonstrates gameplay programming, UI state management, and lightweight data persistence in one package.