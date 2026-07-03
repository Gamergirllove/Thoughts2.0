# Run

pip install -r requirements.txt
python main.py

# ffmpeg required (pydub dependency)

# Endpoints
POST /shows
POST /shows/{id}/intro
POST /shows/{id}/outro
POST /shows/{id}/sponsor
POST /shows/{id}/episodes          -> voice_note upload, auto-assembles + auto-publishes
POST /episodes/{id}/sponsor        -> swap sponsor clip, re-syncs audio + RSS
GET  /audio/{id}
GET  /shows/{id}/rss.xml
