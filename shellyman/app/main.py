import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from routers import security, devices  # absolute import

PORT = int(os.getenv("PORT", "8099"))

app = FastAPI(title="Shellyman (Ingress)")
app.include_router(security.router)
app.include_router(devices.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="ui")

@app.get("/")
def root():
    return RedirectResponse(url="/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
