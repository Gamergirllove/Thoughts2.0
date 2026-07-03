import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse

DATA_DIR = os.environ.get("STORAGE_DATA_DIR", "storage_data")
TOKEN = os.environ.get("STORAGE_TOKEN")
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI(title="Wavecast Home Storage")


def check_auth(request: Request):
    if not TOKEN:
        raise HTTPException(500, "STORAGE_TOKEN not set on server")
    header = request.headers.get("x-storage-token")
    if header != TOKEN:
        raise HTTPException(401, "bad token")


def safe_path(key: str) -> str:
    key = key.replace("..", "")
    path = os.path.join(DATA_DIR, key)
    os.makedirs(os.path.dirname(path) or DATA_DIR, exist_ok=True)
    return path


@app.put("/files/{key:path}")
async def put_file(key: str, request: Request):
    check_auth(request)
    path = safe_path(key)
    body = await request.body()
    with open(path, "wb") as f:
        f.write(body)
    return {"key": key, "bytes": len(body)}


@app.get("/files/{key:path}")
def get_file(key: str, request: Request):
    check_auth(request)
    path = safe_path(key)
    if not os.path.exists(path):
        raise HTTPException(404, "not found")
    return FileResponse(path)


@app.get("/list")
def list_files(request: Request):
    check_auth(request)
    keys = []
    for root, _, files in os.walk(DATA_DIR):
        for fname in files:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, DATA_DIR).replace(os.sep, "/")
            keys.append(rel)
    return {"keys": keys}


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8899))
    if not TOKEN:
        print("WARNING: STORAGE_TOKEN is not set. Set it before exposing this server publicly.")
    uvicorn.run(app, host="0.0.0.0", port=port)
