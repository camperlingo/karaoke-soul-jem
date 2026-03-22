import json
import websocket


class MirrorClient:
    def __init__(self, url="ws://localhost:8765/ws"):
        self.url = url
        self.ws = None

    def connect(self):
        if not self.ws:
            self.ws = websocket.WebSocket()
            self.ws.connect(self.url)

    def navigate(self, url):
        self.connect()
        payload = {
            "type": "navigate",
            "url": url
        }
        self.ws.send(json.dumps(payload))

    def close(self):
        if self.ws:
            self.ws.close()
            self.ws = None

