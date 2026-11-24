"""Beyond Good and Evil (PC, Steam) - world de Archipelago (prototipo)."""
from typing import Any

from BaseClasses import Item, ItemClassification, Location, Region, Tutorial
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import Component, Type, components, launch_subprocess

from .data import (CREDITS_FILLER, FILLER_ITEMS, GAME_NAME, GOAL_LOCATION, ISLA, ITEM_IDS, ITEMS, LOCATION_IDS,
                   LOCATIONS, MAMMAGO, MAR, MENU, NEGRA, VANILLA_ITEMS)
from .options import BGEOptions


def launch_client(*args: str):
    # Import perezoso: la generacion no necesita cargar el cliente.
    from .client import launch
    launch_subprocess(launch, name="BGEClient", args=args)


components.append(Component("Beyond Good and Evil Client", func=launch_client, component_type=Type.CLIENT))

CLASSIFICATIONS = {
    "progression": ItemClassification.progression,
    "useful": ItemClassification.useful,
    "filler": ItemClassification.filler,
}


class BGEItem(Item):
    game = GAME_NAME


class BGELocation(Location):
    game = GAME_NAME


class BGEWeb(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Beyond Good and Evil for Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Cristobal Lara"],
    )]


class BGEWorld(World):
    """Beyond Good and Evil: Jade, reportera y fotografa, investiga la invasion DomZ en el planeta Hillys."""

    game = GAME_NAME
    web = BGEWeb()
    options_dataclass = BGEOptions
    options: BGEOptions

    item_name_to_id = ITEM_IDS
    location_name_to_id = LOCATION_IDS
    origin_region_name = MENU

    _classification = {item.name: CLASSIFICATIONS[item.classification] for item in ITEMS}

    def create_item(self, name: str) -> BGEItem:
        return BGEItem(name, self._classification[name], self.item_name_to_id[name], self.player)

    def create_regions(self) -> None:
        regions = {name: Region(name, self.player, self.multiworld) for name in (MENU, ISLA, MAMMAGO, MAR, NEGRA)}
        for loc in LOCATIONS:
            region = regions[loc.region]
            region.locations.append(BGELocation(self.player, loc.name, self.location_name_to_id[loc.name], region))

        regions[MENU].connect(regions[ISLA])
        regions[ISLA].connect(regions[MAMMAGO], "Remolque a Mammago")
        regions[MAMMAGO].connect(regions[MAR], "Deslizador con turbomotor",
                              lambda state: state.has("Permiso: Turbomotor", self.player))
        regions[MAR].connect(regions[NEGRA], "Viaje a Isla Negra")
        self.multiworld.regions += regions.values()

    def create_items(self) -> None:
        # Items que no tienen location vanilla (permisos de la tienda de mejoras)
        names = [item.name for item in ITEMS for _ in range(item.count)]
        # Recompensa vanilla de cada location
        names += [VANILLA_ITEMS[loc.vanilla] for loc in LOCATIONS]
        # Los permisos ocupan el lugar de creditos
        while len(names) > len(LOCATIONS):
            names.remove(CREDITS_FILLER)
        self.multiworld.itempool += [self.create_item(name) for name in names]

    def set_rules(self) -> None:
        goal = self.multiworld.get_location(GOAL_LOCATION, self.player)
        self.multiworld.completion_condition[self.player] = lambda state: goal.can_reach(state)

    def get_filler_item_name(self) -> str:
        return self.random.choice(FILLER_ITEMS)

    def fill_slot_data(self) -> dict[str, Any]:
        return {"death_link": bool(self.options.death_link.value)}
