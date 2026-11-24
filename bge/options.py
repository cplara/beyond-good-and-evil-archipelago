from dataclasses import dataclass

from Options import DeathLink, PerGameCommonOptions


@dataclass
class BGEOptions(PerGameCommonOptions):
    death_link: DeathLink
