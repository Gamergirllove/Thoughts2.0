import os
import time
import requests
import archive_storage as _archive

HOME_STORAGE_URL = os.environ.get("HOME_STORAGE_URL", "").rstrip("/")
HOME_STORAGE_TOKEN = os.environ.get("HOME_STORAGE_TOKEN")


def _home_enabled() -> bool:
    return bool(HOME_STORAGE_URL and HOME_STORAGE_TOKEN)


def enabled() -> bool:
    return _home_enabled() or _archive.enabled()


def backend_name() -> str:
    if _home_enabled():
        return "home"
    if _archive.enabled():
        return "archive.org"
    return "none"


def _headers():
    return {"x-storage-token": HOME_STORAGE_TOKEN}


def upload_file(local_path: str, remote_key: str) -> str | None:
    if _home_enabled():
        if not os.path.exists(local_path):
            return None
        url = f"{HOME_STORAGE_URL}/files/{remote_key}"
        try:
            with open(local_path, "rb") as f:
                r = requests.put(url, headers=_headers(), data=f, timeout=60)
            if r.status_code == 200:
                return url
            print(f"[home-storage] upload failed for {remote_key}: {r.status_code}")
            return None
        except requests.RequestException as e:
            print(f"[home-storage] upload error for {remote_key}: {e}")
            return None
    return _archive.upload_file(local_path, remote_key)


def download_file(remote_key: str, local_path: str, retries: int = 2) -> bool:
    if _home_enabled():
        url = f"{HOME_STORAGE_URL}/files/{remote_key}"
        for attempt in range(retries + 1):
            try:
                r = requests.get(url, headers=_headers(), timeout=30)
                if r.status_code == 200:
                    os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
                    with open(local_path, "wb") as f:
                        f.write(r.content)
                    return True
                if r.status_code == 404:
                    return False
            except requests.RequestException as e:
                print(f"[home-storage] download error for {remote_key}: {e}")
            time.sleep(1.5 * (attempt + 1))
        return False
    return _archive.download_file(remote_key, local_path, retries=retries)


def list_remote_files() -> list[str]:
    if _home_enabled():
        try:
            r = requests.get(f"{HOME_STORAGE_URL}/list", headers=_headers(), timeout=15)
            if r.status_code == 200:
                return r.json().get("keys", [])
            return []
        except requests.RequestException as e:
            print(f"[home-storage] list error: {e}")
            return []
    return _archive.list_remote_files()


def ensure_local(path: str | None) -> str | None:
    if not path:
        return None
    if os.path.exists(path):
        return path
    if download_file(path, path):
        return path
    return None
