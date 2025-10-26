import asyncio
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Literal

from ..settings import load_options
from ..ha_ws import HAClient
from ..utils.http import HttpClient
from ..services.shelly_gen1 import ShellyGen1
from ..services.shelly_gen2 import ShellyGen2

router = APIRouter(prefix="/api/devices", tags=["devices"])

class Device(BaseModel):
    id: str
    name: str | None = None
    ip: str | None = None
    model: str | None = None
    gen: Literal[1, 2] | None = None
    firmware_version: str | None = None
    firmware_uptodate: bool | None = None
    auth_enabled: bool | None = None
    protocol: Literal['CoIoT','RPC','Unknown'] = 'Unknown'

def _probe_one(ip: str, http: HttpClient) -> dict:
    """Probe a device to determine gen, firmware, auth and protocol."""
    # Try Gen2 first
    s2 = ShellyGen2(http)
    r2 = s2.auth_status(ip)
    if r2.enabled is False or r2.enabled is True:
        info_status, info = http.get_json(f"http://{ip}/rpc/Shelly.GetDeviceInfo")
        firmware = (info or {}).get('fw_id') if info_status == 200 else None
        model = (info or {}).get('model') if info_status == 200 else None
        return {
            'gen': 2,
            'protocol': 'RPC',
            'firmware_version': firmware,
            'auth_enabled': r2.enabled,
            'model': model,
        }
    # Try Gen1
    s1 = ShellyGen1(http)
    r1 = s1.auth_status(ip)
    if r1.enabled is not None:
        code, inf = http.get_json(f"http://{ip}/shelly")
        firmware = (inf or {}).get('fw') if code == 200 else None
        model = (inf or {}).get('type') if code == 200 else None
        return {
            'gen': 1,
            'protocol': 'CoIoT',
            'firmware_version': firmware,
            'auth_enabled': r1.enabled,
            'model': model,
        }
    return {}

@router.get("")
async def list_devices(q: str | None = Query(default=None, description="Case-insensitive filter on name/ip/model")):
    opts = load_options()
    if not opts.ha_token:
        raise HTTPException(status_code=400, detail="ha_token is required in add-on options")

    client = HAClient(opts.hass_ws_url or "ws://supervisor/core/websocket", opts.ha_token)
    await client.connect()
    try:
        entries = await client.get_config_entries(domain_filter="shelly")
        candidates = []
        for e in entries:
            host = e.get('data', {}).get('host') or e.get('data', {}).get('ip') or e.get('data', {}).get('hostname')
            if not host:
                host = e.get('title')
            name = e.get('title')
            unique_id = e.get('entry_id')
            candidates.append({'id': unique_id, 'name': name, 'ip': host})
    finally:
        await client.close()

    http = HttpClient(timeout=opts.request_timeout)
    sem = asyncio.Semaphore(8)

    async def work(c):
        ip = c['ip']
        result = {}
        if ip:
            async with sem:
                result = await asyncio.to_thread(_probe_one, ip, http)
        d = Device(id=c['id'], name=c.get('name'), ip=ip, **result)
        return d

    devices = await asyncio.gather(*[work(c) for c in candidates])

    items = devices
    if q:
        ql = q.lower()
        items = [d for d in items if (d.name and ql in d.name.lower()) or (d.ip and ql in d.ip) or (d.model and ql in d.model.lower())]

    return {"devices": [d.model_dump() for d in items]}
