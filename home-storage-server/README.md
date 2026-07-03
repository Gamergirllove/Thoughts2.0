# Wavecast Home Storage Server

Run this on a computer you leave on to give the Render-hosted app free,
private, persistent storage.

## Setup

pip install -r requirements.txt
export STORAGE_TOKEN=pick-a-long-random-secret
python server.py

Runs on port 8899 by default (override with PORT env var).

## Expose it to the internet

Recommended: [Tailscale Funnel](https://tailscale.com/kb/1223/funnel) (free,
stable HTTPS URL, no port forwarding needed):

    tailscale funnel 8899

Copy the printed URL. On Render, set on the Wavecast service:

- HOME_STORAGE_URL = that URL
- HOME_STORAGE_TOKEN = the same STORAGE_TOKEN you set above

## Endpoints

- PUT  /files/{key}   (auth header: x-storage-token)
- GET  /files/{key}
- GET  /list
- GET  /health
