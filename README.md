# UniLife Simulator: The Freshman's Fortune

> One-line description here

## Demo


![UniLife Simulator gameplay](docs/demo.gif)
## Overview
## Features
## How to Run
## How to Play
## Game Mechanics
## Technical Highlights
## Project Structure
## Future Improvements
## Author

## Technical Highlights

- Built with **pure Python** — zero external dependencies
- Uses a centralized `game_state` dictionary as the **single source of truth** for all game data
- Implements **probability-based action resolution** using `random.random()` compared against a wellbeing-derived success threshold
- Handles **stat clamping** (0–100), temporary buffs, task deadlines, and random events
- Features a **CLI UX** with typewriter text, animated progress bars, and spinner animations
- Includes **demo modes** for scripted winning and losing playthroughs


 ## Architecture

The game follows a state-driven loop:

User Input
   ↓
Action Handler
   ↓
resolve_action()
   ↓
apply_stat_change()
   ↓
game_state update
   ↓
display_status()
   ↓
End of Day Processing

The entire game state lives in a single dictionary, making it easy to track stats, tasks, buffs, cash, and progression across days.





