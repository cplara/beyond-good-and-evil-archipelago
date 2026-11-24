"""Cliente de Archipelago para Beyond Good and Evil (lee y escribe la memoria de BGE.exe en vivo)."""
import asyncio

import Utils
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, gui_enabled, logger, server_loop
from NetUtils import ClientStatus

from ..data import GAME_NAME
from .game import BGEGame

POLL_SECONDS = 0.25
QUIET_STATUSES = {"En partida", "Cambiando de zona...", "Cargando..."}


class BGECommandProcessor(ClientCommandProcessor):
    def _cmd_bge(self):
        """Muestra el estado de la conexion con el juego."""
        ctx: BGEContext = self.ctx  # type: ignore[assignment]
        self.output(f"Juego: {ctx.game_status}  zona: {ctx.last_zone}")


class BGEContext(CommonContext):
    command_processor = BGECommandProcessor
    game = GAME_NAME
    items_handling = 0b111   # recibir todo: los premios vanilla se reemplazan por los del multiworld

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.bge = BGEGame()
        self.game_status = "Sin iniciar"
        self.last_zone = None
        self.death_pending = False

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            slot_data = args.get("slot_data") or {}
            Utils.async_start(self.update_death_link(bool(slot_data.get("death_link", False))))

    def on_deathlink(self, data: dict):
        super().on_deathlink(data)
        self.death_pending = True

    @property
    def connected_to_slot(self) -> bool:
        return self.slot is not None and self.server is not None


def _item_names(ctx: BGEContext) -> list:
    return [ctx.item_names.lookup_in_game(item.item, GAME_NAME) for item in ctx.items_received]


async def game_watcher(ctx: BGEContext):
    while not ctx.exit_event.is_set():
        try:
            await asyncio.wait_for(ctx.watcher_event.wait(), POLL_SECONDS)
        except asyncio.TimeoutError:
            pass
        ctx.watcher_event.clear()

        if not ctx.connected_to_slot:
            ctx.game_status = "Sin conexion al servidor"
            continue
        try:
            result = ctx.bge.tick(_item_names(ctx), ctx.checked_locations, ctx.death_pending,
                                  already_checked=ctx.locations_checked)
        except Exception as e:  # el juego se cerro a mitad de lectura, etc.
            logger.debug(f"Error leyendo el juego: {e}")
            ctx.bge.mem.detach()
            continue

        if result.status != ctx.game_status:
            # Los estados de rutina van al log de depuracion; solo se muestran los que piden accion.
            (logger.debug if result.status in QUIET_STATUSES else logger.info)(f"[BGE] {result.status}")
            ctx.game_status = result.status
        ctx.last_zone = result.zone
        if result.entered:
            logger.info(f"Jade entra a: {result.entered}")
        if result.killed:
            ctx.death_pending = False
            logger.info("DeathLink recibido: Jade cae.")
        for name in result.applied:
            logger.debug(f"[BGE] Item aplicado: {name}")
        for text in result.reverted:
            logger.debug(f"[BGE] Premio vanilla revertido: {text}")
        for name in result.collected:
            logger.debug(f"[BGE] Marcado como recogido (collect): {name}")

        new = result.checked - ctx.locations_checked
        if new:
            await ctx.check_locations(new)
        if result.goal and not ctx.finished_game:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
            logger.info("¡Meta completada!")
        if result.died and "DeathLink" in ctx.tags:
            await ctx.send_death(f"{ctx.player_names.get(ctx.slot, 'Jade')} cayo en Hillys.")


async def main(args):
    ctx = BGEContext(args.connect, args.password)
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()
    watcher = asyncio.create_task(game_watcher(ctx), name="BGEGameWatcher")

    await ctx.exit_event.wait()
    ctx.server_address = None
    ctx.watcher_event.set()
    await watcher
    await ctx.shutdown()


def launch(*launch_args: str):
    Utils.init_logging("BGEClient", exception_logger="Client")
    parser = get_base_parser(description="Beyond Good and Evil Client")
    args = parser.parse_args(launch_args)
    asyncio.run(main(args))
