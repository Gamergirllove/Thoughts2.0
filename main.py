import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, Response
from models import init_db, get_db
from audio import assemble_episode
from rss import generate_feed

UPLOAD_DIR = "uploads"
EPISODE_DIR = "episodes"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EPISODE_DIR, exist_ok=True)

app = FastAPI(title="Podcast Auto-Publisher")
init_db()


def save_upload(file: UploadFile, subdir: str) -> str:
    dest_dir = os.path.join(UPLOAD_DIR, subdir)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return dest


@app.post("/shows")
def create_show(
    title: str = Form(...),
    description: str = Form(""),
    author: str = Form(""),
    base_url: str = Form(...),
    image_url: str = Form(""),
):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO shows (title, description, author, image_url, base_url) VALUES (?, ?, ?, ?, ?)",
            (title, description, author, image_url, base_url),
        )
        return {"show_id": cur.lastrowid}


@app.post("/shows/{show_id}/intro")
def upload_intro(show_id: int, file: UploadFile = File(...)):
    path = save_upload(file, f"show_{show_id}")
    with get_db() as db:
        db.execute("UPDATE shows SET intro_path = ? WHERE id = ?", (path, show_id))
    return {"intro_path": path}


@app.post("/shows/{show_id}/outro")
def upload_outro(show_id: int, file: UploadFile = File(...)):
    path = save_upload(file, f"show_{show_id}")
    with get_db() as db:
        db.execute("UPDATE shows SET outro_path = ? WHERE id = ?", (path, show_id))
    return {"outro_path": path}


@app.post("/shows/{show_id}/sponsor")
def upload_sponsor(show_id: int, file: UploadFile = File(...)):
    path = save_upload(file, f"show_{show_id}")
    with get_db() as db:
        db.execute("UPDATE shows SET sponsor_path = ? WHERE id = ?", (path, show_id))
    return {"sponsor_path": path}


@app.post("/shows/{show_id}/episodes")
def create_episode(
    show_id: int,
    title: str = Form(...),
    description: str = Form(""),
    voice_note: UploadFile = File(...),
):
    with get_db() as db:
        show = db.execute("SELECT * FROM shows WHERE id = ?", (show_id,)).fetchone()
        if not show:
            raise HTTPException(404, "show not found")

        raw_path = save_upload(voice_note, f"show_{show_id}/raw")

        cur = db.execute(
            "INSERT INTO episodes (show_id, title, description, raw_path) VALUES (?, ?, ?, ?)",
            (show_id, title, description, raw_path),
        )
        episode_id = cur.lastrowid

        final_path = os.path.join(EPISODE_DIR, f"episode_{episode_id}.mp3")
        duration, size = assemble_episode(
            raw_path,
            show["intro_path"],
            show["outro_path"],
            show["sponsor_path"],
            final_path,
        )

        db.execute(
            "UPDATE episodes SET final_path = ?, duration_seconds = ?, file_size = ?, published = 1 WHERE id = ?",
            (final_path, duration, size, episode_id),
        )

    return {"episode_id": episode_id, "duration_seconds": duration, "published": True}


@app.post("/episodes/{episode_id}/sponsor")
def update_episode_sponsor(episode_id: int, file: UploadFile = File(...)):
    with get_db() as db:
        ep = db.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,)).fetchone()
        if not ep:
            raise HTTPException(404, "episode not found")
        show = db.execute("SELECT * FROM shows WHERE id = ?", (ep["show_id"],)).fetchone()

        sponsor_path = save_upload(file, f"show_{ep['show_id']}/sponsor_override")

        final_path = ep["final_path"]
        duration, size = assemble_episode(
            ep["raw_path"],
            show["intro_path"],
            show["outro_path"],
            sponsor_path,
            final_path,
        )

        db.execute(
            "UPDATE episodes SET duration_seconds = ?, file_size = ? WHERE id = ?",
            (duration, size, episode_id),
        )

    return {"episode_id": episode_id, "duration_seconds": duration, "resynced": True}


@app.get("/audio/{episode_id}")
def get_audio(episode_id: int):
    with get_db() as db:
        ep = db.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,)).fetchone()
        if not ep or not ep["final_path"] or not os.path.exists(ep["final_path"]):
            raise HTTPException(404, "audio not found")
        return FileResponse(ep["final_path"], media_type="audio/mpeg", filename=os.path.basename(ep["final_path"]))


@app.get("/shows/{show_id}/rss.xml")
def get_rss(show_id: int):
    with get_db() as db:
        show = db.execute("SELECT * FROM shows WHERE id = ?", (show_id,)).fetchone()
        if not show:
            raise HTTPException(404, "show not found")
        episodes = db.execute(
            "SELECT * FROM episodes WHERE show_id = ? ORDER BY pub_date DESC", (show_id,)
        ).fetchall()

    xml = generate_feed(dict(show), [dict(e) for e in episodes])
    return Response(content=xml, media_type="application/rss+xml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
