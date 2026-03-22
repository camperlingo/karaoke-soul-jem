#!/usr/bin/env python3
import asyncio
import threading
from pathlib import Path
from aiohttp import web, WSMsgType

class MirrorController:
    """
    Gestore del server WebSocket per la ricerca sincronizzata.
    Lavora in un thread separato per non bloccare la GUI Tkinter.
    """
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.absolute()
        self.ASSETS_DIR = self.BASE_DIR / "mirror_assets"
        self.clients = set()
        self.loop = None
        self.runner = None
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()

    def _run_server(self):
        """Avvia il ciclo asyncio in un thread dedicato."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        app = web.Application()
        app.router.add_get("/master", self.master_page)
        app.router.add_get("/client", self.client_page)
        app.router.add_get("/ws", self.websocket_handler)
        
        self.runner = web.AppRunner(app)
        self.loop.run_until_complete(self.runner.setup())
        site = web.TCPSite(self.runner, "127.0.0.1", 8765)
        self.loop.run_until_complete(site.start())
        print("[SISTEMA] Server Mirror attivo sulla porta 8765")
        self.loop.run_forever()

    async def master_page(self, request): 
        return web.FileResponse(self.ASSETS_DIR / "mirror_master.html")
    
    async def client_page(self, request): 
        return web.FileResponse(self.ASSETS_DIR / "mirror_client.html")

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.clients.add(ws)
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    for c in list(self.clients):
                        if not c.closed and c != ws:
                            await c.send_str(msg.data)
        finally:
            self.clients.discard(ws)
        return ws

    def shutdown(self):
        """Chiude il server in modo pulito."""
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
            print("[SISTEMA] Server Mirror arrestato.")
