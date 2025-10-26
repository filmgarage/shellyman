from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..settings import load_options
from ..utils.http import HttpClient
from ..services.shelly_gen1 import ShellyGen1
from ..services.shelly_gen2 import ShellyGen2

router = APIRouter(prefix="/api/security", tags=["security"])

class Gen1EnableBody(BaseModel):
    ip: str
    username: str | None = None
    password: str | None = None

class Gen1DisableBody(BaseModel):
    ip: str

class Gen2EnableBody(BaseModel):
    ip: str
    password: str | None = None

class Gen2DisableBody(BaseModel):
    ip: str

@router.get("/status")
def status(ip: str, gen: int):
    opts = load_options()
    client = HttpClient(timeout=opts.request_timeout)
    if gen == 1:
        s1 = ShellyGen1(client)
        return s1.auth_status(ip).__dict__
    elif gen == 2:
        s2 = ShellyGen2(client)
        return s2.auth_status(ip).__dict__
    raise HTTPException(status_code=400, detail="gen must be 1 or 2")

@router.post("/gen1/enable")
def gen1_enable(body: Gen1EnableBody):
    opts = load_options()
    user = body.username or (opts.gen1_username or "")
    pwd = body.password or (opts.gen1_password or "")
    if not user or not pwd:
        raise HTTPException(status_code=400, detail="username and password required for Gen1")
    client = HttpClient(timeout=opts.request_timeout)
    s1 = ShellyGen1(client)
    ok = s1.enable_auth(body.ip, user, pwd)
    return {"ok": ok}

@router.post("/gen1/disable")
def gen1_disable(body: Gen1DisableBody):
    opts = load_options()
    client = HttpClient(timeout=opts.request_timeout)
    s1 = ShellyGen1(client)
    ok = s1.disable_auth(body.ip, opts.gen1_username, opts.gen1_password)
    return {"ok": ok}

@router.post("/gen2/enable")
def gen2_enable(body: Gen2EnableBody):
    opts = load_options()
    pwd = body.password or (opts.gen2_password or "")
    if not pwd:
        raise HTTPException(status_code=400, detail="password required for Gen2")
    client = HttpClient(timeout=opts.request_timeout)
    s2 = ShellyGen2(client)
    ok = s2.enable_auth(body.ip, pwd)
    return {"ok": ok}

@router.post("/gen2/disable")
def gen2_disable(body: Gen2DisableBody):
    opts = load_options()
    client = HttpClient(timeout=opts.request_timeout)
    s2 = ShellyGen2(client)
    ok = s2.disable_auth(body.ip)
    return {"ok": ok}
