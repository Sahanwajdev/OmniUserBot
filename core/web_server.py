import os
import asyncio
from aiohttp import web
from config import config
from core.logger import log


async def handle_root(request):
    bot = request.app.get("bot")
    uptime = getattr(bot, "uptime_str", "N/A") if bot else "N/A"
    cmd_count = len(getattr(bot, "commands", {})) if bot else 0
    
    return web.json_response({
        "status": "online",
        "service": config.BOT_NAME,
        "version": "1.0.0",
        "commands_loaded": cmd_count,
        "uptime": uptime,
        "edge_provider": "Cloudflare",
        "message": "OmniUserBot is running live and healthy."
    })


async def handle_health(request):
    return web.Response(text="OK", status=200)


async def start_web_server(bot, port: int = None):
    """Starts a non-blocking background HTTP health server for Cloudflare / cloud hosting."""
    if port is None:
        port_env = os.getenv("PORT", "8080").strip()
        try:
            port = int(port_env)
        except ValueError:
            port = 8080

    app = web.Application()
    app["bot"] = bot
    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/ping", handle_health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)

    try:
        await site.start()
        log.info(f"Cloudflare web health server listening on port {port}")
        return runner
    except Exception as e:
        log.warning(f"Web server could not bind to port {port}: {e}")
        return None
