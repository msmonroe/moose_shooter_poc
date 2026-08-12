# Moose Shooter POC

A deliberately tiny arcade-shooter prototype for testing the gameplay idea.

## Current validation build

Run `run_game.bat` on Windows. It now launches `demo_v2.py`, the more polished fake-gameplay build with a custom rear-view moose sprite embedded directly in the repository.

## What is in it

- Custom armed moose player sprite
- Twin blue blasters
- Mountain/forest night backdrop
- Glow, particle, explosion, and screen-shake effects
- Wave 1: aliens
- Wave 2: chickens
- Wave 3: shopping carts
- Boss warning
- CRAIG, the beige office printer boss
- PAPER JAM +500 victory screen
- Score, lives, restart

## Windows 10 setup

Install Python 3.11 or newer from python.org and check `Add Python to PATH` during installation.

Then open Command Prompt in this folder and run:

    py -m pip install -r requirements.txt

After that, double-click:

    run_game.bat

## Controls

- A / Left Arrow = move left
- D / Right Arrow = move right
- Space = fire
- R = restart after win/loss
- Esc = quit

## Purpose

This is not meant to be a finished commercial game. It is a fast playable validation demo designed to look convincing enough for gameplay clips while we test whether the premise gets attention.
