# Thoughts2.0 (Wavecast)

Deliver a polished podcast from your phone. Upload a raw voice note, Wavecast
splices in your intro, mid-roll sponsor read, and outro automatically, then
publishes straight to your RSS feed.

## Run locally

pip install -r requirements.txt
python main.py

Open http://localhost:8000

ffmpeg is required (pydub dependency).

## Free persistent storage (archive.org)

Free hosts (Render free tier, etc.) wipe local disk on restart/redeploy. To
keep shows, episodes, and audio files permanently without paying for storage,
Wavecast can back everything up to a free archive.org item and restore it on
startup.

1. Create a free account: https://archive.org/account/signup
2. Get S3-like keys: https://archive.org/account/s3.php
3. Set these environment variables (copy `.env.example` to `.env` for local
   dev, or set them in your host's dashboard for deployment):
   - `IA_ACCESS_KEY`
   - `IA_SECRET_KEY`
   - `IA_ITEM` (a unique identifier for your data, e.g. `wavecast-yourname`)

Once set, every show/episode/clip upload is mirrored to archive.org, and the
app pulls everything back down automatically on startup. Without these vars
set, the app just runs on local disk as before (fine for local use, not
persistent on ephemeral hosts).

**Note:** archive.org items are public by nature — anyone with the direct
file URL could access an audio file. Fine for content you intend to publish
anyway; don't use it for anything that must stay private.

## Deploy on Render (free)

1. Push this repo to GitHub (already done if you're reading this on GitHub)
2. Go to render.com → sign in with GitHub → New → Blueprint → select this repo
3. Render reads `render.yaml` and deploys automatically
4. In the Render dashboard, add the `IA_ACCESS_KEY` / `IA_SECRET_KEY` / `IA_ITEM`
   environment variables under the service's Environment tab for persistence

## Pages
- `/` — Shows (create show, list shows, RSS links)
- `/episodes-page` — Upload voice notes, view episodes, swap sponsor clip
- `/settings-page` — Intro / outro / default sponsor clips, RSS feed URL

## API endpoints
- `POST /shows`
- `POST /shows/{id}/intro`
- `POST /shows/{id}/outro`
- `POST /shows/{id}/sponsor`
- `POST /shows/{id}/episodes` — voice_note upload, auto-assembles + auto-publishes
- `POST /episodes/{id}/sponsor` — swap sponsor clip, re-syncs audio + RSS
- `GET /shows`
- `GET /shows/{id}`
- `GET /shows/{id}/episodes-list`
- `GET /audio/{id}`
- `GET /shows/{id}/rss.xml`
