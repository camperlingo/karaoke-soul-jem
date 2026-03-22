#!/usr/bin/env python3
import asyncio
import signal
from pathlib import Path
from aiohttp import web, WSMsgType

BASE_DIR = Path(__file__).parent.absolute()
ASSETS_DIR = BASE_DIR / "mirror_assets"
clients = set()

async def master_page(request): return web.FileResponse(ASSETS_DIR / "mirror_master.html")
async def client_page(request): return web.FileResponse(ASSETS_DIR / "mirror_client.html")

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    clients.add(ws)
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                for c in list(clients):
                    if not c.closed and c != ws:
                        await c.send_str(msg.data)
    finally:
        clients.discard(ws)
    return ws

async def main():
    app = web.Application()
    app.router.add_get("/master", master_page)
    app.router.add_get("/client", client_page)
    app.router.add_get("/ws", websocket_handler)
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8765); await site.start()
    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)
    await stop_event.wait()
    await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
