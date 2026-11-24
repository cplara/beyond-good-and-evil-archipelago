# Beyond Good and Evil

## What does randomization do to this game?

Picking up collectables, taking photos of new animal species, buying from shops and earning pearls send checks to the
multiworld. The original reward of each of those locations is removed and replaced by whatever item the multiworld
placed there, which may belong to you or to another player.

The story is not changed: missions, fights and cutscenes still happen in their original order.

## What items and locations get randomized?

### Items

- **Hovercraft permits**: one for each upgrade sold at Mammago's garage (Turbomotor, Cañón neutralizador, Equipo de
  salto, Estabilizador de vuelo, Motor estelar). An upgrade can only be bought once you have its permit.
- **Camera zoom**.
- **Extra hearts**.
- Filler: starkos, servoreparadores, cápsulas turbo, sets de servos, mechaimpulsores, K-Bups and credits.

The item pool is built from the original rewards of the locations, so there are as many starkos, hearts and so on as
in the original game.

### Locations

- Collectables lying in the world, in crates and in lockers: starkos, turbo capsules, repair servos, K-Bups, extra
  hearts and large essence crystals.
- The photo of each new animal species, and the rewards for completing a photo roll.
- Purchases at Mammago's shop and at the vending machines of the Black Isle mines.
- Pearls: the DomZ creatures, the thieves' cave, photo rolls and the mine boss.
- Story rewards such as the Castelac mdisk and the pliers.

Currently covered areas: the prologue, the lighthouse island, Mammago's garage, the Hillys sea, the first thieves'
cave, Vorax's lair and the Black Isle mines up to the boss.

## What is the goal?

Collect the pearl of the DomZ creature that attacks in Hillys. This requires the **Permiso: Turbomotor** to buy the
hovercraft engine.

## What other changes are made to the game?

- Hovercraft upgrades in Mammago's shop are shown without a price until their permit is received.
- The camera zoom is turned off until the **Zoom de camara** item is received.
- Locations collected with `!collect` disappear from the world while you play.

## What does another world's item look like in Beyond Good and Evil?

There is no special model for them: the collectable keeps its usual look. Once it is picked up, the original reward
is taken back and the client prints what was found and for whom.

## When the player receives an item, what happens?

The item is added to Jade's inventory straight away, while you play. During a loading screen it is added as soon as
the new area has loaded. Hovercraft items (mechaimpulsores, turbos, servos) go to Jade's inventory and are moved to
the hovercraft when she boards it, as in the original game.

## Can I play offline?

Items only arrive while the client is connected to the server. You can keep playing while disconnected: whatever you
checked in the meantime is reported once the client reconnects.

## Known Issues

### Alt+Tab

The game has no windowed mode and may crash on Alt+Tab. Pause the game first if you need to switch windows.

### Shops restock

Shops and vending machines restock every visit. Only the first purchase of each item is a location; buying it again
works as in the original game.

### Pearls and abilities

Pearls are checks but are not shuffled into the item pool yet, because they are needed to buy hovercraft upgrades.
The rocket boots and the pliers are obtained as in the original game.

### Save slots

The save remembers how many items it has received. Use one save slot per multiworld.

## DeathLink

When DeathLink is enabled, Jade's deaths are sent to other DeathLink players, and a death received from them kills
Jade.
