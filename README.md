# Andimarium (Python Prototype)

A top-down tile-based RPG prototype built in Python using `pygame` and `pygame-widgets`.
This repository contains the early prototype version created before the project was later rebuilt as a full-featured game in Godot.

## Overview

Andimarium is a small RPG prototype showcasing:
- tile-based movement and camera scrolling
- actor definitions, inventories, and equipment
- turn-based combat and reactions
- a simple interface with buttons for weapons, attacks, spells, and activities
- multiple map levels and stairs-based vertical navigation
- primitive AI and player/non-player character systems

The game is implemented in Python as a proof of concept, with assets stored under `assets/`.

## Requirements

This prototype was developed for Python 3 and depends on the following packages:

- `pygame==2.5.2`
- `pygame-widgets==1.1.5`
- `numpy==1.26.4`
- `pillow==10.2.0`
- `imageio==2.34.1`
- `setuptools==70.0.0`
- `wheel==0.43.0`
- `pyastar2d` (local/package path dependency in `requirements.txt`)

## Running the Prototype

From the repository root:

```bash
python3 main.py
```

If needed, install dependencies first:

```bash
pip install -r requirements.txt
```

If `pyastar2d` is not available from the given local path, install the package separately or adjust the dependency to a compatible path or version.

## Project Structure

- `main.py` — entry point and scene setup
- `config.py` — game constants, map definitions, and state management
- `world.py` — map loading, tiles, and level initialization
- `logic_graphics_merge.py` — logic-layer and graphics-layer integration
- `game_graphics.py` — rendering support and sprite drawing
- `interface.py` — UI controls, buttons, and input handling
- `characters.py` — character classes, stats, and animation components
- `items.py` — item definitions and equipment handling
- `activities.py` — actions, spells, and combat interactions
- `talents.py` — talent and specialization support
- `archetypes.py` — archetypes, character templates, and power effects
- `computer_ai.py` — basic AI decision-making
- `conditions.py` — status effects and conditional logic
- `pathfinding.py` — path calculation support

## Notes

This repository represents an early prototype and is not a polished release.
The code is intended as a working demonstration of core RPG mechanics rather than a finished product.

The project later evolved into a full Godot-based game, so this repository is best viewed as the Python prototype layer that informed the later rewrite.

## License

Original project assets and code were created by Antoine Margoloff.
Some sprite assets are modified from external sources under CC BY-NC 4.0.