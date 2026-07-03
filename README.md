# Thoughts2.0 (Wavecast)

Deliver a polished podcast from your phone. Upload a raw voice note, Wavecast
splices in your intro, mid-roll sponsor read, and outro automatically, then
publishes straight to your RSS feed.

## Run locally

pip install -r requirements.txt
python main.py

Open http://localhost:8000

ffmpeg is required (pydub dependency).

## Free persistent storage

Free hosts (Render free tier, etc.) wipe local disk on restart/redeploy. To
keep shows, episodes, and audio files permanently without paying for storage,
Wavecast backs everything up to a storage backend and restores it on startup.
Two options, pick one:

### Option A — Your own computer (`home-storage-server/`)

Run a tiny storage server on a computer you leave on, and point the Render
app at it. Files are end-to-end encrypted before they ever leave Render — the
home server only ever stores ciphertext and never has the key, so even if
that machine were compromised, an attacker can't read your audio or database,
and can't feed it anything meaningful either.

1. Generate an encryption key:
   ```
   python -c "from crypto_utils import generate_key; print(generate_key())"
   ```
2. On your computer (the storage server — does **not** get the encryption key):
   ```
   cd home-storage-server
   pip install -r requirements.txt
   export STORAGE_TOKEN=pick-a-long-random-secret
   python server.py
   ```
3. Expose it to the internet with a free tunnel — [Tailscale Funnel](https://tailscale.com/kb/1223/funnel)
   is the simplest free option that gives you a stable HTTPS URL:
   ```
   tailscale funnel 8899
   ```
   This prints a URL like `https://your-machine.your-tailnet.ts.net`.
4. On Render, set these environment variables on the **Wavecast** service
   (the app, not the home server):
   - `HOME_STORAGE_URL` = the URL from step 3
   - `HOME_STORAGE_TOKEN` = the same secret from step 2
   - `HOME_STORAGE_KEY` = the key generated in step 1

If `HOME_STORAGE_KEY` isn't set, the app refuses to upload/download anything
to/from the home server rather than silently sending plaintext — local files
are preserved either way.

Your computer needs to be on and connected for the app to save/load files.
If it's off, the app still runs on Render's local disk temporarily but won't
persist until your computer is back online and the app restarts.

### Option B — archive.org (no computer required, always-on)

1. Create a free account: https://archive.org/account/signup
2. Get S3-like keys: https://archive.org/account/s3.php
3. Set environment variables on Render:
   - `IA_ACCESS_KEY`
   - `IA_SECRET_KEY`
   - `IA_ITEM` (a unique identifier for your data, e.g. `wavecast-yourname`)

**Note:** archive.org items are public by nature — anyone with the direct
file URL could access an audio file. Fine for content you intend to publish
anyway; don't use it for anything that must stay private. The home-storage
option (A) is private since it's on hardware you control.

If neither is configured, the app just runs on local disk (fine for local
use, not persistent on ephemeral hosts).

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
