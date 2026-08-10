
# Moose Shooter POC

A deliberately tiny arcade-shooter prototype for testing the gameplay idea.

## What is in it

- Moose player at the bottom of the screen
- A/D or Left/Right arrows to move
- Spacebar to shoot
- Wave 1: aliens
- Wave 2: chickens
- Wave 3: shopping carts
- Boss warning
- CRAIG, the beige office printer boss
- PAPER JAM +500 victory screen
- Score, lives, restart

## Windows 10 setup

### 1. Install Python

Install Python 3.11 or newer from python.org.

During installation, check:

    Add Python to PATH

### 2. Open Command Prompt in this folder

Then run:

    py -m pip install -r requirements.txt

### 3. Start the game

Double-click:

    run_game.bat

Or run:

    py main.py

## Controls

- A / Left Arrow = move left
- D / Right Arrow = move right
- Space = fire
- R = restart after win/loss
- Esc = quit

## Purpose

This is not meant to be a finished game. It is a quick playable proof of concept that can also be screen-recorded for short-form video tests.

Everything is drawn with simple Pygame shapes, so there are no external art assets or licensing problems in this prototype.
