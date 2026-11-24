# Beyond Good and Evil Setup Guide

## What you need

- Beyond Good and Evil on PC (tested with the Steam release).
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.4 or later.
- The release zip from this project's
  [releases page](https://github.com/cplara/beyond-good-and-evil-archipelago/releases), which contains
  `bge.apworld` and a YAML template.

## Installing

Copy `bge.apworld` into the `custom_worlds` folder inside your Archipelago install (opening the file with the
Archipelago Launcher does the same). If the Launcher was running, close it and open it again so it picks up the new
game.

The game folder stays untouched: nothing from the zip goes there.

## Your YAML

Open `Beyond Good and Evil.yaml`, write your slot name, choose your options and hand the file to the person
generating the multiworld.

## Playing

1. Launch Beyond Good and Evil and load a save or begin a new one.
2. From the Archipelago Launcher, open **Beyond Good and Evil Client**.
3. Type `/connect address:port` and your slot name.

The client attaches to the game on its own. Besides the normal Archipelago messages, it prints the name of each area
Jade enters. Type `/bge` to check whether the client is attached to the game.

Keep a separate save slot for each multiworld, since a save keeps track of the items it has already been given.
