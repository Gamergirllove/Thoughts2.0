# Thoughts2.0

Deliver a polished podcast from your phone. Upload a raw voice note, Wavecast
splices in your intro, mid-roll sponsor read, and outro automatically, then
publishes straight to your RSS feed.

## Run

pip install -r requirements.txt
python main.py

Open http://localhost:8000

ffmpeg is required (pydub dependency).

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
