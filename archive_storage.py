import os
import time
import requests

IA_ACCESS_KEY = os.environ.get("IA_ACCESS_KEY")
IA_SECRET_KEY = os.environ.get("IA_SECRET_KEY")
IA_ITEM = os.environ.get("IA_ITEM", "wavecast-app-data")

S3_BASE = "https://s3.us.archive.org"
DL_BASE = "https://archive.org/download"
META_URL = f"https://archive.org/metadata/{IA_ITEM}"


def enabled() -> bool:
    return bool(IA_ACCESS_KEY and IA_SECRET_KEY)


def _auth_header() -> str:
    return f"LOW {IA_ACCESS_KEY}:{IA_SECRET_KEY}"


def upload_file(local_path: str, remote_key: str) -> str | None:
    """Upload a local file to the archive.org item. Returns the public URL or None."""
    if not enabled() or not os.path.exists(local_path):
        return None
    url = f"{S3_BASE}/{IA_ITEM}/{remote_key}"
    headers = {
        "Authorization": _auth_header(),
        "x-archive-auto-make-bucket": "1",
        "x-archive-meta-mediatype": "audio",
        "x-archive-meta-title": IA_ITEM,
        "x-archive-meta-collection": "opensource_media",
        "x-archive-ignore-preexisting-bucket": "1",
    }
    try:
        with open(local_path, "rb") as f:
            r = requests.put(url, headers=headers, data=f, timeout=180)
        if r.status_code not in (200, 201):
            print(f"[archive] upload failed for {remote_key}: {r.status_code} {r.text[:200]}")
            return None
        return f"{DL_BASE}/{IA_ITEM}/{remote_key}"
    except requests.RequestException as e:
        print(f"[archive] upload error for {remote_key}: {e}")
        return None


def download_file(remote_key: str, local_path: str, retries: int = 2) -> bool:
    """Download a file from the archive.org item to a local path. Returns True on success."""
    if not enabled():
        return False
    url = f"{DL_BASE}/{IA_ITEM}/{remote_key}"
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(r.content)
                return True
            if r.status_code == 404:
                return False
        except requests.RequestException as e:
            print(f"[archive] download error for {remote_key}: {e}")
        time.sleep(1.5 * (attempt + 1))
    return False


def list_remote_files() -> list[str]:
    """List all file names currently stored in the archive.org item."""
    if not enabled():
        return []
    try:
        r = requests.get(META_URL, timeout=30)
        if r.status_code != 200:
            return []
        data = r.json()
        return [f["name"] for f in data.get("files", []) if not f["name"].startswith("_")]
    except requests.RequestException as e:
        print(f"[archive] list error: {e}")
        return []


def ensure_local(path: str | None) -> str | None:
    """If `path` doesn't exist locally, try to pull it from archive.org. Returns the path if it
    exists (or was restored), otherwise None."""
    if not path:
        return None
    if os.path.exists(path):
        return path
    if download_file(path, path):
        return path
    return None
