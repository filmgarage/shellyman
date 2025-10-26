import asyncio
import json
import websockets

class HAClient:
    """Minimal Home Assistant WebSocket API client.
    Only what we need: auth and config_entries/get.
    """
    def __init__(self, ws_url: str, token: str):
        self.ws_url = ws_url
        self.token = token
        self.ws = None
        self._msg_id = 1

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, ping_interval=20, ping_timeout=20)
        # handshake
        hello = await self.ws.recv()
        # send auth
        await self.ws.send(json.dumps({"type": "auth", "access_token": self.token}))
        auth_result = await self.ws.recv()
        if 'auth_ok' not in auth_result:
            raise RuntimeError("HA auth failed")

    async def call(self, payload: dict) -> dict:
        payload = dict(payload)
        payload['id'] = self._msg_id
        self._msg_id += 1
        await self.ws.send(json.dumps(payload))
        while True:
            msg = json.loads(await self.ws.recv())
            if msg.get('id') == payload['id']:
                return msg

    async def get_config_entries(self, domain_filter: str | None = None):
        res = await self.call({"type": "config_entries/get"})
        entries = res.get('result', [])
        if domain_filter:
            entries = [e for e in entries if e.get('domain') == domain_filter]
        return entries

    async def close(self):
        if self.ws:
            await self.ws.close()
            self.ws = None
