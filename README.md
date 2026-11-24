# Beyond Good and Evil — Archipelago

[![CI](https://github.com/cplara/beyond-good-and-evil-archipelago/actions/workflows/ci.yml/badge.svg)](https://github.com/cplara/beyond-good-and-evil-archipelago/actions/workflows/ci.yml)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)

An [Archipelago](https://archipelago.gg) multiworld randomizer integration for **Beyond Good and Evil** (PC, Steam).

Items, animal photos, pearls and hovercraft upgrades become *checks* shared with other games in the multiworld:
when you pick up a starkos in Hillys, someone else may receive a key in their Zelda game — and their checks can
send you the hovercraft engine.

The game has **no modding API and no existing randomizer**. Everything here — memory layout, item and event
flags, shop tables, ability switches — was **reverse-engineered from scratch** by reading and writing the live
memory of the running game.

> **Status:** playable prototype (`v0.3.1`, 105 locations) covering the prologue, the lighthouse island, Mammago's
> garage, Hillys, the thieves' cave, the Vorax lair and the whole Black Isle mine with its boss. A full multiworld
> session has been played end-to-end against a real Archipelago server.

---

## Technical highlights

- **Live memory client, zero dependencies.** The client attaches to `BGE.exe` (32-bit, no ASLR) through the Win32
  API (`ReadProcessMemory` / `WriteProcessMemory`) using only `ctypes`, so it runs inside Archipelago's frozen
  Python without extra packages.
- **Stable pointers.** Static pointers into the executable's `.data` section that survive restarts, zone changes
  and death/reload, validated against each other before any write.
- **Game-aware safety.** No writes during zone transitions (the game reloads its flag block and would overwrite
  them), filtering of transient all-zero reads during sector loads, two-read debounce for checks, and a
  received-item index stored *inside the save data* so items are never lost or duplicated on death or reload.
- **Randomizer design.** Vanilla rewards are reverted when a location is checked, shop stock is locked/unlocked
  live through the game's own shop table, interchangeable shop units are grouped, and abilities (camera zoom,
  rocket boots, pliers) are toggled through their flags.
- **Archipelago world.** Regions, logic, item pool built from vanilla rewards, DeathLink, launcher component and
  docs, packaged as a standard `.apworld` and generated/served with an unmodified Archipelago install.

| Path | What it is |
|---|---|
| [`bge/`](bge/) | The apworld: world definition (`__init__.py`), location/item tables (`data.py`), options, client |
| [`bge/client/`](bge/client/) | Memory access, game logic (testable without a server) and the Archipelago bridge |
| [`tests/`](tests/) | Offline smoke test (stubs Archipelago's modules; runs in CI) |
| [`bge/docs/`](bge/docs/) | Player guides: [game info](bge/docs/en_Beyond%20Good%20and%20Evil.md) and [setup](bge/docs/setup_en.md) |
| [`release/`](release/) | Files shipped in the release zip (YAML template, install notes) |

## How it works in game

- Every collectible, new animal photo, shop purchase and pearl is a **bit in the game's flag table**. The client
  watches those bits and sends the matching location to the server.
- The original reward (e.g. a starkos) is **removed** and replaced by the item the multiworld assigned there.
- Items received from other players are applied **instantly**, while you play.
- Locations already collected elsewhere (`!collect`) **disappear from the world in real time**.
- Story fights still happen in their original order.

## Install & play

1. Download the latest release zip from **[Releases](https://github.com/cplara/beyond-good-and-evil-archipelago/releases)**.
2. Copy `bge.apworld` into Archipelago's `custom_worlds` folder. Nothing goes into the game folder: the client
   finds the running game by itself, wherever it is installed.
3. Edit `Beyond Good and Evil.yaml` with your slot name and generate the multiworld.
4. Start the game, open **Beyond Good and Evil Client** from the Archipelago Launcher and
   `/connect <server>:<port>`, start a new game or load an existing save.

Requirements: Beyond Good and Evil (Steam, PC) and Archipelago 0.6.4+.

## Roadmap

Pearls and abilities as shuffled items, the rest of the game, YAML options (goal, photosanity, shopsanity…).

## AI Disclosure

Development was assisted with AI for recommending code implementation and maintaining documentation. All AI generated code and documentation were manually reviewed, tested in game, and approved by hand. This repository contains no game files and no AI-generated art.

## Disclaimer

Fan project, not affiliated with Ubisoft. **No game files are included** — you need a legal copy of Beyond Good
and Evil. Released under the [MIT License](LICENSE).
